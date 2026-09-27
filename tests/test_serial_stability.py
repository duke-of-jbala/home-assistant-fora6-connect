"""Synthetic, hardware-free tests of private serial equality."""

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


def _load_stability():
    serial, bluetooth, connector = _load_probe()
    package = types.ModuleType("_fora6_stability_test")
    package.__path__ = [str(INTEGRATION)]
    const = types.ModuleType("_fora6_stability_test.const")
    exec((INTEGRATION / "const.py").read_text(encoding="utf-8"), const.__dict__)
    homeassistant = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    spec = importlib.util.spec_from_file_location(
        "_fora6_stability_test.serial_stability", INTEGRATION / "serial_stability.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        "_fora6_stability_test": package,
        "_fora6_stability_test.const": const,
        "_fora6_stability_test.serial_probe": serial,
        "homeassistant": homeassistant,
        "homeassistant.core": core,
    }):
        spec.loader.exec_module(module)
    return module, serial, bluetooth, connector


class SerialStabilityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.stability, self.serial_probe, self.bluetooth, self.connector = _load_stability()
        self.hass = types.SimpleNamespace(data={}, config_entries=Mock())
        self.address = "synthetic-runtime-address"
        self.serial = b"SYNTHETIC-DEVICE-A"
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.characteristic = types.SimpleNamespace(
            uuid=self.serial_probe.SERIAL_NUMBER_UUID, properties=["read"]
        )
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[_service(self.serial_probe.DEVICE_INFORMATION_UUID, self.characteristic)],
            read_gatt_char=AsyncMock(return_value=self.serial),
            disconnect=AsyncMock(),
            write_gatt_char=AsyncMock(),
            start_notify=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client

    async def run_action(self, operation):
        return await self.stability.async_probe_serial_stability(
            self.hass, self.address, operation
        )

    def assert_private(self, result):
        rendered = json.dumps(result)
        self.assertNotIn(self.serial.decode(), rendered)
        self.assertNotIn(self.address, rendered)
        for name in result:
            self.assertNotIn("digest", name)
            self.assertNotIn("hash", name)
            self.assertNotIn("length", name)
            self.assertNotIn("prefix", name)
            self.assertNotIn("suffix", name)
        self.assertNotIn(self.serial.decode(), repr(self.hass.data))

    def assert_read_only(self):
        self.client.write_gatt_char.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        self.hass.config_entries.assert_not_called()
        self.assertEqual(self.connector.establish_connection.call_args.kwargs["pair"], False)

    async def test_set_reference_reads_once_and_is_private(self):
        with patch.object(logging.Logger, "_log") as logged:
            result = await self.run_action("set_reference")
        logged.assert_not_called()
        self.assertTrue(result["reference_set"])
        self.assertTrue(result["reference_available"])
        self.assertIsNone(result["serial_matches_reference"])
        self.assertTrue(result["disconnected_cleanly"])
        self.client.read_gatt_char.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()
        self.assert_read_only()
        self.assert_private(result)
        self.assertEqual(set(self.hass.data), {"fora6_connect"})
        self.assertEqual(set(self.hass.data["fora6_connect"]), {"serial_stability"})

    async def test_compare_same_and_different_serial(self):
        await self.run_action("set_reference")
        self.client.read_gatt_char.return_value = self.serial
        same = await self.run_action("compare")
        self.assertTrue(same["serial_matches_reference"])
        self.client.read_gatt_char.return_value = b"SYNTHETIC-DEVICE-B"
        different = await self.run_action("compare")
        self.assertFalse(different["serial_matches_reference"])
        self.assertTrue(different["reference_available"])
        self.assertEqual(self.client.read_gatt_char.await_count, 3)
        self.assertEqual(self.client.disconnect.await_count, 3)
        self.assert_private(same)
        self.assert_private(different)

    async def test_compare_without_reference_does_not_read_or_set(self):
        result = await self.run_action("compare")
        self.assertEqual(result["error_stage"], "comparison")
        self.assertEqual(result["error_code"], "no_reference")
        self.assertFalse(result["reference_available"])
        self.assertFalse(result["reference_set"])
        self.assertIsNone(result["serial_matches_reference"])
        self.connector.establish_connection.assert_not_awaited()
        self.client.read_gatt_char.assert_not_awaited()
        self.assert_private(result)

    async def test_set_replaces_reference_only_after_success(self):
        await self.run_action("set_reference")
        self.client.read_gatt_char.return_value = b"SYNTHETIC-DEVICE-B"
        result = await self.run_action("set_reference")
        self.assertTrue(result["reference_set"])
        self.client.read_gatt_char.return_value = self.serial
        self.assertFalse((await self.run_action("compare"))["serial_matches_reference"])
        self.client.read_gatt_char.return_value = b"SYNTHETIC-DEVICE-B"
        self.assertTrue((await self.run_action("compare"))["serial_matches_reference"])

    async def test_failed_read_does_not_replace_reference(self):
        await self.run_action("set_reference")
        self.client.read_gatt_char.side_effect = RuntimeError(self.serial.decode())
        failure = await self.run_action("set_reference")
        self.assertEqual(failure["error_code"], "serial_read_failed")
        self.assertFalse(failure["reference_set"])
        self.assertTrue(failure["reference_available"])
        self.assert_private(failure)
        self.client.read_gatt_char.side_effect = None
        self.client.read_gatt_char.return_value = self.serial
        self.assertTrue((await self.run_action("compare"))["serial_matches_reference"])

    async def test_invalid_empty_or_unusable_serial_preserves_reference(self):
        await self.run_action("set_reference")
        for raw in (b"", b"\xff", b"X\x01Y", b" \x00 "):
            with self.subTest(raw=raw):
                self.client.read_gatt_char.return_value = raw
                failure = await self.run_action("set_reference")
                self.assertEqual(failure["error_code"], "unusable_serial")
                self.assertFalse(failure["reference_set"])
                self.assertTrue(failure["reference_available"])
        self.client.read_gatt_char.return_value = self.serial
        self.assertTrue((await self.run_action("compare"))["serial_matches_reference"])

    async def test_disconnect_failure_preserves_reference(self):
        await self.run_action("set_reference")
        self.client.read_gatt_char.return_value = b"SYNTHETIC-DEVICE-B"
        self.client.disconnect.side_effect = RuntimeError(self.address)
        failure = await self.run_action("set_reference")
        self.assertEqual(failure["error_code"], "disconnect_failed")
        self.assertTrue(failure["reference_available"])
        self.client.disconnect.side_effect = None
        self.client.read_gatt_char.return_value = self.serial
        self.assertTrue((await self.run_action("compare"))["serial_matches_reference"])

    async def test_cancellation_does_not_erase_reference(self):
        await self.run_action("set_reference")
        started = asyncio.Event()
        async def pending_read(_characteristic):
            started.set()
            await asyncio.Future()
        self.client.read_gatt_char.side_effect = pending_read
        task = asyncio.create_task(self.run_action("set_reference"))
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.read_gatt_char.side_effect = None
        self.client.read_gatt_char.return_value = self.serial
        self.assertTrue((await self.run_action("compare"))["serial_matches_reference"])

    async def test_exact_raw_bytes_not_normalized(self):
        self.client.read_gatt_char.return_value = b" SYNTHETIC-DEVICE-A "
        await self.run_action("set_reference")
        self.client.read_gatt_char.return_value = b"SYNTHETIC-DEVICE-A"
        self.assertFalse((await self.run_action("compare"))["serial_matches_reference"])
        self.client.read_gatt_char.return_value = b" synthetic-device-a "
        self.assertFalse((await self.run_action("compare"))["serial_matches_reference"])

    async def test_lock_serializes_set_and_compare(self):
        started = asyncio.Event()
        release = asyncio.Event()
        async def delayed_read(_characteristic):
            started.set()
            await release.wait()
            return self.serial
        self.client.read_gatt_char.side_effect = delayed_read
        setter = asyncio.create_task(self.run_action("set_reference"))
        await started.wait()
        comparer = asyncio.create_task(self.run_action("compare"))
        await asyncio.sleep(0)
        self.assertFalse(comparer.done())
        release.set()
        self.assertTrue((await setter)["reference_set"])
        self.assertTrue((await comparer)["serial_matches_reference"])

    async def test_process_local_state_is_not_shared_with_new_hass(self):
        await self.run_action("set_reference")
        restarted_hass = types.SimpleNamespace(data={}, config_entries=Mock())
        result = await self.stability.async_probe_serial_stability(
            restarted_hass, self.address, "compare"
        )
        self.assertEqual(result["error_code"], "no_reference")
        self.assertFalse(result["reference_available"])
        self.assertTrue(self.hass.data["fora6_connect"]["serial_stability"]._value)

    async def test_original_identity_probe_schema_unchanged(self):
        result = await self.serial_probe.async_probe_serial_identity(self.hass, self.address)
        self.assertNotIn("reference_set", result)
        self.assertNotIn("reference_available", result)
        self.assertNotIn("serial_matches_reference", result)
        self.assertTrue(result["serial_read_successful"])
        self.assertEqual(self.hass.data, {})

    async def test_invalid_operation_does_not_connect(self):
        result = await self.run_action("other")
        self.assertEqual(result["error_code"], "invalid_operation")
        self.connector.establish_connection.assert_not_awaited()

    async def test_action_registration_and_private_error(self):
        from test_gatt_probe import _load_probe as _load_gatt_probe, _load_setup
        integration, _, _, exceptions = _load_setup(_load_gatt_probe()[0])
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services, data={}, config_entries=Mock())
        self.assertTrue(await integration.async_setup(hass, {}))
        action = next(
            call for call in services.async_register.call_args_list
            if call.args[1] == "probe_serial_stability"
        )
        self.assertEqual(action.kwargs["supports_response"], "response_only")
        result = await action.args[2](types.SimpleNamespace(
            data={"address": self.address, "operation": "set_reference"}
        ))
        self.assertEqual(result, {"reference_available": True})
        integration._test_stability.async_probe_serial_stability.assert_awaited_once_with(
            hass, self.address, "set_reference"
        )
        self.assertEqual(hass.data, {})
        hass.config_entries.assert_not_called()
        integration._test_stability.async_probe_serial_stability.side_effect = RuntimeError(self.address)
        with self.assertRaises(exceptions.ServiceValidationError) as caught:
            await action.args[2](types.SimpleNamespace(
                data={"address": self.address, "operation": "compare"}
            ))
        self.assertNotIn(self.address, str(caught.exception))
