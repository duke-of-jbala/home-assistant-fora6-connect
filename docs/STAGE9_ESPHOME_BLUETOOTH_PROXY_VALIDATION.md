# Stage 9 — ESPHome Bluetooth Proxy path validation

**Status: complete for the tested M5Stack Atom Lite proxy path.** The user-run real Home Assistant validation below directly identified the Atom Lite as the active connection source during the existing manual refresh. This closes the route-evidence gate for that run; it does not generalize to other proxies, adapters, meter states, or hardware.

## Physical validation result — user supplied

In Home Assistant Bluetooth → Connections, an active row named `FORA 6 CONNECT` appeared during `fora6_connect.refresh_current_uric_acid`. Its **Source** explicitly named the **(Lounge) M5Stack Atom Lite ESPHome Bluetooth Proxy**. The row disappeared shortly after the action completed. This is direct, connection-specific evidence that the tested BLE/GATT session traversed the Lounge Atom Lite proxy rather than merely succeeding while a proxy was online.

The sanitized action result reported `refresh_performed`, `refresh_successful`, `supported_raw_slot_count`, and `sensor_updated` true; `retained_previous_state` and `ambiguity_detected` false; no error stage/code or cleanup errors; raw count four; and two eligible primary candidates. An eligible primary was selected successfully. The user observed no duplicate FORA device or uric-acid entity. The private selected measurement, meter-local time, and Bluetooth address are excluded. The existing entry was targeted without a manually entered address.

This is **LIVE-CORROBORATED** for the specific tested session and Lounge proxy source. Unit-test and prior synthetic results remain separate and do not by themselves establish proxy traversal. No runtime change or test was needed for this documentation-only closure.

## Architecture and evidence boundary

The intended route is GD82 → **M5Stack Atom Lite ESPHome Bluetooth Proxy** → Home Assistant Bluetooth → `fora6_connect`. The integration's `Fora6BluetoothTransport.async_connect` calls `bluetooth.async_ble_device_from_address(hass, configured_address, connectable=True)` and passes the returned `BLEDevice` to `establish_connection`. It does not pin a scanner, rewrite a MAC, or run a separate scan. Home Assistant may choose among local adapters and proxies, and connector failover can change the route. The count-two/four manual refresh, identity, commands, sensor, and cleanup remain unchanged.

[Home Assistant's Bluetooth API](https://developers.home-assistant.io/docs/core/bluetooth/api/) describes connectable device resolution and per-scanner advertisement data through `async_scanner_devices_by_address`. These show reachability, **not necessarily the scanner that completed a connection**. The [Bluetooth adapter and network views](https://www.home-assistant.io/integrations/bluetooth/#viewing-your-bluetooth-adapters-and-proxies) identify registered scanners and device links, but a device appearing near Atom Lite is also insufficient on its own. [ESPHome's proxy documentation](https://esphome.io/components/bluetooth_proxy/) distinguishes advertisement reception from active GATT connections and identifies its `bluetooth_connection` log tag. Stage 9 needs evidence of the actual connection route.

Accepted route evidence, in order of directness:

1. A time-correlated Home Assistant connection monitor/diagnostic or Atom Lite `bluetooth_connection` connect/disconnect record identifies the Atom Lite as the active GATT carrier for the GD82 manual-action session. Keep the original record private and report only the sanitized source identity and success/cleanup flags.
2. A controlled isolation run: Home Assistant shows the Atom Lite online with active connection capability and **no other enabled connectable scanner that could reach the GD82** during the action. A successful transaction under that condition establishes the Atom Lite as the only available route. Check this before and after the action; restore the previous scanner configuration afterward. If another local adapter or proxy remains available, this argument is inconclusive.

An advertisement row, network-map proximity, scanner count, `BLEDevice` resolution, or successful FORA action while several scanners remain capable is supporting evidence only. No new production diagnostic or scanner-selection code is needed before this test. Do not persist scanner objects or expose scanner/MAC details in public action results.

## Controlled user procedure

1. In Home Assistant, confirm the configured FORA entry and existing single GD82/ForaCare device and uric-acid entity. Record the **count** of entries/devices/entities privately, without copying MAC or health state into Git.
2. Confirm the M5Stack Atom Lite is online in ESPHome and appears in **Settings → Connectivity → Bluetooth → Adapters**. Verify it is a connectable/active GATT proxy with an available connection slot, not merely an advertisement receiver. Privately identify its scanner/source in HA. [ESPHome active-connection behavior](https://esphome.io/components/bluetooth_proxy/) is distinct from scanning mode.
3. Inventory all other enabled connectable scanners, including local adapters and other proxies. Prefer direct, time-correlated connection evidence. For the clearest isolation test, temporarily **disable** local Bluetooth adapter entries and other connectable proxy entries through Home Assistant's entry controls **only if the UI offers a reversible Disable action and doing so will not disrupt other required devices**. Record each prior enabled state. Do not delete entries, change the meter, or alter ESPHome firmware. Confirm the HA adapter view now shows Atom Lite as the only enabled connectable route to the GD82. If isolation is unavailable or unsafe, leave adapters alone and require direct connection evidence instead.
4. Open the HA Bluetooth Connection Monitor or the Atom Lite's private ESPHome logs filtered to `bluetooth_connection`, if available, before the action. Use HA's adapter/network view to corroborate the source. Keep addresses and other private log contents local. A network-map advertisement edge alone does not establish the completed connection route.
5. Manually turn the GD82 **ON normally**. Do not press its history-arrow buttons. Do not start immediately from the post-measurement transfer state.
6. Invoke `fora6_connect.refresh_current_uric_acid`, selecting the existing FORA config entry. Do not enter a Bluetooth MAC. Run it once for this controlled test.
7. Privately inspect the action response for `refresh_successful`, supported raw count **2 or 4**, `sensor_updated`, `error_stage`, `error_code`, and `cleanup_errors`. The response's selected health value and meter-local time remain private. The existing count-two/four plans and semantic rules must pass without any new command.
8. Correlate the action window with the HA connection monitor or Atom Lite `bluetooth_connection` record. Record only whether **Atom Lite carried the active connection**, whether subscription/requests succeeded, and whether disconnect was observed. If using isolation instead, recheck the enabled-scanner inventory during/after the action and ensure no other connectable route appeared.
9. Confirm the **existing** uric-acid entity is available/updated as expected and still belongs to the same one GD82/ForaCare device. Confirm there is no second FORA entry, device, or entity. Do not publish the value, time, MAC, serial, System ID, screenshot, or raw log.
10. Restore every temporarily disabled local adapter/proxy to its recorded prior state. Confirm ordinary HA Bluetooth operation resumes. Retain the private raw observations outside Git; provide only the sanitized checklist below for Stage 9 closure.

If the user cannot safely isolate adapters and no connection-specific source evidence is available, the route remains **unproven** even if refresh succeeds. Do not infer it from the mere existence of the proxy.

## Sanitized result checklist for the user

Report only: Atom Lite online/active-capable; other connectable scanners isolated **yes/no**; connection-specific Atom Lite evidence **yes/no** (source type: HA connection monitor or ESPHome connection log); count supported **yes/no**; refresh successful **yes/no**; sensor updated **yes/no**; original entry/device/entity preserved **yes/no**; cleanup errors **none or safe code**; failure stage/code if any; adapter restoration complete **yes/no**. Do not include a measurement value, timestamp, MAC, IP, token, credential, raw frame, or unredacted log. An actual raw count of two or four is safe metadata if needed, but a boolean is enough for this gate.

## Pass, failure, and limits

Stage 9 passes only when Atom Lite is online and active-capable; a current GD82 connection is **attributable to Atom Lite** by direct connection evidence or valid sole-route isolation; the existing configured-entry action succeeds through identity, notification subscription, validated User1 count-two/four commands, selection, sensor update, and cleanup; and the same entry/device/entity remain. The existing factory-MAC identity and mg/dL unit remain unchanged. Do not infer that other proxy firmware, scanner placements, meter states, or record counts work.

If the test fails, retain the previous valid in-process sensor state and classify the first failing stage: proxy offline/capability, reachability, connectable resolution, connection, GATT/service discovery, subscription, wake/project, metadata/count, record part `0x25`/`0x26`, selection, cleanup, or **route unproven**. Compare with a separately observed local/native path only if such an observation exists; do not assume a prior Stage 7H success used local Bluetooth. Stage 8 preserves a primary failure code when cleanup also fails. Do not add retries, sleeps, scanner pinning, special MAC handling, or protocol changes without evidence and separate review.

**Stage 9 is complete for this bounded physical proxy-path validation. Exact next proposed gate:** separately authorize **Stage 10 — HACS packaging/readiness**. Stage 8H bounded history exposure remains optional and is not required before Stage 10. Neither Stage 8H nor Stage 10 is implemented or started by this closure.
