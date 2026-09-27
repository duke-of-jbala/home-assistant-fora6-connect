"""Bounded model confirmation and private, read-only meter identity."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .bluetooth import Fora6BluetoothTransport, TransportError
from .protocol import (
    build_project_query_request,
    build_wake_request,
    parse_project_id,
)
from .serial_probe import _async_read_serial_private

EXPECTED_PROJECT_ID = 0x4183


class SetupIdentityError(Exception):
    """One privacy-safe Config Flow reason, never a device identifier."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


async def async_confirm_meter_identity(hass: HomeAssistant, address: str) -> str:
    """Confirm GD82 project, close the session, then read exact UTF-8 serial."""
    transport = Fora6BluetoothTransport(hass, address)
    failure: str | None = None
    try:
        await transport.async_connect()
        await transport.async_subscribe()
        await transport.async_exchange(build_wake_request())
        response = await transport.async_exchange(build_project_query_request())
        if parse_project_id(response) != EXPECTED_PROJECT_ID:
            failure = "not_fora6_connect"
    except TransportError as exc:
        failure = "cannot_connect" if exc.stage in ("resolution", "connection") else "identity_failed"
    except Exception:
        failure = "identity_failed"
    finally:
        cleanup = await transport.async_close()
    if failure is not None:
        raise SetupIdentityError(failure)
    if not cleanup.notification_stopped_cleanly or not cleanup.disconnected_cleanly or cleanup.errors:
        raise SetupIdentityError("identity_failed")

    result, raw = await _async_read_serial_private(hass, address)
    if raw is None or not result["serial_value_usable"] or not result["disconnected_cleanly"]:
        raise SetupIdentityError("serial_unavailable")
    # Validation above checks printable, nonblank UTF-8. Do not normalize.
    return raw.decode("utf-8")
