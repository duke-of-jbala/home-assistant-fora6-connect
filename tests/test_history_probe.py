"""Synthetic Stage 7B two-slot probe tests; no captured record is included."""

import asyncio
import importlib.util
import json
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import yaml

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
ADDRESS = "SYNTHETIC-PRIVATE-LOCATOR"
EXPECTED_REQUESTS = (
    bytes.fromhex("51 22 00 00 00 00 A3 16"),
    bytes.fromhex("51 24 00 00 00 00 A3 18"),
    bytes.fromhex("51 2B 01 00 00 00 A3 20"),
    bytes.fromhex("51 25 01 00 00 01 A3 1B"),
    bytes.fromhex("51 26 01 00 00 01 A3 1C"),
    bytes.fromhex("51 25 00 00 00 01 A3 1A"),
    bytes.fromhex("51 26 00 00 00 01 A3 1B"),
    bytes.fromhex("51 25 01 00 00 01 A3 1B"),
    bytes.fromhex("51 26 01 00 00 01 A3 1C"),
)


def frame(command, payload):
    """Construct a checksummed artificial response."""
    head = bytes((0x51, command)) + payload + b"\xA5"
    return head + bytes((sum(head) & 0xFF,))


def _load_history():
    name = "_fora6_history_test"
    package = types.ModuleType(name)
    package.__path__ = [str(INTEGRATION)]
    const = types.ModuleType(f"{name}.const")
    exec((INTEGRATION / "const.py").read_text(), const.__dict__)
    homeassistant = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    connector = types.ModuleType("bleak_retry_connector")
    connector.BleakClientWithServiceCache = type("FakeClient", (), {})
    connector.BleakOutOfConnectionSlotsError = type("NoSlots", (Exception,), {})
    connector.establish_connection = AsyncMock()
    modules = {
        name: package,
        f"{name}.const": const,
        "homeassistant": homeassistant,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
        "bleak_retry_connector": connector,
    }
    loaded = []
    for short in ("protocol", "bluetooth", "history_probe"):
        spec = importlib.util.spec_from_file_location(
            f"{name}.{short}", INTEGRATION / f"{short}.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        modules[spec.name] = module
        loaded.append((spec, module))
    with patch.dict(sys.modules, modules):
        for spec, module in loaded:
            spec.loader.exec_module(module)
    return loaded[0][1], loaded[2][1], bluetooth, connector, const


class HistoryProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.protocol, self.probe, self.bluetooth, self.connector, self.const = _load_history()
        self.hass = object()
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.characteristic = types.SimpleNamespace(
            uuid=self.const.CHARACTERISTIC_UUID, properties=("write", "notify")
        )
        self.events = []
        self.callback = None
        self.responses = [
            frame(0x22, b"\x00\x00\xFF\xFF"),
            frame(0x24, b"\x83\x41\x00\x00"),
            frame(0x2B, b"\x02\x00\x01\x00"),
            frame(0x25, b"\x41\x4A\x2A\x49"),
            frame(0x26, b"\xD2\x04\x11\xE0"),
            frame(0x25, b"\x42\x4A\x2B\x09"),
            frame(0x26, b"\xB0\x04\x12\x20"),
            frame(0x25, b"\x41\x4A\x2A\x49"),
            frame(0x26, b"\xD2\x04\x11\xE0"),
        ]
        self.fail_write_at = None
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[types.SimpleNamespace(
                uuid=self.const.SERVICE_UUID, characteristics=[self.characteristic]
            )],
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
        index = self.client.write_gatt_char.await_count - 1
        self.events.append((data[1], int.from_bytes(data[2:4], "little")))
        self.assertIs(response, True)
        self.assertEqual(data, EXPECTED_REQUESTS[index])
        if index == self.fail_write_at:
            raise RuntimeError(ADDRESS)
        reply = self.responses[index]
        if reply is not None:
            self.callback(characteristic, bytearray(reply))

    async def _stop(self, characteristic):
        self.events.append("unsubscribe")

    async def _disconnect(self):
        self.events.append("disconnect")

    async def run_probe(self):
        return await self.probe.async_probe_history_window(self.hass, ADDRESS)

    def assert_privacy(self, result):
        public = json.dumps(result)
        self.assertNotIn(ADDRESS, public)
        for raw in self.responses:
            if raw is not None:
                self.assertNotIn(raw.hex(), public.lower())
        for key in result:
            self.assertNotIn(key, ("raw_value", "meter_local_time", "serial", "address", "hash", "digest"))
        self.client.read_gatt_char.assert_not_awaited()
        self.client.write_gatt_descriptor.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        for call in self.client.write_gatt_char.call_args_list:
            self.assertIs(call.kwargs["response"], True)
            self.assertEqual(call.args[0].uuid, self.const.CHARACTERISTIC_UUID)
        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, ADDRESS, connectable=True
        )
        if self.connector.establish_connection.await_count:
            self.assertEqual(
                self.connector.establish_connection.await_args.kwargs["pair"], False
            )

    def assert_cleanup(self):
        self.client.stop_notify.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()

    async def test_exact_success_sequence_and_private_result(self):
        result = await self.run_probe()
        self.assertEqual(
            [x.args[1] for x in self.client.write_gatt_char.call_args_list],
            list(EXPECTED_REQUESTS),
        )
        self.assertEqual(self.events[-2:], ["unsubscribe", "disconnect"])
        self.assertEqual(result["requested_indexes"], [1, 0, 1])
        self.assertTrue(result["identity_confirmed"])
        self.assertTrue(result["record_metadata_response_valid"])
        self.assertTrue(result["traversal_gate_passed"])
        self.assertTrue(result["traversal_performed"])
        self.assertTrue(result["repeated_index_1_pair_equal"])
        self.assertEqual(result["error_code"], None)
        self.assertEqual(self.client.write_gatt_char.await_count, 9)
        self.assertNotIn("newest_index", result)
        self.assert_cleanup()
        self.assert_privacy(result)

    async def test_index_one_builders_and_newest_index_parser(self):
        self.assertEqual(self.protocol.build_second_record_part_one_request().data, EXPECTED_REQUESTS[3])
        self.assertEqual(self.protocol.build_second_record_part_two_request().data, EXPECTED_REQUESTS[4])
        metadata = self.protocol.ProtocolFrame(self.responses[2])
        self.assertEqual(self.protocol.parse_record_slot_count(metadata), 2)
        self.assertEqual(self.protocol.parse_record_newest_index(metadata), 1)
        with self.assertRaises(self.protocol.FrameError):
            self.protocol.parse_record_newest_index(self.protocol.ProtocolFrame(self.responses[3]))
        self.assertNotIn("homeassistant", (INTEGRATION / "protocol.py").read_text().lower())
        self.assertNotIn("bleak", (INTEGRATION / "protocol.py").read_text().lower())

    async def test_count_zero_stops_after_one_metadata_query(self):
        await self._count_gate(0)

    async def test_count_one_stops_after_one_metadata_query(self):
        await self._count_gate(1)

    async def test_count_three_stops_after_one_metadata_query(self):
        await self._count_gate(3)

    async def _count_gate(self, count):
        self.responses[2] = frame(0x2B, count.to_bytes(2, "little") + b"\x01\x00")
        result = await self.run_probe()
        self.assertEqual(self.client.write_gatt_char.await_count, 3)
        self.assertEqual(result["expected_raw_slot_count"], 2)
        self.assertFalse(result["raw_slot_count_matches_expected"])
        self.assertFalse(result["traversal_gate_passed"])
        self.assertFalse(result["traversal_performed"])
        self.assertEqual(result["requested_indexes"], [])
        self.assertIsNone(result["error_code"])
        self.assert_cleanup()
        self.assert_privacy(result)

    async def test_invalid_metadata_stops(self):
        self.responses[2] = self.responses[2][:-1] + b"\x00"
        await self._failure("metadata", "invalid_response", 3)

    async def test_wrong_metadata_echo_stops(self):
        self.responses[2] = frame(0x25, b"\x02\x00\x01\x00")
        await self._failure("metadata", "invalid_response", 3)

    async def test_project_mismatch_stops_before_metadata(self):
        self.responses[1] = frame(0x24, b"\x84\x41\x00\x00")
        await self._failure("project", "unexpected_project_id", 2)

    async def test_first_index_one_part_one_failure(self):
        self.responses[3] = None
        await self._failure("index_1_first_part_1", "response_timeout", 4)

    async def test_first_index_one_part_two_failure(self):
        self.responses[4] = None
        await self._failure("index_1_first_part_2", "response_timeout", 5)

    async def test_index_zero_part_one_failure(self):
        self.responses[5] = None
        await self._failure("index_0_part_1", "response_timeout", 6)

    async def test_index_zero_part_two_failure(self):
        self.responses[6] = None
        await self._failure("index_0_part_2", "response_timeout", 7)

    async def test_second_index_one_part_one_failure(self):
        self.responses[7] = None
        await self._failure("index_1_second_part_1", "response_timeout", 8)

    async def test_second_index_one_part_two_failure(self):
        self.responses[8] = None
        await self._failure("index_1_second_part_2", "response_timeout", 9)

    async def _failure(self, stage, code, writes):
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], stage)
        self.assertEqual(result["error_code"], code)
        self.assertEqual(self.client.write_gatt_char.await_count, writes)
        self.assertFalse(result["traversal_performed"])
        self.assert_cleanup()
        self.assert_privacy(result)

    async def test_repeat_first_part_difference_is_boolean_only(self):
        self.responses[7] = frame(0x25, b"\x41\x4A\x2B\x49")
        result = await self.run_probe()
        self.assertFalse(result["repeated_index_1_part_1_equal"])
        self.assertTrue(result["repeated_index_1_part_2_equal"])
        self.assertFalse(result["repeated_index_1_pair_equal"])
        self.assert_privacy(result)

    async def test_repeat_second_part_difference_is_boolean_only(self):
        self.responses[8] = frame(0x26, b"\xD3\x04\x11\xE0")
        result = await self.run_probe()
        self.assertTrue(result["repeated_index_1_part_1_equal"])
        self.assertFalse(result["repeated_index_1_part_2_equal"])
        self.assertFalse(result["repeated_index_1_pair_equal"])
        self.assert_privacy(result)

    async def test_invalid_calendar_frame_stops_before_part_two(self):
        self.responses[3] = frame(0x25, b"\x01\x00\x2A\x49")
        await self._failure("index_1_first_part_1", "invalid_response", 4)

    async def test_invalid_part_two_checksum_stops_before_next_pair(self):
        self.responses[4] = self.responses[4][:-1] + b"\x00"
        await self._failure("index_1_first_part_2", "invalid_response", 5)

    async def test_no_connectable_device_never_writes(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "no_connectable_device")
        self.client.write_gatt_char.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()
        self.client.disconnect.assert_not_awaited()
        self.assert_privacy(result)

    async def test_write_failure_has_no_command_retry_or_private_log(self):
        self.fail_write_at = 3
        with patch.object(logging.Logger, "_log") as logs:
            await self._failure("index_1_first_part_1", "write_failed", 4)
        self.assertNotIn(ADDRESS, str(logs.call_args_list))

    async def test_cleanup_failure_does_not_claim_clean_disconnect(self):
        self.client.stop_notify.side_effect = RuntimeError(ADDRESS)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "notification_stop_failed")
        self.assertFalse(result["notification_stopped_cleanly"])
        self.client.disconnect.assert_awaited_once()
        self.assert_privacy(result)

    async def test_cancellation_cleans_up_without_late_pair(self):
        entered = asyncio.Event()
        async def block_write(characteristic, data, *, response):
            if self.client.write_gatt_char.await_count == 4:
                entered.set()
                await asyncio.Event().wait()
            else:
                await self._write(characteristic, data, response=response)
        self.client.write_gatt_char.side_effect = block_write
        task = asyncio.create_task(self.run_probe())
        await asyncio.wait_for(entered.wait(), 1)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(self.client.write_gatt_char.await_count, 4)
        self.assert_cleanup()


class ActionRegistrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_only_private_address_is_an_action_input(self):
        from test_gatt_probe import _load_probe, _load_setup, _registered_action

        gatt, _, _ = _load_probe()
        integration, _, _, _ = _load_setup(gatt)
        services = Mock()
        hass = types.SimpleNamespace(services=services)
        self.assertTrue(await integration.async_setup(hass, {}))
        action = _registered_action(services, "probe_history_window")
        self.assertEqual(action.kwargs["supports_response"], "response_only")
        result = await action.args[2](types.SimpleNamespace(data={"address": ADDRESS}))
        self.assertEqual(result, {"traversal_performed": True})
        integration.async_probe_history_window.assert_awaited_once_with(hass, ADDRESS)
        definitions = yaml.safe_load((INTEGRATION / "services.yaml").read_text())
        self.assertEqual(set(definitions["probe_history_window"]["fields"]), {"address"})
        self.assertEqual(set(definitions["probe_protocol_identity"]["fields"]), {"address"})
        self.assertEqual(set(definitions["probe_protocol_record"]["fields"]), {"address"})


if __name__ == "__main__":
    unittest.main()
