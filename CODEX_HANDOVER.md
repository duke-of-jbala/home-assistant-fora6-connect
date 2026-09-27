# FORA 6 Connect Codex Handover

## Stage 7G1 private primary correlation output

Starting checkpoint: clean public `main` at `efd280d2617bc605811077813977745dae810018` (`feat: add primary chronology probe`) on 2026-09-27 (Europe/London). Files changed after that checkpoint are listed in `CURRENT_STATUS.md`. This is a **pre-commit observation**; verify and report post-commit/push state separately.

The separately authorized Stage 7G1 follow-up changes only the existing development-only `fora6_connect.probe_history_chronology` response. After a raw primary independently passes uric-acid/General/valid/non-QC gating, the response includes that primary's evidence-backed mg/dL value (`raw / 10`) and exact parsed meter-local minute as `YYYY-MM-DD HH:MM`. Index 0 and index 2 are treated independently; a failing record has no corresponding health fields. The count-four gate, project confirmation, fixed User1 `0x22 → 0x24 → 0x2B → 0:(0x25,0x26) → 2:(0x25,0x26)` sequence, relative booleans, and fail-closed behavior remain unchanged.

The response is **private health data**. No value or timestamp is logged, persisted, committed as real data, added to diagnostics, or used by the sensor. Raw frames, raw wire integers, address, serial, System ID, and hashes remain excluded. The unit is mg/dL; meter-local time has minute precision and no timezone. The uric-acid entity remains unavailable; no production sync or physical Stage 7G1 run occurred in this task.

Files changed: see `CURRENT_STATUS.md`. Focused Stage 7G1 tests: **12 passed**. Full verbose suite: **353 passed** (352 existing plus one new test). Compileall, tabnanny, four JSON parses, one YAML parse, `git diff --check`, and `git diff --cached --check` passed. Changed-file privacy and tracked-artifact scans found no prohibited data or file; the staged diff was reviewed. The action has no logging, storage, product-state update, or new command path.

**Exact next gate:** user-run private Stage 7G1 physical action with the meter manually ON and count four, compare values/times to the physical display locally, and report only a privacy-safe slot-to-display/order conclusion. Do not share the action response or real values/timestamps. Any current-state sync or further chronology experiment requires separate authorization.
