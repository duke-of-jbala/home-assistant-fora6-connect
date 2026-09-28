"""Development-only one-attempt custom-notification readiness probe.

This stops before every FORA application command. Unsolicited notification
payloads are discarded by the shared transport and never leave the session.
"""

import asyncio
import re
from typing import Any

from homeassistant.core import HomeAssistant

from .bluetooth import Fora6BluetoothTransport, TransportError


def _safe_exception_type(error: Exception) -> str:
    name = type(error).__name__
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", name) else "Exception"


async def async_probe_transaction_readiness(
    hass: HomeAssistant, address: str
) -> dict[str, Any]:
    """Resolve, connect once, subscribe once, then clean up without a write."""
    transport = Fora6BluetoothTransport(hass, address, connect_max_attempts=1)
    result: dict[str, Any] = {
        "probe_performed": True,
        "connectable_device_resolved": False,
        "connection_attempted": False,
        "connection_successful": False,
        "custom_service_found": False,
        "custom_characteristic_found": False,
        "notification_subscription_attempted": False,
        "notification_subscription_successful": False,
        "cleanup_successful": False,
        "cleanup_errors": [],
        "failure_stage": None,
        "failure_code": None,
        "exception_type": None,
    }
    try:
        await transport.async_connect()
        result["notification_subscription_attempted"] = True
        await transport.async_subscribe()
    except asyncio.CancelledError:
        raise
    except TransportError as error:
        if error.stage == "resolution":
            stage = "device_resolution"
        elif error.stage == "connection":
            stage = "connection"
        elif error.stage == "gatt":
            stage = "characteristic_lookup" if transport.service_found else "service_discovery"
        elif error.stage == "subscription":
            stage = "notification_subscription"
        else:
            stage = "probe"
        result.update(failure_stage=stage, failure_code=error.code)
    except Exception as error:
        result.update(
            failure_stage="probe",
            failure_code="unexpected_failure",
            exception_type=_safe_exception_type(error),
        )
    finally:
        result.update(
            connectable_device_resolved=transport.device_resolved,
            connection_attempted=transport.device_resolved,
            connection_successful=transport.connection_established,
            custom_service_found=transport.service_found,
            custom_characteristic_found=transport.characteristic_found,
            notification_subscription_successful=transport.subscription_established,
        )
        try:
            cleanup = await transport.async_close()
            result["cleanup_errors"] = list(cleanup.errors)
            result["cleanup_successful"] = (
                not cleanup.errors
                and (not transport.connection_established or cleanup.disconnected_cleanly)
                and (not transport.subscription_established or cleanup.notification_stopped_cleanly)
            )
        except Exception:
            result["cleanup_errors"] = ["cleanup_failed"]
        if not result["cleanup_successful"] and result["failure_stage"] is None:
            result.update(failure_stage="cleanup", failure_code="cleanup_failed")
    return result
