# Stage 1 capture guide

Stage 1 is in progress. **Stage 1A preparation is complete.** A user-supplied, externally screenshot-reviewed iPhone scanner observation confirmed the real meter's name, connectability, and GATT inventory. Home Assistant's Advertisement Monitor did not show FORA in the tested ESPHome proxy state. This guide now supports a controlled repeat through Home Assistant. It does not authorize Home Assistant-side GATT work, application writes, or protocol implementation.

## Current user-supplied observation (screenshots reviewed externally)

- While the real meter's blue Bluetooth indicator flashed, a generic iPhone BLE scanner saw `FORA 6 CONNECT`, reported connectable at approximately −50 dBm close range, and connected successfully. It marked the connection `BONDED`; whether bonding is required remains unknown. Do not treat an iPhone CoreBluetooth UUID as a physical MAC address.
- The iPhone scanner displayed Device Information `0x180A`, Glucose `0x1808` (`0x2A18` Notify, `0x2A34` Notify, `0x2A51` Read, `0x2A52` Write/Indicate), and FORA custom service `00001523-1212-efde-1523-785feabcd123` with characteristic `00001524-1212-efde-1523-785feabcd123` Write/Notify. See `PROTOCOL.md` for the evidence register.
- Home Assistant's Bluetooth Adapter view showed Bedroom in `Auto (passive)` with 0/3 slots in use and Lounge in `Auto (passive)` with 1/3 slots in use. Lounge was temporarily changed to Active scanning. While iPhone discovery succeeded, Advertisement Monitor did not show FORA, although it continued to show other BLE devices such as the user's EcoFlow. This does not establish a meter radio failure.
- The Lounge M5Stack Atom Lite configuration uses the official `esphome.bluetooth-proxy` package at `github://esphome/bluetooth-proxies/m5stack/m5stack-atom-lite.yaml@main` and this explicit scan timing override:

  ```yaml
  esp32_ble_tracker:
    scan_parameters:
      interval: 320ms
      window: 30ms
  ```

  The scan window is about 9.4% of the interval. Missed advertisements from this timing are a hypothesis, not an established cause. The actual Home Assistant/ESPHome GATT path remains untested.

## Next controlled gate

1. Record the Lounge proxy's current scan settings and baseline Home Assistant Advertisement Monitor outcome while the meter indicator flashes.
2. Correct/test the Lounge BLE scan timing as one controlled change; record the exact setting, scanner mode, proxy state, observation window, and meter state. Repeat Advertisement Monitor observation under comparable conditions.
3. Determine whether Home Assistant sees `FORA 6 CONNECT` through the proxy. Record negative results as well as positive results; do not infer causation from one missed observation.
4. Only after Home Assistant discovery and separate authorization, validate Home Assistant-side connectability and GATT. Do not perform FORA application writes.

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

## Stage 1B — planned Home Assistant-side observational GATT method, not yet implemented

**Entry gate:** Home Assistant discovers the real candidate through an eligible scanner, the candidate is sufficiently distinguished from unrelated BLE devices, a connectable path is shown, and Home Assistant-side GATT inspection is explicitly authorized. The iPhone GATT inventory does not itself validate that path. This section is a design for a future probe, not code or permission to run it now.

1. Use Home Assistant's Bluetooth stack to inspect recent candidate observations with `bluetooth.async_discovered_service_info(hass, connectable=False)` and `bluetooth.async_last_service_info(hass, address, connectable=True)` as appropriate. These are observations, not identity proof. If needed, inspect per-scanner observations through `bluetooth.async_scanner_devices_by_address` to understand which scanner heard the candidate.
2. Resolve the current connectable `BLEDevice` through `bluetooth.async_ble_device_from_address(hass, address, connectable=True)`. If unavailable, use `bluetooth.async_address_reachability_diagnostics` with connection intent for a **private** reachability report; do not parse its human-readable text or publish an unredacted report. Do not hard-code the Atom Lite, another proxy, or a local BlueZ interface.
3. For an authorized read-only GATT inspection, follow then-current Home Assistant/Bleak retry-safe connection guidance (including fresh client instances and suitable timeouts). Let Home Assistant choose an eligible scanner path, which may be the ESPHome proxy. Avoid creating a separate local scanner.
4. Enumerate every service and characteristic and record UUIDs/properties with provenance. Verify whether `00001523-1212-efde-1523-785feabcd123` and `00001524-1212-efde-1523-785feabcd123` actually exist on this device and whether write/notify properties are present.
5. Subscribe to notifications **only under separate explicit authorization**; record whether any arrive without FORA application writes. Do not send any FORA application write during Stage 1. Disconnect cleanly. Keep raw notifications private pending sanitization review.

Home Assistant-side Stage 1B must not be implemented or run before its entry gate. Stage 2 protocol acquisition is not authorized. No command bytes, packet layouts, or response meanings are inferred from the observed UUIDs or properties.

## Evidence and public reporting

Keep the original private capture with its source, date/time, Home Assistant and ESPHome versions, scanner configuration, meter state, and collection method. In public project documents, report only sanitized findings and distinguish **observed facts**, **interpretations**, and **unknowns**. Before adding any future fixture, remove identifying health values and addresses, document transformations, and verify the fixture still tests the intended behavior. If useful evidence cannot be safely sanitized, keep it private and publish only a non-sensitive conclusion.

The next action is the controlled Lounge scan-timing test and repeat Home Assistant Advertisement Monitor observation. Stage 1 is not complete: iPhone GATT inventory exists, but Home Assistant-side GATT and notification behavior remain uncollected.
