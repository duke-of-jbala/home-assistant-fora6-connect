# Current Stage

Stage 0 is complete. **Stage 1 remains in progress; Stage 2 is not authorized.** Stage 1B is a development-only Home Assistant transport/GATT probe. The real meter's connected GATT inventory was observed on iPhone, while Home Assistant-side FORA GATT connection and inventory remain unvalidated.

## Observed evidence and limits

- **User-supplied Home Assistant UI observation:** the user manually opened the `FORA 6 CONNECT` row in Advertisement Monitor. The popup marked it connectable, showed BLE flags, advertised `0x1808` Glucose and `0x180A` Device Information, showed manufacturer-specific data present, and displayed Complete Local Name `FORA 6 CONNECT` plus five trailing NULs. Custom `0x1523` was absent from that advertisement but was present with `0x1524` in the earlier connected iPhone GATT inventory. The popup packet was **not** returned by the probe.
- **Latest real Stage 1B result, user-supplied:** the installed trailing-NUL normalization build still returned `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not resolve a connectable FORA BLEDevice, attempt a FORA connection, enumerate GATT, or transmit any FORA operation. ESPHome status=133 events around EcoFlow River 3 Plus reconnections are not evidence of a FORA connection failure.
- **Platform fact reviewed 2026-09-26:** [Home Assistant's Bluetooth API](https://developers.home-assistant.io/docs/core/bluetooth/api/) suppresses identical advertisement callbacks, supports a per-address `async_clear_advertisement_history` that leaves integration matcher history intact, and exposes `async_last_service_info`. [Home Assistant's iBeacon coordinator](https://github.com/home-assistant/core/blob/dev/homeassistant/components/ibeacon/coordinator.py) checks latest service-info timestamps when unchanged advertisements do not generate callbacks. **Duplicate suppression is the next evidence-backed hypothesis, not a proven cause of the FORA timeout.** Advertisement Monitor visibility and action callback delivery are separate observations.
- **This task's change:** the development probe keeps its private runtime address field. It captures latest service info as a baseline, records monotonic wait start, clears advertisement history only for that address, and waits for a targeted callback while checking latest service-info time. Either path must show an observation newer than baseline and invocation start, with the normalized packet name matching when present. It reports callback/latest-source diagnostics without addresses. No stale cache row counts as fresh. The existing no-pair, GATT-metadata-only connection path remains gated on freshness.
- **Still unknown:** whether the revised probe receives a new FORA observation, whether duplicate suppression caused previous timeouts, whether Home Assistant can resolve a connectable FORA BLEDevice and enumerate GATT, and whether fresh Auto-mode discovery works. No Home Assistant GATT success is claimed.

## Exact Next Gate

Replace the installed development integration with this checkout's complete `custom_components/fora6_connect/` directory, check Home Assistant configuration, and restart Home Assistant Core. For this immediate controlled Stage 1B GATT validation, temporarily set the Lounge ESPHome proxy to **Active** scanning; this mode has exposed FORA in Advertisement Monitor. Privately enter the address from the identified FORA row in **Developer Tools → Actions → `fora6_connect.probe_gatt`** during the meter's transfer window. Share only the privacy-safe action result or error. Record whether the targeted callback fired, whether latest service-info time advanced, the freshness source, name confirmation, connectable resolution, connection/GATT outcome, and disconnect. Do not treat the UI popup or a stale cache entry as the action's fresh result. Keep the address and raw platform logs private. Auto-mode discovery and production discovery remain separate later work. Do not begin Stage 2.

## Repository State at Pre-Commit Review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `be7f21217fc6aecf19141d194ecd3d21e5cda3c2` — `fix: normalize FORA advertised name padding`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes. The nine files below are modified in this dirty pre-commit state. Verify and report the post-commit state separately.
- **Files changed:** `custom_components/fora6_connect/gatt_probe.py`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`.
- **Remote actions:** none; no push, tag, or release.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 38 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this status update; final rerun follows.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy/source audit — inspected changed source and documentation. An automated check found zero new MAC-formatted addresses and zero unexpected UUID-formatted identifiers; no raw capture, manufacturer payload, serial number, health measurement, or secret was added. Probe source has no characteristic read/write, notification, pairing, or RACP call; tests exercise the boundary. Runtime address is absent from integration responses, errors, and logs tested by the suite.

Updated 2026-09-26 (Europe/London), pre-commit.
