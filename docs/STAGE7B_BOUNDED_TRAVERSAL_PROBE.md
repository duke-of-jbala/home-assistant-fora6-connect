# Stage 7B — bounded TD4183 traversal probe

**Scope/status:** a manually invoked, development-only Home Assistant action, `fora6_connect.probe_history_window`. **Stage 7B is complete for its authorized bounded physical scope** following the user-run GD82 validation recorded below. No coordinator retrieval, entity update, polling, history store, deduplication, cursor, or production synchronization is added.

## Evidence and exact bound

[Stage 7A](STAGE7A_HISTORY_TRAVERSAL_DESIGN.md) traces both retained app versions' `0x2B` raw count and app-labeled newest-index fields and their indexed User1 `0x25`/`0x26` request builders. The retained private app capture observed the raw-index order **1 → 0 → 1**. That order is evidence for this probe plan, not a general history traversal rule. Earlier user-run Home Assistant probes physically established User1/index zero only. Stage 7B adds index-one constructors to pure `protocol.py` using the statically supported, app-captured little-endian raw index in request bytes 2–3 and User1 selector in byte 5. They construct only raw index one; no arbitrary-index iterator is exposed.

The action accepts only a private runtime Bluetooth address. It uses `Fora6BluetoothTransport` with Home Assistant-selected local adapter or eligible proxy, bounded waits, connection-only retry, single-flight exchanges, poisoned-session handling, `response=True` writes, and cleanup. It connects and subscribes to custom 1524, sends exactly one `0x22` wake and one `0x24` project query, and requires project `0x4183`. It then sends exactly one User1 `0x2B`. Response bytes 2–3 are the unadjusted raw slot count; bytes 4–5 are parsed as the app-labeled newest index but are not used to select an index or infer ordering.

**Count gate:** only raw slot count **exactly 2** permits indexed reads. Count 0, 1, 3, or any other value stops after metadata with no `0x25` or `0x26`; the action returns a count-match boolean, not the private count. An invalid metadata frame, identity failure, or project mismatch also stops. There is no dynamic adaptation.

After the gate, the fixed request plan is:

| Occurrence | Raw index | Commands |
| --- | ---: | --- |
| Last-slot probe | 1 | `0x25`, then `0x26` |
| First slot | 0 | `0x25`, then `0x26` |
| Repeated last slot | 1 | `0x25`, then `0x26` |

This is at most **nine application writes total**: two identity requests, one metadata request, and six record-part requests. Each request is sent once. No `0x27`, `0x28`, `0x2F`, `0x33`, `0x50`, RACP, pairing, or application-command retry exists in this path. Every response must have the correct frame length, marker, checksum, and command echo; each record part is also passed through its existing parser so malformed date/time payloads fail closed. An invalid part, timeout, write failure, or disconnect stops before the next pair. Notification stop and disconnect run on success, failure, and cancellation.

## Result and privacy

The action reports connection/identity status, metadata validity, `expected_raw_slot_count: 2`, count-match and gate booleans, attempted indexes (only literals from `[1, 0, 1]`), per-occurrence part-valid/pair-complete booleans, cleanup status, and stable error stage/code. It compares the two validated index-one `ProtocolFrame.data` values separately for `0x25` and `0x26` **only in memory**. Equality fields are `null` until both index-one pairs complete, then booleans; pair equality requires both parts equal. `traversal_performed` means all three fixed pairs completed, with cleanup outcome reported separately.

No frame bytes, payload, raw or scaled health value, meter-local timestamp, serial, Bluetooth address, manufacturer data, payload hash, or differing byte position is returned, logged, or persisted. The existing development actions and their schemas remain unchanged. The configured uric-acid entity remains unavailable because no production measurement state is fed by this action.

## Controlled user-run validation after review

Deploy the committed integration and restart Home Assistant. Turn the GD82 **ON** and wait until it is connectable. Run `fora6_connect.probe_history_window` **once** with its private runtime address. Share only the sanitized action result; do not share logs, raw frames, health values, timestamps, serial, or address. Codex does not run this physical test.

- **Count mismatch:** confirms only that the tested meter state did not meet the two-slot gate. No indexed request was sent; it is not evidence of traversal failure or permission to change indexes.
- **Repeated index one equal:** the two index-one response frames were byte-identical within this bounded session. It does not prove long-term stability, latest ordering, capacity, wrap, or a deduplication key.
- **Repeated index one different:** at least one validated index-one part changed within the session. The booleans do not reveal why; inspect the protocol hypothesis privately before any broader probe.

## User-run physical result and interpretation

The user deployed the Stage 7B build and ran the action once against the real GD82 with the meter ON. Device resolution, connection, characteristic discovery, subscription, wake response, project response, project match, and identity confirmation all succeeded. One metadata response was valid and reported the expected raw count of two. Traversal ran at indexes `1 → 0 → 1`; both parts of all three pairs validated. The first and second index-one `0x25` frames matched, the first and second index-one `0x26` frames matched, and the pair equality result was true. Notification stop and disconnect succeeded; no error or cleanup error was reported. No private health value, timestamp, raw response, serial, address, or payload digest was disclosed.

This physically confirms the fixed two-slot branch is usable in this tested meter state, every selected pair validates, and index one is byte-for-byte stable within that session. It corroborates the retained private app sequence. It does **not** establish general oldest/newest order, arbitrary count traversal, circular-buffer behavior, wrap, capacity, empty-slot behavior, stable raw-index identity, collision-safe deduplication, production synchronization, or resume behavior.

**Exact next proposed gate:** Stage 7C — bounded semantic pair confirmation. Using existing evidence-backed parsers, determine whether index 0 classifies as uric acid / General / valid and index 1 as hematocrit / QC / invalid sentinel; compare repeated index-one classifications. A Stage 7C result must expose classifications and equality/status booleans only, never numeric measurements, timestamps, raw frames, or hashes. Stage 7C requires separate authorization and is not implemented here.

**Stage 7C follow-up:** [the separately authorized semantic action](STAGE7C_SEMANTIC_PAIR_CONFIRMATION.md) was implemented with synthetic validation and then physically validated. Its result matched the expected classifications and repeat comparison with clean cleanup. Stage 7B's action and result remain unchanged.

**Stage 7C physical result:** the separate action confirmed the expected classifications for index zero (uric acid/General/valid/not-QC) and index one (hematocrit/QC/invalid-sentinel/QC); repeated index-one semantic fields matched and cleanup was clean. Stage 7C is complete for its bounded scope. General history behavior remains unresolved.
