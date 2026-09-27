# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stage 4 reusable Home Assistant Bluetooth transport and its post-review session/cancellation hardening are implemented for their authorized scopes; controlled physical regression is pending separate review and user action. Stages 0, 1, 3, and 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open/deferred. Stage 5 has not started.

- **Branch:** `main`.
- **Last completed checkpoint:** `b457289eec66f603130b24d2401449c276f8e4f7` — `feat: add reusable Home Assistant Bluetooth transport`.
- **Starting tree:** clean, verified with `git status --short` before the hardening edits.
- **Changes after checkpoint:** yes; transport failure/cancellation handling, mock tests, and Markdown are changed at this pre-commit point. Report the task commit SHA and post-commit status separately.
- **Live actions by Codex:** none. No deployment, push, tag, release, or physical meter test.

## Implementation and behavior

`bluetooth.py` contains `Fora6BluetoothTransport(hass, runtime_address)`. It resolves a connectable `BLEDevice` through Home Assistant, uses the repository's proven two-attempt connector pattern, validates the custom Write/Notify characteristic, subscribes, performs one command-agnostic request/response exchange at a time, and closes deterministically. It bounds connection, notification, write, response, and cleanup waits; serializes exchanges per instance; fails malformed pending notifications closed; retries no application write; and exposes stable privacy-safe error codes. A failure after any application write attempt poisons the session; later exchanges return `invalid_session_state` with no write, so delayed same-command responses cannot contaminate another exchange. Pre-write rejection does not poison. The connector task is owned through cancellation or timeout, and any returned client is disconnected, including a late client returned after the bounded cancellation wait. No raw notification queue, address logging, or hard-coded adapter path exists. [The Stage 4 record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) documents the API and limits.

`protocol_probe.py` delegates transport mechanics to this class but retains the two existing bounded command sequences, service/action names, input/result schemas, timeout settings, and privacy semantics. Existing probe tests pass. `gatt_probe.py` and `notification_observer.py` were not refactored. `protocol.py` and `models.py` are unchanged and remain HA/Bleak independent. No production discovery, config flow, synchronization, entity, polling, pairing, RACP, or additional command path was introduced.

## Exact next gate and checks

**Next gate:** review Stage 4 and separately authorize a controlled user-run identity regression on the GD82 with the meter ON, optionally followed by the already-proven one-slot record action. Stage 5 measurement/entity work needs a distinct later authorization. Do not claim a physical transport regression or a selected proxy before that test.

- **Files changed at pre-commit:** `custom_components/fora6_connect/bluetooth.py`, `tests/test_bluetooth_transport.py`, `docs/STAGE4_BLUETOOTH_TRANSPORT.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, and `CHANGELOG.md`.
- **Checks actually run:** 163 unit tests passed (44 transport tests); existing probe regressions retained exact writes and result fields. Compileall, tabnanny, integration JSON and YAML parsing, `git diff --check`, and `git diff --cached --check` passed with all seven changed files staged. The complete diff was inspected. Added-line privacy/artifact review found no private path, Bluetooth address, captured frame, APK/capture/keystore artifact, or health data; tracked artifact paths were clean. Neither transport nor probe logs raw bytes or addresses. `bluetooth.py` has no FORA command ID, logging call, or adapter hard-coding. AST review confirmed `protocol.py` and `models.py` remain HA/Bleak independent. Action/service/protocol/model files have no diff from the checkpoint; existing probe tests verify the same exact writes and response flags.
