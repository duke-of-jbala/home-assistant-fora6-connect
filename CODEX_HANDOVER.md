# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stage 4 reusable Home Assistant Bluetooth transport is COMPLETE for its authorized scope, including user-run physical regression validation of both existing development actions. Stages 0, 1, 3, and 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open/deferred. Stage 5 has not started.

- **Branch:** `main`.
- **Last completed checkpoint:** `50bccaaf04a54c6ec50b11c636e2ad8bca4abdde` — `fix: harden Bluetooth session failure handling`.
- **Starting tree:** clean, verified with `git status --short` before this documentation closure.
- **Changes after checkpoint:** yes; documentation/status files only are changed at this pre-commit point. Report the task commit SHA and post-commit status separately.
- **Physical evidence provenance:** user-supplied privacy-safe result summaries; meter ON; run date not supplied. No private address, raw frame, health value, timestamp, or identifier is retained.
- **Actions by Codex:** no live Home Assistant action or physical test. No deployment, push, tag, or release.

## Implementation and behavior

`bluetooth.py` contains `Fora6BluetoothTransport(hass, runtime_address)`. It resolves a connectable `BLEDevice` through Home Assistant, uses the repository's proven two-attempt connector pattern, validates the custom Write/Notify characteristic, subscribes, performs one command-agnostic request/response exchange at a time, and closes deterministically. It bounds connection, notification, write, response, and cleanup waits; serializes exchanges per instance; fails malformed pending notifications closed; retries no application write; and exposes stable privacy-safe error codes. A failure after any application write attempt poisons the session; later exchanges return `invalid_session_state` with no write, so delayed same-command responses cannot contaminate another exchange. Pre-write rejection does not poison. The connector task is owned through cancellation or timeout, and any returned client is disconnected, including a late client returned after the bounded cancellation wait. No raw notification queue, address logging, or hard-coded adapter path exists. [The Stage 4 record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) documents the API and limits.

`protocol_probe.py` delegates transport mechanics to this class but retains the two existing bounded command sequences, service/action names, input/result schemas, timeout settings, and privacy semantics. The user reports both real regressions succeeded with the meter ON: identity `0x22 → 0x24` and bounded record `0x22 → 0x24 → User1 0x2B → User1/index-zero 0x25 → User1/index-zero 0x26`. Both stopped notifications and disconnected cleanly. The record action returned only semantic status and no analyte, measurement, or scaling result. This closes Stage 4 transport validation; the selected HA adapter/proxy remains unknown. `gatt_probe.py` and `notification_observer.py` were not refactored. `protocol.py` and `models.py` remain HA/Bleak independent. No production discovery, config flow, synchronization, entity, polling, pairing, RACP, or additional command path was introduced.

## Exact next gate and checks

**Next gate:** Stage 4 is complete. Stage 5 remains unstarted and requires separate authorization after its measurement/entity scope is reviewed, including supported analytes and unresolved units/category policy. The exact selected adapter/proxy, Auto-mode discovery, address identity/stability, unresolved protocol semantics, and production synchronization remain open.

- **Files changed at pre-commit:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, and `docs/STAGE4_BLUETOOTH_TRANSPORT.md`.
- **Checks actually run:** 163 unit tests passed; compileall, tabnanny, integration JSON/YAML parsing, `git diff --check`, and `git diff --cached --check` passed. The complete staged documentation diff was inspected. Privacy/artifact scan found no private path, address, frame, value, timestamp, identifier, or binary artifact; changed paths are Markdown only.
