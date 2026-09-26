# Current Stage

Stage 0 is complete. **Stage 1 — FORA 6 Connect BLE discovery is in progress.** User-supplied iPhone observations established the real meter's local name, connectability, and GATT inventory. In a later user-supplied controlled retest, Home Assistant Advertisement Monitor detected `FORA 6 CONNECT` through the Lounge ESPHome proxy while Lounge was temporarily in Active scanning mode. A fresh Auto-mode advertisement and Home Assistant-side connection/GATT remain unconfirmed. Stage 2 is not authorized.

# Current Gate

**Stage 1B — minimal development-only Home Assistant probe:** leave Lounge in Auto; call `bluetooth.async_request_active_scan(hass)`; resolve a fresh `FORA 6 CONNECT` observation through Home Assistant Bluetooth; obtain a connectable `BLEDevice` through supported APIs; connect through an available proxy; enumerate GATT services and characteristics. Do not make application-level FORA writes. This probe was not implemented in the current documentation task.

# Repository State at Pre-Commit Review

- **Actual checkout path:** `<local checkout>`.
- **Branch:** `main`.
- **Last completed checkpoint:** `a94a7613d6d3fb4b872c6b9a5cbaff5c4a39c58c` — `docs: record FORA 6 Connect BLE observations`.
- **Changes after checkpoint:** yes — documentation-only updates in the eight files listed below. The task began with a clean tree (`git status --short --branch --untracked-files=all` showed `## main`); this is the dirty pre-commit state.
- **Remote operations:** none in this task. No push, tag, or release.

# Evidence and Provenance

- **Prior user-supplied iPhone observation:** the real meter appeared as `FORA 6 CONNECT` while its blue Bluetooth indicator flashed; it was connectable, the scanner connected, and the iPhone GATT view showed standard Device Information and Glucose services plus the documentary FORA `1523`/`1524` service/characteristic. Bonding was reported, but whether required remains unknown. The prior evidence register contains the details.
- **Before controlled retest — user-supplied observation:** Lounge M5Stack Atom Lite had an explicit `esp32_ble_tracker` scan interval `320ms` and window `30ms`. Home Assistant Advertisement Monitor did not detect FORA, even with Lounge temporarily set to Active.
- **Change — user-supplied environment action:** the explicit `320ms`/`30ms` override was removed. Lounge was rebuilt and reflashed using ESPHome `2026.9.0`. Bedroom remained unchanged as a control.
- **After change — user-supplied observation:** with Lounge temporarily set to Active, Home Assistant Advertisement Monitor detected `FORA 6 CONNECT` through the Lounge ESPHome proxy. The ESPHome → Home Assistant advertisement path works in this tested state. Because override removal and firmware reflash occurred together, the result does not isolate the prior cause.
- **Auto retest — user-supplied observation:** Lounge was returned to Auto. The previous FORA row remained, but its Updated age did not refresh during the test. A fresh Auto-mode advertisement was not confirmed. This does not establish that Auto cannot support FORA.
- **Platform documentation:** Home Assistant's [Bluetooth API guidance](https://developers.home-assistant.io/docs/core/bluetooth/api/) documents that `bluetooth.async_request_active_scan(hass)` performs an on-demand active sweep of Auto-mode scanners. This platform capability was checked for the planned probe, not demonstrated on the user's system in Auto mode.
- **Privacy:** the private Bluetooth address displayed in the UI is not recorded.

# Unknowns and Limits

Fresh Auto-mode observation under an on-demand active scan; Home Assistant-side connectability and GATT; whether bonding is required; detailed advertisement fields, address behavior, and FORA application protocol. The Lounge scan-timing override may have contributed to the initial miss, but causation remains unproven. No protocol semantics are inferred from the GATT inventory.

# Files Changed in This Task

`CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `docs/CAPTURE_GUIDE.md`, and `docs/PROTOCOL.md`. No code or tests changed.

# Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass: 5 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `command -v ruff` — Ruff unavailable; no Ruff check claimed.
- `git diff --check` — pass.
- Documentation/privacy audit — no private Bluetooth address, CoreBluetooth identifier, serial number, health measurement, raw capture, or secret included.

# Authorization Boundary

Stage 1 remains in progress. The Stage 1B probe is the next gate and was not begun in this documentation task. Stage 2 is not authorized. No application-level BLE writes, protocol implementation, push, tag, or release occurred.

# Last Updated

2026-09-26 (Europe/London), at this documentation task's pre-commit review. The new commit SHA and post-commit working-tree state are reported separately.
