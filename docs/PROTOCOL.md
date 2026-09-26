# Protocol evidence register

This page records evidence before any FORA application protocol implementation. Documentary claims come from the FORA 6 Connect GD82 documentation described in the Stage 0 project brief; the underlying document has not been independently inspected in this repository. The iPhone findings below are a sanitized user-supplied summary of screenshots reviewed externally. The later Home Assistant/ESPHome retest is user-supplied. Neither was independently reproduced by this repository task. No private identifiers, health data, or raw captures are stored here.

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

Lounge was then returned to Auto. The prior FORA row remained visible, but its Updated age did not refresh during the test. A fresh Auto-mode advertisement was **not** confirmed. This does not establish that Auto cannot support FORA. Home Assistant's [Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/) describes `bluetooth.async_request_active_scan(hass)` as an on-demand active sweep of Auto-mode scanners; the Stage 1B probe should use that supported API while Lounge stays in Auto.

## Working hypotheses

- The meter may expose historical measurements over the documented write/notify characteristic. This is a product goal, not a verified protocol fact.
- The meter may be reachable for GATT through an eligible ESPHome Bluetooth proxy via Home Assistant's stack. Advertisement forwarding has been observed; GATT operation remains untested.
- The previous Lounge scan timing may have contributed to missed advertisements, but the override removal and firmware reflash were combined, so causation remains unproven.

## Unknown

- Whether bonding is required, address behavior, manufacturer/service advertisement data, advertised UUIDs, fresh Auto-mode advertisement behavior, detailed Home Assistant scanner-source/RSSI relationship beyond the reported Lounge source, and Home Assistant-side connectability/GATT.
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
