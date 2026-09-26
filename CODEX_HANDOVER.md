# FORA 6 Codex Handover

## Task

Stage 1A — prepare passive FORA 6 Bluetooth discovery through Home Assistant and the existing M5Stack Atom Lite ESPHome proxy. Stage 1 is in progress; this task prepares capture and records platform guidance without observing the user's meter.

## Starting State

- **Branch:** `main`.
- **Starting checkpoint:** `cfd3704c3e82c1ff091b0388780614b4fb8571ef` — `docs: add durable Codex handover workflow`.
- **Working tree:** clean at task start (`git status --short --branch --untracked-files=all` showed `## main` only).

## Work Performed

- Reviewed the existing capture guide and current official Home Assistant and ESPHome documentation.
- Prepared Home Assistant Adapters, Advertisement Monitor, and Connection Monitor observation instructions with fields for the Atom Lite proxy and two candidate advertisements.
- Added a blank template for private use; completed copies and raw logs must stay outside Git.
- Documented the gated Stage 1B method using Home Assistant Bluetooth APIs for observational GATT inspection; no probe was implemented.
- Set Stage 1 to in progress and Stage 1A preparation to complete in the master roadmap and current status; aligned the README, architecture, and development wording. Stage 2 remains unauthorized.

## Files Added

- `docs/STAGE1_OBSERVATION_TEMPLATE.md`

## Files Modified

- `docs/CAPTURE_GUIDE.md`
- `FORA6_MASTER_ROADMAP.md`
- `ROADMAP.md`
- `CURRENT_STATUS.md`
- `CODEX_HANDOVER.md`
- `CHANGELOG.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/DEVELOPMENT.md`

## Files Deleted

None.

## Technical Decisions

- Stage 1A starts with Home Assistant's built-in Bluetooth views; a field not displayed by the UI is recorded as “not shown”, not assumed absent from the advertisement.
- The Atom Lite's advertisement and active/GATT capabilities must be observed in the user's installation, not inferred from the hardware model or ESPHome defaults. Actual scanning mode is recorded separately from active GATT capability.
- Stage 1B remains a documented, separately authorized method. No direct local BlueZ interface, hard-coded proxy, discovery matcher, sensor, or application-protocol code was added.

## Evidence / Findings

- **Official platform documentation checked 2026-09-26:** Home Assistant describes Settings → Connectivity → Bluetooth with Adapters, Advertisement Monitor, and Connection Monitor; its Bluetooth APIs support discovered/last service information, connectable device resolution, and reachability diagnostics. ESPHome describes Bluetooth proxy advertisement forwarding, active GATT connections, and connection slots. Exact source URLs are in `docs/CAPTURE_GUIDE.md`.
- **Documentary FORA facts from the Stage 0 brief:** service UUID `00001523-1212-efde-1523-785feabcd123`, characteristic UUID `00001524-1212-efde-1523-785feabcd123`, documented write/notify properties. These have not been verified on the real meter.
- **Real-device observation:** none supplied or performed. The actual proxy configuration, advertisement, address behavior, GATT inventory, and notifications remain unknown. No application command was transmitted and no protocol behavior was inferred.

## Commands / Checks Run

- `git status --short --branch --untracked-files=all`, `git rev-parse HEAD`, `git log -1 --format='%s'`, `git remote -v` — confirmed the clean starting checkpoint.
- `python3 -m unittest discover -s tests -v` — pass, five tests.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- File/privacy and staged-diff review — only the ten intended documentation files are included; no generated cache or private capture is committed.

## Tests

- **Total:** 5
- **Passed:** 5
- **Failed:** 0
- **Skipped:** 0
- **Unavailable tooling:** Ruff is not installed; not run.

## Git State

- **Branch:** `main`
- **Last completed checkpoint SHA:** `cfd3704c3e82c1ff091b0388780614b4fb8571ef`
- **Checkpoint message:** `docs: add durable Codex handover workflow`
- **Changes after checkpoint:** yes — the ten documentation files listed above. At pre-commit review, those were the only task changes. This task's exact commit SHA and final `git status --short` are reported after commit, outside tracked Markdown.
- **Pushed:** no.
- **Tagged:** no.
- **Released:** no.

## Blockers / Unknowns

No real-device advertisement has been supplied. The Atom Lite scanner state/capabilities and the FORA candidate identity cannot yet be evaluated. Stage 1B entry criteria are unmet; Stage 2 is not authorized.

## Privacy Check

No actual MAC address, private measurement, Home Assistant credential, secret/token, or raw BLE capture was added or committed. The observation template contains placeholders only; completed copies must remain private and outside Git.

## Exact Next Gate

Obtain the user's **Home Assistant Advertisement Monitor observation** and Atom Lite proxy/environment fields described in `docs/CAPTURE_GUIDE.md`; compare at least two observations and review a sanitized summary. Do not start Stage 1B before candidate review and explicit authorization.

## Authorization Boundary

No FORA application writes or protocol inference during Stage 1. Do not implement/run a Stage 1B probe, subscribe to notifications, add a discovery matcher or sensors, begin Stage 2, push, tag, or release without the relevant explicit authorization.
