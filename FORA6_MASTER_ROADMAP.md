# Home Assistant — FORA 6 Connect: master roadmap

This is the authoritative project roadmap. `ROADMAP.md` points here. Stage gates require explicit user authorization; completing one stage does not start the next. **Stage 0 is complete; Stage 1 is in progress; Stage 2 is not authorized.**

## Project identity and goal

| Item | Value |
| --- | --- |
| Repository | `duke-of-jbala/home-assistant-fora6-connect` |
| Canonical local path | `<local checkout>` |
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

- The target product is FORA 6 Connect, model/variant GD82. The Stage 0 brief reports that FORA documentation lists service UUID `00001523-1212-efde-1523-785feabcd123` and characteristic UUID `00001524-1212-efde-1523-785feabcd123`, with write and notify properties. The underlying document has not been independently inspected in this repository.
- The integration skeleton records these UUIDs but does not register Bluetooth discovery, connect to a meter, decode packets, or expose measurements.
- The UUID pair alone is insufficient proof that an observed BLE device is a FORA 6 Connect; similar UUIDs may be reused.

### User-supplied real-device observations, screenshots reviewed externally

- A generic iPhone BLE scanner saw the real meter as `FORA 6 CONNECT` while its blue Bluetooth indicator flashed. It reported connectable, about −50 dBm at close range, and a successful connection marked `BONDED`. Whether the meter requires bonding is unknown; the scanner may have initiated it automatically.
- The iPhone GATT view showed Device Information `0x180A` with readable standard fields, Glucose `0x1808` with `0x2A18` Notify, `0x2A34` Notify, `0x2A51` Read, and `0x2A52` Write/Indicate; and the documentary FORA custom `1523` service and `1524` characteristic with Write/Notify. This confirms their presence on the real device without establishing proprietary packet semantics.
- Home Assistant showed Bedroom and Lounge ESPHome proxies in `Auto (passive)` mode, with 0/3 and 1/3 connection slots in use respectively. Lounge was temporarily switched to Active scanning. In the tested state, the iPhone still saw FORA and Home Assistant's Advertisement Monitor showed other BLE devices but not FORA. This is a Home Assistant visibility gap in that test, not evidence of meter radio failure.
- Lounge uses the official M5Stack Atom Lite ESPHome Bluetooth proxy package and an explicit `esp32_ble_tracker` scan interval of `320ms` and window of `30ms`. The approximately 9.4% scan duty cycle is a plausible missed-advertisement hypothesis, not an established cause.

### Working hypotheses, not validated behavior

- The meter may expose stored measurements through the documented characteristic.
- Home Assistant may be able to connect through an eligible ESPHome Bluetooth Proxy. End-to-end operation has not been tested.
- The Lounge scan timing may contribute to missed FORA advertisements; a controlled A/B test is needed before attributing cause.
- The exact GD82 variant may support some or all of the expected analytes listed below.

### Unknown

Address behavior, manufacturer/service data, advertised UUIDs, Home Assistant scanner-source/RSSI relationship, Home Assistant-side connectability/GATT, raw notification behavior, and whether bonding is required; application commands/responses, framing, checksums, identity response, memory retrieval, record layout, analyte codes, timestamps, status and control-solution flags, units/scaling, error responses, and exact GD82 analyte support. `docs/PROTOCOL.md` is the detailed evidence register. Do not fill unknowns with guesses.

## Stage plan and gates

| Stage | Scope | Status | Entry criterion | Exit criterion |
| --- | --- | --- | --- | --- |
| 0 — Repository/bootstrap | Skeleton, tests, documentation, architecture freeze, local checkpoint. | **Complete** | Fixed project decisions supplied. | Requested files, guardrails, validation baseline, and local Stage 0 commit exist. |
| 1 — FORA 6 Connect BLE discovery | Establish advertisement/local name, address behavior, manufacturer data, advertised UUIDs, connectability, GATT structure, characteristic properties, and raw notification behavior. | **In progress: iPhone identity/GATT observed; Home Assistant proxy visibility unsuccessful in tested state** | Stage 1A explicitly authorized; controlled meter and capture path to be verified. | Observations, provenance, gaps, and sanitized/non-sensitive findings recorded; Home Assistant-side GATT needs discovery and separate authorization. |
| 2 — Protocol acquisition / reverse engineering | Use legitimate public documentation and/or controlled device/app observations to establish actual commands and responses. | **Not authorized** | Stage 1 evidence reviewed and Stage 2 explicitly authorized. | Each claimed protocol behavior has a source or captured observation, confidence, and open questions. |
| 3 — Protocol parser and captured-frame fixtures | Build an HA-independent parser with sanitized, evidence-derived regression fixtures. | **Not started** | Protocol behavior supported by Stage 2 evidence. | Decoding tests cover supported frames, invalid data, and evidence-backed record semantics without HA or hardware. |
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

- **Stage 1A — passive Bluetooth discovery and environment verification:** preparation is complete. User-supplied, externally screenshot-reviewed iPhone observations established the real meter's local name and connectability. Home Assistant's Advertisement Monitor did not show FORA in the tested proxy state despite seeing other devices. The guide and private-use template remain available for the controlled repeat. Advertisement fields, address behavior, and scanner-source details remain unknown. A UUID or name match alone is not proof of identity.
- **Stage 1B — observational GATT inspection:** the real-device GATT inventory was observed through the iPhone scanner, but the Home Assistant/ESPHome proxy connection and GATT path has **not** been validated or authorized for this repository task. After Home Assistant discovery and separate authorization, use Home Assistant Bluetooth APIs to resolve a connectable path and inspect GATT. Notification subscription needs separate authorization. No FORA application writes during Stage 1.

## Current next gate

**Correct/test Lounge ESPHome BLE scan timing in a controlled A/B test, repeat Home Assistant Advertisement Monitor observation, and determine whether Home Assistant can see `FORA 6 CONNECT` through the proxy.** Only after Home Assistant discovery and separate authorization, validate Home Assistant-side connectability/GATT. Stage 1 remains in progress. Do not begin Stage 2 or invent/send FORA application commands.

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
