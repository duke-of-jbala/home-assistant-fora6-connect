# Stage 7G — bounded primary chronology probe and Stage 7G1 private output

**Later implementation note:** The user-run Stage 7G chronology result informed the separately authorized [Stage 7H manual current-state refresh](STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md). Stage 7G remains a development action; Stage 7H is synthetic-tested and awaits its own physical validation. The chronology result does not establish index ordering or circular-buffer behavior.

Stage 7G implements a **development-only** relative-time check. Stage 7E physically confirmed that raw indexes 0 and 2 were valid General primary candidates in one four-slot GD82 state, with indexes 1 and 3 behaving as companions. The order of the two primaries remained unknown. This action has synthetic test coverage only; no physical Stage 7G result is claimed here.

## Fixed read and gates

`fora6_connect.probe_history_chronology` accepts one private runtime Bluetooth address. It uses `Fora6BluetoothTransport` with Home Assistant's selected Bluetooth route, no pairing, bounded waits, one response per request, and deterministic cleanup. It sends only `0x22` wake, `0x24` project query, and one User1 `0x2B` metadata request. It requires project `0x4183` and a valid **exact raw count of four**. Any other count stops before record reads.

At count four it requests User1 raw index 0 (`0x25`, `0x26`) and then User1 raw index 2 (`0x25`, `0x26`), using the existing request builders and record parsers. The maximum is seven application writes: identity pair, one metadata query, and two record pairs. No other index, selector, command, loop, retry, or dynamic count adaptation is present.

Each combined record must independently be identified as uric acid, General, valid/non-sentinel, and non-QC. If index 0 fails, index 2 is not read. If either gate fails, the action does not compare times. Malformed responses, timeouts, disconnects, and transport poison stop the sequence; cleanup still runs. A semantic mismatch is a returned false gate, not a claim that the wire exchange failed.

## Private development response

Stage 7G1 explicitly authorizes **private health data in this local Home Assistant development action response only**. After an individual primary passes the complete semantic gate, the result includes `index_0_meter_local_time` and `index_0_uric_acid_value_mg_dl`, or the corresponding `index_2_*` fields. The value comes from the existing evidence-backed `TD4183Record.uric_acid_scaled_value` (`raw / 10`, mg/dL) and is returned as a JSON-compatible number. The time is the exact parsed meter-local fields formatted `YYYY-MM-DD HH:MM`. A failing record has neither field. If index 0 fails, index 2 is not read. No real measurement or timestamp appears in this documentation or any tracked fixture.

Only after both semantic gates pass does the action compare their existing `MeterLocalTimestamp.as_naive_datetime()` values inside the current session. Exactly one of `index_0_time_before_index_2`, `index_0_time_equal_index_2`, or `index_0_time_after_index_2` is true when `chronology_comparison_complete` is true. Other outputs are connection/identity/metadata status, pair and semantic-gate booleans, cleanup status, and privacy-safe error codes. No raw wire integer, auxiliary byte, app code number, raw frame, time difference, identifier, digest, or address is returned. Values and times are not logged, persisted, added to diagnostics, or sent to the sensor/entity.

The meter-local fields have minute precision and an unknown timezone. They remain naive: no UTC, local-zone, or DST interpretation is applied. This comparison is meaningful only between the two parsed records in this current snapshot. Equal-minute readings, clock changes, resets, and buffer behavior limit any broader conclusion.

## User-run physical gate

After review, the user may deploy the build, restart Home Assistant, and turn the GD82 **manually ON**. The post-measurement Bluetooth-flashing state previously allowed connection but failed notification subscription. The user should privately browse the two stored results with the meter's arrow keys, then run `fora6_connect.probe_history_chronology` once with the private runtime address. Compare the returned private values and meter-local times with the physical display **locally** to identify which raw slot corresponds to each displayed result. Do not share the action response, measurement values, dates, or times publicly. A privacy-safe follow-up may state the resulting slot-to-display/order conclusion without the underlying health data.

If count is not four, the action stops after metadata and gives no chronology evidence. A failed semantic gate likewise gives no chronology comparison; only successfully gated records may expose their private fields. If comparison succeeds, the three booleans identify which **raw primary has the later meter-local wall time in this snapshot**, or whether the times are equal. Direct private value/time matching can now associate a raw slot with a displayed result if the two results are distinguishable. Even if index 2 is later here, that does not establish a general highest-index-is-newest rule.

## Product boundary and next gate

This action does not touch `sensor_state`, the entity, coordinator, ConfigEntry, or a history store. The existing uric-acid entity remains unavailable; production sync and historical import are absent. General traversal, latest selection across arbitrary counts, wrap, durable deduplication, and resume remain unresolved.

**Exact next gate:** user-run bounded Stage 7G1 physical validation and private meter-display correlation. The private action response stays local; only a conclusion without measurement values or timestamps need be reported. After that conclusion is reviewed, separately authorize any further chronology experiment or a narrow current-state sync design. No production sync follows automatically.

## Stage 7G2 physical closure

The user ran the private Stage 7G1 action once with the GD82 manually ON, without browsing meter history first. Model confirmation, count-four gate, both raw-primary semantic gates, chronology comparison, and cleanup all succeeded. The response showed **raw primary 0 later than raw primary 2** by their parsed meter-local times. The private values and times were reviewed by the user and are deliberately absent from this public record. **Stage 7G is complete for its bounded count-four primary chronology scope (LIVE-CORROBORATED).** In this snapshot, a higher raw index was not newer. Neither this result nor the app code proves a universal index order, wrap behavior, reset behavior, or ordering for arbitrary counts.

The user also observed that normal manual power-on gave a Bluetooth-flashing usable state, whereas pressing the history arrow keys stopped the Bluetooth light. This is a **LIVE-CORROBORATED meter-state observation**; the internal cause is unknown. A later production manual refresh should start with the meter normally ON and no history-button browsing, pending separate authorization.

The two distinct private mg/dL records appeared as the same two-decimal mmol/L text on the physical display. The [Stage 7G2 conversion review](URIC_ACID_UNIT_CONVERSION.md) explains the retained app's floor-formatting rule and its limit as evidence about the separate meter firmware. No production value or entity state changed.

**Next gate:** separately authorize Stage 7H, a strict manual current-state uric-acid refresh for only raw counts two and four, with complete fixed-plan validation and fail-closed timestamp ties. Historical import and automatic triggering remain gated.
