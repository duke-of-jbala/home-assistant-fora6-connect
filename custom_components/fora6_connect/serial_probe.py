"""Development-only, bounded Device Information serial read.

The serial and runtime address remain in memory and never enter results,
exceptions, logs, or persistent Home Assistant state.
"""

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

from .const import NAME

DEVICE_INFORMATION_UUID = "0000180a-0000-1000-8000-00805f9b34fb"
SERIAL_NUMBER_UUID = "00002a25-0000-1000-8000-00805f9b34fb"
CONNECTION_TIMEOUT = 20.0
CONNECT_TOTAL_TIMEOUT = 50.0
READ_TIMEOUT = 10.0
DISCONNECT_TIMEOUT = 10.0


class _ProbeFailure(Exception):
    """Internal privacy-safe stage and code only."""

    def __init__(self, stage: str, code: str) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code


async def _disconnect(client: Any) -> bool:
    """Bound disconnect without allowing client exception text to escape."""
    try:
        await asyncio.wait_for(client.disconnect(), timeout=DISCONNECT_TIMEOUT)
    except Exception:
        return False
    return True


def _close_late_client(task: asyncio.Task[Any]) -> None:
    """Own a connector result that arrives after the bounded reap window."""
    try:
        client = task.result()
    except BaseException:
        return
    asyncio.create_task(_disconnect(client))


async def _reap_connector(task: asyncio.Task[Any]) -> None:
    """Cancel the connector and close a client returned despite cancellation."""
    if not task.done():
        task.cancel()
    try:
        client = await asyncio.wait_for(
            asyncio.shield(task), timeout=CONNECT_TOTAL_TIMEOUT
        )
    except asyncio.CancelledError:
        return
    except TimeoutError:
        task.add_done_callback(_close_late_client)
        task.cancel()
        return
    except Exception:
        return
    await _disconnect(client)


async def _connect(device: Any) -> Any:
    task = asyncio.create_task(
        establish_connection(
            BleakClientWithServiceCache,
            device,
            NAME,
            max_attempts=2,
            use_services_cache=False,
            timeout=CONNECTION_TIMEOUT,
            pair=False,
        )
    )
    try:
        return await asyncio.wait_for(
            asyncio.shield(task), timeout=CONNECT_TOTAL_TIMEOUT
        )
    except asyncio.CancelledError:
        await _reap_connector(task)
        raise
    except BleakOutOfConnectionSlotsError:
        raise _ProbeFailure("connection", "no_connection_slot") from None
    except Exception:
        await _reap_connector(task)
        raise _ProbeFailure("connection", "connection_failed") from None


def _usable_serial(raw: bytes) -> tuple[bool, bool]:
    """Classify text without retaining or exposing its contents."""
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False, False
    stripped = decoded.strip("\x00 \t\r\n")
    return True, bool(stripped) and all(char.isprintable() for char in stripped)


async def async_probe_serial_identity(
    hass: HomeAssistant, address: str
) -> dict[str, Any]:
    """Resolve, read standard 0x2A25 once, and return only safe booleans."""
    result: dict[str, Any] = {
        "device_found": False,
        "connectable_device_resolved": False,
        "connection_successful": False,
        "device_information_service_found": False,
        "serial_characteristic_found": False,
        "serial_readable": False,
        "serial_read_successful": False,
        "serial_value_present": False,
        "serial_value_nonempty": False,
        "serial_value_utf8_valid": False,
        "serial_value_usable": False,
        "disconnected_cleanly": False,
        "error_stage": None,
        "error_code": None,
        "cleanup_errors": [],
    }
    client = None
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
            services = client.services
            service = next(
                (item for item in services if str(item.uuid).lower() == DEVICE_INFORMATION_UUID),
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
                    if str(item.uuid).lower() == SERIAL_NUMBER_UUID
                ),
                None,
            )
        except Exception:
            raise _ProbeFailure("gatt", "characteristics_unavailable") from None
        if characteristic is None:
            raise _ProbeFailure("gatt", "serial_characteristic_missing")
        result["serial_characteristic_found"] = True
        try:
            readable = "read" in {
                str(prop).lower() for prop in characteristic.properties
            }
        except Exception:
            readable = False
        if not readable:
            raise _ProbeFailure("gatt", "serial_not_readable")
        result["serial_readable"] = True
        try:
            raw = bytes(
                await asyncio.wait_for(
                    client.read_gatt_char(characteristic), timeout=READ_TIMEOUT
                )
            )
        except Exception:
            raise _ProbeFailure("read", "serial_read_failed") from None
        result["serial_read_successful"] = True
        result["serial_value_present"] = bool(raw)
        utf8_valid, usable = _usable_serial(raw)
        result["serial_value_utf8_valid"] = utf8_valid
        result["serial_value_nonempty"] = usable
        result["serial_value_usable"] = usable
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
    return result
