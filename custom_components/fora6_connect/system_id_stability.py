"""Development-only process-local comparison of private System ID reads."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .system_id_probe import _async_read_system_id_private, _empty_result

STATE_KEY = "system_id_stability"
SET_REFERENCE = "set_reference"
COMPARE = "compare"


class PrivateSystemIdReference:
    """One process-local byte sequence, with a privacy-safe repr."""

    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self._value: bytes | None = None

    def __repr__(self) -> str:
        return "<PrivateSystemIdReference>"


def _state(hass: HomeAssistant) -> PrivateSystemIdReference:
    integration_data = hass.data.setdefault(DOMAIN, {})
    return integration_data.setdefault(STATE_KEY, PrivateSystemIdReference())


async def async_probe_system_id_stability(
    hass: HomeAssistant, address: str, operation: str
) -> dict[str, Any]:
    """Set or compare an exact 0x2A23 value without exposing it."""
    state = _state(hass)
    async with state.lock:
        if operation not in (SET_REFERENCE, COMPARE):
            result = _empty_result()
            result["error_stage"] = "comparison"
            result["error_code"] = "invalid_operation"
        elif operation == COMPARE and state._value is None:
            result = _empty_result()
            result["error_stage"] = "comparison"
            result["error_code"] = "no_reference"
        else:
            result, private_value = await _async_read_system_id_private(hass, address)
            if result["error_code"] is None and private_value is None:
                result["error_stage"] = "comparison"
                result["error_code"] = "unusable_system_id"
            if result["error_code"] is None and private_value is not None:
                if operation == SET_REFERENCE:
                    state._value = private_value
                else:
                    result["system_id_matches_reference"] = private_value == state._value
        result["reference_set"] = (
            operation == SET_REFERENCE
            and result["error_code"] is None
            and state._value is not None
        )
        result["reference_available"] = state._value is not None
        result.setdefault("system_id_matches_reference", None)
        return result
