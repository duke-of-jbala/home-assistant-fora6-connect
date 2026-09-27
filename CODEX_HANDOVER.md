# FORA 6 Connect Codex Handover

## Pre-GitHub device metadata checkpoint

The Stage 6B sensor now puts exact confirmed `0x2A25` text into `DeviceInfo.serial_number`, intentionally visible on the authenticated local Home Assistant device page. The same text remains ConfigEntry unique ID and `(DOMAIN, serial)` identifier. Home Assistant's supported `CONNECTION_BLUETOOTH` type carries the current runtime address as entity registration connection metadata. The address does not become a ConfigEntry unique ID or DeviceInfo identifier, and no IP is assigned to this BLE meter. Name, manufacturer, and model remain `FORA 6 Connect`, `ForaCare`, and `GD82`; `model_id` is omitted because it would duplicate `GD82`. The connection tuple is a registration snapshot; automatic removal of stale registry connections after a confirmed address change remains unresolved. No physical metadata validation was run by Codex.

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Last completed/checkpoint commit before task:** `c095475018c1042b85cea284c11af6d2cfd33cc9` — `chore: add temporary integration branding`.
- **Starting working tree:** clean, verified before edits.
- **Changes after checkpoint:** yes, focused device metadata, synthetic tests, and documentation at this pre-commit observation.
- **Files changed:** `custom_components/fora6_connect/sensor.py`, `tests/test_stage6b_entity.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md`.
- **Stage boundary:** no Config Flow, transport, development action, protocol, measurement, command, or synchronization change. Serial/address remain absent from integration logs, diagnostics, action results, and public examples.

## Checks

- Full unit suite: **242 passed** (`python3 -m unittest discover -s tests -q`); three new synthetic tests extend entity metadata coverage.
- `python3 -m compileall -q custom_components tests`: passed.
- `python3 -m tabnanny custom_components tests`: passed.
- Four JSON and one YAML file parsed successfully.
- `git diff --check` and `git diff --cached --check`: passed after staging. Full eight-file diff reviewed; scope, deprecated-field, serial/address leakage, privacy, and artifact audits passed. The only runtime change is `sensor.py` DeviceInfo metadata; this pre-commit tree is not described as clean.

**Exact next gate:** separately authorize Stage 7B bounded development probe implementation and user-run physical validation under [the Stage 7A design](docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md). General traversal, latest ordering, deduplication, resume/persistence, and production entity updates remain deferred.
