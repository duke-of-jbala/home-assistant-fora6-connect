# Stage 8H-B — bounded uric-acid history action, synthetic implementation

**Status:** repository implementation with synthetic validation only. No real GD82 history action was run, and this build was **not deployed** to Home Assistant. The currently deployed Stage 13A-P4 transaction-readiness build stays in place until its naturally occurring post-measurement comparison. P4 remains physically **open**; Stage 13B remains unstarted. The released `v1.0.0` tag remains at `dd26b65ab467381db58ba7a525c6b8eabca8e00a`.

## Baseline and boundary

Started on 2026-09-28 (Europe/London) from observed clean `main` at `33aaca6a378b41e2a0b24c75856f6c90aa8f65af` (`docs: design bounded uric-acid history exposure`), with local `origin/main` matching and `git status --short` empty. The [Stage 8H-A architecture](STAGE8H_A_BOUNDED_HISTORY_ARCHITECTURE.md) authorizes exactly count-two/four manual private history exposure, no import or persistence. Record layout, request constructors, native mg/dL scaling, identity checks, and the tested raw-slot shapes already have [Stage 2G](STAGE2G_TD4183_RECORD_SCHEMA.md), [Stage 7E](STAGE7E_FOUR_SLOT_TRAVERSAL_PROBE.md), [Stage 7G](STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md), and [Stage 7H](STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md) provenance. This task adds no protocol behavior or captured fixture.

## Implementation

`fora6_connect.read_uric_acid_history` is an explicitly invoked action registered in integration `async_setup` with a required response. It accepts only `config_entry_id`; no MAC, raw index, count, proxy, or address input. The handler checks the loaded FORA entry, uses its per-entry `history_reader`, and holds the same `gatt_lock` used by manual current refresh and the P4 readiness probe. A second same-entry operation is rejected; different entries retain separate locks. Entry unload cancels a running history action and lets transport cleanup finish. No startup work, callback, poll, or automatic invocation was added.

`bounded_records.py` extracts the **existing** Stage 7H wake/project/metadata and fixed indexed pair read, preserving the same `0x22`, `0x24`, `0x2B`, `0x25`, and `0x26` constructors and parsers. Both current refresh and history use it. It still requires project `0x4183`, validates the metadata response, and fails closed unless raw count is exactly 2 or 4. The exact command sequence for a supported count is wake, project, metadata, then `0x25`/`0x26` for each raw slot in order `0,1` or `0,1,2,3`. Connection and custom notification subscription precede commands. No `0x33`, `0x2F`, or `0x50` request is introduced.

The history reader validates every expected record and all odd-slot QC-invalid companions before publishing a response. Every even primary must be identified, valid, General uric acid and map to native mg/dL. Count 2 returns raw 0 only; count 4 returns raw 0 **and** raw 2. QC-invalid companions are structural checks and never enter `measurements`. The physical observations found matching or near-matching pair times, but no general quantitative tolerance was established; the existing record model explicitly defines no cross-part time constraint. This action therefore does **not** invent a companion-time threshold. It retains the established adjacency and category/invalid-sentinel gates.

Primaries are sorted by parsed meter-local minute, newest first. Equal-minute valid count-four primaries both remain, with `chronology_ambiguous: true`. Ascending raw index is only a stable tie presentation order; it conveys no newer/older claim. Stage 7H's current-state `_select_primary` remains separate and still fails closed on an equal-minute tie. A history read never calls `MeasurementState.replace`, changes `synchronized_at`, alters availability, creates an entity, or updates the current sensor.

## Private response and failure behavior

On complete success, the JSON-compatible response has:

| Field | Meaning |
| --- | --- |
| `history_read_performed`, `history_read_successful`, `supported_raw_slot_count` | Structural operation status; all true after a complete supported read. |
| `raw_slot_count` | The validated raw metadata count, exactly 2 or 4 on success. A raw count is not a logical measurement count or buffer capacity. |
| `eligible_measurement_count` | Exactly 1 or 2 on success. |
| `chronology_ambiguous` | True only when both valid count-four primaries have equal meter-local minutes. |
| `measurements` | One or two objects with `raw_index`, `uric_acid_value_mg_dl`, `meter_local_time` in `YYYY-MM-DD HH:MM` form, and `meter_local_timezone_known: false`. Index is transient within this snapshot, not a durable ID. |
| `error_stage`, `error_code`, `cleanup_errors` | Null/null/empty list on success. The reader retains sanitized operational failures internally; the HA action raises a sanitized exception on failure instead of returning a successful partial list. |

The meter timestamp has minute precision and **unknown timezone**. No UTC, HA, browser, or system offset is attached. This is a wall-clock transcription, not an absolute instant. Native values remain mg/dL; no mmol/L conversion or state-class/statistics change is made.

On identity, subscription, model, metadata, part read, calendar, semantic, or cleanup failure, the reader returns `measurements: []` and zero eligible count. The HA action raises an operational error with bounded stage/code/cleanup labels, sanitized before interpolation. It does not log a value, time, address, raw frame, or upstream exception text. Cleanup failure after valid reads prevents success; an earlier causal error is kept while cleanup codes remain separate. Cancellation propagates after transport cleanup. [Home Assistant's current service-action guidance](https://developers.home-assistant.io/docs/dev_101_services/) supports response dictionaries and recommends exceptions for failed actions; [exception guidance](https://developers.home-assistant.io/docs/core/platform/raising_exceptions/) distinguishes invalid input from communication failure.

The action description and English translation explicitly warn that the response contains **private health values and measurement times**. The integration does not persist the result. Home Assistant scripts, automations, or users could separately copy an action response into traces, notifications, or external storage; users should invoke and handle it privately. The action fires no measurement event and does not write Recorder, statistics, diagnostics, entity attributes, a history database, dedup fingerprints, or a resume cursor. Repeated invocations may return the same meter records.

## Synthetic validation and remaining gate

Synthetic tests use artificial values and dates built from the already evidenced frame/field structure. They cover counts 2/4, both timestamp order directions, equal-minute preservation, unsupported counts including 6+, invalid primaries/companions, identity/project/metadata/part failures, partial count-four failure, cleanup-only and dual failure, locking against current refresh and P4, independent entries, unload/cancellation, private action registration/error text, sensor non-mutation, and forbidden call/command audits. Existing Stage 7H and P4 tests provide regressions for their unchanged selection/probe semantics. No live meter result is claimed.

The manifest remains at `1.0.0`: this is unreleased post-v1 source work, and this gate neither tags nor publishes a new version. The tagged release is unchanged. **Exact next Stage 8H state:** Stage 8H-B synthetic implementation complete; defer physical history validation until the deployed P4 post-measurement comparison is complete and a separate deployment/physical-test gate is authorized. Do not deploy this build now, close P4, or begin Stage 13B.
