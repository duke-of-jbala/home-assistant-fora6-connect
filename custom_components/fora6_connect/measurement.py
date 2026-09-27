"""Evidence-bounded product measurement model, independent of Home Assistant."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .models import TD4183Record
from .protocol import TD4183Analyte, TD4183RecordCategory


class MeasurementValueStatus(Enum):
    """What the available protocol evidence permits for a record value."""

    URIC_ACID_UNIT_UNRESOLVED = "uric_acid_unit_unresolved"
    INVALID_RAW_VALUE = "invalid_raw_value"
    UNSUPPORTED_ANALYTE_SCALING = "unsupported_analyte_scaling"
    UNKNOWN_ANALYTE = "unknown_analyte"


@dataclass(frozen=True, slots=True, repr=False)
class Fora6Measurement:
    """Product-level interpretation of one parsed TD4183 record.

    ``scaled_number`` is populated only for a valid, positively identified
    uric-acid record. The GD82 display unit is not established in tracked
    evidence, so ``unit`` must remain absent and this number is not publishable
    as a Home Assistant sensor state.
    """

    analyte: TD4183Analyte | None
    scaled_number: Decimal | None = field(repr=False)
    category: TD4183RecordCategory
    transmitted: bool
    meter_local_time: datetime = field(repr=False)
    value_status: MeasurementValueStatus
    unit: None = None

    def __post_init__(self) -> None:
        if self.meter_local_time.tzinfo is not None:
            raise ValueError("Meter-local time must remain timezone-naive.")
        if self.meter_local_time.second or self.meter_local_time.microsecond:
            raise ValueError("TD4183 meter-local time has minute precision.")
        if self.unit is not None:
            raise ValueError("No evidence-backed GD82 measurement unit is known.")
        if self.value_status is MeasurementValueStatus.URIC_ACID_UNIT_UNRESOLVED:
            if self.analyte is not TD4183Analyte.URIC_ACID:
                raise ValueError("Only identified uric acid has supported scaling.")
            if self.scaled_number is None:
                raise ValueError(
                    "A scaled uric-acid number is required for this status."
                )
        elif self.scaled_number is not None:
            raise ValueError("Unsupported or invalid records cannot carry a number.")

    @property
    def is_qc(self) -> bool:
        """Preserve the app-mapped QC category without further interpretation."""
        return self.category is TD4183RecordCategory.QC


def measurement_from_record(record: TD4183Record) -> Fora6Measurement:
    """Map a parsed wire record into the supported product-level fields."""
    if not isinstance(record, TD4183Record):
        raise TypeError("Expected a validated TD4183Record.")

    if not record.is_valid_value:
        scaled_number = None
        value_status = MeasurementValueStatus.INVALID_RAW_VALUE
    elif record.analyte is None:
        scaled_number = None
        value_status = MeasurementValueStatus.UNKNOWN_ANALYTE
    elif record.analyte is TD4183Analyte.URIC_ACID:
        scaled_number = record.uric_acid_scaled_value
        value_status = MeasurementValueStatus.URIC_ACID_UNIT_UNRESOLVED
    else:
        scaled_number = None
        value_status = MeasurementValueStatus.UNSUPPORTED_ANALYTE_SCALING

    return Fora6Measurement(
        analyte=record.analyte,
        scaled_number=scaled_number,
        category=record.category,
        transmitted=record.transmitted,
        meter_local_time=record.meter_local_time.as_naive_datetime(),
        value_status=value_status,
    )
