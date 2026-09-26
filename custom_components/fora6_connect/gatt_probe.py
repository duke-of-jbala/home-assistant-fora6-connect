"""Temporary Stage 1B GATT inventory probe; no characteristic I/O."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from bleak_retry_connector import (
    BleakClientWithServiceCache,
    BleakOutOfConnectionSlotsError,
    establish_connection,
)
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothReachabilityIntent
from homeassistant.core import HomeAssistant

from .const import CHARACTERISTIC_UUID, NAME, SERVICE_UUID

TARGET_LOCAL_NAME = "FORA 6 CONNECT"
CONNECTION_TIMEOUT = 20.0
DISCONNECT_TIMEOUT = 10.0
SIG_BASE = "-0000-1000-8000-00805f9b34fb"
PRIVATE_IDENTIFIER = re.compile(
    r"(?i)(?<![0-9a-f])(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}(?![0-9a-f])"
    r"|(?<![0-9a-f])[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}(?![0-9a-f])"
    r"|(?<![0-9a-f])[0-9a-f]{12}(?![0-9a-f])"
)
_LOGGER = logging.getLogger(__name__)


class ProbeError(Exception):
    """A privacy-safe failure message for the manual service action."""


def _uuid128(value: str) -> str:
    """Normalize standard 16-bit UUIDs for comparison with Bleak UUIDs."""
    value = str(value).lower()
    return f"0000{value}{SIG_BASE}" if len(value) == 4 else value


def normalize_local_name(name: str | None) -> str | None:
    """Remove only trailing NUL padding from an advertised local name."""
    return name.rstrip("\x00") if name is not None else None


def _advertised_local_name(info: Any) -> str | None:
    """Get the normalized packet name, separate from HA's resolved name."""
    return normalize_local_name(
        getattr(getattr(info, "advertisement", None), "local_name", None)
    )


def _safe_reachability_reason(reason: str, address: str) -> str:
    """Redact device and scanner identifiers without interpreting HA wording."""
    if not isinstance(reason, str) or not reason:
        return "No additional reachability detail was available."
    reason = re.sub(re.escape(address), "[private address]", reason, flags=re.I)
    return PRIVATE_IDENTIFIER.sub("[private identifier]", reason)


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


async def async_probe_gatt(hass: HomeAssistant, address: str) -> dict[str, Any]:
    """Connect through Home Assistant and list GATT metadata only."""
    try:
        ble_device = bluetooth.async_ble_device_from_address(
            hass, address, connectable=True
        )
    except Exception:
        raise ProbeError(
            "Home Assistant could not resolve a connectable BLEDevice."
        ) from None
    _LOGGER.debug("GATT probe: connectable BLEDevice resolved: %s", ble_device is not None)
    if ble_device is None:
        try:
            reachability = bluetooth.async_address_reachability_diagnostics(
                hass, address, BluetoothReachabilityIntent.CONNECTION
            )
        except Exception:
            reachability = "No additional reachability detail was available."
        raise ProbeError(
            "No connectable BLEDevice is available. Home Assistant reachability: "
            f"{_safe_reachability_reason(reachability, address)}"
        )

    scanner_count = bluetooth.async_scanner_count(hass, connectable=True)
    _LOGGER.debug("GATT probe: connectable scanners=%d", scanner_count)

    try:
        last_info = bluetooth.async_last_service_info(hass, address, connectable=False)
    except Exception:
        last_info = None
        _LOGGER.debug("GATT probe: optional last service info unavailable")
    local_name = _advertised_local_name(last_info) if last_info is not None else None
    _LOGGER.debug("GATT probe: last service info available=%s", last_info is not None)

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
        _LOGGER.debug("GATT probe: connection successful=false (no slot)")
        raise ProbeError(
            "No Bluetooth proxy/adapter connection slot is available."
        ) from None
    except Exception:
        _LOGGER.debug("GATT probe: connection successful=false")
        raise ProbeError(
            "Bluetooth connection failed or the device disappeared; "
            "check reachability privately."
        ) from None

    result: list[dict[str, Any]] | None = None
    failure: ProbeError | None = None
    try:
        if not client.is_connected:
            raise ProbeError("The meter disconnected before GATT discovery.")
        _LOGGER.debug("GATT probe: connection successful=true")
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
        "local_name": local_name,
        "advertised_name_confirmed": local_name == TARGET_LOCAL_NAME,
        "last_service_info_available": last_info is not None,
        "connectable_device_resolved": True,
        "connectable_scanner_count": scanner_count,
        "gatt_connection_attempted": True,
        "connection_successful": True,
        "connected_via_ha_bluetooth": True,
        "gatt_service_count": len(result),
        "services": result,
        "expected_gatt": _expected_gatt(result),
        "disconnected_cleanly": True,
    }
