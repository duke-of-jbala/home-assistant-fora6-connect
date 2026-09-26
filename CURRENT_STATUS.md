# Current Stage

Stage 0 is complete. **Stage 1 remains in progress; Stage 2 is not authorized.** Stage 1B is a development-only Home Assistant transport/GATT probe. The real meter's connected GATT inventory was observed on iPhone, but Home Assistant-side FORA GATT connection and inventory remain unvalidated.

## Observed evidence and limits

- **User-supplied Home Assistant UI observation:** the user manually opened a `FORA 6 CONNECT` row in Advertisement Monitor. The popup marked it connectable, showed BLE flags, advertised `0x1808` Glucose and `0x180A` Device Information, showed manufacturer-specific data present, and displayed Complete Local Name `FORA 6 CONNECT` plus five trailing NULs. Custom `0x1523` was absent from that advertisement but present with `0x1524` in an earlier connected iPhone GATT inventory. The popup packet was **not** returned by the development action.
- **Latest real Stage 1B result, user-supplied:** the deduplication/timestamp revision was installed and still returned `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not resolve a connectable FORA BLEDevice, attempt connection, enumerate GATT, or transmit any FORA operation. Advertisement Monitor has independently shown FORA while Lounge was manually Active. UI visibility and action callback delivery remain separate; the timeout cause is unresolved. No meter/proxy GATT failure can be inferred.
- **This task's change:** the development action keeps the private runtime address. It now asks Home Assistant for a connectable BLEDevice immediately, without a callback, timestamp, or deduplication-history gate. If unavailable, it returns Home Assistant's outgoing-connection reachability explanation with private identifiers redacted. Optional last service info supplies a NUL-normalized name diagnostic only. After resolution, the existing fresh, no-pair retry-safe client enumerates service/characteristic metadata and disconnects. It performs no characteristic I/O. This direct-connect revision has **not** run on the real device.
- **Still unknown:** whether Home Assistant can resolve/connect to FORA and enumerate its GATT inventory, which eligible adapter/proxy it selects, why the earlier targeted waits timed out, and whether fresh Auto-mode discovery works. Production discovery remains Stage 6 work.

## Exact Next Gate

Install this checkout's complete `custom_components/fora6_connect/` directory in Home Assistant, check configuration, and restart Home Assistant Core. Temporarily set Lounge to **Active**. Make the meter advertise and confirm its `FORA 6 CONNECT` Advertisement Monitor row is visibly current/refreshing. Privately enter that identified row's address in **Developer Tools → Actions → `fora6_connect.probe_gatt`** during the transfer window. Share only the privacy-safe result/error: connectable resolution or sanitized reachability, connection outcome, actual GATT inventory/comparison, and disconnect. Keep addresses and raw logs private. Return Lounge to its usual mode afterward. Auto-mode and production discovery remain later work. Do not begin Stage 2.

## Repository State at Pre-Commit Review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `18b40e6a03b64a3eba1556b41234162f9d91a80c` — `fix: handle duplicate FORA advertisements in GATT probe`.
- **Starting tree:** clean at the checkpoint.
- **Changes after checkpoint:** yes; this is the dirty pre-commit state. Verify and report the post-commit state separately.
- **Files changed:** `custom_components/fora6_connect/gatt_probe.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `tests/test_gatt_probe.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`.
- **Remote actions:** none; no push, tag, or release.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 25 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this status update; final rerun follows.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Privacy/source audit — added lines contain only a synthetic MAC/UUID in tests and the documented public FORA UUIDs. No real address, raw advertisement, manufacturer payload, serial number, health measurement, or secret was found. Probe source contains no characteristic read/write, notification, pairing, or RACP call. Tests assert that the synthetic runtime address is absent from responses, errors, and integration DEBUG logs.

Updated 2026-09-26 (Europe/London), pre-commit.
