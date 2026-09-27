# Current Status — FORA 6 Connect

**Stage 5 — product measurement and entity architecture is COMPLETE for its authorized evidence-bounded scope. Stage 4 is also complete, including successful user-run physical regressions of both development actions.** Stages 0, 1, and 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open/deferred. No numeric sensor, production discovery, synchronization, or decoded real-result action exists.

## Stage 4 transport closure

[The Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes `Fora6BluetoothTransport`: Home Assistant connectable-device resolution, the two-attempt connection pattern, custom Write/Notify characteristic validation, bounded single-response exchanges, privacy-safe failures, and cancellation-aware cleanup. A failed exchange after a write attempt invalidates that session, so a delayed response cannot satisfy a later same-command request. Connector cancellation is explicitly owned and obtained clients are disconnected. The user reported that both `probe_protocol_identity` and `probe_protocol_record` succeeded on the real GD82 with the meter ON using the hardened transport; both stopped notifications and disconnected cleanly. The record action exposed no decoded measurement. `protocol_probe.py` retains the same sequences and result fields. `gatt_probe.py` and `notification_observer.py` remain prior development diagnostics.

The user-reported physical regressions confirm identity `0x22 → 0x24` with project `0x4183`, and bounded retrieval `0x22 → 0x24 → User1 0x2B → User1/index-zero 0x25 → User1/index-zero 0x26`. Both had clean notification stop and disconnect. The selected HA adapter/proxy, Auto-mode discovery, address identity/stability, unresolved protocol semantics, and production synchronization remain open.

## Stage 5 product and entity boundary

[The Stage 5 model record](docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md) documents the pure-Python `Fora6Measurement` and inert `sensor.py` mapping/state holder. The tracked Stage 2C and Stage 2G evidence supports uric-acid raw/10 scaling, but does not establish the displayed unit. Thus the product model retains the scaled number with no unit and the sensor mapper returns no numeric state. Other analytes have no numeric product output without both supported scaling and unit. Invalid `0xFFFF` is unusable; categories, transmitted status, and naive meter-local time are retained. QC and non-General categories do not enter ordinary sensor state. Stage 6 must supply stable identity before device registration; the current integration still has no config flow, SensorEntity, polling, or BLE sync path.

## Exact next gate

Stage 5 is complete for its authorized bounded model/entity scope. **Exact next gate:** separately authorize Stage 6 device discovery and identity policy, or a focused evidence follow-up to establish the uric-acid displayed unit before numeric sensor exposure. Stage 6 has not started. Do not infer a unit or begin Stage 6 automatically.

## Repository state at Stage 4 closure pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `6768ef78d268c4472f13b8245a5dc69bbed9c1c9` — `docs: record successful Stage 4 transport regression`.
- **Starting tree:** clean (`git status --short` empty before this documentation closure).
- **Changes after checkpoint:** yes; documentation/status files only are changed at this pre-commit point. The task commit SHA and post-commit status are reported separately.
- **Files changed:** `custom_components/fora6_connect/measurement.py`, `custom_components/fora6_connect/sensor.py`, `tests/test_measurement.py`, `tests/test_sensor.py`, `docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, and `docs/STAGE4_BLUETOOTH_TRANSPORT.md`.
- **Live actions by Codex:** none. No physical test, deployment, push, tag, or release.

## Checks actually run

- `python3 -m unittest discover -s tests -q`: 178 tests passed, including 15 new measurement/entity-boundary tests.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Integration JSON/YAML parsing and the changed Python 88-character line-length check: passed.
- `git diff --check`: passed. `git diff --cached --check` follows staging.
- Stage 4 transport, probe/action, protocol, combined wire-model, services, and integration entry-point files have no diff from the Stage 4 closure checkpoint.
- Audits found no guessed unit strings, QC/control-solution equivalence, BLE calls, sensor device/state class, command ID, or changes to Stage 4/action behavior. No private path, address, raw frame, health value, timestamp, identifier, or binary artifact was added; no prohibited artifact is tracked.
- The complete staged diff and `git diff --cached --check` will be inspected after staging.
