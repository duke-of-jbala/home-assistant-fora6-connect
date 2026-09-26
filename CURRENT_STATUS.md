# Current Stage

Stage 0 is complete. **Stage 1 — FORA 6 Connect BLE discovery is in progress.** Stage 1A preparation is complete; user-supplied, externally screenshot-reviewed iPhone observations established the real meter's local name, connectability, and GATT inventory. Home Assistant Advertisement Monitor did not show FORA in the tested ESPHome proxy state. Home Assistant-side discovery, connection, and GATT remain unvalidated. Stage 2 is not authorized.

# Current Gate

Correct/test Lounge ESPHome BLE scan timing in a controlled A/B test, repeat Home Assistant Advertisement Monitor observation, and determine whether Home Assistant can see `FORA 6 CONNECT` through the proxy. Only after Home Assistant discovery and separate authorization, validate Home Assistant-side connectability/GATT. No FORA application writes.

# Repository State at Pre-Commit Review

- **Actual checkout path:** `<local checkout>`; the directory move is complete.
- **Branch:** `main`.
- **Last completed checkpoint:** `418c0fe0eec26c9d2ef08a877fddc823ea0d8d18` — `refactor: rename integration to FORA 6 Connect`.
- **Changes after checkpoint:** yes — documentation-only Stage 1 evidence update in the files listed below. The task began with a clean tree (`git status --short --branch --untracked-files=all` showed `## main` only); the tree is dirty at this pre-commit review.
- **GitHub repository target:** `duke-of-jbala/home-assistant-fora6-connect`. No remote operation occurred in this task.

# Evidence and Provenance

- **Documentary Stage 0 claim:** the project brief reports FORA documentation listing custom service `00001523-1212-efde-1523-785feabcd123` and characteristic `00001524-1212-efde-1523-785feabcd123` with Write/Notify. The underlying document has not been independently inspected in this repository.
- **User-supplied observation, screenshots reviewed externally:** while the real meter's blue Bluetooth indicator flashed, a generic iPhone BLE scanner displayed local name `FORA 6 CONNECT`, connectable yes, and close-range RSSI around −50 dBm. It connected successfully and reported `BONDED`. Bonding requirement is unknown; the scanner may have initiated bonding automatically. No iPhone CoreBluetooth UUID or private device identifier is recorded.
- **User-supplied iPhone GATT observation:** Device Information `0x180A` with readable standard fields; Glucose `0x1808` with `0x2A18` Notify, `0x2A34` Notify, `0x2A51` Read, and `0x2A52` Write/Indicate; FORA custom `1523` service and `1524` characteristic with Write/Notify. This confirms the documentary custom UUIDs on the real device, not proprietary packet semantics.
- **User-supplied Home Assistant observation:** Bedroom and Lounge ESPHome proxies initially displayed `Auto (passive)`, with 0/3 and 1/3 slots in use respectively. Lounge was temporarily switched to Active scanning. With the meter indicator flashing and iPhone detection succeeding, Home Assistant Advertisement Monitor did not show FORA; it continued to show other BLE devices including the user's EcoFlow. This does not indicate a meter radio failure.
- **User-supplied Lounge configuration:** official ESPHome M5Stack Atom Lite Bluetooth proxy package `github://esphome/bluetooth-proxies/m5stack/m5stack-atom-lite.yaml@main`, plus explicit `esp32_ble_tracker` scan interval `320ms` and window `30ms`.
- **Hypothesis:** the approximately 9.4% scan duty cycle may cause missed advertisements. A controlled A/B test has not yet established causation.

# Unknowns and Limits

Home Assistant/ESPHome proxy discovery and GATT path; whether bonding is required; address behavior; manufacturer/service advertisement data; advertised UUIDs; Home Assistant scanner-source/RSSI relationship; notification behavior; FORA application commands/responses, packet format, checksums, records, analyte codes, timestamps, flags, units, and exact GD82 analyte support. No protocol behavior is inferred.

# Files Changed in This Task

`AGENTS.md`, `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, and `docs/PROTOCOL.md`. No integration code or tests changed.

# Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass: 5 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `command -v ruff` — Ruff unavailable; no Ruff checks claimed.
- `git diff --check` — pass.
- Documentation and privacy audit — no private MAC address, CoreBluetooth UUID, serial number, health measurement, raw capture, or secret included. Only public standard/documentary GATT UUIDs and sanitized observations appear.

# Authorization Boundary

Stage 1 remains in progress. Home Assistant-side GATT inspection requires discovery and separate authorization. Stage 2 is not authorized. No BLE writes, protocol implementation, push, tag, or release occurred in this task.

# Last Updated

2026-09-26 (Europe/London), at documentation-update pre-commit review. The task commit SHA and post-commit working-tree state are reported separately after commit.
