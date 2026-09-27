# Stage 7D — general TD4183 traversal and deduplication evidence review

**Status:** offline review complete. The evidence supports the TD4183 app's count conversion and per-record access, but does not establish chronological meter order, a circular-buffer rule, a durable record ID, or safe resume. Production synchronization remains gated. No meter operation or runtime change occurred in Stage 7D.

## Evidence and limits

- Retained private iFORA HM 1.7.6: `z3/c.java` (TD4183 handler), `z3/a.java` (base handler), `b4/a.java` (metadata parser and request builders), `a4/r.java` (metadata model), `com/foracare/tdlink/hm/ImportMeterRecordService.java` (import), `n0/d.java` (medical-record lookup), and `m0/a.java` (database schema).
- Retained private iFORA HM 1.7.9 equivalents: `d2/C0428c.java`, `d2/AbstractC0426a.java`, `f2/a.java`, `e2/r.java`, `com/foracare/tdlink/hm/ImportMeterRecordService.java`, `X/d.java`, and `W/C0152a.java`. These are source locations for review, not copied source. The 1.7.9 import thread failed decompilation; the 1.7.6 import thread decompiled with contradictory branches. Neither is reliable enough to establish a complete import loop.
- The retained private GD82 app-import capture was previously examined in place and documented in [Stages 2C](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) and [7A](STAGE7A_HISTORY_TRAVERSAL_DESIGN.md). Its indexed request order was `1 → 0 → 1`. The capture has one tested two-slot state; it cannot establish larger histories.
- The user-run [Stage 7B](STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) and [Stage 7C](STAGE7C_SEMANTIC_PAIR_CONFIRMATION.md) actions independently confirmed raw count two, valid pairs in that fixed order, repeated index-one equality and semantics, and clean cleanup. Index zero was General uric acid with a valid value; index one was QC hematocrit with invalid `0xFFFF`. No private values, times, identifiers, or frames are recorded here.

The labels **STATIC-ANALYSIS-SUPPORTED BOTH VERSIONS**, **STATIC-ANALYSIS-SUPPORTED ONE VERSION**, **LIVE-CORROBORATED**, **INFERRED**, and **UNRESOLVED** below distinguish what the app does from what the meter guarantees.

## Per-version call flow and traversal pseudocode

Both handlers have this independently visible structure (**STATIC-ANALYSIS-SUPPORTED BOTH VERSIONS**):

```text
metadata(user):
    raw = parse_unadjusted_0x2B(user)  # raw count; wire field called newest index
    if raw.count == 0: return raw
    if mode unknown:
        last = read_pair(raw.count - 1, user)
        mode = MULTI if last is hematocrit with QC category else SINGLE
    logical_count = raw.count if SINGLE else floor(raw.count / 2)
    return metadata(count=logical_count, reported_newest=logical_count - 1)

record(logical_index, user):
    if mode unknown: metadata(user)
    primary_index = logical_index if SINGLE else 2 * logical_index
    primary = read_pair(primary_index, user)  # one 0x25 and one 0x26
    if MULTI and primary is not already a hematocrit record:
        companion = read_pair(primary_index + 1, user)
        conditionally attach hematocrit companion fields to primary
    return primary
```

The pseudocode describes the handler, **not** a verified general meter traversal or an authorized request loop. The actual multi branch excludes another primary class from attachment and does not prove every possible pair layout. The handler accepts a caller's logical index; it does not itself iterate all records.

| Question | 1.7.6 | 1.7.9 | Evidence conclusion |
| --- | --- | --- | --- |
| `0x2B` | `b4/a.java` parses unsigned little-endian bytes 2–3 as raw count and 4–5 as the field labeled newest index; TD4183 calls the unadjusted parser. | Same in `f2/a.java`. | **STATIC-ANALYSIS-SUPPORTED BOTH VERSIONS.** |
| Empty count and mode probe | Zero returns; otherwise read raw `count - 1` once to classify single/multi mode. | Same. | **STATIC-ANALYSIS-SUPPORTED BOTH VERSIONS.** Empty behavior on the meter remains untested. |
| Logical count / reported newest | Single: raw count; multi: integer raw count divided by two; reported newest = logical count minus one. | Same. | **STATIC-ANALYSIS-SUPPORTED BOTH VERSIONS.** The wire newest field is discarded by this TD4183 return path. |
| Logical-to-raw access | Single `i`; multi primary `2*i`, possible companion `2*i+1`; each raw access is one `0x25`/`0x26` pair. | Same. | **STATIC-ANALYSIS-SUPPORTED BOTH VERSIONS**; only indexes zero and one are **LIVE-CORROBORATED**. |
| Companion attachment | Hematocrit companion may attach without a visible time-equality guard; invalid sentinel does not create a usable secondary number. | Hematocrit companion attaches only when its meter-local time equals the primary time; invalid sentinel does not create a usable secondary number. | **STATIC-ANALYSIS-SUPPORTED ONE VERSION** for each differing guard. No universal companion rule follows. |
| Import loop start/end/step | Decompiled thread appears to initialize logical index zero and call `d(index, user)` after a count query, but contains a visibly reversed loop condition and duplicated exception branches. | Thread body is omitted by the decompiler. | Complete bounds, step, and retrieval order **UNRESOLVED**. |
| Import/database order | Visible 1.7.6 code invokes a local existence lookup before import. Database read APIs can order by measurement time or local row ID. | Existence helper and DB ordering are visible, but the import thread call chain is not. | App display/database ordering is not proof of meter chronology or wire retrieval order. |
| Capacity, wrap, resume | No TD4183 capacity constant, modulo rotation, or proven cursor in the traced handler. | Same. | **UNRESOLVED**, not evidence that the meter is linear. |

The `0x2B` **raw count** is treated by the app as a number of addressable raw entries, not a capacity. In multi mode the app divides it to obtain logical count; the real two-slot result includes the QC hematocrit companion in the raw count (**LIVE-CORROBORATED** for that state). An odd multi count is truncated by integer division in the app; handling of any such physical state is **UNRESOLVED**. Zero and sentinel handling in the parser differ between the shared parser's adjusted and unadjusted modes; the TD4183 path uses only unadjusted values. The builder's `0..65535` integer range is a wire limit, not meter capacity.

The `0x2B` **newest-index wire field** is parsed and logged by both shared parsers, but neither TD4183 handler uses it to choose the last-slot probe, rotate a list, or calculate the returned newest index. Both create a new metadata object whose newest is `logical_count - 1`. Its real meter meaning could be a last slot, head, write pointer, or something else: **UNRESOLVED**. Calling the field “newest” does not prove any of those interpretations.

## Ordering, grouping, and memory changes

- **Retrieval order:** the one private import and the bounded real tests have `1 → 0 → 1`, explained by the last-slot mode probe followed by logical index zero and its possible companion (**LIVE-CORROBORATED** for count two). The general caller loop is **UNRESOLVED**. The older decompilation's inverted branch must not be repaired by assumption.
- **Chronological order:** whether increasing raw or logical index means newer is **UNRESOLVED**. The app database has queries ordered by meter timestamp descending and alternatives ordered by its local `_id`; those are presentation/database policies, not a proven meter memory order. Meter-local minute precision has no established timezone and can tie or change after clock adjustment.
- **Companion grouping:** in the multi branch, a logical primary is read at `2*i`, with a possible hematocrit companion at `2*i+1`. A primary already classified as hematocrit follows a special path. The physical count-two companion is hematocrit/QC/invalid; this does not prove every companion is hematocrit, invalid, QC, or present, nor that it is an independent health measurement. The app versions disagree on the time-equality guard.
- **Capacity, full memory, wrap, deletion/reset:** no TD4183 handler logic reviewed here identifies a fixed capacity, modulo index, head pointer, overwrite rule, empty-slot response, or effect of a new reading, full memory, clear operation, factory reset, or firmware update. These remain **UNRESOLVED**. The app database's `rec_deleted` flag describes local records; it does not establish meter deletion. A raw index cannot be assumed stable over time.

## App database and transmitted flag

Both app versions have a `medical_record` table with an auto-increment `_id` and no unique constraint on imported type/time/value fields in the reviewed schema. That `_id` is an **app-local row ID**, not a meter record ID. Their `n0/d.java` and `X/d.java` existence helpers first query by demo status, measurement type, and timestamp, then compare three stored numeric values within a tolerance and a normalized raw-data text field. They distinguish a matching deleted row. The visible 1.7.6 import thread calls this lookup for parsed records; the 1.7.9 import thread is unavailable, although its equivalent wrapper and helper remain present. This is a local content comparison (**STATIC-ANALYSIS-SUPPORTED BOTH VERSIONS** for the helper, **ONE VERSION** for the visible import call), not a protocol-provided unique record key. The reviewed lookup does not filter by meter profile, raw slot index, or a meter record ID. A same-minute, same-value collision, or a match across meter profiles, is possible in principle (**INFERRED**); observed collision frequency is unknown. The app does not simply insert every visible 1.7.6 record, but its complete stop/re-download strategy is **UNRESOLVED** because of decompiler damage.

The `0x25` transmitted bit is parsed into app record objects in both versions. The reviewed TD4183 mode/record handlers and visible 1.7.6 import existence lookup do not use it as an index cursor or unique key. Whether another opaque import path filters on it, whether it changes after transfer, and whether the meter mutates it are **UNRESOLVED**. No state-changing FORA command or write behavior is inferred from that flag.

## Deduplication candidates and resume

| Candidate | Stability and collision issue | Decision |
| --- | --- | --- |
| Raw index, alone or with current meter identity | May be reused, shifted, or wrapped; capacity and reset semantics are unknown. | Unsafe as durable ID or resume cursor. |
| Meter-local timestamp alone | Minute precision, unknown timezone, ties, and clock changes. | Unsafe. |
| Analyte + category + timestamp + raw value | Distinct same-minute same-value readings can collide; scale/unit and companion behavior vary. | Not a collision-safe key. |
| Add transmitted flag, code number, or companion fields | No proven uniqueness; transmitted bit may change and code/companion semantics are incomplete. | Does not establish identity. |
| Add canonical meter identity | Prevents cross-meter mixing only; cannot distinguish within-meter collisions. | Necessary scope if future storage exists, insufficient by itself. |
| Bounded content fingerprint | Could avoid reprocessing identical observations in a short window, but cannot prove two identical-content observations are the same event or survive wrap/reset safely. A persisted fingerprint would be sensitive health metadata. | Candidate only; no retention window or hash is justified yet. |

**Outcome C — safe deduplication remains unresolved.** No record key, content fingerprint, recent-window cache, last-import marker, or resume cursor is implemented or persisted. The app's approximate local lookup must not be promoted into a Home Assistant collision-safe identity. Interruption recovery would require a separately justified reread and duplicate policy; the existing two-slot evidence does not define one.

## Production synchronization readiness

| Requirement | Decision | Reason |
| --- | --- | --- |
| Retrieve all current records | **NO** | Only count two and raw indexes zero/one are physically proven; general count, empty slots, pairing, and bounds are not. |
| Determine chronologically newest supported record | **NO** | Wire newest meaning and raw/logical chronological order are unresolved; meter time can tie or change. |
| Avoid duplicate historical observations | **NO** | No collision-safe meter record ID or key; app lookup is only a fallible content match. |
| Resume after interruption | **NO** | No proven stable raw index, cursor, or safe reread policy. |
| Survive full memory, wrap, deletion, or reset | **NO** | Capacity, overwrite, slot reuse, and reset behavior are unresolved. |

## Exact next proposed gate: Stage 7E

Seek separate authorization for a **read-only, development-only, fixed four-slot observation** if the meter naturally reaches a raw count of four in normal use. Do not ask the user to take a new health measurement for the experiment. First compare a private before/after `0x2B` raw-count and wire-newest field classification. After normal GD82 identity confirmation, **only if raw count is exactly four**, read User1 raw indexes `3 → 0 → 1 → 2 → 3`, each with exactly one `0x25`/`0x26` pair; `3` is the last-slot mode probe and final `3` tests same-session stability. Stop after metadata for any other count. At most five pairs, no loop, retries, state change, entity update, or health-data output. Return only validity, analyte/category/sentinel classification, private equality results for repeated slots, and privacy-safe relationships between the parsed meter-local times (never the times or values themselves). A separately reviewed design must decide the exact time-comparison booleans before implementation, handle the two app versions' companion-time disagreement, and ensure no per-record fingerprint leaves the action. A count-four success would test another bounded state; it would **not** establish capacity, wrap, deletion/reset, or a collision-safe dedup key. Those require later evidence gates. No Stage 7E code or physical operation is authorized by this document.
