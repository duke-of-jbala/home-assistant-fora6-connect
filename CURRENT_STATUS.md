# Current Status — FORA 6 Connect

**Stage 4 reusable Bluetooth transport is implemented for its authorized scope and awaits controlled physical regression after review.** Stages 0, 1, 3, and 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open/deferred. No production discovery, synchronization, entity, or decoded real-result action exists.

## Stage 4 implementation

[The Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes `Fora6BluetoothTransport`: Home Assistant connectable-device resolution, the proven two-attempt connection pattern, custom Write/Notify characteristic validation, bounded single-response exchanges, privacy-safe failures, and cancellation-aware cleanup. `protocol_probe.py` now uses this transport while choosing the same identity and one-slot request sequences. Existing action result fields and timeouts are preserved. `gatt_probe.py` and `notification_observer.py` remain their prior development diagnostics.

Mock tests cover connection and GATT failures, timeout boundaries, invalid notifications, write-once behavior, privacy, concurrent exchanges, and cleanup. The refactor has **not** been run against a physical meter. No adapter or ESPHome proxy path is claimed. `protocol.py` and `models.py` remain Home Assistant/Bleak independent; they and all later-stage modules are unchanged.

## Exact next gate

Review Stage 4, then separately authorize a controlled user-run `fora6_connect.probe_protocol_identity` regression with the GD82 ON. The optional already-proven one-slot `fora6_connect.probe_protocol_record` may be authorized in that same controlled review. Compare privacy-safe status and cleanup flags with Stage 2E/2F. Do not add commands, decoded result exposure, or record loops. Stage 5 measurement/entity modeling needs separate authorization after the transport review and any chosen regression.

## Repository state at Stage 4 pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `de7001c1b7b9d5ecb808ee417db3f4b9893269f9` — `fix: preserve TD4183 QC semantics`.
- **Starting tree:** clean (`git status --short` empty before Stage 4 edits).
- **Changes after checkpoint:** yes; reusable transport, development-probe refactor, mock tests, and Markdown are changed at this pre-commit point. The task commit SHA and post-commit status are reported separately.
- **Files changed:** `custom_components/fora6_connect/bluetooth.py`, `custom_components/fora6_connect/protocol_probe.py`, `tests/test_bluetooth_transport.py`, `tests/test_protocol_probe.py`, `docs/STAGE4_BLUETOOTH_TRANSPORT.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, and `docs/PROTOCOL.md`.
- **Live actions by Codex:** none. No physical test, deployment, push, tag, or release.

## Checks actually run

- `python3 -m unittest discover -s tests -q`: 156 passed, including 37 new transport tests; existing identity and record probe regressions passed.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Manifest, translation, and strings JSON plus services YAML parsing: passed.
- `git diff --check` and `git diff --cached --check`: passed. The complete 15-file staged diff was inspected.
- Staged privacy/artifact scan found no private path, Bluetooth address, captured frame, APK/capture/keystore artifact, or private health data; no untracked file remained after staging. Neither transport nor probe logs raw bytes or addresses.
- `bluetooth.py` contains no FORA command ID or hard-coded adapter/interface selection. AST review confirmed `protocol.py` and `models.py` remain HA/Bleak independent. AST comparison found the action result dictionary unchanged from HEAD; service registration/input schemas and later-stage modules have no diff. Existing probe tests verify the same exact writes and response flags.
