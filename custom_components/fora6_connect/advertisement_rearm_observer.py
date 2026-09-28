"""One-shot, development-only advertisement history re-arm observation."""

import asyncio
from collections import Counter
from time import monotonic

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .advertisement_observer import (
    AdvertisementObservationError,
    MAX_COUNT,
    MAX_EVENT_SAMPLES,
    MAX_SOURCE_ALIASES,
    OBSERVATION_SECONDS,
)


async def async_observe_advertisement_rearm(
    hass: HomeAssistant, address: str, stop_event: asyncio.Event
) -> dict:
    """Clear history once after the first live change, then observe only changes.

    Physical ON/OFF state is not available to this callback; the user must
    confirm that the meter remained continuously ON after the clear.
    """
    started = monotonic()
    first_callback = asyncio.Event()
    aliases: dict[str, str] = {}
    sources: Counter[str] = Counter()
    samples: list[dict] = []
    count = 0
    after_clear_count = 0
    first_elapsed: float | None = None
    clear_elapsed: float | None = None
    cleanup_successful = True
    cancel_callback = None

    def elapsed() -> float:
        return round(monotonic() - started, 1)

    def alias(source: str | None) -> str:
        if not source:
            return "Unknown"
        if source not in aliases:
            if len(aliases) >= MAX_SOURCE_ALIASES:
                return "Other"
            aliases[source] = f"Source {chr(ord('A') + len(aliases))}"
        return aliases[source]

    def on_change(info, change) -> None:
        nonlocal count, after_clear_count, first_elapsed
        count = min(count + 1, MAX_COUNT)
        source = alias(getattr(info, "source", None))
        sources[source] = min(sources[source] + 1, MAX_COUNT)
        when = elapsed()
        if first_elapsed is None:
            first_elapsed = when
            first_callback.set()
        elif clear_elapsed is not None:
            after_clear_count = min(after_clear_count + 1, MAX_COUNT)
        if len(samples) < MAX_EVENT_SAMPLES:
            connectable = getattr(info, "connectable", None)
            samples.append({
                "elapsed_seconds": when,
                "after_clear": clear_elapsed is not None,
                "source": source,
                "shape": {
                    "name_matches_fora6_connect": getattr(info, "name", None) == "FORA 6 CONNECT",
                    "service_uuid_count": len(getattr(info, "service_uuids", None) or ()),
                    "manufacturer_entry_count": len(getattr(info, "manufacturer_data", None) or {}),
                    "service_data_entry_count": len(getattr(info, "service_data", None) or {}),
                    "connectable": connectable if isinstance(connectable, bool) else None,
                },
            })

    first_wait = None
    stop_wait = None
    try:
        try:
            cancel_callback = bluetooth.async_register_callback(
                hass, on_change, {"address": address},
                bluetooth.BluetoothScanningMode.PASSIVE,
                replay=bluetooth.BluetoothCallbackReplay.DISABLED,
            )
        except Exception as err:
            raise AdvertisementObservationError("changed_callback_registration", err) from None

        first_wait = asyncio.create_task(first_callback.wait())
        stop_wait = asyncio.create_task(stop_event.wait())
        try:
            await asyncio.wait(
                {first_wait, stop_wait}, timeout=OBSERVATION_SECONDS,
                return_when=asyncio.FIRST_COMPLETED,
            )
            if first_callback.is_set() and not stop_event.is_set():
                try:
                    bluetooth.async_clear_advertisement_history(hass, address)
                except Exception as err:
                    raise AdvertisementObservationError("clear_history", err) from None
                clear_elapsed = elapsed()
                remaining = max(0.0, OBSERVATION_SECONDS - (monotonic() - started))
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=remaining)
                except TimeoutError:
                    pass
        except asyncio.CancelledError:
            raise
        except AdvertisementObservationError:
            raise
        except Exception as err:
            raise AdvertisementObservationError("observation_wait", err) from None
    finally:
        for waiter in (first_wait, stop_wait):
            if waiter is not None and not waiter.done():
                waiter.cancel()
        if cancel_callback is not None:
            try:
                cancel_callback()
            except Exception:
                cleanup_successful = False

    return {
        "observation_seconds": OBSERVATION_SECONDS,
        "first_callback_seen": first_elapsed is not None,
        "first_callback_elapsed_seconds": first_elapsed,
        "clear_performed": clear_elapsed is not None,
        "clear_elapsed_seconds": clear_elapsed,
        "changed_callback_count": count,
        "callbacks_after_clear_count": after_clear_count,
        "changed_source_counts": dict(sources),
        "changed_event_sample": samples,
        "event_sample_limit": MAX_EVENT_SAMPLES,
        "callback_cleanup_successful": cleanup_successful,
        "stopped_by_unload": stop_event.is_set(),
    }
