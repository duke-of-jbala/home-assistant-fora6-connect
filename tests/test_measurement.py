"""Synthetic-only tests for the Stage 5 product and entity boundary."""

import ast
import importlib.util
import sys
import types
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from fixtures_td4183 import SYNTHETIC_CASES, SyntheticRecordCase, build_synthetic_pair


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "custom_components" / "fora6_connect"
PACKAGE_NAME = "fora6_stage5_measurement"
package = types.ModuleType(PACKAGE_NAME)
package.__path__ = [str(PACKAGE_DIR)]
sys.modules[PACKAGE_NAME] = package


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE_NAME}.{name}", PACKAGE_DIR / f"{name}.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


const = load_module("const")
protocol = load_module("protocol")
record_models = load_module("models")
measurement = load_module("measurement")
sensor = load_module("sensor_state")
CASES = {case.name: case for case in SYNTHETIC_CASES}


def record_for(case: SyntheticRecordCase):
    first, second = build_synthetic_pair(case, protocol)
    return record_models.combine_td4183_record(
        protocol.parse_td4183_record_part_one(first),
        protocol.parse_td4183_record_part_two(second),
    )


def fixture_record(name: str):
    return record_for(CASES[name])


class ProductMeasurementTests(unittest.TestCase):
    def test_uric_acid_maps_with_evidenced_base_unit(self) -> None:
        product = measurement.measurement_from_record(fixture_record("uric_general"))
        self.assertIs(product.analyte, protocol.TD4183Analyte.URIC_ACID)
        self.assertEqual(product.scaled_number, Decimal("123.4"))
        self.assertEqual(product.unit, "mg/dL")
        self.assertEqual(sensor.measurement_native_value(product), Decimal("123.4"))
        self.assertIs(
            product.value_status,
            measurement.MeasurementValueStatus.VALID_URIC_ACID,
        )
        self.assertFalse(hasattr(product, "raw_value"))

    def test_only_identified_uric_acid_gets_numeric_scaling(self) -> None:
        for analyte in protocol.TD4183Analyte:
            case = SyntheticRecordCase(
                f"synthetic_{analyte.name.lower()}",
                2041,
                6,
                7,
                8,
                9,
                False,
                1000,
                int(analyte),
                0,
            )
            with self.subTest(analyte=analyte.name):
                product = measurement.measurement_from_record(record_for(case))
                if analyte is protocol.TD4183Analyte.URIC_ACID:
                    self.assertEqual(product.scaled_number, Decimal("100"))
                else:
                    self.assertIsNone(product.scaled_number)
                    self.assertIs(
                        product.value_status,
                        measurement.MeasurementValueStatus.UNSUPPORTED_ANALYTE_SCALING,
                    )

    def test_invalid_sentinel_has_no_product_or_sensor_value(self) -> None:
        record = fixture_record("uric_invalid")
        self.assertEqual(record.raw_value, 0xFFFF)
        product = measurement.measurement_from_record(record)
        self.assertIsNone(product.scaled_number)
        self.assertIsNone(sensor.measurement_native_value(product))
        self.assertIs(
            product.value_status,
            measurement.MeasurementValueStatus.INVALID_RAW_VALUE,
        )

    def test_other_known_analyte_and_unknown_selector_are_not_numeric(self) -> None:
        known = measurement.measurement_from_record(fixture_record("ketone_general"))
        unknown = measurement.measurement_from_record(fixture_record("unknown_type"))
        self.assertIs(known.analyte, protocol.TD4183Analyte.KETONE)
        self.assertIsNone(known.scaled_number)
        self.assertIsNone(sensor.measurement_native_value(known))
        self.assertIsNone(unknown.analyte)
        self.assertIsNone(unknown.scaled_number)
        self.assertIs(
            unknown.value_status,
            measurement.MeasurementValueStatus.UNKNOWN_ANALYTE,
        )

    def test_qc_category_is_preserved_without_extra_interpretation(self) -> None:
        product = measurement.measurement_from_record(fixture_record("uric_qc"))
        self.assertIs(product.category, protocol.TD4183RecordCategory.QC)
        self.assertTrue(product.is_qc)
        self.assertFalse(hasattr(product, "is_control_solution"))
        self.assertIsNone(sensor.measurement_native_value(product))

    def test_ac_and_pc_remain_distinct_and_not_sensor_states(self) -> None:
        ac = measurement.measurement_from_record(fixture_record("ac"))
        pc = measurement.measurement_from_record(fixture_record("pc"))
        self.assertIs(ac.category, protocol.TD4183RecordCategory.AC)
        self.assertIs(pc.category, protocol.TD4183RecordCategory.PC)
        self.assertIsNone(sensor.measurement_native_value(ac))
        self.assertIsNone(sensor.measurement_native_value(pc))

    def test_meter_time_is_naive_and_transmitted_is_preserved(self) -> None:
        product = measurement.measurement_from_record(fixture_record("uric_general"))
        self.assertEqual(product.meter_local_time, datetime(2037, 10, 14, 9, 42))
        self.assertIsNone(product.meter_local_time.tzinfo)
        self.assertEqual(product.meter_local_time.second, 0)
        self.assertTrue(product.transmitted)
        self.assertFalse(
            measurement.measurement_from_record(
                fixture_record("minimum_time")
            ).transmitted
        )

    def test_unsupported_unit_cannot_be_invented(self) -> None:
        product = measurement.measurement_from_record(fixture_record("uric_general"))
        self.assertEqual(product.unit, "mg/dL")
        for unsupported_unit in ("", "µmol/L", "mmol/L"):
            with self.subTest(unit=unsupported_unit), self.assertRaises(ValueError):
                measurement.Fora6Measurement(
                    analyte=product.analyte,
                    scaled_number=product.scaled_number,
                    category=product.category,
                    transmitted=product.transmitted,
                    meter_local_time=product.meter_local_time,
                    value_status=product.value_status,
                    unit=unsupported_unit,
                )
        with self.assertRaises(FrozenInstanceError):
            product.unit = ""

    def test_invalid_status_cannot_carry_a_numeric_number(self) -> None:
        product = measurement.measurement_from_record(fixture_record("uric_general"))
        with self.assertRaises(ValueError):
            measurement.Fora6Measurement(
                analyte=protocol.TD4183Analyte.KETONE,
                scaled_number=Decimal("1"),
                category=protocol.TD4183RecordCategory.GENERAL,
                transmitted=False,
                meter_local_time=product.meter_local_time,
                value_status=(
                    measurement.MeasurementValueStatus.UNSUPPORTED_ANALYTE_SCALING
                ),
            )

    def test_measurement_is_immutable_and_repr_hides_number_and_time(self) -> None:
        product = measurement.measurement_from_record(fixture_record("uric_general"))
        self.assertNotIn("123.4", repr(product))
        self.assertNotIn("2037", repr(product))
        self.assertNotIn("scaled_number", repr(product))


class SensorBoundaryTests(unittest.TestCase):
    def test_latest_invalid_record_replaces_previous_measurement(self) -> None:
        state = sensor.MeasurementState()
        state.replace(
            measurement.measurement_from_record(fixture_record("uric_general"))
        )
        self.assertEqual(state.native_value, Decimal("123.4"))
        invalid = measurement.measurement_from_record(fixture_record("uric_invalid"))
        state.replace(invalid)
        self.assertIs(state.latest, invalid)
        self.assertIsNone(state.native_value)
        state.replace(None)
        self.assertIsNone(state.latest)
        self.assertIsNone(state.native_value)

    def test_qc_input_clears_normal_numeric_state(self) -> None:
        state = sensor.MeasurementState()
        state.replace(
            measurement.measurement_from_record(fixture_record("uric_general"))
        )
        self.assertEqual(state.native_value, Decimal("123.4"))
        state.replace(measurement.measurement_from_record(fixture_record("uric_qc")))
        self.assertIsNone(state.native_value)

    def test_shared_device_identifier_uses_stage6_identity_input(self) -> None:
        stable_identity = "stage6-synthetic-meter-01"
        first_entity_device = sensor.meter_device_identifier(stable_identity)
        second_entity_device = sensor.meter_device_identifier(stable_identity)
        self.assertEqual(first_entity_device, second_entity_device)
        self.assertEqual(first_entity_device, (const.DOMAIN, stable_identity))
        self.assertNotIn("address", first_entity_device[1].lower())
        with self.assertRaises(ValueError):
            sensor.meter_device_identifier(" ")

    def test_sensor_layer_is_inert_and_has_no_transport_imports(self) -> None:
        tree = ast.parse((PACKAGE_DIR / "sensor_state.py").read_text())
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
        self.assertFalse(
            any(
                name.startswith(("homeassistant", "bleak", "esphome"))
                for name in imports
            )
        )
        source = (PACKAGE_DIR / "sensor_state.py").read_text()
        self.assertNotIn("SensorEntity", source)
        for token in (
            "establish_connection",
            "async_ble_device_from_address",
            "write_gatt_char",
            "start_notify",
        ):
            self.assertNotIn(token, source)
        self.assertNotIn("async_update", source)

    def test_protocol_and_wire_model_remain_home_assistant_independent(self) -> None:
        for name in ("protocol.py", "models.py", "measurement.py"):
            tree = ast.parse((PACKAGE_DIR / name).read_text())
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
            self.assertFalse(
                any(
                    value.startswith(("homeassistant", "bleak", "esphome", "bluetooth"))
                    for value in imports
                )
            )

    def test_existing_fixtures_remain_synthetic_only(self) -> None:
        self.assertEqual(len(SYNTHETIC_CASES), 10)
        prefixes = ("uric", "ketone", "hct", "unknown", "ac", "pc", "minimum", "future")
        self.assertTrue(
            all(case.name.startswith(prefixes) for case in SYNTHETIC_CASES)
        )


if __name__ == "__main__":
    unittest.main()
