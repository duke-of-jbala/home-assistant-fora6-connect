# Current Status — FORA 6 Connect

Stages 0–5A and 6A–6A1c are complete for their authorized scopes. **Stage 6B guarded Config Flow implementation is complete and synthetic-tested; controlled physical setup validation remains pending.** Stage 4's physical identity and bounded-record regressions remain the last real transport tests. No Stage 7 synchronization, polling, record loop, or new FORA command exists.

[Stage 6B](docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md) adds a narrow Bluetooth advertisement candidate, explicit user review, the existing bounded `0x22`/`0x24` project `0x4183` confirmation, then one read-only Device Information `0x2A25` serial read. Exact validated serial text is used privately for `ConfigEntry.unique_id` and `(DOMAIN, serial)` device identity. The Bluetooth address is only a mutable, review-gated runtime locator. Duplicate and ambiguous identities fail closed. One mg/dL uric-acid entity registers unavailable until a later authorized stage supplies a measurement; it performs no BLE I/O.

## Repository observation before Stage 6B commit

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed/checkpoint commit:** `1eb776647ef23f62a64f3211137abe5331103df3` — `docs: establish serial identity policy`.
- **Starting tree:** clean; `git status --short` returned no entries before Stage 6B edits.
- **Changes after checkpoint:** yes, Stage 6B code, synthetic tests, localization, and documentation at this pre-commit observation. The task commit SHA and post-commit tree state must be reported separately.
- **Files changed:** `custom_components/fora6_connect/{__init__.py,config_flow.py,discovery.py,manifest.json,sensor.py,sensor_state.py,setup_identity.py,strings.json,translations/en.json}`; `tests/{test_bluetooth.py,test_config_flow.py,test_measurement.py,test_sensor.py,test_stage6b_entity.py,test_stage6b_identity.py,test_stage6b_setup.py}`; `docs/{ARCHITECTURE.md,DECISIONS.md,DEVELOPMENT.md,PROTOCOL.md,STAGE6A_DISCOVERY_IDENTITY_POLICY.md,STAGE6A1C_SERIAL_IDENTITY_POLICY.md,STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md}`; `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`.
- **Physical/deployment actions:** none. No push, tag, release, or Stage 7 work.

## Checks actually run

- Full unit suite: **239 passed** (`python3 -m unittest discover -s tests -q`).
- `compileall`, `tabnanny`, integration JSON and repository YAML parsing, `git diff --check`, and `git diff --cached --check`: passed after staging.
- Staged privacy/artifact scan: 29 changed files, with no private absolute path, address pattern, or prohibited binary/capture artifact.
- Stage 4 transport/probes/action schema and Stage 5/5A protocol, wire/product model files were unchanged. Pure model/protocol modules have no HA/Bleak/ESPHome import.
- No real Home Assistant Config Flow test was run; test validation uses HA mocks.

**Exact next gate:** after review, separately authorize a controlled real Home Assistant Stage 6B discovery/setup test with the GD82 ON, checking one candidate/confirmation, one private serial-backed device and unavailable uric-acid entity, then duplicate discovery abort without publishing identifiers or health data. Stage 7 historical synchronization requires separate authorization and evidence-backed traversal/deduplication design.
