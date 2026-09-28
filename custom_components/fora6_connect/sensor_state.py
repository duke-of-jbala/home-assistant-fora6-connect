"""Pure measurement-state mapping; no entity or BLE I/O is started.

The app's unconverted uric-acid value uses mg/dL. The HA entity receives a
confirmed meter identity separately and performs no transport work itself.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable

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
    """Latest valid measurement and synchronous entity change listeners.

    Replacement is explicit. The Stage 7H coordinator only calls it after a
    complete successful refresh, so failures retain the previous valid value.
    This class starts no task and performs no Bluetooth I/O.
    """

    latest: Fora6Measurement | None = None
    _listeners: list[Callable[[], None]] = field(default_factory=list, repr=False)

    def replace(self, measurement: Fora6Measurement | None) -> None:
        if measurement is not None and not isinstance(measurement, Fora6Measurement):
            raise TypeError("Expected a Fora6Measurement or None.")
        self.latest = measurement
        for listener in tuple(self._listeners):
            listener()

    def subscribe(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Notify the loaded entity after an explicit successful replacement."""
        self._listeners.append(listener)

        def unsubscribe() -> None:
            self._listeners.remove(listener)

        return unsubscribe

    @property
    def native_value(self) -> Decimal | None:
        return measurement_native_value(self.latest)


@dataclass(slots=True, repr=False)
class MeterRuntime:
    """Inert per-entry transport locator and product measurement state."""

    address: str = field(repr=False)
    measurement_state: MeasurementState = field(default_factory=MeasurementState)
    refresh_coordinator: Any = field(default=None, repr=False)
    history_reader: Any = field(default=None, repr=False)
    synchronized_at: datetime | None = field(default=None, repr=False)
    advertisement_observation_stop: asyncio.Event | None = field(default=None, repr=False)
    gatt_lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)
    readiness_probe_task: asyncio.Task | None = field(default=None, repr=False)
    history_read_task: asyncio.Task | None = field(default=None, repr=False)


def meter_device_identifier(stage6_stable_identifier: str) -> tuple[str, str]:
    """Return the shared HA identifier from the guarded ConfigEntry identity.

    This helper does not derive identity. Stage 6B3 can supply a validated
    factory Bluetooth MAC when standard DIS identity is a placeholder.
    """
    if (
        not isinstance(stage6_stable_identifier, str)
        or not stage6_stable_identifier.strip()
    ):
        raise ValueError("A Stage 6 stable meter identifier is required.")
    return DOMAIN, stage6_stable_identifier
