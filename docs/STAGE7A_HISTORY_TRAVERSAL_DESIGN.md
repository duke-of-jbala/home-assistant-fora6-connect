# Stage 7A — offline history traversal and deduplication review

**Decision:** Stage 7A is complete as an offline evidence review. General multi-record traversal and a collision-safe record identity are not established. No production synchronization, indexed request builder, history loop, persistence, or physical test was added. Stage 7 stops here pending a separately authorized bounded Stage 7B probe.

## Sources and provenance

- Retained private iFORA HM 1.7.9 decompilation: TD4183 factory `d2/w.java`, handler `d2/C0428c.java` (especially `d()`/`e()`/`k()`), base `d2/AbstractC0426a.java`, and command parser/builders `f2/a.java`. The retained 1.7.6 equivalents are `z3/u.java`, `z3/c.java`, `z3/a.java`, and `b4/a.java`. The provenance and authenticity limit of these app specimens are in [Stage 2B](STAGE2_IFORA_HM_STATIC_ANALYSIS.md). Decompiled source remains outside Git.
- Retained private successful GD82 app-import HCI capture, previously summarized without private response bytes in [Stage 2C](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md), [Stage 2F](STAGE2F_TD4183_RECORD_PROBE.md), and [Stage 2G](STAGE2G_TD4183_RECORD_SCHEMA.md). Stage 7A rechecked the capture in place: its one `0x2B` response is structurally consistent with the app's last-slot probe, and its paired indexed request order was `1 → 0 → 1`. The previously private-classified index-one pair is hematocrit/QC/invalid sentinel, and index zero is valid General uric acid. No private metadata number, health value, timestamp, address, or raw response is published.
- User-run Stage 2F and Stage 4 regressions physically proved only the Home Assistant User1 raw-index-zero pair after wake, project confirmation, and `0x2B`. They did not establish multi-index traversal.
- The tracked `protocol.py`, `models.py`, and synthetic tests define single-slot parsing and record pairing. Their existing request constructors are limited to raw index zero; tests are not evidence of wider physical behavior.

## `0x2B` count and index model

Both app versions parse a command-matched `0x2B` response as two unsigned little-endian 16-bit quantities: **raw storage count** from response bytes 2–3 and an app-labeled **newest index** from bytes 4–5. The TD4183 handler calls the *unadjusted* parser. Other shared handlers can request an adjusted `+1` interpretation, which must not be applied to TD4183. This field layout and call path are **STATIC-ANALYSIS-SUPPORTED**; the metadata exchange itself is **LIVE-CORROBORATED** on the tested GD82. The broader meaning of “newest index” under wrap, deletion, or clock reset is **UNRESOLVED**.

The indexed request builders place the raw index, unsigned little endian, in bytes 2–3; no `+1` is applied. Both app versions accept the wire integer range `0..65535`, which is a builder limit, **not** an established meter capacity or valid storage range. Raw index zero was **LIVE-CORROBORATED** from Home Assistant; index one appears in the private app capture. Empty slots, out-of-range responses, actual capacity, and circular-buffer behavior are **UNRESOLVED**. A count of zero causes the TD4183 handler to return without a last-slot probe, but the handling of all sentinel/count combinations on a physical meter is untested.

## TD4183 logical records and pair retrieval

In both versions, TD4183 count handling first reads the raw `0x2B` count. If nonzero and storage mode is unknown, it reads the last raw slot (`raw_count - 1`) through exactly one `0x25` then one `0x26`. A last-slot hematocrit record in app category QC selects `MULTI_PARAMS`; otherwise the handler selects `SINGLE_PARAMS`. In single mode the app reports raw count as logical count and maps logical index to the same raw index. In multi mode it reports integer `raw_count / 2` and maps logical index `i` to raw index `2*i`, optionally reading `2*i + 1` as a hematocrit companion. This is **STATIC-ANALYSIS-SUPPORTED** in 1.7.6 `z3/c.java` and 1.7.9 `d2/C0428c.java`, around their `d()` and `e()` methods. It does not prove that every GD82 history or analyte is paired, that odd counts are safe, or that the last-slot heuristic always classifies storage correctly.

Both versions' low-level `k(raw_index, User1)` obtains one `0x25`/`0x26` pair. In multi mode, 1.7.9 attaches a secondary hematocrit record only if its meter-local time matches the primary record's time; 1.7.6 does not make that equality check in the decompiled branch. Both distinguish the invalid `0xFFFF` secondary value. Thus cross-version agreement covers count parsing, mode heuristic, logical-to-raw mapping, and low-level pair order; **cross-version disagreement** exists on the timestamp guard for secondary attachment. The captured index-one QC/invalid-sentinel pair is consistent with a companion in this tested state, not proof of a universal companion rule. QC remains only an app category; no control-solution meaning is assigned.

The private `1 → 0 → 1` order is consistent with the app's last-slot mode probe followed by logical index zero plus a possible companion read. It does not itself prove the precise call-site reason for the final index-one access. The 1.7.6 `ImportMeterRecordService` decompiled loop contains visibly inconsistent branch text, so it cannot independently establish complete import order. Neither app handler requires a new application command *inside* `k()` between successive raw pairs; that does not prove no other prerequisite in other meter states. User1 is the observed selector and the app import's default for this TD4183 path; other user profiles have not been tested.

## Traversal and latest-value decision

No general order is safe to deploy. The app's logical indices start at zero, but whether increasing logical index means older or newer data under all modes is **UNRESOLVED**. The `0x2B` parser labels one field “newest index,” but the TD4183 handler returns `logical_count - 1` as its reported logical newest value and does not establish circular-buffer wrap behavior. A highest raw index must not be assumed to be the latest measurement. Comparing meter-local naive timestamps cannot safely resolve clock changes, ties, or resets. A future entity update must select the latest valid General uric-acid record under a proven ordering rule; no such multi-record rule is implemented now.

## Deduplication and resume decision

No durable record identifier is present in the proven `0x25`/`0x26` schema. Raw index might be reused or shifted when storage wraps. Meter-local minute precision can collide. Two distinct measurements can also share analyte, category, raw value, transmitted flag, and meter-local minute; a content fingerprint of those fields would then collapse them. Adding serial to such a key scopes it to a meter but does not remove within-meter collisions. Including raw index might distinguish a pair temporarily but could change its identity after wrap. Consequently, a content fingerprint is only a **candidate**, not an established deduplication key. No fingerprint, cursor, health history, raw frame, or sync timestamp is persisted by Stage 7A; resume semantics are **UNRESOLVED**. Future work must state the collision policy explicitly before storing or suppressing observations.

## Safe follow-up: separately authorized Stage 7B

Propose one development-only, manually invoked, privacy-safe probe against the tested GD82 with the meter ON. It would use the existing Home Assistant transport, session poisoning, one write per exchange, and deterministic cleanup. The exact proposed application sequence is:

1. `0x22` wake and `0x24` project query; require `0x4183`.
2. One User1 `0x2B`; proceed **only if raw count is exactly two**. Treat any other count, invalid metadata, or disconnect as a clean stop without indexed reads.
3. User1 raw index **one**: one `0x25`, then one `0x26`.
4. User1 raw index **zero**: one `0x25`, then one `0x26`.
5. User1 raw index **one** again: one `0x25`, then one `0x26`.
6. Stop notifications and disconnect. At most three record pairs; no record loop, command retry, `0x2F`, `0x33`, pairing, RACP, or production state update.

The probe would return only frame/command validity, index acceptance, app-mapped analyte/category/invalid-sentinel classifications, whether index-one repeated identically, and whether companion meter-local fields match **as booleans**, without raw bytes, values, dates, serial, address, or hashes. The repeated index-one read checks the app-captured pattern but does not prove general traversal. If the count gate fails, a new evidence review is required before changing the probe's bounds. A later separately authorized gate must decide how to test larger histories, wrap, latest ordering, and deduplication before production sync.

**Stage 7B follow-up:** [the bounded development action](STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) now implements this exact count-two, `1 → 0 → 1` plan with synthetic tests only. **Exact next gate:** controlled user-run physical validation and separate review of the sanitized result. Stage 7 production synchronization remains blocked by general traversal, latest ordering, and deduplication uncertainty.
