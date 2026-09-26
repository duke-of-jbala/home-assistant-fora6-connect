"""FORA 6 Connect development-only Home Assistant entry point."""

import asyncio

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError

from .const import DOMAIN
from .gatt_probe import ProbeError, async_probe_gatt

SERVICE_PROBE_GATT = "probe_gatt"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the manually invoked Stage 1B read-only probe."""
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
    return True
