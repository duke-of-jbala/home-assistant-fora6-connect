"""Guard unvalidated Bluetooth discovery during bootstrap."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "fora6_connect"


class BluetoothBootstrapTests(unittest.TestCase):
    def test_documented_uuids_are_recorded(self) -> None:
        namespace: dict[str, str] = {}
        exec((INTEGRATION / "const.py").read_text(encoding="utf-8"), namespace)
        self.assertEqual(namespace["DOMAIN"], "fora6_connect")
        self.assertEqual(namespace["NAME"], "FORA 6 Connect")
        self.assertEqual(
            namespace["SERVICE_UUID"], "00001523-1212-efde-1523-785feabcd123"
        )
        self.assertEqual(
            namespace["CHARACTERISTIC_UUID"],
            "00001524-1212-efde-1523-785feabcd123",
        )

    def test_discovery_is_not_enabled(self) -> None:
        manifest = json.loads((INTEGRATION / "manifest.json").read_text())
        self.assertEqual(manifest["domain"], "fora6_connect")
        self.assertEqual(manifest["name"], "FORA 6 Connect")
        self.assertNotIn("bluetooth", manifest)
        self.assertNotIn("config_flow", manifest)
