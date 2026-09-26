# FORA 6 Connect Codex Handover

## Task, checkpoint, and stage

This task records a user-supplied Home Assistant Advertisement Monitor detail popup separately from the failing Stage 1B development action, and fixes the evidence-backed trailing-NUL name comparison. This document describes the dirty pre-commit state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `9178e0fd88de5e82d5d2937503796c3a7a711a40` — `fix: allow private address for Stage 1B probe`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes, nine modified files listed below. Post-commit SHA and tree status must be checked and reported separately.
- **Stage:** Stage 1 in progress, Stage 2 unauthorized. Production automatic discovery remains Stage 6 work. No push, tag, release, or FORA application operation.

## Evidence provenance and interpretation

The user manually opened the real `FORA 6 CONNECT` row in **Settings → Connectivity → Bluetooth → Advertisement Monitor**. The detail popup showed: connectable yes; BLE flags present; Complete Local Name `FORA 6 CONNECT` plus **five trailing NULs**; advertised 16-bit services `0x1808` Glucose and `0x180A` Device Information; manufacturer-specific data present; custom `0x1523` absent from this observed advertisement. The earlier connected iPhone GATT inventory independently showed custom service `0x1523` and characteristic `0x1524`. Advertisement service lists are not complete GATT inventories. Private addresses, source identifiers, raw packet, and manufacturer payload are omitted.

**The popup packet was not returned by `fora6_connect.probe_gatt`.** The latest action still reported `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not reach Home Assistant GATT connection or any FORA operation. The prior exact raw-name comparison would reject a packet with this padding. This may explain rejection if the action received the same representation, but the popup does not establish that its wait callback received it. A separate active-wait/API-path issue remains possible.

## Narrow implementation

`normalize_local_name(name: str | None)` returns `None` unchanged and removes only trailing NUL characters from a string. It preserves spaces, leading NULs, and all other characters. The packet-name accessor applies it for both targeted predicate comparison and the privacy-safe response, without mutating Home Assistant's service-info object. The manual private runtime address field remains. The current probe has no general/cached candidate lookup; a test checks the shared accessor against a general-discovery service-info shape. The 20-second targeted active wait and connection path were not redesigned.

No characteristic reads/writes, notifications, pairing, RACP, record retrieval, protocol parsing, sensors, or production discovery were added. The address remains in memory and is not returned, persisted, or logged by this integration. The revised normalization has not yet been run on the real Home Assistant instance.

## Files Changed

`custom_components/fora6_connect/gatt_probe.py`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 31 tests, 0 failures, 0 skipped. Normalization, privacy, and strict no-I/O tests pass.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this handover update; rerun after the final edit and before commit.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy audit — inspected added code, tests, and documentation. No real Bluetooth/scanner address, raw packet, manufacturer payload, serial number, health measurement, credential, or private UUID was added. An automated check found zero new MAC-formatted addresses and zero unexpected UUID-formatted identifiers. The probe source still has no characteristic read/write, notification, pairing, or RACP call; tests verify the boundary.

## Exact Next Gate

Replace `<Home Assistant config>/custom_components/fora6_connect/` with this checkout's complete `custom_components/fora6_connect/` directory, check configuration, and restart Home Assistant Core. Leave Lounge in Auto. Privately enter the address from the previously identified FORA Advertisement Monitor row in **Developer Tools → Actions → `fora6_connect.probe_gatt`** during the meter's transfer window. Share only the sanitized action result/error. Establish whether the action itself receives a fresh packet after the normalization correction. If it does not, investigate the active-wait/API path within Stage 1B. Only a fresh action packet can lead to connectable resolution and read-only GATT inventory. The UI popup alone cannot satisfy that gate. Stage 2 remains unauthorized.
