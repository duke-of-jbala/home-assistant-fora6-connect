# FORA 6 Connect Codex Handover

## Task and Observed State

Fix the authorized development-only Stage 1B probe's cached-candidate gate after a second user-run discovery failure. This handover describes the dirty pre-commit state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `918d3c349599168de3ace331e2d53978399409c7` — `fix: use targeted active scan for GATT probe`.
- **Starting tree:** clean (`git status --short --branch` showed `## main`).
- **Changes after checkpoint:** yes, 11 files listed below. Report the new full commit SHA and final status after committing.
- **Stage:** Stage 1 in progress; Stage 2 unauthorized. No push, tag, release, or FORA application operation.

## Real Evidence and API Distinction

The first real Stage 1B build repeatedly returned `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` The next targeted-wait build was installed in Home Assistant and returned `No known FORA 6 CONNECT candidate is available for targeted active scanning; first observe it in Home Assistant Bluetooth.` The latter stopped before its targeted wait, Home Assistant GATT connection, or any FORA operation. The device had previously appeared in Advertisement Monitor, but this does not prove current cache presence. Prior iPhone GATT discovery and the Lounge Active-mode HA advertisement remain valid. The failures do not diagnose a meter or proxy GATT problem.

The previously installed build searched the connectable-only discovery cache before waiting. The revision searches Home Assistant's general history using `async_discovered_service_info(hass, connectable=False)`. It prefers `service_info.advertisement.local_name`, then `service_info.name`; it does not compare `BLEDevice.name` as a separate advertised-name source. Safe DEBUG counts report all general discoveries, exact FORA name matches, and connectable scanners without listing names or addresses. No current general candidate produces a sanitized error with those counts.

For a unique candidate, its address remains in memory and `async_process_advertisements` waits up to 20 seconds with an address matcher, explicit `connectable=False`, and `BluetoothScanningMode.ACTIVE`. The explicit flag matters because Home Assistant's callback matcher otherwise defaults to connectable-only. The predicate requires the same address, local name, and an observation time later than the cached candidate and wait start. Only then does `async_ble_device_from_address(hass, fresh_info.address, connectable=True)` gate the GATT-capable connection path. The existing new-client retry-safe connection, GATT metadata enumeration, sanitized errors, and `finally` disconnect remain. No reads/writes, notifications, pairing, RACP, records, protocol parser, sensors, or production discovery were added.

Official/primary sources reviewed 2026-09-26: [Home Assistant Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/), [Home Assistant callback manager](https://github.com/home-assistant/core/blob/dev/homeassistant/components/bluetooth/manager.py), [habluetooth history manager](https://github.com/Bluetooth-Devices/habluetooth/blob/main/src/habluetooth/manager.py), and [BluetoothServiceInfoBleak model](https://github.com/Bluetooth-Devices/habluetooth/blob/main/src/habluetooth/models.py). They support the implementation distinction but do not validate the user's real HA connection path.

## Files Changed

`custom_components/fora6_connect/gatt_probe.py`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/PROTOCOL.md`, `CHANGELOG.md`, `README.md`, `ROADMAP.md`.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 25 tests, 0 failures, 0 skipped. Tests cover a general-only candidate, targeted fresh wait, name-field mismatch, timeout, absent candidate, absent connectable BLEDevice, connection/GATT/disconnect failures, privacy-safe output/logging, and no forbidden GATT calls.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass after code and documentation edits; rerun immediately before commit.
- `command -v ruff` — unavailable; Ruff not run.
- Privacy/source audit — 11 changed paths; added lines contain no MAC-like address, private UUID-like identifier, or secret assignment. No serial value, health measurement, raw capture, or FORA protocol operation was added. Test addresses are non-Bluetooth placeholders. No real-system test of this revision occurred in the checkout.

## Exact Next Gate

Replace the installed `<Home Assistant config>/custom_components/fora6_connect/` directory with this checkout's complete `custom_components/fora6_connect/` directory and restart Home Assistant Core. Leave Lounge in Auto, make the meter advertise normally, then invoke **Developer Tools → Actions → `fora6_connect.probe_gatt`** with no target/data. Share only the sanitized response or error; keep private addresses, raw logs, serials, and health measurements out of Git. Record the safe discovery counts, targeted-wait result, connectable resolution, actual GATT inventory, and disconnect outcome. Check the selected connection path privately if needed. Stage 1 remains open pending review; Stage 2 is unauthorized.
