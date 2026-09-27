"""Synthetic, hardware-free checks for one private System ID read."""

import asyncio
import importlib.util
import json
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from test_serial_probe import _load_probe, _service

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
PACKAGE = "_fora6_system_test"
SYSTEM_VALUE = bytes((1, 2, 3, 4, 5, 6, 7, 8))


def _load_system_probe():
    serial, bluetooth, connector = _load_probe()
    package = types.ModuleType(PACKAGE)
    package.__path__ = [str(INTEGRATION)]
    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    components.bluetooth = bluetooth
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE}.system_id_probe", INTEGRATION / "system_id_probe.py"
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        PACKAGE: package, "homeassistant": ha,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
        f"{PACKAGE}.serial_probe": serial,
    }):
        spec.loader.exec_module(module)
    return module, bluetooth, connector


class SystemIdProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.probe, self.bluetooth, self.connector = _load_system_probe()
        self.hass = types.SimpleNamespace(data={}, config_entries=Mock())
        self.address = "SYNTHETIC-LOCATOR"
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.characteristic = types.SimpleNamespace(
            uuid=self.probe.SYSTEM_ID_UUID, properties=["read"]
        )
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[_service(self.probe.DEVICE_INFORMATION_UUID, self.characteristic)],
            read_gatt_char=AsyncMock(return_value=SYSTEM_VALUE),
            disconnect=AsyncMock(), write_gatt_char=AsyncMock(),
            start_notify=AsyncMock(), pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client

    async def run_probe(self):
        return await self.probe.async_probe_system_id(self.hass, self.address)

    def assert_private(self, result):
        rendered = json.dumps(result)
        self.assertNotIn(self.address, rendered)
        self.assertNotIn(SYSTEM_VALUE.hex(), rendered)
        for key in result:
            self.assertFalse(any(word in key for word in ("hash", "digest", "length", "prefix", "suffix")))

    def assert_read_only(self):
        self.client.write_gatt_char.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        self.hass.config_entries.assert_not_called()
        self.assertEqual(self.hass.data, {})
        self.assertEqual(self.connector.establish_connection.call_args.kwargs["pair"], False)
        self.assertEqual(self.connector.establish_connection.call_args.kwargs["max_attempts"], 2)

    async def test_one_read_success_and_cleanup(self):
        with patch.object(logging.Logger, "_log") as logged:
            result = await self.run_probe()
        logged.assert_not_called()
        for key in (
            "device_found", "connectable_device_resolved", "connection_successful",
            "device_information_service_found", "system_id_characteristic_found",
            "system_id_readable", "system_id_read_successful", "system_id_value_present",
            "system_id_format_plausible", "system_id_value_usable", "disconnected_cleanly",
        ):
            self.assertTrue(result[key], key)
        self.client.read_gatt_char.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()
        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, self.address, connectable=True
        )
        self.assert_read_only()
        self.assert_private(result)

    async def test_no_connectable_device_and_resolution_error(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "no_connectable_device")
        self.connector.establish_connection.assert_not_awaited()
        self.bluetooth.async_ble_device_from_address.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "resolution_failed")
        self.assert_private(result)

    async def test_connection_failure_and_disconnected_client(self):
        self.connector.establish_connection.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "connection_failed")
        self.connector.establish_connection.side_effect = None
        self.client.is_connected = False
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "peer_disconnected")
        self.client.read_gatt_char.assert_not_awaited()

    async def test_missing_service_characteristic_and_read_property(self):
        self.client.services = []
        self.assertEqual((await self.run_probe())["error_code"], "device_information_missing")
        self.client.services = [_service(self.probe.DEVICE_INFORMATION_UUID)]
        self.assertEqual((await self.run_probe())["error_code"], "system_id_characteristic_missing")
        self.client.services = [_service(self.probe.DEVICE_INFORMATION_UUID, self.characteristic)]
        self.characteristic.properties = ["notify"]
        self.assertEqual((await self.run_probe())["error_code"], "system_id_not_readable")
        self.client.read_gatt_char.assert_not_awaited()

    async def test_empty_and_short_and_long_values(self):
        for raw, present in ((b"", False), (b"a" * 7, True), (b"a" * 9, True)):
            with self.subTest(raw=raw):
                self.client.read_gatt_char.return_value = raw
                result = await self.run_probe()
                self.assertTrue(result["system_id_read_successful"])
                self.assertEqual(result["system_id_value_present"], present)
                self.assertFalse(result["system_id_format_plausible"])
                self.assertFalse(result["system_id_value_usable"])
                self.assert_private(result)

    async def test_constant_filled_values_are_plausible_but_unusable(self):
        for raw in (bytes(8), b"\xff" * 8):
            with self.subTest(raw=raw):
                self.client.read_gatt_char.return_value = raw
                result = await self.run_probe()
                self.assertTrue(result["system_id_format_plausible"])
                self.assertFalse(result["system_id_value_usable"])

    async def test_read_failure_and_disconnect_failure_sanitized(self):
        self.client.read_gatt_char.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "system_id_read_failed")
        self.assert_private(result)
        self.client.read_gatt_char.side_effect = None
        self.client.disconnect.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "disconnect_failed")
        self.assertEqual(result["cleanup_errors"], ["disconnect_failed"])
        self.assert_private(result)

    async def test_cancellation_disconnects(self):
        started = asyncio.Event()
        async def pending(_characteristic):
            started.set()
            await asyncio.Future()
        self.client.read_gatt_char.side_effect = pending
        task = asyncio.create_task(self.run_probe())
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.disconnect.assert_awaited_once()

    async def test_no_fora_command_constructor_or_identity_mutation(self):
        source = (INTEGRATION / "system_id_probe.py").read_text()
        for forbidden in ("write_gatt_char", "start_notify", "build_wake", "build_project", "async_update_entry", "DeviceInfo", "0x2f", "0x33", "0x50"):
            self.assertNotIn(forbidden, source)
        await self.run_probe()
        self.assert_read_only()

    async def test_action_registration_and_private_error(self):
        from test_gatt_probe import _load_probe as _load_gatt_probe, _load_setup
        integration, _, _, exceptions = _load_setup(_load_gatt_probe()[0])
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services, data={}, config_entries=Mock())
        self.assertTrue(await integration.async_setup(hass, {}))
        action = next(call for call in services.async_register.call_args_list
                      if call.args[1] == "probe_system_id")
        self.assertEqual(action.kwargs["supports_response"], "response_only")
        self.assertEqual(await action.args[2](types.SimpleNamespace(data={"address": self.address})),
                         {"system_id_read_successful": True})
        integration._test_system_id.async_probe_system_id.assert_awaited_once_with(hass, self.address)
        integration._test_system_id.async_probe_system_id.side_effect = RuntimeError(self.address)
        with self.assertRaises(exceptions.ServiceValidationError) as caught:
            await action.args[2](types.SimpleNamespace(data={"address": self.address}))
        self.assertNotIn(self.address, str(caught.exception))
