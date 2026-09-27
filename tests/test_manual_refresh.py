"""Synthetic-only checks for Stage 7H's manual current-state boundary."""

import asyncio
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from fixtures_td4183 import SYNTHETIC_CASES, build_synthetic_pair
from test_history_probe import frame
from test_gatt_probe import _load_probe, _load_setup, _registered_action

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
MAC = "aa:bb:cc:dd:ee:01"  # Synthetic fixture only.


def load_refresh():
    name = "_fora6_manual_refresh_test"
    package = types.ModuleType(name)
    package.__path__ = [str(ROOT)]
    modules = {name: package}
    bluetooth = types.ModuleType(f"{name}.bluetooth")

    class TransportError(Exception):
        def __init__(self, stage, code):
            self.stage, self.code = stage, code

    bluetooth.TransportError = TransportError
    bluetooth.Fora6BluetoothTransport = object
    modules[bluetooth.__name__] = bluetooth
    loaded = {}
    for short in ("const", "protocol", "models", "measurement", "mac_identity", "sensor_state", "coordinator"):
        spec = importlib.util.spec_from_file_location(f"{name}.{short}", ROOT / f"{short}.py")
        module = importlib.util.module_from_spec(spec)
        modules[spec.name] = module
        loaded[short] = (spec, module)
    with patch.dict(sys.modules, modules):
        for spec, module in loaded.values():
            spec.loader.exec_module(module)
    return {key: module for key, (_, module) in loaded.items()}, bluetooth


class ManualRefreshTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.modules, self.bluetooth = load_refresh()
        self.p = self.modules["protocol"]
        self.c = self.modules["coordinator"]
        self.cases = {case.name: case for case in SYNTHETIC_CASES}
        self.responses = []
        self.requests = []
        self.cleanup_errors = ()
        self.fail_at = None
        outer = self

        class FakeTransport:
            def __init__(self, hass, address, *, response_timeout):
                self._address = address
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
                    notification_stopped_cleanly=not bool(outer.cleanup_errors),
                    disconnected_cleanly=True,
                    errors=outer.cleanup_errors,
                )

        self.bluetooth.Fora6BluetoothTransport = FakeTransport
        self.c.Fora6BluetoothTransport = FakeTransport
        self.closed = 0
        self.runtime = self.modules["sensor_state"].MeterRuntime(address=MAC.upper())
        self.entry = types.SimpleNamespace(unique_id=MAC)
        self.coordinator = self.c.Fora6CurrentRefreshCoordinator(object(), self.entry, self.runtime)

    def prepare(self, names, count=None):
        if count is None:
            count = len(names)
        self.responses = [
            self.p.ProtocolFrame(frame(0x22, b"\x00\x00\xff\xff")),
            self.p.ProtocolFrame(frame(0x24, b"\x83\x41\x00\x00")),
            self.p.ProtocolFrame(frame(0x2B, count.to_bytes(2, "little") + b"\x03\x00")),
        ]
        for name in names:
            self.responses.extend(build_synthetic_pair(self.cases[name], self.p))

    def expected(self, count):
        builders = [self.p.build_wake_request, self.p.build_project_query_request, self.p.build_record_slot_count_request]
        for one, two in self.c._REQUEST_PAIRS[:count]:
            builders += [one, two]
        return [builder().data for builder in builders]

    async def test_count_two_selects_only_primary_and_notifies_state(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        notified = Mock()
        self.runtime.measurement_state.subscribe(notified)
        result = await self.coordinator.async_refresh()
        self.assertEqual([r.data for r in self.requests], self.expected(2))
        self.assertTrue(result["refresh_successful"])
        self.assertEqual(result["selected_primary_index"], 0)
        self.assertEqual(result["selected_uric_acid_value_mg_dl"], 123.4)
        self.assertEqual(result["selected_measurement_time_local"], "2037-10-14 09:42")
        self.assertEqual(str(self.runtime.measurement_state.native_value), "123.4")
        self.assertIsNotNone(self.runtime.synchronized_at.tzinfo)
        self.assertIsNone(self.runtime.measurement_state.latest.meter_local_time.tzinfo)
        notified.assert_called_once()
        self.assertEqual(self.closed, 1)

    async def test_count_four_selects_strict_later_timestamp(self):
        self.prepare(["uric_general", "hct_qc_invalid", "minimum_time", "hct_qc_invalid"])
        result = await self.coordinator.async_refresh()
        self.assertEqual([r.data for r in self.requests], self.expected(4))
        self.assertEqual(result["selected_primary_index"], 0)
        self.assertEqual(result["eligible_primary_count"], 2)
        self.prepare(["minimum_time", "hct_qc_invalid", "future_time", "hct_qc_invalid"])
        result = await self.coordinator.async_refresh()
        self.assertEqual(result["selected_primary_index"], 2)
        self.assertEqual(str(self.runtime.measurement_state.native_value), "0.2")

    async def test_only_one_count_four_candidate(self):
        for names, selected in (
            (["uric_general", "hct_qc_invalid", "ketone_general", "hct_qc_invalid"], 0),
            (["ketone_general", "hct_qc_invalid", "uric_general", "hct_qc_invalid"], 2),
        ):
            with self.subTest(selected=selected):
                self.prepare(names)
                result = await self.coordinator.async_refresh()
                self.assertEqual(result["selected_primary_index"], selected)
                self.assertEqual(result["eligible_primary_count"], 1)

    async def test_unsupported_counts_stop_before_record_access(self):
        for count in (0, 1, 3, 5, 6):
            with self.subTest(count=count):
                self.requests.clear()
                self.prepare([], count)
                result = await self.coordinator.async_refresh()
                self.assertEqual([r.data for r in self.requests], self.expected(0))
                self.assertEqual(result["error_code"], "unsupported_history_count")
                self.assertFalse(result["sensor_updated"])

    async def test_bad_primary_semantics_retain_prior_state(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        await self.coordinator.async_refresh()
        prior = self.runtime.measurement_state.latest
        for name in ("uric_invalid", "uric_qc", "ac", "pc", "ketone_general"):
            with self.subTest(name=name):
                self.prepare([name, "hct_qc_invalid"])
                result = await self.coordinator.async_refresh()
                self.assertFalse(result["refresh_successful"])
                self.assertTrue(result["retained_previous_state"])
                self.assertIs(self.runtime.measurement_state.latest, prior)

    async def test_ambiguous_time_retains_prior(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        await self.coordinator.async_refresh()
        prior = self.runtime.measurement_state.latest
        self.prepare(["uric_general", "hct_qc_invalid", "uric_general", "hct_qc_invalid"])
        result = await self.coordinator.async_refresh()
        self.assertTrue(result["ambiguity_detected"])
        self.assertEqual(result["error_code"], "ambiguous_meter_local_time")
        self.assertIs(self.runtime.measurement_state.latest, prior)
        self.assertNotIn("selected_uric_acid_value_mg_dl", result)

    async def test_bad_companion_fails_closed(self):
        self.prepare(["uric_general", "uric_general"])
        result = await self.coordinator.async_refresh()
        self.assertEqual(result["error_code"], "unexpected_companion")
        self.assertIsNone(self.runtime.measurement_state.native_value)

    async def test_project_mismatch_and_identity_mismatch(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.responses[1] = self.p.ProtocolFrame(frame(0x24, b"\x00\x00\x00\x00"))
        result = await self.coordinator.async_refresh()
        self.assertEqual(result["error_code"], "unexpected_project_id")
        self.assertEqual(len(self.requests), 2)
        self.entry.unique_id = "aa:bb:cc:dd:ee:02"
        self.requests.clear()
        result = await self.coordinator.async_refresh()
        self.assertEqual(result["error_code"], "identity_mismatch")
        self.assertEqual(self.requests, [])

    async def test_transport_and_cleanup_failures_retain_state(self):
        for failure in ("connect", "subscribe", 4):
            with self.subTest(failure=failure):
                self.requests.clear()
                self.prepare(["uric_general", "hct_qc_invalid"])
                self.fail_at = failure
                result = await self.coordinator.async_refresh()
                self.assertFalse(result["sensor_updated"])
                self.assertIsNone(self.runtime.measurement_state.native_value)
        self.fail_at = None
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.cleanup_errors = ("disconnect_failed",)
        result = await self.coordinator.async_refresh()
        self.assertEqual(result["error_stage"], "cleanup")
        self.assertIsNone(self.runtime.measurement_state.native_value)

    async def test_later_cleanup_failure_retains_previous_measurement_and_ingestion_time(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.assertTrue((await self.coordinator.async_refresh())["refresh_successful"])
        previous = self.runtime.measurement_state.latest
        previous_sync = self.runtime.synchronized_at
        self.prepare(["future_time", "hct_qc_invalid"])
        self.cleanup_errors = ("notification_stop_failed",)
        result = await self.coordinator.async_refresh()
        self.assertFalse(result["sensor_updated"])
        self.assertTrue(result["retained_previous_state"])
        self.assertIs(self.runtime.measurement_state.latest, previous)
        self.assertIs(self.runtime.synchronized_at, previous_sync)

    async def test_primary_failure_is_not_hidden_by_cleanup_failure(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.fail_at = "subscribe"
        self.cleanup_errors = ("disconnect_failed",)
        result = await self.coordinator.async_refresh()
        self.assertEqual(result["error_stage"], "subscription")
        self.assertEqual(result["error_code"], "subscription_failed")
        self.assertEqual(result["cleanup_errors"], ["disconnect_failed"])
        self.assertIsNone(self.runtime.measurement_state.native_value)

    async def test_repeat_same_measurement_updates_same_state_holder(self):
        notified = Mock()
        self.runtime.measurement_state.subscribe(notified)
        self.prepare(["uric_general", "hct_qc_invalid"])
        first = await self.coordinator.async_refresh()
        state = self.runtime.measurement_state
        self.prepare(["uric_general", "hct_qc_invalid"])
        second = await self.coordinator.async_refresh()
        self.assertTrue(first["refresh_successful"])
        self.assertTrue(second["refresh_successful"])
        self.assertIs(self.runtime.measurement_state, state)
        self.assertEqual(first["selected_uric_acid_value_mg_dl"], second["selected_uric_acid_value_mg_dl"])
        self.assertEqual(self.closed, 2)
        self.assertEqual(notified.call_count, 2)

    async def test_later_failures_retain_last_valid_measurement(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.assertTrue((await self.coordinator.async_refresh())["refresh_successful"])
        previous = self.runtime.measurement_state.latest
        previous_sync = self.runtime.synchronized_at
        for failure in ("connect", "subscribe", 4):
            with self.subTest(failure=failure):
                self.requests.clear()
                self.prepare(["uric_general", "hct_qc_invalid"])
                self.fail_at = failure
                result = await self.coordinator.async_refresh()
                self.assertFalse(result["sensor_updated"])
                self.assertTrue(result["retained_previous_state"])
                self.assertIs(self.runtime.measurement_state.latest, previous)
                self.assertIs(self.runtime.synchronized_at, previous_sync)
        self.fail_at = None
        for count in (0, 1, 3, 5):
            with self.subTest(count=count):
                self.prepare([], count)
                result = await self.coordinator.async_refresh()
                self.assertEqual(result["error_code"], "unsupported_history_count")
                self.assertIs(self.runtime.measurement_state.latest, previous)
                self.assertIs(self.runtime.synchronized_at, previous_sync)

    async def test_two_entries_have_independent_state_and_locks(self):
        other_mac = "aa:bb:cc:dd:ee:02"  # Synthetic fixture only.
        other_runtime = self.modules["sensor_state"].MeterRuntime(address=other_mac.upper())
        other_entry = types.SimpleNamespace(unique_id=other_mac)
        other = self.c.Fora6CurrentRefreshCoordinator(object(), other_entry, other_runtime)
        entered, release = asyncio.Event(), asyncio.Event()
        original_connect = self.c.Fora6BluetoothTransport.async_connect

        async def held_first_connect(transport):
            if transport._address == MAC.upper():
                entered.set()
                await release.wait()
            await original_connect(transport)

        self.prepare(["uric_general", "hct_qc_invalid"])
        with patch.object(self.c.Fora6BluetoothTransport, "async_connect", held_first_connect):
            first = asyncio.create_task(self.coordinator.async_refresh())
            await entered.wait()
            self.prepare(["future_time", "hct_qc_invalid"])
            second_result = await other.async_refresh()
            self.assertTrue(second_result["refresh_successful"])
            self.assertIsNone(self.runtime.measurement_state.native_value)
            self.assertEqual(str(other_runtime.measurement_state.native_value), "0.2")
            self.prepare(["uric_general", "hct_qc_invalid"])
            release.set()
            self.assertTrue((await first)["refresh_successful"])
        self.assertEqual(str(self.runtime.measurement_state.native_value), "123.4")
        self.assertEqual(str(other_runtime.measurement_state.native_value), "0.2")

    async def test_private_result_and_no_automation(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        result = await self.coordinator.async_refresh()
        serialized = json.dumps(result)
        self.assertNotIn(MAC, serialized)
        self.assertNotIn(MAC.upper(), serialized)
        for forbidden in ("serial", "system_id", "raw_value", "raw_frame", "hash", "digest", "payload"):
            self.assertNotIn(forbidden, serialized)
        source = (ROOT / "coordinator.py").read_text()
        for forbidden in ("0x2F", "0x33", "0x50", "async_create_task", "async_track_time_interval", "DataUpdateCoordinator", "recorder", "statistics", "logger", "logging"):
            self.assertNotIn(forbidden, source)

    async def test_malformed_metadata_and_record_stop(self):
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.responses[2] = self.p.ProtocolFrame(frame(0x25, b"\x02\x00\x01\x00"))
        result = await self.coordinator.async_refresh()
        self.assertEqual(result["error_code"], "invalid_response")
        self.assertEqual(len(self.requests), 3)
        self.requests.clear()
        self.prepare(["uric_general", "hct_qc_invalid"])
        self.responses[3] = self.p.ProtocolFrame(frame(0x26, b"\x00\x00\x00\x00"))
        result = await self.coordinator.async_refresh()
        self.assertEqual(result["error_code"], "invalid_response")
        self.assertEqual(len(self.requests), 4)
        self.assertIsNone(self.runtime.measurement_state.native_value)

    async def test_concurrent_call_rejected_without_second_session(self):
        entered, release = asyncio.Event(), asyncio.Event()
        transport_class = self.c.Fora6BluetoothTransport
        original_connect = transport_class.async_connect

        async def held_connect(transport):
            entered.set()
            await release.wait()
            await original_connect(transport)

        self.prepare(["uric_general", "hct_qc_invalid"])
        with patch.object(transport_class, "async_connect", held_connect):
            first = asyncio.create_task(self.coordinator.async_refresh())
            await entered.wait()
            second = await self.coordinator.async_refresh()
            self.assertEqual(second["error_code"], "already_running")
            release.set()
            self.assertTrue((await first)["refresh_successful"])
        self.assertEqual(self.closed, 1)

    async def test_cancellation_cleans_up_and_does_not_publish(self):
        entered = asyncio.Event()

        async def blocked_connect(_transport):
            entered.set()
            await asyncio.Event().wait()

        self.prepare(["uric_general", "hct_qc_invalid"])
        with patch.object(self.c.Fora6BluetoothTransport, "async_connect", blocked_connect):
            task = asyncio.create_task(self.coordinator.async_refresh())
            await entered.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertEqual(self.closed, 1)
        self.assertIsNone(self.runtime.measurement_state.native_value)


class ManualActionTests(unittest.IsolatedAsyncioTestCase):
    async def test_action_targets_loaded_config_entry_without_address_input(self):
        probe, _, _ = _load_probe()
        integration, _, _, exceptions = _load_setup(probe)
        coordinator = types.SimpleNamespace(async_refresh=AsyncMock(return_value={"refresh_successful": True}))
        entry = types.SimpleNamespace(
            domain="fora6_connect", runtime_data=types.SimpleNamespace(refresh_coordinator=coordinator)
        )
        hass = types.SimpleNamespace(
            services=types.SimpleNamespace(async_register=Mock()),
            config_entries=types.SimpleNamespace(async_get_entry=Mock(return_value=entry)),
        )
        await integration.async_setup(hass, {})
        registration = _registered_action(hass.services, "refresh_current_uric_acid")
        handler = registration.args[2]
        result = await handler(types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"}))
        self.assertEqual(result, {"refresh_successful": True})
        hass.config_entries.async_get_entry.assert_called_once_with("synthetic-entry")
        coordinator.async_refresh.assert_awaited_once()
        with self.assertRaises(exceptions.ServiceValidationError):
            await handler(types.SimpleNamespace(data={"address": MAC}))
        entry.domain = "other_integration"
        with self.assertRaises(exceptions.ServiceValidationError):
            await handler(types.SimpleNamespace(data={"config_entry_id": "synthetic-entry"}))


if __name__ == "__main__":
    unittest.main()
