"""Synthetic, privacy-safe tests for the fixed Stage 7C semantic action."""

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

from fixtures_td4183 import SYNTHETIC_CASES, SyntheticRecordCase, build_synthetic_pair
from test_history_probe import ADDRESS, EXPECTED_REQUESTS, frame

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"


def _load_semantics():
    name = "_fora6_semantics_test"
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
    loaded = {}
    for short in ("protocol", "models", "bluetooth", "history_semantics_probe"):
        spec = importlib.util.spec_from_file_location(
            f"{name}.{short}", INTEGRATION / f"{short}.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        modules[spec.name] = module
        loaded[short] = (spec, module)
    with patch.dict(sys.modules, modules):
        for spec, module in loaded.values():
            spec.loader.exec_module(module)
    return (
        loaded["protocol"][1], loaded["history_semantics_probe"][1],
        bluetooth, connector, const,
    )


class SemanticProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.protocol, self.probe, self.bluetooth, self.connector, self.const = _load_semantics()
        self.hass = object()
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.characteristic = types.SimpleNamespace(
            uuid=self.const.CHARACTERISTIC_UUID, properties=("write", "notify")
        )
        self.callback = None
        cases = {case.name: case for case in SYNTHETIC_CASES}
        self.first_one = cases["hct_qc_invalid"]
        self.zero = cases["uric_general"]
        self.second_one = cases["hct_qc_invalid"]
        self.responses = []
        self.fail_write_at = None
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[types.SimpleNamespace(
                uuid=self.const.SERVICE_UUID, characteristics=[self.characteristic]
            )],
            start_notify=AsyncMock(side_effect=self._start),
            write_gatt_char=AsyncMock(side_effect=self._write),
            stop_notify=AsyncMock(),
            disconnect=AsyncMock(),
            read_gatt_char=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client
        self.probe.RESPONSE_TIMEOUT = 0.005

    def prepare(self, count=2):
        pairs = [
            build_synthetic_pair(case, self.protocol)
            for case in (self.first_one, self.zero, self.second_one)
        ]
        self.responses = [
            frame(0x22, b"\x00\x00\xFF\xFF"),
            frame(0x24, b"\x83\x41\x00\x00"),
            frame(0x2B, count.to_bytes(2, "little") + b"\x01\x00"),
            *(part.data for pair in pairs for part in pair),
        ]

    async def _start(self, characteristic, callback):
        self.callback = callback

    async def _write(self, characteristic, data, *, response):
        index = self.client.write_gatt_char.await_count - 1
        self.assertEqual(data, EXPECTED_REQUESTS[index])
        self.assertIs(response, True)
        if index == self.fail_write_at:
            raise RuntimeError(ADDRESS)
        reply = self.responses[index]
        if reply is not None:
            self.callback(characteristic, bytearray(reply))

    async def run_probe(self):
        if not self.responses:
            self.prepare()
        return await self.probe.async_probe_history_semantics(self.hass, ADDRESS)

    def assert_private(self, result):
        public = json.dumps(result)
        self.assertNotIn(ADDRESS, public)
        self.assertNotIn(str(self.zero.raw_value), public)
        self.assertNotIn("65535", public)
        self.assertNotIn(str(self.zero.year), public)
        for raw in self.responses:
            if raw is not None:
                self.assertNotIn(raw.hex(), public.lower())
        for key in result:
            self.assertNotIn(key, (
                "raw_value", "scaled_value", "unit", "meter_local_time", "serial",
                "address", "hash", "digest", "raw_frame", "payload",
            ))
        self.client.read_gatt_char.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, ADDRESS, connectable=True
        )
        if self.connector.establish_connection.await_count:
            self.assertEqual(self.connector.establish_connection.await_args.kwargs["pair"], False)

    def assert_cleanup(self):
        self.client.stop_notify.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()

    async def test_expected_semantics_and_exact_sequence(self):
        result = await self.run_probe()
        self.assertEqual(
            [call.args[1] for call in self.client.write_gatt_char.call_args_list],
            list(EXPECTED_REQUESTS),
        )
        self.assertEqual(result["requested_indexes"], [1, 0, 1])
        self.assertTrue(result["semantic_probe_performed"])
        self.assertTrue(result["identity_confirmed"])
        self.assertTrue(result["index_0_analyte_identified"])
        self.assertTrue(result["index_0_is_uric_acid"])
        self.assertTrue(result["index_0_category_is_general"])
        self.assertTrue(result["index_0_value_valid"])
        self.assertFalse(result["index_0_is_qc"])
        for name in ("index_1_first", "index_1_second"):
            for suffix in (
                "pair_complete", "analyte_identified", "is_hematocrit",
                "category_is_qc", "value_invalid_sentinel", "is_qc",
            ):
                self.assertTrue(result[f"{name}_{suffix}"])
        self.assertTrue(result["repeated_index_1_semantics_equal"])
        self.assertTrue(result["expected_semantic_pattern_confirmed"])
        self.assertIsNone(result["error_code"])
        self.assert_cleanup()
        self.assert_private(result)

    async def test_count_mismatch_never_reads_records(self):
        self.prepare(count=3)
        result = await self.run_probe()
        self.assertEqual(self.client.write_gatt_char.await_count, 3)
        self.assertFalse(result["traversal_gate_passed"])
        self.assertFalse(result["semantic_probe_performed"])
        self.assertIsNone(result["repeated_index_1_semantics_equal"])
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

    async def test_bad_metadata_stops_before_pairs(self):
        self.prepare()
        self.responses[2] = self.responses[2][:-1] + b"\x00"
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "metadata")
        self.assertEqual(result["error_code"], "invalid_response")
        self.assertEqual(self.client.write_gatt_char.await_count, 3)
        self.assert_cleanup()

    async def test_malformed_pair_stops_before_later_indexes(self):
        self.prepare()
        self.responses[4] = None
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], "index_1_first_part_2")
        self.assertEqual(result["error_code"], "response_timeout")
        self.assertEqual(self.client.write_gatt_char.await_count, 5)
        self.assertFalse(result["semantic_probe_performed"])
        self.assert_cleanup()

    async def test_invalid_calendar_stops_before_part_two(self):
        self.prepare()
        self.responses[3] = frame(0x25, b"\x01\x00\x2A\x49")
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "invalid_response")
        self.assertEqual(self.client.write_gatt_char.await_count, 4)
        self.assert_cleanup()

    async def test_index_zero_wrong_analyte_is_semantic_mismatch(self):
        self.zero = SYNTHETIC_CASES[2]
        result = await self.run_probe()
        self.assertFalse(result["index_0_is_uric_acid"])
        self.assertFalse(result["expected_index_0_semantics_match"])
        self.assertFalse(result["expected_semantic_pattern_confirmed"])
        self.assertTrue(result["semantic_probe_performed"])
        self.assertIsNone(result["error_code"])
        self.assert_private(result)

    async def test_index_zero_wrong_category_is_semantic_mismatch(self):
        self.zero = SYNTHETIC_CASES[5]
        result = await self.run_probe()
        self.assertFalse(result["index_0_category_is_general"])
        self.assertFalse(result["expected_index_0_semantics_match"])
        self.assertIsNone(result["error_code"])

    async def test_index_zero_invalid_value_is_semantic_mismatch(self):
        self.zero = SYNTHETIC_CASES[9]
        result = await self.run_probe()
        self.assertFalse(result["index_0_value_valid"])
        self.assertFalse(result["expected_index_0_semantics_match"])
        self.assert_private(result)

    async def test_index_one_wrong_analyte_is_semantic_mismatch(self):
        self.first_one = SYNTHETIC_CASES[1]
        self.second_one = SYNTHETIC_CASES[1]
        result = await self.run_probe()
        self.assertFalse(result["index_1_first_is_hematocrit"])
        self.assertFalse(result["expected_index_1_semantics_match"])
        self.assertTrue(result["repeated_index_1_semantics_equal"])

    async def test_index_one_wrong_category_is_semantic_mismatch(self):
        self.first_one = SyntheticRecordCase(
            "hct_general", 2037, 11, 17, 10, 45, True, 0xFFFF, 6, 0
        )
        self.second_one = self.first_one
        result = await self.run_probe()
        self.assertFalse(result["index_1_first_category_is_qc"])
        self.assertFalse(result["expected_index_1_semantics_match"])

    async def test_index_one_valid_value_is_semantic_mismatch(self):
        self.first_one = SyntheticRecordCase(
            "hct_valid", 2037, 11, 17, 10, 45, True, 123, 6, 3
        )
        self.second_one = self.first_one
        result = await self.run_probe()
        self.assertFalse(result["index_1_first_value_invalid_sentinel"])
        self.assertFalse(result["expected_index_1_semantics_match"])

    async def test_repeat_analyte_difference(self):
        self.second_one = SYNTHETIC_CASES[1]
        result = await self.run_probe()
        self.assertFalse(result["repeated_index_1_analyte_equal"])
        self.assertFalse(result["repeated_index_1_semantics_equal"])
        self.assertFalse(result["expected_semantic_pattern_confirmed"])

    async def test_repeat_category_difference(self):
        self.second_one = SyntheticRecordCase(
            "hct_general", 2037, 11, 17, 10, 45, True, 0xFFFF, 6, 0
        )
        result = await self.run_probe()
        self.assertFalse(result["repeated_index_1_category_equal"])
        self.assertFalse(result["repeated_index_1_semantics_equal"])

    async def test_repeat_validity_difference(self):
        self.second_one = SyntheticRecordCase(
            "hct_valid", 2037, 11, 17, 10, 45, True, 123, 6, 3
        )
        result = await self.run_probe()
        self.assertFalse(result["repeated_index_1_validity_equal"])
        self.assertFalse(result["repeated_index_1_semantics_equal"])

    async def test_unknown_analyte_is_not_guessed(self):
        self.zero = SYNTHETIC_CASES[4]
        result = await self.run_probe()
        self.assertFalse(result["index_0_analyte_identified"])
        self.assertFalse(result["index_0_is_uric_acid"])
        self.assertIsNone(result["error_code"])

    async def test_write_failure_has_no_retry_and_no_private_log(self):
        self.prepare()
        self.fail_write_at = 3
        with patch.object(logging.Logger, "_log") as logs:
            result = await self.run_probe()
        self.assertEqual(result["error_code"], "write_failed")
        self.assertEqual(self.client.write_gatt_char.await_count, 4)
        self.assertNotIn(ADDRESS, str(logs.call_args_list))
        self.assert_cleanup()
        self.assert_private(result)

    async def test_cancellation_cleans_up(self):
        self.prepare()
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

    async def test_source_boundary(self):
        source = (INTEGRATION / "history_semantics_probe.py").read_text()
        for forbidden in ("0x2F", "0x33", "0x50", "coordinator", "sensor_state", "async_write_ha_state", "async_create_task"):
            self.assertNotIn(forbidden, source)
        for pure in ("protocol.py", "models.py"):
            text = (INTEGRATION / pure).read_text().lower()
            self.assertNotIn("homeassistant", text)
            self.assertNotIn("bleak", text)


class ActionRegistrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_only_address_input_and_separate_action(self):
        from test_gatt_probe import _load_probe, _load_setup, _registered_action

        gatt, _, _ = _load_probe()
        integration, _, _, _ = _load_setup(gatt)
        services = Mock()
        hass = types.SimpleNamespace(services=services)
        self.assertTrue(await integration.async_setup(hass, {}))
        action = _registered_action(services, "probe_history_semantics")
        self.assertEqual(action.kwargs["supports_response"], "response_only")
        result = await action.args[2](types.SimpleNamespace(data={"address": ADDRESS}))
        self.assertEqual(result, {"semantic_probe_performed": True})
        integration.async_probe_history_semantics.assert_awaited_once_with(hass, ADDRESS)
        definitions = yaml.safe_load((INTEGRATION / "services.yaml").read_text())
        for name in (
            "probe_history_semantics", "probe_history_window",
            "probe_protocol_identity", "probe_protocol_record",
        ):
            self.assertEqual(set(definitions[name]["fields"]), {"address"})


if __name__ == "__main__":
    unittest.main()
