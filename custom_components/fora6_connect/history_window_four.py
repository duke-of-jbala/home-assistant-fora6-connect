"""Development-only fixed four-slot TD4183 observation; no product state."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .bluetooth import Fora6BluetoothTransport, TransportError
from .models import TD4183Record, combine_td4183_record
from .protocol import (
    FrameError,
    ProtocolFrame,
    TD4183RecordCategory,
    build_first_record_part_one_request,
    build_first_record_part_two_request,
    build_fourth_record_part_one_request,
    build_fourth_record_part_two_request,
    build_project_query_request,
    build_record_slot_count_request,
    build_second_record_part_one_request,
    build_second_record_part_two_request,
    build_third_record_part_one_request,
    build_third_record_part_two_request,
    build_wake_request,
    parse_project_id,
    parse_record_newest_index,
    parse_record_slot_count,
    parse_td4183_record_part_one,
    parse_td4183_record_part_two,
)

EXPECTED_PROJECT_ID = 0x4183
EXPECTED_RAW_SLOT_COUNT = 4
RESPONSE_TIMEOUT = 15.0


class _ProbeFailure(Exception):
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
        "identity_confirmed": False,
        "project_id_matches": False,
        "record_metadata_query_performed": False,
        "record_metadata_response_valid": False,
        "expected_raw_slot_count": EXPECTED_RAW_SLOT_COUNT,
        "raw_slot_count_matches_expected": False,
        "traversal_gate_passed": False,
        "traversal_performed": False,
        "requested_indexes": [],
        "group_0_pairing_structurally_valid": False,
        "group_1_pairing_structurally_valid": False,
        "index_0_and_1_time_equal": None,
        "index_2_and_3_time_equal": None,
        "repeated_index_3_part_1_equal": None,
        "repeated_index_3_part_2_equal": None,
        "repeated_index_3_pair_equal": None,
        "repeated_index_3_analyte_equal": None,
        "repeated_index_3_category_equal": None,
        "repeated_index_3_validity_equal": None,
        "repeated_index_3_semantics_equal": None,
        "notification_stopped_cleanly": False,
        "disconnected_cleanly": False,
        "error_stage": None,
        "error_code": None,
        "cleanup_errors": [],
    }
    for name in ("index_0", "index_1", "index_2", "index_3_first", "index_3_second"):
        result[f"{name}_part_1_valid"] = False
        result[f"{name}_part_2_valid"] = False
        result[f"{name}_pair_complete"] = False
        result[f"{name}_analyte_identified"] = False
        result[f"{name}_category_is_general"] = False
        result[f"{name}_category_is_qc"] = False
        result[f"{name}_value_valid"] = False
        result[f"{name}_is_qc"] = False
    return result


async def async_probe_history_window_four(
    hass: HomeAssistant, address: str
) -> dict[str, Any]:
    """Read only User1 indexes 3 -> 0 -> 1 -> 2 -> 3 when count is four."""
    result = _empty_result()
    transport = Fora6BluetoothTransport(hass, address, response_timeout=RESPONSE_TIMEOUT)

    async def exchange(request: ProtocolFrame, stage: str) -> ProtocolFrame:
        try:
            return await transport.async_exchange(request)
        except TransportError as failure:
            raise _ProbeFailure(stage, failure.code) from None

    async def read_pair(
        name: str, index: int, first_request: ProtocolFrame, second_request: ProtocolFrame
    ) -> tuple[ProtocolFrame, ProtocolFrame, TD4183Record]:
        # Invoked only at the five literal call sites below.
        result["requested_indexes"].append(index)
        first_frame = await exchange(first_request, f"{name}_part_1")
        try:
            first_part = parse_td4183_record_part_one(first_frame)
        except FrameError:
            raise _ProbeFailure(f"{name}_part_1", "invalid_response") from None
        result[f"{name}_part_1_valid"] = True
        second_frame = await exchange(second_request, f"{name}_part_2")
        try:
            second_part = parse_td4183_record_part_two(second_frame)
        except FrameError:
            raise _ProbeFailure(f"{name}_part_2", "invalid_response") from None
        result[f"{name}_part_2_valid"] = True
        record = combine_td4183_record(first_part, second_part)
        result[f"{name}_pair_complete"] = True
        result[f"{name}_analyte_identified"] = record.analyte is not None
        result[f"{name}_category_is_general"] = record.category is TD4183RecordCategory.GENERAL
        result[f"{name}_category_is_qc"] = record.is_qc
        result[f"{name}_value_valid"] = record.is_valid_value
        result[f"{name}_is_qc"] = record.is_qc
        return first_frame, second_frame, record

    try:
        await transport.async_connect()
        await transport.async_subscribe()
        await exchange(build_wake_request(), "wake")
        project_frame = await exchange(build_project_query_request(), "project")
        try:
            project_id = parse_project_id(project_frame)
        except FrameError:
            raise _ProbeFailure("project", "invalid_response") from None
        result["project_id_matches"] = project_id == EXPECTED_PROJECT_ID
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
            first_three_25, first_three_26, first_three = await read_pair(
                "index_3_first", 3,
                build_fourth_record_part_one_request(),
                build_fourth_record_part_two_request(),
            )
            _, _, zero = await read_pair(
                "index_0", 0,
                build_first_record_part_one_request(),
                build_first_record_part_two_request(),
            )
            _, _, one = await read_pair(
                "index_1", 1,
                build_second_record_part_one_request(),
                build_second_record_part_two_request(),
            )
            _, _, two = await read_pair(
                "index_2", 2,
                build_third_record_part_one_request(),
                build_third_record_part_two_request(),
            )
            second_three_25, second_three_26, second_three = await read_pair(
                "index_3_second", 3,
                build_fourth_record_part_one_request(),
                build_fourth_record_part_two_request(),
            )
            # Structural grouping alone does not prove companion semantics.
            result["group_0_pairing_structurally_valid"] = True
            result["group_1_pairing_structurally_valid"] = True
            result["index_0_and_1_time_equal"] = zero.meter_local_time == one.meter_local_time
            result["index_2_and_3_time_equal"] = two.meter_local_time == first_three.meter_local_time
            result["repeated_index_3_part_1_equal"] = first_three_25.data == second_three_25.data
            result["repeated_index_3_part_2_equal"] = first_three_26.data == second_three_26.data
            result["repeated_index_3_pair_equal"] = (
                result["repeated_index_3_part_1_equal"]
                and result["repeated_index_3_part_2_equal"]
            )
            result["repeated_index_3_analyte_equal"] = (
                first_three.analyte == second_three.analyte
                and first_three.analyte_code == second_three.analyte_code
            )
            result["repeated_index_3_category_equal"] = first_three.category is second_three.category
            result["repeated_index_3_validity_equal"] = first_three.is_valid_value == second_three.is_valid_value
            result["repeated_index_3_semantics_equal"] = (
                result["repeated_index_3_analyte_equal"]
                and result["repeated_index_3_category_equal"]
                and result["repeated_index_3_validity_equal"]
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
        result["notification_subscription_successful"] = transport.subscription_established
        cleanup = await transport.async_close()
        result["notification_stopped_cleanly"] = cleanup.notification_stopped_cleanly
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
