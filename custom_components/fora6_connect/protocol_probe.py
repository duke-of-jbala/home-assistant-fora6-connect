"""Development-only bounded identity and one-slot probes through HA Bluetooth.

The Stage 2E action sends only captured wake/project requests. The separately
invoked Stage 2F action can additionally query one raw record slot. Neither
action pairs, decodes measurements, or registers production discovery.
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

from .const import CHARACTERISTIC_UUID, NAME, SERVICE_UUID
from .gatt_probe import CONNECTION_TIMEOUT, DISCONNECT_TIMEOUT
from .protocol import (
    ProtocolFrame,
    build_project_query_request,
    build_first_record_part_one_request,
    build_first_record_part_two_request,
    build_record_slot_count_request,
    build_wake_request,
    parse_project_id,
    parse_record_slot_count,
    validate_response_echo,
)

EXPECTED_PROJECT_ID = 0x4183
CONNECT_TOTAL_TIMEOUT = 50.0
NOTIFY_TIMEOUT = 10.0
WRITE_TIMEOUT = 10.0
RESPONSE_TIMEOUT = 15.0


class _ProbeFailure(Exception):
    """Internal failure carrying only stable, non-sensitive categories."""

    def __init__(self, stage: str, code: str) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code


def _custom_characteristic(services: Any) -> Any:
    """Select only the custom characteristic with Write and Notify properties."""
    try:
        service = next(
            item for item in services if str(item.uuid).lower() == SERVICE_UUID
        )
        characteristic = next(
            item
            for item in service.characteristics
            if str(item.uuid).lower() == CHARACTERISTIC_UUID
        )
        properties = {str(prop).lower() for prop in characteristic.properties}
    except (AttributeError, StopIteration, TypeError):
        raise _ProbeFailure("gatt", "custom_characteristic_missing") from None
    if not {"write", "notify"} <= properties:
        raise _ProbeFailure("gatt", "custom_properties_missing")
    return characteristic


def _empty_result(*, record_probe: bool = False) -> dict[str, Any]:
    """Create a privacy-safe response with no runtime identifiers or bytes."""
    result = {
        "device_found": False,
        "connectable_device_resolved": False,
        "connection_successful": False,
        "connected_via_ha_bluetooth": False,
        "custom_characteristic_found": False,
        "notification_subscription_successful": False,
        "wake_write_successful": False,
        "wake_response_valid": False,
        "project_query_write_successful": False,
        "project_response_valid": False,
        "project_id": None,
        "expected_project_id": EXPECTED_PROJECT_ID,
        "project_id_matches": False,
        "notification_stopped_cleanly": False,
        "disconnected_cleanly": False,
        "identity_confirmed": False,
        "error_stage": None,
        "error_code": None,
        "cleanup_errors": [],
    }
    if record_probe:
        result.update(
            {
                "record_metadata_query_performed": False,
                "record_metadata_response_valid": False,
                "record_slot_available": False,
                "requested_record_index": None,
                "record_part_1_requested": False,
                "record_part_1_valid": False,
                "record_part_2_requested": False,
                "record_part_2_valid": False,
                "record_pair_complete": False,
                "analyte_identified": False,
                "analyte_type": None,
                "measurement_field_decoded": False,
                "uric_acid_scaling_applied": False,
                "record_retrieval_confirmed": False,
            }
        )
    return result


async def async_probe_protocol_identity(
    hass: HomeAssistant, address: str, *, _record_probe: bool = False
) -> dict[str, Any]:
    """Run bounded identity, optionally followed by one raw-slot exchange."""
    result = _empty_result(record_probe=_record_probe)
    client: Any = None
    characteristic: Any = None
    subscribed = False
    pending_request: ProtocolFrame | None = None
    pending_response: asyncio.Future[ProtocolFrame | None] | None = None

    def on_notification(_sender: Any, data: bytearray) -> None:
        """Validate an ephemeral frame without logging or returning its bytes."""
        current_request = pending_request
        current_future = pending_response
        if current_request is None or current_future is None or current_future.done():
            return
        try:
            frame = ProtocolFrame(bytes(data))
            validate_response_echo(current_request, frame)
        except Exception:
            # Callback failures must remain private and fail the active exchange.
            current_future.set_result(None)
            return
        current_future.set_result(frame)

    async def exchange(
        request: ProtocolFrame,
        *,
        stage: str,
        write_success_key: str,
        response_valid_key: str,
    ) -> ProtocolFrame:
        """Write once and await one matching, validated notification."""
        nonlocal pending_request, pending_response
        if not client.is_connected:
            raise _ProbeFailure(stage, "peer_disconnected")
        future: asyncio.Future[ProtocolFrame | None] = (
            asyncio.get_running_loop().create_future()
        )
        pending_request = request
        pending_response = future
        try:
            try:
                await asyncio.wait_for(
                    client.write_gatt_char(
                        characteristic, request.data, response=True
                    ),
                    timeout=WRITE_TIMEOUT,
                )
            except Exception:
                raise _ProbeFailure(stage, "write_failed") from None
            result[write_success_key] = True
            try:
                response = await asyncio.wait_for(future, timeout=RESPONSE_TIMEOUT)
            except TimeoutError:
                raise _ProbeFailure(stage, "response_timeout") from None
            if response is None:
                raise _ProbeFailure(stage, "invalid_response")
            if not client.is_connected:
                raise _ProbeFailure(stage, "peer_disconnected")
            result[response_valid_key] = True
            return response
        finally:
            pending_request = None
            pending_response = None

    try:
        try:
            ble_device = bluetooth.async_ble_device_from_address(
                hass, address, connectable=True
            )
        except Exception:
            raise _ProbeFailure("resolution", "resolution_failed") from None
        if ble_device is None:
            raise _ProbeFailure("resolution", "no_connectable_device")
        result["device_found"] = True
        result["connectable_device_resolved"] = True

        try:
            client = await asyncio.wait_for(
                establish_connection(
                    BleakClientWithServiceCache,
                    ble_device,
                    NAME,
                    max_attempts=2,
                    use_services_cache=False,
                    timeout=CONNECTION_TIMEOUT,
                    pair=False,
                ),
                timeout=CONNECT_TOTAL_TIMEOUT,
            )
        except BleakOutOfConnectionSlotsError:
            raise _ProbeFailure("connection", "no_connection_slot") from None
        except Exception:
            raise _ProbeFailure("connection", "connection_failed") from None
        if not client.is_connected:
            raise _ProbeFailure("connection", "peer_disconnected")
        result["connection_successful"] = True
        result["connected_via_ha_bluetooth"] = True

        if client.services is None:
            raise _ProbeFailure("gatt", "services_unavailable")
        characteristic = _custom_characteristic(client.services)
        result["custom_characteristic_found"] = True

        try:
            await asyncio.wait_for(
                client.start_notify(characteristic, on_notification),
                timeout=NOTIFY_TIMEOUT,
            )
        except Exception:
            raise _ProbeFailure("subscription", "subscription_failed") from None
        subscribed = True
        result["notification_subscription_successful"] = True

        await exchange(
            build_wake_request(),
            stage="wake",
            write_success_key="wake_write_successful",
            response_valid_key="wake_response_valid",
        )
        project_response = await exchange(
            build_project_query_request(),
            stage="project",
            write_success_key="project_query_write_successful",
            response_valid_key="project_response_valid",
        )
        project_id = parse_project_id(project_response)
        result["project_id"] = project_id
        result["project_id_matches"] = project_id == EXPECTED_PROJECT_ID
        if not result["project_id_matches"]:
            raise _ProbeFailure("project", "unexpected_project_id")

        if _record_probe:
            count_response = await exchange(
                build_record_slot_count_request(),
                stage="metadata",
                write_success_key="record_metadata_query_performed",
                response_valid_key="record_metadata_response_valid",
            )
            if parse_record_slot_count(count_response) < 1:
                raise _ProbeFailure("metadata", "no_record_slots")
            result["record_slot_available"] = True
            result["requested_record_index"] = 0
            await exchange(
                build_first_record_part_one_request(),
                stage="record_part_1",
                write_success_key="record_part_1_requested",
                response_valid_key="record_part_1_valid",
            )
            await exchange(
                build_first_record_part_two_request(),
                stage="record_part_2",
                write_success_key="record_part_2_requested",
                response_valid_key="record_part_2_valid",
            )
            result["record_pair_complete"] = True
    except _ProbeFailure as failure:
        result["error_stage"] = failure.stage
        result["error_code"] = failure.code
    except Exception:
        result["error_stage"] = "probe"
        result["error_code"] = "unexpected_failure"
    finally:
        pending_request = None
        pending_response = None
        if subscribed:
            try:
                await asyncio.wait_for(
                    client.stop_notify(characteristic), timeout=NOTIFY_TIMEOUT
                )
                result["notification_stopped_cleanly"] = True
            except Exception:
                result["cleanup_errors"].append("notification_stop_failed")
        if client is not None:
            try:
                await asyncio.wait_for(
                    client.disconnect(), timeout=DISCONNECT_TIMEOUT
                )
                result["disconnected_cleanly"] = True
            except Exception:
                result["cleanup_errors"].append("disconnect_failed")

    if result["cleanup_errors"] and result["error_code"] is None:
        result["error_stage"] = "cleanup"
        result["error_code"] = result["cleanup_errors"][0]
    result["identity_confirmed"] = (
        result["project_id_matches"]
        and result["notification_stopped_cleanly"]
        and result["disconnected_cleanly"]
        and (
            result["error_code"] is None
            or (
                _record_probe
                and result["error_stage"]
                in ("metadata", "record_part_1", "record_part_2")
            )
        )
    )
    if _record_probe:
        result["record_retrieval_confirmed"] = (
            result["identity_confirmed"]
            and result["record_pair_complete"]
            and result["error_code"] is None
        )
    return result


async def async_probe_protocol_record(
    hass: HomeAssistant, address: str
) -> dict[str, Any]:
    """Read one raw slot after the unchanged Stage 2E identity gate."""
    return await async_probe_protocol_identity(hass, address, _record_probe=True)
