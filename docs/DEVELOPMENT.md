# Development

## Stage discipline

Read `AGENTS.md`, `CURRENT_STATUS.md`, and `PROTOCOL.md` before implementation. Stage 1B now has a manually invoked development-only GATT probe. Protocol decoding, production discovery/config flow, synchronization, and entities remain inactive.

Document every future protocol conclusion with its source, date, capture conditions, confidence, and sanitized fixture when possible. Add parser tests before using decoded data in Home Assistant. Never substitute the time of synchronization for the original meter timestamp.

## Local checks

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q custom_components tests
python3 -m tabnanny custom_components tests
```

If Ruff is installed:

```bash
ruff check .
ruff format --check .
```

These checks use mocks and do not prove that a real Home Assistant instance can connect to the meter. Real tests of the two preceding builds stopped at discovery; retest this general-discovery revision separately. HACS and production validation remain later-stage work.

## Temporary Stage 1B Home Assistant GATT probe

This development action looks up a currently cached `FORA 6 CONNECT` candidate in Home Assistant's **general** discovery view, `async_discovered_service_info(hass, connectable=False)`. It prefers `service_info.advertisement.local_name` where present, then Home Assistant's resolved `service_info.name`; `BLEDevice.name` is not treated as the advertised name. It waits up to 20 seconds for a newer advertisement from the runtime address using `bluetooth.async_process_advertisements` with an address matcher, `connectable=False`, and `BluetoothScanningMode.ACTIVE`. Home Assistant's callback matcher defaults to connectable-only if that flag is omitted, so the explicit `False` allows the general advertisement path. The address stays in memory. The predicate rejects cached replay using both the candidate and wait-start observation times. **Only after a fresh packet** does the probe call `async_ble_device_from_address(..., connectable=True)` to check for a GATT-capable path. It then connects through Home Assistant Bluetooth, lists service/characteristic UUIDs and properties, and disconnects. It does not read characteristics, write characteristics, subscribe to notifications, pair, or retrieve records. Home Assistant chooses an eligible adapter/proxy. See [official Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/), [Home Assistant's callback manager](https://github.com/home-assistant/core/blob/dev/homeassistant/components/bluetooth/manager.py), and [Bluetooth service-info representation](https://github.com/Bluetooth-Devices/habluetooth/blob/main/src/habluetooth/models.py), reviewed 2026-09-26.

The first development build was tried repeatedly on the real Home Assistant system and returned `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` The next targeted-wait build was installed and returned `No known FORA 6 CONNECT candidate is available for targeted active scanning; first observe it in Home Assistant Bluetooth.` This occurred despite a prior Advertisement Monitor observation. That second result stopped before the targeted wait; neither result reached a GATT connection or transmitted a FORA operation. A prior UI row does not establish current presence in the general cache. This does not establish a meter or proxy GATT failure. The general-discovery revision has not yet been tested on the real system.

To install and invoke this **development build** in the user's private Home Assistant instance:

1. Replace the installed `<Home Assistant config>/custom_components/fora6_connect/` directory with the entire repository directory `custom_components/fora6_connect/`, including `__init__.py`, `gatt_probe.py`, `const.py`, `manifest.json`, `services.yaml`, `translations/en.json`, and the other existing files in that directory. Do not copy `tests/` or private captures.
2. Add a top-level entry to Home Assistant's `configuration.yaml` if absent:

   ```yaml
   fora6_connect:
   ```

3. Check the Home Assistant configuration and restart Home Assistant Core so the revised Python module loads. Leave the Lounge ESPHome proxy in **Auto** mode. Make the meter available in its normal Bluetooth-advertising state. The candidate must be present in Home Assistant's current general discovery cache; a row seen previously may have expired. The missing-candidate error includes only general discovery, matching-name, and connectable-scanner counts.
4. Open **Developer Tools → Actions**, select `fora6_connect.probe_gatt`, leave target/data empty, and perform the action once. It returns a JSON-compatible response. A privacy-safe success response has keys such as `device_found`, `local_name`, `active_scan_requested`, `fresh_advertisement_observed`, `connectable_device_resolved`, `connectable_scanner_count`, `connection_successful`, `connected_via_ha_bluetooth`, `gatt_service_count`, `services`, `expected_gatt`, and `disconnected_cleanly`. Service counts and UUID/property lists must be taken from the actual response, not filled in from the iPhone observation.
5. Privately check **Settings → Connectivity → Bluetooth → Connection Monitor** if the proxy path needs confirmation; Home Assistant selects the connection path and the service response does not assert that Lounge was used. Share only the action's sanitized response or sanitized error text. Do not share raw Home Assistant logs, Bluetooth addresses, proxy identifiers, serial values, or health measurements.

The action raises a clear privacy-safe service error for no current general candidate, no fresh advertisement, no connectable scanner/device, connection-slot exhaustion, connection failure, GATT discovery failure, or incomplete disconnect. A cached Advertisement Monitor row alone is insufficient proof of a live packet. It does not clear Bluetooth history, register its own callback, or issue a separate broad scan request. The probe uses a new Bleak client on each invocation, disables service caching for this inventory, sets a 20-second connection timeout, and always attempts a clean disconnect. Its return data contains public GATT UUIDs/properties and no private Bluetooth address. Privacy-safe phase messages are available at DEBUG for `custom_components.fora6_connect.gatt_probe`; do not share unredacted platform logs.

## Integration scaffold

The custom integration manifest has no `config_flow` flag or Bluetooth discovery matcher. This prevents a production user flow from claiming an unverified meter identity. It has `bluetooth_adapters` and `bluetooth` dependencies for the development probe. No entity platform is forwarded. `translations/en.json` provides the development action's UI text. `strings.json` is retained as an empty requested scaffold file, not used at runtime.

The `0.0.0` manifest version is a development placeholder needed for a custom integration, not a release number. HACS packaging and brand assets are deferred to Stage 10.

References checked during bootstrap: [Home Assistant integration manifests](https://developers.home-assistant.io/docs/creating_integration_manifest/), [custom integration localization](https://developers.home-assistant.io/docs/internationalization/custom_integration/), [Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), and [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/). Recheck them at the relevant later stages because APIs and publication requirements can change.
