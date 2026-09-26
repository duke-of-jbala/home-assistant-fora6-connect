# FORA 6 Connect Codex Handover

## Task and Observed Repository State

Implement the explicitly authorized Stage 1B development-only Home Assistant GATT probe without FORA application operations. This handover describes the pre-commit state on 2026-09-26 (Europe/London).

- **Branch:** `main`.
- **Last completed checkpoint:** `6423effdd0499d6dff57c25d2da74e6d10192939` — `docs: record FORA proxy active-scan retest`.
- **Checkout:** `<local checkout>`.
- **Starting tree:** clean (`git status --short --branch --untracked-files=all` showed `## main`).
- **Changes after checkpoint:** yes, the files listed below. The tree is dirty at this pre-commit review. Report the new commit SHA and final tree state after committing.

## Implemented Behavior

`fora6_connect.probe_gatt` is a manually invoked, development-only Home Assistant service/action registered by `async_setup` when the integration is loaded via `configuration.yaml`. It uses supported Home Assistant Bluetooth APIs to request an on-demand active scan while proxy settings can remain Auto. A callback with replay disabled requires a new matching observation; a cached row alone cannot pass. For previously cached candidates, the probe clears only advertisement deduplication history before scanning.

After a unique fresh `FORA 6 CONNECT` observation, the probe resolves a connectable runtime `BLEDevice` through Home Assistant. It uses a new `bleak-retry-connector` client per invocation, with `pair=False`, a 20-second timeout, limited retries, and service caching disabled. It lists actual GATT service/characteristic UUIDs and properties, compares them with the prior iPhone observation, and attempts disconnect in `finally`. A lock prevents overlapping manual probes.

The JSON-compatible success response includes `device_found`, `local_name`, `active_scan_requested`, `fresh_advertisement_observed`, `connectable_device_resolved`, `connectable_scanner_count`, `connection_successful`, `connected_via_ha_bluetooth`, `gatt_service_count`, `services`, `expected_gatt`, and `disconnected_cleanly`. Counts, services, and properties must come from the real run. The response does not assert which eligible proxy Home Assistant chose; confirm that privately in Connection Monitor if needed. Failures become privacy-safe service errors.

No characteristic reads/writes, notification subscriptions, pairing request, glucose record retrieval, proprietary packet parsing, sensor, production config flow, or production discovery matcher were added. `protocol.py` remains unchanged and independent of Home Assistant.

## Real-Device Evidence and Uncertainties

The prior user-supplied iPhone GATT inventory and Home Assistant Active-mode Lounge advertisement are the latest real-device observations. The development probe has **not** been installed or run on the user's Home Assistant system. A fresh Auto-mode advertisement, Home Assistant-side connection/GATT inventory, selected connection path, and clean disconnect remain unobserved. Stage 1 remains in progress; Stage 2 is not authorized.

Official sources reviewed on 2026-09-26: [Home Assistant Bluetooth API](https://developers.home-assistant.io/docs/core/bluetooth/api/), [Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), [service actions](https://developers.home-assistant.io/docs/dev_101_services/), and [bleak-retry-connector usage](https://bleak-retry-connector.readthedocs.io/en/latest/usage.html). These support the implementation choices but do not validate the user's actual Home Assistant version or hardware path.

## Files Changed

- **Added:** `custom_components/fora6_connect/gatt_probe.py`, `custom_components/fora6_connect/services.yaml`, `tests/test_gatt_probe.py`.
- **Modified:** `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/manifest.json`, `custom_components/fora6_connect/translations/en.json`, `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`.
- **Deleted/renamed:** none.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 20 tests, 0 failures, 0 skipped. Mock tests cover scan freshness, discovery, BLEDevice resolution, service registration, connection/slot/GATT failures, cleanup, privacy-safe error text, and no write/notify/pair calls.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `python3 -m json.tool custom_components/fora6_connect/manifest.json` — pass.
- `python3 -m json.tool custom_components/fora6_connect/translations/en.json` — pass.
- PyYAML parse of `custom_components/fora6_connect/services.yaml` — pass: `probe_gatt` action metadata loaded.
- `git diff --check` — pass.
- `command -v ruff` — Ruff unavailable; no Ruff result claimed.
- Source/privacy audit — 15 changed files, no private device address, CoreBluetooth identifier, serial number, health measurement, raw capture, credential, secret, or trailing whitespace added. No real BLE probe was run by Codex.

## Installation and Exact Next Gate

Copy the **entire** `custom_components/fora6_connect/` directory into the Home Assistant configuration's `custom_components/fora6_connect/` path, including `__init__.py`, `gatt_probe.py`, `const.py`, `manifest.json`, `services.yaml`, and `translations/en.json`. Add top-level `fora6_connect:` to `configuration.yaml`, check configuration, restart Home Assistant, leave Lounge in Auto, make the meter advertise normally, then invoke **Developer Tools → Actions → `fora6_connect.probe_gatt`** with no target or data. Share only the sanitized response or error. Full steps are in `docs/DEVELOPMENT.md`.

**Exact next gate:** run that probe on the controlled real meter through Home Assistant and review fresh discovery, connectable resolution, actual GATT inventory, selected connection path (privately), and disconnect outcome. Keep Stage 1 in progress until this evidence is reviewed. Do not perform application-level writes or begin Stage 2.

## Authorization Boundary

No push, tag, release, FORA application operation, or Stage 2 work occurred. Stop at the real-probe gate after the local implementation commit.
