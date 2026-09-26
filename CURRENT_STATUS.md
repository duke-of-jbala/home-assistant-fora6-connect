# Current Stage

Stage 0 is complete. **Stage 1 remains in progress; Stage 2 is not authorized.** Stage 1B Home Assistant transport/GATT validation succeeded on the real FORA 6 Connect. The Stage 1C development-only notification observer is implemented and tested without hardware; **no real Stage 1C notification observation has yet been run**.

## Evidence, implementation, and limits

- **User-supplied real Stage 1B evidence:** Home Assistant resolved a connectable FORA BLEDevice, connected, enumerated five GATT services including the expected Device Information, Glucose, and custom 1523/1524 metadata, and disconnected cleanly. Two connectable scanners were reported, but the selected scanner/adapter is unknown. The full sanitized inventory is in `docs/PROTOCOL.md`. Auto-mode and production discovery remain unresolved separately.
- **Stage 1C action now available:** `fora6_connect.observe_notifications` privately accepts the known meter address, resolves a connectable BLEDevice through Home Assistant, connects with a fresh retry-safe no-pair client, verifies `2A18`, `2A34`, and custom `1524` Notify characteristics, subscribes for an initial 30 seconds, stops every successful subscription, and disconnects. It returns only notification counts, payload lengths/length counts, and distinct-payload counts. Raw payload bytes are never returned, logged, or persisted; only in-memory hashes are used for distinct counts.
- **Narrow CCCD authorization:** Bleak/Home Assistant may configure CCCDs as required by `start_notify`/`stop_notify` for those three characteristics. No application characteristic read/write, direct descriptor write, RACP operation, pairing, record retrieval, packet decoding, or FORA command is authorized or implemented. `2A52` is not subscribed. Zero notifications is a valid outcome and does not justify sending a command.
- **Unknown:** real Stage 1C subscription/notification behavior, selected connection path, fresh Auto-mode discovery, and all FORA application packet semantics. The standard Glucose Service and custom service coexist; which path carries non-glucose analytes remains a hypothesis. Stage 1 is not complete.

## Exact Next Gate

Install this checkout's complete `custom_components/fora6_connect/` directory in Home Assistant, ensure the top-level `fora6_connect:` YAML entry is present, check configuration, and restart Core. Lounge may be temporarily Active. While the meter is in its normal Bluetooth transfer state, privately identify its known address in Advertisement Monitor and run **Developer Tools → Actions → `fora6_connect.observe_notifications`** with that address. Wait through the 30-second observation window and cleanup. Share only the privacy-safe result or safe error, including zero counts if no notifications arrive; keep addresses, raw bytes, and logs with private data out of Git and messages. Do not make a new health measurement solely to generate traffic. Review the real result and remaining Stage 1 discovery questions before changing stage status. Do not begin Stage 2.

## Repository State at Pre-Commit Review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `990a45087f20fbe5fd3273859fc27c6e9b384568` — `docs: sync project status after GATT validation`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes; this is the dirty pre-commit state. Verify and report the post-commit state separately.
- **Files changed:** `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/notification_observer.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `tests/test_gatt_probe.py`, `tests/test_notification_observer.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md`, `docs/STAGE1_OBSERVATION_TEMPLATE.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`.
- **Remote actions:** none; no push, tag, or release. No BLE operation was run from this repository task.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 40 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this status update; final rerun follows.
- `python3 -m json.tool custom_components/fora6_connect/translations/en.json` — pass.
- Parsed `custom_components/fora6_connect/services.yaml` with PyYAML — pass; both development actions present.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy/source audit — reviewed added lines and new files: zero MAC-formatted literals; UUIDs are only the public observed GATT identifiers and a public RACP UUID used in a forbidden-operation test. No real address, scanner identifier, raw capture, manufacturer payload, health measurement, serial value, or secret was added. Observer source has no characteristic read/write, direct descriptor write, pairing, or RACP call. Tests use synthetic payloads/addresses and assert no raw payload in results, no address in results/errors/logs, and no address persistence through the service action.

Updated 2026-09-26 (Europe/London), pre-commit.
