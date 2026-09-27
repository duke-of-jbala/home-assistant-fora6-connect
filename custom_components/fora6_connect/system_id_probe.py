"""Development-only, bounded, read-only Device Information System ID probe."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .serial_probe import (
    DEVICE_INFORMATION_UUID,
    READ_TIMEOUT,
    _ProbeFailure,
    _connect,
    _disconnect,
)

SYSTEM_ID_UUID = "00002a23-0000-1000-8000-00805f9b34fb"
SYSTEM_ID_SIZE = 8  # Bluetooth SIG: uint40 manufacturer ID + uint24 OUI.


def _empty_result() -> dict[str, Any]:
    """Return only fixed structural flags, never a value or its length."""
    return {
        "device_found": False,
        "connectable_device_resolved": False,
        "connection_successful": False,
        "device_information_service_found": False,
        "system_id_characteristic_found": False,
        "system_id_readable": False,
        "system_id_read_successful": False,
        "system_id_value_present": False,
        "system_id_value_usable": False,
        "system_id_format_plausible": False,
        "disconnected_cleanly": False,
        "error_stage": None,
        "error_code": None,
        "cleanup_errors": [],
    }


async def _async_read_system_id_private(
    hass: HomeAssistant, address: str
) -> tuple[dict[str, Any], bytes | None]:
    """Read 0x2A23 once and return private bytes only to local comparison code."""
    result = _empty_result()
    client = None
    raw: bytes | None = None
    try:
        try:
            device = bluetooth.async_ble_device_from_address(
                hass, address, connectable=True
            )
        except Exception:
            raise _ProbeFailure("resolution", "resolution_failed") from None
        if device is None:
            raise _ProbeFailure("resolution", "no_connectable_device")
        result["device_found"] = True
        result["connectable_device_resolved"] = True
        client = await _connect(device)
        if not client.is_connected:
            raise _ProbeFailure("connection", "peer_disconnected")
        result["connection_successful"] = True
        try:
            service = next(
                (
                    item for item in client.services
                    if str(item.uuid).lower() == DEVICE_INFORMATION_UUID
                ),
                None,
            )
        except Exception:
            raise _ProbeFailure("gatt", "services_unavailable") from None
        if service is None:
            raise _ProbeFailure("gatt", "device_information_missing")
        result["device_information_service_found"] = True
        try:
            characteristic = next(
                (
                    item for item in service.characteristics
                    if str(item.uuid).lower() == SYSTEM_ID_UUID
                ),
                None,
            )
        except Exception:
            raise _ProbeFailure("gatt", "characteristics_unavailable") from None
        if characteristic is None:
            raise _ProbeFailure("gatt", "system_id_characteristic_missing")
        result["system_id_characteristic_found"] = True
        try:
            readable = "read" in {
                str(prop).lower() for prop in characteristic.properties
            }
        except Exception:
            readable = False
        if not readable:
            raise _ProbeFailure("gatt", "system_id_not_readable")
        result["system_id_readable"] = True
        try:
            raw = bytes(
                await asyncio.wait_for(
                    client.read_gatt_char(characteristic), timeout=READ_TIMEOUT
                )
            )
        except Exception:
            raise _ProbeFailure("read", "system_id_read_failed") from None
        result["system_id_read_successful"] = True
        result["system_id_value_present"] = bool(raw)
        plausible = len(raw) == SYSTEM_ID_SIZE
        result["system_id_format_plausible"] = plausible
        # Constant-filled structures cannot establish instance identity. This
        # is a conservative local usability rule, not a SIG field constraint.
        usable = plausible and raw not in (bytes(SYSTEM_ID_SIZE), b"\xff" * SYSTEM_ID_SIZE)
        result["system_id_value_usable"] = usable
    except _ProbeFailure as failure:
        result["error_stage"] = failure.stage
        result["error_code"] = failure.code
    except Exception:
        result["error_stage"] = "probe"
        result["error_code"] = "unexpected_failure"
    finally:
        if client is not None:
            close_task = asyncio.create_task(_disconnect(client))
            try:
                result["disconnected_cleanly"] = await asyncio.shield(close_task)
            except asyncio.CancelledError:
                await asyncio.shield(close_task)
                raise
            if not result["disconnected_cleanly"]:
                result["cleanup_errors"].append("disconnect_failed")
                if result["error_code"] is None:
                    result["error_stage"] = "cleanup"
                    result["error_code"] = "disconnect_failed"
    if result["error_code"] is not None or not result["system_id_value_usable"]:
        raw = None
    return result, raw


async def async_probe_system_id(hass: HomeAssistant, address: str) -> dict[str, Any]:
    """Return the privacy-safe status of one standard System ID read."""
    result, _private_raw = await _async_read_system_id_private(hass, address)
    return result
