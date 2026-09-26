# FORA 6 Connect Codex Handover

## Task, checkpoint, and stage

Change the development-only Stage 1B probe to test direct Home Assistant connectable resolution and GATT after the installed deduplication/timestamp build still timed out at its advertisement wait. This document describes the dirty pre-commit state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `18b40e6a03b64a3eba1556b41234162f9d91a80c` — `fix: handle duplicate FORA advertisements in GATT probe`.
- **Starting tree:** clean at that checkpoint; changes after checkpoint: yes. Post-commit SHA and status must be checked and reported separately.
- **Files changed:** `custom_components/fora6_connect/gatt_probe.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`.
- **Stage:** Stage 1 in progress, Stage 2 unauthorized. Production automatic discovery remains Stage 6 work. No push, tag, release, or FORA application operation.

## Real evidence and interpretation

The user manually viewed the real FORA advertisement in Home Assistant's Advertisement Monitor popup. Its sanitized Complete Local Name had five trailing NULs and it advertised Glucose and Device Information services. **The popup packet was not returned by `fora6_connect.probe_gatt`.** The later installed deduplication/timestamp build still reported `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not resolve a FORA BLEDevice, connect, enumerate GATT, or transmit a FORA operation. Advertisement Monitor separately showed FORA when Lounge was manually Active. UI visibility and integration callback delivery are distinct; duplicate suppression was a plausible hypothesis, not a demonstrated cause. No proxy or meter GATT outcome has been observed.

## Implementation and boundary

The development action retains the private required runtime address from the positively identified Advertisement Monitor row. It now calls `bluetooth.async_ble_device_from_address(hass, address, connectable=True)` immediately. A missing connectable BLEDevice causes a sanitized `bluetooth.async_address_reachability_diagnostics(..., BluetoothReachabilityIntent.CONNECTION)` explanation. [Home Assistant's Bluetooth API](https://developers.home-assistant.io/docs/core/bluetooth/api/) describes that explanation as human-readable and unstable; the code redacts identifiers without parsing it. Only after successful resolution does optional `async_last_service_info(..., connectable=False)` supply a normalized name diagnostic; it is not a freshness gate. The action does not request or wait for an active scan, clear advertisement history, or require a timestamp advance.

After resolution, a fresh retry-safe, no-pair client connects with a 20-second timeout, enumerates actual GATT service/characteristic UUIDs and properties, compares expected metadata, and disconnects in `finally`. No characteristic read/write, notification, CCCD, pairing, RACP, record retrieval, protocol parser, sensor, or production discovery was added. The runtime address remains in memory and is not returned, persisted, or logged by this integration. The direct-connect revision has not run on the real Home Assistant instance.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 25 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this handover update; final rerun follows.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy/source audit — added lines contain only a synthetic MAC/UUID in tests and the public documented FORA UUIDs. No real address, raw advertisement, manufacturer payload, serial number, health measurement, or secret was found. Probe source has no characteristic read/write, notification, pairing, or RACP call. Tests check synthetic address removal from responses/errors/logs.

## Exact Next Gate

Replace `<Home Assistant config>/custom_components/fora6_connect/` with this checkout's complete `custom_components/fora6_connect/` directory, check configuration, and restart Home Assistant Core. Temporarily set Lounge to **Active**, make the meter advertise, and verify that its `FORA 6 CONNECT` Advertisement Monitor row is visibly current/refreshing. Privately enter that row's address in **Developer Tools → Actions → `fora6_connect.probe_gatt`** during the transfer window. Share only the sanitized result/error and record connectable resolution or reachability, actual connection/GATT result, and disconnect. Home Assistant chooses the connection path; check Connection Monitor privately if needed. Return Lounge to its usual mode. Auto-mode and production discovery remain later work; Stage 2 remains unauthorized.
