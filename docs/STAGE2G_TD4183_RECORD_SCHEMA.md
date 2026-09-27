# Stage 2G — TD4183 offline record schema and parser

**State:** Evidence-backed offline parser implemented for the supported `0x25` and `0x26` fields. Stage 2F's bounded physical probe succeeded with the GD82 ON, retrieving User1/raw-index-zero frames without `0x33`; it decoded no health data. Stage 2G performed no BLE operation and did not change the development action, transport, synchronization, or entities. Private app source and HCI capture remained outside Git.

## Evidence provenance and parser path

- The retained private iFORA HM 1.7.6 APK and 1.7.9 XAPK decompilations were inspected in place. Their mirror provenance, hashes, signing evidence, and authenticity limit are recorded in [Stage 2B](STAGE2_IFORA_HM_STATIC_ANALYSIS.md). Decompiled source was not copied into this repository.
- In 1.7.9, the `TD4183` factory maps to `d2/w.java` → `d2/C0428c.java` → `d2/AbstractC0426a.java`. `C0428c.k()` obtains indexed `0x25` then `0x26` responses and calls `f2/a.L()` → `M()`; `f2/a.e()` decodes the first response's time. The relevant private source locations are `d2/C0428c.java` around lines 118–187 and `f2/a.java` around lines 225–300, 684–750, and 797–820.
- In 1.7.6, `z3/u.java` → `z3/c.java` → `z3/a.java` follows the same pair. `z3/c.k()` calls `b4/a.L()` → `M()`; `b4/a.e()` decodes time. Relevant private locations are `z3/c.java` around lines 113–183 and `b4/a.java` around lines 225–350, 690–750, and 796–820. Decompiled 1.7.6 `M()` has duplicated/awkward control flow, so the clearer 1.7.9 branch and 1.7.6 enum/consumer behavior were considered together for category dispatch.
- Both versions' record base classes (`e2/b.java`, `a4/b.java`) classify raw `0xFFFF` as invalid. The multifunction handlers probe the last slot for a QC hematocrit companion when deciding single versus multi-parameter storage. The 1.7.9 handler omits the secondary hematocrit attachment when that raw field is `0xFFFF`.
- The retained private successful GD82 HCI import capture was read in place with a local btsnoop/ATT inspection. It contains valid indexed `0x25`/`0x26` request/response pairs for indexes `1 → 0 → 1`, plus a later app `0x2F` exchange. All three `0x25` response payloads matched. The two index-one `0x26` payloads matched; index zero differed at offsets 2, 3, and 5. No raw response, health value, date, address, or private identifier is published here.
- The user-supplied privacy-safe Stage 2F result independently confirms Home Assistant retrieved valid User1/index-zero `0x25`/`0x26` frames with the meter ON. It did not expose payload bytes. The Stage 2C private import summary corroborates uric-acid displayed value = parsed raw / 10, but no separate displayed-value/time specimen was available here for a second numeric/time comparison.

## `0x25` response byte map

Offsets are zero based. The first response is an eight-byte checksummed frame. The original meter-local fields have **minute precision**; seconds and timezone are not present in this path.

| Offset/bits | Meaning | Evidence class |
| --- | --- | --- |
| 0 | `0x51` prefix | **LIVE-CORROBORATED** envelope |
| 1 | `0x25` command echo | **LIVE-CORROBORATED** |
| 2 bits 0–4 | Day of month | **STATIC-ANALYSIS-SUPPORTED**, both versions |
| 2 bits 5–7; 3 bit 0 | Month, low three bits plus high bit | **STATIC-ANALYSIS-SUPPORTED**, both versions |
| 3 bits 1–7 | Year offset from 2000 | **STATIC-ANALYSIS-SUPPORTED**, both versions |
| 4 bits 0–5 | Minute | **STATIC-ANALYSIS-SUPPORTED**, both versions |
| 4 bits 6–7 | Uninterpreted; retained in raw payload | **UNRESOLVED** |
| 5 bits 0–4 | Hour, 24-hour field in app calendar | **STATIC-ANALYSIS-SUPPORTED**, both versions |
| 5 bit 5 | Uninterpreted; retained | **UNRESOLVED** |
| 5 bit 6 | Reading transmitted flag in the app parser | **STATIC-ANALYSIS-SUPPORTED**, both versions |
| 5 bit 7 | Uninterpreted; retained | **UNRESOLVED** |
| 6–7 | `0xA5` response marker; sum of bytes 0–6 modulo 256 | **LIVE-CORROBORATED** envelope |

The app uses `Calendar.getInstance()` on the phone to turn these fields into a Java `Date`; that does **not** establish a timezone stored by the meter. `MeterLocalTimestamp` retains year/month/day/hour/minute without timezone or invented seconds. Its optional conversion returns a naive Python `datetime`. Java Calendar is lenient; the Python parser rejects invalid month/day/hour/minute encodings rather than silently normalizing them. No distinct time sentinel was found in this TD4183 call path. The private capture's three decoded date/time field sets were calendar-valid; the actual timestamp was not published or independently checked against a displayed time.

## `0x26` response byte map

| Offset/bits | Meaning | Evidence class |
| --- | --- | --- |
| 0–1 | `0x51` prefix; `0x26` command echo | **LIVE-CORROBORATED** envelope |
| 2–3 | Raw unsigned 16-bit measurement, little endian | **STATIC-ANALYSIS-SUPPORTED**, both versions; private specimen was parsed but not compared to a separately available displayed number |
| 4 | App labels this an ambient value; unit/physical meaning unresolved. Parser preserves it as auxiliary byte. | Byte position **STATIC-ANALYSIS-SUPPORTED**; physical meaning **UNRESOLVED** |
| 5 bits 0–5 | App's code number; overlaps the analyte selector. Parser preserves the numeric field without assigning a separate meaning. | **STATIC-ANALYSIS-SUPPORTED**, both versions |
| 5 bits 2–5 | Analyte selector. Known wire codes: `0` General, `6` hematocrit, `7` ketone, `8` uric acid, `9` cholesterol, `11` haemoglobin, `12` lactate, `13` triglyceride. Other codes stay unidentified. `General` is not labeled glucose without further context. | **STATIC-ANALYSIS-SUPPORTED**, both versions; uric-acid branch **LIVE-CORROBORATED** privately at index zero |
| 5 bits 6–7 | App-mapped record category: `0` General, `1` AC, `2` PC, `3` QC. The parser preserves QC as a category only; control-solution meaning or policy is unresolved. Expansion/clinical meaning of AC/PC is not assigned here. | **STATIC-ANALYSIS-SUPPORTED**, clearest in 1.7.9; QC branch **LIVE-CORROBORATED** privately at index one |
| 6–7 | `0xA5` response marker; checksum | **LIVE-CORROBORATED** envelope |

Raw `0xFFFF` is the app's invalid-value sentinel, confirmed in both record base classes. The parser flags it and the uric-acid scaling helper rejects it. The private index-zero pair decodes as uric acid, General category, non-sentinel raw value, and a valid meter-local time. The repeated index-one pair decodes as hematocrit, QC category, and invalid sentinel, consistent with the app's multi-parameter last-slot probe. These private checks publish classifications only, never the numeric value or time. The index-one QC/sentinel is not treated as a second valid health measurement.

## Semantics and remaining limits

| Question | Result |
| --- | --- |
| Can `0x25`/`0x26` identify a record without `0x2F`? | **Yes for the app-mapped analyte selector and raw value in this TD4183 path.** The private index-zero frame selects uric acid directly from `0x26` byte 5. `0x2F` supplies category-specific range metadata in the shared handler and is not needed to extract this pair or identify that type. It remains physically untested from Home Assistant. |
| Uric-acid scaling/unit | Prior Stage 2C private import corroborates displayed value = raw / 10 for uric acid; no other analyte scaling or unit is assigned. The parser returns raw integer and identity separately; scaling remains contextual. |
| Control/status | QC category and transmitted flag are decoded. Whether QC means a control solution, any control-solution policy, other reserved bits, low code bits, and AC/PC clinical interpretation remain unresolved. |
| Invalid data | `0xFFFF` raw value is flagged invalid. Invalid time fields are rejected by a deliberate strict parser policy. Unsupported analyte codes remain numeric with `analyte=None`. |
| Multi-parameter behavior | The private `1 → 0 → 1` sequence and app branch support an index-one hematocrit QC/sentinel companion and index-zero uric-acid record for this capture. General pairing/count behavior across other meter states remains unresolved. |
| Timestamp and timezone | Meter-local fields are preserved at minute precision. `timezone_unknown = true` in design terms; no UTC conversion or ingestion-time substitution occurs. |

The offline implementation adds only immutable parser structures to Home Assistant/Bleak-independent `protocol.py`; it does not change BLE requests, the privacy-safe development action, or production behavior. All tracked fixtures are synthetic (including a future date and artificial values). Private validation ran only in memory and reported classifications, not raw bytes or the real measurement.

**Exact next gate:** review Stage 2G evidence and parser, then separately authorize Stage 3's wider sanitized fixture/record-model work or a focused evidence follow-up for the unresolved units, reserved flags, and multi-parameter semantics. Any physical `0x2F` query, real decoded-result exposure, or production synchronization needs its own authorization.
