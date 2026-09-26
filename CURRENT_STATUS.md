# Current Stage

Stage 0 is complete. **Stage 1 — FORA 6 Connect BLE discovery remains in progress; Stage 2 is not authorized.** Stage 1B is a development-only transport/GATT probe. Real runs of earlier builds stopped at discovery. In the latest user-supplied retest, Home Assistant reported `general discoveries: 214; name matches: 0; connectable scanners: 2`. Home Assistant Bluetooth and two connectable scanners were operational, but the intermittently advertising meter was absent by name from the current cache. No targeted wait, Home Assistant GATT connection, or FORA operation occurred. This does not indicate a meter, proxy, or GATT failure. The manual-address revision in this task has not been run on the real system.

# Exact Next Gate

Replace the installed `<Home Assistant config>/custom_components/fora6_connect/` directory with this checkout's complete `custom_components/fora6_connect/` directory and restart Home Assistant Core. Leave Lounge in Auto. Privately copy the Bluetooth address from the Advertisement Monitor row already positively identified as `FORA 6 CONNECT`; do not put it in Git or shared messages. During the meter's Bluetooth transfer window, invoke **Developer Tools → Actions → `fora6_connect.probe_gatt`**, fill the required **Bluetooth address (private)** field, and leave target empty. Share only the privacy-safe response or sanitized error. Review whether a live packet was received, whether its local name was present and matched, connectable BLEDevice resolution, actual GATT metadata and expected comparison, and disconnect. Check the selected HA connection path privately if needed. Stage 1 remains open until a real result is reviewed; production automatic discovery remains Stage 6 work; do not begin Stage 2.

# Repository State at Pre-Commit Review

- **Date/branch:** 2026-09-26 (Europe/London), `main`.
- **Checkout:** `<local checkout>`.
- **Last completed checkpoint:** `f98cc0cc26330ec8fd6852e7581e4749a482031e` — `fix: separate FORA discovery from connectable resolution`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes, the 14 files listed below. This document describes the dirty pre-commit state; verify/report the new commit SHA and final status separately.
- **Remote actions:** none. No push, tag, or release.

# Evidence, Implementation, and Limits

- **Observed, user-supplied:** iPhone discovery/GATT inventory and earlier HA Advertisement Monitor visibility through Lounge in Active mode. The latest real action returned no known FORA candidate with 214 general discoveries, zero exact-name matches, and two connectable scanners. The meter's intermittent, short Bluetooth transfer window explains why a prior monitor row need not remain in the current cache; causation of any future live wait or GATT result remains untested. The latest run never reached targeted scanning or connection.
- **Platform fact reviewed 2026-09-26:** [Home Assistant Bluetooth APIs](https://developers.home-assistant.io/docs/core/bluetooth/api/) say `async_discovered_service_info` contains devices still present in the cache and document `async_process_advertisements` with an address-targeted active wait. [Home Assistant service-action guidance](https://developers.home-assistant.io/docs/dev_101_services/) documents fields and selectors. These describe platform behavior, not a real probe success.
- **Changed:** the development action requires a private `address` field. The handler validates it with a sanitized error, keeps it in memory, and passes it to the probe. The probe no longer consults discovery caches. It waits up to 20 seconds for a packet from that address with `connectable=False` and `BluetoothScanningMode.ACTIVE`, rejecting replay by wait-start time. A present advertised local name must match `FORA 6 CONNECT`; an absent name may proceed because the user selected the previously identified row, and the response reports `local_name: null` plus `advertised_name_confirmed: false`. Only after a live packet does HA resolve a `BLEDevice` with `connectable=True`, connect without pairing, list GATT UUIDs/properties, compare expected metadata including 1523/1524, and disconnect.
- **Boundary/privacy:** no characteristic reads/writes, notifications, CCCDs, pairing, RACP, records, protocol parsing, sensors, or production discovery. The private runtime address is not persisted, returned, or logged by this integration. No real address or health data is in tracked files.
- **Unknown:** whether the manual-address active wait sees a live packet with Lounge in Auto, whether a connectable path resolves, and whether HA can connect/enumerate GATT. No HA-side GATT success is claimed.

# Files Changed in This Task

`custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/gatt_probe.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/PROTOCOL.md`, `CHANGELOG.md`, `README.md`, `ROADMAP.md`.

# Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 26 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass; final pre-commit rerun follows this status update.
- Ruff — not installed (`command -v ruff` returned no path); not run.
- Service metadata — `services.yaml` parsed with PyYAML; `translations/en.json` parsed with `python3 -m json.tool`.
- Privacy/source audit — inspected changed source, tests, and documentation; no real Bluetooth address, CoreBluetooth identifier, serial number, health measurement, raw capture, or secret added. Changed lines contain no MAC-formatted address or private 128-bit identifier. Probe source contains no characteristic read/write, notification, or pairing calls; tests exercise this boundary.

# Last Updated

2026-09-26 (Europe/London), pre-commit review. Post-commit SHA and status belong in the final report.
