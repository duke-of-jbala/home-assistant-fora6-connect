# Current Stage

Stage 0 is complete. **Stage 1 — FORA 6 Connect BLE discovery remains in progress.** Stage 1B was explicitly authorized. A minimal development-only Home Assistant GATT probe is implemented and passes hardware-free tests, but it has **not** been run against the real meter through Home Assistant. The user-supplied iPhone GATT inventory and Home Assistant Active-mode Lounge advertisement remain the latest real-device observations. A fresh Auto-mode advertisement, Home Assistant connection/GATT, and clean disconnect have not been observed. Stage 2 is not authorized.

# Exact Next Gate

Install/load this development build in the user's Home Assistant instance and run `fora6_connect.probe_gatt` once with the Lounge ESPHome proxy left in Auto. Review a privacy-safe response or sanitized error showing whether a fresh advertisement was seen, a connectable device was resolved, a Home Assistant Bluetooth connection succeeded, actual GATT metadata was enumerated, and disconnect completed. Privately verify the selected proxy path in Home Assistant Connection Monitor if needed. Do not send FORA application writes or begin Stage 2.

# Repository State at Pre-Commit Review

- **Branch:** `main`.
- **Checkout:** `<local checkout>`.
- **Last completed checkpoint:** `6423effdd0499d6dff57c25d2da74e6d10192939` — `docs: record FORA proxy active-scan retest`.
- **Starting tree:** clean; `git status --short --branch --untracked-files=all` returned `## main`.
- **Changes after checkpoint:** yes — the files listed below. The tree is dirty at this pre-commit review; the new commit SHA and post-commit state must be reported after the commit.
- **Remote actions:** none. No push, tag, or release.

# Implemented Work

- Added a manually invoked `fora6_connect.probe_gatt` service/action during YAML integration setup, with no production Bluetooth matcher, config flow, sensor, or record retrieval.
- The probe requests an on-demand active scan through Home Assistant, requires a fresh matching callback rather than a cached row, resolves a runtime-only connectable `BLEDevice`, uses a new retry-safe Bleak client with a 20-second connection timeout and service caching disabled, enumerates service/characteristic UUIDs and properties, compares them with the prior iPhone GATT inventory, and attempts a clean disconnect in `finally`.
- The probe does not read/write characteristics, subscribe to notifications, request pairing, retrieve records, or parse FORA packets. It returns public GATT metadata without Bluetooth addresses, serial values, measurements, or credentials. It raises sanitized service errors for missing observations/paths, exhausted slots, connection or discovery failures, and incomplete disconnect.
- Added the `bluetooth_adapters` dependency so supported remote adapters/proxies load before use. The existing `bluetooth` dependency remains. No manifest discovery matcher was added.
- Added mock tests and installation/invocation instructions. The exact Home Assistant installation copy set is the entire `custom_components/fora6_connect/` directory, including `__init__.py`, `gatt_probe.py`, `const.py`, `manifest.json`, `services.yaml`, and `translations/en.json`; add `fora6_connect:` to `configuration.yaml`, check configuration, restart, and invoke the action from Developer Tools → Actions.

# Evidence and Limits

- **Observed before this task, user-supplied:** iPhone discovery and GATT inventory of the real meter; Home Assistant detected `FORA 6 CONNECT` through Lounge with scanning temporarily Active after its scan override was removed and ESPHome reflashed. The later Auto-mode monitor row did not refresh. These observations do not establish Home Assistant-side GATT success.
- **Platform sources checked 2026-09-26:** [Home Assistant Bluetooth APIs](https://developers.home-assistant.io/docs/core/bluetooth/api/) for one-shot Auto-mode active scan, connectable discovery, callback replay control, advertisement-history clearing, and BLEDevice resolution; [Home Assistant Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/) for remote adapters and connection timeout; [Home Assistant service-action guidance](https://developers.home-assistant.io/docs/dev_101_services/) for YAML setup and service registration; [bleak-retry-connector usage](https://bleak-retry-connector.readthedocs.io/en/latest/usage.html) for the current connection signature. These document platform capability, not a real probe outcome.
- **Unknown:** whether the user's Home Assistant Core version supports every used API, whether a fresh Auto-mode scan detects the meter, whether HA can connect/GATT through its selected path, whether bonding is required, and FORA application protocol semantics. No private meter address was supplied to or stored by this task.

# Files Changed in This Task

- **Added:** `custom_components/fora6_connect/gatt_probe.py`, `custom_components/fora6_connect/services.yaml`, `tests/test_gatt_probe.py`.
- **Modified:** `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/manifest.json`, `custom_components/fora6_connect/translations/en.json`, `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`.
- **Deleted/renamed:** none. `protocol.py` remains unchanged and Home Assistant independent.

# Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass: 20 tests, 0 failures, 0 skipped. New tests mock Bluetooth/connector boundaries; no real hardware test occurred.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `python3 -m json.tool custom_components/fora6_connect/manifest.json` — pass.
- `python3 -m json.tool custom_components/fora6_connect/translations/en.json` — pass.
- PyYAML parse of `custom_components/fora6_connect/services.yaml` — pass: `probe_gatt` action metadata loaded.
- `git diff --check` — pass.
- `command -v ruff` — Ruff unavailable; no Ruff result claimed.
- Source/privacy audit — 15 changed files, no private MAC/CoreBluetooth UUID, serial number, health measurement, raw capture, credential, secret, or trailing whitespace added; no characteristic write, notification, or pairing call in the probe.

# Last Updated

2026-09-26 (Europe/London), at implementation pre-commit review. Verify/report the post-commit tree state separately.
