# FORA 6 Connect Codex Handover

## Stage 7H manual current-state refresh implementation

Starting checkpoint: clean public `main` at `1ad97c17fe02c8e313c63ecb12c7c8d6aa1fbd2a` (`docs: close Stage 7G chronology validation`) on 2026-09-27 (Europe/London). The current task changed runtime, service metadata, tests, and Markdown files listed in `CURRENT_STATUS.md`. This is a **pre-commit observation**; the working tree currently has those changes and is not clean. Verify/report post-commit and remote state separately.

[Stage 7H](docs/STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md) adds `fora6_connect.refresh_current_uric_acid`, using a configured-entry selector and no manually entered Bluetooth address. A per-entry coordinator requires canonical factory-MAC/locator agreement and project `0x4183`, reads only fixed two-/four-slot User1 plans, validates QC-invalid companions and eligible General uric-acid primaries, selects by strict meter-local time for two eligible four-slot primaries, and rejects equal-minute ties. The selected mg/dL value feeds the existing sensor only after clean unsubscribe/disconnect. A successful ingestion time remains distinct from naive meter-local measurement time. Prior valid state survives failures. There is no history import, persistent dedup/resume, startup, advertisement, scheduled, or periodic refresh.

Full verbose suite: **369/369 passed** (baseline 353). Compileall, tabnanny, five JSON/YAML parses, both diff whitespace checks, and runtime/command/privacy/artifact review passed at this pre-commit observation. Only synthetic test values are tracked. The physical GD82 was not operated by Codex. The action response can privately contain selected health value and meter-local minute; they are not logged or placed in public docs.

**Exact next gate:** user-run Stage 7H validation on the existing HA entry: deploy/restart, turn the meter ON normally, avoid history arrows, run the action once, inspect the existing uric-acid entity, and report sanitized status/behavior. No historical or automatic sync follows without separate authorization.

## Previous Stage 7G2 checkpoint

## Stage 7G2 physical closure and offline unit-format review

Starting checkpoint: clean public `main` at `623c343429c26f931b2885252b8af56d6fda19db` (`feat: expose private chronology probe values`) on 2026-09-27 (Europe/London). The task changed only the Markdown files listed in `CURRENT_STATUS.md`. This is a **pre-commit observation**; verify and report post-commit/push state separately.

[Stage 7G's bounded physical result](docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md) confirmed count four, project identity, two valid General uric-acid primaries, and clean cleanup. Raw primary 0 was later than raw primary 2 by their parsed meter-local times in that real snapshot. Stage 7G is **complete for this bounded scope**. Highest raw index was not newest there, but arbitrary-count ordering, clock reset, buffer wrap, and durable record identity remain unresolved. The user also saw history-arrow browsing stop the Bluetooth light after normal manual ON had produced flashing light; the internal reason is unknown.

[The two-version app conversion review](docs/URIC_ACID_UNIT_CONVERSION.md) finds `mg/dL × 59.48 ÷ 1000` followed by two-decimal `FLOOR` formatting in the uric-acid record-display path; settings/range thresholds use a separate `HALF_UP` formatter. This app behavior explains why distinct base records can share one two-decimal mmol/L display text. The physical meter firmware's exact arithmetic remains unproven. No real value, date, time, private path, proprietary source, identifier, or capture was added to Git.

[The Stage 7F reassessment](docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md) conditionally supports a separately authorized manual-only current-state refresh at exact raw counts two/four. At count four, select the strict maximum naive meter-local time among eligible General uric-acid primaries only after complete fixed-plan validation; ties fail closed. A meter-clock change remains a residual limitation. A second metadata query can be deferred for the first manually ON/no-arrow procedure because it cannot guarantee atomicity and its placement lacks physical validation. The sensor remains unavailable; Stage 7H production implementation has not begun.

Files changed: see `CURRENT_STATUS.md`. Full verbose suite: **353 passed** (baseline 353). Compileall, tabnanny, four JSON parses, one YAML parse, `git diff --check`, and `git diff --cached --check` passed. Changed-file/added-line privacy and tracked artifact scans found no prohibited data or file. The staged diff was reviewed; only Markdown changed.

**Exact next gate:** separately authorize Stage 7H strict manual current-state uric-acid refresh for raw counts two/four with full fixed-plan validation, meter-local timestamp selection and equal-minute tie rejection, previous-state retention on failure, and no history import, persistence, resume, polling, or automatic trigger.
