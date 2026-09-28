"""Explicit, read-only Stage 13A-P1 Bluetooth callback comparison."""

import asyncio
from collections import Counter
import re
from time import monotonic

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant


OBSERVATION_SECONDS = 60
MAX_EVENT_SAMPLES = 32
MAX_SOURCE_ALIASES = 4
MAX_COUNT = 100_000


class AdvertisementObservationError(Exception):
    """Private-free stage and exception type for development action failures."""

    def __init__(self, stage: str, error: Exception) -> None:
        self.stage = stage
        name = type(error).__name__
        self.error_type = name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", name) else "Exception"
        super().__init__(f"stage={stage}, type={self.error_type}")


async def async_observe_advertisements(
    hass: HomeAssistant, address: str, stop_event: asyncio.Event
) -> dict:
    """Compare live change dispatch with repeated packet delivery for one address.

    No Bluetooth client, active scan request, cache mutation, or FORA protocol
    operation is performed. All identifiers stay within this invocation.
    """
    started = monotonic()
    aliases: dict[str, str] = {}
    packet_sources: Counter[str] = Counter()
    changed_sources: Counter[str] = Counter()
    packet_samples: list[dict] = []
    changed_samples: list[dict] = []
    packet_count = 0
    changed_count = 0
    first_shape: dict | None = None
    last_shape: dict | None = None
    shape_change_count = 0
    first_changed_shape: dict | None = None
    last_changed_shape: dict | None = None
    cancel_callbacks = []
    callback_cleanup_successful = True
    packet_registration = getattr(bluetooth, "async_register_advertisement_callback", None)
    packet_callback_supported = callable(packet_registration)

    def source_alias(source: str | None) -> str:
        if not source:
            return "Unknown"
        if source not in aliases:
            if len(aliases) >= MAX_SOURCE_ALIASES:
                return "Other"
            aliases[source] = f"Source {chr(ord('A') + len(aliases))}"
        return aliases[source]

    def shape(info) -> dict:
        connectable = getattr(info, "connectable", None)
        return {
            "name_matches_fora6_connect": info.name == "FORA 6 CONNECT",
            "service_uuid_count": len(info.service_uuids or ()),
            "manufacturer_entry_count": len(info.manufacturer_data or {}),
            "service_data_entry_count": len(info.service_data or {}),
            "connectable": connectable if isinstance(connectable, bool) else None,
        }

    def elapsed() -> float:
        return round(monotonic() - started, 1)

    def on_packet(info) -> None:
        nonlocal packet_count, first_shape, last_shape, shape_change_count
        packet_count = min(packet_count + 1, MAX_COUNT)
        alias = source_alias(getattr(info, "source", None))
        packet_sources[alias] = min(packet_sources[alias] + 1, MAX_COUNT)
        current_shape = shape(info)
        if last_shape is not None and current_shape != last_shape:
            shape_change_count = min(shape_change_count + 1, MAX_COUNT)
        if len(packet_samples) < MAX_EVENT_SAMPLES:
            packet_samples.append({
                "elapsed_seconds": elapsed(), "source": alias,
                "shape": current_shape,
            })
        last_shape = current_shape
        if first_shape is None:
            first_shape = last_shape

    def on_change(info, change) -> None:
        nonlocal changed_count, first_changed_shape, last_changed_shape
        changed_count = min(changed_count + 1, MAX_COUNT)
        alias = source_alias(getattr(info, "source", None))
        changed_sources[alias] = min(changed_sources[alias] + 1, MAX_COUNT)
        last_changed_shape = shape(info)
        if first_changed_shape is None:
            first_changed_shape = last_changed_shape
        if len(changed_samples) < MAX_EVENT_SAMPLES:
            changed_samples.append({
                "elapsed_seconds": elapsed(), "source": alias,
                "shape": last_changed_shape,
            })

    try:
        if packet_callback_supported:
            try:
                cancel_callbacks.append(packet_registration(hass, on_packet, address))
            except Exception as err:
                raise AdvertisementObservationError("packet_callback_registration", err) from None
        try:
            cancel_callbacks.append(bluetooth.async_register_callback(
                hass,
                on_change,
                {"address": address},
                bluetooth.BluetoothScanningMode.PASSIVE,
                replay=bluetooth.BluetoothCallbackReplay.DISABLED,
            ))
        except Exception as err:
            raise AdvertisementObservationError("changed_callback_registration", err) from None
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=OBSERVATION_SECONDS)
        except TimeoutError:
            pass
        except asyncio.CancelledError:
            raise
        except Exception as err:
            raise AdvertisementObservationError("observation_wait", err) from None
    finally:
        for cancel in reversed(cancel_callbacks):
            try:
                cancel()
            except Exception:
                callback_cleanup_successful = False

    return {
        "observation_seconds": OBSERVATION_SECONDS,
        "packet_callback_supported": packet_callback_supported,
        "stopped_by_unload": stop_event.is_set(),
        "callback_cleanup_successful": callback_cleanup_successful,
        "packet_callback_count": packet_count if packet_callback_supported else None,
        "changed_callback_count": changed_count,
        "packet_source_counts": dict(packet_sources) if packet_callback_supported else None,
        "changed_source_counts": dict(changed_sources),
        "packet_event_sample": packet_samples if packet_callback_supported else None,
        "changed_event_sample": changed_samples,
        "event_sample_limit": MAX_EVENT_SAMPLES,
        "first_packet_shape": first_shape,
        "last_packet_shape": last_shape,
        "packet_shape_change_count": shape_change_count,
        "first_changed_shape": first_changed_shape,
        "last_changed_shape": last_changed_shape,
    }
