"""One inert uric-acid sensor for a serial-identified FORA meter."""

from __future__ import annotations

from decimal import Decimal

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import NAME, PLACEHOLDER_SERIAL
from .sensor_state import MeasurementState, meter_device_identifier


class Fora6UricAcidSensor(SensorEntity):
    """Expose only validated ordinary uric acid after Stage 7 feeds state."""

    _attr_has_entity_name = True
    _attr_name = "Uric acid"
    _attr_native_unit_of_measurement = "mg/dL"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, state: MeasurementState) -> None:
        self._state = state
        # The confirmed serial identifies the device and is shown in its HA page.
        self._attr_unique_id = f"{entry.entry_id}_uric_acid"
        self._attr_device_info = DeviceInfo(
            identifiers={meter_device_identifier(entry.unique_id)},
            connections={(CONNECTION_BLUETOOTH, entry.runtime_data.address)},
            name=NAME,
            manufacturer="ForaCare",
            model="GD82",
            # An older entry may contain the literal GATT placeholder. Do not
            # present that text as a verified physical serial number.
            serial_number=(
                None if entry.unique_id == PLACEHOLDER_SERIAL else entry.unique_id
            ),
        )

    @property
    def native_value(self) -> Decimal | None:
        return self._state.native_value

    @property
    def available(self) -> bool:
        return self.native_value is not None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Register one unavailable sensor; no BLE I/O or initial read."""
    async_add_entities([Fora6UricAcidSensor(entry, entry.runtime_data.measurement_state)])
