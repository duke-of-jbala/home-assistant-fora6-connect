"""Fail-closed in-place migration of the one legacy placeholder-backed entry."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN, PLACEHOLDER_SERIAL
from .mac_identity import canonical_bluetooth_mac


class IdentityMigrationError(Exception):
    """Privacy-safe migration failure; never include an identifier."""


def migrate_placeholder_identity(hass: HomeAssistant, entry) -> bool:
    """Retarget existing entry and device, preserving registry object IDs.

    The existing BLE connection is the evidence that this registered device
    owns the stored factory locator. Ambiguous or incomplete registry state
    leaves the original entry untouched.
    """
    if entry.unique_id != PLACEHOLDER_SERIAL:
        return False
    address = entry.data.get("address")
    mac = canonical_bluetooth_mac(address)
    if mac is None:
        raise IdentityMigrationError("invalid_factory_locator")
    if any(
        other.entry_id != entry.entry_id
        and canonical_bluetooth_mac(other.unique_id) == mac
        for other in hass.config_entries.async_entries(DOMAIN)
    ):
        raise IdentityMigrationError("identity_conflict")

    registry = dr.async_get(hass)
    device = registry.async_get_device_by_identifier(
        (DOMAIN, PLACEHOLDER_SERIAL), entry.entry_id
    )
    if device is None or (DOMAIN, PLACEHOLDER_SERIAL) not in device.identifiers:
        raise IdentityMigrationError("legacy_device_missing")
    ble_connections = {
        value for kind, value in device.connections
        if kind == dr.CONNECTION_BLUETOOTH
    }
    if len(ble_connections) != 1:
        raise IdentityMigrationError("locator_conflict")
    old_ble_connection = next(iter(ble_connections))
    if canonical_bluetooth_mac(old_ble_connection) != mac:
        raise IdentityMigrationError("locator_conflict")
    claimed = registry.async_get_device_by_identifier((DOMAIN, mac), entry.entry_id)
    if claimed is not None and claimed.id != device.id:
        raise IdentityMigrationError("identity_conflict")
    connection_owner = registry.async_get_device_by_connection(
        (dr.CONNECTION_BLUETOOTH, old_ble_connection), entry.entry_id
    )
    if connection_owner is None or connection_owner.id != device.id:
        raise IdentityMigrationError("locator_conflict")

    entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    if len(entities) != 1 or entities[0].device_id != device.id:
        raise IdentityMigrationError("entity_association_conflict")

    old_identifiers = set(device.identifiers)
    old_connections = set(device.connections)
    old_serial = device.serial_number
    new_identifiers = (old_identifiers - {(DOMAIN, PLACEHOLDER_SERIAL)}) | {(DOMAIN, mac)}
    new_connections = {
        connection for connection in old_connections
        if connection[0] != dr.CONNECTION_BLUETOOTH
    } | {(dr.CONNECTION_BLUETOOTH, mac)}
    try:
        registry.async_update_device(
            device.id,
            new_identifiers=new_identifiers,
            new_connections=new_connections,
            serial_number=None,
        )
        hass.config_entries.async_update_entry(entry, unique_id=mac)
        if entry.unique_id != mac:
            raise IdentityMigrationError("entry_update_failed")
    except Exception:
        # The device ID stays the same. Restore identifiers if HA rejects the
        # ConfigEntry update, rather than leaving two inconsistent identities.
        try:
            if entry.unique_id == mac:
                hass.config_entries.async_update_entry(
                    entry, unique_id=PLACEHOLDER_SERIAL
                )
            registry.async_update_device(
                device.id,
                new_identifiers=old_identifiers,
                new_connections=old_connections,
                serial_number=old_serial,
            )
        except Exception:
            raise IdentityMigrationError("rollback_failed") from None
        raise IdentityMigrationError("entry_update_failed") from None
    return True
