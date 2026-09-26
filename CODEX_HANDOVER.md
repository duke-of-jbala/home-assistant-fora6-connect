# FORA 6 Connect Codex Handover

## Task, checkpoint, and stage

This documentation-only task records the completed Stage 1 evidence review and closes Stage 1. This handover describes the dirty pre-commit repository state on 2026-09-26 (Europe/London).

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `592b4195a3d527cdee03730288761f483b3be78d` — `docs: record completed Stage 1C observation`.
- **Starting tree:** clean (`git status --short` empty).
- **Changes after checkpoint:** yes; documentation only. Files changed: `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md`, `docs/STAGE1_OBSERVATION_TEMPLATE.md`. Post-commit SHA/status must be checked and reported separately.
- **Stage state:** Stage 0 complete; Stage 1 complete (1A, 1B, 1C); Stage 2 not yet authorized. No pairing or BLE operation is authorized by this documentation task.

## Evidence and deferrals

Stage 1A established real local name/connectability, controlled Home Assistant Advertisement Monitor visibility in Active mode, and sanitized advertisement fields. Stage 1B established Home Assistant connectable-device resolution, successful connection, five-service GATT inventory including Device Information, complete standard Glucose structure, custom `1523`/`1524`, and clean disconnect without application I/O. Stage 1C established that standard `2A18`/`2A34` subscriptions failed with safe `BleakError`, custom `1524` subscribed, and zero custom notifications arrived over 30 seconds while the user navigated the only existing uric-acid result. Cleanup and disconnect were clean. Only uric acid has been measured on this physical meter. Do not generalize passive notification behavior to other analytes or infer that `1524` requires a command.

The Stage 1 review explicitly deferred fresh Auto-mode advertisement and Bluetooth address stability/randomization/identity to **Stage 6** production discovery and duplicate-device handling. The exact scanner/ESPHome proxy selected for successful GATT connections is deferred to **Stage 9** end-to-end proxy validation. Manufacturer-data meaning remains unknown; revisit in Stage 6 if useful for identification or earlier only if later protocol evidence establishes relevance. None is silently resolved, and none blocks Stage 1 closure.

The Bluetooth SIG Glucose Profile specifies bonding/security for the standard Glucose path. The earlier bonded iPhone connection does not prove why Home Assistant's standard subscriptions failed. Whether the GD82 enforces this security in the tested path, whether later RACP requires pairing, and whether custom `1524` operations require pairing all remain unknown. Proxy/descriptor failure is another possible explanation. Pairing remains unauthorized. No characteristic read/write, RACP command, record retrieval, decoding, or FORA command was implemented or performed.

## Checks actually run

- `python3 -m unittest discover -s tests -v` — pass, 44 tests, 0 failures.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass; final rerun follows.
- Ruff unavailable (`command -v ruff` returned no path); not run. Tracked-Markdown audit found no current Stage 1 in-progress or pending Stage 1C wording; historical failed-probe sections remain identified as earlier observations. Privacy diff audit found no private address, raw payload, serial number, health value, or secret.
- No BLE operation, push, tag, or release performed in this repository task.

## Exact next gate

**Explicit authorization of Stage 2 — protocol acquisition / reverse engineering.** The Stage 1 evidence-review condition is met; Stage 2 authorization is not. Stop at this gate.
