"""User-confirmed Bluetooth setup with exact private serial identity."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import bluetooth

from .const import DOMAIN, NAME
from .discovery import is_fora_candidate
from .setup_identity import SetupIdentityError, async_confirm_meter_identity

LOCATOR_KEY = "address"


class Fora6ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """A passive candidate must pass bounded project and serial checks."""

    VERSION = 1

    def __init__(self) -> None:
        super().__init__()
        self._candidate_address: str | None = None
        self._confirmed_serial: str | None = None

    async def async_step_user(self, user_input: dict | None = None) -> Any:
        """Manual setup cannot bypass the observed Bluetooth candidate gate."""
        return self.async_abort(reason="bluetooth_required")

    async def async_step_bluetooth(self, discovery_info: Any) -> Any:
        """Show a review form; advertisement data alone creates no entry."""
        if not is_fora_candidate(discovery_info):
            return self.async_abort(reason="not_fora6_connect")
        if not isinstance(discovery_info.address, str) or not discovery_info.address:
            return self.async_abort(reason="identity_failed")
        self._candidate_address = discovery_info.address
        self.context["title_placeholders"] = {"name": NAME}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict | None = None) -> Any:
        """Connect only after the user confirms the candidate."""
        if self._candidate_address is None:
            return self.async_abort(reason="identity_failed")
        if user_input is None:
            return self.async_show_form(step_id="confirm", data_schema=vol.Schema({}))
        try:
            serial = await async_confirm_meter_identity(
                self.hass, self._candidate_address
            )
        except SetupIdentityError as exc:
            return self.async_abort(reason=exc.code)
        except Exception:
            return self.async_abort(reason="identity_failed")
        if (
            not isinstance(serial, str)
            or not serial.strip("\x00 \t\r\n")
            or not all(char.isprintable() for char in serial.strip("\x00 \t\r\n"))
        ):
            return self.async_abort(reason="serial_unavailable")
        self._confirmed_serial = serial
        # HA arbitrates concurrent flows for the same domain-scoped ID.
        await self.async_set_unique_id(serial)
        for entry in self._async_current_entries():
            if entry.data.get(LOCATOR_KEY) == self._candidate_address and entry.unique_id != serial:
                return self.async_abort(reason="identity_conflict")
        existing = next(
            (entry for entry in self._async_current_entries() if entry.unique_id == serial),
            None,
        )
        if existing is not None:
            if existing.data.get(LOCATOR_KEY) == self._candidate_address:
                return self.async_abort(reason="already_configured")
            return await self.async_step_update_locator()
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=NAME, data={LOCATOR_KEY: self._candidate_address})

    async def async_step_update_locator(self, user_input: dict | None = None) -> Any:
        """Require a second explicit review before replacing a locator."""
        if self._confirmed_serial is None or self._candidate_address is None:
            return self.async_abort(reason="identity_failed")
        if user_input is None:
            return self.async_show_form(
                step_id="update_locator", data_schema=vol.Schema({})
            )
        entries = self._async_current_entries()
        existing = next(
            (entry for entry in entries if entry.unique_id == self._confirmed_serial),
            None,
        )
        if existing is None:
            return self.async_abort(reason="identity_conflict")
        if any(
            entry is not existing and entry.data.get(LOCATOR_KEY) == self._candidate_address
            for entry in entries
        ):
            return self.async_abort(reason="identity_conflict")
        old_address = existing.data.get(LOCATOR_KEY)
        if old_address != self._candidate_address:
            # A simultaneously connectable old locator makes a same-serial
            # claim ambiguous; never silently merge two physical candidates.
            try:
                old_device = bluetooth.async_ble_device_from_address(
                    self.hass, old_address, connectable=True
                )
            except Exception:
                return self.async_abort(reason="identity_conflict")
            if old_device is not None:
                return self.async_abort(reason="identity_conflict")
            try:
                self.hass.config_entries.async_update_entry(
                    existing, data={**existing.data, LOCATOR_KEY: self._candidate_address}
                )
            except Exception:
                return self.async_abort(reason="identity_conflict")
            runtime = getattr(existing, "runtime_data", None)
            if runtime is not None:
                runtime.address = self._candidate_address
            return self.async_abort(reason="locator_updated")
        return self.async_abort(reason="already_configured")
