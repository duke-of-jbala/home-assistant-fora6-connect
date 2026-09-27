"""Pure measurement-state mapping; no entity or BLE I/O is started.

The app's unconverted uric-acid value uses mg/dL. The HA entity receives a
confirmed meter identity separately and performs no transport work itself.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from .const import DOMAIN
from .measurement import Fora6Measurement, MeasurementValueStatus
from .protocol import TD4183RecordCategory


def measurement_native_value(
    measurement: Fora6Measurement | None,
) -> Decimal | None:
    """Return a safe ordinary sensor value only when value, unit and category
    policy are established.

    Only valid identified uric acid in the General category qualifies.
    QC and non-General categories remain in the product model only.
    """
    if measurement is None:
        return None
    if measurement.unit != "mg/dL" or measurement.scaled_number is None:
        return None
    if measurement.value_status is not MeasurementValueStatus.VALID_URIC_ACID:
        return None
    if measurement.category is not TD4183RecordCategory.GENERAL:
        return None
    return measurement.scaled_number


@dataclass(slots=True)
class MeasurementState:
    """Inert latest-measurement holder for a future entity/coordinator layer.

    Replacement is explicit; an invalid or unsupported new record replaces
    the old record, and the derived sensor value becomes unavailable.
    This class starts no task and performs no Bluetooth or Home Assistant I/O.
    """

    latest: Fora6Measurement | None = None

    def replace(self, measurement: Fora6Measurement | None) -> None:
        if measurement is not None and not isinstance(measurement, Fora6Measurement):
            raise TypeError("Expected a Fora6Measurement or None.")
        self.latest = measurement

    @property
    def native_value(self) -> Decimal | None:
        return measurement_native_value(self.latest)


@dataclass(slots=True, repr=False)
class MeterRuntime:
    """Inert per-entry transport locator and product measurement state."""

    address: str = field(repr=False)
    measurement_state: MeasurementState = field(default_factory=MeasurementState)


def meter_device_identifier(stage6_stable_identifier: str) -> tuple[str, str]:
    """Return the shared HA identifier using an externally confirmed serial.

    This helper never derives identity from a Bluetooth address, local name,
    UUID, or manufacturer data. The caller supplies exact confirmed serial
    text after the guarded setup flow.
    """
    if (
        not isinstance(stage6_stable_identifier, str)
        or not stage6_stable_identifier.strip()
    ):
        raise ValueError("A Stage 6 stable meter identifier is required.")
    return DOMAIN, stage6_stable_identifier
