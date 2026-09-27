# Current Status — FORA 6 Connect

**Stage 4 — reusable Home Assistant Bluetooth transport is COMPLETE for its authorized scope, including successful user-run physical regression validation of both existing development actions.** Stages 0, 1, 3, and 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open/deferred. No production discovery, synchronization, entity, or decoded real-result action exists.

## Stage 4 implementation

[The Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes `Fora6BluetoothTransport`: Home Assistant connectable-device resolution, the two-attempt connection pattern, custom Write/Notify characteristic validation, bounded single-response exchanges, privacy-safe failures, and cancellation-aware cleanup. A failed exchange after a write attempt invalidates that session, so a delayed response cannot satisfy a later same-command request. Connector cancellation is explicitly owned and obtained clients are disconnected. The user reported that both `probe_protocol_identity` and `probe_protocol_record` succeeded on the real GD82 with the meter ON using the hardened transport; both stopped notifications and disconnected cleanly. The record action exposed no decoded measurement. `protocol_probe.py` retains the same sequences and result fields. `gatt_probe.py` and `notification_observer.py` remain prior development diagnostics.

The physical regressions confirm the identity path `0x22 → 0x24` with project `0x4183`, and the bounded record path `0x22 → 0x24 → User1 0x2B → User1/index-zero 0x25 → User1/index-zero 0x26`. They validate the reusable transport and the probe refactor, not production synchronization or measurement exposure. The selected HA adapter/proxy, Auto-mode discovery, address identity/stability, unresolved protocol semantics, and production synchronization behavior remain open. `protocol.py` and `models.py` remain Home Assistant/Bleak independent.

## Exact next gate

Stage 4 is closed. Stage 5 has not started. Its entry gate is separate user authorization after reviewing and defining the Stage 5 measurement/entity scope, including which evidence-backed analytes and semantics can be exposed. No unresolved protocol field may be guessed, and no production synchronization is implied by Stage 4 closure.

## Repository state at Stage 4 closure pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `50bccaaf04a54c6ec50b11c636e2ad8bca4abdde` — `fix: harden Bluetooth session failure handling`.
- **Starting tree:** clean (`git status --short` empty before this documentation closure).
- **Changes after checkpoint:** yes; documentation/status files only are changed at this pre-commit point. The task commit SHA and post-commit status are reported separately.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, and `docs/STAGE4_BLUETOOTH_TRANSPORT.md`.
- **Physical evidence provenance:** user-supplied privacy-safe result summaries; meter ON; the run date was not supplied. No address, raw frame, value, timestamp, or private identifier is recorded.
- **Live actions by Codex:** none. No physical test, deployment, push, tag, or release.

## Checks actually run

- `python3 -m unittest discover -s tests -q`: 163 tests passed.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Integration JSON and YAML parsing: passed.
- `git diff --check` and `git diff --cached --check`: passed; the complete staged documentation diff was inspected.
- Privacy/artifact scan found no private filesystem path, address, raw frame, health value, timestamp, private identifier, capture, APK/XAPK, or keystore added or tracked. The changed paths are Markdown documentation only.
