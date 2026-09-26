# Current Stage

Stage 0 is complete. **Stage 1 — FORA 6 Connect BLE discovery is in progress.** Stage 1A capture preparation is complete, but no real-device advertisement has been supplied or observed in this naming task. Stage 1B has not begun. Stage 2 is not authorized.

# Current Gate

Complete the local checkout-directory move after this naming commit, then obtain and review the user's Home Assistant Advertisement Monitor observation. Do not infer device identity from a name or UUID match alone.

# Repository

- **Actual checkout path at this task's pre-commit review:** `<former local checkout>`
- **Canonical target path:** `<local checkout>`
- **Directory move:** pending manual action after commit to avoid invalidating the active Codex workspace.
- **GitHub repository target:** `duke-of-jbala/home-assistant-fora6-connect`; no remote GitHub repository was created or contacted.
- **Branch:** `main`
- **Last completed checkpoint commit SHA:** `f3a47969f793b39ac04625054a4719e0481c55e6`
- **Checkpoint commit message (historical, verbatim):** `docs: begin FORA 6 BLE discovery stage`
- **Local origin URL:** `https://github.com/duke-of-jbala/home-assistant-fora6-connect`
- **Changes after checkpoint:** yes — this naming migration. At pre-commit review the tree was dirty with only the project changes listed below. The migration commit's full SHA and final `git status --short` are reported after commit, outside tracked Markdown.

# Completed Work

- Renamed the integration directory to `custom_components/fora6_connect/`, updated the manifest and constants to domain `fora6_connect` and display name **FORA 6 Connect**, and updated HACS metadata and tests.
- Updated repository URLs, product naming, roadmap, README, architecture/protocol/decision documentation, Codex instructions, status, handover, and changelog. The master roadmap filename remains `FORA6_MASTER_ROADMAP.md` by design.
- Changed only the local `origin` URL to the new target. No network operation, GitHub repository creation, BLE discovery, hardware connection, application write, or protocol implementation occurred.

# Validated Facts

- Canonical product/display name: **FORA 6 Connect**. Model/variant: **GD82**. Integration domain and directory: `fora6_connect` and `custom_components/fora6_connect/`.
- The Stage 0 brief reports FORA documentation listing service UUID `00001523-1212-efde-1523-785feabcd123`, characteristic UUID `00001524-1212-efde-1523-785feabcd123`, and write/notify properties. These remain documentary claims; actual meter advertisement and GATT have not been observed.
- The user's proxy is described as an M5Stack Atom Lite running ESPHome. Its actual scanner state and capabilities have not yet been observed here. The UUID pair alone cannot identify a FORA 6 Connect.

# Unvalidated / Unknown

- Candidate advertisement, local name, address behavior, manufacturer/service data, RSSI/source relationship, connectability, and physical GATT inventory.
- Atom Lite scanning mode, ESPHome version, active/GATT capability, and connection slots in the user's installation.
- FORA application commands/responses, framing, record format, analyte codes, timestamps, control flags, and historical memory behavior. No protocol behavior was inferred in this task.

# Tests and Validation

- `python3 -m unittest discover -s tests -v` — **pass:** 5 total, 5 passed, 0 failed, 0 skipped.
- `python3 -m compileall -q custom_components tests` — **pass**.
- `python3 -m tabnanny custom_components tests` — **pass**.
- JSON syntax and naming consistency audit — **pass:** manifest domain/name match directory, constants, HACS metadata, and intended repository URL.
- Ruff was unavailable; no Ruff result is claimed.
- Tracked-file and privacy audit — **pass:** no private Bluetooth MAC, personal measurement, secret/token, Home Assistant credential, raw capture, generated cache, virtual environment, or unrelated file is included in the commit.

# Files Changed in Latest Task

- **Renamed:** all 12 tracked files from `custom_components/fora6/` to `custom_components/fora6_connect/`; `__init__.py`, `const.py`, and `manifest.json` also changed internally.
- **Modified:** `AGENTS.md`, `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/PROTOCOL.md`, `hacs.json`, `tests/test_bluetooth.py`, `tests/test_protocol.py`, and `tests/test_sensor.py`.
- **Local Git metadata:** `origin` URL changed; this is not part of the commit.
- **New BLE/protocol functionality:** none.

# Outstanding Issues

- The checkout directory itself remains at the old path until the user moves it safely after this session. Tracked documentation distinguishes that actual path from the canonical target.
- The GitHub repository under the new name has not been created. Local `origin` points to the intended future URL only.
- No real advertisement or proxy-environment observation has been supplied; Stage 1B entry criteria remain unmet.

# Explicitly Not Yet Authorized

- Do not start Stage 1B or Stage 2, transmit or invent FORA application commands, add a Bluetooth discovery matcher, or expose sensors.
- Do not push, create the remote GitHub repository, merge, tag, publish, or release. Do not access unrelated repositories.

# Exact Next Gate

After the manual local directory move, **obtain the user's Home Assistant Advertisement Monitor observation** using `docs/CAPTURE_GUIDE.md` and review a sanitized summary. Stage 1 remains in progress; Stage 1B needs separate authorization after candidate review.

# Last Updated

2026-09-26 (Europe/London), at naming-migration pre-commit review. The final commit SHA and post-commit tree state are reported separately.
