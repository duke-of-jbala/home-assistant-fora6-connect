# FORA 6 Codex Handover

## Task

Establish a durable Markdown handover workflow after the Stage 0 bootstrap checkpoint, without starting Stage 1.

## Starting State

- **Branch:** `main`.
- **Starting commit:** `34cf585f90bf2b7630651860931bcda9d0616576` — `chore: bootstrap FORA 6 Home Assistant integration`.
- **Working tree:** clean (`git status --short --branch --untracked-files=all` showed `## main` and no file entries).

## Work Performed

Created one authoritative master roadmap with all Stage 0–12 gates and preserved architecture decisions. Replaced the old roadmap with a pointer. Added this task handover and updated the status, Codex instructions, and unreleased changelog. The existing Stage 0 checkpoint remains the baseline; this workflow is a separate documentation task.

## Files Added

- `FORA6_MASTER_ROADMAP.md`
- `CODEX_HANDOVER.md`

## Files Modified

- `AGENTS.md`
- `ROADMAP.md`
- `CURRENT_STATUS.md`
- `CHANGELOG.md`

## Files Deleted

None.

## Technical Decisions

- `FORA6_MASTER_ROADMAP.md` is authoritative; `ROADMAP.md` remains a pointer for existing links.
- Tracked handover files record the last completed checkpoint and the six changes after it, avoiding a self-referential task commit SHA. The task commit's full SHA and final working-tree state are reported after the commit.

## Evidence / Findings

- **Observed in local Git at task start:** HEAD was the existing Stage 0 bootstrap commit, branch `main`, and local `origin` pointed to the intended GitHub URL. The working tree was clean.
- **From the Stage 0 brief, not newly observed:** the documented FORA service/characteristic UUIDs and write/notify claim. No BLE capture, hardware observation, or protocol inference occurred in this task.

## Commands / Checks Run

- `git status --short --branch --untracked-files=all`, `git rev-parse HEAD`, `git log -1 --format='%s'`, `git remote -v` — confirmed the clean starting state and existing checkpoint.
- `python3 -m unittest discover -s tests -v` — pass, 5 tests.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `python3 -c 'import json,pathlib; files=list(pathlib.Path("custom_components").rglob("*.json"))+[pathlib.Path("hacs.json")]; [json.loads(p.read_text()) for p in files]; print(f"Validated {len(files)} JSON files")'` — pass, 4 JSON files.
- `ruff check .` and `ruff format --check .` — unavailable (`ruff: command not found`, exit 127).
- Final Git/file/privacy audit — the six listed Markdown files are the only task changes; generated Python caches were removed.

## Tests

- **Total:** 5
- **Passed:** 5
- **Failed:** 0
- **Skipped:** 0
- **Unavailable tooling:** Ruff lint and format checks; Ruff is not installed.

## Git State

- **Branch:** `main`
- **Last completed checkpoint SHA:** `34cf585f90bf2b7630651860931bcda9d0616576`
- **Checkpoint commit message:** `chore: bootstrap FORA 6 Home Assistant integration`
- **Changes after checkpoint:** yes — the six Markdown files listed above. The pre-commit review found a dirty working tree with exactly these files and no staged files. The task commit's full SHA and final status are in the post-commit response.
- **Pushed:** no.
- **Tagged:** no.
- **Released:** no.

## Blockers / Unknowns

Ruff is unavailable. BLE advertisement/GATT behavior and the FORA application protocol remain unknown; they are outside this task. The Stage 0 bootstrap commit remains intact; this documentation workflow is committed separately.

## Privacy Check

No private measurements, secrets, MAC addresses, raw captures, or other sensitive material are included in this documentation task. The new Markdown contains only project metadata and the UUIDs supplied in the Stage 0 brief.

## Exact Next Gate

**Stage 1 — FORA 6 BLE discovery**, only after explicit user authorization. Record advertisement, GATT, and notification observations with provenance and privacy controls.

## Authorization Boundary

Do not start Stage 1, access real hardware, implement speculative protocol behavior, push, create a remote repository, merge, tag, or release without explicit authorization. Screenshots are not required for this handover; use the Markdown files and local Git state.
