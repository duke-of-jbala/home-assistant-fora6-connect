"""Offline GD82 frame primitives supported by the sanitized Stage 2C evidence.

This module has no Home Assistant or Bluetooth dependency. Constructing a frame
here never transmits it; live FORA writes require a separately authorized gate.
"""

from dataclasses import dataclass, field
from decimal import Decimal

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


def scale_td4183_uric_acid(raw_value: int) -> Decimal:
    """Scale an already identified TD4183 uric-acid raw value by ten.

    This does not locate a field in a record or identify an analyte. The
    0x25/0x26 record byte layout remains unpublished in sanitized evidence.
    """
    if isinstance(raw_value, bool) or not isinstance(raw_value, int) or raw_value < 0:
        raise ValueError("A uric-acid raw value must be a nonnegative integer.")
    return Decimal(raw_value) / Decimal(10)
