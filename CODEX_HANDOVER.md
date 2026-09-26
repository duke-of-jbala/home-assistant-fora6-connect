# FORA 6 Connect Codex Handover

## Task and Repository State

Fix the authorized Stage 1B development probe's discovery/freshness gate after real user attempts failed there. This is the observed pre-commit state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `04847ea6971e5dfb53ee24523e0d0e5195698f22` — `feat: add development GATT discovery probe`.
- **Starting tree:** clean (`git status --short --branch` showed `## main`).
- **Changes after checkpoint:** yes, the 11 files below; tree dirty at pre-commit review. Check/report the new full SHA and final tree state after committing.
- **Stage:** Stage 1 in progress; Stage 2 unauthorized. No push, tag, release, or FORA application operation.

## Real Evidence, Cause Boundary, and Revision

User-supplied real HA result: multiple calls to the installed first probe failed with `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` No Home Assistant GATT connection was attempted and no FORA operation was transmitted. Prior iPhone connectability/GATT and Lounge Active-mode HA advertisement observations remain valid. The probe failure alone does not diagnose meter or proxy GATT; EcoFlow activity and unrelated ESPHome API warnings are not FORA evidence.

The first callback/replay-disabled/history-clear/broad-scan discovery path was too brittle for this development probe. The revision reads Home Assistant's current connectable discoveries, identifies one exact `FORA 6 CONNECT` candidate, and keeps its address only in memory. It calls `bluetooth.async_process_advertisements(hass, predicate, {"address": runtime_address, "connectable": True}, BluetoothScanningMode.ACTIVE, 20)` while Lounge remains in Auto. The predicate checks address, exact name, and an observation time newer than both the cached candidate and wait start; the time check prevents callback-history replay from counting as a fresh packet. No cached candidate produces a separate sanitized diagnostic. A timeout does not proceed to connection.

Only after a newer packet does the unchanged transport path resolve a connectable `BLEDevice`, create a fresh retry-safe Bleak client with `pair=False` and a 20-second timeout, enumerate GATT UUIDs/properties, compare metadata with iPhone evidence, and attempt disconnect in `finally`. Phase DEBUG messages and service errors contain no address. The response remains privacy-safe. No reads, writes, notifications, pairing, RACP, records, parser, sensors, or production discovery/config flow were added.

Official sources reviewed 2026-09-26: [Home Assistant Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/) for targeted active scheduling, [API source](https://github.com/home-assistant/core/blob/dev/homeassistant/components/bluetooth/api.py) for the signature and timeout, and [manager source](https://github.com/home-assistant/core/blob/dev/homeassistant/components/bluetooth/manager.py) for possible cached replay, and [habluetooth service-info source](https://github.com/Bluetooth-Devices/habluetooth/blob/main/src/habluetooth/models.py) for the monotonic observation time. These support the design; they do not prove the user's HA installation will discover or connect.

## Files Changed

`custom_components/fora6_connect/gatt_probe.py`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/PROTOCOL.md`, `CHANGELOG.md`, `README.md`, `ROADMAP.md`.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 23 tests, 0 failures, 0 skipped. Includes targeted fresh discovery, timeout, absent candidate, wrong name/replay rejection, missing connectable device, connection/slot/GATT errors, clean disconnect after exceptions, privacy-safe result/error text, and forbidden I/O assertions.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass after code and documentation edits; rerun immediately before commit.
- `command -v ruff` — unavailable, so Ruff not run.
- Privacy/source audit — 11 changed paths; added lines contain no MAC-like address, non-GATT UUID-like identifier, or secret assignment. No raw capture, serial value, or health measurement was added. Test addresses are non-Bluetooth placeholders. No real device test of the revision was run in this checkout.

## Exact Next Gate

Replace the installed `<Home Assistant config>/custom_components/fora6_connect/` directory with this checkout's entire `custom_components/fora6_connect/` directory, then restart Home Assistant Core. Leave Lounge in Auto, make the meter advertise normally, and invoke **Developer Tools → Actions → `fora6_connect.probe_gatt`** with no target/data. A previously observed HA candidate is required for its runtime address. Share only the sanitized response or error; keep private addresses, raw logs, serials, and health measurements out of Git. If the wait succeeds, review actual connectability, GATT inventory, disconnect, and selected HA connection path privately. Keep Stage 1 in progress until the real result is reviewed. Stage 2 remains unauthorized.
