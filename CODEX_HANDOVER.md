# FORA 6 Connect Codex Handover

## Stage 7F offline minimum-sync design review

This task began on clean public `main` at `255f7f969bde199c7d67a4e68960589ec158915f` (`docs: record successful Stage 7E four-slot traversal`) on 2026-09-27 (Europe/London). Only Markdown documentation/status changed after that checkpoint. This is a **pre-commit observation**; report the post-commit and pushed state separately after checking it.

[The Stage 7F review](docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md) selects **Outcome A, conditional**: design an explicit manual current-sensor refresh for only raw counts two and four, with literal physically validated `1 → 0 → 1` and `3 → 0 → 1 → 2 → 3` plans. A numeric update requires exactly one valid General uric-acid primary in a complete, semantically consistent supported-count snapshot. If count four has two eligible primaries, chronology is unresolved and the sensor must not choose either. Count larger than four, odd counts, malformed pairs, QC, invalid sentinel, and unsupported analytes do not update state. No persistent dedup key is needed for a single current-state refresh; historical observation import still lacks one.

The tracked Stage 7D app review and Stage 7B/C/E physical results support this narrow plan. They do not prove whether index two is the newly added measurement, cross-group chronological order, capacity, wrap, deletion/reset behavior, durable index identity, or resume. Meter-local time remains naive and separate from ingestion time. The observed post-measurement Bluetooth-flashing state failed subscription; the initial trigger recommendation is explicit manual refresh while the meter is stably ON. Stage 7F performed no physical operation and changed no runtime source.

Changed files: `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md`, `docs/STAGE7D_GENERAL_TRAVERSAL_DEDUP_REVIEW.md`, `docs/STAGE7E_FOUR_SLOT_TRAVERSAL_PROBE.md`, `docs/STAGE7_HISTORY_SYNC.md`, `docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md`.

Full verbose unit suite **341 passed**; compileall and tabnanny passed; four JSON and one YAML parsed; both diff whitespace checks passed before and after staging. Only Markdown changed. The privacy/artifact scan found no real device identifier, private path, health value, timestamp, raw capture, or proprietary source.

**Exact next gate:** separately authorize Stage 7G implementation/review of this fixed-count, sole-eligible-primary, manual current-state path. A two-eligible-primary count-four snapshot must fail closed and lead to a separate bounded chronology experiment, not an index/time guess. Historical import, automatic triggering, persistence, and resume remain unauthorized.
