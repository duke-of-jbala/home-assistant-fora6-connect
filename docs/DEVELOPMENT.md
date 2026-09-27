# Development

**Stage 6B3 physical validation:** the user restarted HA and confirmed the existing entry, single device, single unavailable uric-acid entity, Bluetooth connection, and GD82/ForaCare metadata were preserved; no bogus serial or discovery Add card appeared. A privacy-safe storage check found the ConfigEntry unique ID now uses canonical lowercase colon MAC format. No actual value was shared or recorded. The in-place migration is complete for this meter.

**Stage 6B3:** [The factory MAC migration plan](STAGE6B3_FACTORY_MAC_IDENTITY.md) specifies offline-tested setup migration and the controlled user-run HA reload check. It requires no device removal, BLE operation, Stage 7 sync, or disclosure of the private MAC.

**Stage 6B2:** [The bounded System ID plan](STAGE6B2_SYSTEM_ID_REVIEW.md) specifies the manual `probe_system_id` and `probe_system_id_stability` actions, expected privacy-safe outputs, and user-run ON/repeat/OFF-ON procedure. Only `0x180A`/`0x2A23` is read; no FORA write, pairing, automatic discovery/sync, or production identity change is added.

**Stage 6B1:** [The metadata/rediscovery follow-up](STAGE6B1_REDISCOVERY_LOCATOR_FIX.md) adds a known-locator Config Flow guard, rejects a generic GATT serial placeholder for new setups, and refreshes the existing registry metadata on reload without BLE I/O. A controlled HA reload/rediscovery regression is the next gate; a separate private identity review is needed before migrating the placeholder-backed entry. No production sync is present.

## Stage discipline

Read `AGENTS.md`, `CURRENT_STATUS.md`, and `PROTOCOL.md` before implementation. Stage 1B has a development-only GATT probe, and Stage 1C has a separately invoked notification-metadata observer. Stage 2D added HA-independent frame/project/scaling helpers to `protocol.py`; Stage 2E's custom wake/project identity probe succeeded on the real meter. Stage 2F's corrected one-slot record-response probe also succeeded with the meter ON. Stage 2G parsing remains offline. Stage 6B now enables a guarded discovery/setup flow and one initially unavailable uric-acid entity; production synchronization and polling remain inactive.

**Stage 4 complete:** `bluetooth.py` contains the reusable Home Assistant session, and the two bounded `protocol_probe.py` actions use it. Mock validation and user-run physical regression are complete for the authorized scope. The user reported successful identity and bounded record runs on the real GD82 with the meter ON; both stopped notifications and disconnected cleanly. [The Stage 4 transport record](STAGE4_BLUETOOTH_TRANSPORT.md) records the API, safe error codes, cleanup, and regression results. No production discovery, record synchronization, or entity is active. Stages 2A–2G remain complete for their authorized scopes while unresolved semantics remain open.

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

`custom_components/fora6_connect/protocol.py` validates the live-confirmed eight-byte request/response envelope without importing Home Assistant, Bleak, or ESPHome. Its original fixed request constructors reproduce the captured `0x22` wake and `0x24` project-query frames. The corrected Stage 2F constructors select `User1 = 1` for `0x2B`, `0x25`, and `0x26` at raw index zero, matching both static builders and the successful app's wire requests. The raw-slot-count parser does not decode record data. The project parser extracts the confirmed little-endian `0x4183` identifier. A separate `scale_td4183_uric_acid` helper divides an already identified uric-acid raw integer by ten; it cannot identify an analyte or locate a numeric field in a record. Neither the sanitized Stage 2C summary nor the current Stage 2F evidence establishes a public record-field or timestamp decoder. Tests use only non-private protocol frames and synthetic data. See [the Stage 2F evidence review](STAGE2F_TD4183_RECORD_PROBE.md).

## Temporary Stage 2E Home Assistant identity probe

The development-only `fora6_connect.probe_protocol_identity` action is installed with the same complete integration directory and Core restart procedure described above. Follow the [controlled invocation guide](STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md) for its privacy rules. It subscribes only to custom `1524`, sends the captured `0x22` and `0x24` requests once each with `response=True`, validates each matching checksummed response, requires project `0x4183`, then unsubscribes and disconnects. The `Write` property supports this explicit write-with-response choice; it is not claimed as a universal protocol rule. **The real Home Assistant run succeeded while the meter was ON.** It did not request a record or require a new measurement.

## Temporary Stage 2F single-slot Home Assistant record probe

**Stage 2F physical validation is complete.** The first committed constructors used `CurrentUser = 0` but the retained successful Stage 2C app traffic used `User1 = 1`. The corrected action was subsequently run against the real GD82 with the meter ON and completed the bounded read. Do not invoke `fora6_connect.probe_protocol_record` again as part of Stage 2G. Keep the address, platform logs, record bytes, health value, and measurement time private.

This action requires the same captured `0x22`/`0x24`/`0x4183` identity gate, then requests User1 raw slot metadata once with `0x2B`, followed by **only raw index zero** using `0x25` and `0x26` once each if a slot exists. Every write uses `response=True`; the action validates each matching eight-byte response but does not return or persist record payload bytes. Its result includes status flags such as `record_metadata_response_valid`, `requested_record_index`, `record_part_1_valid`, `record_part_2_valid`, `record_pair_complete`, `record_retrieval_confirmed`, `error_stage`, `error_code`, and cleanup outcomes. `analyte_identified`, `measurement_field_decoded`, and `uric_acid_scaling_applied` remain false. The action cannot send `0x33`, request another index, loop, retry, or perform production synchronization. A complete response pair establishes frame reception only, not a decoded health record. See [the Stage 2F evidence review](STAGE2F_TD4183_RECORD_PROBE.md).

**Real result, user-supplied:** with the meter ON, wake/project/`0x4183`, User1 `0x2B`, and User1/raw-index-zero `0x25`/`0x26` all validated; notification stop and disconnect were clean. `0x33` was not required for this tested bounded read. Two earlier invocations failed at wake write and subscription before record requests. The successful result exposed no analyte, value, or timestamp. Stage 2G must keep the live transport and semantic response unchanged.

## Stage 2G offline evidence dependency

The actual retained private 1.7.6/1.7.9 decompilation paths were not preserved in durable notes, and a suggested workspace path was absent. The retained private HCI import capture was inspected in place; [the Stage 2G evidence map](STAGE2G_TD4183_RECORD_SCHEMA.md) records sanitized byte comparisons, the known response envelope, and opaque payload bytes. Exact timestamp, raw numeric, analyte, status, and `0x2F` interpretation roles still need line-specific parser evidence and private known-record validation. No semantic parser or new test fixture was added. The user requested a pause of parser implementation until the decompilations are located. The exact next gate is locating them and resuming Stage 2G on the user's direction; do not use a physical meter or expose the real value.

**Subsequent Stage 2G implementation:** The retained private sources became accessible and the pause condition was resolved. Both versions' TD4183 path supports the exact fields now documented in [the Stage 2G schema](STAGE2G_TD4183_RECORD_SCHEMA.md). `protocol.py` parses `0x25` into minute-precision meter-local fields and a transmitted flag, and `0x26` into raw value, analyte selector, category/QC, auxiliary byte, and invalid sentinel. It preserves opaque payload bits, rejects invalid calendar fields without attaching a timezone, and leaves unsupported type selectors unidentified. `tests/test_record_schema.py` uses only artificial values and a future date. A private offline run against the retained capture verified the uric-acid index-zero and hematocrit/QC sentinel companion classifications without printing values or timestamps. The live Home Assistant action is unchanged. **Exact next gate:** review Stage 2G, then separately authorize Stage 3 or a focused evidence follow-up; no physical BLE test or real decoded-result exposure.

**Stage 3 offline model and fixtures:** `models.py` combines already parsed `0x25`/`0x26` parts without changing the live action. `tests/fixtures_td4183.py` generates ten synthetic response pairs from artificial timestamps, values, selector/category bits, and the observed checksum rule; `tests/test_record_model.py` validates the combined model and malformed timestamp path. [The Stage 3 record](STAGE3_RECORD_MODEL_AND_FIXTURES.md) details fixture provenance and unresolved semantics. No fixture is a captured GD82 frame. **Exact next gate:** separately authorize Stage 4 production Bluetooth transport; no physical BLE test or decoded real-result exposure follows from Stage 3.

**Stage 4 transport and physical regression:** `tests/test_bluetooth_transport.py` exercises the reusable session with HA/Bleak mocks. Existing `test_protocol_probe.py` and `test_record_probe.py` assert the established result schemas and exact write order. The user reports both physical regressions succeeded with the GD82 ON and cleanup was clean. No raw response, address, or health value appears in action results or transport errors.

**Stage 5 product/entity model:** `measurement.py` maps validated records to an immutable pure-Python product measurement; `sensor.py` provides an inert state replacement/native-value policy and Stage 6 stable-identity key interface. Tracked evidence establishes uric-acid `/10` scaling but not the displayed unit, so no numeric HA sensor or device registration is created. Other analytes remain non-numeric; QC, AC, and PC categories remain preserved. Tests use synthetic fixtures only. **Exact next gate:** separately authorize Stage 6 device discovery/identity policy or a focused evidence follow-up for the uric-acid unit. Do not start Stage 6 automatically.

**Stage 5A unit follow-up:** [The Stage 5A record](STAGE5A_URIC_ACID_UNIT_EVIDENCE.md) establishes mg/dL as the app's unconverted uric-acid raw/10 base unit; its display preference may select µmol/L or mmol/L. The product model and General-category numeric mapper use only that mg/dL base. No HA entity or device is registered.

**Stage 6A discovery/identity review:** [The Stage 6A record](STAGE6A_DISCOVERY_IDENTITY_POLICY.md) classifies normalized-name/advertised-service/connectability matching as candidate selection only. Project `0x4183` confirms the model path but is not unique. The observed `0x180A` GATT inventory includes readable `0x2A25` Serial Number String and `0x2A23` System ID; values were not read. Address and manufacturer-data identity remain unresolved. No manifest matcher, callback, Config Flow, or persistent ID is active. **Exact next gate:** separately authorize passive comparison and/or a bounded Stage 6A1 serial read before full Stage 6 implementation.

**Stage 6A1 bounded serial probe:** [The Stage 6A1 record](STAGE6A1_SERIAL_IDENTITY_READ.md) documents manual `fora6_connect.probe_serial_identity`. It reads only Device Information `0x2A25` once and returns structural booleans, never serial text, digest, length, or address. The user-run real GD82 test with the meter ON returned usable UTF-8 text and clean disconnect. This alone does not prove stability or uniqueness.

**Stage 6A1b private comparison:** [The Stage 6A1b record](STAGE6A1B_SERIAL_STABILITY.md) documents `fora6_connect.probe_serial_stability`: `set_reference` and `compare` use the same bounded read, with one private exact-byte reference in HA process memory and equality-only public output. User-run comparisons matched immediately and after a meter OFF/ON cycle, with clean disconnects. The serial remains unpublished; stability is shown only for that meter and tested conditions.

**Stage 6A1c identity policy:** [The evidence review](STAGE6A1C_SERIAL_IDENTITY_POLICY.md) combines Bluetooth SIG instance-serial semantics, manufacturer/manual limits, retained app paths, physical stability, and HA unique-ID guidance. It conditionally selects exact validated `0x2A25` text for a future domain-scoped config-entry/device identifier with fail-closed collision handling. Address remains a runtime locator. **Exact next gate:** separately authorize Stage 6B guarded Config Flow implementation; no matcher, entry, device, or entity was added here.

## Temporary Stage 1C Home Assistant notification observer

The development-only `fora6_connect.observe_notifications` action resolves a privately supplied address through Home Assistant, connects without pairing, and attempts `start_notify` independently on Glucose `2A18`, Context `2A34`, and custom `1524`. If any subscription succeeds, it observes for 30 seconds, stops only successful subscriptions, and disconnects. It returns privacy-safe subscription outcomes, sanitized error classes/structured codes, notification counts, payload-length metadata, and separate stop/disconnect outcomes. Raw callback bytes and in-memory distinct-payload digests are never returned or persisted. Stack-managed CCCD configuration required by `start_notify`/`stop_notify` is the only authorized descriptor activity; the integration does not read/write an application characteristic, call pairing, issue RACP, retrieve records, or decode measurements.

**Real Stage 1C result, user-supplied:** the first installed build failed at `2A18` and aborted before the other subscriptions. The revised build then attempted all three: `2A18` and `2A34` failed with sanitized `BleakError`, while custom `1524` subscribed. No notification arrived during 30 seconds, despite the user pressing arrow/navigation keys while the meter displayed its only existing uric-acid result. No new measurement was taken. Unsubscription and disconnect were clean. Passive observation of this existing uric-acid record is complete. It does not establish behavior for other analytes or whether a request is needed to produce custom notifications. The [Bluetooth SIG Glucose Profile 1.0.1](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/GLP_v1.0.1/out/en/index-en.html) bonding/security requirement makes missing security a strong hypothesis for standard subscription failures; proxy/descriptor problems remain possible. Pairing is not authorized.

The Stage 1C action remains available for controlled development diagnostics. The completed Stage 1 review deferred fresh Auto-mode advertisement and Bluetooth address identity behavior to Stage 6 production discovery/duplicate-device handling, and the selected scanner/proxy to Stage 9 end-to-end proxy validation. Manufacturer-data meaning remains unknown. The separate Stage 1C observation of a connection while the display appeared off must not be merged with successful Stage 2E and 2F tests, which ran with the meter ON. **Exact next gate: Stage 2G offline record-schema analysis; no physical BLE test.**

## Integration scaffold

The Stage 6B manifest now enables a narrow connectable name/`0x1808` candidate matcher; the Config Flow checks exact normalized name plus `0x180A` and performs user-confirmed active model/serial identification. Entry setup forwards one inert sensor platform. `translations/en.json` provides runtime flow/action text; `strings.json` mirrors the flow translation source for development. The `bluetooth_adapters` and `bluetooth` dependencies remain, without direct adapter selection.

The `0.0.0` manifest version is a development placeholder needed for a custom integration, not a release number. HACS packaging and brand assets are deferred to Stage 10.

References checked during bootstrap: [Home Assistant integration manifests](https://developers.home-assistant.io/docs/creating_integration_manifest/), [custom integration localization](https://developers.home-assistant.io/docs/internationalization/custom_integration/), [Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), and [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/). Recheck them at the relevant later stages because APIs and publication requirements can change.

## Stage 6B guarded setup

[The Stage 6B record](STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md) describes the new manifest candidate matcher, confirmation forms, existing Stage 4 project exchange and Stage 6A1 serial read, exact serial unique ID, locator collision policy, and inert uric-acid platform. Synthetic tests and user-run real Home Assistant discovery/setup validation succeeded. One GD82 device and one unavailable uric-acid entity were created; no serial/address appeared in the observed UI. OFF/ON did not create another entry. The explicit duplicate-abort flow was not exercised. No new application command, record read, polling, or production sync was run. **Exact next gate:** separately authorize Stage 7 synchronization design and implementation.

## Stage 7A offline history review

[Stage 7A](STAGE7A_HISTORY_TRAVERSAL_DESIGN.md) traces both private TD4183 app handlers and the already sanitized `1 → 0 → 1` import evidence. It documents raw `0x2B` count/newest fields, the last-slot single/multi heuristic, low-level pair order, and why latest ordering and deduplication remain unresolved. [The Stage 7 gate record](STAGE7_HISTORY_SYNC.md) keeps the intended synchronization policy separate from implemented behavior. No production sync, history test, or fixture was added. **Exact next gate:** separately authorize implementation and user-run validation of the bounded Stage 7B probe; no broad traversal or polling.

## Stage 7B bounded development action

`fora6_connect.probe_history_window` is manually invoked with only the private runtime address. [Its fixed procedure](STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) confirms project `0x4183`, queries User1 metadata once, and reads User1 raw indexes `1 → 0 → 1` only when raw count equals two. The user-run real GD82 test passed the count gate, all six part responses, repeated index-one equality, and clean cleanup. The action returns no record, value, timestamp, serial, address, or payload digest and does not touch coordinator or sensor state. **Stage 7B is complete for its bounded physical scope. Exact next proposed gate:** separately authorize Stage 7C bounded semantic pair confirmation; no general traversal or production sync is authorized.

## Stage 7C bounded semantic action

`fora6_connect.probe_history_semantics` is a separate manual action with only the private runtime address. [Its fixed procedure](STAGE7C_SEMANTIC_PAIR_CONFIRMATION.md) repeats the Stage 7B count-two `1 → 0 → 1` sequence, parses all pairs through the existing pure protocol/model layer, and reports only safe classification and equality flags. A valid semantic mismatch returns false flags; a transport/protocol failure stops subsequent requests. The action does not feed coordinator or sensor state or persist health data. Synthetic tests passed; Codex performs no physical test. **Exact next gate:** user-run Stage 7C confirmation after review, then separate interpretation of the sanitized result.

The user-run physical Stage 7C result confirmed the expected index-zero uric-acid/General/valid classification, both index-one hematocrit/QC/invalid-sentinel classifications, and repeated semantic equality, with clean cleanup. Stage 7C is complete for this bounded scope. **Later follow-up:** Stage 6B3 resolved the generic DIS placeholder identity for this configured meter through validated factory-MAC fallback migration. Stage 7C added no production sync.

## Stage 7D offline review

[The Stage 7D evidence record](STAGE7D_GENERAL_TRAVERSAL_DEDUP_REVIEW.md) compares both retained TD4183 handlers and the app's local record lookup. It documents the unavailable/decompiler-damaged import loops, the unused wire newest-index field in the TD4183 handler, and the absence of a collision-safe dedup/resume key. No integration source, action, fixture, or physical meter state changed. A separately authorized Stage 7E read-only four-slot probe is the next proposed evidence gate if the meter naturally reaches that count.

## Stage 7E physical validation

Stage 7E completed its fixed count-four probe on the real GD82 in one state. If invoked in the immediate post-measurement Bluetooth-flashing state, the observed attempt connected but failed notification subscription before any FORA command; manual power-on restored the successful protocol path. The successful run used only indexes `3 → 0 → 1 → 2 → 3`. This observation does not establish why subscription differs by state.
