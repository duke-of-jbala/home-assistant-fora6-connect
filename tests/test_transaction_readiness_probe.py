"""Synthetic-only tests for the one-attempt Stage 13A-P4 readiness action."""

import asyncio
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from test_gatt_probe import _load_probe as load_gatt, _load_setup, _registered_action
from test_protocol_probe import _load_probe as load_transport


ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
ADDRESS = "synthetic-private-address"


def load_readiness():
    identity, bluetooth, connector = load_transport()
    name = "_fora6_readiness_test"
    package = types.ModuleType(name)
    package.__path__ = [str(ROOT)]
    transport = types.ModuleType(f"{name}.bluetooth")
    transport.Fora6BluetoothTransport = identity.Fora6BluetoothTransport
    transport.TransportError = identity.TransportError
    homeassistant = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    spec = importlib.util.spec_from_file_location(
        f"{name}.transaction_readiness_probe", ROOT / "transaction_readiness_probe.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        name: package,
        transport.__name__: transport,
        "homeassistant": homeassistant,
        "homeassistant.core": core,
        spec.name: module,
    }):
        spec.loader.exec_module(module)
    return module, identity, bluetooth, connector


class ReadinessProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.probe, self.identity, self.bluetooth, self.connector = load_readiness()
        self.hass = object()
        self.device = object()
        self.bluetooth.async_ble_device_from_address = Mock(return_value=self.device)
        self.characteristic = types.SimpleNamespace(
            uuid=self.identity.CHARACTERISTIC_UUID, properties=("write", "notify")
        )
        self.service = types.SimpleNamespace(
            uuid=self.identity.SERVICE_UUID, characteristics=[self.characteristic]
        )
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[self.service],
            start_notify=AsyncMock(),
            stop_notify=AsyncMock(),
            disconnect=AsyncMock(),
            write_gatt_char=AsyncMock(),
            read_gatt_char=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client

    async def run_probe(self):
        return await self.probe.async_probe_transaction_readiness(self.hass, ADDRESS)

    def assert_no_private_or_protocol_io(self, result):
        serialized = json.dumps(result)
        self.assertNotIn(ADDRESS, serialized)
        self.client.write_gatt_char.assert_not_awaited()
        self.client.read_gatt_char.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, ADDRESS, connectable=True
        )
        self.assertEqual(self.connector.establish_connection.await_count, 1)
        self.assertEqual(self.connector.establish_connection.call_args.kwargs["max_attempts"], 1)

    async def test_success_subscribes_once_then_unsubscribes_and_disconnects(self):
        result = await self.run_probe()
        self.assertTrue(result["notification_subscription_successful"])
        self.assertTrue(result["cleanup_successful"])
        self.assertIsNone(result["failure_stage"])
        self.assertTrue(result["custom_service_found"])
        self.assertTrue(result["custom_characteristic_found"])
        self.client.start_notify.assert_awaited_once()
        self.client.stop_notify.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()
        self.assert_no_private_or_protocol_io(result)

    async def test_no_device_stops_before_connection(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        result = await self.run_probe()
        self.assertEqual(result["failure_stage"], "device_resolution")
        self.assertEqual(result["failure_code"], "no_connectable_device")
        self.assertFalse(result["connection_attempted"])
        self.connector.establish_connection.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()

    async def test_connection_failure_one_attempt(self):
        self.connector.establish_connection.side_effect = RuntimeError(ADDRESS)
        result = await self.run_probe()
        self.assertEqual(result["failure_stage"], "connection")
        self.assertEqual(result["failure_code"], "connection_failed")
        self.assertTrue(result["connection_attempted"])
        self.assertEqual(self.connector.establish_connection.await_count, 1)
        self.assertEqual(self.connector.establish_connection.call_args.kwargs["max_attempts"], 1)
        self.client.start_notify.assert_not_awaited()
        self.assertNotIn(ADDRESS, json.dumps(result))

    async def test_missing_service_stops_before_subscription(self):
        self.client.services = []
        result = await self.run_probe()
        self.assertEqual(result["failure_stage"], "service_discovery")
        self.assertFalse(result["custom_service_found"])
        self.assertFalse(result["notification_subscription_attempted"])
        self.client.disconnect.assert_awaited_once()

    async def test_missing_characteristic_stops_before_subscription(self):
        self.service.characteristics = []
        result = await self.run_probe()
        self.assertEqual(result["failure_stage"], "characteristic_lookup")
        self.assertTrue(result["custom_service_found"])
        self.assertFalse(result["custom_characteristic_found"])
        self.client.start_notify.assert_not_awaited()

    async def test_subscription_failure_disconnects_without_unsubscribe(self):
        self.client.start_notify.side_effect = RuntimeError(ADDRESS)
        result = await self.run_probe()
        self.assertEqual(result["failure_stage"], "notification_subscription")
        self.assertEqual(result["failure_code"], "subscription_failed")
        self.assertTrue(result["notification_subscription_attempted"])
        self.assertFalse(result["notification_subscription_successful"])
        self.client.start_notify.assert_awaited_once()
        self.client.stop_notify.assert_not_awaited()
        self.client.disconnect.assert_awaited_once()
        self.assert_no_private_or_protocol_io(result)

    async def test_cleanup_failure_after_success_is_reported(self):
        self.client.stop_notify.side_effect = RuntimeError(ADDRESS)
        result = await self.run_probe()
        self.assertTrue(result["notification_subscription_successful"])
        self.assertFalse(result["cleanup_successful"])
        self.assertEqual(result["failure_stage"], "cleanup")
        self.assertIn("notification_stop_failed", result["cleanup_errors"])
        self.client.disconnect.assert_awaited_once()

    async def test_primary_failure_survives_disconnect_failure(self):
        self.client.start_notify.side_effect = RuntimeError(ADDRESS)
        self.client.disconnect.side_effect = RuntimeError(ADDRESS)
        result = await self.run_probe()
        self.assertEqual(result["failure_stage"], "notification_subscription")
        self.assertEqual(result["failure_code"], "subscription_failed")
        self.assertIn("disconnect_failed", result["cleanup_errors"])
        self.assertFalse(result["cleanup_successful"])

    async def test_unexpected_error_returns_type_without_private_message(self):
        with patch.object(
            self.probe.Fora6BluetoothTransport,
            "async_connect",
            AsyncMock(side_effect=ValueError(ADDRESS)),
        ):
            result = await self.run_probe()
        self.assertEqual(result["failure_stage"], "probe")
        self.assertEqual(result["exception_type"], "ValueError")
        self.assertNotIn(ADDRESS, json.dumps(result))

    async def test_cancellation_still_disconnects(self):
        entered = asyncio.Event()

        async def pending(*_args):
            entered.set()
            await asyncio.Event().wait()

        self.client.start_notify.side_effect = pending
        task = asyncio.create_task(self.run_probe())
        await entered.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.disconnect.assert_awaited_once()

    async def test_two_entries_and_unload_are_isolated(self):
        integration, _, _, errors = _load_setup(load_gatt()[0])
        started = asyncio.Event()

        async def pending(hass, address):
            started.set()
            await asyncio.Event().wait()

        integration.async_probe_transaction_readiness.side_effect = pending
        first = types.SimpleNamespace(
            domain="fora6_connect",
            runtime_data=types.SimpleNamespace(
                address="synthetic-first", gatt_lock=asyncio.Lock(),
                readiness_probe_task=None, advertisement_observation_stop=None,
            ),
        )
        second = types.SimpleNamespace(
            domain="fora6_connect",
            runtime_data=types.SimpleNamespace(
                address="synthetic-second", gatt_lock=asyncio.Lock(),
                readiness_probe_task=None, advertisement_observation_stop=None,
            ),
        )
        entries = {"first": first, "second": second}
        hass = types.SimpleNamespace(
            services=types.SimpleNamespace(async_register=Mock()),
            config_entries=types.SimpleNamespace(
                async_get_entry=Mock(side_effect=entries.get),
                async_unload_platforms=AsyncMock(return_value=True),
            ),
        )
        await integration.async_setup(hass, {})
        action = _registered_action(hass.services, "probe_transaction_readiness")
        first_request = types.SimpleNamespace(data={"config_entry_id": "first"})
        second_request = types.SimpleNamespace(data={"config_entry_id": "second"})
        first_task = asyncio.create_task(action.args[2](first_request))
        await started.wait()
        with self.assertRaises(errors.ServiceValidationError):
            await action.args[2](first_request)
        second_task = asyncio.create_task(action.args[2](second_request))
        await asyncio.sleep(0)
        self.assertIsNotNone(first.runtime_data.readiness_probe_task)
        self.assertIsNotNone(second.runtime_data.readiness_probe_task)
        self.assertIsNot(first.runtime_data.gatt_lock, second.runtime_data.gatt_lock)
        await integration.async_unload_entry(hass, first)
        with self.assertRaises(asyncio.CancelledError):
            await first_task
        self.assertIsNone(first.runtime_data.readiness_probe_task)
        await integration.async_unload_entry(hass, second)
        with self.assertRaises(asyncio.CancelledError):
            await second_task
        self.assertIsNone(second.runtime_data.readiness_probe_task)

    def test_no_forbidden_calls_in_probe_source(self):
        source = (ROOT / "transaction_readiness_probe.py").read_text()
        for forbidden in (
            "async_exchange(", "write_gatt_char(", "read_gatt_char(",
            "async_clear_advertisement_history(", "async_request_active_scan(",
            "async_register_callback(", "async_refresh(", "measurement_state.replace(",
            "_LOGGER", "print(",
        ):
            self.assertNotIn(forbidden, source)
