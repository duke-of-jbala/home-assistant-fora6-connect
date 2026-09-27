# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stage 5 product measurement/entity architecture is COMPLETE for its authorized evidence-bounded scope. Stage 4 is complete, including user-run physical regression validation of both existing development actions. Stages 0, 1, 3, and 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open/deferred. Stage 6 has not started.

- **Branch:** `main`.
- **Last completed checkpoint:** `6768ef78d268c4472f13b8245a5dc69bbed9c1c9` — `docs: record successful Stage 4 transport regression`.
- **Starting tree:** clean, verified with `git status --short` before Stage 5 edits.
- **Changes after checkpoint:** yes; pure product mapping, inert sensor boundary, synthetic tests, and Stage 5 documentation are changed at this pre-commit point. Report the task commit SHA and post-commit status separately.
- **Physical evidence provenance:** Stage 4 regression summaries are user-supplied; meter ON; run date not supplied. This Stage 5 task performed no physical test and retains no private address, raw frame, health value, timestamp, or identifier.
- **Actions by Codex:** no live Home Assistant action or physical test. No deployment, push, tag, or release.

## Implementation and behavior

`bluetooth.py` contains `Fora6BluetoothTransport(hass, runtime_address)`. It resolves a connectable `BLEDevice` through Home Assistant, uses the repository's proven two-attempt connector pattern, validates the custom Write/Notify characteristic, subscribes, performs one command-agnostic request/response exchange at a time, and closes deterministically. It bounds connection, notification, write, response, and cleanup waits; serializes exchanges per instance; fails malformed pending notifications closed; retries no application write; and exposes stable privacy-safe error codes. A failure after any application write attempt poisons the session; later exchanges return `invalid_session_state` with no write, so delayed same-command responses cannot contaminate another exchange. Pre-write rejection does not poison. The connector task is owned through cancellation or timeout, and any returned client is disconnected, including a late client returned after the bounded cancellation wait. No raw notification queue, address logging, or hard-coded adapter path exists. [The Stage 4 record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) documents the API and limits.

`protocol_probe.py` delegates transport mechanics to this class but retains the two existing bounded command sequences, service/action names, input/result schemas, timeout settings, and privacy semantics. The user reports both real regressions succeeded with the meter ON: identity `0x22 → 0x24` and bounded record `0x22 → 0x24 → User1 0x2B → User1/index-zero 0x25 → User1/index-zero 0x26`. Both stopped notifications and disconnected cleanly. The record action returned only semantic status and no analyte, measurement, or scaling result. This closes Stage 4 transport validation; the selected HA adapter/proxy remains unknown. `gatt_probe.py` and `notification_observer.py` were not refactored. `protocol.py` and `models.py` remain HA/Bleak independent.

`measurement.py` adds a frozen pure-Python `Fora6Measurement` mapped from a validated `TD4183Record`. Only valid identified uric acid receives a raw/10 `Decimal`; the model enforces `unit=None` because the tracked Stage 2C/2G evidence does not state the display unit. Other analytes and unknown selectors have no numeric value. `sensor.py` contains a replacement state holder, a unit/category-gated value mapper, and a `(DOMAIN, Stage6StableId)` device-identifier interface. It defines no `SensorEntity`, platform setup, config entry, DeviceInfo registration, polling, or Bluetooth I/O. Invalid sentinel input replaces the latest state and maps to no numeric value. [The Stage 5 record](docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md) documents these boundaries.

## Exact next gate and checks

**Next gate:** Stage 5 is complete for the bounded product/entity architecture. Separately authorize Stage 6 device discovery and identity policy, or a focused evidence follow-up establishing the uric-acid displayed unit before numeric sensor exposure. Stage 6 has not started. Unresolved semantics, exact selected adapter/proxy, Auto-mode discovery, address stability, and production synchronization remain open.

- **Files changed at pre-commit:** `custom_components/fora6_connect/measurement.py`, `custom_components/fora6_connect/sensor.py`, `tests/test_measurement.py`, `tests/test_sensor.py`, `docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, and `docs/STAGE4_BLUETOOTH_TRANSPORT.md`.
- **Checks actually run:** 178 unit tests passed, including 15 new product/entity tests; compileall, tabnanny, integration JSON/YAML parsing, 88-character line length, and `git diff --check` passed. Stage 4 transport/probe/action and pure wire modules are unchanged from the closure checkpoint. Audits found no guessed units, QC/other clinical meaning, sensor/BLE I/O, classes, command IDs, private data, or prohibited artifacts. `git diff --cached --check` and full staged review follow staging.
