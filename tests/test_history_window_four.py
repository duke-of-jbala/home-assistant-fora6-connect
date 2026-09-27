"""Synthetic tests for Stage 7E's fixed four-slot action."""

import asyncio
import importlib.util
import json
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from fixtures_td4183 import SYNTHETIC_CASES, build_synthetic_pair
from test_history_probe import ADDRESS, frame

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"


def _load_probe():
    name = "_fora6_four_slot_test"
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
        name: package, f"{name}.const": const, "homeassistant": homeassistant,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core, "bleak_retry_connector": connector,
    }
    loaded = {}
    for short in ("protocol", "models", "bluetooth", "history_window_four"):
        spec = importlib.util.spec_from_file_location(f"{name}.{short}", INTEGRATION / f"{short}.py")
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        modules[spec.name] = module
        loaded[short] = (spec, module)
    with patch.dict(sys.modules, modules):
        for spec, module in loaded.values():
            spec.loader.exec_module(module)
    return loaded["protocol"][1], loaded["history_window_four"][1], bluetooth, connector, const


class FourSlotProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.protocol, self.probe, self.bluetooth, self.connector, self.const = _load_probe()
        self.hass = object()
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.characteristic = types.SimpleNamespace(
            uuid=self.const.CHARACTERISTIC_UUID, properties=("write", "notify")
        )
        self.callback = None
        cases = {case.name: case for case in SYNTHETIC_CASES}
        self.zero = cases["uric_general"]
        self.one = cases["hct_qc_invalid"]
        self.two = cases["ketone_general"]
        self.three = cases["uric_qc"]
        self.repeat_three = self.three
        self.expected = [
            self.protocol.build_wake_request().data,
            self.protocol.build_project_query_request().data,
            self.protocol.build_record_slot_count_request().data,
            self.protocol.build_fourth_record_part_one_request().data,
            self.protocol.build_fourth_record_part_two_request().data,
            self.protocol.build_first_record_part_one_request().data,
            self.protocol.build_first_record_part_two_request().data,
            self.protocol.build_second_record_part_one_request().data,
            self.protocol.build_second_record_part_two_request().data,
            self.protocol.build_third_record_part_one_request().data,
            self.protocol.build_third_record_part_two_request().data,
            self.protocol.build_fourth_record_part_one_request().data,
            self.protocol.build_fourth_record_part_two_request().data,
        ]
        self.responses = []
        self.fail_write_at = None
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[types.SimpleNamespace(uuid=self.const.SERVICE_UUID, characteristics=[self.characteristic])],
            start_notify=AsyncMock(side_effect=self._start),
            write_gatt_char=AsyncMock(side_effect=self._write),
            stop_notify=AsyncMock(),
            disconnect=AsyncMock(),
            read_gatt_char=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client
        self.probe.RESPONSE_TIMEOUT = 0.005

    def prepare(self, count=4):
        pairs = [build_synthetic_pair(case, self.protocol) for case in
                 (self.three, self.zero, self.one, self.two, self.repeat_three)]
        self.responses = [
            frame(0x22, b"\x00\x00\xFF\xFF"),
            frame(0x24, b"\x83\x41\x00\x00"),
            frame(0x2B, count.to_bytes(2, "little") + b"\x03\x00"),
            *(part.data for pair in pairs for part in pair),
        ]

    async def _start(self, characteristic, callback):
        self.callback = callback

    async def _write(self, characteristic, data, *, response):
        index = self.client.write_gatt_char.await_count - 1
        self.assertEqual(data, self.expected[index])
        self.assertIs(response, True)
        if index == self.fail_write_at:
            raise RuntimeError(ADDRESS)
        reply = self.responses[index]
        if reply is not None:
            self.callback(characteristic, bytearray(reply))

    async def run_probe(self):
        if not self.responses:
            self.prepare()
        return await self.probe.async_probe_history_window_four(self.hass, ADDRESS)

    def assert_private(self, result):
        public = json.dumps(result)
        self.assertNotIn(ADDRESS, public)
        self.assertNotIn(str(self.zero.raw_value), public)
        self.assertNotIn(str(self.zero.year), public)
        for raw in self.responses:
            if raw is not None:
                self.assertNotIn(raw.hex(), public.lower())
        for key in result:
            self.assertNotIn(key, ("raw_value", "scaled_value", "unit", "meter_local_time", "serial", "address", "hash", "digest", "raw_frame", "payload"))
        self.client.read_gatt_char.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        if self.connector.establish_connection.await_count:
            self.assertIs(self.connector.establish_connection.await_args.kwargs["pair"], False)
        for call in self.client.write_gatt_char.call_args_list:
            self.assertIs(call.kwargs["response"], True)

    def assert_cleanup(self):
        self.client.stop_notify.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()

    async def test_success_exact_bounded_sequence_and_grouping(self):
        result = await self.run_probe()
        self.assertEqual([c.args[1] for c in self.client.write_gatt_char.call_args_list], self.expected)
        self.assertEqual(self.client.write_gatt_char.await_count, 13)
        self.assertEqual(result["requested_indexes"], [3, 0, 1, 2, 3])
        self.assertTrue(result["identity_confirmed"])
        self.assertTrue(result["traversal_performed"])
        self.assertTrue(result["group_0_pairing_structurally_valid"])
        self.assertTrue(result["group_1_pairing_structurally_valid"])
        self.assertTrue(result["repeated_index_3_pair_equal"])
        self.assertTrue(result["repeated_index_3_semantics_equal"])
        for name in ("index_0", "index_1", "index_2", "index_3_first", "index_3_second"):
            self.assertTrue(result[f"{name}_part_1_valid"])
            self.assertTrue(result[f"{name}_part_2_valid"])
            self.assertTrue(result[f"{name}_pair_complete"])
        self.assert_cleanup()
        self.assert_private(result)

    async def test_count_mismatch_stops_before_record_reads(self):
        for count in (0, 1, 2, 3, 5):
            with self.subTest(count=count):
                self.prepare(count)
                self.client.write_gatt_char.reset_mock()
                self.client.stop_notify.reset_mock()
                self.client.disconnect.reset_mock()
                result = await self.run_probe()
                self.assertEqual(self.client.write_gatt_char.await_count, 3)
                self.assertFalse(result["traversal_gate_passed"])
                self.assertFalse(result["traversal_performed"])
                self.assertEqual(result["requested_indexes"], [])
                self.assert_cleanup()
                self.assert_private(result)

    async def test_project_mismatch_stops_before_metadata(self):
        self.prepare()
        self.responses[1] = frame(0x24, b"\x84\x41\x00\x00")
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "unexpected_project_id")
        self.assertEqual(self.client.write_gatt_char.await_count, 2)
        self.assert_cleanup()

    async def test_invalid_metadata_stops(self):
        self.prepare()
        self.responses[2] = self.responses[2][:-1] + b"\x00"
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "metadata")
        self.assertEqual(self.client.write_gatt_char.await_count, 3)
        self.assert_cleanup()

    async def test_each_pair_failure_stops_immediately(self):
        for index in range(3, 13):
            with self.subTest(write=index):
                self.prepare()
                self.client.write_gatt_char.reset_mock()
                self.client.stop_notify.reset_mock()
                self.client.disconnect.reset_mock()
                self.responses[index] = None
                result = await self.run_probe()
                self.assertEqual(self.client.write_gatt_char.await_count, index + 1)
                self.assertEqual(result["error_code"], "response_timeout")
                self.assertFalse(result["traversal_performed"])
                self.assert_cleanup()
                self.assert_private(result)

    async def test_repeat_byte_difference(self):
        self.prepare()
        changed = bytearray(self.responses[11]); changed[2] ^= 1; changed[-1] = sum(changed[:-1]) & 0xFF
        self.responses[11] = bytes(changed)
        result = await self.run_probe()
        self.assertFalse(result["repeated_index_3_part_1_equal"])
        self.assertTrue(result["repeated_index_3_part_2_equal"])
        self.assertFalse(result["repeated_index_3_pair_equal"])
        self.assertTrue(result["repeated_index_3_semantics_equal"])
        self.assert_private(result)

    async def test_repeat_semantics_difference(self):
        self.repeat_three = {case.name: case for case in SYNTHETIC_CASES}["ketone_general"]
        result = await self.run_probe()
        self.assertFalse(result["repeated_index_3_analyte_equal"])
        self.assertFalse(result["repeated_index_3_category_equal"])
        self.assertFalse(result["repeated_index_3_semantics_equal"])
        self.assert_private(result)

    async def test_repeat_second_part_and_validity_difference(self):
        self.repeat_three = {case.name: case for case in SYNTHETIC_CASES}["uric_invalid"]
        result = await self.run_probe()
        self.assertFalse(result["repeated_index_3_part_2_equal"])
        self.assertFalse(result["repeated_index_3_validity_equal"])
        self.assertFalse(result["repeated_index_3_pair_equal"])
        self.assertFalse(result["repeated_index_3_semantics_equal"])
        self.assert_private(result)

    async def test_no_connectable_device_stops_without_write(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        result = await self.run_probe()
        self.assertFalse(result["device_found"])
        self.client.write_gatt_char.assert_not_awaited()
        self.assert_private(result)

    async def test_timestamp_relationships_are_equality_only(self):
        self.one = self.zero
        self.three = self.two
        self.repeat_three = self.three
        result = await self.run_probe()
        self.assertTrue(result["index_0_and_1_time_equal"])
        self.assertTrue(result["index_2_and_3_time_equal"])
        self.assert_private(result)

    async def test_failure_has_privacy_safe_error_and_no_retry(self):
        self.prepare()
        self.fail_write_at = 5
        with patch.object(logging, "exception") as log_exception:
            result = await self.run_probe()
        self.assertEqual(result["error_stage"], "index_0_part_1")
        self.assertEqual(result["error_code"], "write_failed")
        self.assertEqual(self.client.write_gatt_char.await_count, 6)
        log_exception.assert_not_called()
        self.assert_private(result)

    async def test_action_registration(self):
        from test_gatt_probe import _load_probe, _load_setup, _registered_action
        integration, _, _, _ = _load_setup(_load_probe()[0])
        hass = types.SimpleNamespace(services=types.SimpleNamespace(async_register=Mock()), data={})
        await integration.async_setup(hass, {})
        registration = _registered_action(hass.services, "probe_history_window_four")
        self.assertEqual(registration.kwargs["supports_response"], "response_only")
        result = await registration.args[2](types.SimpleNamespace(data={"address": ADDRESS}))
        self.assertEqual(result, {"traversal_performed": True})
        integration.async_probe_history_window_four.assert_awaited_once_with(hass, ADDRESS)

    async def test_cleanup_on_cancellation(self):
        self.prepare()
        self.responses[3] = None
        task = asyncio.create_task(self.run_probe())
        await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.disconnect.assert_awaited_once()

    async def test_pure_builders_and_no_forbidden_commands(self):
        for index, part in ((2, 1), (2, 2), (3, 1), (3, 2)):
            builder = getattr(self.protocol, f"build_{'third' if index == 2 else 'fourth'}_record_part_{'one' if part == 1 else 'two'}_request")
            data = builder().data
            self.assertEqual(int.from_bytes(data[2:4], "little"), index)
            self.assertEqual(data[5], 1)
            self.assertIn(data[1], (0x25, 0x26))
        self.assertNotIn("homeassistant", (INTEGRATION / "protocol.py").read_text().lower())
        self.assertNotIn("bleak", (INTEGRATION / "protocol.py").read_text().lower())
        self.assertFalse({0x2F, 0x33, 0x50} & {data[1] for data in self.expected})

    async def test_no_product_state_or_persistence_path(self):
        source = (INTEGRATION / "history_window_four.py").read_text()
        for forbidden in (
            "0x2F", "0x33", "0x50", "sensor_state", "async_write_ha_state",
            "coordinator", "async_create_task", "async_store", "config_entries",
        ):
            self.assertNotIn(forbidden, source)
