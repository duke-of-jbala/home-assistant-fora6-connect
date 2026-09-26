# FORA 6 Connect Codex Handover

## Task, checkpoint, and stage

Revise the development-only Stage 1B fresh-advertisement mechanism after the installed trailing-NUL normalization build still timed out. This document describes the dirty pre-commit state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `be7f21217fc6aecf19141d194ecd3d21e5cda3c2` — `fix: normalize FORA advertised name padding`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes, nine modified files listed below. Post-commit SHA and tree status must be checked and reported separately.
- **Stage:** Stage 1 in progress, Stage 2 unauthorized. Production automatic discovery remains Stage 6 work. No push, tag, release, or FORA application operation.

## Real evidence and interpretation

The user manually viewed the real FORA advertisement in Home Assistant's Advertisement Monitor popup; its sanitized name had five trailing NULs and it advertised Glucose and Device Information services. **That popup packet was not returned by `fora6_connect.probe_gatt`.** The installed name-normalization build then still reported `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not resolve a connectable FORA BLEDevice, connect, enumerate GATT, or transmit any FORA operation. ESPHome status=133 events around EcoFlow River 3 Plus reconnections are unrelated context, not evidence of a FORA connection failure.

[Home Assistant's current Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/) says identical advertisement callbacks are suppressed and documents `async_clear_advertisement_history(hass, address)`, which clears only advertisement deduplication state, not matcher/config-flow history. [Home Assistant core's iBeacon coordinator](https://github.com/home-assistant/core/blob/dev/homeassistant/components/ibeacon/coordinator.py) checks latest service-info timestamps when unchanged data does not generate callbacks. Reviewed 2026-09-26. Duplicate suppression is an evidence-backed **hypothesis**, not a confirmed cause of the FORA timeout. Advertisement Monitor UI visibility does not establish action callback delivery.

## Implementation and boundary

The development service retains the private runtime address. The probe reads `async_last_service_info(hass, address, connectable=False)` only as a baseline, records monotonic wait start, clears advertisement history for that address, and starts the supported 20-second targeted active wait. While it waits, it checks latest service info for a timestamp newer than both baseline and start. Either a callback result or a latest-info fallback must pass the same address, strict freshness, and normalized-name checks. A missing packet local name remains allowed only for this private-address, read-only diagnostic. The probe reports `targeted_callback_received`, `latest_service_info_advanced`, `freshness_source`, freshness, name confirmation, connectable resolution, and GATT connection status without private identifiers. Callback and latest-info paths are distinguishable. Stale service info cannot pass.

Only after freshness does Home Assistant resolve a connectable BLEDevice. The existing fresh retry-safe, no-pair client, metadata-only service/characteristic enumeration, and disconnect remain. No characteristic reads/writes, notifications, CCCDs, pairing, RACP, record retrieval, protocol parsing, sensors, or production discovery were added. The address remains in memory and is not returned, persisted, or logged by this integration. The deduplication/timestamp revision has not yet run on the real Home Assistant instance.

## Files Changed

`custom_components/fora6_connect/gatt_probe.py`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 38 tests, 0 failures, 0 skipped. Callback-after-clear, timestamp fallback, stale rejection, name normalization, privacy, and strict no-I/O tests pass.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this handover update; final rerun follows.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy/source audit — inspected changed source and documentation. An automated check found zero new MAC-formatted addresses and zero unexpected UUID-formatted identifiers; no raw capture, manufacturer payload, serial number, health measurement, or secret was added. Probe source has no characteristic read/write, notification, pairing, or RACP call; tests exercise the boundary. Runtime address is absent from integration responses, errors, and logs tested by the suite.

## Exact Next Gate

Replace `<Home Assistant config>/custom_components/fora6_connect/` with this checkout's complete `custom_components/fora6_connect/` directory, check configuration, and restart Home Assistant Core. Temporarily set Lounge to **Active** for this immediate controlled Stage 1B GATT validation. Privately enter the address from the positively identified FORA Advertisement Monitor row in **Developer Tools → Actions → `fora6_connect.probe_gatt`** during the meter's transfer window. Share only the sanitized action result or error. Record whether the callback fired, latest service-info time advanced, freshness source, normalized name confirmation, connectable resolution, connection/GATT outcome, and disconnect. Treat the UI popup separately from the action result. Auto-mode discovery remains unresolved separately; Stage 2 remains unauthorized.
