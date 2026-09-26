# Protocol evidence register

This page records evidence before any FORA application protocol implementation. Documentary claims come from the FORA 6 Connect GD82 documentation described in the Stage 0 project brief; the underlying document has not been independently inspected in this repository. The iPhone findings below are a sanitized user-supplied summary of screenshots reviewed externally. The later Home Assistant/ESPHome observations are user-supplied and were not independently reproduced by this repository task. No private identifiers, health data, or raw captures are stored here.

## Confirmed for this project brief

- Product: FORA 6 Connect; model/variant: GD82.
- Documented BLE service UUID: `00001523-1212-efde-1523-785feabcd123`.
- Documented BLE characteristic UUID: `00001524-1212-efde-1523-785feabcd123`.
- The documentation describes the characteristic as supporting write and notify.

The UUID pair alone cannot establish that an observed BLE device is a FORA 6 Connect.

## Observed on the real meter — user-supplied, screenshots reviewed externally

The real meter's blue Bluetooth indicator was flashing when a generic iPhone BLE scanner displayed local name `FORA 6 CONNECT`. The scanner showed it as connectable, with close-range RSSI approximately −50 dBm. The iPhone connected successfully and marked the connection `BONDED`. This shows bonding occurred in that session; it does **not** establish that the meter requires bonding. The scanner may have initiated bonding automatically. An iPhone CoreBluetooth identifier is not a physical MAC address and is not recorded here.

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

The action returns only per-characteristic notification counts, observed payload lengths/length counts, and a distinct-payload count calculated from in-memory SHA-256 digests. It returns no digest or payload bytes, and neither bytes nor digests are persisted. A zero-notification result is valid. No raw notification has yet been observed on the real meter through this action; do not infer that any notification requires an application request merely from zero traffic. No packet layout, measurement, or proprietary meaning is decoded. Stage 2 is not authorized. [Home Assistant's Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/) supports retry-safe fresh clients; [Bleak's client API](https://bleak.readthedocs.io/en/latest/api/client.html) documents notification callback and stop-notify behavior.

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

**Stage 1C passive observation is complete.** Stage 1 remains in progress pending review of unresolved discovery questions, including Auto-mode and address behavior. Pairing and Stage 2 are not authorized. No private address, raw payload, measurement value, or personal timestamp is recorded here.

## Working hypotheses

- The meter may expose historical measurements over the documented write/notify characteristic. This is a product goal, not a verified protocol fact.
- The previous Lounge scan timing may have contributed to missed advertisements, but the override removal and firmware reflash were combined, so causation remains unproven.

## Unknown

- Whether bonding is required, address behavior, manufacturer payload meaning, any additional advertised UUIDs, fresh Auto-mode advertisement behavior, detailed Home Assistant scanner-source/RSSI relationship beyond the reported Lounge source, and the exact selected Home Assistant GATT scanner/adapter.
- Commands and responses.
- Framing and checksums.
- Device identification response.
- Memory retrieval protocol.
- Measurement record format and analyte codes.
- Timestamp representation.
- Measurement status and control-solution flags.
- Units, scaling, and error responses.
- Which expected analytes are supported by the exact GD82 variant.

Do not add protocol behavior until evidence, provenance, sanitized frames, and regression tests are available. See `CAPTURE_GUIDE.md`.
