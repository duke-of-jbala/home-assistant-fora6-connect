"""Synthetic-only tests for the read-only Stage 13A-P1 callback observer."""

import asyncio
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from test_gatt_probe import _load_probe, _load_setup, _registered_action


ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
ADDRESS = "aa:bb:cc:dd:ee:ff"  # Synthetic fixture only.


def load_observer():
    homeassistant = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    bluetooth.BluetoothScanningMode = types.SimpleNamespace(PASSIVE="passive")
    bluetooth.BluetoothCallbackReplay = types.SimpleNamespace(DISABLED="disabled")
    bluetooth.async_register_advertisement_callback = Mock(return_value=Mock())
    bluetooth.async_register_callback = Mock(return_value=Mock())
    bluetooth.async_clear_advertisement_history = Mock()
    name = "_fora6_advertisement_observer_test"
    spec = importlib.util.spec_from_file_location(name, ROOT / "advertisement_observer.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        "homeassistant": homeassistant,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
        name: module,
    }):
        spec.loader.exec_module(module)
    return module, bluetooth


def info(source, *, uuids=("glucose", "custom")):
    return types.SimpleNamespace(
        name="FORA 6 CONNECT", source=source, service_uuids=uuids,
        manufacturer_data={123: b"synthetic"}, service_data={},
        connectable=True, address=ADDRESS, raw=b"private-synthetic-payload",
    )


class AdvertisementObserverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.observer, self.bluetooth = load_observer()
        self.stop = asyncio.Event()
        self.hass = object()

    async def start(self):
        task = asyncio.create_task(self.observer.async_observe_advertisements(
            self.hass, ADDRESS, self.stop
        ))
        await asyncio.sleep(0)
        packet = self.bluetooth.async_register_advertisement_callback.call_args.args[1]
        changed = self.bluetooth.async_register_callback.call_args.args[1]
        return task, packet, changed

    def assert_read_only(self):
        self.bluetooth.async_register_advertisement_callback.assert_called_once()
        self.assertEqual(
            self.bluetooth.async_register_advertisement_callback.call_args.args[2], ADDRESS
        )
        self.bluetooth.async_register_callback.assert_called_once()
        args = self.bluetooth.async_register_callback.call_args.args
        self.assertEqual(args[2], {"address": ADDRESS})
        self.assertEqual(args[3], "passive")
        self.assertEqual(self.bluetooth.async_register_callback.call_args.kwargs,
                         {"replay": "disabled"})
        self.bluetooth.async_clear_advertisement_history.assert_not_called()

    def assert_cancelled(self):
        self.bluetooth.async_register_advertisement_callback.return_value.assert_called_once()
        self.bluetooth.async_register_callback.return_value.assert_called_once()

    async def test_repeated_packets_without_changed_dispatch(self):
        task, packet, changed = await self.start()
        for _ in range(3):
            packet(info("private-source-one"))
        changed(info("private-source-one"), "new")
        self.stop.set()
        result = await task
        self.assertEqual(result["packet_callback_count"], 3)
        self.assertEqual(result["changed_callback_count"], 1)
        self.assertEqual(result["packet_source_counts"], {"Source A": 3})
        self.assertEqual(result["changed_source_counts"], {"Source A": 1})
        self.assertEqual(result["first_packet_shape"], result["last_packet_shape"])
        self.assertEqual(result["packet_shape_change_count"], 0)
        self.assertTrue(result["stopped_by_unload"])
        self.assertTrue(result["callback_cleanup_successful"])
        self.assert_read_only()
        self.assert_cancelled()
        serialized = json.dumps(result)
        for private in (ADDRESS, "private-source-one", "private-synthetic-payload", "synthetic"):
            self.assertNotIn(private, serialized)

    async def test_multiple_sources_and_structural_change(self):
        task, packet, changed = await self.start()
        packet(info("private-source-one"))
        packet(info("private-source-two", uuids=("glucose",)))
        changed(info("private-source-two"), "changed")
        self.stop.set()
        result = await task
        self.assertEqual(result["packet_source_counts"], {"Source A": 1, "Source B": 1})
        self.assertEqual(result["changed_source_counts"], {"Source B": 1})
        self.assertEqual(result["packet_shape_change_count"], 1)
        self.assertEqual(result["last_packet_shape"]["service_uuid_count"], 1)
        self.assertEqual(
            [event["source"] for event in result["packet_event_sample"]],
            ["Source A", "Source B"],
        )
        self.assert_cancelled()

    async def test_no_packet_is_not_a_fabricated_absence_event(self):
        task, _, _ = await self.start()
        self.stop.set()
        result = await task
        self.assertEqual(result["packet_callback_count"], 0)
        self.assertEqual(result["changed_callback_count"], 0)
        self.assertIsNone(result["first_packet_shape"])
        self.assert_cancelled()

    async def test_event_samples_are_bounded(self):
        task, packet, _ = await self.start()
        for _ in range(100):
            packet(info("private-source-one"))
        self.stop.set()
        result = await task
        self.assertEqual(result["packet_callback_count"], 100)
        self.assertEqual(len(result["packet_event_sample"]), 32)
        self.assert_cancelled()

    async def test_time_limit_removes_callbacks(self):
        self.observer.OBSERVATION_SECONDS = 0.001
        result = await self.observer.async_observe_advertisements(
            self.hass, ADDRESS, self.stop
        )
        self.assertEqual(result["observation_seconds"], 0.001)
        self.assertFalse(result["stopped_by_unload"])
        self.assert_cancelled()

    async def test_cancellation_removes_both_callbacks(self):
        task, _, _ = await self.start()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assert_cancelled()

    async def test_second_registration_failure_removes_first_callback(self):
        self.bluetooth.async_register_callback.side_effect = RuntimeError("synthetic")
        with self.assertRaises(RuntimeError):
            await self.observer.async_observe_advertisements(self.hass, ADDRESS, self.stop)
        self.bluetooth.async_register_advertisement_callback.return_value.assert_called_once()

    async def test_one_cancel_error_still_attempts_other_cancel(self):
        self.bluetooth.async_register_callback.return_value.side_effect = RuntimeError(
            "synthetic"
        )
        task, _, _ = await self.start()
        self.stop.set()
        result = await task
        self.assertFalse(result["callback_cleanup_successful"])
        self.assert_cancelled()

    async def test_action_uses_configured_entry_and_unload_stops_observation(self):
        integration, _, _, errors = _load_setup(_load_probe()[0])
        async def wait_for_unload(hass, address, stop_event):
            await stop_event.wait()
            return {"packet_callback_count": 0}

        integration.async_observe_advertisements.side_effect = wait_for_unload
        runtime = types.SimpleNamespace(
            address=ADDRESS, advertisement_observation_stop=None,
            refresh_coordinator=object(),
        )
        entry = types.SimpleNamespace(domain="fora6_connect", runtime_data=runtime)
        hass = types.SimpleNamespace(
            services=types.SimpleNamespace(async_register=Mock()),
            config_entries=types.SimpleNamespace(
                async_get_entry=Mock(return_value=entry),
                async_unload_platforms=AsyncMock(return_value=True),
            ),
        )
        await integration.async_setup(hass, {})
        action = _registered_action(hass.services, "observe_advertisements")
        self.assertEqual(action.kwargs["supports_response"], "response_only")
        request = types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"})
        task = asyncio.create_task(action.args[2](request))
        await asyncio.sleep(0)
        self.assertIsNotNone(runtime.advertisement_observation_stop)
        with self.assertRaises(errors.ServiceValidationError):
            await action.args[2](request)
        await integration.async_unload_entry(hass, entry)
        self.assertEqual(await task, {"packet_callback_count": 0})
        self.assertIsNone(runtime.advertisement_observation_stop)
        integration.async_observe_advertisements.assert_awaited_once()
        self.assertEqual(integration.async_observe_advertisements.await_args.args[1], ADDRESS)

    def test_no_connection_command_cache_clear_or_logging_in_observer(self):
        source = (ROOT / "advertisement_observer.py").read_text()
        for forbidden in (
            "async_ble_device_from_address", "establish_connection", "start_notify",
            "write_gatt_char", "async_clear_advertisement_history(",
            "async_request_active_scan", "async_refresh", "_LOGGER", "print(",
        ):
            self.assertNotIn(forbidden, source)
