# Stage 7F — minimum production sync reassessment

**Later validation note:** Stage 7G's real four-slot result resolved that snapshot's primary ordering by parsed meter-local time. The user then physically validated the separately authorized [Stage 7H](STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md) manual count-four current-state refresh; the existing entity became available without duplication. Stage 7F remains an offline design record. Historical import, dedup, resume, and automatic triggers remain deferred.

**Original Stage 7F decision (before Stage 7G): Outcome A, conditional current-state refresh only.** An explicitly requested, bounded refresh can be designed for the physically tested raw counts **2 and 4** if it accepts only a *single* valid General uric-acid primary in the complete, internally consistent snapshot. It must decline to choose between two eligible primaries. This original decision is superseded for the two-primary count-four case by the **Stage 7G2 reassessment below**. Neither review implements or authorizes production meter operation. Full historical synchronization remains unjustified.

## Evidence and scope

The source base is the tracked [Stage 7A](STAGE7A_HISTORY_TRAVERSAL_DESIGN.md) and [Stage 7D](STAGE7D_GENERAL_TRAVERSAL_DEDUP_REVIEW.md) two-version app analysis, the private import capture's sanitized `1 → 0 → 1` request order, and the user-run [Stage 7B/C](STAGE7C_SEMANTIC_PAIR_CONFIRMATION.md) and [Stage 7E](STAGE7E_FOUR_SLOT_TRAVERSAL_PROBE.md) results. The retained private source and capture remain outside Git; this review uses their existing tracked paraphrases and adds no proprietary source, private value, or timestamp. The app handler maps multi-parameter logical index `i` to raw primary `2*i` and possible companion `2*i+1` (**STATIC-ANALYSIS-SUPPORTED BOTH VERSIONS**). Count-two and count-four physical results support the even-General/odd-QC-invalid pattern only in those tested meter states (**LIVE-CORROBORATED**). The four-slot test also found equal meter-local times within `0/1` and `2/3`. It did not report the relative time of primaries 0 and 2, or the analyte identity of index 2.

## Logical grouping and record policy

| Raw count | Bounded candidate groups | Evidence limit |
| --- | --- | --- |
| 2 | Primary 0, possible companion 1 | The tested primary was uric acid/General/valid; index 1 was hematocrit/QC/invalid. The app's multi-mode mapping and physical pair sequence agree. Within-pair time equality was not part of the Stage 7C result. |
| 4 | Primaries 0 and 2, possible companions 1 and 3 | Both even slots were identified General/valid and both odd slots QC/invalid in one tested state. Both adjacent pairs had equal meter-local time; index 3 was stable on repeat. Exact analytes and cross-group time order were not returned. |

A proposed refresh must parse every fixed slot using the existing parser, check the last-slot multi-mode condition and every companion's observed QC/invalid structure, and reject any mismatch. Comparing paired meter-local times in memory is a conservative consistency check, not a universal protocol law: iFORA HM 1.7.6 and 1.7.9 differ on that guard. A pair that fails it is unsupported by the proposed narrow refresh; it is not declared malformed for all TD4183 modes. Odd slots are support data for this candidate layout and never numeric state. QC is the app category and is not assigned a further clinical meaning.

This does not establish an arbitrary `2*i` traversal for larger counts, a capacity, or a stable per-record raw index.

## Chronology and latest selection

The earlier count-two observation and a later count-four observation after a normal new measurement make primary 2 a *plausible* newly added record (**INFERRED**). No before/after primary-frame comparison or cross-group meter-local time relation was recorded. The app's TD4183 handlers discard the wire `0x2B` newest-index field, and the decompiled import loops do not establish a general retrieval order. App database sorting by meter time or local row ID is not meter chronology. Whether logical index 1 is newer than 0 is **UNRESOLVED**.

| Candidate selection | Decision and failure mode |
| --- | --- |
| Maximum naive meter-local timestamp among current primaries | **Defer.** One snapshot avoids timezone conversion, but equal-minute readings, clock adjustment/reset, and unobserved cross-group order can select the wrong event. A max is a meter-clock ordering rule, not proven actual chronology. |
| Highest logical/raw index | **Reject.** Newest-index wire meaning, wrap, and index reuse remain unknown. |
| Read only the newest-looking pair | **Reject.** No index is proven newest and it would omit a possibly newer supported analyte elsewhere. |
| Require exactly one eligible primary | **Accept for the bounded current-state design.** If the complete tested-count snapshot has one valid General uric-acid primary, it is the sole eligible current-memory value; no comparison between two candidates is needed. Zero or more than one eligible primary means no state update. This does not claim it is the meter's most recent reading of any analyte, nor one outside current memory. |

The proposed rule uses existing `measurement_from_record` and `measurement_native_value` only after pair and category validation. Unsupported analytes, QC, AC, PC, and `0xFFFF` cannot become numeric state. If two uric-acid primaries are present in a count-four snapshot, the current real meter may still leave the sensor unavailable; Stage 7E did not publish index-two analyte or cross-group chronology. This is an explicit functional limit of Outcome A.

## Snapshot versus history, deduplication, and time

A full **supported-count snapshot** on every manual request avoids a durable raw-index cursor and interruption resume. It does not solve arbitrary-count traversal or historical event ingestion. The proposed snapshot uses the already validated literal plans: for count two, `1 → 0 → 1`; for count four, `3 → 0 → 1 → 2 → 3`, each raw access one `0x25` then `0x26`. Project `0x4183` is confirmed first, then one User1 `0x2B`. At most 9 or 13 application writes, respectively. No dynamic index loop or command retry is justified. A production implementation would require its own review and test gate before physical operation.

Updating one current sensor state does **not** require a collision-safe persistent record ID. A repeated manual refresh may encounter the same visible value. In-memory comparison can avoid redundant entity writes, but must never be treated as measurement-event deduplication; restart may reread the same record. Home Assistant recorder time is ingestion/state time, not meter measurement time. Historical observations, statistics backfill, persistent fingerprints, and resume still require separate identity, collision, ordering, and privacy policies. No history is persisted by this design.

Keep every selected record's minute-precision, timezone-naive `meter_local_time` separate from a timezone-aware `synchronized_at` in prospective runtime state. Do not assign UTC, a local timezone, or DST to meter time. The unique-candidate rule does not use meter time to choose among primaries. Equal or backwards meter times are therefore not silently sorted; within-pair equality may be checked only for structural consistency. A future product UI must distinguish measurement time from sync time so an old stored reading is not presented as newly measured. No new attribute or timestamp exposure is authorized by Stage 7F.

## Count and consistency gates

The initial software bound should be **exact raw counts 2 and 4**, not an invented meter capacity. Larger even counts have app-side mapping evidence but no physical traversal validation. Odd counts have unresolved grouping. Count zero means no candidate and no state update; count one, every odd count, counts above four, invalid/sentinel metadata, and any **detected** count change during a future sync must fail closed without selecting a value. No MAC, timestamp, or highest index supplies a fallback.

A second `0x2B` after traversal could detect a changed count, but cannot detect same-count overwrite or clock changes. It adds application traffic not physically validated in that position and is **not part of this proposed first sequence**. Re-reading the last slot, already validated in the fixed plans, detects change there but does not prove an atomic snapshot of all slots. A manual run while the meter is stably ON and no measurement is underway limits the practical mutation window; the residual consistency risk remains explicit. Any detected response mismatch, repeated-slot difference, disconnect, or count inconsistency must discard the new candidate and retain prior state.

## Trigger, coordinator, and failure design

| Trigger | Rank for first production attempt | Reason |
| --- | --- | --- |
| Explicit integration manual refresh while meter is manually ON | **1 — recommended** | User controls timing; the known working custom subscription path is available in the tested ON state. |
| Config-entry reload/startup sync | **2 — defer** | Meter may be off or in an unsuitable transfer state; unexpected connections and failed startup are likely. |
| Advertisement-triggered sync | **3 — defer** | Needs state detection, rate limiting, and proxy-path evidence. |
| Post-measurement automatic sync | **4 — defer** | Stage 7E's flashing state connected but failed custom notification subscription before any FORA command. Cause unknown. |
| Periodic polling | **5 — defer** | No justified cadence and would reconnect repeatedly. |

The prospective coordinator owns one per-entry lock, confirms project identity every session, reads metadata once, chooses one of the literal bounded plans, validates every response and candidate pair, produces product measurements, filters to valid General uric acid, selects only a sole eligible primary, and updates the existing in-memory sensor state only after the entire session and cleanup pass. It records privacy-safe status/error codes and a separate ingestion time. It never exposes raw frames, private address, value in logs, or a health-data fingerprint. SensorEntity remains transport-free. Connection and application exchange use the existing transport's bounded waits, poisoned-session behavior, no in-session application retry, no pairing, and deterministic cleanup.

| Condition | Proposed behavior |
| --- | --- |
| Connection/subscription failure, project mismatch, invalid metadata, malformed pair, timeout, disconnect, poisoned session, or cleanup failure | Abort; retain previous valid state; record a safe status/code; try only on a later explicit manual request. |
| Unsupported count or pair/mode mismatch | No numeric update; retain previous state; report an unsupported-snapshot status. |
| No valid General uric-acid primary, including QC-only or invalid-only snapshot | No numeric update; retain previous state; report no eligible measurement. |
| More than one eligible primary, equal-minute tie, backwards clock, or unknown order | No selection based on index or meter time. Retain previous state and report ambiguity. |
| Detected snapshot mutation or repeated-slot difference | Discard the candidate; retain prior state. |
| No previous valid state | Sensor remains unavailable. |

Retaining a previous value is a failure policy, not evidence that it is fresh. Availability and UI age semantics need explicit Stage 7G implementation review; the current `MeasurementState.replace()` would clear a value when passed an invalid measurement, so a future coordinator must call it only after a successful eligible selection. Stage 7F changes no code.

## Original Stage 7F readiness matrix (before Stage 7G)

“Ready” below means the **evidence supports a narrowly specified implementation design**, not that production code exists or that this stage authorizes BLE operation.

| Capability | Status | Evidence or blocker |
| --- | --- | --- |
| 1. Manual current uric-acid refresh at raw count 2 | **READY** | One physical primary/companion group and exact pair plan validated; accept only one valid General uric-acid primary after strict checks. No inter-record ordering needed. |
| 2. Manual current uric-acid refresh at raw count 4 | **PARTIAL** | Fixed plan and two candidate groups validated. Only a *sole* eligible uric-acid primary can be selected; two eligible primaries require chronology evidence. Index-three analyte was identified but not named in the public result. |
| 3. Manual current refresh at any even count | **NOT READY** | Larger histories, last-slot mode, empty slots, capacity, and wrap untested. |
| 4. Automatic current-state refresh | **NOT READY** | Post-measurement subscription failure, trigger/rate limits, and proxy path unresolved. |
| 5. Import all historical measurements | **NOT READY** | General traversal, chronology, event identity, and duplicate policy unresolved. |
| 6. Persistent deduplication | **NOT READY** | No collision-safe meter record ID; app content comparison can collide. |
| 7. Resume interrupted sync | **NOT READY** | No stable cursor or per-record identity. A manual current-state refresh can simply start over. |
| 8. Survive circular-buffer wrap | **NOT READY** | Capacity, head/write pointer, overwrite and index reuse unresolved. |
| 9. Import HA long-term statistics/history | **NOT READY** | Historical event times, ordering, dedup, and HA import policy remain unestablished. |

## Exact next gate

**Outcome A — a narrow manual current-state refresh is justified as a design.** Separately authorize **Stage 7G** to implement only this conditional, fixed-count current-state path: counts 2 and 4; literal validated index plans; exactly one eligible General uric-acid primary; explicit user trigger; no timestamp/index ordering, automatic trigger, historical import, persistent dedup, cursor, polling, or background task. Stage 7G must review the snapshot-consistency residual risk and failure/availability semantics before any real deployment. If the observed count-four state has two eligible uric-acid primaries, it must leave the sensor unchanged and propose a separate bounded cross-group chronology experiment rather than guessing which is newer. No Stage 7G implementation or physical operation occurs in Stage 7F.

## Stage 7G update

The separately authorized Stage 7G work is a bounded chronology evidence probe, not the conditional production refresh proposed in this Stage 7F design. It requires exactly four slots and compares only validated raw primaries 0 and 2 privately. Production current-state sync remains a later gate.

## Stage 7G2 reassessment of the Stage 7F design

The real Stage 7G action confirmed two valid General uric-acid primaries in one four-slot snapshot. Their parsed meter-local times differed, and raw index **0** was later than raw index **2** (**LIVE-CORROBORATED**). This directly rejects highest-raw-index selection for that snapshot. It supports selecting the **strict maximum meter-local timestamp among eligible primaries in a complete, bounded current snapshot** as a prospective *meter-clock* policy. It does not prove actual event ordering if the meter clock was reset or changed, or ordering across separate snapshots. Preserve the original naive meter-local time separately from ingestion time.

| Manual current-state case | Revised design readiness | Strict rule |
| --- | --- | --- |
| Raw count 2 | **READY for Stage 7H implementation review** | Validate the fixed `1 → 0 → 1` plan and its sole eligible General uric-acid primary at raw 0. No cross-primary comparison is needed. |
| Raw count 4 | **READY conditionally for Stage 7H implementation review** | Validate the complete fixed `3 → 0 → 1 → 2 → 3` plan, both groups, and eligible General uric-acid primaries. Select the sole eligible primary if there is one; if there are two, select only the one with a strictly greater meter-local timestamp. Equal-minute timestamps are ambiguous: retain the previous valid state and report a safe ambiguity status. Zero eligible primaries produce no update. |
| Other counts, historical import, automatic refresh, dedup/resume | **NOT READY** | Larger or odd counts, wrap/reset behavior, and durable record identity remain unresolved. |

The timestamp maximum is used **only within the single current snapshot**, with the meter clock treated as the ordering source. Raw index, the wire `0x2B` newest-index label, and sync/ingestion time are not tie-breakers. A plausible but incorrect meter clock is a residual risk; Stage 7H must document what its displayed current value means and never portray the meter-local time as an absolute UTC event time.

A second `0x2B` after traversal could detect a changed count, but not a same-count overwrite or clock adjustment. It would add an unvalidated command placement and is **not required for the first manually triggered, fixed-count implementation** if the meter is normally ON, no new measurement is underway, history arrows are untouched, and the existing repeated-last-slot consistency check succeeds. Any inconsistency detected within the fixed plan must discard the candidate and retain prior state. Revisit an after-traversal metadata read if physical mutation becomes a concrete concern.

The initial trigger remains **explicit manual refresh only**: turn the meter ON normally, do not press history arrows, then request Home Assistant refresh. The user observed that history-button browsing stops the flashing Bluetooth light, and an earlier post-measurement flashing state allowed connection but failed custom subscription; the internal reasons are unknown. Startup, advertisement, post-measurement automatic sync, and polling remain unsupported.

**Original next gate, now complete:** Stage 7H implemented and the user physically validated the bounded manual current-state refresh. **Current next proposed gate:** Stage 8 offline/synthetic/design-first refresh hardening and product-behavior review. No historical import, persistent dedup, resume, polling, or automatic trigger is authorized by this review.
