# Stage 7E — bounded four-slot traversal probe

**Status: complete for the authorized bounded physical scope.** The real GD82 passed this fixed four-slot probe in one tested state. No production synchronization, state update, persistence, deduplication, or resume behavior was implemented.

## Procedure and privacy boundary

The manually invoked `fora6_connect.probe_history_window_four` action confirms project `0x4183`, queries User1 raw metadata once, and proceeds only for raw slot count exactly four. It reads only indexes `3 → 0 → 1 → 2 → 3`, each with one `0x25`/`0x26` pair. No adaptation occurs for other counts. The action parses pairs in memory, compares index-three repeats privately, then stops notifications and disconnects. It returns structural/classification/equality status only. It does not expose values, timestamps, frames, serial, address, or hashes and does not update the entity. See the implementation checkpoint `bd1fafc097e43ca17ffafbac455f6ea1c513341f`.

## User-run physical result

The user took a normal measurement. In the immediate post-measurement state, strip ejection switched the meter off and the Bluetooth light flashed. During this state Home Assistant resolved and connected, but notification subscription failed. No application command, metadata query, or record read occurred; disconnect was clean. The user then manually switched the meter ON and ran the action once. The second run confirmed identity, queried valid metadata with raw count four, and completed the fixed `3 → 0 → 1 → 2 → 3` sequence. All five record pairs validated and cleanup succeeded.

Observed classifications:

- Raw indexes 0 and 2: analyte identified, General category, valid value, QC false.
- Raw indexes 1 and 3: analyte identified, QC category, invalid sentinel, QC true.
- Candidate pair 0/1 parsed structurally and their meter-local times compared equal.
- Candidate pair 2/3 parsed structurally and their meter-local times compared equal.
- The repeated index-three first and second frames matched byte-for-byte. Its analyte, category, validity, and combined semantic classifications also matched.

The post-measurement subscription failure is a **LIVE-CORROBORATED meter-state observation**: connection was possible while custom notification subscription failed, and manually turning the meter back ON restored the successful custom protocol path. The internal cause is unknown; transport behavior is unchanged.

## Interpretation and limits

The four-slot result materially strengthens, for this GD82 state, the hypothesis that even raw indexes are primary measurement records and odd indexes are QC/invalid companions, with matching meter-local times within each proposed pair. Structural pairing and equal times do not prove a universal companion rule. They do not establish the chronological relationship between group 0 and group 1, or oldest/newest order.

Still unresolved are general traversal order, exact relation between logical group timestamps, capacity, circular-buffer/wrap/overwrite behavior, deletion/reset behavior, durable raw-index identity, collision-safe deduplication, resume, and production-safe arbitrary-size traversal. No new measurement should be taken for a future evidence gate.

**Exact next proposed gate:** separately authorize Stage 7F as an offline reassessment of logical grouping, chronology, and a minimal production-sync design using this result. Stage 7F is not begun here.
