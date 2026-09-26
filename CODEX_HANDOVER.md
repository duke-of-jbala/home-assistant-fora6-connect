# FORA 6 Connect Codex Handover

## Task and Repository State at Pre-Commit Review

Document the user-supplied controlled Lounge ESPHome proxy retest and set the Stage 1B Home Assistant probe gate. This task changes documentation only.

- **Branch:** `main`.
- **Last completed checkpoint:** `a94a7613d6d3fb4b872c6b9a5cbaff5c4a39c58c` — `docs: record FORA 6 Connect BLE observations`.
- **Checkout path:** `<local checkout>`.
- **Starting working tree:** clean; `git status --short --branch --untracked-files=all` showed `## main`.
- **Changes after checkpoint:** yes — only the eight Markdown files listed below. The tree is dirty at this pre-commit review. Verify and report the post-commit state separately.

## Files Changed

Modified: `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `docs/CAPTURE_GUIDE.md`, `docs/PROTOCOL.md`.

Added, deleted, renamed: none. Integration code and tests did not change.

## Evidence and Provenance

The controlled retest below is **user-supplied**. Codex did not inspect the private UI address, access the Home Assistant or ESPHome systems, or perform a BLE operation.

| Phase | Reported observation |
| --- | --- |
| Before | Lounge M5Stack Atom Lite used explicit `esp32_ble_tracker` interval `320ms` and window `30ms`. Home Assistant Advertisement Monitor did not detect FORA, even when Lounge was temporarily set to Active. |
| Change | The explicit override was removed. Lounge was rebuilt and reflashed with ESPHome `2026.9.0`; Bedroom remained unchanged as control. |
| After | With Lounge temporarily in Active mode, Home Assistant Advertisement Monitor detected `FORA 6 CONNECT` through Lounge. The ESPHome → Home Assistant advertisement path worked in this tested state. |
| Auto retest | Lounge was returned to Auto. The existing FORA row stayed visible, but its Updated age did not refresh. No fresh Auto-mode advertisement was confirmed. |

The override removal and reflash occurred together. Their individual effects were not isolated, so scan timing is still only a possible explanation for the initial miss. The stale Auto row does not establish that Auto cannot support FORA.

Home Assistant's [Bluetooth API guidance](https://developers.home-assistant.io/docs/core/bluetooth/api/) documents `bluetooth.async_request_active_scan(hass)` as an on-demand active sweep across Auto-mode scanners. This supports the next probe design; the user's Auto-mode behavior remains to be tested.

The prior iPhone local-name, connectability, bonding, and GATT observations remain in `docs/PROTOCOL.md`. The private Bluetooth address shown in the Home Assistant UI is not included.

## Stage and Unknowns

**Stage 1 remains in progress.** Home Assistant Active-mode advertisement forwarding through Lounge is observed. A fresh Auto-mode advertisement, Home Assistant-side connection and GATT enumeration, bonding requirement, detailed advertisement fields, and FORA application protocol remain unverified. **Stage 2 is not authorized.**

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass: 5 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `command -v ruff` — Ruff unavailable; no Ruff check claimed.
- `git diff --check` — pass.
- Documentation/privacy audit — no private Bluetooth address, CoreBluetooth identifier, serial number, health measurement, raw capture, or secret included.

## Exact Next Gate

**Stage 1B — minimal development-only Home Assistant probe:** leave Lounge in Auto, call `bluetooth.async_request_active_scan(hass)`, resolve a fresh `FORA 6 CONNECT` observation through Home Assistant Bluetooth, obtain a connectable `BLEDevice` through supported APIs, connect through an available proxy, and enumerate GATT services/characteristics. Perform no application-level writes. The probe was not implemented in this documentation task.

## Authorization Boundary

No BLE writes, protocol code, push, tag, or release occurred. Stop after the documentation commit; Stage 2 remains unauthorized.

## Last Updated

2026-09-26 (Europe/London), at documentation pre-commit review. Report the new commit SHA and final working-tree state after commit.
