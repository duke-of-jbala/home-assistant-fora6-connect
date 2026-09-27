"""Hardware-free checks for the read-only Stage 6A1 identity action."""

import asyncio
import importlib.util
import json
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"


def _load_probe():
    package = types.ModuleType("_fora6_serial_test")
    package.__path__ = [str(INTEGRATION)]
    const = types.ModuleType("_fora6_serial_test.const")
    exec((INTEGRATION / "const.py").read_text(encoding="utf-8"), const.__dict__)
    homeassistant = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    connector = types.ModuleType("bleak_retry_connector")
    connector.BleakClientWithServiceCache = type("FakeClient", (), {})
    connector.BleakOutOfConnectionSlotsError = type("NoSlot", (Exception,), {})
    connector.establish_connection = AsyncMock()
    spec = importlib.util.spec_from_file_location(
        "_fora6_serial_test.serial_probe", INTEGRATION / "serial_probe.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        "_fora6_serial_test": package,
        "_fora6_serial_test.const": const,
        "homeassistant": homeassistant,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
        "bleak_retry_connector": connector,
    }):
        spec.loader.exec_module(module)
    return module, bluetooth, connector


def _service(uuid, *chars):
    return types.SimpleNamespace(uuid=uuid, characteristics=list(chars))


class SerialProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.probe, self.bluetooth, self.connector = _load_probe()
        self.address = "synthetic-private-address"
        self.serial = "SYNTHETIC-SERIAL-ONLY"
        self.hass = types.SimpleNamespace(data={}, config_entries=Mock())
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.characteristic = types.SimpleNamespace(
            uuid=self.probe.SERIAL_NUMBER_UUID, properties=["read"]
        )
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[_service(self.probe.DEVICE_INFORMATION_UUID, self.characteristic)],
            read_gatt_char=AsyncMock(return_value=self.serial.encode()),
            disconnect=AsyncMock(),
            write_gatt_char=AsyncMock(),
            start_notify=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client

    async def run_probe(self):
        return await self.probe.async_probe_serial_identity(self.hass, self.address)

    def assert_read_only(self):
        self.client.write_gatt_char.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        self.hass.config_entries.assert_not_called()
        self.assertEqual(self.hass.data, {})

    def assert_private(self, result):
        rendered = json.dumps(result)
        self.assertNotIn(self.serial, rendered)
        self.assertNotIn(self.address, rendered)
        self.assertNotIn("token", rendered)

    async def test_success_reads_only_serial_once(self):
        with patch.object(logging.Logger, "_log") as logged:
            result = await self.run_probe()
        logged.assert_not_called()
        self.assertTrue(result["connection_successful"])
        self.assertTrue(result["device_information_service_found"])
        self.assertTrue(result["serial_characteristic_found"])
        self.assertTrue(result["serial_readable"])
        self.assertTrue(result["serial_read_successful"])
        self.assertTrue(result["serial_value_present"])
        self.assertTrue(result["serial_value_nonempty"])
        self.assertTrue(result["serial_value_utf8_valid"])
        self.assertTrue(result["serial_value_usable"])
        self.assertTrue(result["disconnected_cleanly"])
        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, self.address, connectable=True
        )
        self.client.read_gatt_char.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()
        self.assertEqual(self.connector.establish_connection.call_args.kwargs["pair"], False)
        self.assertEqual(self.connector.establish_connection.call_args.kwargs["max_attempts"], 2)
        self.assert_read_only()
        self.assert_private(result)

    async def test_no_connectable_device(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "no_connectable_device")
        self.connector.establish_connection.assert_not_awaited()
        self.assert_private(result)

    async def test_resolution_error_is_sanitized(self):
        self.bluetooth.async_ble_device_from_address.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "resolution_failed")
        self.assert_private(result)

    async def test_connection_errors_are_sanitized(self):
        for error, code in (
            (RuntimeError(self.address), "connection_failed"),
            (self.connector.BleakOutOfConnectionSlotsError(self.address), "no_connection_slot"),
        ):
            with self.subTest(code=code):
                self.connector.establish_connection.side_effect = error
                result = await self.run_probe()
                self.assertEqual(result["error_code"], code)
                self.assert_private(result)

    async def test_peer_disconnected(self):
        self.client.is_connected = False
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "peer_disconnected")
        self.client.disconnect.assert_awaited_once()

    async def test_missing_service(self):
        self.client.services = []
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "device_information_missing")
        self.client.read_gatt_char.assert_not_awaited()
        self.client.disconnect.assert_awaited_once()

    async def test_missing_characteristic(self):
        self.client.services = [_service(self.probe.DEVICE_INFORMATION_UUID)]
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "serial_characteristic_missing")
        self.client.read_gatt_char.assert_not_awaited()

    async def test_not_readable(self):
        self.characteristic.properties = ["notify"]
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "serial_not_readable")
        self.client.read_gatt_char.assert_not_awaited()
        self.assert_read_only()

    async def test_empty_and_whitespace_values(self):
        for raw in (b"", b"\x00\x00", b" \t\r\n"):
            with self.subTest(raw=raw):
                self.client.read_gatt_char.return_value = raw
                result = await self.run_probe()
                self.assertTrue(result["serial_read_successful"])
                self.assertFalse(result["serial_value_nonempty"])
                self.assertFalse(result["serial_value_usable"])
                self.assert_private(result)

    async def test_invalid_utf8_and_binary_looking_values(self):
        for raw, utf8 in ((b"\xff", False), (b"A\x01B", True)):
            with self.subTest(raw=raw):
                self.client.read_gatt_char.return_value = raw
                result = await self.run_probe()
                self.assertTrue(result["serial_value_present"])
                self.assertEqual(result["serial_value_utf8_valid"], utf8)
                self.assertFalse(result["serial_value_usable"])

    async def test_read_failure_and_timeout_sanitized(self):
        for error in (RuntimeError(self.serial + self.address), TimeoutError()):
            with self.subTest(error=type(error).__name__):
                self.client.read_gatt_char.side_effect = error
                result = await self.run_probe()
                self.assertEqual(result["error_code"], "serial_read_failed")
                self.assertTrue(result["disconnected_cleanly"])
                self.assert_private(result)

    async def test_disconnect_failure_sanitized(self):
        self.client.disconnect.side_effect = RuntimeError(self.address + self.serial)
        result = await self.run_probe()
        self.assertEqual(result["cleanup_errors"], ["disconnect_failed"])
        self.assertEqual(result["error_code"], "disconnect_failed")
        self.assert_private(result)

    async def test_cancellation_during_read_disconnects(self):
        started = asyncio.Event()
        async def pending_read(_characteristic):
            started.set()
            await asyncio.Future()
        self.client.read_gatt_char.side_effect = pending_read
        task = asyncio.create_task(self.run_probe())
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.disconnect.assert_awaited_once()
        self.assert_read_only()

    async def test_cancellation_during_connect_reaps_returned_client(self):
        started = asyncio.Event()
        async def reluctant_connector(*_args, **_kwargs):
            started.set()
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                return self.client
        self.connector.establish_connection.side_effect = reluctant_connector
        task = asyncio.create_task(self.run_probe())
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.disconnect.assert_awaited_once()
        self.client.read_gatt_char.assert_not_awaited()
        self.assert_read_only()

    async def test_connection_timeout_reaps_late_client(self):
        self.probe.CONNECT_TOTAL_TIMEOUT = 0.01
        async def reluctant_connector(*_args, **_kwargs):
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                return self.client
        self.connector.establish_connection.side_effect = reluctant_connector
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "connection_failed")
        self.client.disconnect.assert_awaited_once()
        self.assert_private(result)

    async def test_service_registration_has_no_persistence(self):
        from test_gatt_probe import _load_probe, _load_setup, _registered_action
        integration, _, _, exceptions = _load_setup(_load_probe()[0])
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services, data={}, config_entries=Mock())
        self.assertTrue(await integration.async_setup(hass, {}))
        action = _registered_action(services, "probe_serial_identity")
        self.assertEqual(action.kwargs["supports_response"], "response_only")
        result = await action.args[2](types.SimpleNamespace(data={"address": self.address}))
        self.assertEqual(result, {"serial_read_successful": True})
        integration._test_serial.async_probe_serial_identity.assert_awaited_once_with(hass, self.address)
        hass.config_entries.assert_not_called()
        self.assertEqual(hass.data, {})
        integration._test_serial.async_probe_serial_identity.side_effect = RuntimeError(self.address)
        with self.assertRaises(exceptions.ServiceValidationError) as caught:
            await action.args[2](types.SimpleNamespace(data={"address": self.address}))
        self.assertNotIn(self.address, str(caught.exception))
