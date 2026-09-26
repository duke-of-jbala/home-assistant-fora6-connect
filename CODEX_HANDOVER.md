# FORA 6 Connect Codex Handover

## Task and Observed State

Add a private runtime address field to the authorized development-only Stage 1B GATT probe after a real cache-miss retest. This handover describes the dirty pre-commit state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `f98cc0cc26330ec8fd6852e7581e4749a482031e` — `fix: separate FORA discovery from connectable resolution`.
- **Starting tree:** clean (`git status --short --branch` showed `## main`).
- **Changes after checkpoint:** yes, the 14 files below. Check/report the new full commit SHA and final tree status after committing.
- **Stage:** Stage 1 in progress; Stage 2 unauthorized. No push, tag, release, or FORA application operation.

## Real Evidence and Interpretation

The latest user-supplied Home Assistant result was `No known FORA 6 CONNECT candidate is available for targeted active scanning; first observe it in Home Assistant Bluetooth (general discoveries: 214; name matches: 0; connectable scanners: 2).` The meter had previously appeared in Advertisement Monitor, but Home Assistant's current general cache held no exact-name candidate when the action ran. Home Assistant Bluetooth was operational and two connectable scanners were available. The meter advertises intermittently with a short transfer window. This result stopped before the targeted wait, HA GATT connection, or any FORA operation. It does not indicate meter, proxy, or GATT failure. Prior iPhone GATT evidence and Lounge Active-mode advertisement observation remain separate facts.

[Home Assistant Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/) states that `async_discovered_service_info` contains devices still present in cache and documents an address-targeted `async_process_advertisements` active wait. [Service-action guidance](https://developers.home-assistant.io/docs/dev_101_services/) documents UI fields and selectors. Reviewed 2026-09-26. These sources support this development design but do not validate the real HA path.

## Implementation and Boundary

`fora6_connect.probe_gatt` now requires an `address` action field. The user privately copies it from the Advertisement Monitor row already positively identified as `FORA 6 CONNECT`. The handler validates a nonempty string with a sanitized error and passes it only in memory to the probe. No config entry, storage, response, or integration log includes it. The action UI and English translation explain the private use and contain no real address example.

The probe does not consult discovery caches. It starts a 20-second `async_process_advertisements` wait for the supplied runtime address with `connectable=False` and `BluetoothScanningMode.ACTIVE`; Lounge remains in Auto. The predicate rejects replayed cache history by requiring an observation newer than wait start. A present packet local name must be `FORA 6 CONNECT`; if absent, read-only GATT inspection may proceed because the user selected the known monitor row. The response reports the actual packet local name (or `null`) and `advertised_name_confirmed`. Only after a live packet does HA resolve a connectable `BLEDevice`, create a fresh retry-safe no-pair client, enumerate service/characteristic UUIDs and properties, compare them with the prior iPhone GATT metadata (especially 1523/1524), and attempt disconnect in `finally`.

No characteristic reads/writes, notifications, CCCDs, pairing, RACP, record retrieval, protocol parsing, sensors, or production discovery were added. Production automatic discovery is deferred to Stage 6. The manual-address revision has not been run on the real system; HA-side GATT success remains unknown.

## Files Changed

`custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/gatt_probe.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/PROTOCOL.md`, `CHANGELOG.md`, `README.md`, `ROADMAP.md`.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 26 tests, 0 failures, 0 skipped. Tests mock the active wait, name checks, connectable resolution, connection/GATT/disconnect failures, service field, privacy-safe result/logs, no persistence, and forbidden operations.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass; final pre-commit rerun follows this handover update.
- Ruff — not installed (`command -v ruff` returned no path); not run.
- Service metadata — `services.yaml` parsed with PyYAML; `translations/en.json` parsed with `python3 -m json.tool`.
- Privacy/source audit — inspected changed source, tests, and documentation; no real Bluetooth address, CoreBluetooth identifier, serial number, health measurement, raw capture, or secret added. Changed lines contain no MAC-formatted address or private 128-bit identifier. Probe source contains no characteristic read/write, notification, or pairing calls; tests exercise this boundary. No real address or capture was supplied to this task.

## Exact Next Gate

Replace `<Home Assistant config>/custom_components/fora6_connect/` with this checkout's entire `custom_components/fora6_connect/` directory and restart Home Assistant Core. Leave Lounge in Auto. Privately copy the address from the positively identified FORA Advertisement Monitor row. During the meter's transfer window invoke **Developer Tools → Actions → `fora6_connect.probe_gatt`**, fill **Bluetooth address (private)**, and leave target empty. Share only the sanitized response or error. Record live-advertisement result, local-name confirmation, connectable resolution, actual GATT inventory/comparison, and disconnect; check the connection path privately. Stage 1 remains open until the real result is reviewed. Stage 2 and production discovery are not authorized here.
