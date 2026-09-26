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

These checks use mocks and do not prove that a real Home Assistant instance can connect to the meter. Record the real Stage 1B probe outcome separately after running it; HACS and production validation remain later-stage work.

## Temporary Stage 1B Home Assistant GATT probe

This development action only requests an on-demand active scan, resolves a fresh `FORA 6 CONNECT` advertisement, connects through Home Assistant Bluetooth, lists service/characteristic UUIDs and properties, then disconnects. It does not read characteristics, write characteristics, subscribe to notifications, pair, or retrieve records. Home Assistant chooses an eligible adapter/proxy; the code does not select Lounge or a local adapter by address. Home Assistant Core must expose `bluetooth.async_request_active_scan`; [current official Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/) describes this one-shot scan for `Auto` scanners. [Home Assistant Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/) recommends the `bluetooth_adapters` dependency and a connection timeout of at least 10 seconds. The [current bleak-retry-connector usage guide](https://bleak-retry-connector.readthedocs.io/en/latest/usage.html) documents the connection call used here. These sources were checked on 2026-09-26.

To install and invoke this **development build** in the user's private Home Assistant instance:

1. Copy the entire repository directory `custom_components/fora6_connect/` to `<Home Assistant config>/custom_components/fora6_connect/`. Include `__init__.py`, `gatt_probe.py`, `const.py`, `manifest.json`, `services.yaml`, `translations/en.json`, and the other existing files in that directory. Do not copy `tests/` or private captures.
2. Add a top-level entry to Home Assistant's `configuration.yaml` if absent:

   ```yaml
   fora6_connect:
   ```

3. Check the Home Assistant configuration and restart Home Assistant so the custom integration loads and registers the action. Leave the Lounge ESPHome proxy in **Auto** mode. Make the meter available in its normal Bluetooth-advertising state.
4. Open **Developer Tools → Actions**, select `fora6_connect.probe_gatt`, leave target/data empty, and perform the action once. It returns a JSON-compatible response. A privacy-safe success response has keys such as `device_found`, `local_name`, `active_scan_requested`, `fresh_advertisement_observed`, `connectable_device_resolved`, `connectable_scanner_count`, `connection_successful`, `connected_via_ha_bluetooth`, `gatt_service_count`, `services`, `expected_gatt`, and `disconnected_cleanly`. Service counts and UUID/property lists must be taken from the actual response, not filled in from the iPhone observation.
5. Privately check **Settings → Connectivity → Bluetooth → Connection Monitor** if the proxy path needs confirmation; Home Assistant selects the connection path and the service response does not assert that Lounge was used. Share only the action's sanitized response or sanitized error text. Do not share raw Home Assistant logs, Bluetooth addresses, proxy identifiers, serial values, or health measurements.

The action raises a clear privacy-safe service error for no fresh advertisement, no connectable scanner/device, connection-slot exhaustion, connection failure, GATT discovery failure, or incomplete disconnect. A cached Advertisement Monitor row alone is insufficient. The probe clears only Home Assistant's advertisement deduplication history for a previously cached candidate before listening for new packets; it does not clear discovery identity history or write to the meter. The probe uses a new Bleak client on each invocation, disables service caching for this inventory, sets a 20-second connection timeout, and always attempts a clean disconnect. Its return data contains public GATT UUIDs/properties and no private Bluetooth address.

## Integration scaffold

The custom integration manifest has no `config_flow` flag or Bluetooth discovery matcher. This prevents a production user flow from claiming an unverified meter identity. It has `bluetooth_adapters` and `bluetooth` dependencies for the development probe. No entity platform is forwarded. `translations/en.json` provides the development action's UI text. `strings.json` is retained as an empty requested scaffold file, not used at runtime.

The `0.0.0` manifest version is a development placeholder needed for a custom integration, not a release number. HACS packaging and brand assets are deferred to Stage 10.

References checked during bootstrap: [Home Assistant integration manifests](https://developers.home-assistant.io/docs/creating_integration_manifest/), [custom integration localization](https://developers.home-assistant.io/docs/internationalization/custom_integration/), [Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), and [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/). Recheck them at the relevant later stages because APIs and publication requirements can change.
