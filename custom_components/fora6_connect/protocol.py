"""Offline GD82 frame and TD4183 record primitives backed by captured evidence.

This module has no Home Assistant or Bluetooth dependency. Constructing a frame
here never transmits it; live FORA writes require a separately authorized gate.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import IntEnum

FRAME_LENGTH = 8
FRAME_PREFIX = 0x51
REQUEST_MARKER = 0xA3
RESPONSE_MARKER = 0xA5
WAKE_COMMAND = 0x22
PROJECT_QUERY_COMMAND = 0x24
RECORD_SLOT_COUNT_COMMAND = 0x2B
RECORD_PART_ONE_COMMAND = 0x25
RECORD_PART_TWO_COMMAND = 0x26
USER_ONE_SELECTOR = 0x01


class FrameError(ValueError):
    """An observed-format GD82 frame is malformed or used in the wrong role."""


class TD4183Analyte(IntEnum):
    """Wire type selectors in 0x26 byte 5 bits 2–5, as mapped by both apps."""

    GENERAL = 0
    HEMATOCRIT = 6
    KETONE = 7
    URIC_ACID = 8
    CHOLESTEROL = 9
    HEMOGLOBIN = 11
    LACTATE = 12
    TRIGLYCERIDE = 13


class TD4183RecordCategory(IntEnum):
    """The app's symbolic 0x26 byte 5 bits 6–7 categories."""

    GENERAL = 0
    AC = 1
    PC = 2
    QC = 3


@dataclass(frozen=True, slots=True, repr=False)
class MeterLocalTimestamp:
    """Meter wall-clock fields, with minute precision and unknown timezone."""

    year: int
    month: int
    day: int
    hour: int
    minute: int

    def __post_init__(self) -> None:
        try:
            datetime(self.year, self.month, self.day, self.hour, self.minute)
        except ValueError as exc:
            raise FrameError("Invalid TD4183 meter-local date or time.") from exc

    def as_naive_datetime(self) -> datetime:
        """Represent the minute-precision fields without attaching a timezone."""
        return datetime(self.year, self.month, self.day, self.hour, self.minute)


@dataclass(frozen=True, slots=True)
class TD4183RecordPartOne:
    """Decoded 0x25 fields; uninterpreted payload bits remain available."""

    meter_local_time: MeterLocalTimestamp = field(repr=False)
    transmitted: bool
    raw_payload: bytes = field(repr=False)


@dataclass(frozen=True, slots=True)
class TD4183RecordPartTwo:
    """Decoded 0x26 fields, without assigning a unit or scaled value."""

    raw_value: int = field(repr=False)
    analyte_code: int
    analyte: TD4183Analyte | None
    category: TD4183RecordCategory
    auxiliary_value: int = field(repr=False)
    code_number: int = field(repr=False)
    invalid_raw_value: bool
    raw_payload: bytes = field(repr=False)

    @property
    def is_control_solution(self) -> bool:
        """The app's QC category is distinct from general measurements."""
        return self.category is TD4183RecordCategory.QC


def checksum_for(first_seven_bytes: bytes) -> int:
    """Return the live-confirmed modulo-256 sum for seven frame bytes."""
    if len(first_seven_bytes) != FRAME_LENGTH - 1:
        raise FrameError("A checksum requires exactly seven frame bytes.")
    return sum(first_seven_bytes) & 0xFF


def has_valid_checksum(frame_bytes: bytes) -> bool:
    """Check byte 7 of an eight-byte frame without assigning payload semantics."""
    if len(frame_bytes) != FRAME_LENGTH:
        raise FrameError("A GD82 frame must contain exactly eight bytes.")
    return frame_bytes[-1] == checksum_for(frame_bytes[:-1])


@dataclass(frozen=True, slots=True)
class ProtocolFrame:
    """Validated, immutable observed-format request or response frame."""

    data: bytes = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.data, (bytes, bytearray, memoryview)):
            raise TypeError("Frame data must be bytes-like.")
        data = bytes(self.data)
        object.__setattr__(self, "data", data)
        if len(data) != FRAME_LENGTH:
            raise FrameError("A GD82 frame must contain exactly eight bytes.")
        if data[0] != FRAME_PREFIX:
            raise FrameError("Unexpected GD82 frame prefix.")
        if data[6] not in (REQUEST_MARKER, RESPONSE_MARKER):
            raise FrameError("Unexpected GD82 frame marker.")
        if not has_valid_checksum(data):
            raise FrameError("Invalid GD82 frame checksum.")

    def __repr__(self) -> str:
        """Keep command metadata visible without exposing a future private payload."""
        return (
            f"ProtocolFrame(command_id=0x{self.command_id:02X}, "
            f"marker=0x{self.marker:02X})"
        )

    @property
    def command_id(self) -> int:
        """Command identifier at byte 1, echoed by observed responses."""
        return self.data[1]

    @property
    def marker(self) -> int:
        """Observed request/response marker at byte 6."""
        return self.data[6]

    @property
    def opaque_data(self) -> bytes:
        """Return command-specific bytes 2–5 without interpreting them."""
        return self.data[2:6]

    def require_request(self) -> None:
        """Reject a response frame where a request is required."""
        if self.marker != REQUEST_MARKER:
            raise FrameError("Expected a GD82 request frame.")

    def require_response(self) -> None:
        """Reject a request frame where a response is required."""
        if self.marker != RESPONSE_MARKER:
            raise FrameError("Expected a GD82 response frame.")


def _build_confirmed_request(command_id: int) -> ProtocolFrame:
    """Build only the two exact zero-data requests seen in Stage 2C."""
    if command_id not in (WAKE_COMMAND, PROJECT_QUERY_COMMAND):
        raise FrameError("Only confirmed Stage 2C requests can be constructed.")
    first_seven = bytes((FRAME_PREFIX, command_id, 0, 0, 0, 0, REQUEST_MARKER))
    return ProtocolFrame(first_seven + bytes((checksum_for(first_seven),)))


def build_wake_request() -> ProtocolFrame:
    """Construct the observed 0x22 wake request, without transmitting it."""
    return _build_confirmed_request(WAKE_COMMAND)


def build_project_query_request() -> ProtocolFrame:
    """Construct the observed 0x24 project query, without transmitting it."""
    return _build_confirmed_request(PROJECT_QUERY_COMMAND)


def _build_static_record_request(command_id: int) -> ProtocolFrame:
    """Build only the read-oriented User1, raw-index-zero app requests.

    Both app builders encode the User1 enum value directly: byte 2 in the
    0x2B query and byte 5 in indexed 0x25/0x26 requests. The Stage 2C wire
    requests corroborate these exact forms. This does not decode record data.
    """
    if command_id not in (
        RECORD_SLOT_COUNT_COMMAND,
        RECORD_PART_ONE_COMMAND,
        RECORD_PART_TWO_COMMAND,
    ):
        raise FrameError("Unsupported Stage 2F record request.")
    if command_id == RECORD_SLOT_COUNT_COMMAND:
        parameters = (USER_ONE_SELECTOR, 0, 0, 0)
    else:
        parameters = (0, 0, 0, USER_ONE_SELECTOR)
    first_seven = bytes((FRAME_PREFIX, command_id, *parameters, REQUEST_MARKER))
    return ProtocolFrame(first_seven + bytes((checksum_for(first_seven),)))


def build_record_slot_count_request() -> ProtocolFrame:
    """Build the statically traced 0x2B User1 slot query."""
    return _build_static_record_request(RECORD_SLOT_COUNT_COMMAND)


def build_first_record_part_one_request() -> ProtocolFrame:
    """Build the statically traced 0x25 query for raw index zero only."""
    return _build_static_record_request(RECORD_PART_ONE_COMMAND)


def build_first_record_part_two_request() -> ProtocolFrame:
    """Build the statically traced 0x26 query for raw index zero only."""
    return _build_static_record_request(RECORD_PART_TWO_COMMAND)


def validate_response_echo(request: ProtocolFrame, response: ProtocolFrame) -> None:
    """Validate the request/response roles and observed command-ID echo."""
    request.require_request()
    response.require_response()
    if response.command_id != request.command_id:
        raise FrameError("GD82 response command does not match the request.")


def parse_project_id(response: ProtocolFrame) -> int:
    """Extract the little-endian project ID from a validated 0x24 response."""
    response.require_response()
    if response.command_id != PROJECT_QUERY_COMMAND:
        raise FrameError("Expected a GD82 project-query response.")
    return int.from_bytes(response.data[2:4], "little")


def parse_record_slot_count(response: ProtocolFrame) -> int:
    """Extract raw storage slots from a validated 0x2B response.

    The TD4183 app may reinterpret this count for multi-parameter records.
    This value is not a logical measurement count or analyte identifier.
    """
    response.require_response()
    if response.command_id != RECORD_SLOT_COUNT_COMMAND:
        raise FrameError("Expected a GD82 record-slot response.")
    return int.from_bytes(response.data[2:4], "little")


def parse_td4183_record_part_one(response: ProtocolFrame) -> TD4183RecordPartOne:
    """Decode the app's 0x25 packed meter-local minute and transmit flag.

    The source app converts these fields through the phone's default timezone.
    A meter timezone is not supplied, so this parser retains wall-clock fields.
    Invalid calendar fields are rejected instead of adopting Java Calendar's
    lenient normalization. Other payload bits remain opaque.
    """
    response.require_response()
    if response.command_id != RECORD_PART_ONE_COMMAND:
        raise FrameError("Expected a TD4183 record-part-one response.")
    day_and_month = response.data[2]
    month_and_year = response.data[3]
    minute_and_flags = response.data[4]
    hour_and_flags = response.data[5]
    meter_local_time = MeterLocalTimestamp(
        year=2000 + (month_and_year >> 1),
        month=(day_and_month >> 5) + ((month_and_year & 1) << 3),
        day=day_and_month & 0x1F,
        hour=hour_and_flags & 0x1F,
        minute=minute_and_flags & 0x3F,
    )
    return TD4183RecordPartOne(
        meter_local_time=meter_local_time,
        transmitted=bool(hour_and_flags & 0x40),
        raw_payload=response.opaque_data,
    )


def parse_td4183_record_part_two(response: ProtocolFrame) -> TD4183RecordPartTwo:
    """Decode the app's 0x26 raw value, type selector, and record category.

    The app calls byte 4 an ambient value and byte 5 low six bits a code
    number. Neither has a verified unit; code-number bits overlap the type.
    Unknown analyte codes stay numeric and cannot become uric acid by context.
    """
    response.require_response()
    if response.command_id != RECORD_PART_TWO_COMMAND:
        raise FrameError("Expected a TD4183 record-part-two response.")
    raw_value = int.from_bytes(response.data[2:4], "little")
    type_and_category = response.data[5]
    analyte_code = (type_and_category & 0x3C) >> 2
    try:
        analyte = TD4183Analyte(analyte_code)
    except ValueError:
        analyte = None
    return TD4183RecordPartTwo(
        raw_value=raw_value,
        analyte_code=analyte_code,
        analyte=analyte,
        category=TD4183RecordCategory(type_and_category >> 6),
        auxiliary_value=response.data[4],
        code_number=type_and_category & 0x3F,
        invalid_raw_value=raw_value == 0xFFFF,
        raw_payload=response.opaque_data,
    )


def scale_td4183_uric_acid(raw_value: int) -> Decimal:
    """Scale an already identified TD4183 uric-acid raw value by ten.

    Call only after the 0x26 type field identifies uric acid and the raw
    value is not the app's 0xFFFF invalid sentinel. The helper itself remains
    contextual and does not identify an analyte or attach a unit.
    """
    if (
        isinstance(raw_value, bool)
        or not isinstance(raw_value, int)
        or raw_value < 0
        or raw_value >= 0xFFFF
    ):
        raise ValueError("A uric-acid raw value must be a valid 16-bit reading.")
    return Decimal(raw_value) / Decimal(10)
