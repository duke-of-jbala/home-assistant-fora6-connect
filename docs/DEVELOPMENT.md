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

These checks use mocks and do not prove that a real Home Assistant instance can connect to the meter. Real tests of the preceding builds stopped at discovery; retest this manual-address development revision separately. HACS and production validation remain later-stage work.

## Temporary Stage 1B Home Assistant GATT probe

This development action requires the user to supply the privately observed FORA Bluetooth address at invocation. It does **not** consult Home Assistant's current discovery cache. It waits up to 20 seconds for an advertisement from that address using `bluetooth.async_process_advertisements` with `connectable=False` and `BluetoothScanningMode.ACTIVE`. Home Assistant's targeted active-scan scheduler can activate Auto scanners for the wait. The predicate requires the supplied address and an observation time newer than the wait start, so replayed cache history is insufficient. If the live packet includes a local name, it must equal `FORA 6 CONNECT` after removing trailing NUL padding; a missing local name may proceed because the user selected the address from a previously identified Advertisement Monitor row. A different resolved `service_info.name` or `BLEDevice.name` does not override the packet local name. The response reports the normalized packet local name, or `null` when absent, and `advertised_name_confirmed` separately. The read-only GATT metadata comparison gives additional identity evidence, especially the custom 1523/1524 pair; it is not a production identity decision. **Only after a live packet** does the probe call `async_ble_device_from_address(..., connectable=True)` and attempt a fresh retry-safe, no-pair connection. It enumerates UUIDs/properties and disconnects; it does not read or write characteristics, subscribe, pair, or retrieve records. Home Assistant selects an eligible adapter/proxy. See [official Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/), reviewed 2026-09-26.

The user separately opened the `FORA 6 CONNECT` row in Home Assistant's Advertisement Monitor and saw **five trailing NUL characters** in the popup's Complete Local Name. The popup is a manual UI observation, not the probe's `async_process_advertisements` result. The development action still failed with `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` The probe now strips only trailing NUL padding before comparing a packet local name; that can resolve a name mismatch **if** the probe receives such a packet, but the popup does not prove it did. A separate active-wait/API-path issue remains possible. The action has not reached a Home Assistant GATT connection in this observation.

The first development build was tried repeatedly on the real Home Assistant system and returned `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` The targeted-wait build then stopped at its cached-candidate gate. The later general-discovery build reported `general discoveries: 214; name matches: 0; connectable scanners: 2` and also stopped before its targeted wait. Home Assistant Bluetooth and two connectable scanners were operational; FORA was absent by name from the current cache in that run. The meter advertises intermittently with a short transfer window. The user reports that the development action still failed to obtain or accept a fresh advertisement when the Advertisement Monitor popup was inspected manually. These results do not establish a meter, proxy, or GATT failure; no HA GATT connection or FORA operation occurred. Production automatic discovery remains deferred to Stage 6. The NUL-normalization correction has not been tested on the real system.

To install and invoke this **development build** in the user's private Home Assistant instance:

1. Replace the installed `<Home Assistant config>/custom_components/fora6_connect/` directory with the entire repository directory `custom_components/fora6_connect/`, including `__init__.py`, `gatt_probe.py`, `const.py`, `manifest.json`, `services.yaml`, `translations/en.json`, and the other existing files in that directory. Do not copy `tests/` or private captures.
2. Add a top-level entry to Home Assistant's `configuration.yaml` if absent:

   ```yaml
   fora6_connect:
   ```

3. Check the Home Assistant configuration and restart Home Assistant Core so the revised Python module and action field load. Leave the Lounge ESPHome proxy in **Auto** mode. Make the meter available in its normal Bluetooth-advertising state.
4. In **Settings → Connectivity → Bluetooth → Advertisement Monitor**, privately copy the Bluetooth address from the row already positively identified as `FORA 6 CONNECT`. Do not place it in Git, screenshots for public sharing, or messages to ChatGPT.
5. Open **Developer Tools → Actions**, select `fora6_connect.probe_gatt`, enter that address in the required **Bluetooth address (private)** field, leave target empty, and perform the action during the meter's Bluetooth transfer window. It returns a JSON-compatible response. A privacy-safe success response has keys such as `device_found`, `local_name`, `advertised_name_confirmed`, `active_scan_requested`, `fresh_advertisement_observed`, `connectable_device_resolved`, `connectable_scanner_count`, `connection_successful`, `connected_via_ha_bluetooth`, `gatt_service_count`, `services`, `expected_gatt`, and `disconnected_cleanly`. Service counts and UUID/property lists must come from the actual response.
6. Privately check **Settings → Connectivity → Bluetooth → Connection Monitor** if the proxy path needs confirmation; Home Assistant selects the connection path and the service response does not assert that Lounge was used. Share only the action's sanitized response or sanitized error text. Do not share raw Home Assistant logs, Bluetooth addresses, proxy identifiers, serial values, or health measurements.

The action raises privacy-safe errors for a missing address, no fresh advertisement, no connectable scanner/device, connection-slot exhaustion, connection failure, GATT discovery failure, or incomplete disconnect. A cached Advertisement Monitor row alone is insufficient proof of a live packet. It does not clear Bluetooth history, register its own callback, or issue a separate broad scan request. The supplied address remains only in memory; it is not persisted, returned, or logged by this integration. The probe uses a new Bleak client per invocation, disables service caching for this inventory, sets a 20-second connection timeout, and attempts a clean disconnect. Privacy-safe phase messages are available at DEBUG for `custom_components.fora6_connect.gatt_probe`; do not share unredacted platform logs.

## Integration scaffold

The custom integration manifest has no `config_flow` flag or Bluetooth discovery matcher. This prevents a production user flow from claiming an unverified meter identity. It has `bluetooth_adapters` and `bluetooth` dependencies for the development probe. No entity platform is forwarded. `translations/en.json` provides the development action's UI text. `strings.json` is retained as an empty requested scaffold file, not used at runtime.

The `0.0.0` manifest version is a development placeholder needed for a custom integration, not a release number. HACS packaging and brand assets are deferred to Stage 10.

References checked during bootstrap: [Home Assistant integration manifests](https://developers.home-assistant.io/docs/creating_integration_manifest/), [custom integration localization](https://developers.home-assistant.io/docs/internationalization/custom_integration/), [Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), and [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/). Recheck them at the relevant later stages because APIs and publication requirements can change.
