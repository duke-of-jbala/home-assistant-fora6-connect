"""SYNTHETIC TD4183 record pairs; no captured GD82 response is stored here.

The builder preserves only evidenced command IDs, field packing, response
marker, modulo-256 checksum, selector/category bits, and 0xFFFF sentinel.
Dates and numbers are artificial. Passing the pure protocol module avoids
importing the Home Assistant integration package in offline tests.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SyntheticRecordCase:
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    transmitted: bool
    raw_value: int
    analyte_code: int
    category: int
    auxiliary_byte: int = 0
    low_code_bits: int = 0


SYNTHETIC_CASES = (
    SyntheticRecordCase("uric_general", 2037, 10, 14, 9, 42, True, 1234, 8, 0, 17, 1),
    SyntheticRecordCase("uric_qc", 2037, 10, 15, 9, 43, False, 4321, 8, 3),
    SyntheticRecordCase("ketone_general", 2037, 11, 16, 10, 44, False, 2468, 7, 0),
    SyntheticRecordCase("hct_qc_invalid", 2037, 11, 17, 10, 45, True, 0xFFFF, 6, 3),
    SyntheticRecordCase("unknown_type", 2037, 12, 18, 11, 46, False, 777, 10, 0),
    SyntheticRecordCase("ac", 2037, 12, 19, 11, 47, False, 888, 8, 1),
    SyntheticRecordCase("pc", 2037, 12, 20, 11, 48, True, 999, 8, 2),
    SyntheticRecordCase("minimum_time", 2000, 1, 1, 0, 0, False, 1, 8, 0),
    SyntheticRecordCase("future_time", 2099, 12, 31, 23, 59, True, 2, 8, 0),
    SyntheticRecordCase("uric_invalid", 2037, 10, 21, 12, 49, False, 0xFFFF, 8, 0),
)


def _response(protocol, command: int, payload: bytes):
    head = bytes((0x51, command)) + payload + b"\xA5"
    return protocol.ProtocolFrame(head + bytes((protocol.checksum_for(head),)))


def build_synthetic_pair(case: SyntheticRecordCase, protocol):
    """Build two artificial checksummed responses for one named case."""
    assert 2000 <= case.year <= 2127
    assert 0 <= case.analyte_code <= 15
    assert 0 <= case.category <= 3
    assert 0 <= case.low_code_bits <= 3
    year_bits = case.year - 2000
    part_one_payload = bytes((
        case.day | ((case.month & 7) << 5),
        (year_bits << 1) | (case.month >> 3),
        case.minute,
        case.hour | (0x40 if case.transmitted else 0),
    ))
    part_two_payload = (
        case.raw_value.to_bytes(2, "little")
        + bytes((case.auxiliary_byte, (case.category << 6) | (case.analyte_code << 2) | case.low_code_bits))
    )
    return _response(protocol, 0x25, part_one_payload), _response(protocol, 0x26, part_two_payload)


def invalid_time_frame(protocol):
    """Artificial month-zero response, with a correct frame checksum."""
    return _response(protocol, 0x25, bytes((1, 0, 30, 12)))
