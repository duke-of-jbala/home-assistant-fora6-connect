# Current Status — FORA 6 Connect

**Stage 4 reusable Bluetooth transport is implemented and its post-review session/cancellation hardening is verified with mocks; controlled physical regression remains pending.** Stages 0, 1, 3, and 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open/deferred. No production discovery, synchronization, entity, or decoded real-result action exists.

## Stage 4 implementation

[The Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes `Fora6BluetoothTransport`: Home Assistant connectable-device resolution, the proven two-attempt connection pattern, custom Write/Notify characteristic validation, bounded single-response exchanges, privacy-safe failures, and cancellation-aware cleanup. A failed exchange after a write attempt now invalidates that session, so a delayed response cannot satisfy a later same-command request. Connector cancellation is explicitly owned: a client returned during cancellation or timeout is disconnected before propagation; a client returned only after the bounded wait is disconnected by a completion callback. `protocol_probe.py` still chooses the same identity and one-slot request sequences. Existing action result fields and timeouts are preserved. `gatt_probe.py` and `notification_observer.py` remain their prior development diagnostics.

Mock tests cover connection and GATT failures, timeout boundaries, invalid notifications, poisoned-session rejection, write-once behavior, privacy, concurrent exchanges, and cancellation cleanup. The refactor has **not** been run against a physical meter. No adapter or ESPHome proxy path is claimed. `protocol.py` and `models.py` remain Home Assistant/Bleak independent; they and all later-stage modules are unchanged.

## Exact next gate

Review Stage 4, then separately authorize a controlled user-run `fora6_connect.probe_protocol_identity` regression with the GD82 ON. The optional already-proven one-slot `fora6_connect.probe_protocol_record` may be authorized in that same controlled review. Compare privacy-safe status and cleanup flags with Stage 2E/2F. Do not add commands, decoded result exposure, or record loops. Stage 5 measurement/entity modeling needs separate authorization after the transport review and any chosen regression.

## Repository state at hardening pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `b457289eec66f603130b24d2401449c276f8e4f7` — `feat: add reusable Home Assistant Bluetooth transport`.
- **Starting tree:** clean (`git status --short` empty before hardening edits).
- **Changes after checkpoint:** yes; transport session/cancellation handling, transport tests, and Markdown are changed at this pre-commit point. The task commit SHA and post-commit status are reported separately.
- **Files changed:** `custom_components/fora6_connect/bluetooth.py`, `tests/test_bluetooth_transport.py`, `docs/STAGE4_BLUETOOTH_TRANSPORT.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, and `CHANGELOG.md`.
- **Live actions by Codex:** none. No physical test, deployment, push, tag, or release.

## Checks actually run

- `python3 -m unittest discover -s tests -q`: 163 passed, including 44 transport tests; existing identity and record probe regressions passed.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Manifest, translation, and strings JSON plus services YAML parsing: passed.
- `git diff --check` and `git diff --cached --check`: passed with the seven changed files staged. The complete staged diff was inspected.
- Privacy/artifact scan of added lines and tracked paths found no private path, address, captured frame, APK/capture/keystore artifact, or private health data. Neither transport nor probe logs raw bytes or addresses.
- `bluetooth.py` contains no FORA command ID, logging call, or hard-coded adapter/interface selection. AST review confirmed `protocol.py` and `models.py` remain HA/Bleak independent. Action/service/protocol/model files have no diff from the checkpoint; existing probe regressions verify the same exact writes and result fields.
