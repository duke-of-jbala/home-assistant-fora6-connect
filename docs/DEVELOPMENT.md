# Development

## Stage discipline

Read `AGENTS.md`, `CURRENT_STATUS.md`, and `PROTOCOL.md` before implementation. Stage 1B has a development-only GATT probe, and Stage 1C has a separately invoked notification-metadata observer. Stage 2D added HA-independent frame/project/scaling helpers to `protocol.py`; Stage 2E's custom wake/project identity probe succeeded on the real meter. Stage 2F adds a separately invoked, physically untested one-slot record-response probe. Record decoding, production discovery/config flow, synchronization, and entities remain inactive.

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

**Real Stage 1B result, user-supplied:** the direct-connect action resolved a connectable FORA BLEDevice, connected through Home Assistant, returned five GATT services with all expected Glucose and FORA custom metadata/properties, and disconnected cleanly. Its normalized local name was `FORA 6 CONNECT`; two connectable scanners were reported, but the selected scanner/adapter was not identified. See the [sanitized inventory](PROTOCOL.md). No characteristic I/O, notification, pairing, or FORA application operation occurred. Stage 1B transport/GATT validation succeeded. The later Stage 1C observation and Stage 1 evidence review are complete; Stage 2C captured proprietary app traffic on the real GD82; Stage 2D added offline helpers; Stage 2E's bounded Home Assistant identity action subsequently succeeded with the meter ON. Auto-mode discovery remains unresolved and is deferred to Stage 6.

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

## Stage 2D offline protocol helpers

`custom_components/fora6_connect/protocol.py` validates the live-confirmed eight-byte request/response envelope without importing Home Assistant, Bleak, or ESPHome. Its original fixed request constructors reproduce the captured `0x22` wake and `0x24` project-query frames. The Stage 2F offline review added fixed, statically traced current-user/raw-index-zero constructors for `0x2B`, `0x25`, and `0x26`, plus a raw-slot-count parser; these do not decode record data. The project parser extracts the confirmed little-endian `0x4183` identifier. A separate `scale_td4183_uric_acid` helper divides an already identified uric-acid raw integer by ten; it cannot identify an analyte or locate a numeric field in a record. Neither the sanitized Stage 2C summary nor the current Stage 2F evidence establishes a public record-field or timestamp decoder. Tests use only non-private protocol frames and synthetic data. See [the Stage 2F evidence review](STAGE2F_TD4183_RECORD_PROBE.md).

## Temporary Stage 2E Home Assistant identity probe

The development-only `fora6_connect.probe_protocol_identity` action is installed with the same complete integration directory and Core restart procedure described above. Follow the [controlled invocation guide](STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md) for its privacy rules. It subscribes only to custom `1524`, sends the captured `0x22` and `0x24` requests once each with `response=True`, validates each matching checksummed response, requires project `0x4183`, then unsubscribes and disconnects. The `Write` property supports this explicit write-with-response choice; it is not claimed as a universal protocol rule. **The real Home Assistant run succeeded while the meter was ON.** It did not request a record or require a new measurement.

## Temporary Stage 2F single-slot Home Assistant record probe

Copy the **entire updated** `custom_components/fora6_connect/` directory to the Home Assistant configuration's `custom_components/fora6_connect/`, replacing the prior development copy. Keep the existing `fora6_connect:` entry in `configuration.yaml` (add it only if absent), then restart Home Assistant Core. The address remains private and runtime-only. With the real meter ON and its existing Bluetooth transfer window available, privately confirm its row in **Settings → Connectivity → Bluetooth → Advertisement Monitor** and copy the known address. In **Developer Tools → Actions**, select `fora6_connect.probe_protocol_record`, enter that address in **Bluetooth address (private)**, request the action response, and invoke it **once**. Do not make a new measurement. Share only the structured action result; do not share the address, platform logs, screenshots with identifiers, record bytes, a health value, or a measurement time. No physical Stage 2F run has yet been reported.

This action requires the same captured `0x22`/`0x24`/`0x4183` identity gate, then requests current-user raw slot metadata once with `0x2B`, followed by **only raw index zero** using `0x25` and `0x26` once each if a slot exists. Every write uses `response=True`; the action validates each matching eight-byte response but does not return or persist record payload bytes. Its result includes status flags such as `record_metadata_response_valid`, `requested_record_index`, `record_part_1_valid`, `record_part_2_valid`, `record_pair_complete`, `record_retrieval_confirmed`, `error_stage`, `error_code`, and cleanup outcomes. `analyte_identified`, `measurement_field_decoded`, and `uric_acid_scaling_applied` remain false. The action cannot send `0x33`, request another index, loop, retry, or perform production synchronization. A complete response pair establishes frame reception only, not a decoded health record. See [the Stage 2F evidence review](STAGE2F_TD4183_RECORD_PROBE.md).

## Temporary Stage 1C Home Assistant notification observer

The development-only `fora6_connect.observe_notifications` action resolves a privately supplied address through Home Assistant, connects without pairing, and attempts `start_notify` independently on Glucose `2A18`, Context `2A34`, and custom `1524`. If any subscription succeeds, it observes for 30 seconds, stops only successful subscriptions, and disconnects. It returns privacy-safe subscription outcomes, sanitized error classes/structured codes, notification counts, payload-length metadata, and separate stop/disconnect outcomes. Raw callback bytes and in-memory distinct-payload digests are never returned or persisted. Stack-managed CCCD configuration required by `start_notify`/`stop_notify` is the only authorized descriptor activity; the integration does not read/write an application characteristic, call pairing, issue RACP, retrieve records, or decode measurements.

**Real Stage 1C result, user-supplied:** the first installed build failed at `2A18` and aborted before the other subscriptions. The revised build then attempted all three: `2A18` and `2A34` failed with sanitized `BleakError`, while custom `1524` subscribed. No notification arrived during 30 seconds, despite the user pressing arrow/navigation keys while the meter displayed its only existing uric-acid result. No new measurement was taken. Unsubscription and disconnect were clean. Passive observation of this existing uric-acid record is complete. It does not establish behavior for other analytes or whether a request is needed to produce custom notifications. The [Bluetooth SIG Glucose Profile 1.0.1](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/GLP_v1.0.1/out/en/index-en.html) bonding/security requirement makes missing security a strong hypothesis for standard subscription failures; proxy/descriptor problems remain possible. Pairing is not authorized.

The Stage 1C action remains available for controlled development diagnostics. The completed Stage 1 review deferred fresh Auto-mode advertisement and Bluetooth address identity behavior to Stage 6 production discovery/duplicate-device handling, and the selected scanner/proxy to Stage 9 end-to-end proxy validation. Manufacturer-data meaning remains unknown. The separate Stage 1C observation of a connection while the display appeared off must not be merged with the successful Stage 2E test, which ran with the meter ON. **Exact next gate: one user-run physical Stage 2F action and review of its privacy-safe result.**

## Integration scaffold

The custom integration manifest has no `config_flow` flag or Bluetooth discovery matcher. This prevents a production user flow from claiming an unverified meter identity. It has `bluetooth_adapters` and `bluetooth` dependencies for the development probe. No entity platform is forwarded. `translations/en.json` provides the development action's UI text. `strings.json` is retained as an empty requested scaffold file, not used at runtime.

The `0.0.0` manifest version is a development placeholder needed for a custom integration, not a release number. HACS packaging and brand assets are deferred to Stage 10.

References checked during bootstrap: [Home Assistant integration manifests](https://developers.home-assistant.io/docs/creating_integration_manifest/), [custom integration localization](https://developers.home-assistant.io/docs/internationalization/custom_integration/), [Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), and [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/). Recheck them at the relevant later stages because APIs and publication requirements can change.
