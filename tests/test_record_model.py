"""Offline combined-record tests using entirely synthetic TD4183 pairs."""

import ast
import importlib.util
import sys
import types
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from fixtures_td4183 import (
    SYNTHETIC_CASES,
    build_synthetic_pair,
    invalid_time_frame,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "custom_components" / "fora6_connect"
PACKAGE_NAME = "fora6_stage3_offline"
package = types.ModuleType(PACKAGE_NAME)
package.__path__ = [str(PACKAGE_DIR)]
sys.modules[PACKAGE_NAME] = package


def load_offline_module(name: str):
    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE_NAME}.{name}", PACKAGE_DIR / f"{name}.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


protocol = load_offline_module("protocol")
models = load_offline_module("models")
CASES = {case.name: case for case in SYNTHETIC_CASES}


def combined(name: str):
    first_frame, second_frame = build_synthetic_pair(CASES[name], protocol)
    return models.combine_td4183_record(
        protocol.parse_td4183_record_part_one(first_frame),
        protocol.parse_td4183_record_part_two(second_frame),
    )


class Stage3RecordModelTests(unittest.TestCase):
    def test_all_fixtures_are_distinct_valid_synthetic_frames(self) -> None:
        self.assertEqual(len(SYNTHETIC_CASES), 10)
        self.assertEqual(len(CASES), len(SYNTHETIC_CASES))
        pairs = [build_synthetic_pair(case, protocol) for case in SYNTHETIC_CASES]
        self.assertEqual(len({(a.data, b.data) for a, b in pairs}), len(pairs))
        for first, second in pairs:
            self.assertEqual((first.command_id, second.command_id), (0x25, 0x26))
            self.assertEqual((first.marker, second.marker), (0xA5, 0xA5))
            self.assertTrue(protocol.has_valid_checksum(first.data))
            self.assertTrue(protocol.has_valid_checksum(second.data))
            models.combine_td4183_record(
                protocol.parse_td4183_record_part_one(first),
                protocol.parse_td4183_record_part_two(second),
            )

    def test_valid_uric_record_preserves_supported_fields(self) -> None:
        record = combined("uric_general")
        self.assertIsInstance(record, models.TD4183Record)
        self.assertEqual(record.meter_local_time.as_naive_datetime(), datetime(2037, 10, 14, 9, 42))
        self.assertIsNone(record.meter_local_time.as_naive_datetime().tzinfo)
        self.assertTrue(record.transmitted)
        self.assertIs(record.analyte, protocol.TD4183Analyte.URIC_ACID)
        self.assertEqual(record.analyte_code, 8)
        self.assertIs(record.category, protocol.TD4183RecordCategory.GENERAL)
        self.assertEqual(record.raw_value, 1234)
        self.assertEqual(record.usable_raw_value, 1234)
        self.assertTrue(record.is_valid_value)
        self.assertEqual(record.auxiliary_byte, 17)
        self.assertEqual(record.app_code_number, 33)  # Overlaps analyte bits.
        self.assertEqual(record.uric_acid_scaled_value, Decimal("123.4"))
        self.assertFalse(record.is_qc)

    def test_transmitted_false_and_minimum_time(self) -> None:
        record = combined("minimum_time")
        self.assertFalse(record.transmitted)
        self.assertEqual(record.meter_local_time.as_naive_datetime(), datetime(2000, 1, 1))

    def test_future_time_remains_naive(self) -> None:
        local = combined("future_time").meter_local_time.as_naive_datetime()
        self.assertEqual(local, datetime(2099, 12, 31, 23, 59))
        self.assertIsNone(local.tzinfo)

    def test_uric_acid_qc_kept_distinct_without_exclusion_policy(self) -> None:
        record = combined("uric_qc")
        self.assertTrue(record.is_qc)
        self.assertTrue(record.is_valid_value)
        self.assertEqual(record.uric_acid_scaled_value, Decimal("432.1"))

    def test_invalid_sentinel_is_never_usable_or_scaled(self) -> None:
        for name in ("hct_qc_invalid", "uric_invalid"):
            with self.subTest(name=name):
                record = combined(name)
                self.assertEqual(record.raw_value, 0xFFFF)
                self.assertFalse(record.is_valid_value)
                self.assertIsNone(record.usable_raw_value)
                self.assertIsNone(record.uric_acid_scaled_value)
        self.assertTrue(combined("hct_qc_invalid").is_qc)

    def test_other_known_analyte_has_no_uric_scaling(self) -> None:
        record = combined("ketone_general")
        self.assertIs(record.analyte, protocol.TD4183Analyte.KETONE)
        self.assertTrue(record.is_valid_value)
        self.assertIsNone(record.uric_acid_scaled_value)

    def test_unknown_selector_stays_unknown(self) -> None:
        record = combined("unknown_type")
        self.assertEqual(record.analyte_code, 10)
        self.assertIsNone(record.analyte)
        self.assertIsNone(record.uric_acid_scaled_value)

    def test_ac_and_pc_remain_distinct(self) -> None:
        self.assertIs(combined("ac").category, protocol.TD4183RecordCategory.AC)
        self.assertIs(combined("pc").category, protocol.TD4183RecordCategory.PC)
        self.assertFalse(combined("ac").is_qc)
        self.assertFalse(combined("pc").is_qc)

    def test_invalid_calendar_input_fails_before_combination(self) -> None:
        bad = invalid_time_frame(protocol)
        self.assertTrue(protocol.has_valid_checksum(bad.data))
        with self.assertRaises(protocol.FrameError):
            protocol.parse_td4183_record_part_one(bad)

    def test_combination_rejects_wrong_part_types(self) -> None:
        first, second = build_synthetic_pair(CASES["uric_general"], protocol)
        part_one = protocol.parse_td4183_record_part_one(first)
        part_two = protocol.parse_td4183_record_part_two(second)
        for left, right in ((part_two, part_one), (first, part_two), (part_one, second)):
            with self.subTest(left=type(left).__name__, right=type(right).__name__):
                with self.assertRaises(TypeError):
                    models.combine_td4183_record(left, right)

    def test_parts_and_opaque_bytes_are_retained_but_not_represented(self) -> None:
        record = combined("uric_general")
        self.assertEqual(len(record.part_one.raw_payload), 4)
        self.assertEqual(len(record.part_two.raw_payload), 4)
        self.assertNotIn("1234", repr(record))
        self.assertNotIn("2037", repr(record))
        self.assertNotIn("raw_payload", repr(record))

    def test_model_and_protocol_imports_are_ha_and_bleak_independent(self) -> None:
        for name in ("protocol", "models"):
            tree = ast.parse((PACKAGE_DIR / f"{name}.py").read_text())
            imports = [
                node.module or ""
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
            ]
            imports += [
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            ]
            for imported in imports:
                self.assertFalse(imported.startswith(("homeassistant", "bleak", "esphome", "bluetooth")))


if __name__ == "__main__":
    unittest.main()
