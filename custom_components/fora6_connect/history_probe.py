"""Development-only, count-gated TD4183 two-slot traversal observation.

No measurement, timestamp, raw frame, identifier, or record fingerprint leaves
this function. The fixed three-pair plan is not a production history loop.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .bluetooth import Fora6BluetoothTransport, TransportError
from .protocol import (
    FrameError,
    ProtocolFrame,
    build_first_record_part_one_request,
    build_first_record_part_two_request,
    build_project_query_request,
    build_record_slot_count_request,
    build_second_record_part_one_request,
    build_second_record_part_two_request,
    build_wake_request,
    parse_project_id,
    parse_record_newest_index,
    parse_record_slot_count,
    parse_td4183_record_part_one,
    parse_td4183_record_part_two,
)

EXPECTED_PROJECT_ID = 0x4183
EXPECTED_RAW_SLOT_COUNT = 2
RESPONSE_TIMEOUT = 15.0


class _ProbeFailure(Exception):
    """Carry only a stable stage and privacy-safe failure code."""

    def __init__(self, stage: str, code: str) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code


def _empty_result() -> dict[str, Any]:
    result: dict[str, Any] = {
        "device_found": False,
        "connectable_device_resolved": False,
        "connection_successful": False,
        "custom_characteristic_found": False,
        "notification_subscription_successful": False,
        "wake_response_valid": False,
        "project_response_valid": False,
        "project_id_matches": False,
        "identity_confirmed": False,
        "record_metadata_query_performed": False,
        "record_metadata_response_valid": False,
        "expected_raw_slot_count": EXPECTED_RAW_SLOT_COUNT,
        "raw_slot_count_matches_expected": False,
        "traversal_gate_passed": False,
        "traversal_performed": False,
        "requested_indexes": [],
        "repeated_index_1_part_1_equal": None,
        "repeated_index_1_part_2_equal": None,
        "repeated_index_1_pair_equal": None,
        "notification_stopped_cleanly": False,
        "disconnected_cleanly": False,
        "error_stage": None,
        "error_code": None,
        "cleanup_errors": [],
    }
    for name in ("index_1_first", "index_0", "index_1_second"):
        result[f"{name}_part_1_valid"] = False
        result[f"{name}_part_2_valid"] = False
        result[f"{name}_pair_complete"] = False
    return result


async def async_probe_history_window(
    hass: HomeAssistant, address: str
) -> dict[str, Any]:
    """Read only the app-captured 1 -> 0 -> 1 branch when raw count is two."""
    result = _empty_result()
    transport = Fora6BluetoothTransport(
        hass, address, response_timeout=RESPONSE_TIMEOUT
    )

    async def exchange(request: ProtocolFrame, stage: str) -> ProtocolFrame:
        try:
            return await transport.async_exchange(request)
        except TransportError as failure:
            raise _ProbeFailure(stage, failure.code) from None

    async def read_pair(
        name: str, index: int, first_request: ProtocolFrame, second_request: ProtocolFrame
    ) -> tuple[ProtocolFrame, ProtocolFrame]:
        # This helper is called only by the three literal calls below.
        result["requested_indexes"].append(index)
        first = await exchange(first_request, f"{name}_part_1")
        try:
            parse_td4183_record_part_one(first)
        except FrameError:
            raise _ProbeFailure(f"{name}_part_1", "invalid_response") from None
        result[f"{name}_part_1_valid"] = True
        second = await exchange(second_request, f"{name}_part_2")
        try:
            parse_td4183_record_part_two(second)
        except FrameError:
            raise _ProbeFailure(f"{name}_part_2", "invalid_response") from None
        result[f"{name}_part_2_valid"] = True
        result[f"{name}_pair_complete"] = True
        return first, second

    try:
        await transport.async_connect()
        await transport.async_subscribe()
        await exchange(build_wake_request(), "wake")
        result["wake_response_valid"] = True
        project_response = await exchange(build_project_query_request(), "project")
        try:
            project = parse_project_id(project_response)
        except FrameError:
            raise _ProbeFailure("project", "invalid_response") from None
        result["project_response_valid"] = True
        result["project_id_matches"] = project == EXPECTED_PROJECT_ID
        if not result["project_id_matches"]:
            raise _ProbeFailure("project", "unexpected_project_id")

        result["record_metadata_query_performed"] = True
        metadata = await exchange(build_record_slot_count_request(), "metadata")
        try:
            raw_count = parse_record_slot_count(metadata)
            parse_record_newest_index(metadata)
        except FrameError:
            raise _ProbeFailure("metadata", "invalid_response") from None
        result["record_metadata_response_valid"] = True
        result["raw_slot_count_matches_expected"] = raw_count == EXPECTED_RAW_SLOT_COUNT
        if result["raw_slot_count_matches_expected"]:
            result["traversal_gate_passed"] = True
            first_one = await read_pair(
                "index_1_first", 1,
                build_second_record_part_one_request(),
                build_second_record_part_two_request(),
            )
            await read_pair(
                "index_0", 0,
                build_first_record_part_one_request(),
                build_first_record_part_two_request(),
            )
            second_one = await read_pair(
                "index_1_second", 1,
                build_second_record_part_one_request(),
                build_second_record_part_two_request(),
            )
            result["repeated_index_1_part_1_equal"] = (
                first_one[0].data == second_one[0].data
            )
            result["repeated_index_1_part_2_equal"] = (
                first_one[1].data == second_one[1].data
            )
            result["repeated_index_1_pair_equal"] = (
                result["repeated_index_1_part_1_equal"]
                and result["repeated_index_1_part_2_equal"]
            )
            result["traversal_performed"] = True
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
    )
    return result
