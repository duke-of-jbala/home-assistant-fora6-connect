"""Development-only bounded identity and one-slot probes through HA Bluetooth.

The Stage 2E action sends only captured wake/project requests. The separately
invoked Stage 2F action can additionally query one raw record slot. Neither
action pairs, decodes measurements, or registers production discovery.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .bluetooth import Fora6BluetoothTransport, TransportError
from .const import CHARACTERISTIC_UUID, SERVICE_UUID
from .protocol import (
    ProtocolFrame,
    build_project_query_request,
    build_first_record_part_one_request,
    build_first_record_part_two_request,
    build_record_slot_count_request,
    build_wake_request,
    parse_project_id,
    parse_record_slot_count,
)

EXPECTED_PROJECT_ID = 0x4183
RESPONSE_TIMEOUT = 15.0


class _ProbeFailure(Exception):
    """Internal failure carrying only stable, non-sensitive categories."""

    def __init__(self, stage: str, code: str) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code


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
    transport = Fora6BluetoothTransport(
        hass, address, response_timeout=RESPONSE_TIMEOUT
    )

    async def exchange(
        request: ProtocolFrame,
        *,
        stage: str,
        write_success_key: str,
        response_valid_key: str,
    ) -> ProtocolFrame:
        """Map transport outcomes to the existing semantic action schema."""
        try:
            response = await transport.async_exchange(request)
        except TransportError as failure:
            if failure.write_succeeded:
                result[write_success_key] = True
            raise _ProbeFailure(stage, failure.code) from None
        result[write_success_key] = True
        result[response_valid_key] = True
        return response

    try:
        await transport.async_connect()
        await transport.async_subscribe()
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
    except TransportError as failure:
        result["error_stage"] = failure.stage
        result["error_code"] = failure.code
    except _ProbeFailure as failure:
        result["error_stage"] = failure.stage
        result["error_code"] = failure.code
    except Exception:
        result["error_stage"] = "probe"
        result["error_code"] = "unexpected_failure"
    finally:
        result["device_found"] = transport.device_resolved
        result["connectable_device_resolved"] = transport.device_resolved
        result["connection_successful"] = transport.connection_established
        result["connected_via_ha_bluetooth"] = transport.connection_established
        result["custom_characteristic_found"] = transport.characteristic_found
        result["notification_subscription_successful"] = (
            transport.subscription_established
        )
        cleanup = await transport.async_close()
        result["notification_stopped_cleanly"] = (
            cleanup.notification_stopped_cleanly
        )
        result["disconnected_cleanly"] = cleanup.disconnected_cleanly
        result["cleanup_errors"].extend(cleanup.errors)

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
