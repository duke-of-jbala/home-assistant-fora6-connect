"""Explicit, bounded current uric-acid refresh for one configured GD82."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from .bluetooth import Fora6BluetoothTransport, TransportError
from .mac_identity import canonical_bluetooth_mac, is_mac_identity
from .measurement import Fora6Measurement, measurement_from_record
from .models import TD4183Record, combine_td4183_record
from .protocol import (
    FrameError,
    ProtocolFrame,
    TD4183Analyte,
    TD4183RecordCategory,
    build_first_record_part_one_request,
    build_first_record_part_two_request,
    build_second_record_part_one_request,
    build_second_record_part_two_request,
    build_third_record_part_one_request,
    build_third_record_part_two_request,
    build_fourth_record_part_one_request,
    build_fourth_record_part_two_request,
    build_project_query_request,
    build_record_slot_count_request,
    build_wake_request,
    parse_project_id,
    parse_record_newest_index,
    parse_record_slot_count,
    parse_td4183_record_part_one,
    parse_td4183_record_part_two,
)
from .sensor_state import MeterRuntime, measurement_native_value

PROJECT_ID = 0x4183
RESPONSE_TIMEOUT = 15.0
_REQUEST_PAIRS = (
    (build_first_record_part_one_request, build_first_record_part_two_request),
    (build_second_record_part_one_request, build_second_record_part_two_request),
    (build_third_record_part_one_request, build_third_record_part_two_request),
    (build_fourth_record_part_one_request, build_fourth_record_part_two_request),
)


class _RefreshFailure(Exception):
    def __init__(self, stage: str, code: str) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code


def _eligible(record: TD4183Record) -> bool:
    return (
        record.analyte is TD4183Analyte.URIC_ACID
        and record.category is TD4183RecordCategory.GENERAL
        and record.is_valid_value
        and not record.is_qc
    )


def _select_primary(records: tuple[TD4183Record, ...]) -> tuple[int, Fora6Measurement, int]:
    """Select only within this complete two- or four-slot snapshot."""
    if len(records) not in (2, 4):
        raise _RefreshFailure("metadata", "unsupported_history_count")
    for index in range(1, len(records), 2):
        companion = records[index]
        if companion.category is not TD4183RecordCategory.QC or companion.is_valid_value:
            raise _RefreshFailure("record", "unexpected_companion")
    candidates = [(index, records[index]) for index in range(0, len(records), 2) if _eligible(records[index])]
    if not candidates:
        raise _RefreshFailure("selection", "no_valid_uric_acid_primary")
    if len(candidates) == 2:
        first_time = candidates[0][1].meter_local_time.as_naive_datetime()
        second_time = candidates[1][1].meter_local_time.as_naive_datetime()
        if first_time == second_time:
            raise _RefreshFailure("selection", "ambiguous_meter_local_time")
        selected = candidates[0] if first_time > second_time else candidates[1]
    else:
        selected = candidates[0]
    measurement = measurement_from_record(selected[1])
    if measurement_native_value(measurement) is None:
        raise _RefreshFailure("selection", "invalid_measurement")
    return selected[0], measurement, len(candidates)


class Fora6CurrentRefreshCoordinator:
    """One manual session at a time; commit state only after full cleanup."""

    def __init__(self, hass: Any, entry: Any, runtime: MeterRuntime) -> None:
        self._hass = hass
        self._entry = entry
        self._runtime = runtime
        self._lock = asyncio.Lock()

    async def async_refresh(self) -> dict[str, Any]:
        prior_valid = self._runtime.measurement_state.native_value is not None
        result: dict[str, Any] = {
            "refresh_performed": False,
            "refresh_successful": False,
            "supported_raw_slot_count": False,
            "sensor_updated": False,
            "retained_previous_state": prior_valid,
            "ambiguity_detected": False,
            "error_stage": None,
            "error_code": None,
            "cleanup_errors": [],
        }
        if self._lock.locked():
            result.update(error_stage="refresh", error_code="already_running")
            return result
        async with self._lock:
            # The configured canonical factory MAC must match the locator.
            if not is_mac_identity(self._entry.unique_id) or (
                canonical_bluetooth_mac(self._runtime.address) != self._entry.unique_id
            ):
                result.update(error_stage="identity", error_code="identity_mismatch")
                return result
            transport = Fora6BluetoothTransport(
                self._hass, self._runtime.address, response_timeout=RESPONSE_TIMEOUT
            )
            selected: tuple[int, Fora6Measurement, int] | None = None

            async def exchange(request: ProtocolFrame, stage: str) -> ProtocolFrame:
                try:
                    return await transport.async_exchange(request)
                except TransportError as failure:
                    raise _RefreshFailure(stage, failure.code) from None

            async def read_pair(index: int) -> TD4183Record:
                first_builder, second_builder = _REQUEST_PAIRS[index]
                first = await exchange(first_builder(), "record_part_1")
                try:
                    part_one = parse_td4183_record_part_one(first)
                except FrameError:
                    raise _RefreshFailure("record_part_1", "invalid_response") from None
                second = await exchange(second_builder(), "record_part_2")
                try:
                    part_two = parse_td4183_record_part_two(second)
                except FrameError:
                    raise _RefreshFailure("record_part_2", "invalid_response") from None
                return combine_td4183_record(part_one, part_two)

            try:
                await transport.async_connect()
                await transport.async_subscribe()
                await exchange(build_wake_request(), "wake")
                project_frame = await exchange(build_project_query_request(), "project")
                try:
                    project = parse_project_id(project_frame)
                except FrameError:
                    raise _RefreshFailure("project", "invalid_response") from None
                if project != PROJECT_ID:
                    raise _RefreshFailure("project", "unexpected_project_id")
                result["refresh_performed"] = True
                metadata = await exchange(build_record_slot_count_request(), "metadata")
                try:
                    count = parse_record_slot_count(metadata)
                    parse_record_newest_index(metadata)
                except FrameError:
                    raise _RefreshFailure("metadata", "invalid_response") from None
                result["raw_slot_count"] = count
                if count not in (2, 4):
                    raise _RefreshFailure("metadata", "unsupported_history_count")
                result["supported_raw_slot_count"] = True
                indexes = (0, 1) if count == 2 else (0, 1, 2, 3)
                records = tuple([await read_pair(index) for index in indexes])
                selected = _select_primary(records)
            except TransportError as failure:
                result.update(error_stage=failure.stage, error_code=failure.code)
            except _RefreshFailure as failure:
                result.update(error_stage=failure.stage, error_code=failure.code)
                result["ambiguity_detected"] = failure.code == "ambiguous_meter_local_time"
            except Exception:
                result.update(error_stage="refresh", error_code="unexpected_failure")
            finally:
                try:
                    cleanup = await transport.async_close()
                    result["cleanup_errors"] = list(cleanup.errors)
                    if selected is not None and not (
                        cleanup.notification_stopped_cleanly and cleanup.disconnected_cleanly
                    ):
                        result["cleanup_errors"].append("incomplete_cleanup")
                except Exception:
                    result["cleanup_errors"] = ["cleanup_failed"]
            if result["cleanup_errors"] and result["error_code"] is None:
                result.update(error_stage="cleanup", error_code=result["cleanup_errors"][0])
            if selected is None or result["error_code"] is not None:
                return result
            index, measurement, eligible_count = selected
            self._runtime.measurement_state.replace(measurement)
            self._runtime.synchronized_at = datetime.now(timezone.utc)
            result.update(
                refresh_successful=True,
                sensor_updated=True,
                retained_previous_state=False,
                selected_primary_index=index,
                eligible_primary_count=eligible_count,
                selected_measurement_time_local=measurement.meter_local_time.strftime("%Y-%m-%d %H:%M"),
                selected_uric_acid_value_mg_dl=float(measurement.scaled_number),
            )
            return result
