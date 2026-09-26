"""Guard against publishing unverified health entities in Stage 0."""

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "fora6"


class SensorBootstrapTests(unittest.TestCase):
    def test_no_sensor_platform_is_registered(self) -> None:
        init_source = (INTEGRATION / "__init__.py").read_text(encoding="utf-8")
        sensor_tree = ast.parse((INTEGRATION / "sensor.py").read_text())
        self.assertNotIn("async_forward_entry_setups", init_source)
        self.assertFalse(
            any(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                for node in sensor_tree.body
            )
        )
