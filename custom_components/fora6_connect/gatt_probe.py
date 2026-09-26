"""Temporary Stage 1B GATT inventory probe; no characteristic I/O."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from bleak_retry_connector import (
    BleakClientWithServiceCache,
    BleakOutOfConnectionSlotsError,
    establish_connection,
)
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import CHARACTERISTIC_UUID, NAME, SERVICE_UUID

TARGET_LOCAL_NAME = "FORA 6 CONNECT"
CONNECTION_TIMEOUT = 20.0
DISCONNECT_TIMEOUT = 10.0
ADVERTISEMENT_TIMEOUT = 20
SIG_BASE = "-0000-1000-8000-00805f9b34fb"
_LOGGER = logging.getLogger(__name__)


class ProbeError(Exception):
    """A privacy-safe failure message for the manual service action."""


def _uuid128(value: str) -> str:
    """Normalize standard 16-bit UUIDs for comparison with Bleak UUIDs."""
    value = str(value).lower()
    return f"0000{value}{SIG_BASE}" if len(value) == 4 else value


def _local_name(info: Any) -> str | None:
    """Prefer the packet local name, then HA's resolved service-info name."""
    advertised = getattr(getattr(info, "advertisement", None), "local_name", None)
    return advertised or getattr(info, "name", None)


def _enumerate_services(services: Any) -> list[dict[str, Any]]:
    """Copy only public GATT UUIDs and characteristic properties."""
    return [
        {
            "uuid": str(service.uuid).lower(),
            "characteristics": [
                {
                    "uuid": str(characteristic.uuid).lower(),
                    "properties": sorted(
                        str(prop).lower() for prop in characteristic.properties
                    ),
                }
                for characteristic in service.characteristics
            ],
        }
        for service in services
    ]


def _expected_gatt(observed: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare observed metadata with the prior iPhone GATT inventory."""
    by_service = {_uuid128(item["uuid"]): item for item in observed}
    expected_chars = (
        ("1808", "2a18", ("notify",)),
        ("1808", "2a34", ("notify",)),
        ("1808", "2a51", ("read",)),
        ("1808", "2a52", ("write", "indicate")),
        (SERVICE_UUID, CHARACTERISTIC_UUID, ("write", "notify")),
    )
    comparisons = []
    for service_uuid, char_uuid, properties in expected_chars:
        service = by_service.get(_uuid128(service_uuid), {})
        characteristics = {
            _uuid128(item["uuid"]): item
            for item in service.get("characteristics", ())
        }
        found = characteristics.get(_uuid128(char_uuid))
        observed_properties = found["properties"] if found else []
        comparisons.append(
            {
                "service_uuid": _uuid128(service_uuid),
                "uuid": _uuid128(char_uuid),
                "present": found is not None,
                "expected_properties": list(properties),
                "observed_properties": observed_properties,
                "expected_properties_present": (
                    set(properties) <= set(observed_properties)
                ),
            }
        )
    return {
        "device_information_service_present": _uuid128("180a") in by_service,
        "glucose_service_present": _uuid128("1808") in by_service,
        "fora_custom_service_present": _uuid128(SERVICE_UUID) in by_service,
        "characteristics": comparisons,
    }


async def async_probe_gatt(hass: HomeAssistant) -> dict[str, Any]:
    """Find a fresh advertisement, connect through HA, and list GATT metadata."""
    scanner_count = bluetooth.async_scanner_count(hass, connectable=True)
    discoveries = tuple(
        bluetooth.async_discovered_service_info(hass, connectable=False)
    )
    candidates = {
        info.address: info
        for info in discoveries
        if _local_name(info) == TARGET_LOCAL_NAME
    }
    _LOGGER.debug(
        "GATT probe: general discoveries=%d; FORA name matches=%d; "
        "connectable scanners=%d; cached candidate found=%s",
        len(discoveries),
        len(candidates),
        scanner_count,
        bool(candidates),
    )
    if not scanner_count:
        _LOGGER.debug("GATT probe: no connectable Home Assistant scanner")
        raise ProbeError(
            "No connectable Home Assistant Bluetooth scanner is available."
        )

    if not candidates:
        raise ProbeError(
            "No known FORA 6 CONNECT candidate is available for targeted active "
            "scanning; first observe it in Home Assistant Bluetooth "
            f"(general discoveries: {len(discoveries)}; name matches: 0; "
            f"connectable scanners: {scanner_count})."
        )
    if len(candidates) > 1:
        raise ProbeError("Multiple matching devices are known; probe stopped.")

    cached_info = next(iter(candidates.values()))
    address = cached_info.address  # Runtime only; never returned or logged.
    cached_time = cached_info.time
    wait_started = bluetooth.MONOTONIC_TIME()

    def _is_fresh_fora(info: Any) -> bool:
        # async_process_advertisements may replay cached history on registration.
        # A replay can be newer than this candidate if another scanner heard
        # the device later, so it must also postdate the start of this wait.
        return (
            info.address == address
            and _local_name(info) == TARGET_LOCAL_NAME
            and info.time > max(cached_time, wait_started)
        )

    _LOGGER.debug("GATT probe: targeted active advertisement wait started")
    try:
        fresh_info = await bluetooth.async_process_advertisements(
            hass,
            _is_fresh_fora,
            # HA's callback matcher defaults to connectable-only when omitted.
            {"address": address, "connectable": False},
            bluetooth.BluetoothScanningMode.ACTIVE,
            ADVERTISEMENT_TIMEOUT,
        )
    except TimeoutError:
        _LOGGER.debug("GATT probe: no fresh advertisement received before timeout")
        raise ProbeError(
            "No fresh FORA 6 CONNECT advertisement was observed during the "
            "targeted active wait."
        ) from None
    except Exception:
        _LOGGER.debug("GATT probe: targeted active wait failed")
        raise ProbeError(
            "Home Assistant could not complete the targeted active wait."
        ) from None
    if not _is_fresh_fora(fresh_info):
        _LOGGER.debug("GATT probe: targeted wait returned no valid fresh candidate")
        raise ProbeError("Targeted wait returned no fresh FORA 6 CONNECT advertisement.")

    _LOGGER.debug("GATT probe: fresh FORA advertisement received")
    ble_device = bluetooth.async_ble_device_from_address(
        hass, fresh_info.address, connectable=True
    )
    _LOGGER.debug("GATT probe: connectable BLEDevice resolved: %s", ble_device is not None)
    if ble_device is None:
        raise ProbeError(
            "FORA 6 CONNECT was seen, but no connectable BLEDevice is available."
        )

    _LOGGER.debug("GATT probe: connection attempted")
    try:
        client = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            NAME,
            max_attempts=2,
            use_services_cache=False,
            timeout=CONNECTION_TIMEOUT,
            pair=False,
        )
    except BleakOutOfConnectionSlotsError:
        raise ProbeError(
            "No Bluetooth proxy/adapter connection slot is available."
        ) from None
    except Exception:
        raise ProbeError(
            "Bluetooth connection failed or the device disappeared; "
            "check reachability privately."
        ) from None

    result: list[dict[str, Any]] | None = None
    failure: ProbeError | None = None
    try:
        if not client.is_connected:
            raise ProbeError("The meter disconnected before GATT discovery.")
        services = client.services
        _LOGGER.debug("GATT probe: GATT enumeration reached")
        if services is None:
            raise ProbeError("GATT services were unavailable after connection.")
        result = _enumerate_services(services)
        if not result:
            raise ProbeError("No GATT services were returned after connection.")
        if not client.is_connected:
            raise ProbeError("The meter disconnected during GATT discovery.")
    except ProbeError as err:
        failure = err
    except Exception:
        failure = ProbeError("GATT service discovery failed or the peer disconnected.")
    finally:
        _LOGGER.debug("GATT probe: disconnect attempted")
        try:
            await asyncio.wait_for(client.disconnect(), timeout=DISCONNECT_TIMEOUT)
        except Exception:
            _LOGGER.debug("GATT probe: disconnect did not complete cleanly")
            raise ProbeError(
                "GATT probe could not confirm a clean disconnect."
            ) from None
        _LOGGER.debug("GATT probe: disconnect completed")

    if failure is not None:
        raise failure
    assert result is not None
    return {
        "device_found": True,
        "local_name": TARGET_LOCAL_NAME,
        "active_scan_requested": True,
        "fresh_advertisement_observed": True,
        "connectable_device_resolved": True,
        "connectable_scanner_count": scanner_count,
        "connection_successful": True,
        "connected_via_ha_bluetooth": True,
        "gatt_service_count": len(result),
        "services": result,
        "expected_gatt": _expected_gatt(result),
        "disconnected_cleanly": True,
    }
