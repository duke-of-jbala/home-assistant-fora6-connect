# Current Stage

Stage 0 is complete. **Stage 1 — FORA 6 Connect BLE discovery remains in progress; Stage 2 is not authorized.** Stage 1B remains a development-only transport/GATT probe. The first real build repeatedly failed at fresh-advertisement discovery. The installed targeted-wait build then returned `No known FORA 6 CONNECT candidate is available for targeted active scanning; first observe it in Home Assistant Bluetooth.` This occurred despite a previous Home Assistant Advertisement Monitor observation. The second build stopped before its targeted wait; neither build reached a Home Assistant GATT connection or transmitted a FORA operation. The general-discovery revision in this task has not been run on the real system.

# Exact Next Gate

Replace the installed `<Home Assistant config>/custom_components/fora6_connect/` directory with this checkout's complete `custom_components/fora6_connect/` directory and restart Home Assistant Core. Leave Lounge in Auto, make the meter advertise normally, then invoke **Developer Tools → Actions → `fora6_connect.probe_gatt`** with no target or data. Share only the privacy-safe response or sanitized error. Record general discovery and matching-name counts, whether the targeted wait received a newer packet, connectable BLEDevice resolution, actual GATT inventory, and disconnect outcome. Check the selected adapter/proxy privately if connected. A prior Advertisement Monitor row does not prove current cache presence. Keep Stage 1 open pending this real result; do not start Stage 2.

# Repository State at Pre-Commit Review

- **Date/branch:** 2026-09-26 (Europe/London), `main`.
- **Checkout:** `<local checkout>`.
- **Last completed checkpoint:** `918d3c349599168de3ace331e2d53978399409c7` — `fix: use targeted active scan for GATT probe`.
- **Starting tree:** clean; `git status --short --branch` returned `## main`.
- **Changes after checkpoint:** yes, the 11 files listed below. This is the dirty pre-commit state; verify/report the new SHA and post-commit status separately.
- **Remote actions:** none. No push, tag, or release.

# Evidence, Implementation, and Limits

- **Observed, user-supplied:** the real meter was previously detected by an iPhone scanner and its GATT inventory viewed there; Home Assistant Advertisement Monitor detected it through Lounge with scanning temporarily Active after the ESPHome retest. The first HA probe failed at the fresh-advertisement gate. The installed targeted-wait build then failed at the connectable-only cached-candidate gate. No targeted wait, GATT connection, or FORA operation occurred in that second run. These results do not establish a meter or proxy GATT failure.
- **Platform sources reviewed 2026-09-26:** [Home Assistant Bluetooth APIs](https://developers.home-assistant.io/docs/core/bluetooth/api/) distinguish discovery and connectable BLEDevice resolution; [habluetooth manager](https://github.com/Bluetooth-Devices/habluetooth/blob/main/src/habluetooth/manager.py) uses general/all history for `connectable=False`; [Home Assistant's callback manager](https://github.com/home-assistant/core/blob/dev/homeassistant/components/bluetooth/manager.py) defaults an omitted matcher flag to connectable-only; [BluetoothServiceInfoBleak](https://github.com/Bluetooth-Devices/habluetooth/blob/main/src/habluetooth/models.py) carries both advertisement local name and resolved service-info name. These establish API behavior, not a real probe success.
- **Changed:** candidate lookup reads general HA discoveries with `connectable=False` and prefers advertisement `local_name` before `service_info.name`. The address remains in memory. A privacy-safe DEBUG summary reports general discovery count, matching-name count, and connectable scanner count. The targeted active wait explicitly matches `connectable=False` so it can receive advertisements from general history; its predicate still requires the runtime address, correct name, and an observation newer than both cached and wait-start times. Only after a fresh packet does the probe resolve a `BLEDevice` with `connectable=True` for GATT.
- **Unchanged boundary:** the existing retry-safe client, service/characteristic metadata enumeration, and `finally` disconnect path remain. No characteristic read/write, notification, pairing, RACP, record retrieval, protocol parsing, production matcher, or sensor was added. Public results, errors, and probe DEBUG logs contain no address or health data.
- **Unknown:** whether the revised general lookup currently finds the meter, whether the targeted wait sees a live packet with Lounge in Auto, whether a connectable path resolves, and whether HA can connect/enumerate GATT. No HA-side GATT success is claimed.

# Files Changed in This Task

`custom_components/fora6_connect/gatt_probe.py`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/PROTOCOL.md`, `CHANGELOG.md`, `README.md`, `ROADMAP.md`.

# Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 25 tests, 0 failures, 0 skipped, including an explicit general-only candidate test.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass after code and documentation edits; rerun immediately before commit.
- `command -v ruff` — unavailable; Ruff not run.
- Privacy/source audit — 11 changed paths; added lines contain no MAC-like address, private UUID-like identifier, or secret assignment. No serial value, health measurement, raw capture, or FORA protocol operation was added. Test addresses are non-Bluetooth placeholders.

# Last Updated

2026-09-26 (Europe/London), pre-commit review. Report the post-commit state separately.
