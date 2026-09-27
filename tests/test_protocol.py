"""Sanitized Stage 2C frame regression tests; no Bluetooth hardware is used."""

import ast
import importlib.util
import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "custom_components" / "fora6_connect" / "protocol.py"
SPEC = importlib.util.spec_from_file_location("fora6_protocol_under_test", PROTOCOL)
assert SPEC is not None and SPEC.loader is not None
protocol = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = protocol
SPEC.loader.exec_module(protocol)


class ProtocolBoundaryTests(unittest.TestCase):
    def test_protocol_has_no_home_assistant_or_bluetooth_dependency(self) -> None:
        source = PROTOCOL.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)

        forbidden = ("homeassistant", "bleak", "esphome", "bluetooth")
        for name in imported:
            self.assertFalse(name.startswith(forbidden), name)
        self.assertNotIn("write_gatt_char", source)


class Stage2CFrameTests(unittest.TestCase):
    """The two live exchanges contain no device identifier or health reading."""

    WAKE_REQUEST = bytes.fromhex("51 22 00 00 00 00 A3 16")
    WAKE_RESPONSE = bytes.fromhex("51 22 00 00 FF FF A5 16")
    PROJECT_REQUEST = bytes.fromhex("51 24 00 00 00 00 A3 18")
    PROJECT_RESPONSE = bytes.fromhex("51 24 83 41 04 00 A5 E2")

    def test_valid_checksum_and_marker_roles(self) -> None:
        request = protocol.ProtocolFrame(self.WAKE_REQUEST)
        response = protocol.ProtocolFrame(self.WAKE_RESPONSE)
        self.assertTrue(protocol.has_valid_checksum(request.data))
        self.assertTrue(protocol.has_valid_checksum(response.data))
        self.assertEqual(protocol.checksum_for(request.data[:7]), 0x16)
        self.assertEqual(request.marker, protocol.REQUEST_MARKER)
        self.assertEqual(response.marker, protocol.RESPONSE_MARKER)
        request.require_request()
        response.require_response()
        protocol.validate_response_echo(request, response)

    def test_invalid_checksum(self) -> None:
        corrupted = self.PROJECT_RESPONSE[:-1] + b"\x00"
        self.assertFalse(protocol.has_valid_checksum(corrupted))
        with self.assertRaises(protocol.FrameError):
            protocol.ProtocolFrame(corrupted)

    def test_invalid_length_prefix_and_marker(self) -> None:
        for data in (b"", self.WAKE_REQUEST[:-1], self.WAKE_REQUEST + b"\x00"):
            with self.subTest(length=len(data)), self.assertRaises(protocol.FrameError):
                protocol.ProtocolFrame(data)
        with self.assertRaises(protocol.FrameError):
            protocol.checksum_for(b"\x00")
        with self.assertRaises(protocol.FrameError):
            protocol.has_valid_checksum(b"\x00")
        wrong_prefix = bytes((0x52,)) + self.WAKE_REQUEST[1:7]
        with self.assertRaises(protocol.FrameError):
            protocol.ProtocolFrame(
                wrong_prefix + bytes((protocol.checksum_for(wrong_prefix),))
            )
        wrong_marker = self.WAKE_REQUEST[:6] + b"\xA4"
        with self.assertRaises(protocol.FrameError):
            protocol.ProtocolFrame(
                wrong_marker + bytes((protocol.checksum_for(wrong_marker),))
            )

    def test_command_extraction_and_response_echo(self) -> None:
        request = protocol.ProtocolFrame(self.PROJECT_REQUEST)
        response = protocol.ProtocolFrame(self.PROJECT_RESPONSE)
        self.assertEqual(request.command_id, 0x24)
        self.assertEqual(response.command_id, 0x24)
        self.assertEqual(response.opaque_data, bytes.fromhex("83 41 04 00"))
        protocol.validate_response_echo(request, response)
        with self.assertRaises(protocol.FrameError):
            response.require_request()
        with self.assertRaises(protocol.FrameError):
            request.require_response()
        with self.assertRaises(protocol.FrameError):
            protocol.validate_response_echo(
                protocol.ProtocolFrame(self.WAKE_REQUEST), response
            )

    def test_fixed_request_construction(self) -> None:
        wake = protocol.build_wake_request()
        project = protocol.build_project_query_request()
        self.assertEqual(wake.data, self.WAKE_REQUEST)
        self.assertEqual(project.data, self.PROJECT_REQUEST)
        wake.require_request()
        project.require_request()
        with self.assertRaises(protocol.FrameError):
            protocol._build_confirmed_request(0x25)

    def test_project_id_is_little_endian_0x4183(self) -> None:
        response = protocol.ProtocolFrame(self.PROJECT_RESPONSE)
        self.assertEqual(protocol.parse_project_id(response), 0x4183)
        with self.assertRaises(protocol.FrameError):
            protocol.parse_project_id(protocol.ProtocolFrame(self.PROJECT_REQUEST))
        with self.assertRaises(protocol.FrameError):
            protocol.parse_project_id(protocol.ProtocolFrame(self.WAKE_RESPONSE))

    def test_frame_owns_immutable_bytes(self) -> None:
        source = bytearray(self.WAKE_REQUEST)
        frame = protocol.ProtocolFrame(source)
        source[1] = 0
        self.assertEqual(frame.data, self.WAKE_REQUEST)
        with self.assertRaises(AttributeError):
            frame.data = b""

    def test_frame_repr_omits_payload_bytes(self) -> None:
        frame = protocol.ProtocolFrame(self.PROJECT_RESPONSE)
        self.assertIn("command_id=0x24", repr(frame))
        self.assertNotIn("83 41", repr(frame))
        self.assertNotIn("b'", repr(frame))

    def test_synthetic_uric_acid_scaling_only(self) -> None:
        # Artificial raw value; no private measurement or record payload.
        self.assertEqual(protocol.scale_td4183_uric_acid(73), Decimal("7.3"))
        for invalid in (-1, True, 1.5, "73"):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                protocol.scale_td4183_uric_acid(invalid)


class Stage2FRecordFrameTests(unittest.TestCase):
    """Static app-derived fixed requests and artificial response metadata."""

    def test_exact_current_user_index_zero_requests(self) -> None:
        expected = (
            (protocol.build_record_slot_count_request(), "51 2B 00 00 00 00 A3 1F"),
            (
                protocol.build_first_record_part_one_request(),
                "51 25 00 00 00 00 A3 19",
            ),
            (
                protocol.build_first_record_part_two_request(),
                "51 26 00 00 00 00 A3 1A",
            ),
        )
        for frame, hex_bytes in expected:
            with self.subTest(command=frame.command_id):
                self.assertEqual(frame.data, bytes.fromhex(hex_bytes))
                frame.require_request()
        with self.assertRaises(protocol.FrameError):
            protocol._build_static_record_request(0x33)
        with self.assertRaises(protocol.FrameError):
            protocol._build_static_record_request(0x50)

    def test_synthetic_raw_slot_count_only(self) -> None:
        first_seven = bytes.fromhex("51 2B 01 00 00 00 A5")
        response = protocol.ProtocolFrame(
            first_seven + bytes((protocol.checksum_for(first_seven),))
        )
        self.assertEqual(protocol.parse_record_slot_count(response), 1)
        with self.assertRaises(protocol.FrameError):
            protocol.parse_record_slot_count(protocol.build_record_slot_count_request())
        with self.assertRaises(protocol.FrameError):
            protocol.parse_record_slot_count(
                protocol.ProtocolFrame(Stage2CFrameTests.PROJECT_RESPONSE)
            )


if __name__ == "__main__":
    unittest.main()
