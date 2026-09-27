# FORA 6 Connect Codex Handover

## First public GitHub push: blocked by historical paths

The first-publication audit found specific local absolute filesystem paths in older revisions of `AGENTS.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, and `FORA6_MASTER_ROADMAP.md`. Current tracked revisions no longer contain them, but they remain in Git history. All existing commits also expose a personal, non-noreply author name and email; decide whether that attribution is intended for publication. Per the user's first-push gate, **do not push `main` until a separately authorized history cleanup removes the paths and the rewritten history is re-audited**. No rewrite, force push, tag, release, physical test, or Stage 7B work was performed. The known local path also named another repository in an early `AGENTS.md` revision; that repository was not accessed.

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Last completed/checkpoint commit before task:** `e40caca2b7ab621e94925a48854b15a172588e3e` — `feat: enrich FORA device metadata`.
- **Starting working tree:** clean, verified before edits. `origin` matched the intended GitHub repository and there were no tags.
- **Changes after checkpoint:** yes, public README and ignore-file corrections plus status/handover refresh. This is a pre-commit observation; verify and report the task commit SHA and final tree separately.
- **Files changed:** `.gitignore`, `README.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`.
- **Runtime boundary:** no integration code, BLE commands, action schemas, Config Flow, measurement mapping, or synchronization behavior changed.

## Audit and checks

- Full unit suite: **242 passed** (`python3 -m unittest discover -s tests -v`).
- `compileall` and `tabnanny`: passed; four JSON and one YAML file parsed.
- Four placeholder PNGs validated for format, dimensions, alpha, and size; landscape artwork rendered and inspected. MIT license present. HACS metadata and manifest represent development status, with no release tag.
- Complete tracked-file inventory and 573 historical blobs reviewed for filenames, capture/package/key artifacts, local paths, MAC-shaped values, and common credential markers. No captured/proprietary binary or credential marker was found; the one historical MAC shape was an all-`AA` synthetic fixture. The historical absolute paths are the publication blocker.
- Runtime command and dependency review found no Stage 7 sync loop, new BLE command, or BLE I/O in `sensor.py`; pure protocol/model/measurement modules remain free of HA/Bleak imports.
- `git diff --check` and staged-diff checks are recorded in the final task report after staging.

**Immediate publication gate:** decide whether to retain or anonymize personal Git attribution, authorize a focused history cleanup preserving substantive commits, then rerun the full privacy and quality gates before the first public push. **Exact protocol gate after that:** separately authorize Stage 7B bounded physical traversal probe implementation and user-run validation under [the Stage 7A design](docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md). General traversal, latest ordering, deduplication, and production entity updates remain deferred.
