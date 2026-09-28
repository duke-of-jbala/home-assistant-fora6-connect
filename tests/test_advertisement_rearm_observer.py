"""Synthetic tests for the one-clear development observer; no meter used."""

import asyncio
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from test_advertisement_observer import ADDRESS, info, load_observer
from test_gatt_probe import _load_probe, _load_setup, _registered_action


ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"


def load_rearm():
    base, bluetooth = load_observer()
    bluetooth.async_register_advertisement_callback = None  # Core 2026.9.4
    package = types.ModuleType("_fora6_rearm_test")
    package.__path__ = [str(ROOT)]
    homeassistant = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    components.bluetooth = bluetooth
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    name = "_fora6_rearm_test.advertisement_rearm_observer"
    spec = importlib.util.spec_from_file_location(name, ROOT / "advertisement_rearm_observer.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        "_fora6_rearm_test": package,
        "_fora6_rearm_test.advertisement_observer": base,
        "homeassistant": homeassistant,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
        name: module,
    }):
        spec.loader.exec_module(module)
    return module, bluetooth


class RearmObserverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.observer, self.bluetooth = load_rearm()
        self.stop = asyncio.Event()
        self.hass = object()

    async def start(self):
        task = asyncio.create_task(self.observer.async_observe_advertisement_rearm(
            self.hass, ADDRESS, self.stop,
        ))
        await asyncio.sleep(0)
        callback = self.bluetooth.async_register_callback.call_args.args[1]
        return task, callback

    async def first(self, callback):
        callback(info("private-proxy"), "changed")
        for _ in range(5):
            if self.bluetooth.async_clear_advertisement_history.called:
                break
            await asyncio.sleep(0)

    async def test_one_clear_only_after_first_callback_and_same_on_callback(self):
        task, callback = await self.start()
        self.bluetooth.async_clear_advertisement_history.assert_not_called()
        await self.first(callback)
        self.bluetooth.async_clear_advertisement_history.assert_called_once_with(
            self.hass, ADDRESS
        )
        callback(info("private-proxy"), "changed")
        self.stop.set()
        result = await task
        self.assertTrue(result["first_callback_seen"])
        self.assertTrue(result["clear_performed"])
        self.assertEqual(result["changed_callback_count"], 2)
        self.assertEqual(result["callbacks_after_clear_count"], 1)
        self.assertTrue(result["callback_cleanup_successful"])
        self.assertEqual(result["changed_source_counts"], {"Source A": 2})
        self.assertEqual(self.bluetooth.async_register_callback.call_args.args[2], {"address": ADDRESS})
        self.assertEqual(self.bluetooth.async_register_callback.call_args.args[3], "passive")
        self.assertEqual(self.bluetooth.async_register_callback.call_args.kwargs,
                         {"replay": "disabled"})
        self.bluetooth.async_register_callback.return_value.assert_called_once()
        serialized = json.dumps(result)
        for private in (ADDRESS, "private-proxy", "private-synthetic-payload", "synthetic"):
            self.assertNotIn(private, serialized)

    async def test_no_changed_callback_means_no_clear(self):
        task, _ = await self.start()
        self.stop.set()
        result = await task
        self.assertFalse(result["first_callback_seen"])
        self.assertFalse(result["clear_performed"])
        self.bluetooth.async_clear_advertisement_history.assert_not_called()
        self.bluetooth.async_register_callback.return_value.assert_called_once()

    async def test_first_callback_then_no_second_callback(self):
        task, callback = await self.start()
        await self.first(callback)
        self.stop.set()
        result = await task
        self.assertEqual(result["callbacks_after_clear_count"], 0)
        self.assertEqual(result["changed_callback_count"], 1)

    async def test_later_off_on_uses_existing_no_clear_observer(self):
        first_task, first_callback = await self.start()
        await self.first(first_callback)
        self.stop.set()
        first_result = await first_task
        self.assertEqual(first_result["callbacks_after_clear_count"], 0)
        self.bluetooth.async_clear_advertisement_history.assert_called_once()

        old, bluetooth = load_observer()
        bluetooth.async_register_advertisement_callback = None
        stop = asyncio.Event()
        second_task = asyncio.create_task(old.async_observe_advertisements(
            self.hass, ADDRESS, stop,
        ))
        await asyncio.sleep(0)
        bluetooth.async_register_callback.call_args.args[1](info("private-proxy"), "changed")
        stop.set()
        second_result = await second_task
        self.assertEqual(second_result["changed_callback_count"], 1)
        bluetooth.async_clear_advertisement_history.assert_not_called()
        # Physical OFF and ON state cannot be asserted by a synthetic callback.

    async def test_cancel_and_unload_cleanup(self):
        task, callback = await self.start()
        await self.first(callback)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.bluetooth.async_register_callback.return_value.assert_called_once()
        self.bluetooth.async_clear_advertisement_history.assert_called_once()

        observer, bluetooth = load_rearm()
        stop = asyncio.Event()
        task = asyncio.create_task(observer.async_observe_advertisement_rearm(
            self.hass, ADDRESS, stop,
        ))
        await asyncio.sleep(0)
        stop.set()
        result = await task
        self.assertTrue(result["stopped_by_unload"])
        bluetooth.async_register_callback.return_value.assert_called_once()

    async def test_clear_error_reports_only_stage_and_type(self):
        self.bluetooth.async_clear_advertisement_history.side_effect = RuntimeError(ADDRESS)
        task, callback = await self.start()
        callback(info("private-proxy"), "changed")
        with self.assertRaises(self.observer.AdvertisementObservationError) as context:
            await task
        self.assertEqual(context.exception.stage, "clear_history")
        self.assertEqual(context.exception.error_type, "RuntimeError")
        self.assertNotIn(ADDRESS, str(context.exception))
        self.bluetooth.async_register_callback.return_value.assert_called_once()

    async def test_missing_clear_api_is_sanitized(self):
        del self.bluetooth.async_clear_advertisement_history
        task, callback = await self.start()
        callback(info("private-proxy"), "changed")
        with self.assertRaises(self.observer.AdvertisementObservationError) as context:
            await task
        self.assertEqual(context.exception.stage, "clear_history")
        self.assertEqual(context.exception.error_type, "AttributeError")

    async def test_registration_error_is_sanitized(self):
        self.bluetooth.async_register_callback.side_effect = ValueError(ADDRESS)
        with self.assertRaises(self.observer.AdvertisementObservationError) as context:
            await self.observer.async_observe_advertisement_rearm(self.hass, ADDRESS, self.stop)
        self.assertEqual(context.exception.stage, "changed_callback_registration")
        self.assertNotIn(ADDRESS, str(context.exception))
        self.bluetooth.async_clear_advertisement_history.assert_not_called()

    async def test_action_is_entry_scoped_and_exclusive_with_old_observer(self):
        integration, _, _, errors = _load_setup(_load_probe()[0])
        async def wait_for_unload(hass, address, stop_event):
            await stop_event.wait()
            return {"clear_performed": False}

        integration.async_observe_advertisement_rearm.side_effect = wait_for_unload
        runtime = types.SimpleNamespace(address=ADDRESS, advertisement_observation_stop=None)
        entry = types.SimpleNamespace(domain="fora6_connect", runtime_data=runtime)
        hass = types.SimpleNamespace(
            services=types.SimpleNamespace(async_register=Mock()),
            config_entries=types.SimpleNamespace(
                async_get_entry=Mock(return_value=entry),
                async_unload_platforms=AsyncMock(return_value=True),
            ),
        )
        await integration.async_setup(hass, {})
        rearm = _registered_action(hass.services, "observe_advertisement_rearm")
        old = _registered_action(hass.services, "observe_advertisements")
        request = types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"})
        task = asyncio.create_task(rearm.args[2](request))
        await asyncio.sleep(0)
        with self.assertRaises(errors.ServiceValidationError):
            await old.args[2](request)
        await integration.async_unload_entry(hass, entry)
        self.assertEqual(await task, {"clear_performed": False})
        self.assertIsNone(runtime.advertisement_observation_stop)
        self.assertEqual(integration.async_observe_advertisement_rearm.await_args.args[1], ADDRESS)

    async def test_action_preserves_sanitized_clear_failure(self):
        integration, _, _, errors = _load_setup(_load_probe()[0])
        integration.async_observe_advertisement_rearm.side_effect = (
            integration.AdvertisementObservationError("stage=clear_history, type=RuntimeError")
        )
        runtime = types.SimpleNamespace(address=ADDRESS, advertisement_observation_stop=None)
        entry = types.SimpleNamespace(domain="fora6_connect", runtime_data=runtime)
        hass = types.SimpleNamespace(
            services=types.SimpleNamespace(async_register=Mock()),
            config_entries=types.SimpleNamespace(async_get_entry=Mock(return_value=entry)),
        )
        await integration.async_setup(hass, {})
        action = _registered_action(hass.services, "observe_advertisement_rearm")
        with self.assertRaises(errors.ServiceValidationError) as context:
            await action.args[2](types.SimpleNamespace(data={"config_entry_id": "entry"}))
        self.assertIn("stage=clear_history, type=RuntimeError", str(context.exception))
        self.assertNotIn(ADDRESS, str(context.exception))
        self.assertIsNone(runtime.advertisement_observation_stop)

    def test_no_gatt_sensor_or_production_auto_sync(self):
        source = (ROOT / "advertisement_rearm_observer.py").read_text()
        for forbidden in (
            "establish_connection", "start_notify", "write_gatt_char",
            "async_ble_device_from_address", "async_request_active_scan",
            "async_refresh", "sensor_state", "create_task(async_refresh",
            "_LOGGER", "print(",
        ):
            self.assertNotIn(forbidden, source)
        self.assertEqual(source.count("bluetooth.async_clear_advertisement_history("), 1)
