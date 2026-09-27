# Current Status — FORA 6 Connect

**Stage 7H manual current-state refresh is implemented and synthetic-tested; real Home Assistant validation is pending.** It supports only raw counts two/four through an explicit configured-entry action. The existing uric-acid entity starts unavailable and can become available after a successful manual run. Stages 0–6B3 and 7A–7G remain complete for their authorized scopes. No historical import, persistent dedup/resume, polling, startup sync, or advertisement-triggered sync exists.

## Stage 7H pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Starting checkpoint:** `1ad97c17fe02c8e313c63ecb12c7c8d6aa1fbd2a` — `docs: close Stage 7G chronology validation`.
- **Starting tree:** clean (`git status --short` returned no entries); origin was the public project repository.
- **Changes after checkpoint:** yes. At this pre-commit observation, runtime, action metadata, tests, and documentation are modified; the working tree is not clean. Verify and report the post-commit/push state separately.
- **Implementation:** `refresh_current_uric_acid` targets a configured entry, verifies canonical MAC/locator and project identity, accepts only count two/four, validates all fixed pairs, excludes QC-invalid companions, and selects an eligible General uric-acid primary. At count four, two eligible primaries require a unique later meter-local minute; ties fail closed. State changes only after clean transport cleanup. One per-entry lock rejects overlapping runs; no background trigger exists.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `custom_components/fora6_connect/__init__.py`, `coordinator.py`, `sensor.py`, `sensor_state.py`, `services.yaml`, `translations/en.json`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md`, `docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md`, `docs/STAGE7_HISTORY_SYNC.md`, new `docs/STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md`, `tests/test_gatt_probe.py`, `tests/test_stage6b_entity.py`, and new `tests/test_manual_refresh.py`.
- **Checks actually run so far:** full verbose suite **369/369 passed** (baseline 353); compileall and tabnanny passed; all five tracked JSON/YAML files parsed; `git diff --check` and `git diff --cached --check` passed. Runtime diff, command IDs, privacy boundary, automatic-trigger absence, and tracked-artifact inventory were inspected. No real health data, identifier, proprietary artifact, or private path was added. No physical meter operation was performed by Codex.

**Exact next gate:** deploy Stage 7H to the existing Home Assistant installation, restart, manually turn the GD82 ON without pressing its history arrows, run `fora6_connect.refresh_current_uric_acid` once for the configured entry, and inspect the existing uric-acid entity. Share only sanitized status/behavior for closure. Broader sync requires separate authorization.

## Earlier Stage 7G2 checkpoint

## Stage 7G2 pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Starting checkpoint:** `623c343429c26f931b2885252b8af56d6fda19db` — `feat: expose private chronology probe values`.
- **Starting tree:** clean (`git status --short` returned no entries); origin is the public project repository.
- **Changes after checkpoint:** yes, Markdown evidence/status only. This is a pre-commit observation; verify post-commit and remote state separately.
- **Real chronology:** the manually ON meter passed count-four, project, both General uric-acid primary gates, relative comparison, and cleanup. Raw primary **0** had the later parsed meter-local time than raw primary **2** in this snapshot. A higher raw index was not newer here. No private health value, date, time, or identifier is tracked.
- **Meter state:** the user observed normal power-on with flashing Bluetooth light, and history-arrow browsing stopped that light. The cause is unresolved; no runtime change was made.
- **Conversion review:** both retained app versions use the `mg/dL × 59.48 ÷ 1000` mmol/L conversion and two-decimal `FLOOR` formatting in the record-display path. A separate threshold formatter uses `HALF_UP`. Two distinct private base measurements showed the same two-decimal mmol/L meter text. Equivalent firmware formatting is inferred, not proven.
- **Design outcome:** count two remains ready for a narrow manual current-state implementation review. Count four is conditionally ready with complete fixed-plan validation, strict greatest meter-local timestamp among eligible primaries, and fail-closed equal-minute ties. Manual meter-on/no-arrow trigger only. Stage 7H requires separate authorization.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md`, `docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md`, `docs/STAGE7_HISTORY_SYNC.md`, `docs/URIC_ACID_UNIT_CONVERSION.md`.

## Checks

Full verbose unit suite: **353 tests passed** (baseline 353). Compileall and tabnanny passed. Four JSON and one YAML file parsed. `git diff --check` and `git diff --cached --check` passed. Changed-file and added-line scans found no real health value, meter timestamp, MAC, serial, private path, proprietary source, or capture. Tracked artifact scan found no prohibited file. The staged diff was reviewed. Only Markdown changed; no physical operation was performed by Codex.

**Exact next gate:** separately authorize Stage 7H strict manual current-state uric-acid refresh for raw counts two/four only, with full fixed-plan semantic validation, strict meter-local timestamp selection for two eligible count-four primaries, equal-minute tie rejection, and prior-state retention on failure. No historical import, persistent dedup/resume, polling, or automatic trigger.
