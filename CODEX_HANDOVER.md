# FORA 6 Connect Codex Handover

## Task and Starting State

Record the user-supplied, externally screenshot-reviewed Stage 1 real-device and Home Assistant/ESPHome observations without implementing protocol behavior.

- **Branch:** `main`.
- **Last completed checkpoint:** `418c0fe0eec26c9d2ef08a877fddc823ea0d8d18` — `refactor: rename integration to FORA 6 Connect`.
- **Actual checkout path:** `<local checkout>`. The directory move recorded as pending in the prior handover has occurred.
- **Starting working tree:** clean; `git status --short --branch --untracked-files=all` showed `## main` only.
- **Pre-commit state for this task:** dirty with only the documentation changes listed below. The post-commit state is to be verified and reported outside tracked Markdown.

## Changes After Checkpoint

Updated the evidence register, capture guide, master roadmap, status, handover, README, roadmap pointer, architecture/development descriptions, repository instruction path, and changelog. No integration code, protocol parser, test, or BLE behavior changed.

**Files modified:** `AGENTS.md`, `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`.

**Files added/deleted/renamed:** none.

## Evidence and Provenance

- **Documentary claim from Stage 0 brief:** FORA documentation lists custom service `00001523-1212-efde-1523-785feabcd123` and characteristic `00001524-1212-efde-1523-785feabcd123`, Write/Notify. The underlying document was not independently inspected here.
- **User-supplied, screenshots reviewed externally:** a generic iPhone BLE scanner saw the real meter while its blue Bluetooth indicator flashed, displaying `FORA 6 CONNECT`, connectable yes, about −50 dBm at close range. It connected and reported `BONDED`. Whether bonding is required is unknown; the scanner could have initiated it. No private identifier or iPhone CoreBluetooth UUID is recorded.
- **User-supplied iPhone GATT observation:** Device Information `0x180A` with readable standard fields; Glucose `0x1808` containing `0x2A18` Notify, `0x2A34` Notify, `0x2A51` Read, `0x2A52` Write/Indicate; custom FORA `1523` service and `1524` characteristic with Write/Notify. The actual device therefore exposes the documentary custom UUIDs. No proprietary packet semantics follow from this.
- **User-supplied Home Assistant view:** Bedroom proxy `Auto (passive)`, 0/3 slots in use; Lounge proxy `Auto (passive)`, 1/3 slots in use. Lounge was temporarily changed to Active scanning. While the iPhone saw FORA, Advertisement Monitor did not; it still saw other BLE devices including EcoFlow. This is a Home Assistant visibility gap in the tested state, not evidence of meter radio failure.
- **User-supplied Lounge configuration:** official M5Stack Atom Lite ESPHome Bluetooth proxy package plus `esp32_ble_tracker` scan interval `320ms`, window `30ms`. The roughly 9.4% scan duty cycle is a possible explanation for missed advertisements, not a proven cause.
- **Not independently observed in this task:** the screenshots, private capture, Home Assistant system, meter, or proxy. No new BLE operation was run by Codex.

## Unknowns and Boundaries

Home Assistant discovery/connection/GATT through the proxy, bonding requirement, address behavior, advertisement manufacturer/service data and UUIDs, scanner-source relationship, notification behavior, and FORA application protocol remain unknown. Stage 1 remains in progress; Stage 2 is not authorized. No BLE write, protocol implementation, push, tag, or release was performed.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 5 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `command -v ruff` — Ruff unavailable; no Ruff check claimed.
- `git diff --check` — pass.
- Documentation and privacy audit — no private MAC address, CoreBluetooth UUID, serial number, health measurement, raw capture, or secret included. The listed public GATT UUIDs are service/characteristic identifiers, not private device identifiers.

## Exact Next Gate

Correct/test Lounge ESPHome BLE scan timing in a controlled A/B test, repeat Home Assistant Advertisement Monitor observation, and determine whether Home Assistant can discover `FORA 6 CONNECT` through the proxy. Only after Home Assistant discovery and separate authorization, validate Home Assistant-side connectability/GATT. No application-level FORA writes yet.

## Last Updated

2026-09-26 (Europe/London), at this documentation task's pre-commit review. Verify and report the new commit SHA and final working-tree state after committing.
