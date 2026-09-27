"""Development-only, process-local comparison of private serial reads."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .serial_probe import _async_read_serial_private, _empty_result

STATE_KEY = "serial_stability"
SET_REFERENCE = "set_reference"
COMPARE = "compare"


class PrivateSerialReference:
    """Exactly one process-local serial; never render its value in repr."""

    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self._value: bytes | None = None

    def __repr__(self) -> str:
        return "<PrivateSerialReference>"


def _state(hass: HomeAssistant) -> PrivateSerialReference:
    """Use integration runtime memory, never an entry or persistent store."""
    integration_data = hass.data.setdefault(DOMAIN, {})
    return integration_data.setdefault(STATE_KEY, PrivateSerialReference())


async def async_probe_serial_stability(
    hass: HomeAssistant, address: str, operation: str
) -> dict[str, Any]:
    """Set or compare an exact private 0x2A25 byte sequence."""
    state = _state(hass)
    async with state.lock:
        if operation not in (SET_REFERENCE, COMPARE):
            result = _empty_result()
            result["error_stage"] = "comparison"
            result["error_code"] = "invalid_operation"
        elif operation == COMPARE and state._value is None:
            # A missing reference is known without connecting to the meter.
            result = _empty_result()
            result["error_stage"] = "comparison"
            result["error_code"] = "no_reference"
        else:
            result, private_value = await _async_read_serial_private(hass, address)
            if result["error_code"] is None and private_value is None:
                result["error_stage"] = "comparison"
                result["error_code"] = "unusable_serial"
            if result["error_code"] is None and private_value is not None:
                if operation == SET_REFERENCE:
                    # No await between successful cleanup and atomic replacement.
                    state._value = private_value
                else:
                    result["serial_matches_reference"] = private_value == state._value

        result["reference_set"] = (
            operation == SET_REFERENCE
            and result["error_code"] is None
            and state._value is not None
        )
        result["reference_available"] = state._value is not None
        result.setdefault("serial_matches_reference", None)
        return result
