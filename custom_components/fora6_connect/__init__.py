"""FORA 6 Connect development-only Home Assistant entry point."""

import asyncio

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError

from .const import DOMAIN
from .gatt_probe import ProbeError, async_probe_gatt
from .notification_observer import ObservationError, async_observe_notifications
from .protocol_probe import async_probe_protocol_identity, async_probe_protocol_record

SERVICE_PROBE_GATT = "probe_gatt"
SERVICE_OBSERVE_NOTIFICATIONS = "observe_notifications"
SERVICE_PROBE_PROTOCOL_IDENTITY = "probe_protocol_identity"
SERVICE_PROBE_PROTOCOL_RECORD = "probe_protocol_record"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the manually invoked development-only Bluetooth actions."""
    probe_lock = asyncio.Lock()

    async def async_handle_probe_gatt(call: ServiceCall) -> dict:
        """Return sanitized GATT evidence or a sanitized service error."""
        if probe_lock.locked():
            raise ServiceValidationError("A FORA GATT probe is already running.")
        address = call.data.get("address")
        if not isinstance(address, str) or not address.strip():
            raise ServiceValidationError(
                "A Bluetooth address is required for this development probe."
            )
        try:
            async with probe_lock:
                return await async_probe_gatt(hass, address.strip())
        except ProbeError as err:
            raise ServiceValidationError(str(err)) from None
        except Exception:
            raise ServiceValidationError(
                "FORA GATT probe failed; inspect private Home Assistant diagnostics."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_GATT,
        async_handle_probe_gatt,
        supports_response=SupportsResponse.ONLY,
    )

    async def async_handle_observe_notifications(call: ServiceCall) -> dict:
        """Return notification metadata without private payloads or identifiers."""
        if probe_lock.locked():
            raise ServiceValidationError(
                "A FORA development action is already running."
            )
        address = call.data.get("address")
        if not isinstance(address, str) or not address.strip():
            raise ServiceValidationError(
                "A Bluetooth address is required for this development action."
            )
        try:
            async with probe_lock:
                return await async_observe_notifications(hass, address.strip())
        except ObservationError as err:
            raise ServiceValidationError(str(err)) from None
        except Exception:
            raise ServiceValidationError(
                "FORA notification observation failed; "
                "inspect private Home Assistant diagnostics."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_OBSERVE_NOTIFICATIONS,
        async_handle_observe_notifications,
        supports_response=SupportsResponse.ONLY,
    )

    async def async_handle_probe_protocol_identity(call: ServiceCall) -> dict:
        """Return only bounded, sanitized wake/project identity status."""
        if probe_lock.locked():
            raise ServiceValidationError(
                "A FORA development action is already running."
            )
        address = call.data.get("address")
        if not isinstance(address, str) or not address.strip():
            raise ServiceValidationError(
                "A Bluetooth address is required for this development action."
            )
        try:
            async with probe_lock:
                return await async_probe_protocol_identity(hass, address.strip())
        except Exception:
            raise ServiceValidationError(
                "FORA identity probe failed; inspect private Home Assistant "
                "diagnostics."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_PROTOCOL_IDENTITY,
        async_handle_probe_protocol_identity,
        supports_response=SupportsResponse.ONLY,
    )

    async def async_handle_probe_protocol_record(call: ServiceCall) -> dict:
        """Return only sanitized status for one current-user raw slot."""
        if probe_lock.locked():
            raise ServiceValidationError(
                "A FORA development action is already running."
            )
        address = call.data.get("address")
        if not isinstance(address, str) or not address.strip():
            raise ServiceValidationError(
                "A Bluetooth address is required for this development action."
            )
        try:
            async with probe_lock:
                return await async_probe_protocol_record(hass, address.strip())
        except Exception:
            raise ServiceValidationError(
                "FORA record probe failed; inspect private Home Assistant "
                "diagnostics."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_PROTOCOL_RECORD,
        async_handle_probe_protocol_record,
        supports_response=SupportsResponse.ONLY,
    )
    return True
