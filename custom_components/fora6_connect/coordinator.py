"""Explicit, bounded current uric-acid refresh for one configured GD82."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .bluetooth import Fora6BluetoothTransport, TransportError
from .bounded_records import (
    RESPONSE_TIMEOUT,
    REQUEST_PAIRS,
    BoundedReadError,
    BoundedReadProgress,
    async_read_bounded_records,
    eligible_primary,
    validate_companions,
)
from .mac_identity import canonical_bluetooth_mac, is_mac_identity
from .measurement import Fora6Measurement, measurement_from_record
from .models import TD4183Record
from .sensor_state import MeterRuntime, measurement_native_value

_REQUEST_PAIRS = REQUEST_PAIRS
_eligible = eligible_primary


class _RefreshFailure(Exception):
    def __init__(self, stage: str, code: str) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code


def _select_primary(records: tuple[TD4183Record, ...]) -> tuple[int, Fora6Measurement, int]:
    """Select only within this complete two- or four-slot snapshot."""
    if len(records) not in (2, 4):
        raise _RefreshFailure("metadata", "unsupported_history_count")
    validate_companions(records)
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
        self._lock = runtime.gatt_lock

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
            progress = BoundedReadProgress()

            try:
                await transport.async_connect()
                await transport.async_subscribe()
                records = await async_read_bounded_records(transport, progress)
                selected = _select_primary(records)
            except TransportError as failure:
                result.update(error_stage=failure.stage, error_code=failure.code)
            except (BoundedReadError, _RefreshFailure) as failure:
                result.update(error_stage=failure.stage, error_code=failure.code)
                result["ambiguity_detected"] = failure.code == "ambiguous_meter_local_time"
            except Exception:
                result.update(error_stage="refresh", error_code="unexpected_failure")
            finally:
                result["refresh_performed"] = progress.project_confirmed
                result["supported_raw_slot_count"] = progress.supported_raw_slot_count
                if progress.raw_slot_count is not None:
                    result["raw_slot_count"] = progress.raw_slot_count
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
