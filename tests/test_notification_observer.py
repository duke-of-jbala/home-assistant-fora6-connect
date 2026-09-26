"""Hardware-free tests for the development-only Stage 1C observer."""

import importlib.util
import json
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


INTEGRATION = (
    Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
)


def _load_observer():
    package = types.ModuleType("_fora6_observer_test")
    package.__path__ = [str(INTEGRATION)]
    const = types.ModuleType("_fora6_observer_test.const")
    exec((INTEGRATION / "const.py").read_text(encoding="utf-8"), const.__dict__)
    gatt = types.ModuleType("_fora6_observer_test.gatt_probe")
    gatt.CONNECTION_TIMEOUT = 20.0
    gatt.DISCONNECT_TIMEOUT = 10.0

    homeassistant = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    connector = types.ModuleType("bleak_retry_connector")
    connector.BleakClientWithServiceCache = type("FakeBleakClient", (), {})
    connector.BleakOutOfConnectionSlotsError = type(
        "BleakOutOfConnectionSlotsError", (Exception,), {}
    )
    connector.establish_connection = AsyncMock()
    modules = {
        "_fora6_observer_test": package,
        "_fora6_observer_test.const": const,
        "_fora6_observer_test.gatt_probe": gatt,
        "homeassistant": homeassistant,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
        "bleak_retry_connector": connector,
    }
    spec = importlib.util.spec_from_file_location(
        "_fora6_observer_test.notification_observer",
        INTEGRATION / "notification_observer.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, bluetooth, connector


def _service(uuid, *characteristics):
    return types.SimpleNamespace(
        uuid=uuid,
        characteristics=[
            types.SimpleNamespace(uuid=char_uuid, properties=properties)
            for char_uuid, properties in characteristics
        ],
    )


class NotificationObserverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.observer, self.bluetooth, self.connector = _load_observer()
        self.hass = object()
        self.address = "synthetic-private-device"
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[
                _service(
                    self.observer.GLUCOSE_SERVICE_UUID,
                    (self.observer.GLUCOSE_MEASUREMENT_UUID, ("notify",)),
                    (self.observer.GLUCOSE_CONTEXT_UUID, ("notify",)),
                    ("00002a52-0000-1000-8000-00805f9b34fb", ("write", "indicate")),
                ),
                _service(
                    self.observer.SERVICE_UUID,
                    (self.observer.CHARACTERISTIC_UUID, ("notify", "write")),
                ),
            ],
            start_notify=AsyncMock(),
            stop_notify=AsyncMock(),
            disconnect=AsyncMock(),
            read_gatt_char=AsyncMock(),
            write_gatt_char=AsyncMock(),
            write_gatt_descriptor=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client
        self.observer.OBSERVATION_SECONDS = 0.001

    def assert_boundary(self):
        self.client.read_gatt_char.assert_not_awaited()
        self.client.write_gatt_char.assert_not_awaited()
        self.client.write_gatt_descriptor.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        subscribed = [
            call.args[0].uuid for call in self.client.start_notify.call_args_list
        ]
        self.assertNotIn("00002a52-0000-1000-8000-00805f9b34fb", subscribed)

    async def test_all_three_subscriptions_attribution_lengths_and_unique_counts(self):
        async def observe(_seconds):
            callbacks = {
                call.args[0].uuid: call.args[1]
                for call in self.client.start_notify.call_args_list
            }
            callbacks[self.observer.GLUCOSE_MEASUREMENT_UUID](None, bytearray(b"alpha"))
            callbacks[self.observer.GLUCOSE_MEASUREMENT_UUID](None, bytearray(b"alpha"))
            callbacks[self.observer.GLUCOSE_MEASUREMENT_UUID](
                None, bytearray(b"longer")
            )
            callbacks[self.observer.GLUCOSE_CONTEXT_UUID](None, bytearray(b"alpha"))
            callbacks[self.observer.CHARACTERISTIC_UUID](None, bytearray(b"z"))

        with patch.object(
            self.observer.asyncio, "sleep", new=AsyncMock(side_effect=observe)
        ):
            result = await self.observer.async_observe_notifications(
                self.hass, self.address
            )

        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, self.address, connectable=True
        )
        self.assertEqual(
            self.connector.establish_connection.call_args.kwargs,
            {
                "max_attempts": 2,
                "use_services_cache": False,
                "timeout": 20.0,
                "pair": False,
            },
        )
        self.assertEqual(result["subscriptions_successful"], 3)
        self.assertEqual(result["subscriptions_attempted"], 3)
        self.assertEqual(result["notifications_observed"], 5)
        self.assertTrue(result["connection_successful"])
        self.assertTrue(result["disconnected_cleanly"])
        by_uuid = {item["uuid"]: item for item in result["characteristics"]}
        measure = by_uuid[self.observer.GLUCOSE_MEASUREMENT_UUID]
        self.assertEqual(measure["notification_count"], 3)
        self.assertEqual(measure["payload_lengths"], [5, 6])
        self.assertEqual(measure["length_counts"], {"5": 2, "6": 1})
        self.assertEqual(measure["distinct_payload_count"], 2)
        self.assertEqual(
            by_uuid[self.observer.GLUCOSE_CONTEXT_UUID]["notification_count"], 1
        )
        self.assertEqual(
            by_uuid[self.observer.CHARACTERISTIC_UUID]["notification_count"], 1
        )
        self.assertEqual(self.client.stop_notify.await_count, 3)
        self.assertEqual(
            [call.args[0].uuid for call in self.client.stop_notify.call_args_list],
            [uuid for _, uuid in reversed(self.observer.TARGETS)],
        )
        self.client.disconnect.assert_awaited_once()
        public = json.dumps(result)
        for private in (self.address, "alpha", "longer", "z"):
            self.assertNotIn(f'"{private}"', public)
        self.assert_boundary()

    async def test_zero_notifications_is_successful(self):
        with patch.object(logging.Logger, "_log") as recorded_logs:
            result = await self.observer.async_observe_notifications(
                self.hass, self.address
            )
        self.assertEqual(result["notifications_observed"], 0)
        self.assertEqual(result["subscriptions_successful"], 3)
        self.assertTrue(
            all(item["notification_count"] == 0 for item in result["characteristics"])
        )
        self.assertTrue(
            all(item["payload_lengths"] == [] for item in result["characteristics"])
        )
        self.assertTrue(
            all(
                item["distinct_payload_count"] == 0
                for item in result["characteristics"]
            )
        )
        self.client.disconnect.assert_awaited_once()
        self.assertNotIn(self.address, str(recorded_logs.call_args_list))
        self.assert_boundary()

    async def test_missing_characteristic_disconnects_without_subscription(self):
        self.client.services[0].characteristics.pop(1)
        with self.assertRaisesRegex(self.observer.ObservationError, "Expected Notify"):
            await self.observer.async_observe_notifications(self.hass, self.address)
        self.client.start_notify.assert_not_awaited()
        self.client.stop_notify.assert_not_awaited()
        self.client.disconnect.assert_awaited_once()
        self.assert_boundary()

    async def test_non_notify_characteristic_is_rejected(self):
        self.client.services[0].characteristics[0].properties = ("read",)
        with self.assertRaisesRegex(self.observer.ObservationError, "Expected Notify"):
            await self.observer.async_observe_notifications(self.hass, self.address)
        self.client.start_notify.assert_not_awaited()
        self.client.disconnect.assert_awaited_once()

    async def test_first_subscription_failure_continues_and_cleans_successes(self):
        attempts = 0

        async def subscribe(_characteristic, _callback):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise RuntimeError(self.address)

        self.client.start_notify.side_effect = subscribe
        with patch.object(logging.Logger, "_log") as recorded_logs:
            result = await self.observer.async_observe_notifications(
                self.hass, self.address
            )
        self.assertNotIn(self.address, json.dumps(result))
        self.assertNotIn(self.address, str(recorded_logs.call_args_list))
        self.assertEqual(self.client.start_notify.await_count, 3)
        self.assertEqual(result["subscriptions_attempted"], 3)
        self.assertEqual(result["subscriptions_successful"], 2)
        self.assertEqual(self.client.stop_notify.await_count, 2)
        self.assertEqual(
            [call.args[0].uuid for call in self.client.stop_notify.call_args_list],
            [self.observer.CHARACTERISTIC_UUID, self.observer.GLUCOSE_CONTEXT_UUID],
        )
        by_uuid = {item["uuid"]: item for item in result["characteristics"]}
        self.assertFalse(
            by_uuid[self.observer.GLUCOSE_MEASUREMENT_UUID]["subscription_successful"]
        )
        self.assertEqual(
            by_uuid[self.observer.GLUCOSE_MEASUREMENT_UUID]["subscription_error"],
            "RuntimeError",
        )
        self.assertTrue(
            by_uuid[self.observer.GLUCOSE_CONTEXT_UUID]["subscription_successful"]
        )
        self.client.disconnect.assert_awaited_once()
        self.assert_boundary()

    async def test_all_subscriptions_fail_returns_normal_result(self):
        self.client.start_notify.side_effect = RuntimeError(self.address)
        with patch.object(self.observer.asyncio, "sleep", new=AsyncMock()) as sleep:
            result = await self.observer.async_observe_notifications(
                self.hass, self.address
            )
        sleep.assert_not_awaited()
        self.assertEqual(result["subscriptions_attempted"], 3)
        self.assertEqual(result["subscriptions_successful"], 0)
        self.assertEqual(result["observation_duration_seconds"], 0.0)
        self.assertEqual(result["notifications_observed"], 0)
        self.assertEqual(self.client.start_notify.await_count, 3)
        self.client.stop_notify.assert_not_awaited()
        self.client.disconnect.assert_awaited_once()
        self.assertTrue(
            all(
                not item["subscription_successful"] for item in result["characteristics"]
            )
        )
        self.assertNotIn(self.address, json.dumps(result))
        self.assert_boundary()

    async def test_only_custom_subscription_succeeds(self):
        async def subscribe(characteristic, _callback):
            if characteristic.uuid != self.observer.CHARACTERISTIC_UUID:
                raise RuntimeError("GATT descriptor failure")

        self.client.start_notify.side_effect = subscribe
        result = await self.observer.async_observe_notifications(
            self.hass, self.address
        )
        self.assertEqual(result["subscriptions_successful"], 1)
        self.client.stop_notify.assert_awaited_once()
        self.assertEqual(
            self.client.stop_notify.call_args.args[0].uuid,
            self.observer.CHARACTERISTIC_UUID,
        )
        self.assert_boundary()

    async def test_only_standard_subscriptions_succeed(self):
        async def subscribe(characteristic, _callback):
            if characteristic.uuid == self.observer.CHARACTERISTIC_UUID:
                raise RuntimeError("Insufficient Authentication")

        self.client.start_notify.side_effect = subscribe
        result = await self.observer.async_observe_notifications(
            self.hass, self.address
        )
        self.assertEqual(result["subscriptions_successful"], 2)
        self.assertEqual(
            [call.args[0].uuid for call in self.client.stop_notify.call_args_list],
            [self.observer.GLUCOSE_CONTEXT_UUID, self.observer.GLUCOSE_MEASUREMENT_UUID],
        )
        self.assert_boundary()

    async def test_structured_error_code_is_reported_without_private_text(self):
        error = RuntimeError(self.address + " private payload")
        error.dbus_error = "org.bluez.Error.NotAuthorized"
        self.client.start_notify.side_effect = error
        with patch.object(logging.Logger, "_log") as recorded_logs:
            result = await self.observer.async_observe_notifications(
                self.hass, self.address
            )
        self.assertEqual(
            result["characteristics"][0]["subscription_error"],
            "RuntimeError (org.bluez.Error.NotAuthorized)",
        )
        self.assertNotIn(self.address, json.dumps(result))
        self.assertNotIn(self.address, str(recorded_logs.call_args_list))
        self.assert_boundary()

    async def test_observation_exception_unsubscribes_and_disconnects(self):
        with patch.object(
            self.observer.asyncio,
            "sleep",
            new=AsyncMock(side_effect=RuntimeError(self.address)),
        ):
            with self.assertRaises(self.observer.ObservationError) as caught:
                await self.observer.async_observe_notifications(self.hass, self.address)
        self.assertNotIn(self.address, str(caught.exception))
        self.assertEqual(self.client.stop_notify.await_count, 3)
        self.client.disconnect.assert_awaited_once()
        self.assert_boundary()

    async def test_cancellation_still_unsubscribes_and_disconnects(self):
        with patch.object(
            self.observer.asyncio,
            "sleep",
            new=AsyncMock(side_effect=self.observer.asyncio.CancelledError()),
        ):
            with self.assertRaises(self.observer.asyncio.CancelledError):
                await self.observer.async_observe_notifications(
                    self.hass, self.address
                )
        self.assertEqual(self.client.stop_notify.await_count, 3)
        self.client.disconnect.assert_awaited_once()
        self.assert_boundary()

    async def test_stop_failure_still_stops_others_and_disconnects(self):
        self.client.stop_notify.side_effect = [RuntimeError(self.address), None, None]
        result = await self.observer.async_observe_notifications(
            self.hass, self.address
        )
        self.assertFalse(result["subscriptions_stopped_cleanly"])
        self.assertTrue(result["disconnected_cleanly"])
        self.assertNotIn(self.address, json.dumps(result))
        self.assertEqual(self.client.stop_notify.await_count, 3)
        self.client.disconnect.assert_awaited_once()
        self.assert_boundary()

    async def test_disconnect_failure_is_sanitized(self):
        self.client.disconnect.side_effect = RuntimeError(self.address)
        result = await self.observer.async_observe_notifications(
            self.hass, self.address
        )
        self.assertFalse(result["disconnected_cleanly"])
        self.assertTrue(result["subscriptions_stopped_cleanly"])
        self.assertNotIn(self.address, json.dumps(result))
        self.assertEqual(self.client.stop_notify.await_count, 3)
        self.assert_boundary()

    async def test_no_connectable_device_never_connects(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        with self.assertRaisesRegex(self.observer.ObservationError, "No connectable"):
            await self.observer.async_observe_notifications(self.hass, self.address)
        self.connector.establish_connection.assert_not_awaited()
        self.assert_boundary()

    async def test_connection_failure_does_not_echo_address(self):
        self.connector.establish_connection.side_effect = RuntimeError(self.address)
        with self.assertRaises(self.observer.ObservationError) as caught:
            await self.observer.async_observe_notifications(self.hass, self.address)
        self.assertNotIn(self.address, str(caught.exception))
        self.client.start_notify.assert_not_awaited()
        self.assert_boundary()

    async def test_connection_slot_failure_is_reported(self):
        self.connector.establish_connection.side_effect = (
            self.connector.BleakOutOfConnectionSlotsError(self.address)
        )
        with self.assertRaisesRegex(self.observer.ObservationError, "connection slot"):
            await self.observer.async_observe_notifications(self.hass, self.address)
        self.assert_boundary()
