# Architecture decisions

## Stage 8H-B — implement the manual private bounded history response

**Status:** Synthetically implemented, physical validation deferred. [The Stage 8H-B record](STAGE8H_B_BOUNDED_HISTORY_IMPLEMENTATION.md) uses one configured-entry action and the existing count-two/four read and semantic gates. It returns both valid count-four primaries in meter-local newest-first order, flags equal-minute ambiguity, and fails without a partial list on any required read or cleanup failure. The existing sensor and P4 probe semantics remain separate. There is no imported history, persistent dedup/cursor, new entity, event, Recorder/statistics backfill, deployment, tag, or release. Stage 13A-P4 is physically open.

## Stage 8H-A — expose bounded history through one manual response action

**Status:** Architecture accepted for a separately gated implementation. [The Stage 8H-A review](STAGE8H_A_BOUNDED_HISTORY_ARCHITECTURE.md) treats each valid General uric-acid primary in a complete count-two/four snapshot as a discrete historical measurement. Return one or two in a configured-entry private response, sorted by meter-local minute with unknown timezone; retain both equal-minute primaries and disclose the order ambiguity. Validate all fixed slots and cleanup before returning any list. Keep QC-invalid companions internal, and keep the existing current-state winner/sensor policy separate. No event, history entity, Recorder/statistics backfill, persistence, automatic trigger, runtime code, or deployment follows from this decision. Stage 13A-P4 remains physically open.

## Stage 13A-P3 — do not use delayed reachability as a physical wake boundary

**Status:** Accepted for Core 2026.9.4. Its pinned Bluetooth manager tracks
connectable presence across scanners, but remote stale-entry expiry and the
periodic unavailable check can take several minutes. A later unchanged
advertisement can dispatch after genuine manager-unavailability without cache
clearing; that does not make short meter OFF → ON cycles observable. Loss of all
proxy coverage can mimic physical OFF. [The source-derived assessment](STAGE13A_P3_ABSENCE_RETURN_ASSESSMENT.md)
therefore rejects absence/return as the primary GD82 automatic trigger. No
observer or production sync was added; manual refresh remains the supported path.

## Stage 13A — physical evidence before an automatic trigger

**Status:** Design review accepted; trigger implementation deferred. The
released v1.0.0 manual action and HA-selected scanner/proxy path remain intact.
HA changed-advertisement callbacks, availability transitions, and cached
replay do not establish GD82 subscription readiness, particularly after the
observed post-measurement failure. Prefer an opt-in, configured-address,
live-only callback only after physical state/episode correlation; reuse the
existing per-entry refresh lock and retain manual fallback. See
[the Stage 13A review](STAGE13A_AUTOMATIC_SYNC_ARCHITECTURE.md).

## Stage 12 Phase A — stable version and normal HACS release source

**Status:** Prepared, awaiting final approval. Use manifest `1.0.0` and a
future annotated `v1.0.0` Git tag with a published stable GitHub release.
HACS uses the release tag as its remote version; no custom ZIP or special
`hacs.json` release switch is needed for this single component layout. Keep
the exact [release note body](RELEASE_NOTES_V1.0.0.md) and [execution plan](STAGE12_V1_RELEASE_PREPARATION.md)
in Git for review. Neither tag nor release is created in Phase A.

## Stage 11 — validate default-branch HACS install before RC publication

**Status:** Accepted for the current controlled validation. Keep manifest
`0.1.0` while testing HACS installation of the default branch over the user's
manual component copy. HACS must download the files; it does not adopt an
existing local directory automatically. Preserve the Home Assistant config
entry/device/entity and back up the working component first. A same-branch
re-download can test package replacement but does not prove versioned update
notification. A future explicitly authorized release candidate should use a
single prerelease version across manifest, tag, and published release after
validator acceptance. No RC tag/release is created here. See [Stage 11](STAGE11_RELEASE_CANDIDATE_VALIDATION.md).

**Closure update:** The real HACS download, restart/reload, preserved
entry/device/entity, and manual count-four refresh through the named Atom Lite
proxy succeeded. HACS offered no safe re-download option, so versioned update
behavior remains untested. Stage 11 is complete for the applicable custom
repository validation scope; no tag or release was created.

## Stage 10 — default-branch HACS distribution before releases

**Status:** Accepted for the pre-RC packaging gate. Use one `custom_components/fora6_connect/` package, root `hacs.json`, original local brand icon, and a `0.1.0` development manifest version. HACS custom repositories can use the default branch without a GitHub release; release-based update selection begins only after an explicitly authorized release. Stage 11 should use matching manifest/tag/release SemVer for a candidate such as `1.0.0-rc.1`. CI validates HACS and hassfest; a separate controlled HACS UI install/update remains Stage 11. See [Stage 10](STAGE10_HACS_PACKAGING_READINESS.md).

## Stage 9 — require connection-specific proxy evidence

**Status:** Physically validated for the tested Lounge Atom Lite session. HA Bluetooth Connections showed the active FORA connection with Source explicitly naming the (Lounge) M5Stack Atom Lite ESPHome Bluetooth Proxy during the successful manual refresh; it disappeared shortly after. This direct evidence identifies the route for that run. Keep HA-selected scanner resolution and existing connector; no pinning/instrumentation is needed. Do not generalize to other routes or setups. Private device address and health data remain outside Git. See [Stage 9](STAGE9_ESPHOME_BLUETOOTH_PROXY_VALIDATION.md).

## Stage 8 — retain process-local current state and primary failure codes

**Status:** Accepted for the Stage 8 offline/synthetic hardening scope. Repeat manual refresh writes to the same existing sensor; only a complete, clean session replaces its value. A later failed refresh keeps the previous in-process value. Reload/restart intentionally starts unavailable until another explicit refresh; HA-native restoration is deferred because an old private health reading could appear current. The private action response already supplies selected meter-local time and bounded status, so no time/status entity attributes or diagnostic entity are added. When a refresh and its cleanup both fail, retain the original failure code and list cleanup errors separately. See [Stage 8](STAGE8_CURRENT_STATE_HARDENING_REVIEW.md). Stage 8H and Stage 9 remain separately gated.

**Stage 7H closure:** the user physically validated one manual count-four refresh on the real GD82. The later meter-local primary was selected, the existing entity became available, and no duplicate appeared. This validates the bounded path for that snapshot only. Keep the count-two/four plans, fail-closed equal-minute rule, and failure retention. Historical import, durable dedup/resume, arbitrary counts, and automatic triggers remain gated. This was the checkpoint before Stage 8; [Stage 7H record](STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md).

**Stage 6B3 physical decision:** the user-run HA migration confirms the factory BT MAC fallback preserved the configured object graph for this GD82. Keep the exact fallback policy scoped to this meter's observed identity; do not generalize fixed-address or uniqueness claims to all GD82s. Reset/update behavior is open. Stage 7 remains separately gated.

**Stage 6B3 identity decision:** the observed factory BT MAC is the best available fallback for this GD82, formatted as lowercase colon-separated octets. It is a private internal ConfigEntry/DeviceInfo identifier and Bluetooth connection, not a serial display value. An in-place registry update preserves the existing device/entity; no different-MAC merge is inferred. See [Stage 6B3](STAGE6B3_FACTORY_MAC_IDENTITY.md).

**Stage 6B2 evidence decision:** standard System ID `0x2A23` is a candidate, not yet the canonical identity. Eight-octet shape and all-zero/all-`0xFF` rejection are structural/local checks only. The exact raw bytes remain process-local for repeat comparison. No identity migration follows without a user-run stability result and separate policy gate. See [Stage 6B2](STAGE6B2_SYSTEM_ID_REVIEW.md).

**Stage 6B1 identity correction:** a known Bluetooth locator suppresses rediscovery, but remains transport metadata rather than logical identity. The current GD82 entry's unique ID was privately found to be the generic literal “Serial Number,” so it does not establish device-specific identity; do not silently migrate it to the BT MAC. Preserve the existing entry and hide the false serial field pending a separately authorized identity review. See [Stage 6B1](STAGE6B1_REDISCOVERY_LOCATOR_FIX.md).

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

**Stage 5A evidence update:** The later [unit review](STAGE5A_URIC_ACID_UNIT_EVIDENCE.md) establishes mg/dL as the app's unconverted raw/10 uric-acid base value. The product model and General-category numeric mapper now use it. Actual entity/device registration still waits for stable identity and config entry setup.

## ADR-016 — Separate Bluetooth candidate, model confirmation, and meter identity

**Status:** Accepted for Stage 6A policy review, 2026-09-27. The observed normalized name, advertised `0x1808`/`0x180A`, and connectability can select a candidate but cannot identify a unique meter. The already proven `0x22`/`0x24` project `0x4183` exchange can confirm a TD4183/GD82 protocol path during a future explicit setup flow; it also cannot identify one meter. The existing GATT inventory lists readable Serial Number String `0x2A25` and System ID `0x2A23`, but no value was read. Address stability and manufacturer-data semantics are unresolved. No permanent config-entry `unique_id`, `DeviceInfo.identifiers`, manifest Bluetooth matcher, automatic connection, or Config Flow is created until a meter-specific stable identifier is evidenced. [The Stage 6A record](STAGE6A_DISCOVERY_IDENTITY_POLICY.md) specifies the proposed passive comparison and bounded serial-read follow-up.

**Later Stage 6A1/6A1b physical update:** The user-run `0x2A25` read yielded usable UTF-8 text, and private exact-byte comparisons matched immediately and after a meter OFF/ON cycle. The value remains unpublished. This establishes stability for the tested meter and states, not global uniqueness.

## ADR-017 — Conditionally use the Device Information serial as meter identity

**Status:** Accepted as Stage 6A1c policy for a separately authorized Stage 6B implementation, 2026-09-27. Bluetooth SIG defines `0x2A25` as the serial for a particular device instance; it does not guarantee this manufacturer's entire population is collision-free. The FORA manual acknowledges serial-number labeling without linking it to `0x2A25`. Home Assistant accepts device serials as integration-domain unique IDs. A future guarded flow may use the exact validated UTF-8 `0x2A25` text for `ConfigEntry.unique_id` and `(DOMAIN, text)` for all `DeviceInfo.identifiers`, with private HA-internal persistence and no serial/address exposure in diagnostics or logs. Empty/unusable reads fail setup; duplicate or ambiguous identities fail closed; an address change requires re-confirmation rather than another entry. Project `0x4183` confirms model only, and address remains a runtime locator. No Config Flow, matcher, persisted serial, or registry device is added by this review. [The Stage 6A1c policy](STAGE6A1C_SERIAL_IDENTITY_POLICY.md) records sources, collision handling, privacy, and unresolved population uniqueness.

## Stage 6B guarded identity implementation

**Status:** Implemented and synthetic-tested on 2026-09-27; controlled physical setup validation pending. [Stage 6B](STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md) uses exact validated `0x2A25` UTF-8 text only for private ConfigEntry unique ID and shared DeviceInfo identifier. The Bluetooth address persists only as a mutable locator; same-serial/new-locator updates require explicit review and stop when the old locator is still connectable or another entry owns the new one. One uric-acid entity is registered unavailable until a later sync stage supplies an evidenced measurement. Population serial uniqueness and address rotation remain unresolved; no Stage 7 behavior is implied.

## Stage 7A — defer production history traversal

**Status:** Accepted evidence gate, 2026-09-27. [Stage 7A](STAGE7A_HISTORY_TRAVERSAL_DESIGN.md) finds that both TD4183 app versions parse a raw `0x2B` count and retrieve a raw slot through `0x25`/`0x26`, but their multi-parameter heuristic and one private `1 → 0 → 1` sequence do not prove general index order, wrap, latest selection, or a collision-safe deduplication key. Do not activate coordinator retrieval, cursor persistence, polling, or entity updates. A development-only bounded Stage 7B physical probe requires separate authorization. Meter-local time stays naive and separate from future ingestion time.

## Stage 6B device metadata refinement

**Status:** Accepted for the pre-GitHub metadata update, 2026-09-27. Exact validated `0x2A25` serial text is intentionally displayed through `DeviceInfo.serial_number` in the authenticated local Home Assistant device page, while remaining private in logs, diagnostics, actions, entity attributes, and public documentation. The serial remains the ConfigEntry unique ID and `(DOMAIN, serial)` device identifier. Home Assistant's supported `CONNECTION_BLUETOOTH` type carries the current runtime address as connection metadata at entity registration; it is not a ConfigEntry unique ID or `DeviceInfo` identifier. Name, manufacturer, and model remain `FORA 6 Connect`, `ForaCare`, and `GD82`. No IP is assigned to the BLE meter. Automatic pruning of an old registry connection after a confirmed locator change remains unresolved; no Config Flow or BLE behavior changes here.

## Stage 7B — fixed two-slot physical-evidence gate

**Status:** Implemented and physically validated for the exact count-two branch. [The Stage 7B action](STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) sends `1 → 0 → 1` only after identity and an exact raw-count-two metadata result. The user-run GD82 result returned valid pairs, within-session repeated index-one frame equality, and clean cleanup. This fixed physical result does not authorize general history traversal, deduplication, persistence, polling, or an entity update.

## Stage 7C — classify only the fixed pair sequence

**Status:** Development-only implementation and user-run physical semantic confirmation complete for the bounded count-two state. [The Stage 7C action](STAGE7C_SEMANTIC_PAIR_CONFIRMATION.md) repeats only the already validated Stage 7B command/index sequence and applies the existing pure record parser/model in memory. It returns only analyte/category/QC/sentinel classification and repeat-equality booleans. Semantic mismatch is reported without guessing its cause. No value, timestamp, raw frame, identifier, or hash is disclosed; no entity state, coordinator, persistence, deduplication, or production sync is changed. The sanitized real-device result matched the expected pattern; broader traversal remains gated.

## Stage 7D — defer general history synchronization

**Status:** Stage 7D offline review complete. [The evidence review](STAGE7D_GENERAL_TRAVERSAL_DEDUP_REVIEW.md) finds that the TD4183 handler discards the parsed wire newest-index field, the general import loop is not reliably recoverable, and the app's time/type/value database comparison is not a collision-safe meter record identity. No raw-index cursor, content fingerprint, or production history path is authorized. The proposed next gate is a separately authorized, read-only Stage 7E fixed four-slot observation if that meter state occurs naturally.

## Stage 7F — separate current sensor state from historical import

**Status:** offline design review complete. [The evidence review](STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md) conditionally supports a manually triggered current-state refresh for only raw counts two/four and only when exactly one valid General uric-acid primary is present. It does not choose by highest index or maximum naive meter-local time. A single current state does not require a durable per-record dedup key; importing historical observations still does. Stage 7G requires separate authorization for implementation, and production historical synchronization remains gated.

## Stage 7G update

Stage 7G is a bounded evidence step ahead of Stage 7F’s proposed production refresh. At exactly four raw slots, compare only validated General uric-acid primaries 0 and 2 within one session. Stage 7G1 separately permits their decoded values and meter-local times in the private development response so the user can correlate them locally with the display. It selects no production latest record. A one-snapshot relation does not establish general index order.

## Stage 7G2 — bounded timestamp selection policy

**Status:** Stage 7G bounded chronology scope complete on one real four-slot GD82 snapshot. Raw primary 0 had the later parsed meter-local time than raw primary 2, so highest-index selection is contradicted in that state (**LIVE-CORROBORATED**). For a separately authorized Stage 7H manual-only current-state refresh, prefer the strict maximum naive meter-local time among eligible primaries in a complete tested-count snapshot; equal-minute ties fail closed. This is a meter-clock policy, not a universal actual-time or raw-index rule. No production sync, history import, or persistent dedup is implemented. The retained apps' `m0()` two-decimal mmol/L record display uses `FLOOR`; meter firmware's exact arithmetic remains **UNRESOLVED**. See [conversion evidence](URIC_ACID_UNIT_CONVERSION.md).
