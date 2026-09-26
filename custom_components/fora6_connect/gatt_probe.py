"""Temporary Stage 1B GATT inventory probe; no characteristic I/O."""

from __future__ import annotations

import asyncio
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
SIG_BASE = "-0000-1000-8000-00805f9b34fb"


class ProbeError(Exception):
    """A privacy-safe failure message for the manual service action."""


def _uuid128(value: str) -> str:
    """Normalize standard 16-bit UUIDs for comparison with Bleak UUIDs."""
    value = str(value).lower()
    return f"0000{value}{SIG_BASE}" if len(value) == 4 else value


def _local_name(info: Any) -> str | None:
    """Read the advertised name without persisting its device address."""
    return info.name or info.device.name


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
    if not scanner_count:
        raise ProbeError(
            "No connectable Home Assistant Bluetooth scanner is available."
        )

    # HA may deduplicate identical advertisements. Clear only a previously
    # cached candidate's advertisement history so a new radio packet can
    # reach our callback; never treat that cached candidate as fresh evidence.
    for info in bluetooth.async_discovered_service_info(hass, connectable=True):
        if _local_name(info) == TARGET_LOCAL_NAME:
            bluetooth.async_clear_advertisement_history(hass, info.address)

    fresh_addresses: set[str] = set()

    def _on_advertisement(info: Any, change: Any) -> None:
        if _local_name(info) == TARGET_LOCAL_NAME:
            fresh_addresses.add(info.address)

    cancel = bluetooth.async_register_callback(
        hass,
        _on_advertisement,
        {"local_name": TARGET_LOCAL_NAME, "connectable": True},
        bluetooth.BluetoothScanningMode.ACTIVE,
        replay=bluetooth.BluetoothCallbackReplay.DISABLED,
    )
    try:
        await bluetooth.async_request_active_scan(hass)
    except Exception:
        raise ProbeError("Home Assistant could not complete the active scan.") from None
    finally:
        cancel()

    candidates = {
        info.address: info
        for info in bluetooth.async_discovered_service_info(hass, connectable=True)
        if info.address in fresh_addresses and _local_name(info) == TARGET_LOCAL_NAME
    }
    if not candidates:
        raise ProbeError(
            "No fresh FORA 6 CONNECT advertisement was observed during the active scan."
        )
    if len(candidates) > 1:
        raise ProbeError("Multiple matching devices were observed; probe stopped.")

    address = next(iter(candidates))  # Runtime only; never returned or logged.
    ble_device = bluetooth.async_ble_device_from_address(
        hass, address, connectable=True
    )
    if ble_device is None:
        raise ProbeError(
            "FORA 6 CONNECT was seen, but no connectable BLEDevice is available."
        )

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
        try:
            await asyncio.wait_for(client.disconnect(), timeout=DISCONNECT_TIMEOUT)
        except Exception:
            raise ProbeError(
                "GATT probe could not confirm a clean disconnect."
            ) from None

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
