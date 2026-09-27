# FORA 6 Connect Codex Handover

## Stage 7G bounded primary chronology probe

Starting public checkpoint: clean `main` at `29e1af06a83043ec2bd08094ca1074d274e31016` (`docs: define minimum FORA sync architecture`) on 2026-09-27 (Europe/London). Files changed after that checkpoint as listed in `CURRENT_STATUS.md`. This records a **pre-commit observation**; verify and report the post-commit/push state separately.

[The Stage 7G design and action](docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md) requires project `0x4183`, one User1 metadata response with raw count exactly four, and precisely two User1 record pairs at indexes 0 then 2. Each primary must be identified as valid, non-QC General uric acid. Only then are the two naive meter-local timestamps compared in memory. The response gives three mutually exclusive relative-order booleans, plus gate and cleanup flags. It never returns or logs values, timestamps, raw frames, hashes, serial, or address. It performs no production update or persistence and introduces no new command.

The action has synthetic test coverage only. Stage 7E's real four-slot evidence motivated these fixed indexes; no Stage 7G real result exists yet. Do not interpret a later raw timestamp as a general index-order rule. Meter browsing order alone does not identify which raw slot corresponds to a displayed result. Stage 7F's earlier proposed production refresh was superseded by this separately authorized chronology evidence step. The existing sensor remains unavailable.

Files changed: see the complete explicit list in `CURRENT_STATUS.md`. Focused Stage 7G tests: **11 passed**. Full verbose suite: **352 passed** (341 existing plus 11 new). Compileall, tabnanny, four JSON parses, one YAML parse, `git diff --check`, and `git diff --cached --check` passed. The changed-file privacy and tracked artifact scans found no prohibited data or file. The staged diff was reviewed. The new action has no persistence, product-state update, logging, pairing, or additional command path.

**Exact next gate:** user-run Stage 7G physical action once with the meter manually ON and strict count four, plus only the sanitized action result and private meter browsing-order statement (“newest first”, “oldest first”, or “cannot tell”). Review this one-snapshot chronology before separately authorizing further experiments or production current-state sync. Historical import, polling, dedup, and resume remain unauthorized.
