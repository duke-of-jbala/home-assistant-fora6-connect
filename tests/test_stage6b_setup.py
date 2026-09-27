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
