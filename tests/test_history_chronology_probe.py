"""Synthetic tests for the fixed two-primary chronology action."""

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
    name = "_fora6_chronology_test"
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
    for short in ("protocol", "models", "bluetooth", "history_chronology_probe"):
        spec = importlib.util.spec_from_file_location(f"{name}.{short}", INTEGRATION / f"{short}.py")
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        modules[spec.name] = module
        loaded[short] = (spec, module)
    with patch.dict(sys.modules, modules):
        for spec, module in loaded.values():
            spec.loader.exec_module(module)
    return loaded["protocol"][1], loaded["history_chronology_probe"][1], bluetooth, connector, const


class ChronologyProbeTests(unittest.IsolatedAsyncioTestCase):
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
        self.two = cases["future_time"]
        self.expected = [
            self.protocol.build_wake_request().data,
            self.protocol.build_project_query_request().data,
            self.protocol.build_record_slot_count_request().data,
            self.protocol.build_first_record_part_one_request().data,
            self.protocol.build_first_record_part_two_request().data,
            self.protocol.build_third_record_part_one_request().data,
            self.protocol.build_third_record_part_two_request().data,
        ]
        self.responses = []
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
        pair_zero = build_synthetic_pair(self.zero, self.protocol)
        pair_two = build_synthetic_pair(self.two, self.protocol)
        self.responses = [
            frame(0x22, b"\x00\x00\xFF\xFF"),
            frame(0x24, b"\x83\x41\x00\x00"),
            frame(0x2B, count.to_bytes(2, "little") + b"\x03\x00"),
            *(part.data for pair in (pair_zero, pair_two) for part in pair),
        ]

    async def _start(self, characteristic, callback):
        self.callback = callback

    async def _write(self, characteristic, data, *, response):
        index = self.client.write_gatt_char.await_count - 1
        self.assertEqual(data, self.expected[index])
        self.assertIs(response, True)
        reply = self.responses[index]
        if reply is not None:
            self.callback(characteristic, bytearray(reply))

    async def run_probe(self):
        if not self.responses:
            self.prepare()
        return await self.probe.async_probe_history_chronology(self.hass, ADDRESS)

    def assert_private(self, result):
        public = json.dumps(result)
        self.assertNotIn(ADDRESS, public)
        private_response_keys = {
            f"index_{index}_{field}"
            for index in (0, 2)
            for field in ("meter_local_time", "uric_acid_value_mg_dl")
        }
        self.assertTrue(all(
            key in private_response_keys or
            value is None or isinstance(value, (bool, list)) or
            (key == "expected_raw_slot_count" and value == 4) or
            (key in ("error_stage", "error_code") and isinstance(value, str))
            for key, value in result.items()
        ))
        for key in private_response_keys & result.keys():
            if key.endswith("meter_local_time"):
                self.assertRegex(result[key], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
                self.assertNotIn("Z", result[key])
                self.assertNotIn("+", result[key])
            else:
                self.assertIsInstance(result[key], float)
        for raw in self.responses:
            if raw is not None:
                self.assertNotIn(raw.hex(), public.lower())
        for key in result:
            self.assertNotIn(key, (
                "raw_value", "scaled_value", "unit", "serial", "system_id",
                "address", "hash", "digest", "raw_frame", "payload", "time_delta",
            ))
        self.client.read_gatt_char.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        if self.connector.establish_connection.await_count:
            self.assertIs(self.connector.establish_connection.await_args.kwargs["pair"], False)
        for call in self.client.write_gatt_char.call_args_list:
            self.assertIs(call.kwargs["response"], True)

    def assert_cleanup(self):
        self.client.stop_notify.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()

    async def test_before_exact_sequence_and_semantic_gate(self):
        result = await self.run_probe()
        self.assertEqual([c.args[1] for c in self.client.write_gatt_char.call_args_list], self.expected)
        self.assertEqual(self.client.write_gatt_char.await_count, 7)
        self.assertTrue(result["chronology_comparison_complete"])
        self.assertTrue(result["index_0_semantic_match"])
        self.assertTrue(result["index_2_semantic_match"])
        self.assertEqual(result["index_0_uric_acid_value_mg_dl"], self.zero.raw_value / 10)
        self.assertEqual(result["index_2_uric_acid_value_mg_dl"], self.two.raw_value / 10)
        self.assertNotEqual(result["index_0_uric_acid_value_mg_dl"], self.zero.raw_value)
        self.assertNotEqual(result["index_2_uric_acid_value_mg_dl"], self.two.raw_value)
        self.assertEqual(result["index_0_meter_local_time"], "2037-10-14 09:42")
        self.assertEqual(result["index_2_meter_local_time"], "2099-12-31 23:59")
        self.assertTrue(result["index_0_time_before_index_2"])
        self.assertEqual(sum(result[key] for key in (
            "index_0_time_before_index_2", "index_0_time_equal_index_2", "index_0_time_after_index_2"
        )), 1)
        self.assert_cleanup()
        self.assert_private(result)

    async def test_equal_and_after(self):
        cases = {case.name: case for case in SYNTHETIC_CASES}
        for zero, two, expected in (
            (cases["uric_general"], cases["uric_general"], "index_0_time_equal_index_2"),
            (cases["future_time"], cases["minimum_time"], "index_0_time_after_index_2"),
        ):
            with self.subTest(expected=expected):
                self.zero, self.two = zero, two
                self.prepare()
                self.client.write_gatt_char.reset_mock()
                self.client.stop_notify.reset_mock()
                self.client.disconnect.reset_mock()
                result = await self.run_probe()
                self.assertTrue(result[expected])
                self.assertEqual(sum(result[key] for key in (
                    "index_0_time_before_index_2", "index_0_time_equal_index_2", "index_0_time_after_index_2"
                )), 1)
                self.assert_cleanup()
                self.assert_private(result)

    async def test_count_gate_stops_before_primary_reads(self):
        for count in (0, 1, 2, 3, 5):
            with self.subTest(count=count):
                self.prepare(count)
                self.client.write_gatt_char.reset_mock()
                self.client.stop_notify.reset_mock()
                self.client.disconnect.reset_mock()
                result = await self.run_probe()
                self.assertEqual(self.client.write_gatt_char.await_count, 3)
                self.assertFalse(result["raw_slot_count_matches_expected"])
                self.assertFalse(result["chronology_probe_performed"])
                for index in (0, 2):
                    self.assertNotIn(f"index_{index}_meter_local_time", result)
                    self.assertNotIn(f"index_{index}_uric_acid_value_mg_dl", result)
                self.assert_cleanup()
                self.assert_private(result)

    async def test_semantic_mismatch_stops_before_comparison(self):
        cases = {case.name: case for case in SYNTHETIC_CASES}
        for position in ("zero", "two"):
            for bad in ("ketone_general", "uric_qc", "uric_invalid"):
                with self.subTest(position=position, bad=bad):
                    self.zero = cases["uric_general"]
                    self.two = cases["future_time"]
                    setattr(self, position, cases[bad])
                    self.prepare()
                    self.client.write_gatt_char.reset_mock()
                    self.client.stop_notify.reset_mock()
                    self.client.disconnect.reset_mock()
                    result = await self.run_probe()
                    self.assertFalse(result[f"index_{0 if position == 'zero' else 2}_semantic_match"])
                    self.assertFalse(result["chronology_probe_performed"])
                    self.assertFalse(result["chronology_comparison_complete"])
                    self.assertEqual(self.client.write_gatt_char.await_count, 5 if position == "zero" else 7)
                    failing_index = 0 if position == "zero" else 2
                    self.assertNotIn(f"index_{failing_index}_uric_acid_value_mg_dl", result)
                    self.assertNotIn(f"index_{failing_index}_meter_local_time", result)
                    if position == "zero":
                        self.assertNotIn("index_2_uric_acid_value_mg_dl", result)
                    else:
                        self.assertIn("index_0_uric_acid_value_mg_dl", result)
                    self.assert_cleanup()
                    self.assert_private(result)

    async def test_project_and_metadata_fail_closed(self):
        for write, altered, stage in (
            (1, frame(0x24, b"\x84\x41\x00\x00"), "project"),
            (2, b"invalid", "metadata"),
        ):
            with self.subTest(stage=stage):
                self.prepare()
                self.responses[write] = altered
                self.client.write_gatt_char.reset_mock()
                self.client.stop_notify.reset_mock()
                self.client.disconnect.reset_mock()
                result = await self.run_probe()
                self.assertEqual(result["error_stage"], stage)
                self.assertEqual(self.client.write_gatt_char.await_count, write + 1)
                self.assertFalse(result["chronology_probe_performed"])
                self.assert_cleanup()
                self.assert_private(result)

    async def test_each_pair_failure_stops_and_cleans_up(self):
        for write in range(3, 7):
            with self.subTest(write=write):
                self.prepare()
                self.responses[write] = None
                self.client.write_gatt_char.reset_mock()
                self.client.stop_notify.reset_mock()
                self.client.disconnect.reset_mock()
                result = await self.run_probe()
                self.assertEqual(result["error_code"], "response_timeout")
                self.assertEqual(self.client.write_gatt_char.await_count, write + 1)
                self.assertFalse(result["chronology_probe_performed"])
                self.assert_cleanup()
                self.assert_private(result)

    async def test_malformed_pair_and_wrong_echo_stop_without_retry(self):
        for write in range(3, 7):
            with self.subTest(write=write):
                self.prepare()
                response = bytearray(self.responses[write])
                response[1] = 0x26 if write % 2 else 0x25
                response[-1] = sum(response[:-1]) & 0xFF
                self.responses[write] = bytes(response)
                self.client.write_gatt_char.reset_mock()
                self.client.stop_notify.reset_mock()
                self.client.disconnect.reset_mock()
                result = await self.run_probe()
                self.assertEqual(result["error_code"], "invalid_response")
                self.assertEqual(self.client.write_gatt_char.await_count, write + 1)
                self.assertFalse(result["chronology_comparison_complete"])
                self.assert_cleanup()
                self.assert_private(result)

    async def test_subscription_failure_sends_no_application_command(self):
        self.client.start_notify.side_effect = RuntimeError(ADDRESS)
        result = await self.run_probe()
        self.client.write_gatt_char.assert_not_awaited()
        self.assertFalse(result["chronology_probe_performed"])
        self.assertIsNotNone(result["error_code"])
        self.assertNotIn(ADDRESS, json.dumps(result))
        self.client.disconnect.assert_awaited_once()

    async def test_cleanup_failure_is_privacy_safe(self):
        self.client.stop_notify.side_effect = RuntimeError(ADDRESS)
        result = await self.run_probe()
        self.assertFalse(result["notification_stopped_cleanly"])
        self.assertIsNotNone(result["error_code"])
        self.assertNotIn(ADDRESS, json.dumps(result))

    async def test_no_device_and_cancellation(self):
        self.bluetooth.async_ble_device_from_address.return_value = None
        result = await self.run_probe()
        self.assertFalse(result["device_found"])
        self.client.write_gatt_char.assert_not_awaited()
        self.assert_private(result)
        self.bluetooth.async_ble_device_from_address.return_value = object()
        self.prepare()
        self.responses[3] = None
        task = asyncio.create_task(self.run_probe())
        await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.client.disconnect.assert_awaited_once()

    async def test_safe_log_registration_and_no_product_state(self):
        self.prepare()
        self.responses[3] = None
        with patch.object(logging, "exception") as log_exception:
            result = await self.run_probe()
        log_exception.assert_not_called()
        self.assert_private(result)
        from test_gatt_probe import _load_probe, _load_setup, _registered_action
        integration, _, _, _ = _load_setup(_load_probe()[0])
        hass = types.SimpleNamespace(services=types.SimpleNamespace(async_register=Mock()), data={})
        await integration.async_setup(hass, {})
        registration = _registered_action(hass.services, "probe_history_chronology")
        self.assertEqual(registration.kwargs["supports_response"], "response_only")
        response = await registration.args[2](types.SimpleNamespace(data={"address": ADDRESS}))
        self.assertEqual(response, {"chronology_comparison_complete": True})
        integration.async_probe_history_chronology.assert_awaited_once_with(hass, ADDRESS)
        source = (INTEGRATION / "history_chronology_probe.py").read_text()
        for forbidden in (
            "0x2F", "0x33", "0x50", "sensor_state", "async_write_ha_state",
            "coordinator", "async_create_task", "async_store", "config_entries",
        ):
            self.assertNotIn(forbidden, source)
        self.assertFalse({0x2F, 0x33, 0x50} & {data[1] for data in self.expected})
        self.assertNotIn("homeassistant", (INTEGRATION / "protocol.py").read_text().lower())
        self.assertNotIn("bleak", (INTEGRATION / "protocol.py").read_text().lower())

    async def test_valid_health_fields_are_response_only(self):
        with patch.object(logging.Logger, "_log") as log_call:
            result = await self.run_probe()
        log_call.assert_not_called()
        self.assertIn("index_0_meter_local_time", result)
        self.assertIn("index_2_uric_acid_value_mg_dl", result)
        self.assert_private(result)
        source = (INTEGRATION / "history_chronology_probe.py").read_text()
        for forbidden in (
            "hass.data", "storage", "Store(", "async_store", "config_entries",
            "async_write_ha_state", "logger", "logging", "print(",
        ):
            self.assertNotIn(forbidden, source)
