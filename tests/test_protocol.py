"""Bootstrap guardrails; decoder fixtures and tests begin in Stage 3."""

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "custom_components" / "fora6_connect" / "protocol.py"


class ProtocolBoundaryTests(unittest.TestCase):
    def test_protocol_has_no_home_assistant_or_bluetooth_dependency(self) -> None:
        source = PROTOCOL.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)

        forbidden = ("homeassistant", "bleak", "esphome")
        for name in imported:
            self.assertFalse(name.startswith(forbidden), name)

    def test_no_speculative_decoder_exists(self) -> None:
        tree = ast.parse(PROTOCOL.read_text(encoding="utf-8"))
        executable_definitions = (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.ClassDef,
        )
        self.assertFalse(
            any(isinstance(node, executable_definitions) for node in tree.body)
        )
