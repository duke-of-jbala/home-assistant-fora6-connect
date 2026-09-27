# FORA 6 Connect Codex Handover

## Stage 8 current-state hardening — pre-commit observation

At the start, public `main` was clean at `0775869d2fd7daf5a904795f4d468ac40bcc7798` (`docs: close Stage 7H manual refresh validation`), on 2026-09-27 (Europe/London), with the expected origin. This task has changed files after that checkpoint; the working tree is currently modified. This is a pre-commit observation. The task commit SHA, remote result, and final status belong in the post-commit report.

Stage 8 is **complete for its authorized offline/synthetic review**. The only runtime change is a one-condition error-precedence fix in `coordinator.py`: if a refresh failed before cleanup and cleanup also failed, retain the original error stage/code and return cleanup errors separately. Successful refresh, count-two/four fixed commands, timestamp selection, privacy boundary, configured-entry target, and manual-only triggering are unchanged. New synthetic tests cover repeat same-measurement refresh, prior-state retention after later failures, combined primary/cleanup failures, unload/reload fresh runtime, and two independent entries/locks. The full verbose suite passed **374/374** (baseline 369). Compileall, tabnanny, four JSON and one YAML parse passed. Unstaged and staged diff checks passed, and the complete staged diff was reviewed before this final handover wording update; recheck the final cached diff before committing.

The process-local current value intentionally becomes unavailable on reload/restart until manual refresh. No `RestoreSensor`, measurement-time or status attribute, diagnostic entity, history store, dedup/resume, startup/advertisement/post-measurement trigger, or polling was added. Action response already supplies selected private value/time and bounded status. The mg/dL native sensor value is separate from app mmol/L display formatting. Device identity/metadata is unchanged. Source review and synthetic tests support two-entry isolation at the coordinator/state level; a real multi-device HA validation has not occurred. The exact selected ESPHome proxy path is still unverified.

Files changed are listed in `CURRENT_STATUS.md`; the new durable review is [Stage 8](docs/STAGE8_CURRENT_STATE_HARDENING_REVIEW.md). Changed-file privacy scan found no private paths, real health examples, or secret assignments; MAC-shaped strings occur only in explicitly synthetic test fixtures. Artifact and runtime command/automation/logging scans found no new prohibited path. No physical meter test was run.

**Exact next proposed gate:** separately authorize Stage 9 explicit ESPHome Bluetooth Proxy path validation. Optional Stage 8H bounded manual uric-acid history exposure is a separate future gate, not a prerequisite. Do not start either from this handover.

## Stage 7H real-device closure — pre-commit observation

Starting checkpoint: clean public `main` at `b5b21ceeaa933d10195febf82f333f74874cf766` (`feat: add manual uric acid refresh`) on 2026-09-27 (Europe/London). Origin is the expected public repository and no tags are present. This task changes Markdown status/evidence files only; this is a **pre-commit observation**. The working tree is currently modified, so report its post-commit/push state separately.

The user validated `fora6_connect.refresh_current_uric_acid` against the existing configured GD82. They powered it on normally, avoided the history arrows, and ran the action once. At raw count four, both candidate primaries were eligible and the parsed meter-local ordering selected index zero. The action succeeded and cleanup was clean. The existing GD82/ForaCare device and single uric-acid entity remained; the entity became available and showed the selected mg/dL state. No duplicate appeared. The private result's value and timestamp, screenshot, MAC, serial, and System ID are intentionally absent from the repository.

Stage 7H is **complete for its authorized scope**: exact count-two indexes `0 → 1`; exact count-four indexes `0 → 1 → 2 → 3`; count-four selection by strictly later minute-precision meter-local time when two primaries qualify; equal-minute ties fail closed. Manual refresh only. Counts above four, history import, recorder/statistics backfill, persistent record identity/dedup/resume, automatic triggers, mixed-analyte support, and meter-state automation remain out of scope. Meter-local time has unknown timezone and the meter clock can affect apparent order; raw-index magnitude is never a chronology rule.

Full suite: **369/369 passed** (baseline 369). Compileall, tabnanny, five JSON/YAML parses, diff checks, and privacy/health/identifier/artifact/path/proprietary-source audits passed. Only Markdown changed; no physical operation was performed by Codex during this closure.

**Exact next proposed gate:** Stage 8 offline/synthetic/design-first hardening and product-behavior review. Stage 9 proxy-path validation and later release gates remain pending. Do not begin them from this closure.

## Previous Stage 7G2 checkpoint

## Stage 7G2 physical closure and offline unit-format review

Starting checkpoint: clean public `main` at `623c343429c26f931b2885252b8af56d6fda19db` (`feat: expose private chronology probe values`) on 2026-09-27 (Europe/London). The task changed only the Markdown files listed in `CURRENT_STATUS.md`. This is a **pre-commit observation**; verify and report post-commit/push state separately.

[Stage 7G's bounded physical result](docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md) confirmed count four, project identity, two valid General uric-acid primaries, and clean cleanup. Raw primary 0 was later than raw primary 2 by their parsed meter-local times in that real snapshot. Stage 7G is **complete for this bounded scope**. Highest raw index was not newest there, but arbitrary-count ordering, clock reset, buffer wrap, and durable record identity remain unresolved. The user also saw history-arrow browsing stop the Bluetooth light after normal manual ON had produced flashing light; the internal reason is unknown.

[The two-version app conversion review](docs/URIC_ACID_UNIT_CONVERSION.md) finds `mg/dL × 59.48 ÷ 1000` followed by two-decimal `FLOOR` formatting in the uric-acid record-display path; settings/range thresholds use a separate `HALF_UP` formatter. This app behavior explains why distinct base records can share one two-decimal mmol/L display text. The physical meter firmware's exact arithmetic remains unproven. No real value, date, time, private path, proprietary source, identifier, or capture was added to Git.

[The Stage 7F reassessment](docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md) conditionally supports a separately authorized manual-only current-state refresh at exact raw counts two/four. At count four, select the strict maximum naive meter-local time among eligible General uric-acid primaries only after complete fixed-plan validation; ties fail closed. A meter-clock change remains a residual limitation. A second metadata query can be deferred for the first manually ON/no-arrow procedure because it cannot guarantee atomicity and its placement lacks physical validation. The sensor remains unavailable; Stage 7H production implementation has not begun.

Files changed: see `CURRENT_STATUS.md`. Full verbose suite: **353 passed** (baseline 353). Compileall, tabnanny, four JSON parses, one YAML parse, `git diff --check`, and `git diff --cached --check` passed. Changed-file/added-line privacy and tracked artifact scans found no prohibited data or file. The staged diff was reviewed; only Markdown changed.

**Exact next gate:** separately authorize Stage 7H strict manual current-state uric-acid refresh for raw counts two/four with full fixed-plan validation, meter-local timestamp selection and equal-minute tie rejection, previous-state retention on failure, and no history import, persistence, resume, polling, or automatic trigger.
