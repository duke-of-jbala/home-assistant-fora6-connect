# Current Stage

Stage 0 is complete. **Stage 1 remains in progress; Stage 2 is not authorized.** **Stage 1B Home Assistant transport/GATT validation succeeded** on the real FORA 6 Connect. No application protocol operation has been performed.

## Real evidence and limits

- **User-supplied, privacy-safe real Stage 1B action result:** `fora6_connect.probe_gatt` reported `device_found=true`, normalized `local_name=FORA 6 CONNECT`, `advertised_name_confirmed=true`, `last_service_info_available=true`, `connectable_device_resolved=true`, `connectable_scanner_count=2`, `gatt_connection_attempted=true`, `connection_successful=true`, `connected_via_ha_bluetooth=true`, `gatt_service_count=5`, and `disconnected_cleanly=true`. No Bluetooth address is recorded.
- **Observed Home Assistant GATT inventory:** Generic Access `0x1800`, Generic Attribute `0x1801` (no characteristics returned), Device Information `0x180A`, Glucose `0x1808`, and FORA custom `00001523-1212-efde-1523-785feabcd123`. Every previously expected Glucose characteristic/property and custom `1524` Write/Notify pair was present. The full sanitized UUID/property inventory is in `docs/PROTOCOL.md`. This independently confirms the earlier connected iPhone GATT observation. The probe enumerated metadata only; it did not read/write characteristics, subscribe, pair, retrieve records, or transmit a FORA operation.
- **Connection-path boundary:** two connectable scanners were reported, but the action response did not identify which scanner/adapter handled the connection. Home Assistant-side GATT transport is validated; a particular ESPHome proxy path is not claimed without Connection Monitor evidence.
- **Discovery boundary:** earlier targeted-advertisement callback timeouts were discovery-layer results, not evidence of meter or GATT failure. The user separately observed a FORA advertisement in Home Assistant Advertisement Monitor when Lounge was manually Active. The action did not return that popup packet. Fresh Auto-mode advertisement behavior and production automatic discovery remain unresolved separately.
- **Architecture evidence:** the meter exposes a complete standard Bluetooth Glucose Service alongside the FORA custom 1523/1524 service. Later, separately authorized protocol acquisition should consider both the Bluetooth SIG Glucose Service/RACP path for standard glucose functionality and the custom path for FORA-specific functionality. Whether non-glucose analytes use the custom path is unknown; UUIDs and properties do not establish protocol semantics.

## Exact Next Gate

Review remaining Stage 1 discovery questions and plan a controlled, privacy-safe observation of raw notification behavior. Any notification subscription or further BLE operation requires a separate explicit instruction; none is authorized by this documentation task. Keep Stage 1 open until the remaining evidence is reviewed. Auto-mode and production discovery do not invalidate the successful direct GATT result. Do not begin Stage 2.

## Repository State at Pre-Commit Review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `3d00f18e822e332f7a671bd90e69ffa29da92b3a` — `docs: record successful FORA GATT validation`.
- **Starting tree:** clean; `git status --short --branch` showed `## main`.
- **Changes after checkpoint:** yes; the six documentation files below are modified in this dirty pre-commit state. Verify and report the post-commit state separately.
- **Files changed:** `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/STAGE1_OBSERVATION_TEMPLATE.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`.
- **Code/remote actions:** no Python change, BLE operation, push, tag, or release.

## Checks Actually Run

- `python3 -m unittest discover -s tests -v` — pass, 25 tests, 0 failures, 0 skipped.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before this status update; final rerun follows.
- Ruff — unavailable (`command -v ruff` returned no path); not run.
- Tracked-Markdown audit — enumerated and searched all 13 tracked Markdown paths for stale GATT/discovery status, then reviewed the affected current-state passages. Updated the README, roadmap pointer, architecture page, and materially stale GATT heading in the blank Stage 1 template. Historical failed-probe evidence and accepted ADRs were preserved.
- Privacy audit — reviewed added lines: zero MAC- or UUID-formatted literals, and no private identifier, raw capture, measurement, or secret was added.

Updated 2026-09-26 (Europe/London), pre-commit.
