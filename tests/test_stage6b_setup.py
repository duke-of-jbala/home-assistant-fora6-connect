"""Stage 6B entry setup/unload never initiates a meter operation."""

import sys
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

from test_gatt_probe import _load_probe, _load_setup


class SetupTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        probe, _, _ = _load_probe()
        self.integration, _, _, _ = _load_setup(probe)
        self.hass = types.SimpleNamespace(config_entries=types.SimpleNamespace(
            async_forward_entry_setups=AsyncMock(),
            async_unload_platforms=AsyncMock(return_value=True),
        ))
        self.entry = types.SimpleNamespace(
            unique_id="SYNTHETIC-SERIAL-A", data={"address": "SYNTHETIC-LOCATOR-A"},
            runtime_data=None,
        )

    async def test_setup_creates_inert_state_and_forwards_only_sensor(self):
        metadata = types.ModuleType(self.integration.__package__ + ".device_metadata")
        metadata.async_reconcile_device_metadata = Mock()
        with patch.dict(sys.modules, {self.integration.__name__: self.integration, metadata.__name__: metadata}):
            self.assertTrue(await self.integration.async_setup_entry(self.hass, self.entry))
        self.assertEqual(self.entry.runtime_data.address, "SYNTHETIC-LOCATOR-A")
        self.assertIsNone(self.entry.runtime_data.measurement_state.native_value)
        self.assertNotIn("SYNTHETIC-LOCATOR-A", repr(self.entry.runtime_data))
        self.hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(self.entry, ["sensor"])
        metadata.async_reconcile_device_metadata.assert_called_once_with(self.hass, self.entry, "SYNTHETIC-LOCATOR-A")

    async def test_missing_identity_or_locator_does_not_setup(self):
        with patch.dict(sys.modules, {self.integration.__name__: self.integration}):
            self.entry.unique_id = None
            self.assertFalse(await self.integration.async_setup_entry(self.hass, self.entry))
            self.entry.unique_id = "SYNTHETIC-SERIAL-A"
            self.entry.data = {}
            self.assertFalse(await self.integration.async_setup_entry(self.hass, self.entry))
        self.hass.config_entries.async_forward_entry_setups.assert_not_awaited()

    async def test_unload_forwards_sensor_only(self):
        self.assertTrue(await self.integration.async_unload_entry(self.hass, self.entry))
        self.hass.config_entries.async_unload_platforms.assert_awaited_once_with(self.entry, ["sensor"])

    async def test_unload_disables_refresh_and_reload_creates_fresh_process_state(self):
        self.entry.unique_id = "aa:bb:cc:dd:ee:01"  # Synthetic fixture only.
        self.entry.data["address"] = "AA:BB:CC:DD:EE:01"
        metadata = types.ModuleType(self.integration.__package__ + ".device_metadata")
        metadata.async_reconcile_device_metadata = Mock()
        with patch.dict(sys.modules, {self.integration.__name__: self.integration, metadata.__name__: metadata}):
            self.assertTrue(await self.integration.async_setup_entry(self.hass, self.entry))
            old_runtime = self.entry.runtime_data
            self.assertIsNotNone(old_runtime.refresh_coordinator)
            self.assertTrue(await self.integration.async_unload_entry(self.hass, self.entry))
            self.assertIsNone(old_runtime.refresh_coordinator)
            self.assertTrue(await self.integration.async_setup_entry(self.hass, self.entry))
        self.assertIsNot(self.entry.runtime_data, old_runtime)
        self.assertIsNotNone(self.entry.runtime_data.refresh_coordinator)
        self.assertIsNone(self.entry.runtime_data.measurement_state.native_value)
        self.assertEqual(self.hass.config_entries.async_forward_entry_setups.await_count, 2)
        self.assertEqual(self.hass.config_entries.async_unload_platforms.await_count, 1)

    async def test_placeholder_migrates_before_sensor_forward(self):
        self.entry.unique_id = "Serial Number"
        self.entry.data["address"] = "AA:BB:CC:DD:EE:01"
        metadata = types.ModuleType(self.integration.__package__ + ".device_metadata")
        metadata.async_reconcile_device_metadata = Mock()
        migration = types.ModuleType(self.integration.__package__ + ".identity_migration")
        migration.IdentityMigrationError = type("IdentityMigrationError", (Exception,), {})

        def migrate(_hass, entry):
            entry.unique_id = "aa:bb:cc:dd:ee:01"
            return True

        migration.migrate_placeholder_identity = Mock(side_effect=migrate)

        async def forwarded(entry, platforms):
            self.assertEqual(entry.unique_id, "aa:bb:cc:dd:ee:01")
            self.assertEqual(platforms, ["sensor"])

        self.hass.config_entries.async_forward_entry_setups.side_effect = forwarded
        with patch.dict(sys.modules, {
            self.integration.__name__: self.integration,
            metadata.__name__: metadata,
            migration.__name__: migration,
        }):
            self.assertTrue(await self.integration.async_setup_entry(self.hass, self.entry))
        migration.migrate_placeholder_identity.assert_called_once_with(self.hass, self.entry)
        self.hass.config_entries.async_forward_entry_setups.assert_awaited_once()

    async def test_unsafe_placeholder_migration_stops_before_forward(self):
        self.entry.unique_id = "Serial Number"
        migration = types.ModuleType(self.integration.__package__ + ".identity_migration")
        migration.IdentityMigrationError = type("IdentityMigrationError", (Exception,), {})
        migration.migrate_placeholder_identity = Mock(side_effect=migration.IdentityMigrationError())
        with patch.dict(sys.modules, {
            self.integration.__name__: self.integration,
            migration.__name__: migration,
        }):
            with self.assertRaisesRegex(RuntimeError, "migration could not be completed safely"):
                await self.integration.async_setup_entry(self.hass, self.entry)
        self.hass.config_entries.async_forward_entry_setups.assert_not_awaited()
