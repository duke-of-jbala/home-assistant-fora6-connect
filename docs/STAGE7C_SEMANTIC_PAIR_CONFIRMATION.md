# Stage 7C — bounded semantic pair confirmation

**Status:** development-only implementation with synthetic validation. No Stage 7C physical result has been run or claimed. The [Stage 7B physical probe](STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) established that the tested GD82 accepted the fixed two-slot branch, but its action disclosed no record classifications.

## Purpose and fixed operation

`fora6_connect.probe_history_semantics` accepts only the private runtime Bluetooth address. It uses `Fora6BluetoothTransport` to connect through Home Assistant Bluetooth, subscribe to custom 1524, send one `0x22` wake and one `0x24` project request, and require project `0x4183`. It then sends one User1 `0x2B`. **Only raw slot count exactly two** permits the three literal pair reads:

| Occurrence | Raw index | Requests |
| --- | ---: | --- |
| First last-slot read | 1 | `0x25`, `0x26` |
| First-slot read | 0 | `0x25`, `0x26` |
| Repeated last-slot read | 1 | `0x25`, `0x26` |

At most nine application requests occur. There is no user-selected count, index, selector, analyte, command retry, record loop, `0x27`, `0x28`, `0x2F`, `0x33`, `0x50`, pairing, or RACP. Transport failures, invalid frames, malformed record parts, or disconnect stop subsequent requests. A valid pair with unexpected semantics is a completed probe with false pattern flags, not a transport failure. Notification stop and disconnect run on success, failure, and cancellation.

## Parser and classification path

Each command-matched `ProtocolFrame` passes through `parse_td4183_record_part_one` or `parse_td4183_record_part_two`, then `combine_td4183_record` produces a private in-memory `TD4183Record`. The action reads only its analyte, category, sentinel validity, and `is_qc` properties. It does not call uric-acid scaling or use the meter-local timestamp. `protocol.py` and `models.py` remain independent of Home Assistant and Bleak.

The evidence-backed expected pattern from the retained private app import is:

- Raw index zero: identified `URIC_ACID`, `GENERAL`, valid/non-sentinel raw value, `is_qc = false`.
- Raw index one: identified `HEMATOCRIT`, `QC`, invalid `0xFFFF` sentinel, `is_qc = true`.

The result reports a boolean for each test and an `expected_*_semantics_match` summary. The first and second index-one records are compared by analyte code/classification, category, and sentinel validity. `repeated_index_1_semantics_equal` requires all three equality checks. Semantic equality does not imply the underlying frames, timestamps, or raw values were identical. The Stage 7B result separately established frame equality only for its earlier single session.

## Privacy and product boundary

Only connection, identity, count-gate, pair-completion, classification, equality, expected-pattern, cleanup, and stable error-status fields leave the action. The fixed requested-index list and expected raw count are public probe constants. No raw frame/payload, numeric or scaled health value, unit, meter-local time, serial, Bluetooth address, hash, or other recoverable measurement representation is returned, logged, or persisted.

The action does not update `sensor_state.py`, the uric-acid entity, or `coordinator.py`; it does not persist health records, fingerprints, or cursors. The existing uric-acid entity remains unavailable until separately authorized production synchronization supplies a valid measurement. There is no general history traversal or production synchronization in Stage 7C.

## Controlled physical procedure after review

The user may deploy this commit, restart Home Assistant, turn the GD82 **ON**, and run `fora6_connect.probe_history_semantics` once with the private runtime address. Share only the privacy-safe action result. Do not share raw frames, health measurements, meter timestamps, serials, addresses, or logs containing them. Codex does not run the physical test.

If `expected_semantic_pattern_confirmed` is true with valid pairs and clean cleanup, the tested session confirms the expected index-zero and index-one classifications for this meter state. If a valid pair yields a false expected-pattern flag, the classification differs from the private captured import; the booleans identify only which expected property differed and do not establish why. If count differs from two or a transport/protocol error occurs, no later indexed requests are allowed. The outcome does not establish oldest/newest ordering, wrap, capacity, empty slots, stable record identity, deduplication, resume semantics, or a production sync policy.

**Exact next gate:** review the sanitized user-run Stage 7C result. Any further physical probe, broader traversal design, or production synchronization requires a separate authorization and evidence review.
