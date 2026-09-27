"""Synthetic, hardware-free process-local System ID comparison tests."""

import asyncio
import importlib.util
import json
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from test_serial_probe import _service
from test_system_id_probe import INTEGRATION, SYSTEM_VALUE, _load_system_probe

PACKAGE = "_fora6_system_stability_test"


def _load_stability():
    probe, bluetooth, connector = _load_system_probe()
    package = types.ModuleType(PACKAGE)
    package.__path__ = [str(INTEGRATION)]
    const = types.ModuleType(f"{PACKAGE}.const")
    exec((INTEGRATION / "const.py").read_text(), const.__dict__)
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE}.system_id_stability", INTEGRATION / "system_id_stability.py"
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        PACKAGE: package, f"{PACKAGE}.const": const,
        f"{PACKAGE}.system_id_probe": probe,
        "homeassistant": types.ModuleType("homeassistant"),
        "homeassistant.core": core,
    }):
        spec.loader.exec_module(module)
    return module, probe, bluetooth, connector


class SystemIdStabilityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.stability, self.probe, self.bluetooth, self.connector = _load_stability()
        self.hass = types.SimpleNamespace(data={}, config_entries=Mock())
        self.address = "SYNTHETIC-LOCATOR"
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.characteristic = types.SimpleNamespace(uuid=self.probe.SYSTEM_ID_UUID, properties=["read"])
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[_service(self.probe.DEVICE_INFORMATION_UUID, self.characteristic)],
            read_gatt_char=AsyncMock(return_value=SYSTEM_VALUE),
            disconnect=AsyncMock(), write_gatt_char=AsyncMock(),
            start_notify=AsyncMock(), pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client

    async def run_action(self, operation, hass=None):
        return await self.stability.async_probe_system_id_stability(
            hass or self.hass, self.address, operation
        )

    def assert_private(self, result):
        rendered = json.dumps(result)
        self.assertNotIn(self.address, rendered)
        self.assertNotIn(SYSTEM_VALUE.hex(), rendered)
        self.assertNotIn(SYSTEM_VALUE.hex(), repr(self.hass.data))
        for key in result:
            self.assertFalse(any(word in key for word in ("hash", "digest", "length", "prefix", "suffix")))

    async def test_set_reference_one_read_and_exact_compare(self):
        with patch.object(logging.Logger, "_log") as logged:
            set_result = await self.run_action("set_reference")
            same = await self.run_action("compare")
            self.client.read_gatt_char.return_value = bytes((1, 2, 3, 4, 5, 6, 7, 9))
            different = await self.run_action("compare")
        logged.assert_not_called()
        self.assertTrue(set_result["reference_set"])
        self.assertTrue(set_result["reference_available"])
        self.assertTrue(same["system_id_matches_reference"])
        self.assertFalse(different["system_id_matches_reference"])
        self.assertEqual(self.client.read_gatt_char.await_count, 3)
        self.assertEqual(self.client.disconnect.await_count, 3)
        self.client.write_gatt_char.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        self.hass.config_entries.assert_not_called()
        self.assertEqual(set(self.hass.data["fora6_connect"]), {"system_id_stability"})
        for result in (set_result, same, different):
            self.assert_private(result)

    async def test_compare_without_reference_does_not_connect(self):
        result = await self.run_action("compare")
        self.assertEqual(result["error_code"], "no_reference")
        self.assertFalse(result["reference_available"])
        self.connector.establish_connection.assert_not_awaited()
        self.assert_private(result)

    async def test_failed_and_unusable_reads_preserve_reference(self):
        await self.run_action("set_reference")
        self.client.read_gatt_char.side_effect = RuntimeError(self.address)
        failure = await self.run_action("set_reference")
        self.assertEqual(failure["error_code"], "system_id_read_failed")
        self.assertTrue(failure["reference_available"])
        self.client.read_gatt_char.side_effect = None
        for raw in (b"", b"1234567", bytes(8), b"\xff" * 8):
            with self.subTest(raw=raw):
                self.client.read_gatt_char.return_value = raw
                failure = await self.run_action("set_reference")
                self.assertEqual(failure["error_code"], "unusable_system_id")
                self.assertTrue(failure["reference_available"])
        self.client.read_gatt_char.return_value = SYSTEM_VALUE
        self.assertTrue((await self.run_action("compare"))["system_id_matches_reference"])

    async def test_set_replaces_only_after_success(self):
        await self.run_action("set_reference")
        replacement = bytes((1, 2, 3, 4, 5, 6, 7, 9))
        self.client.read_gatt_char.return_value = replacement
        self.assertTrue((await self.run_action("set_reference"))["reference_set"])
        self.client.read_gatt_char.return_value = SYSTEM_VALUE
        self.assertFalse((await self.run_action("compare"))["system_id_matches_reference"])
        self.client.read_gatt_char.return_value = replacement
        self.assertTrue((await self.run_action("compare"))["system_id_matches_reference"])

    async def test_cancellation_preserves_reference_and_disconnects(self):
        await self.run_action("set_reference")
        started = asyncio.Event()
        async def pending(_characteristic):
            started.set()
            await asyncio.Future()
        self.client.read_gatt_char.side_effect = pending
        task = asyncio.create_task(self.run_action("set_reference"))
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.read_gatt_char.side_effect = None
        self.client.read_gatt_char.return_value = SYSTEM_VALUE
        self.assertTrue((await self.run_action("compare"))["system_id_matches_reference"])
        self.assertEqual(self.client.disconnect.await_count, 3)

    async def test_new_hass_process_has_no_reference(self):
        await self.run_action("set_reference")
        restarted = types.SimpleNamespace(data={}, config_entries=Mock())
        result = await self.run_action("compare", restarted)
        self.assertEqual(result["error_code"], "no_reference")
        self.assertFalse(result["reference_available"])
        self.assert_private(result)

    async def test_lock_serializes_set_and_compare(self):
        started = asyncio.Event()
        release = asyncio.Event()
        async def delayed(_characteristic):
            started.set()
            await release.wait()
            return SYSTEM_VALUE
        self.client.read_gatt_char.side_effect = delayed
        setter = asyncio.create_task(self.run_action("set_reference"))
        await started.wait()
        comparer = asyncio.create_task(self.run_action("compare"))
        await asyncio.sleep(0)
        self.assertFalse(comparer.done())
        release.set()
        self.assertTrue((await setter)["reference_set"])
        self.assertTrue((await comparer)["system_id_matches_reference"])

    async def test_action_registration_and_private_error(self):
        from test_gatt_probe import _load_probe as _load_gatt_probe, _load_setup
        integration, _, _, exceptions = _load_setup(_load_gatt_probe()[0])
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services, data={}, config_entries=Mock())
        self.assertTrue(await integration.async_setup(hass, {}))
        action = next(call for call in services.async_register.call_args_list
                      if call.args[1] == "probe_system_id_stability")
        self.assertEqual(action.kwargs["supports_response"], "response_only")
        result = await action.args[2](types.SimpleNamespace(
            data={"address": self.address, "operation": "set_reference"}
        ))
        self.assertEqual(result, {"reference_available": True})
        integration._test_system_stability.async_probe_system_id_stability.assert_awaited_once_with(
            hass, self.address, "set_reference"
        )
        integration._test_system_stability.async_probe_system_id_stability.side_effect = RuntimeError(self.address)
        with self.assertRaises(exceptions.ServiceValidationError) as caught:
            await action.args[2](types.SimpleNamespace(
                data={"address": self.address, "operation": "compare"}
            ))
        self.assertNotIn(self.address, str(caught.exception))
