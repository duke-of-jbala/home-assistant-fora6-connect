# Architecture decisions

These decisions are accepted for Stage 0. Revisit only on explicit instruction or documented new evidence.

## ADR-001 — FORA logic in Home Assistant

**Status:** Accepted. Home Assistant performs FORA-specific communication and decoding. This keeps device behavior within the integration that owns its entities and sync state.

## ADR-002 — ESPHome is transport only

**Status:** Accepted. ESPHome Bluetooth Proxy remains generic, allowing the same integration to use local or remote Home Assistant Bluetooth paths.

## ADR-003 — Independent parser

**Status:** Accepted. The FORA protocol parser is independent of Home Assistant, so captured raw frames can be decoded in unit tests without Bluetooth hardware.

## ADR-004 — Evidence before protocol code

**Status:** Accepted. Documented or captured evidence with provenance must precede protocol implementation, preventing guessed packets from becoming production behavior.

## ADR-005 — One meter, one HA device

**Status:** Accepted. One Home Assistant device represents each physical FORA 6 Connect meter; later entities belong to it.

## ADR-006 — Preserve meter time

**Status:** Accepted. Original measurement timestamps must be stored separately from synchronization time, so imported history is not misdated.

## ADR-007 — Protect health data

**Status:** Accepted. Private health data and identifiable raw captures must not enter the public repository. Any public fixture must be sanitized and provenance recorded.

## ADR-008 — Bound the first protocol implementation to confirmed evidence

**Status:** Accepted for Stage 2D, 2026-09-27. The user-supplied Stage 2C capture summary confirms the GD82 eight-byte frame envelope, wake and project-query exchanges, project ID `0x4183`, and uric-acid raw-value `/10` display scaling on that path. `protocol.py` may implement offline frame checks, those two fixed request constructors, project-ID extraction, and a contextual uric-acid scaling helper. The sanitized evidence does not establish public byte positions or analyte identifiers for `0x25`/`0x26` records, so record parsing, timestamp decoding, and analyte dispatch wait for a later evidence gate. This decision does not authorize Home Assistant BLE writes or automatic record retrieval. See [the Stage 2C evidence record](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md).

## ADR-009 — Isolate the controlled Stage 2E identity transport

**Status:** Accepted for Stage 2E, 2026-09-27. Explicit user authorization permits a separate, manually invoked Home Assistant action to subscribe only to custom `1524`, write the captured `0x22` wake and `0x24` project requests once each with response, validate the matching notifications through HA-independent `protocol.py`, require project `0x4183`, and disconnect. This does not broaden ADR-008 into a production path or authorize record operations, pairing, RACP, or automatic sync. See [the Stage 2E evidence](STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md).

**Stage 2E evidence update:** The real action succeeded with the GD82 ON: both exchanges validated, project `0x4183` matched, and subscription/disconnect cleanup succeeded. The prior Stage 1C connection while the display appeared off is separate. This closes the bounded identity gate; Stage 2F record commands require their own exact-construction and non-destructive evidence review.

## ADR-010 — Bound the Stage 2F record transport to raw index zero

**Status:** Accepted and physically validated for one bounded read on the real GD82 with the meter ON, 2026-09-27. The [Stage 2F evidence review](STAGE2F_TD4183_RECORD_PROBE.md) traces the TD4183 app's read-oriented `User1 = 1` `0x2B` slot query and `0x25`/`0x26` indexed pair, including exact index-zero requests. After the unchanged wake/project/`0x4183` identity gate, the manual action issued those requests once, with explicit write response and no loop or retry. Each returned a valid command-matched frame, and cleanup succeeded. It returned only response-status metadata. The app's `0x33` clock-set operation was excluded and was not required for this successful bounded read in the tested meter state. No analyte/value/time parser or production sync path follows from this decision. Stage 2F is complete; Stage 2G is offline only.

**Selector correction and physical pause:** Pre-test review found that the original constructors used `CurrentUser = 0`, while the retained successful app import sent `User1 = 1`. Static builders and call sites confirm the corrected selector positions, recorded in the revised [Stage 2F review](STAGE2F_TD4183_RECORD_PROBE.md). No Home Assistant record request was physically sent. The bounded command set and identity prerequisite stay unchanged; physical validation is paused until the correction is reviewed.

**Subsequent physical result:** The corrected User1/index-zero action succeeded while the meter was ON. The pause above was a historical pre-test state. The first wake-write failure and a separate subscription failure stopped before record commands; neither is a record-protocol failure. `0x2F` was not sent by Home Assistant and remains a separate future evidence gate if semantic decoding needs it.

## ADR-011 — Defer semantic record fields until exact parser evidence is accessible

**Status:** Accepted for the Stage 2G offline evidence checkpoint, 2026-09-27. The actual retained private iFORA HM decompilation paths were not preserved; a suggested workspace path was absent. The retained private HCI import capture was inspected in place, supporting only byte-comparison observations. The sanitized Stage 2B/2C/2F notes and Stage 2F semantic physical result support the shared response envelope and broad `0x25` time/`0x26` measurement roles, but no exact time, raw-value, analyte, or flag positions. The existing raw/10 uric-acid scaling helper remains contextual and cannot identify an opaque record. [The Stage 2G evidence map](STAGE2G_TD4183_RECORD_SCHEMA.md) records the byte map and missing dependency. The user requested a pause of parser implementation until the decompilations are located. Do not add speculative semantic parsing, alter the live probe, or send `0x2F` under Stage 2G.

**Subsequent source recovery:** The retained private 1.7.6/1.7.9 decompilations became available. The pause condition was resolved and the separately authorized Stage 2G offline parser work resumed. [The revised Stage 2G map](STAGE2G_TD4183_RECORD_SCHEMA.md) documents exact supported fields, cross-version evidence, and private capture classification without proprietary source or health data.

## ADR-012 — Parse only evidenced TD4183 record fields offline

**Status:** Accepted for Stage 2G, 2026-09-27. Both retained app versions support exact `0x25` date/hour/minute packing and transmitted bit, and `0x26` raw value, analyte selector, category, and invalid `0xFFFF` sentinel. The private capture corroborates index-zero uric-acid type and repeated index-one hematocrit/QC sentinel classifications without publishing value/time. The protocol layer returns meter-local minute fields with unknown timezone, rejects malformed calendar values, preserves uninterpreted payload bits, leaves unsupported analyte codes unidentified, and keeps QC distinct. Uric-acid raw/10 scaling stays conditional on a decoded uric-acid type and valid raw value. Do not expose a real decoded result through the live action or add `0x2F` transport under this decision.

## ADR-013 — Combine validated record parts without inventing product semantics

**Status:** Accepted for Stage 3, 2026-09-27. The immutable pure-Python model retains the validated `0x25` and `0x26` parts, including opaque bytes, and exposes only their supported fields. It imposes no unevidenced cross-part constraint or record identifier. Raw `0xFFFF` remains visible as wire data but unavailable as a usable numeric result. Only identified valid uric-acid records receive contextual raw/10 scaling; other analytes and unknown selectors have no scaled value. Meter time remains local and timezone-free; QC stays distinct without an entity-exclusion policy. Ten synthetic, checksummed fixture cases cover the supported variants. The [Stage 3 record](STAGE3_RECORD_MODEL_AND_FIXTURES.md) documents the boundary. No live transport or Home Assistant action consumes this model yet.

## ADR-014 — Reuse a bounded Home Assistant Bluetooth session

**Status:** Accepted and complete for Stage 4, 2026-09-27. `bluetooth.py` resolves only a connectable HA `BLEDevice`, uses the proven two-attempt connector for connection establishment, validates the custom Write/Notify characteristic, and offers one command-agnostic exchange at a time. It bounds all asynchronous operations, validates responses through the HA-independent protocol layer, reports only stable privacy-safe errors, and attempts unsubscribe/disconnect under cancellation. It never retries an application command or stores a raw packet queue. The existing development actions retain their exact authorized sequences and result schemas. The user-run real-GD82 regressions for both identity and bounded record actions succeeded with the meter ON and clean notification stop/disconnect. This does not establish which adapter/proxy was selected or authorize discovery, sync, entities, or new commands. [The Stage 4 record](STAGE4_BLUETOOTH_TRANSPORT.md) documents the API, tests, and physical regression results.

## ADR-015 — Keep product values separate from unit-backed Home Assistant sensors

**Status:** Accepted for Stage 5, 2026-09-27. The pure-Python `Fora6Measurement` maps valid identified uric acid to the evidenced raw/10 scaled number, but the tracked Stage 2C and Stage 2G records do not establish its displayed unit. The product model therefore carries no unit and the sensor mapper returns no numeric state. Other analytes have no supported numeric output because their scaling and units are not both established. QC, AC, and PC remain distinct categories; QC is not assigned an additional meaning, and non-General records are not mapped to the ordinary measurement sensor. Meter time remains naive and minute-precision. No `SensorEntity` or device registration is created until the unit gate and Stage 6 config-entry/stable-identity gate are met. [The Stage 5 record](STAGE5_MEASUREMENT_ENTITY_MODEL.md) documents the model and tests.
