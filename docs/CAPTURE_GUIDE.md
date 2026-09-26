# Stage 1 capture guide

Stage 1 is in progress. **Stage 1A preparation is complete.** User-supplied iPhone observations confirmed the real meter's name, connectability, and GATT inventory. A controlled Lounge proxy retest confirmed Home Assistant Advertisement Monitor visibility in Active mode. A later manually opened Advertisement Monitor popup supplied sanitized advertisement details, including five trailing NULs in the Complete Local Name; the development action did not return that packet. The installed name-normalization and deduplication/timestamp builds both timed out at their targeted wait, without FORA BLEDevice resolution or GATT inventory. The cause is unresolved; callback delivery is not assumed from Advertisement Monitor visibility. The immediate Stage 1B validation will use Lounge temporarily Active; fresh Auto-mode discovery remains a separate unknown. No application-level writes or protocol implementation are authorized.

## User-supplied Stage 1 observations

- In screenshots reviewed externally, while the real meter's blue Bluetooth indicator flashed, a generic iPhone BLE scanner saw `FORA 6 CONNECT`, reported connectable at approximately −50 dBm close range, and connected successfully. It marked the connection `BONDED`; whether bonding is required remains unknown. Do not treat an iPhone CoreBluetooth UUID as a physical MAC address.
- The iPhone scanner displayed Device Information `0x180A`, Glucose `0x1808` (`0x2A18` Notify, `0x2A34` Notify, `0x2A51` Read, `0x2A52` Write/Indicate), and FORA custom service `00001523-1212-efde-1523-785feabcd123` with characteristic `00001524-1212-efde-1523-785feabcd123` Write/Notify. See `PROTOCOL.md` for the evidence register.
- Home Assistant's initial Bluetooth Adapter view showed Bedroom in `Auto (passive)` with 0/3 slots in use and Lounge in `Auto (passive)` with 1/3 slots in use. Lounge was temporarily changed to Active scanning. While iPhone discovery succeeded, Advertisement Monitor did not show FORA, although it continued to show other BLE devices such as the user's EcoFlow. This did not establish a meter radio failure.
- Before the controlled retest, the Lounge M5Stack Atom Lite used the official `esphome.bluetooth-proxy` package at `github://esphome/bluetooth-proxies/m5stack/m5stack-atom-lite.yaml@main` and this explicit scan timing override:

  ```yaml
  esp32_ble_tracker:
    scan_parameters:
      interval: 320ms
      window: 30ms
  ```

  The scan window was about 9.4% of the interval. The override was subsequently removed; it is not the current Lounge configuration.
- **Controlled retest:** Lounge was rebuilt and reflashed with ESPHome `2026.9.0` after removing the override; Bedroom remained unchanged as a control. With Lounge temporarily set to Active, Advertisement Monitor detected `FORA 6 CONNECT` through Lounge. This confirms advertisement forwarding in the tested Active state. The override removal and reflash occurred together, so the cause of the prior missed detections is not isolated.
- **Auto retest:** Lounge was returned to Auto. The previous FORA row remained, but its Updated age did not refresh during the test. A fresh Auto-mode advertisement was not confirmed; the result does not prove Auto cannot support FORA.
- **First real Stage 1B probe attempts, user-supplied:** repeated calls returned `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` No Home Assistant GATT connection was attempted, and no FORA operation was transmitted. This is a discovery-gate result, not evidence of a meter or proxy GATT failure. EcoFlow activity and unrelated ESPHome API warnings do not establish a FORA failure.
- **Second real Stage 1B probe, user-supplied:** after the targeted-wait build was installed, the action returned `No known FORA 6 CONNECT candidate is available for targeted active scanning; first observe it in Home Assistant Bluetooth.` This occurred despite an earlier Advertisement Monitor observation. The code stopped before the targeted wait, GATT connection, or any FORA operation. A previously observed UI row does not prove current presence in either HA cache; the restrictive connectable-only lookup is being removed as the first gate.
- **General-discovery real retest, user-supplied:** the development action again returned no known FORA candidate, with `general discoveries: 214; name matches: 0; connectable scanners: 2`. Home Assistant Bluetooth and two connectable scanners were operational, but the intermittently advertising meter was absent by name from the current cache during this run. Home Assistant documents that discovery results contain devices still present in the cache. No targeted wait, HA GATT connection, or FORA operation occurred. This is not a meter, proxy, or GATT failure finding.
- **Advertisement-detail popup, user-supplied:** the user manually opened the `FORA 6 CONNECT` row in Home Assistant's Advertisement Monitor. Its Complete Local Name was canonical `FORA 6 CONNECT` with **five trailing NULs**; the popup marked the meter connectable, showed BLE flags, advertised `0x1808` Glucose and `0x180A` Device Information, and showed manufacturer-specific data present. Custom `0x1523` was absent from this advertisement, although connected iPhone GATT had previously shown `0x1523`/`0x1524`. Advertised services are a subset observation, not the complete GATT inventory. The development action did **not** return this packet and still failed with `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` Padding may explain a name-comparison rejection if the probe received such a packet, but the UI observation cannot establish that it did. A separate targeted-wait/API-path issue remains possible. No private address, raw packet, or manufacturer payload is recorded.
- **Normalization-build real retest, user-supplied:** after installing the trailing-NUL correction, the action still returned `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not resolve a connectable FORA BLEDevice, connect, enumerate GATT, or transmit a FORA operation. ESPHome status=133 events around EcoFlow River 3 Plus reconnections do not describe a FORA connection failure because the action never reached that stage. The later deduplication/timestamp build also timed out at the targeted wait. Duplicate suppression has not been established as the cause; neither build reached GATT.

## Next Stage 1B gate — run the direct-connect development probe

1. Replace the installed development integration and restart Home Assistant Core as described in [the development guide](DEVELOPMENT.md). Temporarily set Lounge to **Active**. Make the meter advertise and confirm the `FORA 6 CONNECT` Advertisement Monitor row is visibly current/refreshing. Privately copy that identified row's address; do not add it to this repository or share it publicly.
2. Invoke `fora6_connect.probe_gatt` with its required private address field during the transfer window. The action immediately asks Home Assistant for a connectable BLEDevice. It does **not** wait for an advertisement callback, newer timestamp, or history-clearing result. Optional last service info and its NUL-normalized name are diagnostic only; an absent or stale row does not block resolution. If resolution fails, record only the sanitized outgoing-connection reachability explanation. If it succeeds, report the privacy-safe connection outcome, actual GATT inventory/comparison, and disconnect outcome.
3. Privately confirm the selected connection path in Home Assistant's Connection Monitor if necessary. Record actual Home Assistant and ESPHome versions, meter state, scan/source observations, connection outcome, GATT inventory, and disconnect outcome with provenance. Keep addresses and raw logs private. Return Lounge to its usual mode after the controlled test.
4. Perform no characteristic I/O or FORA application operation. Stage 2 remains unauthorized. Auto-mode and production discovery remain later work.

## Source provenance (checked 2026-09-26)

- [Home Assistant Bluetooth integration](https://www.home-assistant.io/integrations/bluetooth): `Settings > Connectivity > Bluetooth`, Adapters, Advertisement Monitor, Connection Monitor, scanner modes, and proxy support.
- [Home Assistant Bluetooth APIs](https://developers.home-assistant.io/docs/core/bluetooth/api/): discovered/last service info, connectable device resolution, per-scanner observations, and reachability diagnostics.
- [Home Assistant Bluetooth developer guidance](https://developers.home-assistant.io/docs/bluetooth/): remote-controller capability and retry-safe Bleak connection guidance.
- [ESPHome Bluetooth Proxy](https://esphome.io/components/bluetooth_proxy/): advertisement forwarding, active GATT connections, connection slots, and the distinction between scanning mode and active connection support.

These sources describe platform capabilities, **not** this meter or the user's actual proxy configuration. Record the versions and capabilities shown by the user's system. Home Assistant UI labels can change; preserve the displayed wording if it differs.

## Privacy before observing

1. Use a meter and Home Assistant environment the user controls. Keep the completed [private observation template](STAGE1_OBSERVATION_TEMPLATE.md) and any logs **outside this Git repository**.
2. Do not publish full unredacted Home Assistant logs, screenshots, raw Bluetooth addresses, personal measurements, tokens, credentials, or raw BLE captures. A short redacted summary is enough for review; mark omitted fields as private.
3. Record precise local observation times privately, with time zone. If redacting an address, use a consistent local label such as `candidate A` across observations; keep the mapping private. Do not alter protocol-relevant values in a future public fixture without documenting the transformation.
4. Do not send guessed FORA commands or make a personal health measurement solely to generate test data. Observe the meter in an ordinary, controlled state.

## Stage 1A — Home Assistant environment and passive discovery

“Passive discovery” here means observing existing Home Assistant Bluetooth data without making a FORA application connection or write. Record the scanner's actual **Auto/Active/Passive scanning mode**; the observation workflow does not imply that the radio is in Passive mode. Active scanning requests scan-response data, while active GATT connection support is a separate capability.

1. In Home Assistant, open **Settings → Connectivity → Bluetooth**. Record the Home Assistant version and observation date/time. Use **Adapters** to locate the M5Stack Atom Lite ESPHome proxy. Record its displayed scanner/proxy name, availability/state, area if useful, capabilities, current scanning mode, whether active/GATT connection capability is shown, and available connection slots if exposed. Record the ESPHome firmware version if visible in its device page. Do not infer a capability from the hardware model or ESPHome defaults.
2. Open **Advertisement Monitor**. Observe a candidate while the meter is available through its normal behavior. Record privately the fields below for **observation #1** and a later **observation #2**. If nothing appears, record that negative result with time, proxy state, and scanner mode; absence in one window does not prove the meter never advertises.
3. Record whether the Atom Lite appears as the source that received the candidate advertisement, if Home Assistant exposes the source. If several scanners see the candidate, record each visible source/RSSI relationship separately. Do not assume the strongest source was the only scanner that heard it.
4. Open **Connection Monitor** and note whether the candidate already has a connection and which scanner is shown, if any. Do not initiate or interrupt a connection for Stage 1A.
5. Compare both observations. Treat local name, advertised service UUIDs, and the documented 1523/1524 UUID pair as clues, not proof of identity. Record why the candidate is plausible, what competing devices could fit, and what remains unverified. Do not add a manifest Bluetooth matcher yet.

### Private advertisement fields to record for each observation

| Field | What to record |
| --- | --- |
| Observation time | Local time and time zone; capture window/duration if known. |
| Local name | Exact displayed name, or “not shown”. Do not assume it contains FORA. |
| Address/identifier | Exact value **privately**; compare stability across observations. Do not commit it. |
| RSSI | Displayed value and units, paired with scanner/source where possible. |
| Connectable | Displayed yes/no/unknown; distinguish this from scanner GATT capability. |
| Scanner/proxy source | Name/source for each visible scanner; specifically whether Atom Lite received it. |
| Advertised service UUIDs | Exact displayed list, or “not shown”. The documented 1523 UUID may not be advertised. |
| Service data | UUIDs and data privately if shown; otherwise “not shown”. |
| Manufacturer data | Manufacturer ID and data privately if shown; otherwise “not shown”. |
| TX power | Value if present; otherwise “not shown”. |
| Other fields | Any additional advertisement fields Home Assistant actually exposes. |

“Not shown” means the UI did not display a field; it does **not** mean the device omitted it. Do not copy a full raw log into this repository. The blank [Stage 1 observation template](STAGE1_OBSERVATION_TEMPLATE.md) is safe to keep in Git; completed copies are private.

## Stage 1B — Home Assistant-side observational GATT method, direct-connect probe pending real test

**Entry gate:** Home Assistant has shown the real candidate through Lounge in Active mode. The immediate controlled test requires Lounge temporarily Active and the FORA Advertisement Monitor row visibly current/refreshing. The iPhone GATT inventory does not itself validate Home Assistant's connection path. Mock tests do not constitute a real-device result. Auto-mode discovery remains a separate later question.

1. Privately supply the Bluetooth address from the positively identified Advertisement Monitor row to the development action. This address stays in memory. The action uses `bluetooth.async_ble_device_from_address(hass, address, connectable=True)` immediately; Home Assistant chooses the eligible path. Do not hard-code Atom Lite, another proxy, or a local BlueZ interface.
2. If no connectable BLEDevice resolves, inspect only the action's sanitized Home Assistant outgoing-connection reachability explanation. Do not infer a GATT failure from a resolution failure. Optional last service info is a name diagnostic only and does not gate connection.
3. If resolved, use a fresh retry-safe, no-pair Bleak client and a suitable timeout for read-only GATT inventory. Do not create a separate scanner.
4. Enumerate service and characteristic UUIDs/properties. Compare whether `00001523-1212-efde-1523-785feabcd123` and `00001524-1212-efde-1523-785feabcd123` actually appear. Report the actual inventory, including absent expected items.
5. Disconnect cleanly. Do not read characteristics, subscribe, pair, enable CCCDs, or send an application command. Keep the runtime address and raw platform logs private.

All real Stage 1B builds so far stopped at discovery, including the installed deduplication/timestamp revision. None tested Home Assistant GATT. The direct-connect revision is awaiting its first real run. Production automatic discovery belongs to Stage 6. Stage 2 is not authorized. No command bytes, packet layouts, or response meanings are inferred from UUIDs or properties.

## Evidence and public reporting

Keep the original private capture with its source, date/time, Home Assistant and ESPHome versions, scanner configuration, meter state, and collection method. In public project documents, report only sanitized findings and distinguish **observed facts**, **interpretations**, and **unknowns**. Before adding any future fixture, remove identifying health values and addresses, document transformations, and verify the fixture still tests the intended behavior. If useful evidence cannot be safely sanitized, keep it private and publish only a non-sensitive conclusion.

The next gate is running the direct-connect Stage 1B Home Assistant probe above with Lounge temporarily Active and a visibly current FORA row. Stage 1 is not complete: Active-mode Lounge advertisement forwarding is established, while Home Assistant-side GATT inventory and Auto-mode discovery remain unconfirmed.
