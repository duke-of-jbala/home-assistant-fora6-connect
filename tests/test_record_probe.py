"""Hardware-free Stage 2F single-slot probe tests with artificial frames."""

import json
import logging
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

from test_protocol_probe import (
    PROJECT_REQUEST,
    PROJECT_RESPONSE,
    WAKE_REQUEST,
    WAKE_RESPONSE,
    _load_probe,
)


def _synthetic_response(command: int, data: bytes = b"\x00\x00\x00\x00") -> bytes:
    """Make an artificial checksum-valid frame; it is not a captured record."""
    first_seven = bytes((0x51, command)) + data + b"\xA5"
    return first_seven + bytes((sum(first_seven) & 0xFF,))


COUNT_REQUEST = bytes.fromhex("51 2B 00 00 00 00 A3 1F")
PART_ONE_REQUEST = bytes.fromhex("51 25 00 00 00 00 A3 19")
PART_TWO_REQUEST = bytes.fromhex("51 26 00 00 00 00 A3 1A")
COUNT_RESPONSE = _synthetic_response(0x2B, b"\x01\x00\x00\x00")
PART_ONE_RESPONSE = _synthetic_response(0x25)
PART_TWO_RESPONSE = _synthetic_response(0x26)
EXPECTED_REQUESTS = (
    WAKE_REQUEST,
    PROJECT_REQUEST,
    COUNT_REQUEST,
    PART_ONE_REQUEST,
    PART_TWO_REQUEST,
)


class RecordProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.probe, self.bluetooth, self.connector = _load_probe()
        self.hass = object()
        self.address = "synthetic-private-address"
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.characteristic = types.SimpleNamespace(
            uuid=self.probe.CHARACTERISTIC_UUID, properties=("write", "notify")
        )
        self.responses = {
            0x22: WAKE_RESPONSE,
            0x24: PROJECT_RESPONSE,
            0x2B: COUNT_RESPONSE,
            0x25: PART_ONE_RESPONSE,
            0x26: PART_TWO_RESPONSE,
        }
        self.write_error_command = None
        self.callback = None
        self.events = []
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[
                types.SimpleNamespace(
                    uuid=self.probe.SERVICE_UUID,
                    characteristics=[self.characteristic],
                )
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
        self.events.append(data[1])
        if data[1] == self.write_error_command:
            raise RuntimeError(self.address)
        reply = self.responses.get(data[1])
        if reply is not None:
            self.callback(characteristic, bytearray(reply))

    async def _stop(self, characteristic):
        self.events.append("unsubscribe")

    async def _disconnect(self):
        self.events.append("disconnect")

    async def run_probe(self):
        return await self.probe.async_probe_protocol_record(self.hass, self.address)

    def assert_private_boundary(self, result):
        public = json.dumps(result)
        self.assertNotIn(self.address, public)
        for payload in self.responses.values():
            if payload is not None:
                self.assertNotIn(payload.hex(), public.lower())
                self.assertNotIn(payload.hex(" "), public.lower())
        self.assertNotIn("measurement_value", public)
        self.assertNotIn("measurement_timestamp", public)
        self.client.read_gatt_char.assert_not_awaited()
        self.client.write_gatt_descriptor.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        for call in self.client.start_notify.call_args_list:
            self.assertEqual(call.args[0].uuid, self.probe.CHARACTERISTIC_UUID)
        for call in self.client.write_gatt_char.call_args_list:
            self.assertIn(call.args[1], EXPECTED_REQUESTS)
            self.assertIs(call.kwargs["response"], True)
            self.assertEqual(call.args[0].uuid, self.probe.CHARACTERISTIC_UUID)

    def assert_cleanup(self):
        self.client.stop_notify.assert_awaited_once_with(self.characteristic)
        self.client.disconnect.assert_awaited_once()

    async def test_one_slot_success_and_exact_write_order(self):
        result = await self.run_probe()
        self.assertEqual(
            [call.args[1] for call in self.client.write_gatt_char.call_args_list],
            list(EXPECTED_REQUESTS),
        )
        self.assertEqual(
            self.events,
            ["subscribe", 0x22, 0x24, 0x2B, 0x25, 0x26, "unsubscribe", "disconnect"],
        )
        self.assertTrue(result["identity_confirmed"])
        self.assertTrue(result["record_metadata_response_valid"])
        self.assertTrue(result["record_part_1_valid"])
        self.assertTrue(result["record_part_2_valid"])
        self.assertTrue(result["record_pair_complete"])
        self.assertTrue(result["record_retrieval_confirmed"])
        self.assertEqual(result["requested_record_index"], 0)
        self.assertFalse(result["analyte_identified"])
        self.assertIsNone(result["analyte_type"])
        self.assertFalse(result["measurement_field_decoded"])
        self.assertFalse(result["uric_acid_scaling_applied"])
        self.assertEqual(result["cleanup_errors"], [])
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_other_project_stops_before_record_request(self):
        self.responses[0x24] = _synthetic_response(0x24, b"\x84\x41\x04\x00")
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "unexpected_project_id")
        self.assertEqual(self.client.write_gatt_char.await_count, 2)
        self.assertFalse(result["record_metadata_query_performed"])
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_record_count_zero_stops_before_index(self):
        self.responses[0x2B] = _synthetic_response(0x2B)
        result = await self.run_probe()
        self.assertEqual(result["error_code"], "no_record_slots")
        self.assertTrue(result["record_metadata_response_valid"])
        self.assertIsNone(result["requested_record_index"])
        self.assertEqual(self.client.write_gatt_char.await_count, 3)
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_metadata_timeout(self):
        self.responses[0x2B] = None
        await self._assert_stage_failure("metadata", "response_timeout", 3)

    async def test_metadata_invalid_checksum(self):
        self.responses[0x2B] = COUNT_RESPONSE[:-1] + b"\x00"
        await self._assert_stage_failure("metadata", "invalid_response", 3)

    async def test_metadata_wrong_command(self):
        self.responses[0x2B] = PART_ONE_RESPONSE
        await self._assert_stage_failure("metadata", "invalid_response", 3)

    async def test_part_one_timeout(self):
        self.responses[0x25] = None
        await self._assert_stage_failure("record_part_1", "response_timeout", 4)

    async def test_part_one_invalid_checksum(self):
        self.responses[0x25] = PART_ONE_RESPONSE[:-1] + b"\x00"
        await self._assert_stage_failure("record_part_1", "invalid_response", 4)

    async def test_part_one_wrong_command(self):
        self.responses[0x25] = PART_TWO_RESPONSE
        await self._assert_stage_failure("record_part_1", "invalid_response", 4)

    async def test_part_one_wrong_length(self):
        self.responses[0x25] = PART_ONE_RESPONSE[:-1]
        await self._assert_stage_failure("record_part_1", "invalid_response", 4)

    async def test_part_two_timeout(self):
        self.responses[0x26] = None
        await self._assert_stage_failure("record_part_2", "response_timeout", 5)

    async def test_part_two_invalid_checksum(self):
        self.responses[0x26] = PART_TWO_RESPONSE[:-1] + b"\x00"
        await self._assert_stage_failure("record_part_2", "invalid_response", 5)

    async def test_part_two_wrong_command(self):
        self.responses[0x26] = PART_ONE_RESPONSE
        await self._assert_stage_failure("record_part_2", "invalid_response", 5)

    async def test_part_two_wrong_marker(self):
        first_seven = PART_TWO_RESPONSE[:6] + b"\xA3"
        self.responses[0x26] = first_seven + bytes((sum(first_seven) & 0xFF,))
        await self._assert_stage_failure("record_part_2", "invalid_response", 5)

    async def test_metadata_write_failure_has_no_retry(self):
        self.write_error_command = 0x2B
        await self._assert_stage_failure("metadata", "write_failed", 3)

    async def test_part_one_write_failure_has_no_retry(self):
        self.write_error_command = 0x25
        await self._assert_stage_failure("record_part_1", "write_failed", 4)

    async def test_part_two_write_failure_has_no_retry(self):
        self.write_error_command = 0x26
        await self._assert_stage_failure("record_part_2", "write_failed", 5)

    async def _assert_stage_failure(self, stage, code, write_count):
        result = await self.run_probe()
        self.assertEqual(result["error_stage"], stage)
        self.assertEqual(result["error_code"], code)
        self.assertEqual(self.client.write_gatt_char.await_count, write_count)
        self.assertEqual(
            [call.args[1] for call in self.client.write_gatt_char.call_args_list],
            list(EXPECTED_REQUESTS[:write_count]),
        )
        self.assertTrue(result["identity_confirmed"])
        self.assertFalse(result["record_retrieval_confirmed"])
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_private_record_payload_and_exception_never_escape(self):
        # Deliberately artificial sensitive-looking data; no real record fixture.
        self.responses[0x26] = b"synthetic-sensitive-record"
        with patch.object(logging.Logger, "_log") as logs:
            result = await self.run_probe()
        self.assertEqual(result["error_code"], "invalid_response")
        public = json.dumps(result)
        self.assertNotIn("synthetic-sensitive-record", public)
        self.assertNotIn(self.address, public)
        self.assertNotIn("synthetic-sensitive-record", str(logs.call_args_list))
        self.assertNotIn(self.address, str(logs.call_args_list))
        self.assert_cleanup()
        self.assert_private_boundary(result)

    async def test_cleanup_failure_does_not_claim_retrieval(self):
        self.client.stop_notify.side_effect = RuntimeError(self.address)
        result = await self.run_probe()
        self.assertTrue(result["record_pair_complete"])
        self.assertFalse(result["record_retrieval_confirmed"])
        self.assertEqual(result["cleanup_errors"], ["notification_stop_failed"])
        self.client.disconnect.assert_awaited_once()
        self.assert_private_boundary(result)


if __name__ == "__main__":
    unittest.main()
