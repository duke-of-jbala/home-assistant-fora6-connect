"""Development-only semantic check of the fixed TD4183 two-slot branch.

Parsed records remain private in memory. The action returns status booleans only.
"""

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
    """Carry a stable, privacy-safe failure stage and code."""

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
        "semantic_probe_performed": False,
        "requested_indexes": [],
        "repeated_index_1_semantics_equal": None,
        "repeated_index_1_analyte_equal": None,
        "repeated_index_1_category_equal": None,
        "repeated_index_1_validity_equal": None,
        "expected_index_0_semantics_match": False,
        "expected_index_1_semantics_match": False,
        "expected_semantic_pattern_confirmed": False,
        "notification_stopped_cleanly": False,
        "disconnected_cleanly": False,
        "error_stage": None,
        "error_code": None,
        "cleanup_errors": [],
    }
    for name in ("index_0", "index_1_first", "index_1_second"):
        result[f"{name}_pair_complete"] = False
        result[f"{name}_analyte_identified"] = False
    result.update({
        "index_0_is_uric_acid": False,
        "index_0_category_is_general": False,
        "index_0_value_valid": False,
        "index_0_is_qc": False,
    })
    for name in ("index_1_first", "index_1_second"):
        result[f"{name}_is_hematocrit"] = False
        result[f"{name}_category_is_qc"] = False
        result[f"{name}_value_invalid_sentinel"] = False
        result[f"{name}_is_qc"] = False
    return result


async def async_probe_history_semantics(
    hass: HomeAssistant, address: str
) -> dict[str, Any]:
    """Classify only the fixed User1 1 -> 0 -> 1 record pairs."""
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
        name: str,
        index: int,
        first_request: ProtocolFrame,
        second_request: ProtocolFrame,
    ) -> TD4183Record:
        # Only the three literal calls below can select an index.
        result["requested_indexes"].append(index)
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
        result[f"{name}_analyte_identified"] = record.analyte is not None
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
            result["traversal_gate_passed"] = True
            first_one = await read_pair(
                "index_1_first", 1,
                build_second_record_part_one_request(),
                build_second_record_part_two_request(),
            )
            zero = await read_pair(
                "index_0", 0,
                build_first_record_part_one_request(),
                build_first_record_part_two_request(),
            )
            second_one = await read_pair(
                "index_1_second", 1,
                build_second_record_part_one_request(),
                build_second_record_part_two_request(),
            )

            result["index_0_is_uric_acid"] = zero.analyte is TD4183Analyte.URIC_ACID
            result["index_0_category_is_general"] = (
                zero.category is TD4183RecordCategory.GENERAL
            )
            result["index_0_value_valid"] = zero.is_valid_value
            result["index_0_is_qc"] = zero.is_qc
            result["expected_index_0_semantics_match"] = (
                result["index_0_is_uric_acid"]
                and result["index_0_category_is_general"]
                and result["index_0_value_valid"]
                and not result["index_0_is_qc"]
            )

            for name, record in (
                ("index_1_first", first_one),
                ("index_1_second", second_one),
            ):
                result[f"{name}_is_hematocrit"] = (
                    record.analyte is TD4183Analyte.HEMATOCRIT
                )
                result[f"{name}_category_is_qc"] = (
                    record.category is TD4183RecordCategory.QC
                )
                result[f"{name}_value_invalid_sentinel"] = not record.is_valid_value
                result[f"{name}_is_qc"] = record.is_qc

            result["repeated_index_1_analyte_equal"] = (
                first_one.analyte == second_one.analyte
                and first_one.analyte_code == second_one.analyte_code
            )
            result["repeated_index_1_category_equal"] = (
                first_one.category is second_one.category
            )
            result["repeated_index_1_validity_equal"] = (
                first_one.is_valid_value == second_one.is_valid_value
            )
            result["repeated_index_1_semantics_equal"] = (
                result["repeated_index_1_analyte_equal"]
                and result["repeated_index_1_category_equal"]
                and result["repeated_index_1_validity_equal"]
            )
            result["expected_index_1_semantics_match"] = all(
                result[f"{name}_is_hematocrit"]
                and result[f"{name}_category_is_qc"]
                and result[f"{name}_value_invalid_sentinel"]
                and result[f"{name}_is_qc"]
                for name in ("index_1_first", "index_1_second")
            )
            result["expected_semantic_pattern_confirmed"] = (
                result["expected_index_0_semantics_match"]
                and result["expected_index_1_semantics_match"]
                and result["repeated_index_1_semantics_equal"]
            )
            result["semantic_probe_performed"] = True
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
