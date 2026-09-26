# Development

## Stage discipline

Read `AGENTS.md`, `CURRENT_STATUS.md`, and `PROTOCOL.md` before implementation. Stage 1B has a development-only GATT probe, and Stage 1C has a separately invoked notification-metadata observer. Protocol decoding, production discovery/config flow, synchronization, and entities remain inactive.

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

These checks use mocks; the separately reported real direct-connect action confirms Home Assistant-side GATT connection, inventory, and disconnect. It does not confirm which scanner/adapter was selected. HACS and production validation remain later-stage work.

## Temporary Stage 1B Home Assistant GATT probe

This **development-only** action requires a privately supplied Bluetooth address from the positively identified `FORA 6 CONNECT` Advertisement Monitor row. It does not depend on a current discovery-cache candidate or a fresh advertisement callback. For the controlled test, temporarily set Lounge to **Active**, make the meter advertise, and confirm the row is visibly current/refreshing before invoking the action. Auto-mode discovery is unresolved separately; the code does not hard-code Lounge or any adapter.

The action immediately calls Home Assistant's `bluetooth.async_ble_device_from_address(hass, address, connectable=True)`. If no connectable BLEDevice resolves, it returns Home Assistant's outgoing-connection reachability explanation after redacting private identifiers. The [official Bluetooth API](https://developers.home-assistant.io/docs/core/bluetooth/api/) treats that explanation as human-readable and subject to change; the integration does not parse it. If resolution succeeds, optional `async_last_service_info(hass, address, connectable=False)` supplies only a normalized advertised-name diagnostic. It may be missing or stale and **does not gate GATT**. The action uses a fresh retry-safe, no-pair client with a 20-second connection timeout, enumerates GATT service and characteristic UUIDs/properties, compares them with prior iPhone evidence, and disconnects. It does not read or write characteristics, subscribe, pair, retrieve records, or parse measurements.

The user independently saw a FORA packet in Advertisement Monitor with a Complete Local Name padded by five trailing NULs. The packet was **not** returned by the action. The installed name-normalization and later deduplication/timestamp builds both timed out at their targeted advertisement wait. Neither reached BLEDevice resolution or GATT connection. Advertisement Monitor visibility and integration callback delivery are separate observations; the cause of those waits remains unknown. The direct-connect revision bypassed that gate solely to validate transport. Production automatic discovery remains Stage 6 work.

**Real Stage 1B result, user-supplied:** the direct-connect action resolved a connectable FORA BLEDevice, connected through Home Assistant, returned five GATT services with all expected Glucose and FORA custom metadata/properties, and disconnected cleanly. Its normalized local name was `FORA 6 CONNECT`; two connectable scanners were reported, but the selected scanner/adapter was not identified. See the [sanitized inventory](PROTOCOL.md). No characteristic I/O, notification, pairing, or FORA application operation occurred. Stage 1B transport/GATT validation succeeded; Stage 1 remains in progress for remaining discovery/raw notification observations, and Stage 2 is not authorized. Auto-mode discovery remains unresolved separately.

To install and invoke this build in the user's private Home Assistant instance:

1. Replace `<Home Assistant config>/custom_components/fora6_connect/` with the **entire** repository directory `custom_components/fora6_connect/`, including `__init__.py`, `gatt_probe.py`, `const.py`, `manifest.json`, `services.yaml`, `translations/en.json`, and all other files in that directory. Do not copy `tests/` or private captures.
2. If absent, add this top-level entry to Home Assistant's `configuration.yaml`:

   ```yaml
   fora6_connect:
   ```

3. Check Home Assistant configuration and restart Home Assistant Core to load the revised Python module and service metadata. Temporarily set the Lounge ESPHome proxy to **Active**. Make the meter available in its normal Bluetooth-advertising state.
4. In **Settings → Connectivity → Bluetooth → Advertisement Monitor**, confirm the `FORA 6 CONNECT` row is visibly current/refreshing. Privately copy its Bluetooth address. Do not place it in Git or shared screenshots/messages.
5. In **Developer Tools → Actions**, select `fora6_connect.probe_gatt`, enter the address in the required **Bluetooth address (private)** field, leave target empty, and perform the action during the meter's Bluetooth transfer window. A successful privacy-safe response includes `device_found`, normalized `local_name` if available, `last_service_info_available`, `connectable_device_resolved`, `connectable_scanner_count`, `gatt_connection_attempted`, `connection_successful`, `connected_via_ha_bluetooth`, actual `gatt_service_count` and `services`, `expected_gatt`, and `disconnected_cleanly`. It contains no Bluetooth address. A reachability error means a connectable path was not resolved for that invocation; it is not a GATT result.
6. If needed, privately check **Settings → Connectivity → Bluetooth → Connection Monitor** for the actual path. Home Assistant chooses it; the response does not assert Lounge was used. Share only the sanitized action response or error. Keep raw Home Assistant logs, addresses, proxy identifiers, serial values, and health measurements private. Return Lounge to its usual mode after the controlled test.

The address stays in memory and is not persisted, returned, or logged by this integration. The action registers no production discovery matcher, clears no advertisement history, starts no advertisement wait, and performs no characteristic I/O. Privacy-safe phase messages are available at DEBUG for `custom_components.fora6_connect.gatt_probe`; do not share unredacted platform logs.

## Temporary Stage 1C Home Assistant notification observer

The real Stage 1B direct-connect action already confirmed Home Assistant-side connection, expected GATT inventory, and clean disconnect. The new `fora6_connect.observe_notifications` action is **development-only** and has not yet been run against the real meter. It uses the privately supplied known address to resolve a connectable BLEDevice through Home Assistant, creates a fresh retry-safe client with `pair=False` and a 20-second connection timeout, and confirms the three observed Notify characteristics `2A18`, `2A34`, and custom `1524`. It starts notifications for each, observes for an initial **30 seconds**, stops every successful subscription, and disconnects in cleanup. No `2A52`/RACP subscription or command occurs.

`start_notify`/`stop_notify` may cause Bleak/Home Assistant to configure the Client Characteristic Configuration Descriptor (CCCD). That stack-managed descriptor activity is explicitly authorized for this Stage 1C gate. The integration does not call `read_gatt_char`, `write_gatt_char`, `write_gatt_descriptor`, pairing, or any FORA application operation. Raw callback bytes are hashed only in memory for distinct-payload counting; the action returns no bytes or digests and persists nothing. The privacy-safe result contains `device_found`, `connectable_device_resolved`, `connection_successful`, `connected_via_ha_bluetooth`, actual `observation_duration_seconds`, `subscriptions_started`, `notifications_observed`, each characteristic's UUID/subscription status/count/observed payload lengths/length counts/distinct-payload count, and `disconnected_cleanly`. Zero notifications is a successful observation and does not justify sending a command. See [Bleak's current notification API](https://bleak.readthedocs.io/en/latest/api/client.html) and [Home Assistant Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/).

To run the first controlled Stage 1C test privately:

1. Replace `<Home Assistant config>/custom_components/fora6_connect/` with this checkout's **entire** `custom_components/fora6_connect/` directory, including the new `notification_observer.py`, `__init__.py`, `services.yaml`, `translations/en.json`, and all other integration files. Keep the top-level `fora6_connect:` in `configuration.yaml` (add it if absent). Check configuration and restart Home Assistant Core.
2. Lounge may be temporarily **Active** because that mode previously exposed FORA in Advertisement Monitor. Make the meter available in its normal Bluetooth transfer state. Do not make a new health measurement solely to create notifications.
3. In **Settings → Connectivity → Bluetooth → Advertisement Monitor**, privately identify the `FORA 6 CONNECT` row and copy the known address. In **Developer Tools → Actions**, select `fora6_connect.observe_notifications`, enter that address in **Bluetooth address (private)**, leave target empty, and perform the action. Wait for its approximately 30-second observation window plus connection/cleanup time.
4. Share only the privacy-safe action result or safe error. Do not share the private address, raw notification bytes, screenshots/logs containing identifiers or measurements, or manufacturer payload. If no notifications arrive, report the zero counts. Return Lounge to its usual mode after the controlled test.

The action does not confirm which scanner/adapter Home Assistant selected. Fresh Auto-mode and production discovery remain separate work. Stage 1 remains in progress until the real notification result is reviewed; Stage 2 is not authorized.

## Integration scaffold

The custom integration manifest has no `config_flow` flag or Bluetooth discovery matcher. This prevents a production user flow from claiming an unverified meter identity. It has `bluetooth_adapters` and `bluetooth` dependencies for the development probe. No entity platform is forwarded. `translations/en.json` provides the development action's UI text. `strings.json` is retained as an empty requested scaffold file, not used at runtime.

The `0.0.0` manifest version is a development placeholder needed for a custom integration, not a release number. HACS packaging and brand assets are deferred to Stage 10.

References checked during bootstrap: [Home Assistant integration manifests](https://developers.home-assistant.io/docs/creating_integration_manifest/), [custom integration localization](https://developers.home-assistant.io/docs/internationalization/custom_integration/), [Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), and [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/). Recheck them at the relevant later stages because APIs and publication requirements can change.
