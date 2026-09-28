"""Synthetic-only Stage 8H-B bounded history and action regressions."""

import asyncio
import json
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from fixtures_td4183 import SYNTHETIC_CASES, build_synthetic_pair, invalid_time_frame
from test_gatt_probe import _load_probe, _load_setup, _registered_action
from test_history_probe import frame
from test_manual_refresh import MAC, ROOT, load_refresh


class BoundedHistoryReaderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.modules, self.bluetooth = load_refresh()
        self.p = self.modules["protocol"]
        self.reader_module = self.modules["history_reader"]
        self.cases = {case.name: case for case in SYNTHETIC_CASES}
        self.responses = []
        self.requests = []
        self.fail_at = None
        self.cleanup_errors = ()
        self.stop_cleanly = True
        self.disconnect_cleanly = True
        self.closed = 0
        outer = self

        class FakeTransport:
            def __init__(self, hass, address, *, response_timeout):
                outer.address = address
                outer.timeout = response_timeout

            async def async_connect(self):
                if outer.fail_at == "connect":
                    raise outer.bluetooth.TransportError("connection", "connect_failed")

            async def async_subscribe(self):
                if outer.fail_at == "subscribe":
                    raise outer.bluetooth.TransportError("subscription", "subscription_failed")

            async def async_exchange(self, request):
                outer.requests.append(request)
                if outer.fail_at == len(outer.requests):
                    raise outer.bluetooth.TransportError("exchange", "response_timeout")
                return outer.responses.pop(0)

            async def async_close(self):
                outer.closed += 1
                return types.SimpleNamespace(
                    notification_stopped_cleanly=outer.stop_cleanly,
                    disconnected_cleanly=outer.disconnect_cleanly,
                    errors=outer.cleanup_errors,
                )

        self.reader_module.Fora6BluetoothTransport = FakeTransport
        self.runtime = self.modules["sensor_state"].MeterRuntime(address=MAC.upper())
        self.entry = types.SimpleNamespace(unique_id=MAC)
        self.reader = self.reader_module.Fora6HistoryReader(
            object(), self.entry, self.runtime
        )

    def prepare(self, names, count=None):
        count = len(names) if count is None else count
        self.responses = [
            self.p.ProtocolFrame(frame(0x22, b"\x00\x00\xff\xff")),
            self.p.ProtocolFrame(frame(0x24, b"\x83\x41\x00\x00")),
            self.p.ProtocolFrame(frame(0x2B, count.to_bytes(2, "little") + b"\x03\x00")),
        ]
        for name in names:
            self.responses.extend(build_synthetic_pair(self.cases[name], self.p))

    def assert_failure_without_measurements(self, result, stage, code):
        self.assertFalse(result["history_read_successful"])
        self.assertEqual(result["error_stage"], stage)
        self.assertEqual(result["error_code"], code)
        self.assertEqual(result["eligible_measurement_count"], 0)
        self.assertEqual(result["measurements"], [])

    async def test_count_two_returns_only_primary_and_does_not_touch_sensor(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        prior_record = self.modules["models"].combine_td4183_record(
            self.p.parse_td4183_record_part_one(self.responses[3]),
            self.p.parse_td4183_record_part_two(self.responses[4]),
        )
        prior = self.modules["measurement"].measurement_from_record(prior_record)
        self.runtime.measurement_state.replace(prior)
        notified = Mock()
        self.runtime.measurement_state.subscribe(notified)
        sync_time = datetime(2036, 1, 1, tzinfo=timezone.utc)
        self.runtime.synchronized_at = sync_time

        result = await self.reader.async_read()

        self.assertTrue(result["history_read_successful"])
        self.assertEqual(result["raw_slot_count"], 2)
        self.assertEqual(result["eligible_measurement_count"], 1)
        self.assertEqual(result["measurements"], [{
            "raw_index": 0,
            "uric_acid_value_mg_dl": 123.4,
            "meter_local_time": "2037-10-14 09:42",
            "meter_local_timezone_known": False,
        }])
        self.assertFalse(result["chronology_ambiguous"])
        self.assertIs(self.runtime.measurement_state.latest, prior)
        self.assertIs(self.runtime.synchronized_at, sync_time)
        notified.assert_not_called()
        self.assertEqual(self.closed, 1)
        serialized = json.dumps(result)
        self.assertNotIn(MAC, serialized)
        for private_field in ("serial", "system_id", "raw_frame", "payload"):
            self.assertNotIn(private_field, serialized)
        self.assertEqual([request.command_id for request in self.requests],
                         [0x22, 0x24, 0x2B, 0x25, 0x26, 0x25, 0x26])

    async def test_count_four_sorts_by_time_in_both_raw_index_directions(self):
        for names, expected in (
            (["uric_general", "hct_qc_invalid", "minimum_time", "hct_qc_invalid"], [0, 2]),
            (["minimum_time", "hct_qc_invalid", "future_time", "hct_qc_invalid"], [2, 0]),
        ):
            with self.subTest(expected=expected):
                self.prepare(names)
                self.requests.clear()
                result = await self.reader.async_read()
                self.assertTrue(result["history_read_successful"])
                self.assertEqual(result["eligible_measurement_count"], 2)
                self.assertEqual([item["raw_index"] for item in result["measurements"]], expected)
                self.assertFalse(result["chronology_ambiguous"])
                self.assertEqual([request.command_id for request in self.requests],
                                 [0x22, 0x24, 0x2B] + [0x25, 0x26] * 4)
                self.assertEqual(len(self.responses), 0)

    async def test_equal_minute_preserves_both_without_newer_claim(self):
        self.prepare(["uric_general", "hct_qc_invalid", "uric_general", "hct_qc_invalid"])
        result = await self.reader.async_read()
        self.assertTrue(result["history_read_successful"])
        self.assertTrue(result["chronology_ambiguous"])
        self.assertEqual([item["raw_index"] for item in result["measurements"]], [0, 2])
        self.assertEqual(result["measurements"][0]["meter_local_time"],
                         result["measurements"][1]["meter_local_time"])

    async def test_every_unsupported_count_stops_before_record_reads(self):
        for count in (0, 1, 3, 5, 6, 8):
            with self.subTest(count=count):
                self.prepare([], count)
                self.requests.clear()
                result = await self.reader.async_read()
                self.assert_failure_without_measurements(result, "metadata", "unsupported_history_count")
                self.assertEqual(result["raw_slot_count"], count)
                self.assertFalse(result["supported_raw_slot_count"])
                self.assertEqual([request.command_id for request in self.requests],
                                 [0x22, 0x24, 0x2B])

    async def test_invalid_primary_and_companion_fail_closed(self):
        for names, code in (
            (["uric_invalid", "hct_qc_invalid"], "invalid_primary"),
            (["uric_qc", "hct_qc_invalid"], "invalid_primary"),
            (["ketone_general", "hct_qc_invalid"], "invalid_primary"),
            (["uric_general", "uric_general"], "unexpected_companion"),
            (["uric_general", "hct_qc_invalid", "uric_general", "uric_general"], "unexpected_companion"),
            (["uric_general", "hct_qc_invalid", "ketone_general", "hct_qc_invalid"], "invalid_primary"),
        ):
            with self.subTest(names=names):
                self.prepare(names)
                result = await self.reader.async_read()
                self.assert_failure_without_measurements(result, "record", code)

    async def test_identity_project_metadata_and_subscription_failures(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.entry.unique_id = "aa:bb:cc:dd:ee:02"
        result = await self.reader.async_read()
        self.assert_failure_without_measurements(result, "identity", "identity_mismatch")
        self.assertEqual(self.requests, [])
        self.entry.unique_id = MAC

        self.prepare(["uric_general", "hct_qc_invalid"])
        self.fail_at = "connect"
        result = await self.reader.async_read()
        self.assert_failure_without_measurements(result, "connection", "connect_failed")
        self.fail_at = None

        self.prepare(["uric_general", "hct_qc_invalid"])
        self.fail_at = "subscribe"
        result = await self.reader.async_read()
        self.assert_failure_without_measurements(result, "subscription", "subscription_failed")
        self.fail_at = None

        self.prepare(["uric_general", "hct_qc_invalid"])
        self.responses[1] = self.p.ProtocolFrame(frame(0x24, b"\x00\x00\x00\x00"))
        result = await self.reader.async_read()
        self.assert_failure_without_measurements(result, "project", "unexpected_project_id")

        self.prepare(["uric_general", "hct_qc_invalid"])
        self.responses[2] = self.p.ProtocolFrame(frame(0x25, b"\x02\x00\x01\x00"))
        result = await self.reader.async_read()
        self.assert_failure_without_measurements(result, "metadata", "invalid_response")

    async def test_timestamp_value_and_partial_count_four_failures(self):
        for failure_index, stage, code in (
            (4, "record_part_1", "invalid_response"),
            (5, "record_part_2", "invalid_response"),
            (10, "record_part_1", "response_timeout"),
        ):
            with self.subTest(failure_index=failure_index):
                self.prepare(["uric_general", "hct_qc_invalid", "minimum_time", "hct_qc_invalid"])
                if failure_index == 4:
                    self.responses[3] = invalid_time_frame(self.p)
                elif failure_index == 5:
                    self.responses[4] = self.p.ProtocolFrame(frame(0x25, b"\x00\x00\x00\x00"))
                else:
                    self.fail_at = failure_index
                self.requests.clear()
                result = await self.reader.async_read()
                self.assert_failure_without_measurements(result, stage, code)
                self.fail_at = None

    async def test_cleanup_failure_never_returns_private_values(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.cleanup_errors = ("disconnect_failed",)
        result = await self.reader.async_read()
        self.assert_failure_without_measurements(result, "cleanup", "disconnect_failed")
        self.assertEqual(result["cleanup_errors"], ["disconnect_failed"])
        self.cleanup_errors = ()
        self.stop_cleanly = False
        self.prepare(["uric_general", "hct_qc_invalid"])
        result = await self.reader.async_read()
        self.assert_failure_without_measurements(result, "cleanup", "incomplete_cleanup")

    async def test_primary_error_survives_cleanup_error(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.fail_at = "subscribe"
        self.cleanup_errors = ("disconnect_failed",)
        result = await self.reader.async_read()
        self.assert_failure_without_measurements(result, "subscription", "subscription_failed")
        self.assertEqual(result["cleanup_errors"], ["disconnect_failed"])

    async def test_same_entry_lock_rejects_history_and_refresh(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        coordinator = self.modules["coordinator"].Fora6CurrentRefreshCoordinator(
            object(), self.entry, self.runtime
        )
        self.assertIs(self.reader._lock, coordinator._lock)
        async with self.runtime.gatt_lock:
            result = await self.reader.async_read()
            refresh = await coordinator.async_refresh()
        self.assert_failure_without_measurements(result, "history", "already_running")
        self.assertEqual(refresh["error_code"], "already_running")
        self.assertEqual(self.closed, 0)

    async def test_different_entry_has_independent_lock(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        other = self.modules["sensor_state"].MeterRuntime(address="aa:bb:cc:dd:ee:02")
        second = self.reader_module.Fora6HistoryReader(
            object(), types.SimpleNamespace(unique_id="aa:bb:cc:dd:ee:02"), other
        )
        async with self.runtime.gatt_lock:
            result = await second.async_read()
        self.assertTrue(result["history_read_successful"])
        self.assertIsNot(self.reader._lock, second._lock)

    async def test_cancellation_runs_cleanup_without_health_result(self):
        entered = asyncio.Event()

        async def pending(_transport):
            entered.set()
            await asyncio.Event().wait()

        self.prepare(["uric_general", "hct_qc_invalid"])
        with patch.object(self.reader_module.Fora6BluetoothTransport, "async_connect", pending):
            task = asyncio.create_task(self.reader.async_read())
            await entered.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertEqual(self.closed, 1)

    def test_no_persistence_logging_events_or_forbidden_commands(self):
        sources = "\n".join((ROOT / name).read_text() for name in
                            ("bounded_records.py", "history_reader.py"))
        for forbidden in ("0x33", "0x2F", "0x50", "recorder", "statistics", "async_fire(",
                          "measurement_state.replace(", "synchronized_at =", "_LOGGER", "logging.",
                          "Store(", "async_create_task("):
            self.assertNotIn(forbidden, sources)


class HistoryActionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.integration, _, _, self.errors = _load_setup(_load_probe()[0])
        self.reader = types.SimpleNamespace(async_read=AsyncMock(return_value={
            "history_read_successful": True,
            "measurements": [{"uric_acid_value_mg_dl": 1.2}],
        }))
        self.runtime = types.SimpleNamespace(
            address=MAC, history_reader=self.reader, history_read_task=None,
            readiness_probe_task=None, advertisement_observation_stop=None,
            gatt_lock=asyncio.Lock(),
        )
        self.entry = types.SimpleNamespace(
            domain="fora6_connect", state="loaded", runtime_data=self.runtime
        )
        self.hass = types.SimpleNamespace(
            services=types.SimpleNamespace(async_register=Mock()),
            config_entries=types.SimpleNamespace(
                async_get_entry=Mock(return_value=self.entry),
                async_unload_platforms=AsyncMock(return_value=True),
            ),
        )

    async def action(self, name="read_uric_acid_history"):
        await self.integration.async_setup(self.hass, {})
        return _registered_action(self.hass.services, name).args[2]

    async def test_private_action_targets_entry_and_returns_response(self):
        handler = await self.action()
        response = await handler(types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"}))
        self.assertEqual(response["measurements"], [{"uric_acid_value_mg_dl": 1.2}])
        self.hass.config_entries.async_get_entry.assert_called_with("synthetic-entry")
        self.reader.async_read.assert_awaited_once()
        self.assertIsNone(self.runtime.history_read_task)

    async def test_invalid_entry_and_missing_reader_rejected_before_ble(self):
        handler = await self.action()
        with self.assertRaises(self.errors.ServiceValidationError):
            await handler(types.SimpleNamespace(data={"address": MAC}))
        self.entry.domain = "other"
        with self.assertRaises(self.errors.ServiceValidationError):
            await handler(types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"}))
        self.entry.domain = "fora6_connect"
        self.entry.state = "unloaded"
        with self.assertRaises(self.errors.ServiceValidationError):
            await handler(types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"}))
        self.entry.state = "loaded"
        self.runtime.history_reader = None
        with self.assertRaises(self.errors.ServiceValidationError):
            await handler(types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"}))
        self.reader.async_read.assert_not_awaited()

    async def test_failure_raises_sanitized_exception_without_private_data(self):
        handler = await self.action()
        self.reader.async_read.return_value = {
            "history_read_successful": False,
            "error_stage": "subscription",
            "error_code": "subscription_failed",
            "cleanup_errors": ["disconnect_failed"],
            "measurements": [],
        }
        with self.assertRaises(self.errors.HomeAssistantError) as caught:
            await handler(types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"}))
        self.assertIn("stage=subscription, code=subscription_failed", str(caught.exception))
        self.assertIn("cleanup=disconnect_failed", str(caught.exception))
        self.assertNotIn(MAC, str(caught.exception))
        self.reader.async_read.return_value["error_code"] = MAC
        with self.assertRaises(self.errors.HomeAssistantError) as caught:
            await handler(types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"}))
        self.assertIn("code=unknown", str(caught.exception))
        self.assertNotIn(MAC, str(caught.exception))

    async def test_p4_and_history_share_lock_without_changing_probe(self):
        history = await self.action()
        readiness = _registered_action(self.hass.services, "probe_transaction_readiness").args[2]
        request = types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"})
        async with self.runtime.gatt_lock:
            with self.assertRaises(self.errors.ServiceValidationError):
                await history(request)
            with self.assertRaises(self.errors.ServiceValidationError):
                await readiness(request)
        self.reader.async_read.assert_not_awaited()

    async def test_unload_cancels_history_task_and_clears_reader(self):
        handler = await self.action()
        entered = asyncio.Event()

        async def pending():
            entered.set()
            await asyncio.Event().wait()

        self.reader.async_read.side_effect = pending
        request = types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"})
        task = asyncio.create_task(handler(request))
        await entered.wait()
        self.assertIs(self.runtime.history_read_task, task)
        self.assertTrue(await self.integration.async_unload_entry(self.hass, self.entry))
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertIsNone(self.runtime.history_read_task)
        self.assertIsNone(self.runtime.history_reader)


if __name__ == "__main__":
    unittest.main()
