# FORA 6 Connect Codex Handover

## Task, checkpoint, and stage

Implement the explicitly authorized development-only Stage 1C notification-metadata observer after real Stage 1B Home Assistant GATT success. This document describes the dirty pre-commit state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `990a45087f20fbe5fd3273859fc27c6e9b384568` — `docs: sync project status after GATT validation`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes, 17 files listed below. Post-commit SHA and status must be checked and reported separately.
- **Files changed:** `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/notification_observer.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `tests/test_gatt_probe.py`, `tests/test_notification_observer.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md`, `docs/STAGE1_OBSERVATION_TEMPLATE.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`.
- **Stage:** Stage 1 in progress; Stage 1B transport/GATT validation successful; Stage 1C observer implemented with no real-device result yet; Stage 2 unauthorized. Production automatic discovery remains later work. No push, tag, release, or live BLE operation in this task.

## Evidence and implementation

Real Stage 1B action evidence established connectable resolution, successful Home Assistant connection, five GATT services with the expected Glucose and FORA custom structure, and clean disconnect. The selected scanner/adapter is unknown; fresh Auto-mode discovery is unconfirmed. The full sanitized inventory is in `docs/PROTOCOL.md`.

The new development-only `fora6_connect.observe_notifications` action requires the privately known address. It resolves through Home Assistant Bluetooth, creates a fresh retry-safe no-pair client, confirms Notify properties on Glucose Measurement `2A18`, Context `2A34`, and custom `1524`, subscribes for 30 seconds, and stops each successful subscription before disconnect. A shared lock prevents concurrent Stage 1B/1C actions. It returns only per-characteristic notification counts, payload length metadata, and distinct-payload counts from in-memory SHA-256 digests. Neither raw payloads nor digests are returned, logged, persisted, or placed in fixtures. Zero notifications is valid evidence.

Bleak/Home Assistant may configure CCCDs when `start_notify`/`stop_notify` is called; that narrow descriptor activity is explicitly authorized for Stage 1C. The integration does not call characteristic reads/writes, direct descriptor writes, pairing, RACP, record retrieval, or packet parsing. `2A52` is not subscribed. No real Stage 1C result is claimed. The temporary observer does not implement production transport or discovery.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 40 tests, 0 failures, 0 skipped. Tests cover attribution, lengths/distinct counts, zero traffic, missing characteristics, partial failures, cleanup including cancellation, privacy, no persistence, and forbidden-operation boundaries.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this handover update; final rerun follows.
- `python3 -m json.tool custom_components/fora6_connect/translations/en.json` — pass.
- Parsed `custom_components/fora6_connect/services.yaml` with PyYAML — pass; both development actions present.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy/source audit — reviewed added lines and new files: zero MAC-formatted literals; UUIDs are only public observed GATT identifiers and a public RACP UUID in a forbidden-operation test. No real address, scanner identifier, raw capture, manufacturer payload, health measurement, serial value, or secret was added. Observer source has no characteristic read/write, direct descriptor write, pairing, or RACP call.

## Exact Next Gate

Install the complete `custom_components/fora6_connect/` directory in Home Assistant, retain/add top-level `fora6_connect:` in `configuration.yaml`, check configuration, and restart Core. Lounge may temporarily remain Active. Privately identify the known FORA address in Advertisement Monitor and run **Developer Tools → Actions → `fora6_connect.observe_notifications`** with it while the meter is in its normal Bluetooth transfer state. The action observes for 30 seconds plus connection/cleanup time. Share only its privacy-safe counts/lengths/result or safe error; zero notifications is acceptable. Keep identifiers, raw bytes, and unredacted logs private. Do not make a new health measurement solely to generate traffic. Review the real result and remaining discovery questions before Stage 1 closure. Stage 2 remains unauthorized.
