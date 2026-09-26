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

In the initial tested state, Home Assistant's Advertisement Monitor did not display FORA while the iPhone scanner saw the meter and Home Assistant displayed other BLE devices. See the controlled retest below. Home Assistant-side connection and GATT have not been validated.

## Home Assistant/ESPHome advertisement retest — user-supplied observation

Before the change, Lounge had an explicit `esp32_ble_tracker` scan interval of `320ms` and window of `30ms`; Home Assistant Advertisement Monitor did not detect FORA even when Lounge was temporarily set to Active. The explicit override was then removed, and Lounge was rebuilt and reflashed with ESPHome `2026.9.0`. Bedroom remained unchanged as a control.

After the change, with Lounge temporarily set to Active, Home Assistant Advertisement Monitor detected `FORA 6 CONNECT` through the Lounge ESPHome proxy. This confirms the ESPHome → Home Assistant advertisement path works in that tested state. Because the override removal and firmware reflash occurred together, the observation does not prove which change resolved the initial visibility gap.

Lounge was then returned to Auto. The prior FORA row remained visible, but its Updated age did not refresh during the test. A fresh Auto-mode advertisement was **not** confirmed. This does not establish that Auto cannot support FORA.

## Stage 1B discovery gate — user-supplied real probe observation

Multiple calls to the first development Home Assistant probe failed with `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` The next targeted-wait build was installed and returned `No known FORA 6 CONNECT candidate is available for targeted active scanning; first observe it in Home Assistant Bluetooth.` The device had previously appeared in Advertisement Monitor, but that does not establish that a current discovery cache still held it. The second build stopped before the targeted wait. Neither build attempted a Home Assistant GATT connection or transmitted a FORA operation. These results do not establish a meter or proxy GATT failure. EcoFlow activity and unrelated ESPHome API warnings are not FORA evidence.

The later general-discovery retest reported `general discoveries: 214; name matches: 0; connectable scanners: 2`. Home Assistant Bluetooth and two connectable scanners were operating, but the intermittently advertising meter was absent by name from the current cache. The action stopped before its targeted wait; no HA GATT connection or FORA operation occurred. [Home Assistant's Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/) states that `async_discovered_service_info` contains devices still present in the cache. These counts do not indicate a meter, proxy, or GATT failure.

The development-only probe accepts the private Bluetooth address copied from the previously identified `FORA 6 CONNECT` Advertisement Monitor row. It does not require a cached candidate. A live local name must match after removing trailing NUL padding if present; when absent, read-only GATT inventory may proceed because the user selected the address privately. This allowance does not establish production identity. Only after a fresh Home Assistant observation does the probe attempt `async_ble_device_from_address(..., connectable=True)`. The resulting service/characteristic inventory is compared with the iPhone evidence, especially the custom 1523/1524 pair. No characteristic I/O occurs. Production automatic discovery remains deferred to Stage 6.

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

[Home Assistant's Bluetooth API](https://developers.home-assistant.io/docs/core/bluetooth/api/) documents deduplication of identical advertisements and a per-address `async_clear_advertisement_history` operation that does not clear integration matcher history. [Home Assistant's iBeacon implementation](https://github.com/home-assistant/core/blob/dev/homeassistant/components/ibeacon/coordinator.py) uses `async_last_service_info` timestamps because unchanged advertisements may not produce regular callbacks. The Stage 1B development probe now captures a baseline, records a monotonic wait start, clears only the runtime address's advertisement history, and runs its targeted active wait while checking whether latest service-info time advances. A callback or fallback observation must postdate the invocation, and any present local name must match after NUL normalization. Duplicate suppression is an **evidence-backed hypothesis under test**, not an established explanation for the timeout. The next controlled GATT test will temporarily set Lounge to **Active** because that mode has exposed FORA in Advertisement Monitor; fresh Auto-mode discovery remains unresolved separately. The code does not select or hard-code Lounge.

## Working hypotheses

- The meter may expose historical measurements over the documented write/notify characteristic. This is a product goal, not a verified protocol fact.
- The meter may be reachable for GATT through an eligible ESPHome Bluetooth proxy via Home Assistant's stack. Advertisement forwarding has been observed; GATT operation remains untested.
- The previous Lounge scan timing may have contributed to missed advertisements, but the override removal and firmware reflash were combined, so causation remains unproven.

## Unknown

- Whether bonding is required, address behavior, manufacturer payload meaning, any additional advertised UUIDs, fresh Auto-mode advertisement behavior, detailed Home Assistant scanner-source/RSSI relationship beyond the reported Lounge source, and Home Assistant-side GATT connectability.
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
