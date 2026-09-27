"""Synthetic Stage 6B1 device-registry reconciliation checks."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
PACKAGE = "_fora6_metadata_test"


def _load_metadata():
    package = types.ModuleType(PACKAGE)
    package.__path__ = [str(INTEGRATION)]
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    helpers = types.ModuleType("homeassistant.helpers")
    registry_module = types.ModuleType("homeassistant.helpers.device_registry")
    registry_module.CONNECTION_BLUETOOTH = "bluetooth"
    registry = types.SimpleNamespace(
        async_get_device_by_identifier=Mock(), async_update_device=Mock()
    )
    registry_module.async_get = Mock(return_value=registry)
    helpers.device_registry = registry_module
    const = types.ModuleType(f"{PACKAGE}.const")
    exec((INTEGRATION / "const.py").read_text(), const.__dict__)
    modules = {
        PACKAGE: package, "homeassistant": types.ModuleType("homeassistant"),
        "homeassistant.core": core, "homeassistant.helpers": helpers,
        "homeassistant.helpers.device_registry": registry_module,
        f"{PACKAGE}.const": const,
    }
    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE}.device_metadata", INTEGRATION / "device_metadata.py"
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, registry


class DeviceMetadataTests(unittest.TestCase):
    def setUp(self):
        self.module, self.registry = _load_metadata()
        self.hass = object()
        self.entry = types.SimpleNamespace(
            unique_id="SYNTHETIC-SERIAL-A", entry_id="SYNTHETIC-ENTRY-A"
        )
        self.device = types.SimpleNamespace(
            id="SYNTHETIC-DEVICE-A", serial_number="Serial Number",
            connections={("bluetooth", "SYNTHETIC-OLD-LOCATOR"), ("other", "SYNTHETIC-OTHER")},
        )
        self.registry.async_get_device_by_identifier.return_value = self.device

    def test_existing_device_refreshes_literal_label_and_replaces_only_ble_locator(self):
        old = self.module.async_reconcile_device_metadata(
            self.hass, self.entry, "SYNTHETIC-NEW-LOCATOR"
        )
        self.assertEqual(old, self.device.connections)
        self.registry.async_get_device_by_identifier.assert_called_once_with(
            ("fora6_connect", "SYNTHETIC-SERIAL-A"), "SYNTHETIC-ENTRY-A"
        )
        self.registry.async_update_device.assert_called_once_with(
            self.device.id,
            serial_number="SYNTHETIC-SERIAL-A",
            new_connections={("bluetooth", "SYNTHETIC-NEW-LOCATOR"), ("other", "SYNTHETIC-OTHER")},
        )
        self.assertEqual(self.entry.unique_id, "SYNTHETIC-SERIAL-A")

    def test_correct_device_metadata_is_not_rewritten(self):
        self.device.serial_number = self.entry.unique_id
        self.device.connections = {("bluetooth", "SYNTHETIC-NEW-LOCATOR")}
        self.module.async_reconcile_device_metadata(self.hass, self.entry, "SYNTHETIC-NEW-LOCATOR")
        self.registry.async_update_device.assert_not_called()

    def test_legacy_placeholder_is_removed_from_display_without_changing_identity(self):
        self.entry.unique_id = "Serial Number"
        self.module.async_reconcile_device_metadata(
            self.hass, self.entry, "SYNTHETIC-OLD-LOCATOR"
        )
        self.registry.async_update_device.assert_called_once_with(
            self.device.id,
            serial_number=None,
            new_connections={("bluetooth", "SYNTHETIC-OLD-LOCATOR"), ("other", "SYNTHETIC-OTHER")},
        )

    def test_missing_device_causes_no_creation(self):
        self.registry.async_get_device_by_identifier.return_value = None
        self.assertIsNone(self.module.async_reconcile_device_metadata(self.hass, self.entry, "SYNTHETIC-NEW-LOCATOR"))
        self.registry.async_update_device.assert_not_called()

    def test_restore_connections_after_failed_entry_update(self):
        old = set(self.device.connections)
        self.device.connections = {("bluetooth", "SYNTHETIC-NEW-LOCATOR")}
        self.module.async_restore_device_connections(self.hass, self.entry, old)
        self.registry.async_update_device.assert_called_once_with(
            self.device.id, new_connections=old
        )

    def test_registry_code_has_no_ble_or_persistence_io(self):
        source = (INTEGRATION / "device_metadata.py").read_text()
        for forbidden in ("write_gatt_char", "start_notify", "read_gatt_char", "async_ble_device_from_address", "async_create_entry"):
            self.assertNotIn(forbidden, source)
