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
    bluetooth.BluetoothReachabilityIntent = types.SimpleNamespace(
        CONNECTION="connection"
    )
    bluetooth.MONOTONIC_TIME = Mock(return_value=1.5)
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


class LocalNameNormalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.probe, _, _ = _load_probe()

    def test_five_trailing_nuls_and_clean_name(self) -> None:
        self.assertEqual(
            self.probe.normalize_local_name("FORA 6 CONNECT\x00\x00\x00\x00\x00"),
            "FORA 6 CONNECT",
        )
        self.assertEqual(
            self.probe.normalize_local_name("FORA 6 CONNECT"),
            "FORA 6 CONNECT",
        )

    def test_none_and_other_characters_are_preserved(self) -> None:
        self.assertIsNone(self.probe.normalize_local_name(None))
        for name in (
            "FORA 6 CONNECT ",
            "FORA 6 CONNECT!",
            "\x00FORA 6 CONNECT",
            "FORA\x00 6 CONNECT",
        ):
            with self.subTest(name=name):
                self.assertEqual(self.probe.normalize_local_name(name), name)

    def test_general_discovery_service_info_name_is_normalized(self) -> None:
        # Current manual-address probe does not consult the discovery cache.
        # The same accessor handles its service-info representation if used.
        general_info = types.SimpleNamespace(
            advertisement=types.SimpleNamespace(
                local_name="FORA 6 CONNECT\x00\x00\x00\x00\x00"
            ),
            name="UNRELATED RESOLVED NAME",
        )
        self.assertEqual(
            self.probe._advertised_local_name(general_info),
            self.probe.TARGET_LOCAL_NAME,
        )


class GattProbeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.probe, self.bluetooth, self.connector = _load_probe()
        self.hass = object()
        self.address = "synthetic-private-device"
        self.info = types.SimpleNamespace(
            name="UNRELATED RESOLVED NAME",
            device=types.SimpleNamespace(name="UNRELATED BLEAK NAME"),
            advertisement=types.SimpleNamespace(
                local_name="FORA 6 CONNECT\x00\x00\x00\x00\x00"
            ),
            address=self.address,
            time=1.0,
        )
        self.bluetooth.async_scanner_count = Mock(return_value=1)
        self.bluetooth.async_ble_device_from_address = Mock(return_value=object())
        self.bluetooth.async_last_service_info = Mock(return_value=self.info)
        self.bluetooth.async_address_reachability_diagnostics = Mock(
            return_value="in connectable history; 1 scanner(s) registered"
        )
        self.bluetooth.async_process_advertisements = AsyncMock()
        self.bluetooth.async_clear_advertisement_history = Mock()
        self.bluetooth.async_request_active_scan = AsyncMock()
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
            read_gatt_char=AsyncMock(),
            write_gatt_char=AsyncMock(),
            write_gatt_descriptor=AsyncMock(),
            start_notify=AsyncMock(),
            pair=AsyncMock(),
        )
        self.connector.establish_connection.return_value = self.client

    def assert_no_advertisement_gate(self) -> None:
        self.bluetooth.async_process_advertisements.assert_not_awaited()
        self.bluetooth.async_clear_advertisement_history.assert_not_called()
        self.bluetooth.async_request_active_scan.assert_not_awaited()

    def assert_no_characteristic_io(self) -> None:
        self.client.read_gatt_char.assert_not_awaited()
        self.client.write_gatt_char.assert_not_awaited()
        self.client.write_gatt_descriptor.assert_not_awaited()
        self.client.start_notify.assert_not_awaited()
        self.client.pair.assert_not_awaited()

    async def test_private_address_resolves_directly_and_enumerates_gatt(self) -> None:
        with self.assertLogs(self.probe.__name__, level="DEBUG") as captured:
            result = await self.probe.async_probe_gatt(self.hass, self.address)

        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, self.address, connectable=True
        )
        self.bluetooth.async_last_service_info.assert_called_once_with(
            self.hass, self.address, connectable=False
        )
        self.bluetooth.async_address_reachability_diagnostics.assert_not_called()
        self.assert_no_advertisement_gate()
        self.assertEqual(
            self.connector.establish_connection.call_args.kwargs,
            {
                "max_attempts": 2,
                "use_services_cache": False,
                "timeout": 20.0,
                "pair": False,
            },
        )
        self.assertEqual(result["local_name"], "FORA 6 CONNECT")
        self.assertTrue(result["last_service_info_available"])
        self.assertTrue(result["advertised_name_confirmed"])
        self.assertTrue(result["connectable_device_resolved"])
        self.assertTrue(result["gatt_connection_attempted"])
        self.assertTrue(result["connection_successful"])
        self.assertTrue(result["connected_via_ha_bluetooth"])
        self.assertEqual(result["gatt_service_count"], 3)
        self.assertTrue(result["disconnected_cleanly"])
        self.assertTrue(result["expected_gatt"]["fora_custom_service_present"])
        self.assertTrue(
            all(
                item["expected_properties_present"]
                for item in result["expected_gatt"]["characteristics"]
            )
        )
        self.assertNotIn(self.address, json.dumps(result))
        self.assertNotIn(self.address, "\n".join(captured.output))
        self.assertIn("connection attempted", "\n".join(captured.output))
        self.assertIn("GATT enumeration reached", "\n".join(captured.output))
        self.client.disconnect.assert_awaited_once()
        self.assert_no_characteristic_io()

    async def test_missing_last_info_does_not_block_direct_connection(self) -> None:
        self.bluetooth.async_last_service_info.return_value = None
        result = await self.probe.async_probe_gatt(self.hass, self.address)

        self.assertIsNone(result["local_name"])
        self.assertFalse(result["last_service_info_available"])
        self.assertFalse(result["advertised_name_confirmed"])
        self.assertTrue(result["connection_successful"])
        self.assert_no_advertisement_gate()

    async def test_stale_or_wrong_name_is_diagnostic_only(self) -> None:
        self.info.advertisement.local_name = "OTHER"
        self.info.time = 0.0
        result = await self.probe.async_probe_gatt(self.hass, self.address)

        self.assertEqual(result["local_name"], "OTHER")
        self.assertFalse(result["advertised_name_confirmed"])
        self.assertTrue(result["connection_successful"])
        self.assert_no_advertisement_gate()

    async def test_no_connectable_device_returns_sanitized_reachability(self) -> None:
        self.bluetooth.async_ble_device_from_address.return_value = None
        self.bluetooth.async_address_reachability_diagnostics.return_value = (
            "only in non-connectable history (no connectable path); "
            f"device {self.address}; scanner AA:AA:AA:AA:AA:AA slots=0/3; "
            "source 11111111-1111-1111-1111-111111111111; "
            "other scanner AAAAAAAAAAAA"
        )
        with self.assertLogs(self.probe.__name__, level="DEBUG") as captured:
            with self.assertRaises(self.probe.ProbeError) as caught:
                await self.probe.async_probe_gatt(self.hass, self.address)

        error = str(caught.exception)
        self.assertIn("only in non-connectable history", error)
        self.assertIn("slots=0/3", error)
        self.assertNotIn(self.address, error)
        self.assertNotIn("AA:AA:AA:AA:AA:AA", error)
        self.assertNotIn("11111111-1111-1111-1111-111111111111", error)
        self.assertNotIn("AAAAAAAAAAAA", error)
        self.assertNotIn(self.address, "\n".join(captured.output))
        self.bluetooth.async_address_reachability_diagnostics.assert_called_once_with(
            self.hass, self.address, "connection"
        )
        self.bluetooth.async_last_service_info.assert_not_called()
        self.connector.establish_connection.assert_not_awaited()
        self.assert_no_advertisement_gate()

    async def test_reachability_failure_has_safe_fallback(self) -> None:
        self.bluetooth.async_ble_device_from_address.return_value = None
        self.bluetooth.async_address_reachability_diagnostics.side_effect = RuntimeError(
            self.address
        )
        with self.assertRaises(self.probe.ProbeError) as caught:
            await self.probe.async_probe_gatt(self.hass, self.address)

        self.assertIn("No additional reachability detail", str(caught.exception))
        self.assertNotIn(self.address, str(caught.exception))
        self.connector.establish_connection.assert_not_awaited()

    async def test_no_connectable_scanner_count_does_not_skip_resolution(self) -> None:
        self.bluetooth.async_scanner_count.return_value = 0
        result = await self.probe.async_probe_gatt(self.hass, self.address)

        self.bluetooth.async_ble_device_from_address.assert_called_once_with(
            self.hass, self.address, connectable=True
        )
        self.assertEqual(result["connectable_scanner_count"], 0)
        self.assertTrue(result["connection_successful"])

    async def test_optional_last_info_failure_does_not_block_connection(self) -> None:
        self.bluetooth.async_last_service_info.side_effect = RuntimeError(self.address)
        with self.assertLogs(self.probe.__name__, level="DEBUG") as captured:
            result = await self.probe.async_probe_gatt(self.hass, self.address)

        self.assertFalse(result["last_service_info_available"])
        self.assertIsNone(result["local_name"])
        self.assertTrue(result["connection_successful"])
        self.assertNotIn(self.address, "\n".join(captured.output))

    async def test_connection_failure_is_sanitized(self) -> None:
        self.connector.establish_connection.side_effect = RuntimeError(self.address)
        with self.assertRaises(self.probe.ProbeError) as caught:
            await self.probe.async_probe_gatt(self.hass, self.address)
        self.assertNotIn(self.address, str(caught.exception))
        self.client.disconnect.assert_not_awaited()

    async def test_no_connection_slot_is_reported(self) -> None:
        self.connector.establish_connection.side_effect = (
            self.connector.BleakOutOfConnectionSlotsError(self.address)
        )
        with self.assertRaisesRegex(self.probe.ProbeError, "connection slot"):
            await self.probe.async_probe_gatt(self.hass, self.address)

    async def test_service_discovery_failure_still_disconnects(self) -> None:
        self.client.services = [
            types.SimpleNamespace(uuid="180a", characteristics=None)
        ]
        with self.assertRaisesRegex(self.probe.ProbeError, "GATT service discovery"):
            await self.probe.async_probe_gatt(self.hass, self.address)
        self.client.disconnect.assert_awaited_once()
        self.assert_no_characteristic_io()

    async def test_missing_expected_gatt_is_reported_as_missing(self) -> None:
        self.client.services = [_service("180a")]
        result = await self.probe.async_probe_gatt(self.hass, self.address)
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
            await self.probe.async_probe_gatt(self.hass, self.address)
        self.client.disconnect.assert_awaited_once()

    async def test_disconnect_failure_is_reported_without_address(self) -> None:
        self.client.disconnect.side_effect = RuntimeError(self.address)
        with self.assertRaises(self.probe.ProbeError) as caught:
            await self.probe.async_probe_gatt(self.hass, self.address)
        self.assertIn("clean disconnect", str(caught.exception))
        self.assertNotIn(self.address, str(caught.exception))


class ProbeServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_manual_action_registers_and_returns_probe_data(self) -> None:
        probe, _, _ = _load_probe()
        integration, gatt, _ = _load_setup(probe)
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(
            services=services, data={}, config_entries=Mock()
        )
        address = "synthetic-device"

        self.assertTrue(await integration.async_setup(hass, {}))
        args = services.async_register.call_args
        self.assertEqual(args.args[:2], ("fora6_connect", "probe_gatt"))
        self.assertEqual(args.kwargs["supports_response"], "response_only")
        result = await args.args[2](types.SimpleNamespace(data={"address": address}))
        self.assertEqual(result, {"device_found": True})
        self.assertNotIn(address, json.dumps(result))
        gatt.async_probe_gatt.assert_awaited_once_with(hass, address)
        self.assertEqual(hass.data, {})
        hass.config_entries.assert_not_called()

    async def test_manual_action_converts_probe_error_to_safe_service_error(
        self,
    ) -> None:
        probe, _, _ = _load_probe()
        integration, gatt, exceptions = _load_setup(probe)
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services)
        await integration.async_setup(hass, {})
        handler = services.async_register.call_args.args[2]
        gatt.async_probe_gatt.side_effect = probe.ProbeError(
            "No connectable BLEDevice is available."
        )

        with self.assertRaisesRegex(
            exceptions.ServiceValidationError, "No connectable BLEDevice"
        ):
            await handler(types.SimpleNamespace(data={"address": "synthetic-device"}))

    async def test_manual_action_requires_address_without_echoing_input(self) -> None:
        probe, _, _ = _load_probe()
        integration, gatt, exceptions = _load_setup(probe)
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services)
        await integration.async_setup(hass, {})
        handler = services.async_register.call_args.args[2]

        for data in ({}, {"address": "   "}, {"address": ["synthetic-device"]}):
            with self.assertRaises(exceptions.ServiceValidationError) as caught:
                await handler(types.SimpleNamespace(data=data))
            self.assertNotIn("synthetic-device", str(caught.exception))
        gatt.async_probe_gatt.assert_not_awaited()

    async def test_unexpected_service_error_does_not_echo_address(self) -> None:
        probe, _, _ = _load_probe()
        integration, gatt, exceptions = _load_setup(probe)
        services = types.SimpleNamespace(async_register=Mock())
        hass = types.SimpleNamespace(services=services)
        await integration.async_setup(hass, {})
        handler = services.async_register.call_args.args[2]
        address = "synthetic-device"
        gatt.async_probe_gatt.side_effect = RuntimeError(address)

        with self.assertRaises(exceptions.ServiceValidationError) as caught:
            await handler(types.SimpleNamespace(data={"address": address}))
        self.assertNotIn(address, str(caught.exception))
