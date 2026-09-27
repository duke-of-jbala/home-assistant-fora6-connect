# FORA 6 Connect Codex Handover

## Stage 6B implementation checkpoint

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Last completed/checkpoint commit before task:** `1eb776647ef23f62a64f3211137abe5331103df3` — `docs: establish serial identity policy`.
- **Starting working tree:** clean, observed with `git status --short` before editing.
- **Changes after checkpoint:** yes. This is the pre-commit observation; report the Stage 6B commit SHA and final tree status after committing.
- **Files changed:** `custom_components/fora6_connect/{__init__.py,config_flow.py,discovery.py,manifest.json,sensor.py,sensor_state.py,setup_identity.py,strings.json,translations/en.json}`; `tests/{test_bluetooth.py,test_config_flow.py,test_measurement.py,test_sensor.py,test_stage6b_entity.py,test_stage6b_identity.py,test_stage6b_setup.py}`; `docs/{ARCHITECTURE.md,DECISIONS.md,DEVELOPMENT.md,PROTOCOL.md,STAGE6A_DISCOVERY_IDENTITY_POLICY.md,STAGE6A1C_SERIAL_IDENTITY_POLICY.md,STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md}`; `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`.

[Stage 6B design and limitations](docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md): manifest matcher selects likely name/`0x1808`/connectable advertisements, with exact NUL-stripped name and `0x180A` enforced in the flow. User review precedes any connection. Stage 4 transport sends only existing wake/project requests and requires `0x4183`; a separate bounded read gets validated `0x2A25`. Exact serial text becomes private ConfigEntry/DeviceInfo identity. Address is a mutable locator, updated only after identity confirmation and a second review when no conflicting current locator is found. One uric-acid entity registers unavailable with mg/dL and no sync/polling. Population serial uniqueness, address rotation, Auto-mode discovery, and exact proxy path remain unresolved. No physical Stage 6B test was performed.

## Checks actually run

- Full unit suite: **239 passed**.
- `python3 -m compileall -q custom_components tests`: passed.
- `python3 -m tabnanny custom_components tests`: passed.
- Integration JSON and repository YAML parsing: passed.
- `git diff --check` and `git diff --cached --check`: passed after staging.
- Staged privacy/artifact audit of 29 files: no private path, MAC-shaped address, APK/XAPK, capture, keystore, or raw private result. Synthetic serials/locators only in tests.
- Command/logging audit: new flow and entity modules have no raw logging, pairing, record command, record loop, or extra request constructor. `bluetooth.py`, `protocol_probe.py`, `services.yaml`, `protocol.py`, `models.py`, and `measurement.py` are unchanged from the checkpoint. Pure model/protocol files have no HA/Bleak/ESPHome imports.
- Home Assistant runtime is not installed in the local test environment; Config Flow and SensorEntity tests use synthetic HA mocks. Real discovery/setup behavior remains a separate controlled validation.

**Exact next gate:** separately authorize a controlled real Stage 6B Home Assistant Bluetooth discovery/setup test with the meter ON; verify one reviewed setup, one generic device/unavailable uric-acid entity, and duplicate abort while keeping serial/address private. Stage 7 sync, record traversal, deduplication, and polling require a separate authorization and evidence gate.
