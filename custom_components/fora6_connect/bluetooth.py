"""Reusable Home Assistant Bluetooth transport for one FORA session.

The transport accepts validated protocol requests but chooses no commands,
record indexes, health interpretation, or synchronization policy. Runtime
addresses and notification bytes are never logged or included in errors.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from bleak_retry_connector import (
    BleakClientWithServiceCache,
    BleakOutOfConnectionSlotsError,
    establish_connection,
)
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import CHARACTERISTIC_UUID, NAME, SERVICE_UUID
from .protocol import FrameError, ProtocolFrame, validate_response_echo

CONNECTION_TIMEOUT = 20.0
CONNECT_TOTAL_TIMEOUT = 50.0
NOTIFY_TIMEOUT = 10.0
WRITE_TIMEOUT = 10.0
RESPONSE_TIMEOUT = 15.0
DISCONNECT_TIMEOUT = 10.0


class TransportError(Exception):
    """A stable failure code with no device identifier or packet contents."""

    def __init__(self, stage: str, code: str, *, write_succeeded: bool = False) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code
        self.write_succeeded = write_succeeded


@dataclass(frozen=True, slots=True)
class CleanupResult:
    """Only non-sensitive lifecycle outcomes are exposed to the caller."""

    notification_stopped_cleanly: bool
    disconnected_cleanly: bool
    errors: tuple[str, ...]


class Fora6BluetoothTransport:
    """One connectable HA-selected session with single-flight exchanges."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        *,
        response_timeout: float = RESPONSE_TIMEOUT,
    ) -> None:
        self._hass = hass
        self._address = address  # Runtime only; never rendered or persisted.
        self._response_timeout = response_timeout
        self._client: Any = None
        self._characteristic: Any = None
        self._subscribed = False
        self._pending_request: ProtocolFrame | None = None
        self._pending_response: asyncio.Future[ProtocolFrame | None] | None = None
        self._exchange_lock = asyncio.Lock()
        self._close_task: asyncio.Task[CleanupResult] | None = None
        self.device_resolved = False
        self.connection_established = False
        self.characteristic_found = False
        self.subscription_established = False

    def _is_connected(self) -> bool:
        """Treat a failing Bleak connection-state query as disconnected."""
        try:
            return self._client is not None and bool(self._client.is_connected)
        except Exception:
            return False

    async def async_connect(self) -> None:
        """Resolve through HA and retry only connection establishment."""
        if self._client is not None or self._close_task is not None:
            raise TransportError("connection", "invalid_session_state")
        try:
            ble_device = bluetooth.async_ble_device_from_address(
                self._hass, self._address, connectable=True
            )
        except Exception:
            raise TransportError("resolution", "resolution_failed") from None
        if ble_device is None:
            raise TransportError("resolution", "no_connectable_device")
        self.device_resolved = True
        try:
            self._client = await asyncio.wait_for(
                establish_connection(
                    BleakClientWithServiceCache,
                    ble_device,
                    NAME,
                    max_attempts=2,
                    use_services_cache=False,
                    timeout=CONNECTION_TIMEOUT,
                    pair=False,
                ),
                timeout=CONNECT_TOTAL_TIMEOUT,
            )
        except BleakOutOfConnectionSlotsError:
            raise TransportError("connection", "no_connection_slot") from None
        except Exception:
            raise TransportError("connection", "connection_failed") from None
        if not self._is_connected():
            raise TransportError("connection", "peer_disconnected")
        self.connection_established = True
        try:
            services = self._client.services
        except Exception:
            raise TransportError("gatt", "services_unavailable") from None
        if services is None:
            raise TransportError("gatt", "services_unavailable")
        try:
            service = next(
                item for item in services if str(item.uuid).lower() == SERVICE_UUID
            )
            characteristic = next(
                item
                for item in service.characteristics
                if str(item.uuid).lower() == CHARACTERISTIC_UUID
            )
            properties = {str(prop).lower() for prop in characteristic.properties}
        except Exception:
            raise TransportError("gatt", "custom_characteristic_missing") from None
        if not {"write", "notify"} <= properties:
            raise TransportError("gatt", "custom_properties_missing")
        self._characteristic = characteristic
        self.characteristic_found = True

    async def async_subscribe(self) -> None:
        """Subscribe once after validating the custom characteristic."""
        if not self._is_connected():
            raise TransportError("subscription", "peer_disconnected")
        if self._characteristic is None or self._subscribed or self._close_task:
            raise TransportError("subscription", "invalid_session_state")
        try:
            await asyncio.wait_for(
                self._client.start_notify(self._characteristic, self._on_notification),
                timeout=NOTIFY_TIMEOUT,
            )
        except Exception:
            raise TransportError("subscription", "subscription_failed") from None
        self._subscribed = True
        self.subscription_established = True

    def _on_notification(self, _sender: Any, data: bytearray) -> None:
        """Fail the active exchange closed; discard unsolicited notifications."""
        request = self._pending_request
        future = self._pending_response
        if request is None or future is None or future.done():
            return
        try:
            response = ProtocolFrame(bytes(data))
            validate_response_echo(request, response)
        except Exception:
            future.set_result(None)
            return
        future.set_result(response)

    async def async_exchange(self, request: ProtocolFrame) -> ProtocolFrame:
        """Write a request once and return one command-matched response."""
        if not isinstance(request, ProtocolFrame):
            raise TransportError("exchange", "invalid_request")
        try:
            request.require_request()
        except FrameError:
            raise TransportError("exchange", "invalid_request") from None
        async with self._exchange_lock:
            if not self._is_connected():
                raise TransportError("exchange", "peer_disconnected")
            if not self._subscribed or self._close_task is not None:
                raise TransportError("exchange", "invalid_session_state")
            future: asyncio.Future[ProtocolFrame | None] = (
                asyncio.get_running_loop().create_future()
            )
            self._pending_request = request
            self._pending_response = future
            try:
                try:
                    await asyncio.wait_for(
                        self._client.write_gatt_char(
                            self._characteristic, request.data, response=True
                        ),
                        timeout=WRITE_TIMEOUT,
                    )
                except Exception:
                    raise TransportError("exchange", "write_failed") from None
                try:
                    response = await asyncio.wait_for(
                        future, timeout=self._response_timeout
                    )
                except TimeoutError:
                    raise TransportError(
                        "exchange", "response_timeout", write_succeeded=True
                    ) from None
                if response is None:
                    raise TransportError(
                        "exchange", "invalid_response", write_succeeded=True
                    )
                if not self._is_connected():
                    raise TransportError(
                        "exchange", "peer_disconnected", write_succeeded=True
                    )
                return response
            finally:
                self._pending_request = None
                self._pending_response = None
                if not future.done():
                    future.cancel()

    async def async_close(self) -> CleanupResult:
        """Stop notifications and disconnect, even if the caller is cancelled."""
        if self._close_task is None:
            self._close_task = asyncio.create_task(self._async_close_impl())
        try:
            return await asyncio.shield(self._close_task)
        except asyncio.CancelledError:
            # Shield the bounded cleanup task until both steps have run.
            await asyncio.shield(self._close_task)
            raise

    async def _async_close_impl(self) -> CleanupResult:
        errors: list[str] = []
        stopped = False
        disconnected = False
        self._pending_request = None
        pending = self._pending_response
        self._pending_response = None
        if pending is not None and not pending.done():
            pending.set_result(None)
        if self._subscribed:
            try:
                await asyncio.wait_for(
                    self._client.stop_notify(self._characteristic),
                    timeout=NOTIFY_TIMEOUT,
                )
                stopped = True
            except Exception:
                errors.append("notification_stop_failed")
            self._subscribed = False
        if self._client is not None:
            try:
                await asyncio.wait_for(
                    self._client.disconnect(), timeout=DISCONNECT_TIMEOUT
                )
                disconnected = True
            except Exception:
                errors.append("disconnect_failed")
        return CleanupResult(stopped, disconnected, tuple(errors))

    async def __aenter__(self) -> Fora6BluetoothTransport:
        try:
            await self.async_connect()
            await self.async_subscribe()
        except BaseException:
            await self.async_close()
            raise
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.async_close()
