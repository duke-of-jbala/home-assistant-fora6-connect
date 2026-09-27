"""Reconcile private device metadata from an already confirmed config entry."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, PLACEHOLDER_SERIAL


def async_reconcile_device_metadata(hass: HomeAssistant, entry, address: str) -> set[tuple[str, str]] | None:
    """Replace stale BLE connections and serial display on the same HA device.

    The caller must have confirmed that ``address`` belongs to ``entry.unique_id``.
    Return the old connection set for a guarded locator-update rollback.
    """
    registry = dr.async_get(hass)
    device = registry.async_get_device_by_identifier(
        (DOMAIN, entry.unique_id), entry.entry_id
    )
    if device is None:
        return None
    old_connections = set(device.connections)
    new_connections = {
        connection
        for connection in old_connections
        if connection[0] != dr.CONNECTION_BLUETOOTH
    }
    new_connections.add((dr.CONNECTION_BLUETOOTH, address))
    displayed_serial = (
        None if entry.unique_id == PLACEHOLDER_SERIAL else entry.unique_id
    )
    if device.serial_number != displayed_serial or old_connections != new_connections:
        registry.async_update_device(
            device.id,
            serial_number=displayed_serial,
            new_connections=new_connections,
        )
    return old_connections


def async_restore_device_connections(hass: HomeAssistant, entry, connections: set[tuple[str, str]] | None) -> None:
    """Restore registry locator metadata if an entry update fails."""
    if connections is None:
        return
    registry = dr.async_get(hass)
    device = registry.async_get_device_by_identifier(
        (DOMAIN, entry.unique_id), entry.entry_id
    )
    if device is not None and set(device.connections) != connections:
        registry.async_update_device(device.id, new_connections=connections)
