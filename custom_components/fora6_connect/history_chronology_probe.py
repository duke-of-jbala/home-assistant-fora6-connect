"""Development-only comparison of two fixed primary slots; no product state."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .bluetooth import Fora6BluetoothTransport, TransportError
from .models import TD4183Record, combine_td4183_record
from .protocol import (
    FrameError,
    ProtocolFrame,
    TD4183Analyte,
    TD4183RecordCategory,
    build_first_record_part_one_request,
    build_first_record_part_two_request,
    build_project_query_request,
    build_record_slot_count_request,
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
        "chronology_probe_performed": False,
        "chronology_comparison_complete": False,
        "index_0_time_before_index_2": False,
        "index_0_time_equal_index_2": False,
        "index_0_time_after_index_2": False,
        "notification_stopped_cleanly": False,
        "disconnected_cleanly": False,
        "error_stage": None,
        "error_code": None,
        "cleanup_errors": [],
    }
    for name in ("index_0", "index_2"):
        result[f"{name}_pair_complete"] = False
        result[f"{name}_is_uric_acid"] = False
        result[f"{name}_category_is_general"] = False
        result[f"{name}_value_valid"] = False
        result[f"{name}_semantic_match"] = False
    return result


async def async_probe_history_chronology(
    hass: HomeAssistant, address: str
) -> dict[str, Any]:
    """Compare User1 raw primary indexes zero and two only at count four."""
    result = _empty_result()
    transport = Fora6BluetoothTransport(hass, address, response_timeout=RESPONSE_TIMEOUT)

    async def exchange(request: ProtocolFrame, stage: str) -> ProtocolFrame:
        try:
            return await transport.async_exchange(request)
        except TransportError as failure:
            raise _ProbeFailure(stage, failure.code) from None

    async def read_primary(
        name: str, first_request: ProtocolFrame, second_request: ProtocolFrame
    ) -> TD4183Record:
        first_frame = await exchange(first_request, f"{name}_part_1")
        try:
            first_part = parse_td4183_record_part_one(first_frame)
        except FrameError:
            raise _ProbeFailure(f"{name}_part_1", "invalid_response") from None
        second_frame = await exchange(second_request, f"{name}_part_2")
        try:
            second_part = parse_td4183_record_part_two(second_frame)
        except FrameError:
            raise _ProbeFailure(f"{name}_part_2", "invalid_response") from None
        record = combine_td4183_record(first_part, second_part)
        result[f"{name}_pair_complete"] = True
        result[f"{name}_is_uric_acid"] = record.analyte is TD4183Analyte.URIC_ACID
        result[f"{name}_category_is_general"] = record.category is TD4183RecordCategory.GENERAL
        result[f"{name}_value_valid"] = record.is_valid_value
        result[f"{name}_semantic_match"] = (
            result[f"{name}_is_uric_acid"]
            and result[f"{name}_category_is_general"]
            and result[f"{name}_value_valid"]
            and not record.is_qc
        )
        return record

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
            zero = await read_primary(
                "index_0",
                build_first_record_part_one_request(),
                build_first_record_part_two_request(),
            )
            if result["index_0_semantic_match"]:
                two = await read_primary(
                    "index_2",
                    build_third_record_part_one_request(),
                    build_third_record_part_two_request(),
                )
                if result["index_2_semantic_match"]:
                    zero_time = zero.meter_local_time.as_naive_datetime()
                    two_time = two.meter_local_time.as_naive_datetime()
                    result["index_0_time_before_index_2"] = zero_time < two_time
                    result["index_0_time_equal_index_2"] = zero_time == two_time
                    result["index_0_time_after_index_2"] = zero_time > two_time
                    result["chronology_comparison_complete"] = True
                    result["chronology_probe_performed"] = True
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
