"""Synthetic, hardware-free Stage 6B discovery and identity-flow checks."""

import ast
import asyncio
import importlib.util
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
PACKAGE = "_fora6_config_test"


def _load(name, package=PACKAGE):
    spec = importlib.util.spec_from_file_location(f"{package}.{name}", INTEGRATION / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _candidate(**changes):
    values = dict(
        address="AA:BB:CC:DD:EE:01",
        name="FORA 6 CONNECT",
        advertisement=types.SimpleNamespace(local_name="FORA 6 CONNECT\x00\x00\x00\x00\x00"),
        service_uuids=["1808", "0000180a-0000-1000-8000-00805f9b34fb"],
        connectable=True,
        manufacturer_data={},
    )
    values.update(changes)
    return types.SimpleNamespace(**values)


class _FakeFlow:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

    def __init__(self):
        self.context = {}
        self._entries = []
        self.hass = types.SimpleNamespace(config_entries=types.SimpleNamespace(async_update_entry=Mock()))
        self.unique_id = None

    def async_abort(self, reason):
        return {"type": "abort", "reason": reason}

    def async_show_form(self, step_id, data_schema):
        return {"type": "form", "step_id": step_id}

    async def async_set_unique_id(self, unique_id):
        self.unique_id = unique_id

    def _async_current_entries(self):
        return self._entries

    def _abort_if_unique_id_configured(self):
        if any(entry.unique_id == self.unique_id for entry in self._entries):
            raise AssertionError("duplicate unique ID")

    def async_create_entry(self, title, data):
        return {"type": "create_entry", "title": title, "data": data, "unique_id": self.unique_id}


def _load_flow():
    package = types.ModuleType(PACKAGE)
    package.__path__ = [str(INTEGRATION)]
    ha = types.ModuleType("homeassistant")
    entries = types.ModuleType("homeassistant.config_entries")
    entries.ConfigFlow = _FakeFlow
    components = types.ModuleType("homeassistant.components")
    voluptuous = types.ModuleType("voluptuous")
    voluptuous.Schema = lambda value: value
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    bluetooth.async_ble_device_from_address = Mock(return_value=None)
    ha.config_entries = entries
    const = types.ModuleType(f"{PACKAGE}.const")
    exec((INTEGRATION / "const.py").read_text(), const.__dict__)
    identity = types.ModuleType(f"{PACKAGE}.setup_identity")
    identity.SetupIdentityError = type("SetupIdentityError", (Exception,), {"__init__": lambda self, code: (Exception.__init__(self, code), setattr(self, "code", code)) and None})
    identity.async_confirm_meter_identity = AsyncMock(return_value="SYNTHETIC-SERIAL-A")
    metadata = types.ModuleType(f"{PACKAGE}.device_metadata")
    metadata.async_reconcile_device_metadata = Mock(return_value=None)
    metadata.async_restore_device_connections = Mock()
    mac_identity = _load("mac_identity")
    modules = {
        PACKAGE: package, "homeassistant": ha, "homeassistant.config_entries": entries,
        "voluptuous": voluptuous,
        "homeassistant.components": components, "homeassistant.components.bluetooth": bluetooth,
        f"{PACKAGE}.const": const, f"{PACKAGE}.setup_identity": identity,
        f"{PACKAGE}.device_metadata": metadata,
        f"{PACKAGE}.mac_identity": mac_identity,
    }
    with patch.dict(sys.modules, modules):
        discovery = _load("discovery")
        flow = _load("config_flow")
    return discovery, flow, identity, bluetooth, metadata


class DiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.discovery, _, _, _, _ = _load_flow()

    def test_observed_padded_candidate_and_optional_manufacturer_data(self):
        self.assertTrue(self.discovery.is_fora_candidate(_candidate()))
        self.assertTrue(self.discovery.is_fora_candidate(_candidate(manufacturer_data=None)))
        self.assertEqual(self.discovery.normalized_local_name("FORA 6 CONNECT\x00"), "FORA 6 CONNECT")

    def test_wrong_or_partial_name_is_rejected(self):
        for name in ("FORA 6", "FORA 6 CONNECT X", "FORA 6 CONNECT ", "XFORA 6 CONNECT"):
            with self.subTest(name=name):
                self.assertFalse(self.discovery.is_fora_candidate(_candidate(advertisement=types.SimpleNamespace(local_name=name))))

    def test_missing_services_and_nonconnectable_are_rejected(self):
        for services in (["1808"], ["180a"], []):
            self.assertFalse(self.discovery.is_fora_candidate(_candidate(service_uuids=services)))
        self.assertFalse(self.discovery.is_fora_candidate(_candidate(connectable=False)))

    def test_custom_service_not_required_and_no_active_io(self):
        self.assertTrue(self.discovery.is_fora_candidate(_candidate()))
        tree = ast.parse((INTEGRATION / "discovery.py").read_text())
        imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertFalse(any(name.startswith(("homeassistant", "bleak")) for name in imports))


class ConfigFlowTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.discovery, self.module, self.identity, self.bluetooth, self.metadata = _load_flow()
        self.flow = self.module.Fora6ConfigFlow()
        self.address = "AA:BB:CC:DD:EE:01"
        self.serial = "SYNTHETIC-SERIAL-A"

    async def _confirmed(self):
        self.assertEqual((await self.flow.async_step_bluetooth(_candidate()))["step_id"], "confirm")
        return await self.flow.async_step_confirm({})

    async def test_candidate_requires_user_before_active_confirmation(self):
        result = await self.flow.async_step_bluetooth(_candidate())
        self.assertEqual(result, {"type": "form", "step_id": "confirm"})
        self.identity.async_confirm_meter_identity.assert_not_awaited()
        self.assertNotIn(self.address, str(result))

    async def test_invalid_candidate_never_connects(self):
        result = await self.flow.async_step_bluetooth(_candidate(connectable=False))
        self.assertEqual(result["reason"], "not_fora6_connect")
        self.identity.async_confirm_meter_identity.assert_not_awaited()

    async def test_manual_setup_cannot_bypass_candidate(self):
        self.assertEqual((await self.flow.async_step_user())["reason"], "bluetooth_required")
        self.identity.async_confirm_meter_identity.assert_not_awaited()

    async def test_exact_serial_is_unique_id_and_address_only_locator(self):
        self.identity.async_confirm_meter_identity.return_value = "  SYNTHETIC-é-01  "
        result = await self._confirmed()
        self.assertEqual(result["unique_id"], "  SYNTHETIC-é-01  ")
        self.assertEqual(result["title"], "FORA 6 Connect")
        self.assertEqual(result["data"], {"address": self.address})
        self.assertNotIn(self.address, result["unique_id"])
        self.assertNotIn("4183", result["unique_id"])
        self.identity.async_confirm_meter_identity.assert_awaited_once_with(self.flow.hass, self.address)

    async def test_duplicate_same_serial_same_address_aborts(self):
        self.flow._entries = [types.SimpleNamespace(unique_id=self.serial, data={"address": self.address})]
        self.assertEqual((await self.flow.async_step_bluetooth(_candidate()))["reason"], "already_configured")
        self.identity.async_confirm_meter_identity.assert_not_awaited()

    async def test_same_address_different_serial_conflicts(self):
        self.flow._entries = [types.SimpleNamespace(unique_id="SYNTHETIC-SERIAL-B", data={"address": self.address})]
        self.assertEqual((await self.flow.async_step_bluetooth(_candidate()))["reason"], "already_configured")
        self.identity.async_confirm_meter_identity.assert_not_awaited()

    async def test_locator_claimed_after_form_aborts_before_connection(self):
        await self.flow.async_step_bluetooth(_candidate())
        self.flow._entries = [types.SimpleNamespace(unique_id=self.serial, data={"address": self.address})]
        self.assertEqual((await self.flow.async_step_confirm({}))["reason"], "already_configured")
        self.identity.async_confirm_meter_identity.assert_not_awaited()

    async def test_same_serial_new_address_requires_second_review(self):
        existing = types.SimpleNamespace(unique_id=self.serial, data={"address": "AA:BB:CC:DD:EE:02"})
        self.flow._entries = [existing]
        result = await self._confirmed()
        self.assertEqual(result, {"type": "form", "step_id": "update_locator"})
        self.flow.hass.config_entries.async_update_entry.assert_not_called()
        result = await self.flow.async_step_update_locator({})
        self.assertEqual(result["reason"], "locator_updated")
        self.flow.hass.config_entries.async_update_entry.assert_called_once_with(existing, data={"address": self.address})
        self.metadata.async_reconcile_device_metadata.assert_called_once_with(self.flow.hass, existing, self.address)
        self.bluetooth.async_ble_device_from_address.assert_called_once_with(self.flow.hass, "AA:BB:CC:DD:EE:02", connectable=True)

    async def test_simultaneous_old_locator_rejects_update(self):
        self.flow._entries = [types.SimpleNamespace(unique_id=self.serial, data={"address": "AA:BB:CC:DD:EE:02"})]
        await self._confirmed()
        self.bluetooth.async_ble_device_from_address.return_value = object()
        self.assertEqual((await self.flow.async_step_update_locator({}))["reason"], "identity_conflict")
        self.flow.hass.config_entries.async_update_entry.assert_not_called()

    async def test_new_locator_held_by_other_serial_rejects_update(self):
        existing = types.SimpleNamespace(unique_id=self.serial, data={"address": "AA:BB:CC:DD:EE:02"})
        self.flow._entries = [existing]
        await self._confirmed()
        self.flow._entries.append(types.SimpleNamespace(unique_id="SYNTHETIC-SERIAL-B", data={"address": self.address}))
        self.assertEqual((await self.flow.async_step_update_locator({}))["reason"], "identity_conflict")

    async def test_failed_locator_update_rolls_back_registry_connections(self):
        existing = types.SimpleNamespace(unique_id=self.serial, data={"address": "AA:BB:CC:DD:EE:02"})
        self.flow._entries = [existing]
        await self._confirmed()
        previous = {("bluetooth", "AA:BB:CC:DD:EE:02")}
        self.metadata.async_reconcile_device_metadata.return_value = previous
        self.flow.hass.config_entries.async_update_entry.side_effect = RuntimeError("private")
        self.assertEqual((await self.flow.async_step_update_locator({}))["reason"], "identity_conflict")
        self.metadata.async_restore_device_connections.assert_called_once_with(self.flow.hass, existing, previous)
        self.assertEqual(existing.data["address"], "AA:BB:CC:DD:EE:02")

    async def test_serial_and_project_failure_codes_are_private(self):
        for code in ("serial_unavailable", "not_fora6_connect", "cannot_connect", "identity_failed"):
            with self.subTest(code=code):
                self.identity.async_confirm_meter_identity.side_effect = self.identity.SetupIdentityError(code)
                with patch.object(logging.Logger, "_log") as logged:
                    result = await self._confirmed()
                self.assertEqual(result["reason"], code)
                self.assertNotIn(self.address, str(result))
                self.assertNotIn(self.serial, str(result))
                logged.assert_not_called()

    async def test_no_mac_fallback_on_serial_failure(self):
        self.identity.async_confirm_meter_identity.side_effect = self.identity.SetupIdentityError("serial_unavailable")
        result = await self._confirmed()
        self.assertEqual(result["type"], "abort")
        self.assertIsNone(self.flow.unique_id)

    async def test_unusable_serial_from_identity_helper_fails_closed(self):
        for serial in ("", " \x00 ", "SYNTHETIC\x01SERIAL"):
            with self.subTest(serial=serial):
                self.identity.async_confirm_meter_identity.return_value = serial
                result = await self._confirmed()
                self.assertEqual(result["reason"], "serial_unavailable")
                self.assertIsNone(self.flow.unique_id)

    async def test_placeholder_uses_canonical_factory_mac_after_project_confirmation(self):
        self.identity.async_confirm_meter_identity.return_value = "Serial Number"
        result = await self._confirmed()
        self.assertEqual(result["unique_id"], "aa:bb:cc:dd:ee:01")
        self.assertEqual(result["data"], {"address": self.address})
        self.identity.async_confirm_meter_identity.assert_awaited_once()

    async def test_known_mac_case_change_suppresses_without_confirmation(self):
        self.flow._entries = [types.SimpleNamespace(
            unique_id="aa:bb:cc:dd:ee:01", data={"address": "aa:bb:cc:dd:ee:01"}
        )]
        result = await self.flow.async_step_bluetooth(_candidate())
        self.assertEqual(result["reason"], "already_configured")
        self.identity.async_confirm_meter_identity.assert_not_awaited()

    async def test_other_mac_is_new_meter_when_placeholder_is_returned(self):
        self.flow._entries = [types.SimpleNamespace(
            unique_id="aa:bb:cc:dd:ee:02", data={"address": "AA:BB:CC:DD:EE:02"}
        )]
        self.identity.async_confirm_meter_identity.return_value = "Serial Number"
        self.assertEqual((await self._confirmed())["unique_id"], "aa:bb:cc:dd:ee:01")

    async def test_existing_same_mac_with_old_case_cannot_be_duplicated(self):
        self.flow._entries = [types.SimpleNamespace(
            unique_id="AA:BB:CC:DD:EE:01", data={"address": "AA:BB:CC:DD:EE:02"}
        )]
        self.identity.async_confirm_meter_identity.return_value = "Serial Number"
        self.assertEqual((await self._confirmed())["reason"], "identity_conflict")

    async def test_invalid_mac_never_enters_confirmation(self):
        result = await self.flow.async_step_bluetooth(_candidate(address="not-a-mac"))
        self.assertEqual(result["reason"], "identity_failed")
        self.identity.async_confirm_meter_identity.assert_not_awaited()

    async def test_second_in_progress_flow_cannot_create_same_serial(self):
        claimed = set()

        async def claim(flow, serial):
            if serial in claimed:
                raise RuntimeError("already_in_progress")
            claimed.add(serial)
            flow.unique_id = serial

        with patch.object(_FakeFlow, "async_set_unique_id", claim):
            self.assertEqual((await self._confirmed())["type"], "create_entry")
            second = self.module.Fora6ConfigFlow()
            await second.async_step_bluetooth(_candidate(address="AA:BB:CC:DD:EE:03"))
            with self.assertRaisesRegex(RuntimeError, "already_in_progress"):
                await second.async_step_confirm({})
        self.assertEqual(claimed, {self.serial})
