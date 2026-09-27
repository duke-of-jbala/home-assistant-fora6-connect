# Stage 7H — manual current-state uric-acid refresh

**Stage 8 follow-up:** [the offline hardening review](STAGE8_CURRENT_STATE_HARDENING_REVIEW.md) confirms repeat refresh uses the same entity, failures retain the prior in-process reading, and reload/restart intentionally returns it to unavailable until another manual refresh. A cleanup failure no longer masks an earlier primary error. The count-two/four commands, selection, and manual-only trigger remain unchanged.

**Stage 7H is complete for its authorized scope.** The user deployed the implementation, restarted Home Assistant, manually powered on the real GD82 without pressing history arrows, and ran `fora6_connect.refresh_current_uric_acid` once. The real count-four action succeeded, considered two eligible primary candidates, selected the one with the later parsed meter-local minute, and completed cleanup. The existing GD82/ForaCare device remained; its existing single uric-acid entity became available and populated, with no duplicate sensor. The private value/time, screenshot, Bluetooth address, serial, and System ID are not part of this record.

Stage 7H implements the first production-facing **manual** current-state refresh for the existing uric-acid sensor. It reads a bounded current memory snapshot and publishes one selected value. It does not import historical observations, backfill recorder/statistics, persist deduplication or a resume cursor, poll, or start a refresh automatically.

## Evidence and fixed plans

Stages 7B/C physically validated a two-slot User1 memory state. Stage 7E validated a four-slot state with even-index General-valid primaries and odd-index QC-invalid companions. Stage 7G showed that primary raw 0 had a later parsed meter-local time than primary raw 2 in one real four-slot snapshot. Raw-index magnitude is therefore not a chronology rule. The retained app evidence and limitations are recorded in the [Stage 7F reassessment](STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md).

Each manual session confirms the configured canonical factory Bluetooth MAC matches its stored locator, resolves the connectable device through Home Assistant Bluetooth, subscribes to the custom characteristic, then sends one `0x22` wake, one `0x24` project query and one User1 `0x2B` metadata query. The project must equal `0x4183`. The only supported raw counts and record plans are:

| Raw count | Ordered User1 raw index plan | Maximum application writes |
| --- | --- | ---: |
| 2 | `0 → 1`, one `0x25`/`0x26` pair per index | 7 |
| 4 | `0 → 1 → 2 → 3`, one pair per index | 11 |

Other counts stop after metadata. No command is retried. There is no `0x2F`, `0x33`, `0x50`, pairing, or RACP path. One coordinator and lock belong to each loaded config entry; concurrent manual calls do not start overlapping sessions.

Both parts of every requested slot must parse. Odd companions must have the app-mapped QC category and invalid sentinel; they never produce ordinary sensor values. An eligible primary must be valid General uric acid. For count two, raw 0 must be eligible. For count four, raw 0 and raw 2 are considered independently. Zero eligible primaries fails. One is selected. If both are eligible, the strictly later parsed meter-local minute wins. Equal minutes are ambiguous and fail closed. Companion analyte identity and equal primary/companion timestamps are not assumed as universal constraints.

The selected product measurement uses the established `raw / 10` mg/dL base value. The existing sensor becomes available only after full traversal and clean notification stop/disconnect. Later failures retain its previous valid value; an initially failed refresh leaves it unavailable. Cleanup failure also prevents publication. The action result reports safe stage/error codes and, on success, the selected index, eligible count, selected mg/dL value, and meter-local minute. The latter two are private health data authorized only in the local action response and normal sensor state. No raw integer/frame, MAC, serial, System ID, or digest is returned or logged.

The meter-local time remains timezone-naive, minute precision, and is held in the product measurement. The successful ingestion time is tracked separately in process memory as an aware UTC time; it is not substituted for measurement time. No measurement-time sensor attribute is added in this first implementation.

## Manual use and validated operating procedure

For a manual refresh, turn the GD82 ON normally and do not press its history arrow keys. In Home Assistant Actions, run `fora6_connect.refresh_current_uric_acid` and select the configured FORA 6 Connect entry. The [Home Assistant config-entry selector](https://www.home-assistant.io/docs/blueprint/selectors/#config-entry-selector) supplies the entry ID without asking for the Bluetooth address. The private action response contains health data.

The procedure reflects live observations: history-arrow browsing stopped the Bluetooth light, and an immediate post-measurement transfer state previously connected but failed custom notification subscription. Their internal causes remain unknown. Stage 7H does not automate around those states.

The count-four manual refresh is LIVE-CORROBORATED for the tested GD82 snapshot. The count-two production refresh path remains limited to its physically evidenced record layout and synthetic Stage 7H validation. Snapshot mutation, meter-clock adjustment, equal-minute collisions, arbitrary counts above four, count six and larger, capacity, circular-buffer behavior, wrap/overwrite, delete/reset effects, persistent record identity, deduplication, resume, historical import, recorder/statistics backfill, startup/periodic/advertisement/post-measurement refresh, automatic meter-state recovery, mixed-analyte support, and proprietary/printed serial retrieval remain unresolved or out of scope. Meter-local timestamps retain minute precision and unknown timezone; clock changes may alter apparent chronology, and raw index magnitude is not a chronology rule.

Previously observed meter-state behavior remains unexplained: normal manual power-on gives the known working Bluetooth state; history-arrow browsing was observed to stop the Bluetooth light; and an immediate post-measurement flashing state allowed BLE connection but failed custom notification subscription. No firmware cause is inferred and Stage 7H does not automate around these states.

**Exact next proposed gate:** Stage 8 — offline/synthetic/design-first current-state refresh hardening and product-behavior review. Suggested topics are repeat-refresh behavior, failure retention, measurement-time presentation, action/status UX, clean install/reload/upgrade behavior, no-duplicate guarantees, and readiness for Stage 9 proxy-path validation. Stage 8 is not started by this closure. Stage 9 proxy validation, Stage 10 HACS readiness, Stage 11 release candidate, and Stage 12 v1.0.0 remain later gates. Historical import and broader analyte support need not block v1.
