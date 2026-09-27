# Stage 2G — TD4183 offline record-schema evidence review

**State at 2026-09-27 review:** Stage 2G was authorized for offline analysis. The user requested that parser implementation pause until the actual retained 1.7.6/1.7.9 decompilation directories are located. The previously suggested private workspace path did not exist in this environment, and the durable notes do not preserve the actual paths. The retained private HCI import capture was available and inspected in place; it was not copied into Git. Exact field extraction cannot be established from the capture and sanitized repository notes alone. No semantic record parser or new BLE operation was performed.

## Stage 2F physical closure

The user-supplied privacy-safe result from the corrected bounded probe on the GD82 **with the meter ON** confirms valid command-matched `0x2B` metadata and User1/raw-index-zero `0x25` and `0x26` responses after the `0x22`/`0x24`/`0x4183` identity gate. Cleanup succeeded. The probe sent no `0x33`, so it was not required for this bounded read in the tested meter state. It decoded no analyte, value, or timestamp, and no production synchronization exists. Earlier wake-write and subscription failures stopped before record commands.

## Evidence and call paths available at this checkpoint

| Source | Provenance and access | Bounded conclusion |
| --- | --- | --- |
| iFORA HM 1.7.6 and 1.7.9 | Mirror specimens and authenticity limits are recorded in [Stage 2B](STAGE2_IFORA_HM_STATIC_ANALYSIS.md). The exact retained decompilation paths were not preserved in durable notes; a suggested private workspace path was absent here. | Prior Stage 2B/2F notes trace the TD4183 handler and request construction, but the response parser cannot be rechecked byte by byte here. |
| 1.7.9 TD4183 path | Prior Stage 2F static notes: factory `g2/a.java` → `d2/w.java` → `d2/C0428c.java` → `d2/AbstractC0426a.java`; builder `f2/a.java`; large import thread required JADX fallback. | The low-level raw-slot method pairs `0x25` and `0x26` for an index. The shared handler also queries category ranges with `0x2F`. No exact record payload fields are published in the notes. |
| 1.7.6 TD4183 path | Prior Stage 2F static notes: `z3/u.java` → `z3/c.java` → `z3/a.java`; builder `b4/a.java`. | It agrees with 1.7.9 on User1 selector placement, raw index placement, paired retrieval, and the `0x2B` raw-count parsing previously documented. Record response field extraction is not available for cross-version comparison. |
| Private Stage 2C HCI capture | A patched, locally re-signed 1.7.6 research app imported an existing uric-acid record; [sanitized capture summary](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) is tracked, raw capture is not. The retained successful import capture was privately inspected during this review. | Valid eight-byte `0x25`/`0x26` request/notification pairs occurred for raw indexes `1 → 0 → 1`. All three `0x25` response payloads were byte-identical. The first and third `0x26` response payloads were identical; the index-zero payload differed from them at response offsets 2, 3, and 5. A `0x2F` request/response occurred later in the app import. These are byte-comparison observations only, with no published payload bytes or field meanings. The prior private import summary associates `0x25` with time, `0x26` with measurement/analyte data, and uric-acid display scaling with raw / 10. |
| Stage 2F physical result | User-supplied semantic Home Assistant action result, recorded in [Stage 2F](STAGE2F_TD4183_RECORD_PROBE.md). | Both record-part frames passed envelope/checksum/command validation. It does not expose or validate field positions. |
| Current protocol and synthetic tests | `custom_components/fora6_connect/protocol.py` and `tests/test_protocol.py`. | Eight-byte envelope and checksum, record request constructors, slot count, and contextual uric-acid scaling only. No record-part decoder exists. |

The prior notes establish cross-version agreement for the **request path**. They do not establish agreement or disagreement about the exact `0x25`/`0x26` **response parser**. The retained HCI capture was inspected privately, but no separate known-result value/timestamp specimen path was recorded, so exact semantic decoding could not be validated against the displayed result in this environment. No private specimen bytes, value, or timestamp were copied into Git.

## Response byte-field map supported now

The maps below are for already validated eight-byte response frames. They identify only the common envelope and opaque command-specific payload. Byte numbering is zero based. A valid frame does not imply a valid semantic record.

| Offset | `0x25` response | `0x26` response | Evidence class |
| --- | --- | --- | --- |
| 0 | `0x51` frame prefix | `0x51` frame prefix | **LIVE-CORROBORATED** by captured framing and successful Stage 2F validation. |
| 1 | `0x25` command echo | `0x26` command echo | **LIVE-CORROBORATED** by command-matched Stage 2F frames. |
| 2–5 | Four opaque payload bytes; prior summary calls them time related. All three observed payloads were identical. Exact year/month/day/hour/minute/second bits, status, and sentinels are **UNRESOLVED**. | Four opaque payload bytes; prior summary calls them measurement/analyte related. The two index-one payloads matched; index zero differed at offsets 2, 3, and 5. Exact numeric, analyte, subtype, status, and control fields are **UNRESOLVED**. | Payload presence and byte-comparison pattern are **LIVE-CORROBORATED**; broad purpose is **STATIC-ANALYSIS-SUPPORTED** by earlier notes and the private app import. Assigning meanings to changed positions would be **INFERRED** and is not implemented. |
| 6 | `0xA5` response marker | `0xA5` response marker | **LIVE-CORROBORATED** by the captured envelope and Stage 2F frame validation. |
| 7 | Sum of bytes 0–6 modulo 256 | Same | **LIVE-CORROBORATED** by captured framing and Stage 2F validation. |

### Semantic decisions

| Question | Current result | Classification |
| --- | --- | --- |
| Exact date and time packing; seconds; invalid/sentinel values | Undetermined. No timestamp parser or invented UTC conversion. Meter-local time and later ingestion time must remain separate. `timezone_unknown = true` is the required future design stance unless evidence resolves it. | **UNRESOLVED** |
| Raw numeric location, byte order, and invalid values in `0x26` | Undetermined. No raw-value extraction. | **UNRESOLVED** |
| Analyte/type code and analyte-specific variation | Undetermined from `0x25`/`0x26` alone. The known physical record and the user's measurement history cannot establish a payload code. No analyte enum/dispatch. | **UNRESOLVED** |
| Control-solution and other status flags | Neither positions nor meanings established. Keep future status opaque until traced. | **UNRESOLVED** |
| Uric-acid scaling | Once a record is independently identified as uric acid and its raw numeric value extracted, the app/private capture supports displayed value = raw / 10. Existing contextual helper implements this; the unit string is not established by this fact. | **LIVE-CORROBORATED** scaling relation, conditional on identity and extraction. |
| `0x2F` dependency | Earlier static notes show an analyte-range/category query separate from the direct indexed pair. The Stage 2F read succeeded without it, proving it is unnecessary for **retrieval** in the tested state. Whether it supplies context necessary for **reliable interpretation** cannot be decided from sanitized notes. No live `0x2F` query is authorized here. | **UNRESOLVED** for interpretation. |

## Implementation gate and next evidence

Only the common frame envelope is sufficiently mapped here, and `protocol.py` already validates it. Adding a record-part wrapper that merely renames `ProtocolFrame.opaque_data` would not establish a new semantic field. No parser code or new fixture is justified at this checkpoint. Existing synthetic tests cover the known envelope, command roles, request frames, slot count, and contextual uric-acid scaling; they do not imply a real record decode. The user explicitly paused Stage 2G parser implementation until the decompilation directories are located.

**Exact next gate:** locate the actual retained private 1.7.6 and 1.7.9 decompilation directories and resume Stage 2G only on the user's direction. Trace the response parser and TD4183 call sites for both versions, and privately compare the resulting interpretation with the known record if its displayed value/time are available without publishing them. Then implement and test only fields classified **STATIC-ANALYSIS-SUPPORTED** or **LIVE-CORROBORATED**. If static evidence shows `0x2F` is necessary for analyte interpretation, propose its physical evaluation as a separately authorized later gate; do not send it under Stage 2G.
