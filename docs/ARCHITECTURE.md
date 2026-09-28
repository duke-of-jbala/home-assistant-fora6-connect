# Architecture

**Post-v1 action surface audit:** [The complete registration review](POST_V1_ACTION_SURFACE_AUDIT.md) classifies 17 Home Assistant actions. Current refresh and bounded history are the intended normal product actions; the transaction-readiness probe remains temporarily necessary for open Stage 13A-P4. Older address-input probes have a separate global lock and should not remain part of a polished user action list. A separately authorized future cleanup should register only product actions after P4 and physical history validation. This review changes no runtime behavior or deployed build.

**Stage 8H-B synthetic implementation:** [The bounded history action](STAGE8H_B_BOUNDED_HISTORY_IMPLEMENTATION.md) reuses a shared fixed count-two/four transaction reader, pure record parsers, and the existing per-entry GATT lock. Its manual configured-entry response contains one or two discrete General uric-acid measurements and never updates the current-state sensor, Recorder, statistics, or a persistent history store. Equal-minute count-four history retains both results; current-state selection still fails closed. No physical history read or deployment occurred. The deployed P4 probe remains in place for its pending post-measurement comparison.

**Stage 8H-A history decision:** [The bounded architecture review](STAGE8H_A_BOUNDED_HISTORY_ARCHITECTURE.md) selects a future explicitly invoked configured-entry response action for one count-two or two count-four General uric-acid measurements. It would return discrete mg/dL results with timezone-unknown meter-local minutes, sort by those minutes, and mark equal-minute chronology ambiguous. It would reuse validated fixed reads/parser/model while leaving the current sensor, Recorder, statistics, persistence, and P4 probe unchanged. This is documentation only; Stage 8H-B implementation requires separate authorization.

**Post-v1 Stage 13A:** [The auto-trigger review](STAGE13A_AUTOMATIC_SYNC_ARCHITECTURE.md) finds no configured-entry advertisement callback today. Discovery remains in the config flow; manual refresh resolves a connectable HA-selected device when invoked. An eventual opt-in trigger would reuse the per-entry coordinator and need a physically supported readiness/episode signal. No automatic callback or sensor change is implemented. Released `v1.0.0` remains at `dd26b65ab467381db58ba7a525c6b8eabca8e00a`.

**Historical release preparation boundary:** HACS installs the single self-contained `custom_components/fora6_connect/` directory; root `hacs.json`, README, and CI metadata describe distribution only. [Stage 12 Phase A](STAGE12_V1_RELEASE_PREPARATION.md) prepared the manifest at `1.0.0` before the now-published tag/release. Stage 10's hassfest corrections and Stage 11's real HACS installation are retained evidence. The manual refresh, Bluetooth, identity, protocol, coordinator, and sensor behavior remains unchanged after release.

**Stage 9 physical route closure:** Home Assistant Bluetooth → Connections identified the Lounge M5Stack Atom Lite ESPHome Bluetooth Proxy as Source of the active FORA connection during the successful count-four manual refresh; the row disappeared after completion. This directly corroborates proxy traversal for that run. The existing HA-selected transport remains unchanged; no scanner pinning or production instrumentation was added. See [Stage 9](STAGE9_ESPHOME_BLUETOOTH_PROXY_VALIDATION.md).

**Stage 8 hardening:** the per-entry manual coordinator retains an earlier refresh failure when cleanup also fails and reports cleanup errors separately. Repeat calls replace the current process-local value in the same state holder and entity; reload creates a fresh unavailable state. No restore, new attribute, diagnostic entity, automatic trigger, or history import is added. Separate entries retain separate locks and state. See [the Stage 8 review](STAGE8_CURRENT_STATE_HARDENING_REVIEW.md).

**Stage 7H physical closure:** the user validated a count-four manual refresh on the real GD82. The existing sensor became available with the selected current state; no duplicate entity appeared. The physical result confirms this bounded path and does not generalize ordering to other snapshots/counts. See [Stage 7H](STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md).

**Stage 7H implementation:** `coordinator.py` owns an explicit, per-entry, single-flight manual current-state refresh. It reuses the Stage 4 transport, validates project identity and only raw counts two/four, reads complete fixed slot plans, filters General uric-acid primaries, and publishes one mg/dL measurement to `MeasurementState` only after clean unsubscribe/disconnect. `sensor.py` listens to explicit state replacements and performs no BLE I/O. Meter-local naive time stays in the product measurement; successful ingestion time is a separate process-local aware UTC field. The action selects a configured entry and requires no manually entered MAC. There is no startup, advertisement, scheduled, or periodic refresh, and no historical import.

**Stage 6B3 physical closure:** the user confirmed the existing ConfigEntry unique ID now has canonical Bluetooth MAC form after restart. The same entry, device, entity, connection metadata, and GD82/ForaCare metadata remained; the entity is still unavailable and no Add card appeared. This validates the in-place migration on one meter. See [the closure record](STAGE6B3_FACTORY_MAC_IDENTITY.md); broad address stability remains unresolved.

**Stage 6B3:** [Factory MAC identity](STAGE6B3_FACTORY_MAC_IDENTITY.md) is a guarded fallback for the tested GD82 after the generic `0x2A25` text and unusable `0x2A23` result. Existing placeholder entry/device identifiers are migrated in place before the inert sensor loads; the entity unique ID remains based on the unchanged entry ID. No sync or BLE read occurs at setup.

**Stage 6B2:** [The System ID review](STAGE6B2_SYSTEM_ID_REVIEW.md) adds read-only development actions at the Device Information boundary. Private raw `0x2A23` bytes may exist in one process-local comparison holder, but never enter ConfigEntry, DeviceInfo, sensor state, diagnostics, or protocol history. Existing production identity and Stage 7 paths remain unchanged.

**Stage 6B1:** [The locator follow-up](STAGE6B1_REDISCOVERY_LOCATOR_FIX.md) suppresses configured-address discovery before any active exchange. A private check showed this meter's retained unique ID is a generic placeholder, so the current device-specific identity is unresolved. New flows reject that placeholder; existing entry/device/entity are preserved and the false serial display is hidden on reload. No synchronization was added.

## Intended data path

```text
FORA 6 Connect (GD82) --BLE--> Home Assistant Bluetooth stack
                                 ^
                                 | optional generic transport
                         ESPHome Bluetooth Proxy

Home Assistant Bluetooth stack --> custom_components/fora6_connect
                                   |-- Bluetooth transport
                                   |-- HA-independent FORA protocol parser
                                   |-- measurement synchronization
                                   |-- entities and diagnostics
```

The ESPHome proxy forwards Bluetooth activity; it has no FORA-specific code. Stage 4 transport resolves connectable devices through Home Assistant's Bluetooth APIs so either a local adapter or an eligible proxy can carry a connection. Home Assistant chooses the actual path; Stage 9's user-supplied Connections Source now confirms the Lounge Atom Lite carried the tested session. Other adapter/proxy paths remain untested.

## Boundaries

- `bluetooth.py`: reusable Stage 4 HA Bluetooth session for connection, custom characteristic validation, notification exchange, bounded waits, and cleanup. It delegates frame validation to `protocol.py` and chooses no FORA command or health interpretation.
- `protocol.py`: pure-Python frame validation and evidence-backed offline TD4183 record-part parsing, testable with synthetic bytes alone. No HA, ESPHome, adapter, or physical meter requirement. Meter-local time remains separate from ingestion time; unknown timezone, non-uric-acid units, and flags are not invented.
- `models.py`: pure-Python Stage 3 combined TD4183 record over the two validated protocol parts. It preserves meter-local time, unknown/opaque fields, and QC category without introducing sync time, units, or Home Assistant entities.
- `measurement.py`: pure-Python Stage 5/5A product measurement mapping. It applies `/10` only to valid identified uric acid, retains category/transmitted/meter-local time, and assigns the app's evidenced mg/dL base unit to that valid analyte only.
- `sensor_state.py`: pure Stage 5/5A ordinary uric-acid state mapping and inert per-entry runtime holder.
- `sensor.py`: one uric-acid entity associated with the existing factory-MAC-backed HA device. Its Bluetooth connection is metadata; the unusable standard serial is not displayed. The entity is unavailable until a successful manual refresh in the current process. No BLE I/O or polling occurs in the sensor.
- `coordinator.py`: Stage 7H manual-only current-state selection and state update for exactly two/four raw slots, with a per-entry lock and failure retention. It does not import history or schedule work.
- `history_probe.py`: manually invoked Stage 7B fixed two-slot observation through the Stage 4 transport. It selects only the documented User1 count gate and `1 → 0 → 1` pairs, returns structural/equality booleans, and never feeds measurement state.
- `history_semantics_probe.py`: separate manual Stage 7C action using the same fixed count-gated transport sequence and the existing pure parser/model for private in-memory classification. Its result is boolean-only and does not feed measurement state.
- `config_flow.py`: Stage 6B passive candidate, user review, bounded active project/serial confirmation, and private persistent identity.
- `diagnostics.py`: future non-sensitive diagnostics.

[Stage 6A](STAGE6A_DISCOVERY_IDENTITY_POLICY.md) distinguishes a passive candidate from a project-confirmed TD4183 device and from a uniquely identified physical meter. At the Stage 6A checkpoint, advertisement fields and project `0x4183` reached only the first two states; Device Information exposed readable `0x2A25` but its value was not yet read. Later Stage 6A1/6A1b and 6B work established tested-meter serial stability and implemented guarded setup. Address stability and manufacturer-data semantics remain unresolved.

[Stage 6A1](STAGE6A1_SERIAL_IDENTITY_READ.md) adds a separate manually invoked, read-only Device Information `0x2A25` action. It uses HA connectable resolution and the proven connector policy, performs one bounded read, returns structural booleans only, and disconnects. The user-run real GD82 result found usable text with clean cleanup. [Stage 6A1b](STAGE6A1B_SERIAL_STABILITY.md) adds one process-local private reference and a manual exact-byte set/compare action; the user-run comparison matched immediately and after a meter OFF/ON cycle. [Stage 6A1c](STAGE6A1C_SERIAL_IDENTITY_POLICY.md) defines a guarded future serial-identity policy with explicit collision handling. None of these stages registers a persistent identity or Config Flow.

The manually invoked development-only `gatt_probe.py` validated Home Assistant connectable resolution, connection, five-service GATT inventory, and disconnect on the real meter. The separate `notification_observer.py` observed failed standard Glucose subscriptions and a successful custom `1524` subscription with zero notifications during navigation on the only existing uric-acid result. **Stage 2E's real `protocol_probe.py` run succeeded with the meter ON:** Home Assistant subscribed to custom `1524`, validated the captured `0x22` wake and `0x24` project exchanges with project `0x4183`, unsubscribed, and disconnected. An earlier Stage 1C connection while the display appeared off is separate evidence. **Stage 2F's real one-slot probe then succeeded with the meter ON:** User1 `0x2B` metadata and User1/index-zero `0x25`/`0x26` returned valid command-matched frames, followed by clean cleanup. The probe sent no `0x33` and returned no payload, measurement, or timestamp. The selected HA scanner/proxy remains unknown and is deferred to Stage 9; Auto-mode advertisement and address identity remain Stage 6 work. These development actions do not implement production discovery, synchronization, or entities. Stages 2G and 3 are offline parser/model work only. The reusable Stage 4 transport now lives in `bluetooth.py`; `protocol.py` and `models.py` remain independent of Home Assistant and Bluetooth.

**Stage 4 closure:** `protocol_probe.py` uses `Fora6BluetoothTransport` for its established identity and one-slot sequences. The user reported successful real-GD82 runs with the meter ON for both actions, including valid command-matched exchanges and clean notification stop/disconnect. The bounded record action exposed no decoded analyte, value, or timestamp. This validates the transport refactor without identifying the selected HA adapter/proxy or implementing production discovery, synchronization, or entities. [The Stage 4 transport record](STAGE4_BLUETOOTH_TRANSPORT.md) documents lifecycle, limits, and regression evidence. `protocol.py` and `models.py` remain independent of Home Assistant and Bluetooth.

## Documentation and packaging

The custom integration uses `translations/en.json` for runtime localization. `strings.json` is included only to match the requested repository structure; Home Assistant's custom integration guidance does not use it as a runtime translation source. The current custom-integration manifest is prepared at `1.0.0`; no release or tag exists. Stage 10 validated the repository package, and [Stage 11](STAGE11_RELEASE_CANDIDATE_VALIDATION.md) physically validated the real HACS handoff and proxy refresh.

## Stage 6B entry and entity boundary

[Stage 6B](STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md) enables an observed-shape Bluetooth candidate matcher and user-confirmed active model/serial identification. Exact `0x2A25` text is internal ConfigEntry/DeviceInfo identity; the address is mutable transport location only. Entry setup forwards one unavailable uric-acid sensor backed by inert measurement state. Neither discovery nor entity setup starts record retrieval, polling, or synchronization. The user-run real setup created one GD82 device and one unavailable uric-acid entity; after OFF/ON, no discovery card returned and the device/entity totals remained one. The explicit duplicate-abort flow was not exercised.

## Stage 7A history gate

[Stage 7A](STAGE7A_HISTORY_TRAVERSAL_DESIGN.md) reviewed raw-count parsing, indexed pair retrieval, multi-parameter companion logic, and deduplication without adding a data path. The app's observed `1 → 0 → 1` access does not establish general history traversal or latest-record ordering. No collision-safe record ID or resume state is known. The one existing entity remains unavailable; `coordinator.py` is still inert. A separately authorized bounded Stage 7B probe is the next gate before production synchronization.

## Device metadata refinement

The entity's `DeviceInfo` now places the exact validated `0x2A25` text in `serial_number` for the authenticated local device page. `(DOMAIN, serial)` remains the logical device identifier and ConfigEntry unique ID. The current runtime address uses Home Assistant's dedicated `CONNECTION_BLUETOOTH` type in `connections`, without becoming the canonical identifier. Name, ForaCare manufacturer, and GD82 model remain as before; the BLE meter has no IP address. [The Stage 6B record](STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md) documents the privacy and address-rotation limits. No entity value, BLE command, or sync path changed.

## Stage 7B development boundary

[Stage 7B](STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) adds only a bounded, explicitly invoked probe. Its index-one request constructors and newest-index parser remain in pure `protocol.py`; the Home Assistant action chooses the fixed sequence and uses `Fora6BluetoothTransport`. The raw count must equal two. User-run physical validation succeeded for the fixed `1 → 0 → 1` sequence and same-session index-one equality. Existing identity/record actions retain their schemas and sequences. `coordinator.py`, the configured uric-acid entity, Config Flow, and persistent state are untouched. General production traversal remains blocked by unresolved ordering and deduplication semantics.

## Stage 7C semantic boundary

[Stage 7C](STAGE7C_SEMANTIC_PAIR_CONFIRMATION.md) adds one development action that privately combines the parsed `0x25`/`0x26` parts and checks only analyte, category, QC, and invalid-sentinel classifications. It repeats the fixed Stage 7B command/index sequence, returns no measurement or timestamp, and leaves the coordinator, sensor state, and device identity untouched. The user-run real GD82 result matched the expected classifications and repeat semantics; Stage 7C is complete for that bounded scope. Production synchronization remains blocked by general traversal and deduplication uncertainty.

The user-run Stage 7C result confirmed the expected index-zero and index-one classifications and repeated index-one semantic equality on the real GD82 in the tested two-slot state. Stage 7C is complete for this bounded scope. General traversal and deduplication remain unresolved. The later Stage 6B3 identity migration and rediscovery follow-up were validated on this configured meter; this Stage 7C result did not change identity behavior.

## Stage 7D offline evidence boundary

[Stage 7D](STAGE7D_GENERAL_TRAVERSAL_DEDUP_REVIEW.md) confirms that the TD4183 handler computes its own logical newest index from count and does not use the wire newest-index field for ordering. Both app versions contain an approximate local database existence lookup, but the import threads do not provide a reliable general traversal rule and the lookup supplies no collision-safe meter ID. The [Stage 6B3 identity migration](STAGE6B3_FACTORY_MAC_IDENTITY.md) was physically validated before this review. The configured uric-acid entity stays unavailable; coordinator retrieval, persistence, polling, and production synchronization remain absent.

## Stage 7E physical evidence

Stage 7E’s fixed count-four action was physically validated in one GD82 state. Raw indexes 0/2 classified General-valid and 1/3 QC-invalid; candidate pairs 0/1 and 2/3 had equal meter-local times; repeated index 3 was byte- and semantic-equal in-session. An initial post-measurement Bluetooth-flashing state allowed connection but not notification subscription; no application command was sent until a later successful run after manual power-on. No coordinator/entity/history state changed. General chronology, wrap, and dedup remain unresolved.

## Stage 7F minimum current-state boundary

[Stage 7F](STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md) proposes a manual, fixed-count snapshot to feed the existing uric-acid sensor only when one eligible General primary exists. A future coordinator would own BLE I/O, identity confirmation, fixed index plans, semantic filtering, single-flight locking, and failure retention; the SensorEntity remains transport-free. Count four with two eligible primaries is ambiguous. Historical ingestion, persistent dedup, resume, automatic triggers, and production code remain absent.

## Stage 7G update

Stage 7G adds a standalone development probe using the centralized Bluetooth transport and existing pure record parsers. It gates on project `0x4183`, raw count four, and two valid General uric-acid primaries at raw indexes 0 and 2. Stage 7G1 permits each gated primary's mg/dL value and naive meter-local minute in the private action response alongside relative order. No coordinator, sensor-state, persistence, or production sync path is connected.

Stage 7G2's user-run result ordered raw primary 0 after raw primary 2 in one four-slot snapshot. A future manually triggered coordinator may select the strict maximum naive meter-local time among fully validated eligible primaries for counts two/four, rejecting ties and retaining prior state on failure. This is a design proposal, not an active runtime path. The private action response and meter-local time never become a historical import or persistent dedup cursor.
