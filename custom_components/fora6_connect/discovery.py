"""Passive FORA candidate checks; an advertisement never proves identity."""

from __future__ import annotations

from typing import Any

EXPECTED_NAME = "FORA 6 CONNECT"
GLUCOSE_UUID = "00001808-0000-1000-8000-00805f9b34fb"
DEVICE_INFORMATION_UUID = "0000180a-0000-1000-8000-00805f9b34fb"


def normalized_local_name(name: str | None) -> str | None:
    """Remove only the observed trailing NUL advertisement padding."""
    return name.rstrip("\x00") if isinstance(name, str) else None


def _full_uuid(value: str) -> str:
    value = value.lower()
    if len(value) == 4:
        return f"0000{value}-0000-1000-8000-00805f9b34fb"
    return value


def is_fora_candidate(info: Any) -> bool:
    """Require the observed name, both services and connectability only."""
    try:
        advertisement = getattr(info, "advertisement", None)
        advertised_name = getattr(advertisement, "local_name", None)
        name = advertised_name if advertised_name is not None else info.name
        uuids = {_full_uuid(str(value)) for value in info.service_uuids}
        return (
            normalized_local_name(name) == EXPECTED_NAME
            and info.connectable is True
            and {GLUCOSE_UUID, DEVICE_INFORMATION_UUID} <= uuids
        )
    except (AttributeError, TypeError, ValueError):
        return False
