"""Synthetic registry-preserving factory MAC identity migration checks."""

import importlib.util
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
PACKAGE = "_fora6_mac_migration_test"
MAC = "AA:BB:CC:DD:EE:01"  # Synthetic test value, never a physical meter ID.
CANON = MAC.lower()


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{PACKAGE}.{name}", INTEGRATION / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_migration():
    package = types.ModuleType(PACKAGE)
    package.__path__ = [str(INTEGRATION)]
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    helpers = types.ModuleType("homeassistant.helpers")
    dr = types.ModuleType("homeassistant.helpers.device_registry")
    dr.CONNECTION_BLUETOOTH = "bluetooth"
    er = types.ModuleType("homeassistant.helpers.entity_registry")
    modules = {
        PACKAGE: package, "homeassistant": types.ModuleType("homeassistant"),
        "homeassistant.core": core, "homeassistant.helpers": helpers,
        "homeassistant.helpers.device_registry": dr,
        "homeassistant.helpers.entity_registry": er,
    }
    with patch.dict(sys.modules, modules):
        policy = _load("mac_identity")
        migration = _load("identity_migration")
    return policy, migration, dr, er


class _Registry:
    def __init__(self, device):
        self.device = device
        self.devices = {device.id: device}
        self.update_calls = 0

    def async_get_device_by_identifier(self, identifier, entry_id):
        if entry_id != "SYNTHETIC-ENTRY" or identifier not in self.device.identifiers:
            return None
        return self.device

    def async_get_device_by_connection(self, connection, entry_id):
        if entry_id != "SYNTHETIC-ENTRY" or connection not in self.device.connections:
            return None
        return self.device

    def async_update_device(self, device_id, **changes):
        assert device_id == self.device.id
        self.update_calls += 1
        for key, value in changes.items():
            setattr(self.device, key.removeprefix("new_"), value)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.policy, self.migration, self.dr, self.er = _load_migration()
        self.entry = types.SimpleNamespace(
            entry_id="SYNTHETIC-ENTRY", unique_id="Serial Number",
            data={"address": MAC},
        )
        self.device = types.SimpleNamespace(
            id="SYNTHETIC-DEVICE", identifiers={("fora6_connect", "Serial Number")},
            connections={("bluetooth", MAC)}, serial_number=None,
            area_id="SYNTHETIC-AREA", name_by_user="Synthetic user name",
        )
        self.entity = types.SimpleNamespace(
            entity_id="sensor.synthetic_uric_acid", unique_id="SYNTHETIC-ENTRY_uric_acid",
            device_id=self.device.id,
        )
        self.registry = _Registry(self.device)
        self.er.async_get = Mock(return_value=object())
        self.er.async_entries_for_config_entry = Mock(return_value=[self.entity])
        self.dr.async_get = Mock(return_value=self.registry)

        def update_entry(entry, *, unique_id):
            entry.unique_id = unique_id

        self.hass = types.SimpleNamespace(config_entries=types.SimpleNamespace(
            async_entries=Mock(return_value=[self.entry]),
            async_update_entry=Mock(side_effect=update_entry),
        ))

    def test_canonical_format_and_invalid_sources(self):
        self.assertEqual(self.policy.canonical_bluetooth_mac(MAC), CANON)
        self.assertEqual(self.policy.canonical_bluetooth_mac(CANON), CANON)
        self.assertTrue(self.policy.is_mac_identity(CANON))
        for value in ("Serial Number", "FORA 6 CONNECT", "4183", "00:11:22:33:44:GG",
                      "00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff", "", None):
            self.assertIsNone(self.policy.canonical_bluetooth_mac(value))

    def test_same_entry_device_entity_and_connection_are_preserved(self):
        old_device = self.device
        old_entity = self.entity
        with patch.object(logging.Logger, "_log") as logged:
            self.assertTrue(self.migration.migrate_placeholder_identity(self.hass, self.entry))
        logged.assert_not_called()
        self.assertEqual(self.entry.entry_id, "SYNTHETIC-ENTRY")
        self.assertEqual(self.entry.unique_id, CANON)
        self.assertEqual(self.device.identifiers, {("fora6_connect", CANON)})
        self.assertEqual(self.device.connections, {("bluetooth", CANON)})
        self.assertIsNone(self.device.serial_number)
        self.assertIs(self.registry.devices["SYNTHETIC-DEVICE"], old_device)
        self.assertIs(self.entity, old_entity)
        self.assertEqual(self.entity.device_id, self.device.id)
        self.assertEqual(self.entity.entity_id, "sensor.synthetic_uric_acid")
        self.assertEqual(self.device.area_id, "SYNTHETIC-AREA")
        self.assertEqual(self.device.name_by_user, "Synthetic user name")
        self.assertEqual(len(self.registry.devices), 1)
        self.assertEqual(self.registry.update_calls, 1)

    def test_missing_or_mismatched_registry_state_fails_closed(self):
        for mutate in (
            lambda: setattr(self.entry, "data", {"address": "invalid"}),
            lambda: setattr(self.device, "identifiers", set()),
            lambda: setattr(self.device, "connections", {("bluetooth", "AA:BB:CC:DD:EE:02")}),
            lambda: setattr(self.entity, "device_id", "OTHER-DEVICE"),
            lambda: self.er.async_entries_for_config_entry.return_value.clear(),
        ):
            with self.subTest(mutate=mutate):
                self.setUp()
                mutate()
                with self.assertRaises(self.migration.IdentityMigrationError):
                    self.migration.migrate_placeholder_identity(self.hass, self.entry)
                self.assertEqual(self.entry.unique_id, "Serial Number")
                self.assertEqual(self.registry.update_calls, 0)

    def test_other_entry_collision_blocks_migration(self):
        other = types.SimpleNamespace(entry_id="OTHER-ENTRY", unique_id=MAC)
        self.hass.config_entries.async_entries.return_value.append(other)
        with self.assertRaises(self.migration.IdentityMigrationError):
            self.migration.migrate_placeholder_identity(self.hass, self.entry)
        self.assertEqual(self.registry.update_calls, 0)

    def test_entry_update_failure_rolls_back_device(self):
        self.hass.config_entries.async_update_entry.side_effect = RuntimeError(MAC)
        with self.assertRaises(self.migration.IdentityMigrationError) as caught:
            self.migration.migrate_placeholder_identity(self.hass, self.entry)
        self.assertNotIn(MAC, str(caught.exception))
        self.assertEqual(self.entry.unique_id, "Serial Number")
        self.assertEqual(self.device.identifiers, {("fora6_connect", "Serial Number")})
        self.assertEqual(self.device.connections, {("bluetooth", MAC)})
        self.assertEqual(self.registry.update_calls, 2)

    def test_already_migrated_no_change(self):
        self.entry.unique_id = CANON
        self.assertFalse(self.migration.migrate_placeholder_identity(self.hass, self.entry))
        self.assertEqual(self.registry.update_calls, 0)
