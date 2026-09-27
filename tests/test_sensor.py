"""Guard the bounded Stage 6B entity and no-sync boundary."""

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "fora6_connect"


class SensorBootstrapTests(unittest.TestCase):
    def test_only_inert_sensor_platform_is_registered(self) -> None:
        init_source = (INTEGRATION / "__init__.py").read_text(encoding="utf-8")
        sensor_tree = ast.parse((INTEGRATION / "sensor.py").read_text())
        self.assertIn('async_forward_entry_setups(entry, ["sensor"])', init_source)
        self.assertTrue(any(isinstance(node, ast.ClassDef) and node.name == "Fora6UricAcidSensor" for node in sensor_tree.body))
        source = (INTEGRATION / "sensor.py").read_text()
        self.assertIn('_attr_should_poll = False', source)
        for forbidden in ("async_update", "write_gatt_char", "async_ble_device_from_address", "start_notify"):
            self.assertNotIn(forbidden, source)
