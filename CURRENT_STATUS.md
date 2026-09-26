# Current Stage

Stage 0 is complete. **Stage 1 — FORA 6 BLE discovery is in progress. Stage 1A capture preparation is complete; no real-device advertisement has been supplied or observed in this task.** Stage 1B has not begun. Stage 2 is not authorized.

# Current Gate

Obtain and review the user's Home Assistant **Advertisement Monitor** observation and M5Stack Atom Lite proxy/environment details. Do not infer identity from a name or UUID match alone.

# Repository

- **Local path:** `<former local checkout>`
- **GitHub repository:** `duke-of-jbala/home-assistant-fora6` (target; no remote repository created or contacted in this task)
- **Branch:** `main`
- **Last completed checkpoint commit SHA:** `cfd3704c3e82c1ff091b0388780614b4fb8571ef`
- **Checkpoint commit message:** `docs: add durable Codex handover workflow`
- **Remote:** local `origin` is `https://github.com/duke-of-jbala/home-assistant-fora6`
- **Changes after checkpoint:** yes — the ten documentation files listed below. At the pre-commit review, they were the only task changes. The task commit's full SHA and final `git status --short` are reported after commit, outside tracked Markdown.

# Completed Work

- Stage 0 created and locally committed the integration skeleton, architecture decisions, test baseline, and durable handover workflow.
- Stage 1A preparation updated the Home Assistant Bluetooth capture guide, added a blank private observation template, recorded the intended Stage 1B read-only GATT method, and aligned the roadmap, README, architecture, and development guidance. No Bluetooth probe, connection, or application write occurred.
- The guide cites official Home Assistant and ESPHome documentation checked on 2026-09-26, distinguishing platform capabilities from this user's unverified proxy configuration and meter behavior.

# Validated Facts

- Project target: FORA 6 Connect GD82; integration domain `fora6`; display name FORA 6. The user's proxy hardware is described as an M5Stack Atom Lite running ESPHome; its displayed configuration and capability have not yet been observed here.
- The Stage 0 brief reports FORA documentation listing service UUID `00001523-1212-efde-1523-785feabcd123`, characteristic UUID `00001524-1212-efde-1523-785feabcd123`, and write/notify properties. The underlying document and physical GATT have not been independently checked. These are documentary facts, not observed advertisements or device-identification proof.
- Official Home Assistant documentation describes Adapters, Advertisement Monitor, and Connection Monitor under Settings → Connectivity → Bluetooth and APIs for discovered service information and connectable device resolution. Official ESPHome documentation distinguishes advertisement forwarding from active GATT capability. Source URLs and access date are in `docs/CAPTURE_GUIDE.md`.

# Unvalidated / Unknown

- No candidate advertisement, local name, address behavior, manufacturer/service data, RSSI/source relationship, connectability, or actual GATT structure has been observed or supplied.
- The Atom Lite's Home Assistant scanner state, scanning mode, ESPHome version, active/GATT capability, and available connection slots are unverified for this installation.
- FORA commands/responses, framing, checksums, identity response, record layout, analytes, timestamps, flags, units, errors, and historical memory behavior are unknown. No protocol behavior was inferred.

# Tests and Validation

- `python3 -m unittest discover -s tests -v` — **pass:** 5 total, 5 passed, 0 failed, 0 skipped.
- `python3 -m compileall -q custom_components tests` — **pass**.
- `python3 -m tabnanny custom_components tests` — **pass**.
- Ruff was not installed; no Ruff run is claimed.
- File, staged-content, and privacy audit before commit: no private Bluetooth MAC, personal measurement, secret/token, Home Assistant credential, raw BLE capture, generated cache, virtual environment, or unrelated file included.

# Files Changed in Latest Task

- **Added:** `docs/STAGE1_OBSERVATION_TEMPLATE.md`.
- **Modified:** `docs/CAPTURE_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `FORA6_MASTER_ROADMAP.md`, `ROADMAP.md`, `README.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `CHANGELOG.md`.
- **Deleted:** none.
- **Code/manifest changes:** none. No discovery matcher or sensor entity was added.

# Outstanding Issues

- The user has not yet supplied the Home Assistant advertisement or proxy/environment observation. Candidate identification and Stage 1B entry criteria therefore remain unresolved.
- Actual connection and notification behavior, exact GD82 support, and all FORA application protocol details remain unknown.

# Explicitly Not Yet Authorized

- Do not begin Stage 1B until a real candidate advertisement has been reviewed and Stage 1B is explicitly authorized. Do not subscribe to notifications without separate explicit authorization.
- Do not begin Stage 2, invent/transmit FORA command bytes, implement application protocol behavior, add a manifest Bluetooth matcher, or expose sensor entities.
- Do not push, create a remote repository, merge, tag, publish, or release. Do not access unrelated repositories.

# Exact Next Gate

**Obtain the user's Home Assistant Advertisement Monitor observation** using `docs/CAPTURE_GUIDE.md`: record the Atom Lite scanner/proxy fields and at least two candidate advertisement observations privately, then provide a sanitized summary for review. Stage 1 remains in progress until actual evidence is evaluated.

# Last Updated

2026-09-26 (Europe/London), at Stage 1A documentation pre-commit review. Final commit SHA and working-tree status are reported separately.
