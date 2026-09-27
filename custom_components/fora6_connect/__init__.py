"""FORA 6 Connect setup and bounded development actions."""

import asyncio

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError

from .const import DOMAIN
from .gatt_probe import ProbeError, async_probe_gatt
from .history_probe import async_probe_history_window
from .history_semantics_probe import async_probe_history_semantics
from .notification_observer import ObservationError, async_observe_notifications
from .protocol_probe import async_probe_protocol_identity, async_probe_protocol_record
from .serial_probe import async_probe_serial_identity
from .serial_stability import async_probe_serial_stability
from .system_id_probe import async_probe_system_id
from .system_id_stability import async_probe_system_id_stability

SERVICE_PROBE_GATT = "probe_gatt"
SERVICE_OBSERVE_NOTIFICATIONS = "observe_notifications"
SERVICE_PROBE_PROTOCOL_IDENTITY = "probe_protocol_identity"
SERVICE_PROBE_PROTOCOL_RECORD = "probe_protocol_record"
SERVICE_PROBE_HISTORY_WINDOW = "probe_history_window"
SERVICE_PROBE_HISTORY_SEMANTICS = "probe_history_semantics"
SERVICE_PROBE_SERIAL_IDENTITY = "probe_serial_identity"
SERVICE_PROBE_SERIAL_STABILITY = "probe_serial_stability"
SERVICE_PROBE_SYSTEM_ID = "probe_system_id"
SERVICE_PROBE_SYSTEM_ID_STABILITY = "probe_system_id_stability"


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
        """Return only sanitized status for one User1 raw slot."""
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

    async def async_handle_probe_history_window(call: ServiceCall) -> dict:
        """Return only bounded two-slot traversal and equality status."""
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
                return await async_probe_history_window(hass, address.strip())
        except Exception:
            raise ServiceValidationError(
                "FORA history window probe failed."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_HISTORY_WINDOW,
        async_handle_probe_history_window,
        supports_response=SupportsResponse.ONLY,
    )

    async def async_handle_probe_history_semantics(call: ServiceCall) -> dict:
        """Return only the bounded pair classifications and safe status."""
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
                return await async_probe_history_semantics(hass, address.strip())
        except Exception:
            raise ServiceValidationError(
                "FORA history semantic probe failed."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_HISTORY_SEMANTICS,
        async_handle_probe_history_semantics,
        supports_response=SupportsResponse.ONLY,
    )

    async def async_handle_probe_serial_identity(call: ServiceCall) -> dict:
        """Read only Device Information 0x2A25 and return safe status."""
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
                return await async_probe_serial_identity(hass, address.strip())
        except Exception:
            raise ServiceValidationError(
                "FORA serial identity probe failed."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_SERIAL_IDENTITY,
        async_handle_probe_serial_identity,
        supports_response=SupportsResponse.ONLY,
    )

    async def async_handle_probe_serial_stability(call: ServiceCall) -> dict:
        """Set or compare one process-local private serial reference."""
        if probe_lock.locked():
            raise ServiceValidationError(
                "A FORA development action is already running."
            )
        address = call.data.get("address")
        if not isinstance(address, str) or not address.strip():
            raise ServiceValidationError(
                "A Bluetooth address is required for this development action."
            )
        operation = call.data.get("operation")
        if operation not in ("set_reference", "compare"):
            raise ServiceValidationError(
                "Choose set_reference or compare for this development action."
            )
        try:
            async with probe_lock:
                return await async_probe_serial_stability(
                    hass, address.strip(), operation
                )
        except Exception:
            raise ServiceValidationError(
                "FORA serial stability probe failed."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_SERIAL_STABILITY,
        async_handle_probe_serial_stability,
        supports_response=SupportsResponse.ONLY,
    )

    async def async_handle_probe_system_id(call: ServiceCall) -> dict:
        """Read only standard Device Information 0x2A23 once."""
        if probe_lock.locked():
            raise ServiceValidationError("A FORA development action is already running.")
        address = call.data.get("address")
        if not isinstance(address, str) or not address.strip():
            raise ServiceValidationError(
                "A Bluetooth address is required for this development action."
            )
        try:
            async with probe_lock:
                return await async_probe_system_id(hass, address.strip())
        except Exception:
            raise ServiceValidationError("FORA System ID probe failed.") from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_SYSTEM_ID,
        async_handle_probe_system_id,
        supports_response=SupportsResponse.ONLY,
    )

    async def async_handle_probe_system_id_stability(call: ServiceCall) -> dict:
        """Compare one read with a private process-local reference."""
        if probe_lock.locked():
            raise ServiceValidationError("A FORA development action is already running.")
        address = call.data.get("address")
        if not isinstance(address, str) or not address.strip():
            raise ServiceValidationError(
                "A Bluetooth address is required for this development action."
            )
        operation = call.data.get("operation")
        if operation not in ("set_reference", "compare"):
            raise ServiceValidationError(
                "Choose set_reference or compare for this development action."
            )
        try:
            async with probe_lock:
                return await async_probe_system_id_stability(
                    hass, address.strip(), operation
                )
        except Exception:
            raise ServiceValidationError(
                "FORA System ID stability probe failed."
            ) from None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PROBE_SYSTEM_ID_STABILITY,
        async_handle_probe_system_id_stability,
        supports_response=SupportsResponse.ONLY,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Create inert state and forward one sensor without connecting."""
    from .sensor_state import MeterRuntime

    if not isinstance(entry.unique_id, str) or not entry.unique_id.strip():
        return False
    address = entry.data.get("address")
    if not isinstance(address, str) or not address:
        return False
    entry.runtime_data = MeterRuntime(address=address)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    # Refresh retained registry metadata for existing entries without a BLE read.
    from .device_metadata import async_reconcile_device_metadata

    try:
        async_reconcile_device_metadata(hass, entry, address)
    except Exception:
        raise RuntimeError("FORA device metadata refresh failed") from None
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload the inert sensor platform; no transport owns a session."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
