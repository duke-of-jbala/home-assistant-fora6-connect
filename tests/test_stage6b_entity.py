"""Synthetic Stage 6B sensor and device association tests."""

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from test_measurement import fixture_record, measurement, sensor as sensor_state

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
PACKAGE = "fora6_stage5_measurement"


def _load_entity():
    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    sensor_module = types.ModuleType("homeassistant.components.sensor")
    sensor_module.SensorEntity = type("SensorEntity", (), {})
    entries = types.ModuleType("homeassistant.config_entries")
    entries.ConfigEntry = object
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    helpers = types.ModuleType("homeassistant.helpers")
    registry = types.ModuleType("homeassistant.helpers.device_registry")
    registry.DeviceInfo = dict
    platform = types.ModuleType("homeassistant.helpers.entity_platform")
    platform.AddEntitiesCallback = object
    modules = {
        "homeassistant": ha, "homeassistant.components": components,
        "homeassistant.components.sensor": sensor_module,
        "homeassistant.config_entries": entries, "homeassistant.core": core,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.device_registry": registry,
        "homeassistant.helpers.entity_platform": platform,
    }
    spec = importlib.util.spec_from_file_location(f"{PACKAGE}.sensor", INTEGRATION / "sensor.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class EntityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.module = _load_entity()
        self.state = sensor_state.MeasurementState()
        self.entry = types.SimpleNamespace(
            unique_id="SYNTHETIC-SERIAL-A", entry_id="SYNTHETIC-ENTRY-A",
            runtime_data=types.SimpleNamespace(measurement_state=self.state),
        )
        self.entity = self.module.Fora6UricAcidSensor(self.entry, self.state)

    async def test_one_entity_uses_exact_serial_only_for_device_identifier(self):
        add = Mock()
        await self.module.async_setup_entry(object(), self.entry, add)
        add.assert_called_once()
        entities = add.call_args.args[0]
        self.assertEqual(len(entities), 1)
        entity = entities[0]
        self.assertEqual(entity._attr_device_info["identifiers"], {("fora6_connect", self.entry.unique_id)})
        self.assertEqual(entity._attr_unique_id, "SYNTHETIC-ENTRY-A_uric_acid")
        self.assertNotIn(self.entry.unique_id, entity._attr_unique_id)
        self.assertNotIn("serial_number", entity._attr_device_info)
        self.assertEqual(entity._attr_native_unit_of_measurement, "mg/dL")
        self.assertFalse(entity._attr_should_poll)
        self.assertFalse(hasattr(entity, "_attr_device_class"))
        self.assertFalse(hasattr(entity, "_attr_state_class"))

    async def test_initially_unavailable_then_valid_general_uric_acid(self):
        self.assertFalse(self.entity.available)
        self.assertIsNone(self.entity.native_value)
        self.state.replace(measurement.measurement_from_record(fixture_record("uric_general")))
        self.assertTrue(self.entity.available)
        self.assertEqual(str(self.entity.native_value), "123.4")

    async def test_qc_ac_pc_and_invalid_clear_ordinary_state(self):
        self.state.replace(measurement.measurement_from_record(fixture_record("uric_general")))
        for case in ("uric_qc", "ac", "pc", "uric_invalid", "ketone_general", "unknown_type"):
            with self.subTest(case=case):
                self.state.replace(measurement.measurement_from_record(fixture_record(case)))
                self.assertFalse(self.entity.available)
                self.assertIsNone(self.entity.native_value)

    async def test_second_entity_same_meter_shares_device_identifier(self):
        other = self.module.Fora6UricAcidSensor(self.entry, sensor_state.MeasurementState())
        self.assertEqual(other._attr_device_info["identifiers"], self.entity._attr_device_info["identifiers"])

    async def test_entity_has_no_bluetooth_or_auto_update_code(self):
        source = (INTEGRATION / "sensor.py").read_text()
        for forbidden in ("async_ble_device_from_address", "write_gatt_char", "start_notify", "async_update", "asyncio.create_task", "address"):
            self.assertNotIn(forbidden, source)
        tree = ast.parse(source)
        self.assertFalse(any(isinstance(node, ast.FunctionDef) and node.name == "async_update" for node in ast.walk(tree)))
