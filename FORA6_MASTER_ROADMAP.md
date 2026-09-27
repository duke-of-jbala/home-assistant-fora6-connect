# Home Assistant — FORA 6 Connect: master roadmap

This is the authoritative project roadmap. `ROADMAP.md` points here. Stage gates require explicit user authorization; completing one stage does not start the next. **Stage 0 and Stage 1 are complete; Stage 2 is in progress.** Stages 2A–2E are complete. The real Stage 2E Home Assistant identity action succeeded with the meter ON. **Stage 2F remains in progress:** its offline evidence gate passed and its development-only one-slot record probe is implemented; physical Home Assistant validation is pending.

## Project identity and goal

| Item | Value |
| --- | --- |
| Repository | `duke-of-jbala/home-assistant-fora6-connect` |
| Local checkout | This repository's active checkout; do not record private absolute paths in public Git. |
| Home Assistant integration domain | `fora6_connect` |
| Display name | FORA 6 Connect |
| Target device | FORA 6 Connect |
| Model/variant | GD82 |
| Target distribution | HACS-compatible Home Assistant custom integration |
| License | MIT |
| Versioning | Semantic Versioning |

Intended proxy path: **FORA 6 Connect → BLE → ESPHome Bluetooth Proxy → Home Assistant Bluetooth → `fora6_connect` integration**. A local Home Assistant Bluetooth adapter is also an intended transport. ESPHome remains a **generic Bluetooth proxy**: all FORA-specific communication and decoding belong to the integration. The protocol parser remains independent of Home Assistant, ESPHome, Bluetooth adapters, and physical hardware so captured raw frames can be tested directly.

The active checkout is at the canonical local path. `CURRENT_STATUS.md` records the observed repository state and next gate. The GitHub URL is a local remote target; this project work has not created or contacted a remote repository.

## Evidence register

### Confirmed project and documentary facts

- The target product is FORA 6 Connect, model/variant GD82. The [ForaCare FAQ Rev 5.5, Q36–Q37](https://www.foracare.ch/wp-content/uploads/2023/03/3.1-BGM-FAQ_Rev5.5_230313.pdf) has now been independently reviewed: it documents service `00001523-1212-efde-1523-785feabcd123`, characteristic `00001524-1212-efde-1523-785feabcd123` with Write/Notify, and associates GD82 with iFORA HM. It does not provide command bytes. See `docs/STAGE2_PROTOCOL_ACQUISITION.md`.
- The integration records these UUIDs and offers manually invoked Stage 1B GATT inventory and Stage 1C notification-metadata actions. Stage 2D adds offline frame/project/scaling helpers. Stage 2E's separate development-only Home Assistant action sent exactly two captured custom `1524` requests on the real GD82 with the meter ON and confirmed project `0x4183`. Stage 2F adds a separately invoked one-slot record-response probe, pending physical validation. There is no production Bluetooth discovery matcher, record parser, production FORA write path, synchronization, or measurement entity. Earlier builds stopped at discovery; the later direct-connect Stage 1B probe succeeded through Home Assistant without application I/O.
- The UUID pair alone is insufficient proof that an observed BLE device is a FORA 6 Connect; similar UUIDs may be reused.

### User-supplied real-device and proxy observations

- In screenshots reviewed externally, a generic iPhone BLE scanner saw the real meter as `FORA 6 CONNECT` while its blue Bluetooth indicator flashed. It reported connectable, about −50 dBm at close range, and a successful connection marked `BONDED`. The scanner may have initiated bonding automatically; this observation does not establish why the GD82 bonds or whether the tested Home Assistant path enforces the Glucose Profile security requirement.
- The iPhone GATT view showed Device Information `0x180A` with readable standard fields, Glucose `0x1808` with `0x2A18` Notify, `0x2A34` Notify, `0x2A51` Read, and `0x2A52` Write/Indicate; and the documentary FORA custom `1523` service and `1524` characteristic with Write/Notify. This confirms their presence on the real device without establishing proprietary packet semantics.
- Home Assistant showed Bedroom and Lounge ESPHome proxies in `Auto (passive)` mode, with 0/3 and 1/3 connection slots in use respectively. Lounge was temporarily switched to Active scanning. In the tested state, the iPhone still saw FORA and Home Assistant's Advertisement Monitor showed other BLE devices but not FORA. This is a Home Assistant visibility gap in that test, not evidence of meter radio failure.
- Before the retest, Lounge used the official M5Stack Atom Lite ESPHome Bluetooth proxy package and an explicit `esp32_ble_tracker` scan interval of `320ms` and window of `30ms`. The approximately 9.4% scan duty cycle was a plausible missed-advertisement hypothesis, not an established cause.
- **User-supplied controlled retest:** the explicit `320ms`/`30ms` override was removed and Lounge was rebuilt/reflashed with ESPHome `2026.9.0`; Bedroom remained unchanged as the control. With Lounge temporarily set to Active, Home Assistant Advertisement Monitor then detected `FORA 6 CONNECT` through Lounge. This establishes a working Lounge ESPHome → Home Assistant advertisement path in the tested Active state. Removal and reflash occurred together, so the result does not isolate scan timing as the cause of the prior failure.
- **Auto-mode retest:** Lounge was returned to Auto. The prior FORA row remained in Advertisement Monitor, but its Updated age did not refresh during the test. A fresh Auto-mode FORA advertisement was not confirmed; this does not show that Auto cannot work.
- **Stage 1B real probe observation, user-supplied:** multiple calls to the first development probe returned `No fresh FORA 6 CONNECT advertisement was observed during the active scan.` No Home Assistant GATT connection was attempted and no FORA operation was transmitted. This does not establish a meter or proxy GATT failure. EcoFlow activity and unrelated ESPHome API warnings are not FORA evidence.
- **Stage 1B targeted-wait retest, user-supplied:** after installing the revised build, the probe returned `No known FORA 6 CONNECT candidate is available for targeted active scanning; first observe it in Home Assistant Bluetooth.` The meter had previously appeared in Advertisement Monitor. The code stopped before its targeted wait, Home Assistant GATT connection, or any FORA operation. The previous UI observation does not prove the device remained in current HA discovery history. The connectable-only candidate gate was too restrictive for general advertisement evidence.
- **Stage 1B general-discovery retest, user-supplied:** the action again returned no known FORA candidate, now reporting `general discoveries: 214; name matches: 0; connectable scanners: 2`. Home Assistant Bluetooth and two connectable scanners were operating, but the intermittent meter was absent by name from the current cache. Home Assistant documents that this API contains devices still present in its cache. No targeted wait, HA GATT connection, or FORA operation occurred. The result does not indicate meter, proxy, or GATT failure.
- **Advertisement-detail popup, user-supplied:** the user manually opened the `FORA 6 CONNECT` row in Home Assistant's Advertisement Monitor. The Complete Local Name had **five trailing NUL characters**; the popup marked the device connectable, showed BLE flags, advertised `0x1808` Glucose and `0x180A` Device Information, and showed manufacturer-specific data present. Custom `0x1523` was absent from this advertisement but was present with `0x1524` in the earlier connected iPhone GATT inventory. Advertised services are not the complete connected GATT inventory. This was Home Assistant UI advertisement evidence; the development probe did **not** return that packet and still failed with `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` The prior literal name comparison would reject such padding if the probe received it, but the popup does not prove that it did. A separate active-wait/API-path issue remains possible. No GATT connection or FORA operation followed.
- **Normalization-build real retest, user-supplied:** the installed trailing-NUL correction still returned `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` The probe did not resolve a connectable FORA BLEDevice, connect, enumerate GATT, or transmit any FORA operation. ESPHome status=133 events around EcoFlow River 3 Plus reconnections do not establish a FORA failure; the probe had not reached connection.

- **Deduplication/timestamp-build real retest, user-supplied:** the installed revision again returned `No fresh FORA 6 CONNECT advertisement was observed during the targeted active wait.` It did not resolve a FORA BLEDevice, connect, enumerate GATT, or transmit a FORA operation. Advertisement Monitor independently showed FORA when Lounge was manually Active; UI visibility and integration callback delivery remain separate. This result does not isolate the cause of the timeout.

- **Direct-connect Stage 1B real success, user-supplied privacy-safe action result:** Home Assistant resolved a connectable FORA BLEDevice, connected, enumerated five GATT services, and disconnected cleanly. The response reported normalized local name `FORA 6 CONNECT`, confirmed advertised name, last service info available, and two connectable scanners. It reported Device Information `0x180A`, Glucose `0x1808`, and custom `1523`/`1524` with all previously expected characteristic properties. Generic Access `0x1800` and Generic Attribute `0x1801` were also returned. The response did not identify which scanner/adapter handled the connection. This validates Home Assistant-side GATT transport; it does not prove Auto-mode discovery or application protocol semantics. See `docs/PROTOCOL.md` for the full sanitized inventory.

### Working hypotheses, not validated behavior

- At the Stage 1 passive-observation gate, it was unknown whether a request preceded stored-data notifications. The later Stage 2C captured import used application requests over custom `1524`; behavior for passive observation in other meter states remains unknown.
- The prior Lounge scan timing may have contributed to missed FORA advertisements, but removal and ESPHome reflash were combined in the retest, so causation remains unresolved.
- The exact GD82 variant may support some or all of the expected analytes listed below.

### Unknown

Address stability/randomization/identity behavior (Stage 6), manufacturer-data meaning (revisit in Stage 6 if useful for identification or earlier if protocol evidence establishes relevance), any additional advertised UUIDs, detailed Home Assistant scanner-source/RSSI relationship beyond the reported Lounge source, the exact scanner/adapter selected for the successful GATT connection (Stage 9), fresh Auto-mode advertisement behavior (Stage 6), notification behavior under other meter states or requests, the cause of the observed `2A18`/`2A34` subscription failures, and whether the GD82 enforces Glucose security in the tested Home Assistant/ESPHome path; unresolved command fields/responses beyond the captured exchanges, record byte layout, analyte identifiers, timestamp bits/timezone, status and control-solution flags, non-uric-acid units/scaling, error responses, and exact GD82 analyte support. A particular ESPHome proxy connection path is not confirmed. `docs/PROTOCOL.md` is the detailed evidence register. Do not fill unknowns with guesses.

## Stage plan and gates

| Stage | Scope | Status | Entry criterion | Exit criterion |
| --- | --- | --- | --- | --- |
| 0 — Repository/bootstrap | Skeleton, tests, documentation, architecture freeze, local checkpoint. | **Complete** | Fixed project decisions supplied. | Requested files, guardrails, validation baseline, and local Stage 0 commit exist. |
| 1 — FORA 6 Connect BLE discovery | Establish real advertisement/name, connectability, Home Assistant GATT structure, and bounded passive notification behavior; record unresolved production-discovery questions. | **Complete: Stage 1A, 1B, and 1C complete; named unknowns deferred** | Stage 1A preparation completed; Stage 1B and 1C observations explicitly authorized. | Real evidence reviewed; Stage 6/9 deferrals recorded explicitly. |
| 2 — Protocol acquisition / reverse engineering | Use legitimate public documentation and/or controlled device/app observations to establish actual commands and responses. | **In progress — 2A–2E complete; 2F offline gate passed, physical one-slot test pending** | Stage 1 evidence reviewed and explicit Stage 2 authorization; both met. | Each claimed protocol behavior has a source or captured observation, confidence, and open questions. |
| 3 — Protocol parser and captured-frame fixtures | Extend the HA-independent Stage 2D frame foundation to evidence-backed record decoding with sanitized fixtures. | **Not started; Stage 2D frame foundation exists** | Record byte layout and analyte identity supported by further evidence. | Decoding tests cover supported frames, invalid data, and evidence-backed record semantics without HA or hardware. |
| 4 — Home Assistant Bluetooth transport | Implement connection, notification, and retry-safe handling through supported HA Bluetooth APIs for local adapters and ESPHome proxies. | **Not started** | Validated protocol operations and explicit authorization. | Transport handles documented communication and recoverable connection failures without a hard-coded local interface. |
| 5 — Measurement/entity model | Represent validated analytes, units, status, and one-device association in HA. | **Not started** | Validated record semantics. | Supported entities expose correct measurements; control-solution results stay distinct when the protocol supplies status. |
| 6 — Config flow and Bluetooth discovery | Robust setup without claiming unrelated devices sharing similar UUIDs. | **Not started** | Reliable device identification evidence. | Discovery requires confirmation and prevents duplicate or false identification. |
| 7 — Historical-memory synchronization | Retrieve records, deduplicate, resume, and preserve original meter timestamps separately from sync time. | **Not started** | Evidence-backed memory protocol and record identifiers/timestamps. | Repeated/interrupted syncs do not misdate or duplicate records. |
| 8 — Diagnostics and error handling | Non-sensitive diagnostics and predictable recovery. | **Not started** | Transport and sync behavior established. | Diagnostics omit private data and failures have useful recovery paths. |
| 9 — ESPHome Bluetooth Proxy validation | Validate end-to-end operation using the user's existing generic proxy architecture. | **Not started** | Functional integration and authorized environment. | Confirmed discovery, connection, sync, and recovery through the proxy. |
| 10 — HACS packaging | Verify repository, manifest, brand assets, and installation layout against then-current HACS requirements. | **Not started** | Working integration and public packaging plan. | HACS checks and install/update validation pass. |
| 11 — Documentation and release candidate | Public installation, compatibility, privacy, troubleshooting, and release-candidate validation. | **Not started** | Validated functionality and packaging. | Documentation and release-candidate checks are complete. |
| 12 — v1.0.0 release | Stable public release. | **Not started** | Release candidate validated and explicit release authorization. | v1.0.0 is published after approval. |

### Stage 1 subdivisions

- **Stage 1A — passive Bluetooth discovery and environment verification: complete with named production-discovery unknowns deferred.** User-supplied, externally screenshot-reviewed iPhone observations established the real meter's local name and connectability. The controlled Lounge retest established Home Assistant advertisement visibility in Active mode after removal of the explicit scan override and an ESPHome `2026.9.0` reflash. The unchanged Bedroom proxy served as a control. The Advertisement Monitor row did not refresh during the later Auto retest, so that manual test did not confirm a fresh Auto-mode advertisement. A later manually viewed popup established the sanitized advertisement fields above; the Stage 1B action did not return its packet. Address behavior and manufacturer payload meaning remain unknown. A UUID or name match alone is not proof of identity.
- **Stage 1B — observational GATT inspection: complete for Home Assistant-side transport/GATT.** The real direct-connect development action resolved a connectable BLEDevice, connected, returned five services with all expected Device Information, Glucose, and custom 1523/1524 metadata/properties, and disconnected cleanly. The action did not read/write a characteristic, subscribe, pair, retrieve records, or send a FORA command. Two connectable scanners were reported, but the selected connection path is unknown; do not claim a particular ESPHome proxy handled it. Previous advertisement callback timeouts were discovery-layer results and did not demonstrate a GATT failure. The direct result does not resolve Auto-mode or production identification. Passive notification behavior was separately observed in Stage 1C; proprietary protocol semantics remain unknown. Production automatic discovery remains Stage 6 work.

- **Stage 1C — bounded notification observation: complete for the authorized passive gate.** The first real build reached `2A18` subscription and aborted there, so it provided no result for `2A34` or custom `1524`. In the second user-reported real run, the revised observer connected and attempted all three: `2A18` and `2A34` failed subscription with safe `BleakError` summaries; custom `1524` subscribed successfully. Across 30 seconds, custom `1524` delivered zero notifications. The user pressed the meter's arrow/navigation keys while observation was active; the display stayed on the sole existing uric-acid result. No new measurement was taken. Unsubscription and disconnect were clean. Passive subscription plus navigation/display of that record produced no custom notification in this run. Only uric acid has been measured on this physical meter; other analytes have not been tested. This does not prove whether custom notifications require an application request or whether other analytes behave alike.
- **Security hypothesis, not a diagnosis:** [Bluetooth SIG Glucose Profile 1.0.1, sections 6.1–6.2](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/GLP_v1.0.1/out/en/index-en.html) requires bonding between Sensor and Collector and LE Security Mode 1, Security Level 2 or 3 for supported Glucose Service characteristics. The earlier iPhone connection was observed as bonded. Missing bonding/encryption remains a strong hypothesis for the standard Glucose subscription failures; proxy or descriptor-notify failure remains possible. Pairing is not authorized. Bleak/Home Assistant CCCD operations from `start_notify`/`stop_notify` were the only authorized subscription activity; no application characteristic read/write, RACP, retrieval, decoding, or FORA command was performed.

## Deferred Stage 1 unknowns and current Stage 2 gate

The Stage 1 evidence review is complete. These unresolved questions **do not block Stage 1 closure** and remain open at their assigned gates:

| Unresolved question | Deferred gate |
| --- | --- |
| Fresh Auto-mode advertisement behavior | Stage 6 production Config Flow / Bluetooth discovery validation. The prior Auto retest did not confirm a fresh advertisement; Auto is not known to be broken. |
| Bluetooth address stability, randomization, and identity behavior | Stage 6 production discovery and duplicate-device handling. No stability claim is established. |
| Exact Home Assistant scanner/ESPHome proxy selected for successful GATT connections | Stage 9 end-to-end ESPHome Bluetooth Proxy validation. The earlier action reported two connectable scanners but did not identify the selected path. |
| Manufacturer-data meaning | Unknown; revisit in Stage 6 if useful for identification, or earlier only if later protocol evidence establishes relevance. No payload meaning is inferred. |

Stage 2A reviewed manufacturer sources; Stage 2B statically inspected mirror-distributed iFORA HM 1.7.6 and 1.7.9, without an independent official signing anchor. Stage 2C's privacy-safe live capture from a **patched, locally re-signed 1.7.6 research copy** confirmed custom `1523/1524`, eight-byte summed frames, `0x22` wake, `0x24` project query, physical project `0x4183`, and indexed `0x25`/`0x26` uric-acid import participation. Stage 2D added offline frame/project/scaling helpers. **Stage 2E's user-supplied real Home Assistant result:** with the meter ON, custom `1524` subscription, valid `0x22`/`0x24` exchanges, project `0x4183`, clean unsubscribe and disconnect all succeeded. This validates the bounded identity path. Stage 2F's offline review traced exact, read-oriented current-user requests for `0x2B` slot metadata and a paired `0x25`/`0x26` read of raw index zero. A development-only action now implements only that bounded sequence after the Stage 2E identity gate; it has **not** been physically tested. See `docs/STAGE2F_TD4183_RECORD_PROBE.md`. **Exact next gate: one user-run Stage 2F physical action and review of its privacy-safe result.** `0x33` is prohibited from the Stage 2F action; production sync, automatic connection, pairing, and RACP remain outside scope.

## Deferred product work

Expected measurements, subject to protocol validation and exact GD82 support: blood glucose, haematocrit, haemoglobin, beta-ketone/beta-hydroxybutyrate, total cholesterol, and uric acid. Possible diagnostics include last measurement time, last successful sync, synchronization state, record position/count, and useful signal strength. Historical retrieval, deduplication, resume state, timestamp handling, control-solution classification, entity creation, configuration flow, and full HACS readiness are later-stage work. No unverified entity is active in Stage 0.

## Frozen architecture decisions

The accepted decisions are detailed in `docs/DECISIONS.md`:

1. **ADR-001:** Home Assistant performs FORA-specific communication and decoding.
2. **ADR-002:** ESPHome Bluetooth Proxy is transport only and remains generic.
3. **ADR-003:** The protocol parser is independent of Home Assistant.
4. **ADR-004:** Documented or captured evidence with provenance precedes protocol implementation; tests use sanitized evidence-derived fixtures.
5. **ADR-005:** One physical meter is represented by one Home Assistant device, with later entities attached to it.
6. **ADR-006:** Original meter measurement time is preserved separately from synchronization/ingestion time.
7. **ADR-007:** Private health data and identifiable raw BLE captures are excluded from the public repository.

Use supported Home Assistant Bluetooth APIs; do not hard-code a direct local interface. Future connections must work through eligible proxies and follow then-current retry-safe HA/Bleak guidance. A UUID match alone must never claim device identity. Where the protocol provides test/control-solution status, those readings must not silently become ordinary health readings.

## Privacy and evidence rule

Do not commit identifiable health measurements, secrets, meter identifiers, MAC addresses from private captures, or raw private BLE captures. Keep raw material outside Git. Sanitize any public fixture, record its provenance and transformations, and verify that sanitization did not invalidate the tested behavior. Record observed facts separately from interpretations and hypotheses.

## Release and HACS strategy

- `0.0.0` in the custom integration manifest is a development placeholder required by Home Assistant; it is not a release. Use Semantic Versioning for actual releases, with v1.0.0 only after Stage 11 validation and explicit authorization. Keep unreleased changes in `CHANGELOG.md`; do not invent tags or releases.
- The current repository has the single `custom_components/fora6_connect/` integration layout, `manifest.json`, root `hacs.json`, and README. Stage 10 must recheck current HACS rules, including a public GitHub repository with description/topics/README, required manifest metadata, integration brand assets, and installation/update behavior. This Stage 0 skeleton is not yet HACS-ready.
- `translations/en.json` is the custom integration runtime translation source; the requested `strings.json` is an inert scaffold file. Discovery/config flow and entity setup remain disabled until their evidence gates.

The last completed checkpoint, task changes, test results, and next gate are in `CURRENT_STATUS.md` and `CODEX_HANDOVER.md`. The exact SHA and working-tree state after a task's own commit belong in the post-commit report, avoiding a self-referential SHA in tracked files.
