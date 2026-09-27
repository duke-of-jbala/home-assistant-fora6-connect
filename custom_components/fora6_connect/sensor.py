"""Inert Home Assistant measurement mapping; no entity or BLE I/O is started.

The tracked evidence establishes uric-acid scaling but not its displayed unit.
Consequently this module currently maps every product measurement to no
numeric sensor state. Stage 6 must supply the stable meter identity and config
entry before an entity can register a device.
"""

from dataclasses import dataclass
from decimal import Decimal

from .const import DOMAIN
from .measurement import Fora6Measurement, MeasurementValueStatus
from .protocol import TD4183RecordCategory


def measurement_native_value(
    measurement: Fora6Measurement | None,
) -> Decimal | None:
    """Return a safe ordinary sensor value only when value, unit and category
    policy are established.

    No measurement currently qualifies: uric-acid unit evidence is missing;
    QC and non-General categories are retained in the product model but not
    mapped to the ordinary measurement sensor.
    """
    if measurement is None:
        return None
    if measurement.unit is None or measurement.scaled_number is None:
        return None
    if measurement.value_status is not MeasurementValueStatus.URIC_ACID_UNIT_UNRESOLVED:
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


def meter_device_identifier(stage6_stable_identifier: str) -> tuple[str, str]:
    """Return the shared HA identifier using an identity supplied by Stage 6.

    This helper never derives identity from a Bluetooth address, local name,
    UUID, or manufacturer data. It is an interface for later entity device
    registration, not a permanent identity policy or an entity registration.
    """
    if (
        not isinstance(stage6_stable_identifier, str)
        or not stage6_stable_identifier.strip()
    ):
        raise ValueError("A Stage 6 stable meter identifier is required.")
    return DOMAIN, stage6_stable_identifier
