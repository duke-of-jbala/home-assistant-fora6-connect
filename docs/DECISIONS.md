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

**Status:** Accepted for a development-only Stage 2F physical test, 2026-09-27. The [offline evidence review](STAGE2F_TD4183_RECORD_PROBE.md) traces the TD4183 app's read-oriented current-user `0x2B` slot query and `0x25`/`0x26` indexed pair, including exact index-zero requests. After the unchanged wake/project/`0x4183` identity gate, a manual action may issue each of those three requests once, with explicit write response and no loop or retry. It returns only response-status metadata. The app's `0x33` clock-set operation is excluded; its necessity before physical record reads remains unresolved. No analyte/value/time parser or production sync path follows from this decision. Stage 2F remains open until a real one-record result is reviewed.
