# Current Status — FORA 6 Connect

**Stage 0: complete. Stage 1: complete (1A, 1B, 1C). Stage 2: not yet authorized.** The Stage 1 evidence review is complete. Stage 1 closure does not authorize pairing, application characteristic operations, RACP, record retrieval, decoding, or FORA commands.

## Completed Stage 1 evidence

- **Stage 1A:** the real meter's `FORA 6 CONNECT` local name and connectability were observed. Home Assistant Advertisement Monitor saw it through Lounge in a controlled Active-mode test. Sanitized advertisement details include a local name with five trailing NUL bytes, advertised Glucose `0x1808` and Device Information `0x180A`, and manufacturer-data presence. Fresh Auto-mode visibility was not established.
- **Stage 1B:** Home Assistant resolved a connectable BLEDevice, connected through its Bluetooth abstraction, enumerated five GATT services, confirmed Device Information, the full expected standard Glucose structure, and FORA custom `1523`/`1524`, then disconnected cleanly. The selected scanner/proxy is unknown. No application operation occurred.
- **Stage 1C:** the first real observer failed at `2A18` subscription and aborted. The revised run attempted all three: `2A18` and `2A34` failed with sanitized `BleakError`; custom `1524` subscribed successfully and delivered zero notifications in 30 seconds. The user pressed navigation keys while `1524` was subscribed, and the display remained on the only existing uric-acid result. No new measurement was taken. Subscription cleanup and disconnect were clean. Passive navigation/display of this result did not trigger a custom notification in that window. **Only uric acid has been measured on this physical meter**; no behavior is inferred for other analytes.

The Bluetooth SIG Glucose Profile specifies bonding/security for the standard Glucose path. The earlier iPhone connection was observed as bonded, but whether missing bonding/encryption caused the GD82's standard subscription failures is unknown; proxy/descriptor failure is also possible. It is unknown whether the GD82 enforces that security in the tested Home Assistant/ESPHome path, whether later RACP operations require pairing, or whether custom `1524` operations require pairing. An application request to emit stored data is a hypothesis, not an observed requirement. Pairing remains unauthorized.

## Explicitly deferred Stage 1 unknowns

| Unresolved question | Assigned gate |
| --- | --- |
| Fresh Auto-mode advertisement behavior | Stage 6 production Config Flow / Bluetooth discovery validation. Auto is not known to be broken. |
| Bluetooth address stability, randomization, and identity behavior | Stage 6 production discovery and duplicate-device handling. No stability claim is established. |
| Exact Home Assistant scanner/ESPHome proxy selected for successful GATT connections | Stage 9 end-to-end ESPHome Bluetooth Proxy validation. |
| Manufacturer-data meaning | Remains unknown; revisit in Stage 6 if useful for identification, or earlier only if later protocol evidence establishes relevance. |

These open questions **do not block Stage 1 closure** and are not treated as resolved.

## Exact next gate

**Explicit authorization of Stage 2 — protocol acquisition / reverse engineering.** Stage 1 evidence has been reviewed, satisfying the first Stage 2 entry condition; explicit Stage 2 authorization has not been given. Do not begin Stage 2, pairing, or any BLE operation under this documentation task.

## Repository state at pre-commit review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `592b4195a3d527cdee03730288761f483b3be78d` — `docs: record completed Stage 1C observation`.
- **Starting tree:** clean (`git status --short` was empty).
- **Changes after checkpoint:** yes; documentation-only dirty pre-commit state. Verify/report post-commit SHA and status separately.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md`, `docs/STAGE1_OBSERVATION_TEMPLATE.md`.
- **Remote/BLE actions:** none; no push, tag, release, or BLE operation from this repository task.

## Checks actually run

- `python3 -m unittest discover -s tests -v` — pass, 44 tests, 0 failures.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass; final rerun follows.
- Ruff unavailable (`command -v ruff` returned no path); not run. Tracked-Markdown audit found no current Stage 1 in-progress or pending Stage 1C wording; historical failed-probe sections remain identified as earlier observations. Privacy diff audit found no private address, raw payload, serial number, health value, or secret.

Updated 2026-09-26 (Europe/London), pre-commit.
