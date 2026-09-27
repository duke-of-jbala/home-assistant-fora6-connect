"""Guard against publishing unverified health entities in Stage 0."""

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "fora6_connect"


class SensorBootstrapTests(unittest.TestCase):
    def test_no_sensor_platform_or_ha_entity_is_registered(self) -> None:
        init_source = (INTEGRATION / "__init__.py").read_text(encoding="utf-8")
        sensor_tree = ast.parse((INTEGRATION / "sensor.py").read_text())
        self.assertNotIn("async_forward_entry_setups", init_source)
        self.assertFalse(
            any(isinstance(node, ast.AsyncFunctionDef) for node in sensor_tree.body)
        )
        self.assertFalse(
            any(
                isinstance(node, ast.ImportFrom)
                and (node.module or "").startswith(("homeassistant", "bleak"))
                for node in ast.walk(sensor_tree)
            )
        )
        imports = [
            node.module or ""
            for node in ast.walk(sensor_tree)
            if isinstance(node, ast.ImportFrom)
        ]
        self.assertFalse(
            any(module.startswith("homeassistant.components") for module in imports)
        )
