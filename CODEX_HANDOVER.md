# FORA 6 Connect Codex Handover

## Task, checkpoint, and stage

Record the user-supplied real Stage 1B direct-connect GATT success without implementing protocol behavior. This document describes the dirty pre-commit state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `d9a850139163624ea0adba3a81676852fb15ea44` — `fix: connect directly in Stage 1B GATT probe`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes, seven documentation files listed below. Post-commit SHA and status must be checked and reported separately.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`.
- **Stage:** Stage 1 in progress; Stage 1B transport/GATT validation successful; Stage 2 unauthorized. Production automatic discovery remains later work. No push, tag, release, characteristic I/O, notification, pairing, RACP, or FORA application operation in this task.

## Real evidence and interpretation

The user supplied a privacy-safe result from the real `fora6_connect.probe_gatt` action: the FORA device was found, its normalized advertised name was confirmed, Home Assistant resolved a connectable BLEDevice, connected, enumerated five GATT services, and disconnected cleanly. Two connectable scanners were available, but the action did **not** identify which scanner/adapter handled the connection. The full observed UUID/property inventory and comparison with the earlier iPhone observation are in `docs/PROTOCOL.md`; every expected Device Information, Glucose, and custom 1523/1524 item/property was present. Generic Access and Generic Attribute services were also returned. This confirms Home Assistant-side transport/GATT, not a specific ESPHome connection path or any application protocol semantics.

The earlier advertisement callback/timeouts were discovery-layer failures and did not demonstrate a meter or GATT failure. The Advertisement Monitor popup was manually viewed and was not returned by the old action. Fresh Auto-mode discovery remains unresolved and does not negate the successful direct GATT result. The device's standard Glucose Service and FORA custom service coexist. Future protocol acquisition should consider standard Glucose/RACP and custom 1523/1524 as distinct possibilities; use of the custom path for non-glucose analytes is a hypothesis, not an observation.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 25 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this handover update; final rerun follows.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy audit — reviewed the final documentation diff: zero MAC-formatted literals; UUIDs are only the supplied public GATT service/characteristic identifiers. No private address, scanner/source identifier, raw advertisement, manufacturer payload bytes, serial value, health measurement, or secret was added.

## Exact Next Gate

Review the remaining Stage 1 discovery questions and plan a controlled, privacy-safe observation of raw notification behavior. A notification subscription or any further BLE operation requires separate explicit authorization; none is authorized by this task. Do not mark Stage 1 complete or begin Stage 2. Keep Auto-mode and production automatic discovery separate from the validated direct GATT result. Do not claim a particular scanner/proxy connection path without Connection Monitor evidence.
