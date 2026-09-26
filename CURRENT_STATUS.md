# Current Stage

Stage 0 is complete. **Stage 1 remains in progress; Stage 2 is not authorized.** Stage 1B is a development-only Home Assistant transport/GATT probe. The real meter's GATT inventory was independently observed on iPhone, but Home Assistant-side GATT connection and inventory remain unvalidated.

## Observed evidence and limits

- **User-supplied Home Assistant UI observation:** the user manually opened the `FORA 6 CONNECT` row in **Settings → Connectivity → Bluetooth → Advertisement Monitor**. Its detail popup marked the device connectable, showed BLE flags, advertised `0x1808` Glucose and `0x180A` Device Information, showed manufacturer-specific data present, and displayed Complete Local Name `FORA 6 CONNECT` followed by **five trailing NUL characters**. The custom `0x1523` service was absent from this observed advertisement. The earlier connected iPhone GATT inventory did contain custom `0x1523` / `0x1524`. Advertised services are not the complete connected GATT inventory.
- **Separate real action result:** `fora6_connect.probe_gatt` did **not** return the popup's packet. Its latest reported error was `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` No Home Assistant GATT connection or FORA operation followed. The popup proves a trailing-NUL name-comparison defect, but it does not prove that the action's wait callback received that packet. A separate advertisement-wait/API-path issue remains possible.
- **Earlier real cache result:** `general discoveries: 214; name matches: 0; connectable scanners: 2`. The intermittent meter was absent by name from the current cache in that run. This did not establish a meter, proxy, or GATT failure.
- **This task's change:** `normalize_local_name(str | None)` removes only trailing NUL characters. The manual-address targeted predicate and privacy-safe `local_name` response use it through the shared packet-name accessor. There is no current general/cached candidate lookup; the same accessor is tested against a general-discovery service-info shape. The private address field and read-only GATT boundary remain.
- **Still unknown:** whether the corrected targeted wait receives a live packet through Lounge in Auto, whether any remaining wait/API-path issue exists, whether a connectable BLEDevice resolves, and whether Home Assistant can connect and enumerate GATT. No probe success is claimed.

## Exact Next Gate

Replace the installed development integration with this checkout's complete `custom_components/fora6_connect/` directory, check the Home Assistant configuration, and restart Home Assistant Core. Leave Lounge in Auto. Privately enter the address from the previously identified FORA Advertisement Monitor row in **Developer Tools → Actions → `fora6_connect.probe_gatt`** during the meter's transfer window. Do not share the address or raw logs. Report only the sanitized action result/error, clearly separate from Advertisement Monitor observations. Determine whether the action actually receives a new packet after this normalization fix. If it still times out, investigate the active-wait/API path within Stage 1B. Proceed to connectable resolution and read-only GATT inventory only if the fresh packet gate succeeds. Production automatic discovery remains Stage 6 work; do not begin Stage 2.

## Repository State at Pre-Commit Review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `9178e0fd88de5e82d5d2937503796c3a7a711a40` — `fix: allow private address for Stage 1B probe`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes. The files below are modified in this dirty pre-commit state. Verify and report the post-commit state separately.
- **Files changed:** `custom_components/fora6_connect/gatt_probe.py`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`.
- **Remote actions:** none; no push, tag, or release.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 31 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this status update; rerun after the final handover edit and before commit.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy audit — inspected added code, tests, and documentation. No real Bluetooth/scanner address, raw packet, manufacturer payload, serial number, health measurement, credential, or private UUID was added. An automated check found zero new MAC-formatted addresses and zero unexpected UUID-formatted identifiers. The probe source still has no characteristic read/write, notification, pairing, or RACP call; tests verify the boundary.

Updated 2026-09-26 (Europe/London), pre-commit.
