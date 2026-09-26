# Current Stage

Stage 0 is complete. **Stage 1 — FORA 6 Connect BLE discovery is in progress; Stage 2 is not authorized.** Stage 1B is authorized only for development transport/GATT validation. Multiple user-run attempts of the first probe failed at the fresh-advertisement gate. No Home Assistant GATT connection was attempted and no FORA operation was transmitted. The targeted-wait revision in this task passes hardware-free tests but has not been run on the real Home Assistant system.

# Exact Next Gate

Replace the installed `custom_components/fora6_connect/` directory with this development checkout and restart Home Assistant Core. Leave Lounge in Auto and the meter in its normal advertising state, then invoke `fora6_connect.probe_gatt`. Report only its privacy-safe response or sanitized error. Distinguish no cached candidate from a targeted-wait timeout; if fresh discovery succeeds, record connectable-device resolution, actual GATT inventory, connection path checked privately, and disconnect outcome. Stage 1 remains open until the real result is reviewed. No Stage 2 or FORA application operations.

# Repository State at Pre-Commit Review

- **Date/branch:** 2026-09-26 (Europe/London), `main`.
- **Checkout:** `<local checkout>`.
- **Last completed checkpoint:** `04847ea6971e5dfb53ee24523e0d0e5195698f22` — `feat: add development GATT discovery probe`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes, the 11 files listed below. This document describes the dirty pre-commit state; verify and report the resulting commit SHA and tree state afterward.
- **Remote actions:** none. No push, tag, or release.

# Evidence and Change

- **Observed, user-supplied:** iPhone discovery and GATT inventory of the real meter; Home Assistant detected `FORA 6 CONNECT` through Lounge while Active after removal of the scan override and an ESPHome reflash. The later Auto monitor row did not refresh. Multiple calls to the first Stage 1B probe returned `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` No HA GATT connection followed. This does not indicate a meter or proxy GATT failure. EcoFlow activity and unrelated ESPHome API warnings are not FORA evidence.
- **Platform fact reviewed 2026-09-26:** [Home Assistant Bluetooth APIs](https://developers.home-assistant.io/docs/core/bluetooth/api/) document address-targeted `async_process_advertisements` with `BluetoothScanningMode.ACTIVE` and an active window for Auto scanners. [The current HA API implementation](https://github.com/home-assistant/core/blob/dev/homeassistant/components/bluetooth/api.py) shows the five-argument call. [The callback manager](https://github.com/home-assistant/core/blob/dev/homeassistant/components/bluetooth/manager.py) can replay cached history, so the predicate checks that the returned observation time exceeds both the cached candidate's time and the wait-start time.
- **Implemented:** discover a unique cached connectable candidate by exact local name, use its address only in memory for a 20-second targeted active wait, reject replay/wrong-name results using Home Assistant's monotonic observation clock, then resolve a connectable `BLEDevice` and use the existing retry-safe connection/GATT enumeration/disconnect path. Removed direct history clearing, manually registered callback, and separate broad scan call. Added privacy-safe DEBUG phase messages and sanitized missing-candidate/timeout errors.
- **Boundary:** no characteristic reads/writes, notifications, pairing, RACP, record retrieval, protocol parsing, production matcher, or entities. Public results/errors and added logs omit Bluetooth addresses, identifiers, serials, and health data.
- **Unknown:** whether the revised wait receives a live advertisement with Lounge in Auto, which adapter/proxy HA will select, whether HA can connect/enumerate GATT, and whether bonding is required. No new real-world success is claimed.

# Files Changed in This Task

`custom_components/fora6_connect/gatt_probe.py`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/PROTOCOL.md`, `CHANGELOG.md`, `README.md`, `ROADMAP.md`.

# Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 23 tests, 0 failures, 0 skipped; hardware-free mocks only.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass after code and documentation edits; rerun immediately before commit.
- `command -v ruff` — unavailable; Ruff not run.
- Privacy/source audit — 11 changed paths; added lines contain no MAC-like address, non-GATT UUID-like identifier, or secret assignment. No raw capture, serial value, or health measurement was added. Test addresses are non-Bluetooth placeholders.

# Last Updated

2026-09-26 (Europe/London), pre-commit review. Post-commit SHA and status belong in the final report.
