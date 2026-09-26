"""Hardware-free checks for the temporary Stage 1B GATT probe."""

import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


INTEGRATION = (
    Path(__file__).resolve().parents[1] / "custom_components" / "fora6_connect"
)


def _load_probe():
    """Load the probe with only its Home Assistant/Bleak boundaries mocked."""
    package = types.ModuleType("_fora6_probe_test")
    package.__path__ = [str(INTEGRATION)]
    const = types.ModuleType("_fora6_probe_test.const")
    exec((INTEGRATION / "const.py").read_text(encoding="utf-8"), const.__dict__)

    homeassistant = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    bluetooth.BluetoothScanningMode = types.SimpleNamespace(ACTIVE="active")
    bluetooth.BluetoothCallbackReplay = types.SimpleNamespace(DISABLED="disabled")
    connector = types.ModuleType("bleak_retry_connector")
    connector.BleakClientWithServiceCache = type("FakeBleakClient", (), {})
    connector.BleakOutOfConnectionSlotsError = type(
        "BleakOutOfConnectionSlotsError", (Exception,), {}
    )
    connector.establish_connection = AsyncMock()

    modules = {
        "_fora6_probe_test": package,
        "_fora6_probe_test.const": const,
        "homeassistant": homeassistant,
        "homeassistant.components": components,
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.core": core,
        "bleak_retry_connector": connector,
    }
    spec = importlib.util.spec_from_file_location(
        "_fora6_probe_test.gatt_probe", INTEGRATION / "gatt_probe.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, bluetooth, connector


def _service(uuid: str, *characteristics: tuple[str, tuple[str, ...]]):
    return types.SimpleNamespace(
        uuid=uuid,
        characteristics=[
            types.SimpleNamespace(uuid=char_uuid, properties=properties)
            for char_uuid, properties in characteristics
        ],
    )


def _load_setup(probe_module):
    """Load integration setup with its Home Assistant service API mocked."""
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    core.ServiceCall = object
    core.SupportsResponse = types.SimpleNamespace(ONLY="response_only")
    exceptions = types.ModuleType("homeassistant.exceptions")
    exceptions.ServiceValidationError = type("ServiceValidationError", (Exception,), {})
    const = types.ModuleType("_fora6_setup_test.const")
    exec((INTEGRATION / "const.py").read_text(encoding="utf-8"), const.__dict__)
    gatt = types.ModuleType("_fora6_setup_test.gatt_probe")
    gatt.ProbeError = probe_module.ProbeError
    gatt.async_probe_gatt = AsyncMock(return_value={"device_found": True})
    spec = importlib.util.spec_from_file_location(
        "_fora6_setup_test",
        INTEGRATION / "__init__.py",
        submodule_search_locations=[str(INTEGRATION)],
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with patch.dict(
        sys.modules,
        {
            "homeassistant.core": core,
            "homeassistant.exceptions": exceptions,
            "_fora6_setup_test": module,
            "_fora6_setup_test.const": const,
            "_fora6_setup_test.gatt_probe": gatt,
        },
    ):
        spec.loader.exec_module(module)
    return module, gatt, exceptions


class GattProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.probe, self.bluetooth, self.connector = _load_probe()
        self.hass = object()
        self.address = "private-device-1"
        self.info = types.SimpleNamespace(
            name="FORA 6 CONNECT",
            device=types.SimpleNamespace(name="FORA 6 CONNECT"),
            address=self.address,
        )
        self.bluetooth.async_scanner_count = Mock(return_value=1)
        self.bluetooth.async_discovered_service_info = Mock(
            side_effect=[[self.info], [self.info]]
        )
        self.bluetooth.async_clear_advertisement_history = Mock()
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.cancel = Mock()
        self.callback = None

        def register(_hass, callback, _matcher, _mode, **_kwargs):
            self.callback = callback
            return self.cancel

        self.bluetooth.async_register_callback = Mock(side_effect=register)

        async def scan(_hass):
            self.callback(self.info, None)

        self.bluetooth.async_request_active_scan = AsyncMock(side_effect=scan)
        self.client = types.SimpleNamespace(
            is_connected=True,
            services=[
                _service("180a"),
                _service(
                    "1808",
                    ("2a18", ("notify",)),
                    ("2a34", ("notify",)),
                    ("2a51", ("read",)),
                    ("2a52", ("write", "indicate")),
                ),
                _service(
                    self.probe.SERVICE_UUID,
                    (self.probe.CHARACTERISTIC_UUID, ("write", "notify")),
                ),
            ],
            disconnect=AsyncMock(),
            write_gatt_char=AsyncMock(),
            start_notify=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client

    async def test_success_uses_fresh_scan_and_never_writes(self) -> None:
        result = await self.probe.async_probe_gatt(self.hass)

        self.bluetooth.async_request_active_scan.assert_awaited_once_with(self.hass)
        self.bluetooth.async_clear_advertisement_history.assert_called_once_with(
            self.hass, self.address
        )
        self.assertEqual(
            self.bluetooth.async_register_callback.call_args.kwargs["replay"],
            "disabled",
        )
        self.assertEqual(
            self.bluetooth.async_ble_device_from_address.call_args.kwargs,
            {"connectable": True},
        )
        self.assertEqual(
            self.connector.establish_connection.call_args.kwargs,
            {
                "max_attempts": 2,
                "use_services_cache": False,
                "timeout": 20.0,
                "pair": False,
            },
        )
        self.assertEqual(result["gatt_service_count"], 3)
        self.assertTrue(result["fresh_advertisement_observed"])
        self.assertTrue(result["connected_via_ha_bluetooth"])
        self.assertTrue(result["disconnected_cleanly"])
        self.assertTrue(result["expected_gatt"]["fora_custom_service_present"])
        self.assertTrue(
            all(
                item["expected_properties_present"]
                for item in result["expected_gatt"]["characteristics"]
            )
        )
        self.assertNotIn(self.address, json.dumps(result))
        self.client.disconnect.assert_awaited_once()
        self.client.write_gatt_char.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()
        self.client.pair.assert_not_awaited()
        self.cancel.assert_called_once()

    async def test_cached_candidate_without_new_advertisement_is_rejected(self) -> None:
        self.bluetooth.async_request_active_scan = AsyncMock()
        with self.assertRaisesRegex(self.probe.ProbeError, "No fresh"):
            await self.probe.async_probe_gatt(self.hass)
        self.connector.establish_connection.assert_not_awaited()
        self.cancel.assert_called_once()

    async def test_no_connectable_device_is_reported(self) -> None:
        self.bluetooth.async_ble_device_from_address.return_value = None
        with self.assertRaisesRegex(self.probe.ProbeError, "no connectable BLEDevice"):
            await self.probe.async_probe_gatt(self.hass)
        self.connector.establish_connection.assert_not_awaited()

    async def test_active_scan_failure_releases_callback(self) -> None:
        self.bluetooth.async_request_active_scan.side_effect = RuntimeError(
            self.address
        )
        with self.assertRaises(self.probe.ProbeError) as caught:
            await self.probe.async_probe_gatt(self.hass)
        self.assertNotIn(self.address, str(caught.exception))
        self.cancel.assert_called_once()
        self.connector.establish_connection.assert_not_awaited()

    async def test_multiple_matching_devices_are_not_chosen_arbitrarily(self) -> None:
        other = types.SimpleNamespace(
            name="FORA 6 CONNECT",
            device=types.SimpleNamespace(name="FORA 6 CONNECT"),
            address="private-device-2",
        )
        self.bluetooth.async_discovered_service_info.side_effect = [
            [self.info],
            [self.info, other],
        ]

        async def scan(_hass):
            self.callback(self.info, None)
            self.callback(other, None)

        self.bluetooth.async_request_active_scan.side_effect = scan
        with self.assertRaisesRegex(self.probe.ProbeError, "Multiple matching"):
            await self.probe.async_probe_gatt(self.hass)
        self.connector.establish_connection.assert_not_awaited()

    async def test_connection_failure_is_sanitized(self) -> None:
        self.connector.establish_connection.side_effect = RuntimeError(self.address)
        with self.assertRaises(self.probe.ProbeError) as caught:
            await self.probe.async_probe_gatt(self.hass)
        self.assertNotIn(self.address, str(caught.exception))
        self.client.disconnect.assert_not_awaited()

    async def test_no_connection_slot_is_reported(self) -> None:
        self.connector.establish_connection.side_effect = (
            self.connector.BleakOutOfConnectionSlotsError(self.address)
        )
        with self.assertRaisesRegex(self.probe.ProbeError, "connection slot"):
            await self.probe.async_probe_gatt(self.hass)

    async def test_service_discovery_failure_still_disconnects(self) -> None:
        self.client.services = [
            types.SimpleNamespace(uuid="180a", characteristics=None)
        ]
        with self.assertRaisesRegex(self.probe.ProbeError, "GATT service discovery"):
            await self.probe.async_probe_gatt(self.hass)
        self.client.disconnect.assert_awaited_once()
        self.client.write_gatt_char.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()
        self.client.pair.assert_not_awaited()

    async def test_missing_expected_gatt_is_reported_as_missing(self) -> None:
        self.client.services = [_service("180a")]
        result = await self.probe.async_probe_gatt(self.hass)
        self.assertFalse(result["expected_gatt"]["fora_custom_service_present"])
        self.assertTrue(
            all(
                not item["present"]
                for item in result["expected_gatt"]["characteristics"]
            )
        )
        self.client.disconnect.assert_awaited_once()

    async def test_peer_disconnect_still_runs_cleanup(self) -> None:
        self.client.is_connected = False
        with self.assertRaisesRegex(self.probe.ProbeError, "disconnected before"):
            await self.probe.async_probe_gatt(self.hass)
        self.client.disconnect.assert_awaited_once()

    async def test_peer_disconnect_during_inventory_is_not_reported_as_success(
        self,
    ) -> None:
        class DisconnectingClient:
            services = [_service("180a")]

            def __init__(self):
                self.connected_checks = 0
                self.disconnect = AsyncMock()

            @property
            def is_connected(self):
                self.connected_checks += 1
                return self.connected_checks == 1

        client = DisconnectingClient()
        self.connector.establish_connection.return_value = client
        with self.assertRaisesRegex(self.probe.ProbeError, "disconnected during"):
            await self.probe.async_probe_gatt(self.hass)
        client.disconnect.assert_awaited_once()

    async def test_disconnect_failure_is_reported_without_address(self) -> None:
        self.client.disconnect.side_effect = RuntimeError(self.address)
        with self.assertRaises(self.probe.ProbeError) as caught:
            await self.probe.async_probe_gatt(self.hass)
        self.assertIn("clean disconnect", str(caught.exception))
        self.assertNotIn(self.address, str(caught.exception))

    async def test_no_connectable_scanner_stops_before_scan(self) -> None:
        self.bluetooth.async_scanner_count.return_value = 0
        with self.assertRaisesRegex(self.probe.ProbeError, "No connectable"):
            await self.probe.async_probe_gatt(self.hass)
        self.bluetooth.async_request_active_scan.assert_not_awaited()


class ProbeServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_manual_action_registers_and_returns_probe_data(self) -> None:
        probe, _, _ = _load_probe()
        integration, gatt, _ = _load_setup(probe)
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services)

        self.assertTrue(await integration.async_setup(hass, {}))
        args = services.async_register.call_args
        self.assertEqual(args.args[:2], ("fora6_connect", "probe_gatt"))
        self.assertEqual(args.kwargs["supports_response"], "response_only")
        self.assertEqual(await args.args[2](object()), {"device_found": True})
        gatt.async_probe_gatt.assert_awaited_once_with(hass)

    async def test_manual_action_converts_probe_error_to_safe_service_error(
        self,
    ) -> None:
        probe, _, _ = _load_probe()
        integration, gatt, exceptions = _load_setup(probe)
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services)
        await integration.async_setup(hass, {})
        handler = services.async_register.call_args.args[2]
        gatt.async_probe_gatt.side_effect = probe.ProbeError("No fresh advertisement.")

        with self.assertRaisesRegex(
            exceptions.ServiceValidationError, "No fresh advertisement"
        ):
            await handler(object())
