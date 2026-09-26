"""Temporary Stage 1C notification metadata observer; no application I/O."""

from __future__ import annotations

import asyncio
import hashlib
import time
from typing import Any

from bleak_retry_connector import (
    BleakClientWithServiceCache,
    BleakOutOfConnectionSlotsError,
    establish_connection,
)
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import CHARACTERISTIC_UUID, NAME, SERVICE_UUID
from .gatt_probe import CONNECTION_TIMEOUT, DISCONNECT_TIMEOUT

GLUCOSE_SERVICE_UUID = "00001808-0000-1000-8000-00805f9b34fb"
GLUCOSE_MEASUREMENT_UUID = "00002a18-0000-1000-8000-00805f9b34fb"
GLUCOSE_CONTEXT_UUID = "00002a34-0000-1000-8000-00805f9b34fb"
TARGETS = (
    (GLUCOSE_SERVICE_UUID, GLUCOSE_MEASUREMENT_UUID),
    (GLUCOSE_SERVICE_UUID, GLUCOSE_CONTEXT_UUID),
    (SERVICE_UUID, CHARACTERISTIC_UUID),
)
OBSERVATION_SECONDS = 30
NOTIFY_TIMEOUT = 10.0


class ObservationError(Exception):
    """A privacy-safe failure for the development action."""


def _subscription_error(error: Exception) -> str:
    """Report only a structured error class/code, never upstream private text."""
    error_class = type(error).__name__
    if not error_class.isidentifier() or len(error_class) > 80:
        error_class = "BluetoothError"
    # BleakDBusError exposes the D-Bus error name independently of its message.
    code = getattr(error, "dbus_error", None)
    if (
        isinstance(code, str)
        and len(code) <= 100
        and all(part.isidentifier() for part in code.split("."))
    ):
        return f"{error_class} ({code})"
    return error_class


def _find_targets(services: Any) -> list[Any]:
    """Find the three observed Notify characteristics in their services."""
    by_service = {str(service.uuid).lower(): service for service in services}
    found = []
    for service_uuid, characteristic_uuid in TARGETS:
        service = by_service.get(service_uuid)
        characteristic = None
        if service is not None:
            characteristic = next(
                (
                    item
                    for item in service.characteristics
                    if str(item.uuid).lower() == characteristic_uuid
                ),
                None,
            )
        if characteristic is None or "notify" not in {
            str(prop).lower() for prop in characteristic.properties
        }:
            raise ObservationError(
                f"Expected Notify characteristic {characteristic_uuid} is unavailable."
            )
        found.append(characteristic)
    return found


async def async_observe_notifications(
    hass: HomeAssistant, address: str
) -> dict[str, Any]:
    """Connect through HA, observe bounded notification metadata, and clean up."""
    try:
        ble_device = bluetooth.async_ble_device_from_address(
            hass, address, connectable=True
        )
    except Exception:
        raise ObservationError(
            "Home Assistant could not resolve a connectable BLEDevice."
        ) from None
    if ble_device is None:
        raise ObservationError("No connectable BLEDevice is available.")

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
        raise ObservationError(
            "No Bluetooth proxy/adapter connection slot is available."
        ) from None
    except Exception:
        raise ObservationError(
            "Bluetooth connection failed or the device disappeared."
        ) from None

    length_counts = {uuid: {} for _, uuid in TARGETS}
    payload_digests = {uuid: set() for _, uuid in TARGETS}
    notification_counts = {uuid: 0 for _, uuid in TARGETS}
    subscription_errors: dict[str, str | None] = {uuid: None for _, uuid in TARGETS}
    started: list[Any] = []
    accepting = True
    elapsed = 0.0
    failure: ObservationError | None = None
    unsubscribe_failed = False
    disconnect_failed = False

    def callback_for(uuid: str):
        def on_notification(_sender: Any, data: bytearray) -> None:
            if not accepting:
                return
            notification_counts[uuid] += 1
            size = len(data)
            length_counts[uuid][size] = length_counts[uuid].get(size, 0) + 1
            payload_digests[uuid].add(hashlib.sha256(data).digest())

        return on_notification

    try:
        if not client.is_connected:
            raise ObservationError("The meter disconnected before GATT inspection.")
        if client.services is None:
            raise ObservationError("GATT services were unavailable after connection.")
        characteristics = _find_targets(client.services)
        for characteristic in characteristics:
            uuid = str(characteristic.uuid).lower()
            try:
                await asyncio.wait_for(
                    client.start_notify(characteristic, callback_for(uuid)),
                    timeout=NOTIFY_TIMEOUT,
                )
            except Exception as err:
                subscription_errors[uuid] = _subscription_error(err)
                continue
            started.append(characteristic)
        if started:
            started_at = time.monotonic()
            await asyncio.sleep(OBSERVATION_SECONDS)
            elapsed = time.monotonic() - started_at
            if not client.is_connected:
                raise ObservationError("The meter disconnected during observation.")
    except ObservationError as err:
        failure = err
    except Exception:
        failure = ObservationError("Notification observation failed.")
    finally:
        accepting = False
        try:
            for characteristic in reversed(started):
                try:
                    await asyncio.wait_for(
                        client.stop_notify(characteristic), timeout=NOTIFY_TIMEOUT
                    )
                except Exception:
                    unsubscribe_failed = True
        finally:
            try:
                await asyncio.wait_for(client.disconnect(), timeout=DISCONNECT_TIMEOUT)
            except Exception:
                disconnect_failed = True

    if failure is not None:
        raise failure
    result = {
        "device_found": True,
        "connectable_device_resolved": True,
        "connection_successful": True,
        "connected_via_ha_bluetooth": True,
        "observation_duration_seconds": round(elapsed, 3),
        "subscriptions_attempted": len(TARGETS),
        "subscriptions_successful": len(started),
        "notifications_observed": sum(notification_counts.values()),
        "characteristics": [
            {
                "uuid": uuid,
                "subscription_successful": subscription_errors[uuid] is None,
                "subscription_error": subscription_errors[uuid],
                "notification_count": notification_counts[uuid],
                "payload_lengths": sorted(length_counts[uuid]),
                "length_counts": {
                    str(size): count
                    for size, count in sorted(length_counts[uuid].items())
                },
                "distinct_payload_count": len(payload_digests[uuid]),
            }
            for _, uuid in TARGETS
        ],
        "subscriptions_stopped_cleanly": not unsubscribe_failed,
        "disconnected_cleanly": not disconnect_failed,
    }
    for digests in payload_digests.values():
        digests.clear()
    return result
