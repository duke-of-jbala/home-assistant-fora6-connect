# Stage 7G — bounded primary chronology probe

Stage 7G implements a **development-only** relative-time check. Stage 7E physically confirmed that raw indexes 0 and 2 were valid General primary candidates in one four-slot GD82 state, with indexes 1 and 3 behaving as companions. The order of the two primaries remained unknown. This action has synthetic test coverage only; no physical Stage 7G result is claimed here.

## Fixed read and gates

`fora6_connect.probe_history_chronology` accepts one private runtime Bluetooth address. It uses `Fora6BluetoothTransport` with Home Assistant's selected Bluetooth route, no pairing, bounded waits, one response per request, and deterministic cleanup. It sends only `0x22` wake, `0x24` project query, and one User1 `0x2B` metadata request. It requires project `0x4183` and a valid **exact raw count of four**. Any other count stops before record reads.

At count four it requests User1 raw index 0 (`0x25`, `0x26`) and then User1 raw index 2 (`0x25`, `0x26`), using the existing request builders and record parsers. The maximum is seven application writes: identity pair, one metadata query, and two record pairs. No other index, selector, command, loop, retry, or dynamic count adaptation is present.

Each combined record must independently be identified as uric acid, General, valid/non-sentinel, and non-QC. If index 0 fails, index 2 is not read. If either gate fails, the action does not compare times. Malformed responses, timeouts, disconnects, and transport poison stop the sequence; cleanup still runs. A semantic mismatch is a returned false gate, not a claim that the wire exchange failed.

## Relative-time-only result

Only after both semantic gates pass does the action compare the records' existing `MeterLocalTimestamp.as_naive_datetime()` values inside the current session. Exactly one of `index_0_time_before_index_2`, `index_0_time_equal_index_2`, or `index_0_time_after_index_2` is true when `chronology_comparison_complete` is true. Other outputs are connection/identity/metadata status, pair and semantic-gate booleans, cleanup status, and privacy-safe error codes. No measurement, unit, raw frame, timestamp, time difference, identifier, digest, or address is returned or logged. No state or fingerprint is persisted.

The meter-local fields have minute precision and an unknown timezone. They remain naive: no UTC, local-zone, or DST interpretation is applied. This comparison is meaningful only between the two parsed records in this current snapshot. Equal-minute readings, clock changes, resets, and buffer behavior limit any broader conclusion.

## User-run physical gate

After review, the user may deploy the build, restart Home Assistant, and turn the GD82 **manually ON**. The post-measurement Bluetooth-flashing state previously allowed connection but failed notification subscription. The user should privately browse the two stored results with the meter's arrow keys and determine only whether its browsing order is “newest first”, “oldest first”, or “cannot tell”; no value, date, or time needs to be shared. Then run `fora6_connect.probe_history_chronology` once with the private runtime address and share only its sanitized response plus that relative browsing-order phrase.

If count is not four, the action stops after metadata and gives no chronology evidence. A failed semantic gate likewise gives no chronology evidence. If comparison succeeds, the three booleans identify which **raw primary has the later meter-local wall time in this snapshot**, or whether the times are equal. Physical browsing order is separate evidence. The action alone does not map a physical display item to a raw slot; such a mapping must not be inferred from display order alone. Even if index 2 is later here, that does not establish a general highest-index-is-newest rule.

## Product boundary and next gate

This action does not touch `sensor_state`, the entity, coordinator, ConfigEntry, or a history store. The existing uric-acid entity remains unavailable; production sync and historical import are absent. General traversal, latest selection across arbitrary counts, wrap, durable deduplication, and resume remain unresolved.

**Exact next gate:** user-run bounded Stage 7G physical validation and private meter-display correlation. After the sanitized result is reviewed, separately authorize any further chronology experiment or a narrow current-state sync design. No production sync follows automatically.
