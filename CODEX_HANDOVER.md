# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stage 4 reusable Home Assistant Bluetooth transport is implemented for its authorized scope; controlled physical regression is pending separate review and user action. Stages 0, 1, 3, and 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open/deferred. Stage 5 has not started.

- **Branch:** `main`.
- **Last completed checkpoint:** `de7001c1b7b9d5ecb808ee417db3f4b9893269f9` — `fix: preserve TD4183 QC semantics`.
- **Starting tree:** clean, verified with `git status --short` before Stage 4 edits.
- **Changes after checkpoint:** yes; transport, probe refactor, mock tests, and Markdown are changed at this pre-commit point. Report the task commit SHA and post-commit status separately.
- **Live actions by Codex:** none. No deployment, push, tag, release, or physical meter test.

## Implementation and behavior

`bluetooth.py` contains `Fora6BluetoothTransport(hass, runtime_address)`. It resolves a connectable `BLEDevice` through Home Assistant, uses the repository's proven two-attempt connector pattern, validates the custom Write/Notify characteristic, subscribes, performs one command-agnostic request/response exchange at a time, and closes deterministically. It bounds connection, notification, write, response, and cleanup waits; serializes exchanges per instance; fails malformed pending notifications closed; retries no application write; and exposes stable privacy-safe error codes. No raw notification queue, address logging, or hard-coded adapter path exists. [The Stage 4 record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) documents the API and limits.

`protocol_probe.py` delegates transport mechanics to this class but retains the two existing bounded command sequences, service/action names, input/result schemas, timeout settings, and privacy semantics. Existing probe tests pass. `gatt_probe.py` and `notification_observer.py` were not refactored. `protocol.py` and `models.py` are unchanged and remain HA/Bleak independent. No production discovery, config flow, synchronization, entity, polling, pairing, RACP, `0x2F`, or `0x33` path was introduced.

## Exact next gate and checks

**Next gate:** review Stage 4 and separately authorize a controlled user-run identity regression on the GD82 with the meter ON, optionally followed by the already-proven one-slot record action. Stage 5 measurement/entity work needs a distinct later authorization. Do not claim a physical transport regression or a selected proxy before that test.

- **Files changed at pre-commit:** `custom_components/fora6_connect/bluetooth.py`, `custom_components/fora6_connect/protocol_probe.py`, `tests/test_bluetooth_transport.py`, `tests/test_protocol_probe.py`, `docs/STAGE4_BLUETOOTH_TRANSPORT.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, and `docs/PROTOCOL.md`.
- **Checks actually run:** 156 unit tests passed (37 new transport tests); existing probe regressions retained exact writes and result fields. Compileall, tabnanny, manifest/translation/strings JSON, services YAML, `git diff --check`, and `git diff --cached --check` passed. The complete 15-file staged diff was inspected. Staged privacy/artifact review found no private path, Bluetooth address, captured frame, APK/capture/keystore artifact, or health data; no untracked file remained. Neither transport nor probe logs raw bytes or addresses. `bluetooth.py` has no FORA command ID or adapter hard-coding. AST review confirmed `protocol.py` and `models.py` remain HA/Bleak independent; AST comparison found the action result dictionary unchanged from HEAD. Service registration/input schemas and later-stage modules have no diff.
