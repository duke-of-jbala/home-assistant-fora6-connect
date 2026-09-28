"""Hardware-free tests for the reusable HA Bluetooth session boundary."""

import asyncio
import ast
import logging
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

from test_protocol_probe import (
    INTEGRATION,
    PROJECT_REQUEST,
    PROJECT_RESPONSE,
    WAKE_REQUEST,
    WAKE_RESPONSE,
    _load_probe,
)


class BluetoothTransportTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.probe, self.bluetooth, self.connector = _load_probe()
        self.hass = object()
        self.address = "synthetic-runtime-address"
        self.ble_device = object()
        self.bluetooth.async_ble_device_from_address = Mock(return_value=self.ble_device)
        self.characteristic = types.SimpleNamespace(
            uuid=self.probe.CHARACTERISTIC_UUID, properties=("write", "notify")
        )
        self.service = types.SimpleNamespace(
            uuid=self.probe.SERVICE_UUID, characteristics=[self.characteristic]
        )
        self.events = []
        self.callback = None
        self.responses = {WAKE_REQUEST: WAKE_RESPONSE, PROJECT_REQUEST: PROJECT_RESPONSE}
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[self.service],
            start_notify=AsyncMock(side_effect=self._start),
            write_gatt_char=AsyncMock(side_effect=self._write),
            stop_notify=AsyncMock(side_effect=self._stop),
            disconnect=AsyncMock(side_effect=self._disconnect),
        )
        self.connector.establish_connection.return_value = self.client
        self.transport = self.probe.Fora6BluetoothTransport(
            self.hass, self.address, response_timeout=0.01
        )
        method_globals = self.probe.Fora6BluetoothTransport.async_exchange.__globals__
        self.protocol = method_globals["ProtocolFrame"]
        self.error_type = method_globals["TransportError"]

    async def _start(self, characteristic, callback):
        self.events.append("subscribe")
        self.callback = callback

    async def _write(self, characteristic, data, *, response):
        self.events.append("write")
        reply = self.responses.get(data)
        if reply is not None:
            self.callback(characteristic, bytearray(reply))

    async def _stop(self, characteristic):
        self.events.append("unsubscribe")

    async def _disconnect(self):
        self.events.append("disconnect")

    async def connected(self):
        await self.transport.async_connect()
        await self.transport.async_subscribe()

    async def failure(self, awaitable, code):
        with self.assertRaises(self.error_type) as captured:
            await awaitable
        self.assertEqual(captured.exception.code, code)
        self.assertEqual(str(captured.exception), code)
        self.assertNotIn(self.address, str(captured.exception))

    async def test_connectable_resolution_and_connection_contract(self):
        await self.transport.async_connect()
        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, self.address, connectable=True
        )
        self.assertIs(self.connector.establish_connection.call_args.args[1], self.ble_device)
        self.assertEqual(
            self.connector.establish_connection.call_args.kwargs,
            {
                "max_attempts": 2,
                "use_services_cache": False,
                "timeout": 20.0,
                "pair": False,
            },
        )
        self.assertTrue(self.transport.device_resolved)
        self.assertTrue(self.transport.connection_established)
        self.assertTrue(self.transport.characteristic_found)
        await self.transport.async_close()

    async def test_development_probe_can_limit_connection_to_one_attempt(self):
        single = self.probe.Fora6BluetoothTransport(
            self.hass, self.address, connect_max_attempts=1
        )
        await single.async_connect()
        self.assertEqual(
            self.connector.establish_connection.call_args.kwargs["max_attempts"], 1
        )
        await single.async_close()

    def test_nonpositive_connection_attempt_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            self.probe.Fora6BluetoothTransport(
                self.hass, self.address, connect_max_attempts=0
            )

    async def test_no_connectable_device(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        await self.failure(self.transport.async_connect(), "no_connectable_device")
        self.connector.establish_connection.assert_not_awaited()
        result = await self.transport.async_close()
        self.assertFalse(result.disconnected_cleanly)

    async def test_resolution_error_is_sanitized(self):
        self.bluetooth.async_ble_device_from_address.side_effect = RuntimeError(self.address)
        await self.failure(self.transport.async_connect(), "resolution_failed")
        self.connector.establish_connection.assert_not_awaited()

    async def test_no_connection_slot(self):
        self.connector.establish_connection.side_effect = (
            self.connector.BleakOutOfConnectionSlotsError()
        )
        await self.failure(self.transport.async_connect(), "no_connection_slot")

    async def test_connection_failure_is_sanitized(self):
        self.connector.establish_connection.side_effect = RuntimeError(self.address)
        await self.failure(self.transport.async_connect(), "connection_failed")

    async def test_connection_wait_is_bounded(self):
        async def never_connect(*_args, **_kwargs):
            await asyncio.Event().wait()
        self.connector.establish_connection.side_effect = never_connect
        with patch.dict(
            self.probe.Fora6BluetoothTransport.async_connect.__globals__,
            CONNECT_TOTAL_TIMEOUT=0.005,
        ):
            await self.failure(self.transport.async_connect(), "connection_failed")
        self.client.disconnect.assert_not_awaited()

    async def test_cancel_pending_connection_propagates_without_client(self):
        started = asyncio.Event()
        cancelled = asyncio.Event()
        async def pending(*_args, **_kwargs):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
        self.connector.establish_connection.side_effect = pending
        connecting = asyncio.create_task(self.transport.async_connect())
        await started.wait()
        connecting.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await connecting
        self.assertTrue(cancelled.is_set())
        self.client.disconnect.assert_not_awaited()

    async def test_cancel_connection_that_returns_client_closes_it_once(self):
        started = asyncio.Event()
        async def return_after_cancel(*_args, **_kwargs):
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                return self.client
        self.connector.establish_connection.side_effect = return_after_cancel
        connecting = asyncio.create_task(self.transport.async_connect())
        await started.wait()
        connecting.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await connecting
        self.client.disconnect.assert_awaited_once()
        await self.transport.async_close()
        self.client.disconnect.assert_awaited_once()

    async def test_connection_timeout_reaps_client_returned_on_cancel(self):
        async def return_after_cancel(*_args, **_kwargs):
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                return self.client
        self.connector.establish_connection.side_effect = return_after_cancel
        with patch.dict(
            self.probe.Fora6BluetoothTransport.async_connect.__globals__,
            CONNECT_TOTAL_TIMEOUT=0.005,
        ):
            await self.failure(self.transport.async_connect(), "connection_failed")
        self.client.disconnect.assert_awaited_once()
        await self.transport.async_close()
        self.client.disconnect.assert_awaited_once()

    async def test_late_client_after_cancellation_bound_is_disconnected(self):
        release = asyncio.Event()
        async def slow_cancel(*_args, **_kwargs):
            while not release.is_set():
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    continue
            return self.client
        self.connector.establish_connection.side_effect = slow_cancel
        with patch.dict(
            self.probe.Fora6BluetoothTransport.async_connect.__globals__,
            CONNECT_TOTAL_TIMEOUT=0.005,
        ):
            await self.failure(self.transport.async_connect(), "connection_failed")
        await self.transport.async_close()
        release.set()
        for _ in range(50):
            if self.client.disconnect.await_count:
                break
            await asyncio.sleep(0)
        self.client.disconnect.assert_awaited_once()

    async def test_connection_cancellation_error_is_private(self):
        started = asyncio.Event()
        async def fail_after_cancel(*_args, **_kwargs):
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                raise RuntimeError(self.address) from None
        self.connector.establish_connection.side_effect = fail_after_cancel
        connecting = asyncio.create_task(self.transport.async_connect())
        await started.wait()
        with patch.object(logging.Logger, "_log") as logs:
            connecting.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await connecting
        self.assertNotIn(self.address, str(logs.call_args_list))

    async def test_disconnected_client_after_connect_is_cleaned_up(self):
        self.client.is_connected = False
        await self.failure(self.transport.async_connect(), "peer_disconnected")
        result = await self.transport.async_close()
        self.assertTrue(result.disconnected_cleanly)
        self.client.disconnect.assert_awaited_once()

    async def test_connection_state_exception_is_sanitized(self):
        class BadState:
            def __bool__(inner_self):
                raise RuntimeError(self.address)
        self.client.is_connected = BadState()
        await self.failure(self.transport.async_connect(), "peer_disconnected")
        await self.transport.async_close()

    async def test_services_unavailable(self):
        self.client.services = None
        await self.failure(self.transport.async_connect(), "services_unavailable")
        self.assertTrue((await self.transport.async_close()).disconnected_cleanly)

    async def test_gatt_iteration_exception_is_sanitized(self):
        class BadServices:
            def __iter__(inner_self):
                raise RuntimeError(self.address)
        self.client.services = BadServices()
        await self.failure(self.transport.async_connect(), "custom_characteristic_missing")
        await self.transport.async_close()

    async def test_missing_service_or_characteristic(self):
        for services in ([], [types.SimpleNamespace(uuid=self.probe.SERVICE_UUID, characteristics=[])]):
            with self.subTest(services=services):
                self.client.services = services
                await self.failure(self.transport.async_connect(), "custom_characteristic_missing")
                await self.transport.async_close()
                self.transport = self.probe.Fora6BluetoothTransport(self.hass, self.address)

    async def test_missing_write_or_notify_property(self):
        for properties in (("notify",), ("write",), ("write-without-response", "notify")):
            with self.subTest(properties=properties):
                self.characteristic.properties = properties
                await self.failure(self.transport.async_connect(), "custom_properties_missing")
                await self.transport.async_close()
                self.transport = self.probe.Fora6BluetoothTransport(self.hass, self.address)

    async def test_subscription_success_and_single_call(self):
        await self.connected()
        self.client.start_notify.assert_awaited_once()
        self.assertIs(self.client.start_notify.call_args.args[0], self.characteristic)
        self.assertTrue(self.transport.subscription_established)
        await self.transport.async_close()

    async def test_subscription_failure_disconnects_without_stop(self):
        await self.transport.async_connect()
        self.client.start_notify.side_effect = RuntimeError(self.address)
        await self.failure(self.transport.async_subscribe(), "subscription_failed")
        result = await self.transport.async_close()
        self.assertFalse(result.notification_stopped_cleanly)
        self.client.stop_notify.assert_not_awaited()
        self.client.disconnect.assert_awaited_once()

    async def test_subscription_wait_is_bounded(self):
        await self.transport.async_connect()
        async def never_subscribe(*_args):
            await asyncio.Event().wait()
        self.client.start_notify.side_effect = never_subscribe
        with patch.dict(
            self.probe.Fora6BluetoothTransport.async_subscribe.__globals__,
            NOTIFY_TIMEOUT=0.005,
        ):
            await self.failure(self.transport.async_subscribe(), "subscription_failed")
        await self.transport.async_close()

    async def test_successful_exchange_uses_response_true_and_valid_frame(self):
        await self.connected()
        response = await self.transport.async_exchange(self.protocol(WAKE_REQUEST))
        self.assertEqual(response.data, WAKE_RESPONSE)
        self.client.write_gatt_char.assert_awaited_once_with(
            self.characteristic, WAKE_REQUEST, response=True
        )
        await self.transport.async_close()

    async def test_write_failure_has_no_application_retry(self):
        await self.connected()
        self.client.write_gatt_char.side_effect = RuntimeError(self.address)
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "write_failed")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_session_state")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        await self.transport.async_close()

    async def test_write_wait_is_bounded(self):
        await self.connected()
        async def never_write(*_args, **_kwargs):
            await asyncio.Event().wait()
        self.client.write_gatt_char.side_effect = never_write
        with patch.dict(
            self.probe.Fora6BluetoothTransport.async_exchange.__globals__,
            WRITE_TIMEOUT=0.005,
        ):
            await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "write_failed")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        await self.transport.async_close()

    async def test_response_timeout_has_no_application_retry(self):
        await self.connected()
        self.responses[WAKE_REQUEST] = None
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "response_timeout")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_session_state")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        await self.transport.async_close()

    async def test_invalid_length_checksum_marker_and_echo_fail_closed(self):
        wrong_marker_head = WAKE_RESPONSE[:6] + b"\xA3"
        wrong_marker = wrong_marker_head + bytes((sum(wrong_marker_head) & 0xFF,))
        for bad in (
            WAKE_RESPONSE[:-1],
            WAKE_RESPONSE[:-1] + b"\x00",
            wrong_marker,
            PROJECT_RESPONSE,
        ):
            with self.subTest(kind=len(bad)):
                self.transport = self.probe.Fora6BluetoothTransport(
                    self.hass, self.address, response_timeout=0.01
                )
                await self.connected()
                self.responses[WAKE_REQUEST] = bad
                await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_response")
                self.assertIsNone(self.transport._pending_request)
                self.assertIsNone(self.transport._pending_response)
                await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_session_state")
                await self.transport.async_close()
        self.assertEqual(self.client.write_gatt_char.await_count, 4)

    async def test_late_notification_cannot_satisfy_next_exchange(self):
        await self.connected()
        self.responses[WAKE_REQUEST] = None
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "response_timeout")
        self.callback(self.characteristic, bytearray(WAKE_RESPONSE))
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_session_state")
        self.client.write_gatt_char.assert_awaited_once()
        await self.transport.async_close()

    async def test_post_write_disconnect_poisons_session(self):
        await self.connected()
        async def disconnect_after_write(characteristic, data, *, response):
            self.callback(characteristic, bytearray(WAKE_RESPONSE))
            self.client.is_connected = False
        self.client.write_gatt_char.side_effect = disconnect_after_write
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "peer_disconnected")
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_session_state")
        self.client.write_gatt_char.assert_awaited_once()
        await self.transport.async_close()

    async def test_invalid_notification_wins_over_later_valid_frame(self):
        await self.connected()
        async def invalid_then_valid(characteristic, data, *, response):
            self.callback(characteristic, bytearray(b"invalid"))
            self.callback(characteristic, bytearray(WAKE_RESPONSE))
        self.client.write_gatt_char.side_effect = invalid_then_valid
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_response")
        await self.transport.async_close()

    async def test_unsolicited_notification_is_ignored(self):
        await self.connected()
        self.callback(self.characteristic, bytearray(b"synthetic-private-payload"))
        self.assertIsNone(self.transport._pending_response)
        response = await self.transport.async_exchange(self.protocol(WAKE_REQUEST))
        self.assertEqual(response.data, WAKE_RESPONSE)
        await self.transport.async_close()

    async def test_invalid_request_role_is_rejected_without_write(self):
        await self.connected()
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_RESPONSE)), "invalid_request")
        self.client.write_gatt_char.assert_not_awaited()
        response = await self.transport.async_exchange(self.protocol(WAKE_REQUEST))
        self.assertEqual(response.data, WAKE_RESPONSE)
        await self.transport.async_close()

    async def test_exchange_requires_subscribed_connected_session(self):
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "peer_disconnected")
        await self.transport.async_connect()
        await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_session_state")
        await self.transport.async_subscribe()
        self.assertEqual(
            (await self.transport.async_exchange(self.protocol(WAKE_REQUEST))).data,
            WAKE_RESPONSE,
        )
        await self.transport.async_close()

    async def test_privacy_of_errors_and_logs(self):
        await self.connected()
        private_payload = b"synthetic-sensitive-record"
        self.responses[WAKE_REQUEST] = private_payload
        with patch.object(logging.Logger, "_log") as logs:
            await self.failure(self.transport.async_exchange(self.protocol(WAKE_REQUEST)), "invalid_response")
        self.assertNotIn(self.address, str(logs.call_args_list))
        self.assertNotIn(private_payload.decode(), str(logs.call_args_list))
        await self.transport.async_close()

    async def test_clean_stop_and_disconnect(self):
        await self.connected()
        result = await self.transport.async_close()
        self.assertEqual(result.errors, ())
        self.assertTrue(result.notification_stopped_cleanly)
        self.assertTrue(result.disconnected_cleanly)
        self.assertEqual(self.events, ["subscribe", "unsubscribe", "disconnect"])
        self.assertEqual(await self.transport.async_close(), result)
        self.client.stop_notify.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()

    async def test_stop_failure_does_not_skip_disconnect(self):
        await self.connected()
        self.client.stop_notify.side_effect = RuntimeError(self.address)
        result = await self.transport.async_close()
        self.assertEqual(result.errors, ("notification_stop_failed",))
        self.client.disconnect.assert_awaited_once()
        self.assertNotIn(self.address, str(result))

    async def test_disconnect_failure_is_sanitized(self):
        await self.connected()
        self.client.disconnect.side_effect = RuntimeError(self.address)
        result = await self.transport.async_close()
        self.assertEqual(result.errors, ("disconnect_failed",))
        self.assertNotIn(self.address, str(result))

    async def test_cleanup_waits_are_bounded(self):
        await self.connected()
        async def never_finish(*_args):
            await asyncio.Event().wait()
        self.client.stop_notify.side_effect = never_finish
        self.client.disconnect.side_effect = never_finish
        with patch.dict(
            self.probe.Fora6BluetoothTransport._async_close_impl.__globals__,
            NOTIFY_TIMEOUT=0.005,
            DISCONNECT_TIMEOUT=0.005,
        ):
            result = await self.transport.async_close()
        self.assertEqual(result.errors, ("notification_stop_failed", "disconnect_failed"))

    async def test_cleanup_after_exchange_failure(self):
        await self.connected()
        self.responses[WAKE_REQUEST] = None
        try:
            await self.transport.async_exchange(self.protocol(WAKE_REQUEST))
        except self.error_type:
            pass
        result = await self.transport.async_close()
        self.assertEqual(result.errors, ())
        self.client.stop_notify.assert_awaited_once()
        self.client.disconnect.assert_awaited_once()

    async def test_context_manager_cleans_up_on_cancellation(self):
        self.responses[WAKE_REQUEST] = None
        async def session():
            async with self.transport:
                await self.transport.async_exchange(self.protocol(WAKE_REQUEST))
        task = asyncio.create_task(session())
        for _ in range(50):
            if self.client.write_gatt_char.await_count:
                break
            await asyncio.sleep(0)
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.stop_notify.assert_awaited_once()
        self.client.disconnect.assert_awaited_once()

    async def test_context_manager_cleans_up_when_subscription_fails(self):
        self.client.start_notify.side_effect = RuntimeError(self.address)
        await self.failure(self.transport.__aenter__(), "subscription_failed")
        self.client.stop_notify.assert_not_awaited()
        self.client.disconnect.assert_awaited_once()

    async def test_context_manager_cleans_up_on_unexpected_exception(self):
        with self.assertRaisesRegex(RuntimeError, "synthetic internal failure"):
            async with self.transport:
                raise RuntimeError("synthetic internal failure")
        self.client.stop_notify.assert_awaited_once()
        self.client.disconnect.assert_awaited_once()

    async def test_cancellation_during_close_still_disconnects(self):
        await self.connected()
        stop_started = asyncio.Event()
        release_stop = asyncio.Event()
        async def slow_stop(*_args):
            stop_started.set()
            await release_stop.wait()
        self.client.stop_notify.side_effect = slow_stop
        closer = asyncio.create_task(self.transport.async_close())
        await stop_started.wait()
        closer.cancel()
        release_stop.set()
        with self.assertRaises(asyncio.CancelledError):
            await closer
        self.client.stop_notify.assert_awaited_once()
        self.client.disconnect.assert_awaited_once()

    async def test_overlapping_exchanges_are_serialized(self):
        await self.connected()
        first_started = asyncio.Event()
        release_first = asyncio.Event()
        async def slow_write(characteristic, data, *, response):
            if data == WAKE_REQUEST:
                first_started.set()
                await release_first.wait()
            self.callback(characteristic, bytearray(self.responses[data]))
        self.client.write_gatt_char.side_effect = slow_write
        first = asyncio.create_task(self.transport.async_exchange(self.protocol(WAKE_REQUEST)))
        await first_started.wait()
        second = asyncio.create_task(self.transport.async_exchange(self.protocol(PROJECT_REQUEST)))
        await asyncio.sleep(0)
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        release_first.set()
        results = await asyncio.gather(first, second)
        self.assertEqual([r.command_id for r in results], [0x22, 0x24])
        self.assertEqual(self.client.write_gatt_char.await_count, 2)
        await self.transport.async_close()

    def test_no_local_adapter_selection_or_command_policy(self):
        source = (INTEGRATION / "bluetooth.py").read_text()
        self.assertNotIn("hci0", source)
        self.assertNotIn("scanner_by_source", source)
        self.assertNotIn("clear_address_from_match_history", source)
        for command in ("0x22", "0x24", "0x2B", "0x25", "0x26", "0x2F", "0x33"):
            self.assertNotIn(command, source)

    def test_protocol_and_models_are_ha_bleak_independent(self):
        for name in ("protocol.py", "models.py"):
            tree = ast.parse((INTEGRATION / name).read_text())
            imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
            imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
            for imported in imports:
                self.assertFalse(imported.startswith(("homeassistant", "bleak", "esphome", "bluetooth")))


if __name__ == "__main__":
    unittest.main()
