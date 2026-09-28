"""Shared, evidence-bounded User1 record read for counts two and four."""

from dataclasses import dataclass
from typing import Any

from .bluetooth import TransportError
from .models import TD4183Record, combine_td4183_record
from .protocol import (
    FrameError,
    ProtocolFrame,
    TD4183Analyte,
    TD4183RecordCategory,
    build_first_record_part_one_request,
    build_first_record_part_two_request,
    build_second_record_part_one_request,
    build_second_record_part_two_request,
    build_third_record_part_one_request,
    build_third_record_part_two_request,
    build_fourth_record_part_one_request,
    build_fourth_record_part_two_request,
    build_project_query_request,
    build_record_slot_count_request,
    build_wake_request,
    parse_project_id,
    parse_record_newest_index,
    parse_record_slot_count,
    parse_td4183_record_part_one,
    parse_td4183_record_part_two,
)

PROJECT_ID = 0x4183
RESPONSE_TIMEOUT = 15.0
REQUEST_PAIRS = (
    (build_first_record_part_one_request, build_first_record_part_two_request),
    (build_second_record_part_one_request, build_second_record_part_two_request),
    (build_third_record_part_one_request, build_third_record_part_two_request),
    (build_fourth_record_part_one_request, build_fourth_record_part_two_request),
)


class BoundedReadError(Exception):
    """Stable operational stage/code, never a protocol payload or health value."""

    def __init__(self, stage: str, code: str) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code


@dataclass(slots=True)
class BoundedReadProgress:
    """Volatile structural progress available when a read fails."""

    project_confirmed: bool = False
    raw_slot_count: int | None = None
    supported_raw_slot_count: bool = False


def eligible_primary(record: TD4183Record) -> bool:
    """Apply the existing ordinary General uric-acid primary gate."""
    return (
        record.analyte is TD4183Analyte.URIC_ACID
        and record.category is TD4183RecordCategory.GENERAL
        and record.is_valid_value
        and not record.is_qc
    )


def validate_companions(records: tuple[TD4183Record, ...]) -> None:
    """Require the already observed odd-slot QC-invalid companion shape."""
    for index in range(1, len(records), 2):
        companion = records[index]
        if (
            companion.category is not TD4183RecordCategory.QC
            or companion.is_valid_value
        ):
            raise BoundedReadError("record", "unexpected_companion")


async def async_read_bounded_records(
    transport: Any, progress: BoundedReadProgress
) -> tuple[TD4183Record, ...]:
    """Use only the established wake/project/count and fixed 0x25/0x26 plans.

    The caller owns connect, notification subscription, and cleanup. No result
    is returned until every required record part has parsed successfully.
    """

    async def exchange(request: ProtocolFrame, stage: str) -> ProtocolFrame:
        try:
            return await transport.async_exchange(request)
        except TransportError as failure:
            raise BoundedReadError(stage, failure.code) from None

    await exchange(build_wake_request(), "wake")
    project_frame = await exchange(build_project_query_request(), "project")
    try:
        project = parse_project_id(project_frame)
    except FrameError:
        raise BoundedReadError("project", "invalid_response") from None
    if project != PROJECT_ID:
        raise BoundedReadError("project", "unexpected_project_id")
    progress.project_confirmed = True

    metadata = await exchange(build_record_slot_count_request(), "metadata")
    try:
        count = parse_record_slot_count(metadata)
        parse_record_newest_index(metadata)
    except FrameError:
        raise BoundedReadError("metadata", "invalid_response") from None
    progress.raw_slot_count = count
    if count not in (2, 4):
        raise BoundedReadError("metadata", "unsupported_history_count")
    progress.supported_raw_slot_count = True

    records = []
    for first_builder, second_builder in REQUEST_PAIRS[:count]:
        first = await exchange(first_builder(), "record_part_1")
        try:
            part_one = parse_td4183_record_part_one(first)
        except FrameError:
            raise BoundedReadError("record_part_1", "invalid_response") from None
        second = await exchange(second_builder(), "record_part_2")
        try:
            part_two = parse_td4183_record_part_two(second)
        except FrameError:
            raise BoundedReadError("record_part_2", "invalid_response") from None
        records.append(combine_td4183_record(part_one, part_two))
    return tuple(records)
