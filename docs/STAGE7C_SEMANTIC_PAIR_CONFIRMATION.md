# Stage 7C — bounded semantic pair confirmation

**Status:** Stage 7C is complete for its authorized bounded semantic-confirmation scope. The user-run physical result below matched the expected classifications. The [Stage 7B physical probe](STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) had already established that the tested GD82 accepted the fixed two-slot branch, while disclosing no record classifications.

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

## User-run physical result and interpretation

The user deployed the Stage 7C build and ran `fora6_connect.probe_history_semantics` once against the real GD82 with the meter ON. Identity and project confirmation succeeded; metadata was valid with raw count two; the fixed indexes `1 → 0 → 1` completed. Index zero classified as identified uric acid / General / valid / not QC. Both index-one occurrences classified as identified hematocrit / QC / invalid sentinel / QC. Repeated index-one analyte, category, and validity classifications matched. Notification stop and disconnect were clean; no error or cleanup error was reported. No health value, scaled value, timestamp, raw frame, serial, address, or digest was disclosed.

The true expected-pattern summary confirms these classifications in the tested two-slot meter state. A future semantic mismatch would identify only the differing expected field and not its cause. A count mismatch or transport/protocol error stops before later indexed requests. This outcome does not establish general arbitrary-size traversal, oldest/newest ordering, circular-buffer or wrap behavior, capacity, empty slots, stable raw-index identity, collision-safe deduplication, persistence/resume, automatic sync, behavior after record rotation, or other analyte scaling/units.

**Exact next project task:** focused Stage 6B rediscovery/locator-identity follow-up. The user observed a discovery card reappearing for an already configured meter. Privately reconcile printed serial/BT MAC with GATT serial and HA runtime locator, and review duplicate suppression and safe locator update behavior. Keep `0x2A25` serial canonical and Bluetooth address mutable; do not publish actual identifiers. Do not begin Stage 7D or production sync automatically.

**Later Stage 7E evidence:** in one four-slot state, raw indexes 0 and 2 classified General/valid and indexes 1 and 3 QC/invalid; proposed adjacent pairs had equal meter-local times, and repeated index 3 matched. This strengthens but does not universalize the companion hypothesis. Cross-group chronological order and production traversal remain unresolved.
