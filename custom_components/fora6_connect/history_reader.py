"""Explicit, non-persistent count-two/four uric-acid history response."""

from __future__ import annotations

from typing import Any

from .bluetooth import Fora6BluetoothTransport, TransportError
from .bounded_records import (
    RESPONSE_TIMEOUT,
    BoundedReadError,
    BoundedReadProgress,
    async_read_bounded_records,
    eligible_primary,
    validate_companions,
)
from .mac_identity import canonical_bluetooth_mac, is_mac_identity
from .measurement import measurement_from_record
from .models import TD4183Record
from .sensor_state import MeterRuntime, measurement_native_value


def _history_measurements(records: tuple[TD4183Record, ...]) -> tuple[list[dict], bool]:
    """Return both validated primaries, with no inferred slot chronology."""
    validate_companions(records)
    primaries = []
    for index in range(0, len(records), 2):
        record = records[index]
        if not eligible_primary(record):
            raise BoundedReadError("record", "invalid_primary")
        measurement = measurement_from_record(record)
        value = measurement_native_value(measurement)
        if value is None:
            raise BoundedReadError("record", "invalid_measurement")
        primaries.append((index, measurement.meter_local_time, value))

    ambiguous = len(primaries) == 2 and primaries[0][1] == primaries[1][1]
    # The raw index is a deterministic display tie-break only, never evidence
    # that one equal-minute record preceded the other.
    primaries.sort(key=lambda item: (item[1], -item[0]), reverse=True)
    measurements = [
        {
            "raw_index": index,
            "uric_acid_value_mg_dl": float(value),
            "meter_local_time": meter_time.strftime("%Y-%m-%d %H:%M"),
            "meter_local_timezone_known": False,
        }
        for index, meter_time, value in primaries
    ]
    return measurements, ambiguous


class Fora6HistoryReader:
    """Read one complete bounded snapshot without touching sensor state."""

    def __init__(self, hass: Any, entry: Any, runtime: MeterRuntime) -> None:
        self._hass = hass
        self._entry = entry
        self._runtime = runtime
        self._lock = runtime.gatt_lock

    async def async_read(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "history_read_performed": False,
            "history_read_successful": False,
            "supported_raw_slot_count": False,
            "eligible_measurement_count": 0,
            "measurements": [],
            "chronology_ambiguous": False,
            "error_stage": None,
            "error_code": None,
            "cleanup_errors": [],
        }
        if self._lock.locked():
            result.update(error_stage="history", error_code="already_running")
            return result
        async with self._lock:
            if not is_mac_identity(self._entry.unique_id) or (
                canonical_bluetooth_mac(self._runtime.address) != self._entry.unique_id
            ):
                result.update(error_stage="identity", error_code="identity_mismatch")
                return result
            transport = Fora6BluetoothTransport(
                self._hass, self._runtime.address, response_timeout=RESPONSE_TIMEOUT
            )
            progress = BoundedReadProgress()
            private_measurements: list[dict] | None = None
            ambiguous = False
            try:
                await transport.async_connect()
                await transport.async_subscribe()
                records = await async_read_bounded_records(transport, progress)
                private_measurements, ambiguous = _history_measurements(records)
            except TransportError as failure:
                result.update(error_stage=failure.stage, error_code=failure.code)
            except BoundedReadError as failure:
                result.update(error_stage=failure.stage, error_code=failure.code)
            except Exception:
                result.update(error_stage="history", error_code="unexpected_failure")
            finally:
                result["history_read_performed"] = progress.project_confirmed
                result["supported_raw_slot_count"] = (
                    progress.supported_raw_slot_count
                )
                if progress.raw_slot_count is not None:
                    result["raw_slot_count"] = progress.raw_slot_count
                try:
                    cleanup = await transport.async_close()
                    result["cleanup_errors"] = list(cleanup.errors)
                    if private_measurements is not None and not (
                        cleanup.notification_stopped_cleanly
                        and cleanup.disconnected_cleanly
                    ):
                        result["cleanup_errors"].append("incomplete_cleanup")
                except Exception:
                    result["cleanup_errors"] = ["cleanup_failed"]
            if result["cleanup_errors"] and result["error_code"] is None:
                result.update(error_stage="cleanup", error_code=result["cleanup_errors"][0])
            if private_measurements is None or result["error_code"] is not None:
                return result
            result.update(
                history_read_successful=True,
                eligible_measurement_count=len(private_measurements),
                measurements=private_measurements,
                chronology_ambiguous=ambiguous,
            )
            return result
