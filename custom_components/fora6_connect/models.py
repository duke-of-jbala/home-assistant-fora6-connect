"""Offline TD4183 record model; no Home Assistant or transport dependency.

This is a pair of already validated protocol parts, not a synchronized
measurement or a Home Assistant entity. No meter timezone or unit is known.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from .protocol import (
    MeterLocalTimestamp,
    TD4183Analyte,
    TD4183RecordCategory,
    TD4183RecordPartOne,
    TD4183RecordPartTwo,
    scale_td4183_uric_acid,
)


@dataclass(frozen=True, slots=True, repr=False)
class TD4183Record:
    """One paired 0x25/0x26 record, retaining both parts and opaque bits."""

    part_one: TD4183RecordPartOne = field(repr=False)
    part_two: TD4183RecordPartTwo = field(repr=False)

    def __post_init__(self) -> None:
        # Each parser checked its command, response marker, frame, and checksum.
        # The wire evidence establishes pairing, but no cross-part constraint.
        if not isinstance(self.part_one, TD4183RecordPartOne):
            raise TypeError("Expected a parsed 0x25 TD4183 record part.")
        if not isinstance(self.part_two, TD4183RecordPartTwo):
            raise TypeError("Expected a parsed 0x26 TD4183 record part.")

    @property
    def meter_local_time(self) -> MeterLocalTimestamp:
        return self.part_one.meter_local_time

    @property
    def transmitted(self) -> bool:
        return self.part_one.transmitted

    @property
    def analyte_code(self) -> int:
        return self.part_two.analyte_code

    @property
    def analyte(self) -> TD4183Analyte | None:
        return self.part_two.analyte

    @property
    def category(self) -> TD4183RecordCategory:
        return self.part_two.category

    @property
    def raw_value(self) -> int:
        """Preserve the wire integer, including invalid 0xFFFF."""
        return self.part_two.raw_value

    @property
    def is_valid_value(self) -> bool:
        return not self.part_two.invalid_raw_value

    @property
    def usable_raw_value(self) -> int | None:
        """Return no numeric measurement for the invalid wire sentinel."""
        return self.raw_value if self.is_valid_value else None

    @property
    def auxiliary_byte(self) -> int:
        """Preserve byte 4 without assigning a physical meaning or unit."""
        return self.part_two.auxiliary_value

    @property
    def app_code_number(self) -> int:
        """Preserve the app's overlapping byte-5 low-six-bit field."""
        return self.part_two.code_number

    @property
    def is_qc(self) -> bool:
        return self.category is TD4183RecordCategory.QC

    @property
    def uric_acid_scaled_value(self) -> Decimal | None:
        """Apply the evidenced /10 rule only to valid, identified uric acid."""
        if self.analyte is not TD4183Analyte.URIC_ACID or not self.is_valid_value:
            return None
        return scale_td4183_uric_acid(self.raw_value)


def combine_td4183_record(
    part_one: TD4183RecordPartOne, part_two: TD4183RecordPartTwo
) -> TD4183Record:
    """Combine parts already validated by their command-specific parsers."""
    return TD4183Record(part_one, part_two)
