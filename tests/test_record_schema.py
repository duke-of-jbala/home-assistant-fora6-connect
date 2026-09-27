"""Synthetic TD4183 record-schema fixtures; no private capture bytes or results."""

import importlib.util
import sys
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "custom_components" / "fora6_connect" / "protocol.py"
SPEC = importlib.util.spec_from_file_location(
    "fora6_record_schema_under_test", PROTOCOL
)
assert SPEC is not None and SPEC.loader is not None
protocol = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = protocol
SPEC.loader.exec_module(protocol)


def synthetic_response(command: int, payload: bytes, marker: int = 0xA5):
    """Make an artificial frame without a real health measurement or date."""
    assert len(payload) == 4
    head = bytes((0x51, command)) + payload + bytes((marker,))
    return protocol.ProtocolFrame(head + bytes((protocol.checksum_for(head),)))


class TD4183PartOneTests(unittest.TestCase):
    # Artificial future time: 2031-10-14 09:42; never a captured meter time.
    SYNTHETIC_TIME = bytes.fromhex("4E 3F 2A 49")

    def test_packed_meter_local_time_and_transmit_flag(self) -> None:
        part = protocol.parse_td4183_record_part_one(
            synthetic_response(0x25, self.SYNTHETIC_TIME)
        )
        self.assertEqual(
            (
                part.meter_local_time.year,
                part.meter_local_time.month,
                part.meter_local_time.day,
                part.meter_local_time.hour,
                part.meter_local_time.minute,
            ),
            (2031, 10, 14, 9, 42),
        )
        self.assertTrue(part.transmitted)
        self.assertEqual(part.raw_payload, self.SYNTHETIC_TIME)
        local = part.meter_local_time.as_naive_datetime()
        self.assertEqual(local, datetime(2031, 10, 14, 9, 42))
        self.assertIsNone(local.tzinfo)
        self.assertEqual(local.second, 0)  # Minute precision, not a meter second.

    def test_uninterpreted_bits_remain_opaque(self) -> None:
        payload = bytes.fromhex("4E 3F AA E9")
        part = protocol.parse_td4183_record_part_one(
            synthetic_response(0x25, payload)
        )
        self.assertEqual(part.raw_payload, payload)
        self.assertEqual(part.meter_local_time.minute, 42)
        self.assertEqual(part.meter_local_time.hour, 9)
        self.assertTrue(part.transmitted)
        self.assertNotIn("2031", repr(part))
        self.assertNotIn("2031", repr(part.meter_local_time))

    def test_wrong_command_or_request_marker_rejected(self) -> None:
        for frame in (
            synthetic_response(0x26, self.SYNTHETIC_TIME),
            synthetic_response(0x25, self.SYNTHETIC_TIME, 0xA3),
        ):
            with self.subTest(frame=frame), self.assertRaises(protocol.FrameError):
                protocol.parse_td4183_record_part_one(frame)

    def test_bad_checksum_or_length_rejected(self) -> None:
        valid = synthetic_response(0x25, self.SYNTHETIC_TIME).data
        for malformed in (valid[:-1], valid + b"\x00", valid[:-1] + b"\x00"):
            with self.subTest(length=len(malformed)):
                with self.assertRaises(protocol.FrameError):
                    protocol.ProtocolFrame(malformed)

    def test_invalid_date_and_time_rejected_without_normalizing(self) -> None:
        invalid_payloads = (
            bytes.fromhex("0E 3E 2A 09"),  # Month zero.
            bytes.fromhex("40 3F 2A 09"),  # Day zero.
            bytes.fromhex("4E 3F 3F 09"),  # Minute 63.
            bytes.fromhex("4E 3F 2A 1F"),  # Hour 31.
            bytes.fromhex("5E 3E 2A 09"),  # February 30.
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(protocol.FrameError):
                protocol.parse_td4183_record_part_one(
                    synthetic_response(0x25, payload)
                )
        # A valid boundary remains accepted; invalid encodings are not sentinels.
        protocol.parse_td4183_record_part_one(
            synthetic_response(0x25, bytes.fromhex("5E 3F 2A 09"))
        )


class TD4183PartTwoTests(unittest.TestCase):
    def test_uric_acid_raw_value_and_conditional_scaling(self) -> None:
        # Artificial raw value 73 and wire type 8; neither comes from a meter.
        part = protocol.parse_td4183_record_part_two(
            synthetic_response(0x26, bytes.fromhex("49 00 11 20"))
        )
        self.assertEqual(part.raw_value, 73)
        self.assertEqual(part.analyte_code, 8)
        self.assertIs(part.analyte, protocol.TD4183Analyte.URIC_ACID)
        self.assertIs(part.category, protocol.TD4183RecordCategory.GENERAL)
        self.assertEqual(part.auxiliary_value, 17)
        self.assertEqual(part.code_number, 32)
        self.assertFalse(part.invalid_raw_value)
        self.assertFalse(part.is_qc)
        self.assertEqual(
            protocol.scale_td4183_uric_acid(part.raw_value), Decimal("7.3")
        )
        self.assertNotIn("73", repr(part))

    def test_qc_category_and_invalid_raw_sentinel(self) -> None:
        part = protocol.parse_td4183_record_part_two(
            synthetic_response(0x26, bytes.fromhex("FF FF 00 D8"))
        )
        self.assertIs(part.analyte, protocol.TD4183Analyte.HEMATOCRIT)
        self.assertIs(part.category, protocol.TD4183RecordCategory.QC)
        self.assertTrue(part.is_qc)
        self.assertTrue(part.invalid_raw_value)
        with self.assertRaises(ValueError):
            protocol.scale_td4183_uric_acid(part.raw_value)

    def test_category_bits_remain_distinct(self) -> None:
        for high_bits, expected in (
            (0x00, protocol.TD4183RecordCategory.GENERAL),
            (0x40, protocol.TD4183RecordCategory.AC),
            (0x80, protocol.TD4183RecordCategory.PC),
            (0xC0, protocol.TD4183RecordCategory.QC),
        ):
            with self.subTest(category=expected):
                part = protocol.parse_td4183_record_part_two(
                    synthetic_response(0x26, bytes((1, 0, 0, 0x20 | high_bits)))
                )
                self.assertIs(part.category, expected)
                self.assertEqual(
                    part.is_qc,
                    expected is protocol.TD4183RecordCategory.QC,
                )

    def test_supported_wire_type_selectors(self) -> None:
        for code, expected in (
            (0, protocol.TD4183Analyte.GENERAL),
            (6, protocol.TD4183Analyte.HEMATOCRIT),
            (7, protocol.TD4183Analyte.KETONE),
            (8, protocol.TD4183Analyte.URIC_ACID),
            (9, protocol.TD4183Analyte.CHOLESTEROL),
            (11, protocol.TD4183Analyte.HEMOGLOBIN),
            (12, protocol.TD4183Analyte.LACTATE),
            (13, protocol.TD4183Analyte.TRIGLYCERIDE),
        ):
            with self.subTest(code=code):
                part = protocol.parse_td4183_record_part_two(
                    synthetic_response(0x26, bytes((1, 0, 0, code << 2)))
                )
                self.assertIs(part.analyte, expected)

    def test_unsupported_wire_type_stays_unidentified(self) -> None:
        part = protocol.parse_td4183_record_part_two(
            synthetic_response(0x26, bytes((1, 0, 0, 10 << 2)))
        )
        self.assertEqual(part.analyte_code, 10)
        self.assertIsNone(part.analyte)

    def test_wrong_command_marker_checksum_and_length_rejected(self) -> None:
        payload = bytes.fromhex("49 00 11 20")
        for frame in (
            synthetic_response(0x25, payload),
            synthetic_response(0x26, payload, 0xA3),
        ):
            with self.subTest(frame=frame), self.assertRaises(protocol.FrameError):
                protocol.parse_td4183_record_part_two(frame)
        valid = synthetic_response(0x26, payload).data
        for malformed in (valid[:-1], valid + b"\x00", valid[:-1] + b"\x00"):
            with self.subTest(length=len(malformed)):
                with self.assertRaises(protocol.FrameError):
                    protocol.ProtocolFrame(malformed)

    def test_scaling_rejects_invalid_raw_values(self) -> None:
        for raw in (-1, 0xFFFF, True, 1.5):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                protocol.scale_td4183_uric_acid(raw)


if __name__ == "__main__":
    unittest.main()
