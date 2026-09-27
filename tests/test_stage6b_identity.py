"""Synthetic bounded setup confirmation without a physical meter."""

import asyncio
import importlib.util
import logging
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from test_measurement import PACKAGE_NAME, protocol

INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"


def _response(command, low=0, high=0):
    first = bytes((0x51, command, low, high, 0, 0, 0xA5))
    return protocol.ProtocolFrame(first + bytes((protocol.checksum_for(first),)))


def _load_identity():
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    bluetooth = types.ModuleType(f"{PACKAGE_NAME}.bluetooth")
    bluetooth.TransportError = type("TransportError", (Exception,), {"__init__": lambda self, stage: (Exception.__init__(self, stage), setattr(self, "stage", stage)) and None})
    instance = types.SimpleNamespace(
        async_connect=AsyncMock(), async_subscribe=AsyncMock(),
        async_exchange=AsyncMock(side_effect=[_response(0x22), _response(0x24, 0x83, 0x41)]),
        async_close=AsyncMock(return_value=types.SimpleNamespace(
            notification_stopped_cleanly=True, disconnected_cleanly=True, errors=())),
    )
    bluetooth.Fora6BluetoothTransport = Mock(return_value=instance)
    serial_probe = types.ModuleType(f"{PACKAGE_NAME}.serial_probe")
    serial_probe._async_read_serial_private = AsyncMock(return_value=(
        {"serial_value_usable": True, "disconnected_cleanly": True}, b"SYNTHETIC-SERIAL-A"))
    spec = importlib.util.spec_from_file_location(f"{PACKAGE_NAME}.setup_identity", INTEGRATION / "setup_identity.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        "homeassistant.core": core,
        f"{PACKAGE_NAME}.bluetooth": bluetooth,
        f"{PACKAGE_NAME}.serial_probe": serial_probe,
    }):
        spec.loader.exec_module(module)
    return module, instance, serial_probe


class IdentityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.module, self.transport, self.serial_probe = _load_identity()
        self.hass = object()
        self.address = "SYNTHETIC-LOCATOR-A"

    async def test_success_exact_serial_and_only_two_known_commands(self):
        value = await self.module.async_confirm_meter_identity(self.hass, self.address)
        self.assertEqual(value, "SYNTHETIC-SERIAL-A")
        self.assertEqual([call.args[0].command_id for call in self.transport.async_exchange.await_args_list], [0x22, 0x24])
        self.transport.async_connect.assert_awaited_once()
        self.transport.async_subscribe.assert_awaited_once()
        self.transport.async_close.assert_awaited_once()
        self.serial_probe._async_read_serial_private.assert_awaited_once_with(self.hass, self.address)

    async def test_project_mismatch_rejects_without_serial_read(self):
        self.transport.async_exchange.side_effect = [_response(0x22), _response(0x24, 0, 0)]
        with self.assertRaises(self.module.SetupIdentityError) as raised:
            await self.module.async_confirm_meter_identity(self.hass, self.address)
        self.assertEqual(raised.exception.code, "not_fora6_connect")
        self.transport.async_close.assert_awaited_once()
        self.serial_probe._async_read_serial_private.assert_not_awaited()

    async def test_invalid_serial_or_failed_disconnect_rejects(self):
        for result, raw in (({"serial_value_usable": False, "disconnected_cleanly": True}, None),
                            ({"serial_value_usable": True, "disconnected_cleanly": False}, b"SYNTHETIC-SERIAL-A")):
            with self.subTest(result=result):
                self.transport.async_exchange.side_effect = [_response(0x22), _response(0x24, 0x83, 0x41)]
                self.serial_probe._async_read_serial_private.return_value = (result, raw)
                with self.assertRaises(self.module.SetupIdentityError) as raised:
                    await self.module.async_confirm_meter_identity(self.hass, self.address)
                self.assertEqual(raised.exception.code, "serial_unavailable")

    async def test_transport_failure_is_private_and_never_reads_serial(self):
        self.transport.async_connect.side_effect = RuntimeError("SYNTHETIC-LOCATOR-A")
        with patch.object(logging.Logger, "_log") as logged:
            with self.assertRaises(self.module.SetupIdentityError) as raised:
                await self.module.async_confirm_meter_identity(self.hass, self.address)
        self.assertEqual(raised.exception.code, "identity_failed")
        self.assertNotIn(self.address, str(raised.exception))
        logged.assert_not_called()
        self.transport.async_close.assert_awaited_once()
        self.serial_probe._async_read_serial_private.assert_not_awaited()

    async def test_cancellation_closes_identity_session(self):
        started = asyncio.Event()

        async def pending_connect():
            started.set()
            await asyncio.Future()

        self.transport.async_connect.side_effect = pending_connect
        task = asyncio.create_task(self.module.async_confirm_meter_identity(self.hass, self.address))
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.transport.async_close.assert_awaited_once()
        self.serial_probe._async_read_serial_private.assert_not_awaited()
