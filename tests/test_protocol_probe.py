"""Hardware-free Stage 2E identity-probe tests with synthetic private inputs."""

import importlib.util
import json
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
WAKE_REQUEST = bytes.fromhex("51 22 00 00 00 00 A3 16")
WAKE_RESPONSE = bytes.fromhex("51 22 00 00 FF FF A5 16")
PROJECT_REQUEST = bytes.fromhex("51 24 00 00 00 00 A3 18")
PROJECT_RESPONSE = bytes.fromhex("51 24 83 41 04 00 A5 E2")


def _load_probe():
    package = types.ModuleType("_fora6_identity_test")
    package.__path__ = [str(INTEGRATION)]
    const = types.ModuleType("_fora6_identity_test.const")
    exec((INTEGRATION / "const.py").read_text(encoding="utf-8"), const.__dict__)
    gatt = types.ModuleType("_fora6_identity_test.gatt_probe")
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
        "_fora6_identity_test": package,
        "_fora6_identity_test.const": const,
        "_fora6_identity_test.gatt_probe": gatt,
        "homeassistant": homeassistant,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
        "bleak_retry_connector": connector,
    }
    protocol_spec = importlib.util.spec_from_file_location(
        "_fora6_identity_test.protocol", INTEGRATION / "protocol.py"
    )
    assert protocol_spec and protocol_spec.loader
    protocol = importlib.util.module_from_spec(protocol_spec)
    modules[protocol_spec.name] = protocol
    identity_spec = importlib.util.spec_from_file_location(
        "_fora6_identity_test.protocol_probe", INTEGRATION / "protocol_probe.py"
    )
    assert identity_spec and identity_spec.loader
    identity = importlib.util.module_from_spec(identity_spec)
    with patch.dict(sys.modules, modules):
        protocol_spec.loader.exec_module(protocol)
        identity_spec.loader.exec_module(identity)
    return identity, bluetooth, connector


def _service(uuid, *characteristics):
    return types.SimpleNamespace(
        uuid=uuid,
        characteristics=[
            types.SimpleNamespace(uuid=char_uuid, properties=properties)
            for char_uuid, properties in characteristics
        ],
    )


class IdentityProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.probe, self.bluetooth, self.connector = _load_probe()
        self.hass = object()
        self.address = "synthetic-private-address"
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.events = []
        self.characteristic = types.SimpleNamespace(
            uuid=self.probe.CHARACTERISTIC_UUID, properties=("write", "notify")
        )
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[
                _service("00001808-0000-1000-8000-00805f9b34fb"),
                types.SimpleNamespace(
                    uuid=self.probe.SERVICE_UUID,
                    characteristics=[self.characteristic],
                ),
            ],
            start_notify=AsyncMock(side_effect=self._start),
            write_gatt_char=AsyncMock(side_effect=self._write),
            stop_notify=AsyncMock(side_effect=self._stop),
            disconnect=AsyncMock(side_effect=self._disconnect),
            read_gatt_char=AsyncMock(),
            write_gatt_descriptor=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client
        self.probe.RESPONSE_TIMEOUT = 0.005

    async def _start(self, characteristic, callback):
        self.events.append("subscribe")
        self.callback = callback

    async def _write(self, characteristic, data, *, response):
        self.events.append("wake" if data == WAKE_REQUEST else "project")
        assert response is True
        self.callback(
            characteristic,
            bytearray(WAKE_RESPONSE if data == WAKE_REQUEST else PROJECT_RESPONSE),
        )

    async def _stop(self, characteristic):
        self.events.append("unsubscribe")

    async def _disconnect(self):
        self.events.append("disconnect")

    async def run_probe(self):
        return await self.probe.async_probe_protocol_identity(self.hass, self.address)

    def assert_private_boundary(self, result):
        public = json.dumps(result)
        self.assertNotIn(self.address, public)
        for raw in (WAKE_REQUEST, WAKE_RESPONSE, PROJECT_REQUEST, PROJECT_RESPONSE):
            self.assertNotIn(raw.hex(), public.lower())
            self.assertNotIn(raw.hex(" "), public.lower())
        self.client.read_gatt_char.assert_not_awaited()
        self.client.write_gatt_descriptor.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        for call in self.client.start_notify.call_args_list:
            self.assertEqual(call.args[0].uuid, self.probe.CHARACTERISTIC_UUID)
        for call in self.client.write_gatt_char.call_args_list:
            self.assertIn(call.args[1], (WAKE_REQUEST, PROJECT_REQUEST))
            self.assertIs(call.kwargs["response"], True)
            self.assertEqual(call.args[0].uuid, self.probe.CHARACTERISTIC_UUID)

    def assert_cleanup(self, *, subscribed=True):
        self.client.disconnect.assert_awaited_once()
        if subscribed:
            self.client.stop_notify.assert_awaited_once_with(self.characteristic)
        else:
            self.client.stop_notify.assert_not_awaited()

    async def test_full_sequence_writes_once_each_and_cleans_up(self):
        result = await self.run_probe()
        self.assertEqual(
            self.events, ["subscribe", "wake", "project", "unsubscribe", "disconnect"]
        )
        self.assertEqual(result["project_id"], 0x4183)
        self.assertEqual(result["expected_project_id"], 0x4183)
        self.assertTrue(result["identity_confirmed"])
        for key in (
            "connection_successful",
            "custom_characteristic_found",
            "notification_subscription_successful",
            "wake_write_successful",
            "wake_response_valid",
            "project_query_write_successful",
            "project_response_valid",
            "project_id_matches",
            "notification_stopped_cleanly",
            "disconnected_cleanly",
        ):
            self.assertTrue(result[key], key)
        self.assertIsNone(result["error_code"])
        self.assertEqual(self.client.write_gatt_char.await_count, 2)
        self.assertEqual(
            [call.args[1] for call in self.client.write_gatt_char.call_args_list],
            [WAKE_REQUEST, PROJECT_REQUEST],
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
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_no_connectable_device_never_connects(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "no_connectable_device")
        self.connector.establish_connection.assert_not_awaited()
        self.client.write_gatt_char.assert_not_awaited()
        self.client.disconnect.assert_not_awaited()
        self.assert_private_boundary(result)

    async def test_connection_failure_is_sanitized(self):
        self.connector.establish_connection.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "connection_failed")
        self.client.write_gatt_char.assert_not_awaited()
        self.client.disconnect.assert_not_awaited()
        self.assert_private_boundary(result)

    async def test_connection_slot_failure_is_sanitized(self):
        self.connector.establish_connection.side_effect = (
            self.connector.BleakOutOfConnectionSlotsError()
        )
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "no_connection_slot")
        self.client.write_gatt_char.assert_not_awaited()
        self.client.disconnect.assert_not_awaited()
        self.assert_private_boundary(result)

    async def test_integration_emits_no_private_logs(self):
        records = []

        class Capture(logging.Handler):
            def emit(self, record):
                records.append(record.getMessage())

        handler = Capture()
        logger = logging.getLogger()
        logger.addHandler(handler)
        try:
            result = await self.run_probe()
        finally:
            logger.removeHandler(handler)
        self.assertTrue(result["identity_confirmed"])
        log_text = "\n".join(records)
        self.assertNotIn(self.address, log_text)
        for raw in (WAKE_RESPONSE, PROJECT_RESPONSE):
            self.assertNotIn(raw.hex(), log_text.lower())
            self.assertNotIn(raw.hex(" "), log_text.lower())

    async def test_missing_custom_characteristic_disconnects(self):
        self.client.services[1].characteristics = []
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "custom_characteristic_missing")
        self.client.start_notify.assert_not_awaited()
        self.client.write_gatt_char.assert_not_awaited()
        self.assert_cleanup(subscribed=False)
        self.assert_private_boundary(result)

    async def test_custom_characteristic_requires_write_and_notify(self):
        self.characteristic.properties = ("write-without-response", "notify")
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "custom_properties_missing")
        self.client.start_notify.assert_not_awaited()
        self.client.write_gatt_char.assert_not_awaited()
        self.assert_cleanup(subscribed=False)
        self.assert_private_boundary(result)

    async def test_start_notify_failure_disconnects_without_write(self):
        self.client.start_notify.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "subscription_failed")
        self.client.write_gatt_char.assert_not_awaited()
        self.assert_cleanup(subscribed=False)
        self.assert_private_boundary(result)

    async def test_wake_write_failure_stops_and_disconnects(self):
        self.client.write_gatt_char.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "wake")
        self.assertEqual(result["error_code"], "write_failed")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_wake_timeout_sends_no_project_query(self):
        self.client.write_gatt_char.side_effect = None
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "wake")
        self.assertEqual(result["error_code"], "response_timeout")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_invalid_wake_checksum_fails_closed(self):
        async def invalid(*_args, **_kwargs):
            self.callback(self.characteristic, bytearray(WAKE_RESPONSE[:-1] + b"\x00"))

        self.client.write_gatt_char.side_effect = invalid
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "wake")
        self.assertEqual(result["error_code"], "invalid_response")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_wrong_wake_command_fails_closed(self):
        async def wrong(*_args, **_kwargs):
            self.callback(self.characteristic, bytearray(PROJECT_RESPONSE))

        self.client.write_gatt_char.side_effect = wrong
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "wake")
        self.assertEqual(result["error_code"], "invalid_response")
        self.assertEqual(self.client.write_gatt_char.await_count, 1)
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_project_write_failure_after_valid_wake(self):
        async def fail_project(characteristic, data, *, response):
            if data == WAKE_REQUEST:
                self.callback(characteristic, bytearray(WAKE_RESPONSE))
            else:
                raise RuntimeError(self.address)

        self.client.write_gatt_char.side_effect = fail_project
        result = await self.run_probe()
        self.assertTrue(result["wake_response_valid"])
        self.assertEqual(result["error_stage"], "project")
        self.assertEqual(result["error_code"], "write_failed")
        self.assertEqual(self.client.write_gatt_char.await_count, 2)
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_project_timeout_after_valid_wake(self):
        async def no_project_response(characteristic, data, *, response):
            if data == WAKE_REQUEST:
                self.callback(characteristic, bytearray(WAKE_RESPONSE))

        self.client.write_gatt_char.side_effect = no_project_response
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "project")
        self.assertEqual(result["error_code"], "response_timeout")
        self.assertEqual(self.client.write_gatt_char.await_count, 2)
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_invalid_project_checksum_fails_closed(self):
        async def invalid_project(characteristic, data, *, response):
            response_data = (
                WAKE_RESPONSE
                if data == WAKE_REQUEST
                else PROJECT_RESPONSE[:-1] + b"\x00"
            )
            self.callback(characteristic, bytearray(response_data))

        self.client.write_gatt_char.side_effect = invalid_project
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "project")
        self.assertEqual(result["error_code"], "invalid_response")
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_wrong_project_command_fails_closed(self):
        async def wrong_project(characteristic, data, *, response):
            self.callback(characteristic, bytearray(WAKE_RESPONSE))

        async def wake_then_wrong(characteristic, data, *, response):
            if data == WAKE_REQUEST:
                await self._write(characteristic, data, response=response)
            else:
                await wrong_project(characteristic, data, response=response)

        self.client.write_gatt_char.side_effect = wake_then_wrong
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "project")
        self.assertEqual(result["error_code"], "invalid_response")
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_other_project_id_fails_without_fallback(self):
        response_start = bytes.fromhex("51 24 84 41 04 00 A5")
        other_response = response_start + bytes((sum(response_start) & 0xFF,))

        async def other_project(characteristic, data, *, response):
            self.callback(
                characteristic,
                bytearray(WAKE_RESPONSE if data == WAKE_REQUEST else other_response),
            )

        self.client.write_gatt_char.side_effect = other_project
        result = await self.run_probe()
        self.assertEqual(result["project_id"], 0x4184)
        self.assertTrue(result["project_response_valid"])
        self.assertFalse(result["project_id_matches"])
        self.assertEqual(result["error_code"], "unexpected_project_id")
        self.assertEqual(self.client.write_gatt_char.await_count, 2)
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_malformed_response_never_exposes_payload_or_address(self):
        private_payload = bytearray(b"synthetic-sensitive-payload")

        async def malformed(characteristic, data, *, response):
            self.callback(characteristic, private_payload)

        self.client.write_gatt_char.side_effect = malformed
        with patch.object(logging.Logger, "_log") as logs:
            result = await self.run_probe()
        public = json.dumps(result)
        self.assertEqual(result["error_code"], "invalid_response")
        self.assertNotIn(self.address, public)
        self.assertNotIn("synthetic-sensitive-payload", public)
        self.assertNotIn(self.address, str(logs.call_args_list))
        self.assertNotIn("synthetic-sensitive-payload", str(logs.call_args_list))
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_cleanup_failures_are_sanitized(self):
        self.client.stop_notify.side_effect = RuntimeError(self.address)
        self.client.disconnect.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertEqual(
            result["cleanup_errors"],
            ["notification_stop_failed", "disconnect_failed"],
        )
        self.assertFalse(result["identity_confirmed"])
        self.assertNotIn(self.address, json.dumps(result))
        self.assert_cleanup()
        self.assert_private_boundary(result)


if __name__ == "__main__":
    unittest.main()
