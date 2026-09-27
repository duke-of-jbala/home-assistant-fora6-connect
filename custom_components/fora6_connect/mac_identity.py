"""Conservative factory Bluetooth MAC identity for confirmed GD82 meters."""

from __future__ import annotations

import re

_MAC = re.compile(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\Z")


def canonical_bluetooth_mac(address: str) -> str | None:
    """Accept HA's six-octet colon form and match its lowercase MAC format."""
    if not isinstance(address, str) or _MAC.fullmatch(address) is None:
        return None
    normalized = address.lower()
    if normalized in ("00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"):
        return None
    return normalized


def is_mac_identity(unique_id: str | None) -> bool:
    """Identify a canonical MAC unique ID without interpreting other strings."""
    return isinstance(unique_id, str) and canonical_bluetooth_mac(unique_id) == unique_id
