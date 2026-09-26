# FORA 6 Connect Codex Handover

## Task

Canonical naming migration from FORA 6 / `fora6` to **FORA 6 Connect** / `fora6_connect`, model **GD82**, without new BLE or protocol work.

## Starting State

- **Branch:** `main`.
- **Starting checkpoint:** `f3a47969f793b39ac04625054a4719e0481c55e6` — `docs: begin FORA 6 BLE discovery stage` (historical Git message, quoted verbatim).
- **Working tree:** clean at task start (`git status --short --branch --untracked-files=all` showed `## main` only).
- **Starting checkout path:** `<former local checkout>`.

## Work Performed

- Renamed the component directory and changed the manifest, constants, HACS name, and tests to `fora6_connect` / FORA 6 Connect.
- Standardized project identity and repository links throughout tracked documentation while preserving GD82 as the model/variant. Preserved the `FORA6_MASTER_ROADMAP.md` filename to avoid unnecessary churn.
- Changed the local `origin` URL to `https://github.com/duke-of-jbala/home-assistant-fora6-connect` without contacting or creating a remote repository.
- Deferred the parent-directory move because this active workspace is rooted in the old path. The canonical target is `<local checkout>`; the actual checkout remains at the old path until the user runs the move command after this session.

## Files Added

None apart from the renamed component paths below.

## Files Modified

- `AGENTS.md`
- `CHANGELOG.md`
- `CODEX_HANDOVER.md`
- `CURRENT_STATUS.md`
- `FORA6_MASTER_ROADMAP.md`
- `README.md`
- `ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/PROTOCOL.md`
- `hacs.json`
- `tests/test_bluetooth.py`
- `tests/test_protocol.py`
- `tests/test_sensor.py`
- `custom_components/fora6_connect/__init__.py`
- `custom_components/fora6_connect/const.py`
- `custom_components/fora6_connect/manifest.json`

## Files Renamed

All 12 tracked files under `custom_components/fora6/` moved to `custom_components/fora6_connect/`: `__init__.py`, `bluetooth.py`, `config_flow.py`, `const.py`, `coordinator.py`, `diagnostics.py`, `manifest.json`, `models.py`, `protocol.py`, `sensor.py`, `strings.json`, and `translations/en.json`.

## Files Deleted

None; the former component path was replaced by the renamed directory.

## Technical Decisions

- `FORA6_MASTER_ROADMAP.md` retains its established filename; its title and contents now use the canonical product name.
- The current checkout path and canonical target path are recorded separately. The parent-directory move is left for a safe manual action after Codex stops; the active session is not moved out from under itself.
- Historical Git commit messages remain verbatim even where they contain the old product wording. They are labeled as historical checkpoint evidence, not current naming.

## Evidence / Findings

- **Observed locally:** the starting checkpoint was clean on `main`; the integration directory, manifest domain/name, constants, and local origin URL have been changed as described. The GitHub repository at the new URL has not been created or contacted.
- **Documentary FORA facts unchanged:** the 1523 service UUID, 1524 characteristic UUID, and documented write/notify claim. These do not prove identity and have not been checked on the physical GD82.
- **Real-device observation:** none supplied or performed. No BLE connection, application command, protocol decoding, or Stage 1B work occurred.

## Commands / Checks Run

- `git status --short --branch --untracked-files=all`, `git rev-parse HEAD`, `git ls-files`, `git remote -v` — inspected the clean 33-file starting checkpoint.
- `rg -n --hidden -g '!.git/**' 'fora6|FORA 6|home-assistant-fora6|duke-of-jbala/home-assistant-fora6' .` — inventoried old naming references before changes.
- `python3 -m unittest discover -s tests -v` — pass, 5 tests.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- JSON, naming, tracked-file, and privacy audits — pass. No old live domain or repository identity remains outside labeled migration/historical references.

## Tests

- **Total:** 5
- **Passed:** 5
- **Failed:** 0
- **Skipped:** 0
- **Unavailable tooling:** Ruff is not installed; no Ruff result claimed.

## Git State

- **Branch:** `main`
- **Last completed checkpoint SHA:** `f3a47969f793b39ac04625054a4719e0481c55e6`
- **Checkpoint message (historical):** `docs: begin FORA 6 BLE discovery stage`
- **Changes after checkpoint:** yes — the naming migration listed above. The migration commit's full SHA and final `git status --short` are reported after commit, outside tracked Markdown.
- **Current checkout path at pre-commit review:** `<former local checkout>`; canonical target path pending manual move.
- **Local origin URL:** `https://github.com/duke-of-jbala/home-assistant-fora6-connect`.
- **Pushed:** no.
- **Tagged:** no.
- **Released:** no.

## Blockers / Unknowns

The active session remains rooted in the old local directory, so the parent-directory move is pending. The remote GitHub repository has not been created. The candidate advertisement and actual Atom Lite scanner capabilities remain unknown.

## Privacy Check

No private measurements, actual MAC addresses, Home Assistant credentials, secrets/tokens, or raw BLE captures were added or committed. The migration contains identifiers for the project and documentary UUIDs only.

## Exact Next Gate

After the user safely moves the checkout directory, obtain the user's **Home Assistant Advertisement Monitor observation** and Atom Lite proxy details described in `docs/CAPTURE_GUIDE.md`. Review a sanitized summary before any Stage 1B work.

## Authorization Boundary

Do not create the remote GitHub repository, push, merge, tag, or release. Do not begin Stage 1B or Stage 2, add a Bluetooth matcher or sensors, or invent/transmit FORA application commands during this naming task.
