# Protocol evidence register

This page separates historical discovery and static findings from the later [Stage 2C live protocol evidence](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) and Stage 2D offline implementation. The [ForaCare FAQ Rev 5.5](https://www.foracare.ch/wp-content/uploads/2023/03/3.1-BGM-FAQ_Rev5.5_230313.pdf) and [GD82 manual](https://switzerland.foracare.ch/wp-content/uploads/2021/10/FORA-6-Connect-GD82-4183D_meter-manual_311-4183400-070.pdf) were independently reviewed for Stage 2A. No private identifiers, health data, or raw captures are stored here.

## Confirmed for this project brief

- Product: FORA 6 Connect; model/variant: GD82.
- Documented BLE service UUID: `00001523-1212-efde-1523-785feabcd123`.
- Documented BLE characteristic UUID: `00001524-1212-efde-1523-785feabcd123`.
- The documentation describes the characteristic as supporting write and notify.

The manufacturer FAQ Q36 independently documents this UUID pair and Write/Notify metadata for ForaCare Bluetooth V4; Q37 identifies GD82 with iFORA HM. The UUID pair alone cannot establish that an observed BLE device is a FORA 6 Connect. Nordic demonstration apps reuse this UUID namespace with unrelated meanings, which are **not** FORA protocol evidence.

## Observed on the real meter — user-supplied, screenshots reviewed externally

The real meter's blue Bluetooth indicator was flashing when a generic iPhone BLE scanner displayed local name `FORA 6 CONNECT`. The scanner showed it as connectable, with close-range RSSI approximately −50 dBm. The iPhone connected successfully and marked the connection `BONDED`. This shows bonding occurred in that session; the scanner may have initiated it automatically. The Bluetooth SIG Glucose Profile specifies bonding/security for the standard Glucose path, but the iPhone observation does **not** show whether missing bonding/encryption caused the later Home Assistant `2A18`/`2A34` subscription failures. An iPhone CoreBluetooth identifier is not a physical MAC address and is not recorded here.

The iPhone scanner showed these GATT entries:

| Service | Characteristic | Observed properties |
| --- | --- | --- |
| Device Information `0x180A` | Readable standard Device Information fields, including model/firmware/etc. | Read |
| Glucose `0x1808` | Glucose Measurement `0x2A18` | Notify |
| Glucose `0x1808` | Glucose Measurement Context `0x2A34` | Notify |
| Glucose `0x1808` | Glucose Feature `0x2A51` | Read |
| Glucose `0x1808` | Record Access Control Point `0x2A52` | Write, Indicate |
| FORA custom `00001523-1212-efde-1523-785feabcd123` | `00001524-1212-efde-1523-785feabcd123` | Write, Notify |

This confirms the documentary custom service/characteristic and its properties on the physical meter. It does not establish proprietary commands, frames, records, or the behavior of the standard Glucose Service.

In the initial tested state, Home Assistant's Advertisement Monitor did not display FORA while the iPhone scanner saw the meter and Home Assistant displayed other BLE devices. See the controlled retest and later successful Home Assistant GATT result below.

## Home Assistant/ESPHome advertisement retest — user-supplied observation

Before the change, Lounge had an explicit `esp32_ble_tracker` scan interval of `320ms` and window of `30ms`; Home Assistant Advertisement Monitor did not detect FORA even when Lounge was temporarily set to Active. The explicit override was then removed, and Lounge was rebuilt and reflashed with ESPHome `2026.9.0`. Bedroom remained unchanged as a control.

After the change, with Lounge temporarily set to Active, Home Assistant Advertisement Monitor detected `FORA 6 CONNECT` through the Lounge ESPHome proxy. This confirms the ESPHome → Home Assistant advertisement path works in that tested state. Because the override removal and firmware reflash occurred together, the observation does not prove which change resolved the initial visibility gap.

Lounge was then returned to Auto. The prior FORA row remained visible, but its Updated age did not refresh during the test. A fresh Auto-mode advertisement was **not** confirmed. This does not establish that Auto cannot support FORA.

## Stage 1B discovery gate — user-supplied real probe observation

Multiple calls to the first development Home Assistant probe failed with `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` The next targeted-wait build was installed and returned `No known FORA 6 CONNECT candidate is available for targeted active scanning; first observe it in Home Assistant Bluetooth.` The device had previously appeared in Advertisement Monitor, but that does not establish that a current discovery cache still held it. The second build stopped before the targeted wait. Neither build attempted a Home Assistant GATT connection or transmitted a FORA operation. These results do not establish a meter or proxy GATT failure. EcoFlow activity and unrelated ESPHome API warnings are not FORA evidence.

The later general-discovery retest reported `general discoveries: 214; name matches: 0; connectable scanners: 2`. Home Assistant Bluetooth and two connectable scanners were operating, but the intermittently advertising meter was absent by name from the current cache. The action stopped before its targeted wait; no HA GATT connection or FORA operation occurred. [Home Assistant's Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/) states that `async_discovered_service_info` contains devices still present in the cache. These counts do not indicate a meter, proxy, or GATT failure.

The development-only probe accepts the private Bluetooth address copied from the previously identified `FORA 6 CONNECT` Advertisement Monitor row. It does not require a cached candidate. Any available advertised local name is normalized by removing trailing NUL padding, but a missing or different cached name does not gate this private-address, read-only GATT test and does not establish production identity. The current direct-connect Stage 1B probe attempts `async_ble_device_from_address(..., connectable=True)` immediately with the privately supplied address; advertisement freshness is diagnostic context, not a gate. The resulting service/characteristic inventory is compared with the iPhone evidence, especially the custom 1523/1524 pair. No characteristic I/O occurs. Production automatic discovery remains deferred to Stage 6.

## Sanitized Home Assistant advertisement-detail observation

**Source: user-supplied, manually viewed in Settings → Connectivity → Bluetooth → Advertisement Monitor.** The user opened the `FORA 6 CONNECT` device row and read its detail popup. This advertisement was **not returned by `fora6_connect.probe_gatt`**.

| Popup field | Observed sanitized finding |
| --- | --- |
| Connectable | Yes. |
| BLE flags | Present. |
| Complete Local Name | Canonical text `FORA 6 CONNECT` followed by **five trailing NUL characters** (`\x00` × 5). |
| Advertised 16-bit services | `0x1808` Glucose; `0x180A` Device Information. |
| Manufacturer-specific data | Present; payload withheld. |
| Custom `0x1523` service | **Absent from this observed advertisement.** |

**Advertised services are not the complete connected GATT inventory.** The earlier connected iPhone GATT observation independently confirmed FORA custom service `0x1523` and characteristic `0x1524` after connection. The popup proves the padded local-name format in Home Assistant's advertisement view. A raw exact-name comparison would reject that representation, so the development probe now removes trailing NUL padding before comparison. The latest development action still failed with `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait` and did not reach GATT. Padding may explain rejection **if** the probe received that representation, but the popup does not prove that its wait callback received it. A separate advertisement-wait/API-path issue remains possible. No private address, scanner identifier, raw packet, or manufacturer payload is recorded.

**Later real Stage 1B retest, user-supplied:** the installed trailing-NUL normalization build still returned `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not resolve a connectable FORA BLEDevice, attempt a FORA connection, enumerate GATT, or transmit any FORA operation. ESPHome status=133 log events around EcoFlow River 3 Plus reconnections are unrelated context, not evidence of a FORA connection failure. The prior Advertisement Monitor popup and the action's callback delivery must remain separate observations.

**Latest real Stage 1B retest, user-supplied:** the installed deduplication/timestamp revision still returned `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not resolve a FORA BLEDevice, attempt connection, enumerate GATT, or transmit a FORA operation. Home Assistant Advertisement Monitor separately showed FORA with Lounge manually Active. Callback delivery and UI visibility are distinct; the cause of the action timeout remains unknown. Duplicate suppression was a plausible hypothesis, not confirmed by this retest.

The development-only Stage 1B action now bypasses the callback-freshness gate to test the **Home Assistant → eligible Bluetooth adapter/proxy → GATT** path directly. Its controlled procedure asks the user to privately supply the address from a positively identified, visibly current/refreshing `FORA 6 CONNECT` Advertisement Monitor row and temporarily set Lounge to Active. The action first asks Home Assistant for a connectable BLEDevice at that runtime address. Optional `async_last_service_info(..., connectable=False)` supplies only a normalized local-name diagnostic and may be absent or stale; it does not establish live advertisement freshness. If no connectable device resolves, the action returns a sanitized Home Assistant outgoing-connection reachability explanation. If one resolves, it connects without pairing, inventories service/characteristic UUIDs and properties only, and disconnects. This tests GATT transport without proving Auto-mode or production discovery, which remain later work. The code does not choose or hard-code Lounge. The later real direct-connect result is recorded below.

## Home Assistant Stage 1B direct-connect GATT inventory — user-supplied real result

The development-only action ran against the real FORA 6 Connect through Home Assistant's Bluetooth stack. Its privacy-safe response reported `device_found=true`, normalized `local_name=FORA 6 CONNECT`, `advertised_name_confirmed=true`, `last_service_info_available=true`, `connectable_device_resolved=true`, `connectable_scanner_count=2`, `gatt_connection_attempted=true`, `connection_successful=true`, `connected_via_ha_bluetooth=true`, `gatt_service_count=5`, and `disconnected_cleanly=true`. The response did not identify which scanner/adapter made the connection. It confirms Home Assistant-side GATT transport and clean disconnect, without proving a particular ESPHome proxy path. No characteristic was read or written, no notification was started, and no FORA application operation was transmitted by this probe.

The probe returned these **actual service and characteristic UUIDs/properties**. Standard 16-bit UUIDs below are shown in their observed full Bluetooth SIG base-UUID form; `1523`/`1524` use the FORA custom base:

| Service UUID | Characteristic UUID | Properties returned |
| --- | --- | --- |
| `00001800-0000-1000-8000-00805f9b34fb` Generic Access | `00002a00-0000-1000-8000-00805f9b34fb` | Read |
| `00001800-0000-1000-8000-00805f9b34fb` | `00002a01-0000-1000-8000-00805f9b34fb` | Read |
| `00001800-0000-1000-8000-00805f9b34fb` | `00002a04-0000-1000-8000-00805f9b34fb` | Read |
| `00001801-0000-1000-8000-00805f9b34fb` Generic Attribute | — | No characteristics returned by the probe. |
| `0000180a-0000-1000-8000-00805f9b34fb` Device Information | `00002a23-0000-1000-8000-00805f9b34fb` | Read |
| `0000180a-0000-1000-8000-00805f9b34fb` | `00002a24-0000-1000-8000-00805f9b34fb` | Read |
| `0000180a-0000-1000-8000-00805f9b34fb` | `00002a25-0000-1000-8000-00805f9b34fb` | Read |
| `0000180a-0000-1000-8000-00805f9b34fb` | `00002a26-0000-1000-8000-00805f9b34fb` | Read |
| `0000180a-0000-1000-8000-00805f9b34fb` | `00002a27-0000-1000-8000-00805f9b34fb` | Read |
| `0000180a-0000-1000-8000-00805f9b34fb` | `00002a28-0000-1000-8000-00805f9b34fb` | Read |
| `0000180a-0000-1000-8000-00805f9b34fb` | `00002a29-0000-1000-8000-00805f9b34fb` | Read |
| `0000180a-0000-1000-8000-00805f9b34fb` | `00002a2a-0000-1000-8000-00805f9b34fb` | Read |
| `0000180a-0000-1000-8000-00805f9b34fb` | `00002a50-0000-1000-8000-00805f9b34fb` | Read |
| `00001808-0000-1000-8000-00805f9b34fb` Glucose | `00002a18-0000-1000-8000-00805f9b34fb` | Notify |
| `00001808-0000-1000-8000-00805f9b34fb` | `00002a34-0000-1000-8000-00805f9b34fb` | Notify |
| `00001808-0000-1000-8000-00805f9b34fb` | `00002a51-0000-1000-8000-00805f9b34fb` | Read |
| `00001808-0000-1000-8000-00805f9b34fb` | `00002a52-0000-1000-8000-00805f9b34fb` | Indicate, Write |
| `00001523-1212-efde-1523-785feabcd123` FORA custom | `00001524-1212-efde-1523-785feabcd123` | Notify, Write |

**Comparison with prior iPhone GATT observation:** Device Information `0x180A`, Glucose `0x1808`, custom `1523`, and all expected Glucose/custom characteristic properties were present. This independently confirms the earlier inventory. The read/write/notify/indicate labels are GATT properties; they do **not** establish command formats, record semantics, or which service carries non-glucose analytes. The complete standard Bluetooth Glucose Service and the custom FORA service coexist. Future, separately authorized protocol acquisition should examine two possible paths: Bluetooth SIG Glucose Service/RACP for standard glucose functionality and 1523/1524 for FORA-specific functionality. Whether non-glucose analytes use 1523/1524 remains a hypothesis. Earlier callback timeouts were discovery-layer results and did not demonstrate a meter or GATT failure. Auto-mode discovery and raw notification behavior remain unverified.

## Stage 1C passive notification observation — complete

The development-only `fora6_connect.observe_notifications` action is limited to the three **observed Notify characteristics**: Glucose Measurement `00002a18-0000-1000-8000-00805f9b34fb`, Glucose Measurement Context `00002a34-0000-1000-8000-00805f9b34fb`, and FORA custom `00001524-1212-efde-1523-785feabcd123`. It resolves a privately supplied known device through Home Assistant, connects without pairing, confirms the characteristics, attempts each subscription independently, observes for 30 seconds if any succeed, stops only successful subscriptions, and disconnects. It does **not** subscribe to RACP `0x2A52` or read/write an application characteristic. Notification subscription can cause Bleak/Home Assistant to configure CCCDs; only those stack-managed descriptor operations needed by `start_notify`/`stop_notify` are authorized for Stage 1C. They do not authorize a FORA application command.

The action returns only per-characteristic notification counts, observed payload lengths/length counts, and a distinct-payload count calculated from in-memory SHA-256 digests. It returns no digest or payload bytes, and neither bytes nor digests are persisted. A zero-notification result is valid. No raw notification has yet been observed on the real meter through this action; do not infer that any notification requires an application request merely from zero traffic. No packet layout, measurement, or proprietary meaning is decoded. Stage 2A authorizes documentary research only; it does not authorize new live BLE operations. [Home Assistant's Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/) supports retry-safe fresh clients; [Bleak's client API](https://bleak.readthedocs.io/en/latest/api/client.html) documents notification callback and stop-notify behavior.

### First real Stage 1C subscription result (user-supplied)

The installed observer reached notification subscription, but `start_notify` failed for Glucose Measurement `0x2A18`. The previous implementation aborted immediately. It therefore collected **no evidence** about subscription to `0x2A34` or custom `0x1524`, and no notification payload. This is a subscription/CCCD-layer result after connection and GATT discovery; its cause is unknown. The revised development action attempts all three independently and returns sanitized error class/structured code per failed target, with no upstream exception text that could expose private data. Zero successful subscriptions is a normal observation result.

The [Bluetooth SIG Glucose Profile 1.0.1, sections 6.1–6.2](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/GLP_v1.0.1/out/en/index-en.html) requires bonding between Glucose Sensor and Collector and LE Security Mode 1, Security Level 2 or 3 for supported Glucose Service characteristics. A previous iPhone connection was observed as bonded. Missing bonding/encryption is a **strong hypothesis** for this `2A18` subscription failure, not confirmed causation. A proxy or descriptor-notify failure remains an alternative. **Pairing is not authorized** for this gate; neither this result nor GATT properties establish FORA protocol behavior.

### Second real Stage 1C passive observation (user-supplied privacy-safe result)

The revised development observer resolved and connected to the real meter through Home Assistant. Over a 30-second observation, it attempted all three subscriptions. `0x2A18` Glucose Measurement and `0x2A34` Glucose Measurement Context each returned `subscription_successful: false` with sanitized `BleakError`. Custom `0x1524` returned `subscription_successful: true`; it delivered **zero notifications**. Overall: three subscriptions attempted, one successful, zero notifications. The successful subscription stopped cleanly and the BLE connection disconnected cleanly. The sanitized action fields were:

| Field | Observed value |
| --- | --- |
| `device_found` | `true` |
| `connectable_device_resolved` | `true` |
| `connection_successful` / `connected_via_ha_bluetooth` | `true` / `true` |
| `observation_duration_seconds` | `30` |
| `subscriptions_attempted` / `subscriptions_successful` | `3` / `1` |
| `notifications_observed` | `0` |
| `2A18`: subscription / error / count | `false` / `BleakError` / `0` |
| `2A34`: subscription / error / count | `false` / `BleakError` / `0` |
| `1524`: subscription / error / count | `true` / `null` / `0` |
| `subscriptions_stopped_cleanly` / `disconnected_cleanly` | `true` / `true` |

No notification payload was received or decoded.

The meter was new and had only one real measurement so far, for **uric acid**. Its memory appeared to contain only that result. While the custom subscription was already active, the user pressed the meter's arrow/navigation keys. The display remained on the existing uric-acid result, and no new measurement was performed. **Observed conclusion:** passive custom `1524` subscription plus navigation/display of that existing record produced no custom notification during this window. This does not establish that an application command is required, that other analytes behave alike, or that bonding caused the standard Glucose subscription failures. Glucose, ketone, cholesterol, haemoglobin, and haematocrit have not been tested on this physical meter. An explicit application-level request before `1524` emits stored data is only a hypothesis for future, separately authorized Stage 2 acquisition.

**Stage 1C passive observation and the full Stage 1 evidence review are complete.** The remaining discovery questions have explicit Stage 6/9 deferrals below. Stage 2A public research is authorized; pairing and live protocol operations are not. No private address, raw payload, measurement value, or personal timestamp is recorded here.

## Working hypotheses after Stage 1

- At the Stage 1 gate, it was only a hypothesis that historical measurements traveled over the custom Write/Notify characteristic. Stage 2C subsequently confirmed a successful uric-acid import over that path; see the later evidence section below.
- The previous Lounge scan timing may have contributed to missed advertisements, but the override removal and firmware reflash were combined, so causation remains unproven.

## Unknown at Stage 2B — historical snapshot

- The Bluetooth SIG Glucose Profile specifies bonding and LE Security Mode 1, Security Level 2 or 3 for its standard Glucose path. What remains unknown is whether missing bonding/encryption caused the observed GD82 `2A18`/`2A34` failures, whether the GD82 enforces that security in the tested Home Assistant/ESPHome path, whether later RACP operations require pairing, and whether FORA custom `1524` application operations require pairing. The bonded iPhone observation supports investigation but does not establish causation; pairing is not authorized.
- Fresh Auto-mode advertisement behavior and Bluetooth address stability/randomization/identity behavior: Stage 6 production discovery and duplicate-device handling.
- Exact Home Assistant scanner/ESPHome proxy selected for the successful GATT connection: Stage 9 end-to-end proxy validation.
- Manufacturer-data meaning: unknown; revisit in Stage 6 if useful for identification, or earlier only if later protocol evidence establishes relevance.
- Any additional advertised UUIDs and detailed Home Assistant scanner-source/RSSI relationship beyond the reported Lounge source remain unknown; no unsupported identity claim is made.
- Real GD82 commands and responses; Stage 2B has provisional app-derived candidates, not a captured physical response.
- Physical GD82 framing/checksum confirmation; the app uses an eight-byte summed frame on its reviewed path.
- Device identification response.
- Memory retrieval protocol.
- Measurement record format and analyte codes.
- Timestamp representation.
- Measurement status and control-solution flags.
- Units, scaling, and error responses.
- Which expected analytes are supported by the exact GD82 variant.

## Stage 2A evidence classes — reviewed 2026-09-26

### OBSERVED

The Stage 1 real-meter results above remain the only physical GD82 evidence: custom `1524` is Write/Notify and accepted subscription, but passive navigation of the only stored **uric-acid** result yielded zero notifications over 30 seconds; unpaired `2A18`/`2A34` subscriptions failed. No FORA application command has been transmitted. No other analyte has been measured on this physical meter.

### DOCUMENTED

The [ForaCare FAQ Rev 5.5, Q36–Q37](https://www.foracare.ch/wp-content/uploads/2023/03/3.1-BGM-FAQ_Rev5.5_230313.pdf) documents the BLE UUID base `1212-efde-1523-785feabcd123`, service `1523`, characteristic `1524` with Write/Notify, and identifies FORA 6 Connect GD82 with iFORA HM. The [GD82 manual](https://switzerland.foracare.ch/wp-content/uploads/2021/10/FORA-6-Connect-GD82-4183D_meter-manual_311-4183400-070.pdf) describes Bluetooth data transmission after meter shutoff and iFORA HM data download. These sources do not publish a request or frame format in the sections reviewed. The [Bluetooth SIG Glucose Profile](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/GLP_v1.0.1/out/en/index-en.html) specifies bonding/security for its standard Glucose path; that does not establish the GD82 custom `1524` protocol.

### INFERRED

The official iFORA HM client is the strongest identified target for a later, separately authorized static analysis because the manufacturer associates it with GD82 data transfer. This is a source-selection inference, **not** an inferred command. The public Nordic Blinky examples reuse the UUID base with unrelated application semantics; their bytes and operations cannot be imported into FORA.

### HYPOTHESES

An explicit request may precede stored-data notifications on `1524`; the zero-notification Stage 1C observation does not prove this. Missing bonding/encryption may explain standard Glucose subscription failures, with proxy/descriptor failure still possible. Neither hypothesis authorizes a write or pairing.

### UNKNOWN

The first GD82 application request bytes, opcode, framing, checksum, response, record layout, and analyte mapping remain unknown. The FAQ-linked Box share was inaccessible in the Stage 2A environment, so its contents are unknown. See [the source register](STAGE2_PROTOCOL_ACQUISITION.md) for access outcome and Stage 2B plan.

## Stage 2B static application evidence — reviewed 2026-09-26

### OBSERVED

No additional physical-device observation was made. The real meter still has only one known uric-acid measurement; Stage 1C's zero custom notifications and failed standard subscriptions remain as recorded. No application command was transmitted.

### DOCUMENTED

The manufacturer FAQ and GD82 manual still establish only product/app association and GATT/transfer metadata. They do not document the app-derived command bytes below.

### STATICALLY OBSERVED

Two mirror-distributed iFORA HM packages, versions 1.7.6 and 1.7.9, had matching published file hashes, valid APK signatures, the same signing certificate, and package `com.foracare.tdlink.hm`. The certificate has a ForaCare-labelled subject, but no independently trusted official Play signing fingerprint was available. [The static-analysis record](STAGE2_IFORA_HM_STATIC_ANALYSIS.md) contains exact hashes, split composition, tools, code locations, and provenance limits.

In both inspected versions, the app's BLE transport selects custom service `1523` / characteristic `1524`, enables its notifications, writes constructed command bytes there, and processes incoming notifications. Its project-code branch maps `TD4183` to a multifunction handler. The reviewed command builder creates eight-byte frames with a final byte equal to the preceding seven-byte sum modulo 256; the parser checks response command identifiers and the final sum. A provisional project-code query candidate is `51 24 00 00 00 00 A3 18` (hex). The ordinary app detection sequence has an earlier wake-up frame, so this query is **not** an established standalone first operation. No exact standard Glucose UUID strings appeared in either package's decompiled sources/resources; this does not rule out other constructed or unreviewed paths.

The TD4183-linked multifunction handler has a uric-acid record branch. In the 1.7.9 import path, the parsed uric-acid numeric value is divided by ten before storage. No real GD82 record was retrieved or decoded, and the physical unit/scaling remains unverified. Android bond-state changes are handled in the generic BLE path; no GD82-specific bonding requirement was established.

### INFERRED

`TD4183` likely represents the FORA 6 Connect GD82 because the official GD82 manual carries an `4183D` identifier, the app includes a FORA 6 Connect manual, and its import flow selects the TD4183 handler after project-code detection. The real meter's project-code response has **not** been observed. Mirror cross-version signatures support provisional app-code analysis but do not authenticate an official Play binary.

### HYPOTHESES

The app may retrieve GD82 uric-acid history through custom `1524`. This is not yet a physical-device observation or permission to send a command. The app-derived project-code query appears informational, but its standalone behavior and side effects are untested. Bonding causation remains unproven.

### UNKNOWN

Actual GD82 first command/response, write mode, security state, project code, physical frame validation, uric-acid units, and whether standard RACP is used in any GD82 state remain unknown. The preceding wake-up frame is not established as read/query-only. No independent first write meets the gate. A controlled official-app capture or independently authenticated official package is needed before considering a live request.

At the Stage 2B checkpoint, Stage 0 and Stage 1 were complete and Stage 2 remained in progress. The next gate then was a separately authorized controlled app capture. The later Stage 2C result below supersedes the Stage 2B unknowns where explicitly indicated; the earlier evidence classes are retained as historical provenance.

## Stage 2C live capture and Stage 2D offline implementation — reviewed 2026-09-27

### LIVE-CONFIRMED

The user supplied a sanitized summary of a private HCI capture from the physical FORA 6 Connect GD82. The runtime iFORA HM 1.7.6 app was a **patched, locally re-signed research copy**: its original minimum SDK 30 was changed to 27 to run on Android 8.1/API 27. The original APK hash is recorded in [the dedicated evidence record](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md). The runtime specimen was not the untouched officially signed APK. Its successful import used custom `1523/1524`, enabled the CCCD, transmitted requests, and received notifications. No bonding, SMP pairing, or encryption transition was observed in that successful proprietary import session; this does not generalize to standard Glucose/RACP security.

Observed request/response frames are eight bytes: byte 0 `0x51`, byte 1 command ID echoed in the response, bytes 2–5 command-specific, byte 6 request marker `0xA3` or response marker `0xA5`, and byte 7 `sum(bytes[0:7]) mod 256`. The observed `0x22` wake exchange was `51 22 00 00 00 00 A3 16` → `51 22 00 00 FF FF A5 16`; the observed `0x24` project exchange was `51 24 00 00 00 00 A3 18` → `51 24 83 41 04 00 A5 E2`. Little-endian response bytes 2–3 yield project ID `0x4183`, experimentally linking the physical GD82 to the Stage 2B `TD4183` branch. No other bytes in those responses are assigned field meanings here.

The successful uric-acid import used an indexed `0x25` plus `0x26` record retrieval sequence. `0x25` carried packed time-related fields; `0x26` carried the measurement/analyte payload. The displayed uric-acid result equaled the parsed raw numeric value divided by ten, confirming that scaling **only for uric acid on this GD82/TD4183 path**. The private numeric value and timestamp are not recorded. Only uric acid has been physically tested on this meter.

### STATIC-ANALYSIS-SUPPORTED

The Stage 2B iFORA HM code path constructed the same wake/project queries and eight-byte sum, mapped `TD4183` to a multifunction handler, and included uric-acid processing. Stage 2C's physical project response and import sequence now corroborate that path. The original mirror-distributed APK signature still lacks an independent official Play/ForaCare trust anchor; the live runtime was explicitly patched and re-signed.

### INFERRED

The `0x25` and `0x26` responses likely comprise two parts of an indexed record in this workflow. Their detailed field positions, cross-analyte dispatch, and timestamp semantics are not established by the sanitized summary. The presence of custom uric-acid traffic does not establish which path a glucose result uses.

### UNRESOLVED

The exact response fields of `0x27` and `0x28`, category-parameter semantics of `0x2F`, and state effects of `0x50`; `0x25` date/time bit layout and timezone; `0x26` analyte/raw-value byte positions; all other analyte scaling, error/status/control-solution flags, retries, write type, and meter-state variation. Stage 2F's later static review establishes a raw-slot role for `0x2B`, but not a logical analyte count. Fresh Auto-mode discovery and address identity remain Stage 6 work, and the exact Home Assistant scanner/proxy remains Stage 9 work. Standard Glucose/RACP security and the cause of prior unpaired standard subscription failures remain unresolved.

Stage 2D implements an immutable frame, validation/checksum helpers, fixed wake and project-query constructors, `0x4183` project-ID parsing, and a contextual uric-acid scaling helper. It does not parse `0x25`/`0x26` record fields. Stage 2E added a separate development-only Home Assistant action that subscribes to custom `1524`, sends only the two captured requests with explicit write-with-response, validates notifications through `protocol.py`, requires project `0x4183`, and cleans up.

### OBSERVED — real Stage 2E Home Assistant identity result

The user supplied a privacy-safe success result from the physical GD82 **while the meter was ON**. Home Assistant resolved the connectable device, connected, found custom `1524`, subscribed, wrote `0x22` and received a valid matching response, wrote `0x24` and received a valid matching response, parsed project `16771` (`0x4183`), then stopped notifications and disconnected cleanly. All identity and cleanup flags were true; there was no reported error. This independently validates the bounded Home Assistant custom identity path. It does not establish record retrieval or the scanner/proxy used. An earlier Stage 1C connection while the display appeared off is separate evidence, not proof of an off-state Stage 2E exchange. No private address, health value, timestamp, or raw response is recorded.

### STATIC-ANALYSIS-SUPPORTED — Stage 2F record path

The [Stage 2F evidence review](STAGE2F_TD4183_RECORD_PROBE.md) traces the TD4183 handler to a read-oriented `0x2B` raw-slot query, followed by indexed `0x25` and `0x26` record parts. A pre-physical-test reinspection of the successful Stage 2C wire traffic found that the first committed Stage 2F constructors selected `CurrentUser = 0`, whereas the app import selected `User1 = 1`. The static builders encode that enum value directly: at byte 2 for `0x2B` and byte 5 for `0x25`/`0x26`; the raw index occupies bytes 2–3 in the latter pair. The corrected User1/index-zero requests and provenance are documented in the Stage 2F review. No Home Assistant Stage 2F record request was sent before this correction. The development-only action still requires valid `0x22`/`0x24` identity and project `0x4183`, then requests at most one raw slot and validates only frame envelopes/command IDs. **Physical testing is paused pending review of the correction.**

### UNKNOWN — Stage 2F physical result and payloads

The app's `0x33` operation sets clock/date in the static path; whether the meter requires it before record reads is unknown. It is prohibited from Stage 2F transport, which must fail closed rather than add it. `0x27`/`0x28`, `0x2F`, and `0x50` are omitted. The final index-one access in the live `1 → 0 → 1` sequence could be a multi-parameter companion or a later logical slot; its exact branch is not established by the sanitized record responses. No general record schema, analyte identifier, numeric field, timestamp, timezone, or control-solution flag is established. The existing uric-acid scaling fact cannot identify an opaque response. **Next gate: review corrected evidence/code before deciding whether physical Stage 2F validation may resume.**
