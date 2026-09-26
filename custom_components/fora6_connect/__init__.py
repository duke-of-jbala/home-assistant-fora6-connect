"""FORA 6 Connect integration bootstrap.

No meter setup is available until discovery and the protocol are validated.
"""

from homeassistant.core import HomeAssistant


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Load the integration namespace without starting meter communication."""
    return True
