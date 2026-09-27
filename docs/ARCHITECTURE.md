# Architecture

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

The ESPHome proxy forwards Bluetooth activity; it has no FORA-specific code. Stage 4 transport resolves connectable devices through Home Assistant's Bluetooth APIs so either a local adapter or an eligible proxy can carry a connection. Home Assistant chooses the actual path; Stage 9 will validate which proxy or adapter is used in an end-to-end run.

## Boundaries

- `bluetooth.py`: reusable Stage 4 HA Bluetooth session for connection, custom characteristic validation, notification exchange, bounded waits, and cleanup. It delegates frame validation to `protocol.py` and chooses no FORA command or health interpretation.
- `protocol.py`: pure-Python frame validation and evidence-backed offline TD4183 record-part parsing, testable with synthetic bytes alone. No HA, ESPHome, adapter, or physical meter requirement. Meter-local time remains separate from ingestion time; unknown timezone, non-uric-acid units, and flags are not invented.
- `models.py`: pure-Python Stage 3 combined TD4183 record over the two validated protocol parts. It preserves meter-local time, unknown/opaque fields, and QC category without introducing sync time, units, or Home Assistant entities.
- `measurement.py`: pure-Python Stage 5/5A product measurement mapping. It applies `/10` only to valid identified uric acid, retains category/transmitted/meter-local time, and assigns the app's evidenced mg/dL base unit to that valid analyte only.
- `sensor_state.py`: pure Stage 5/5A ordinary uric-acid state mapping and inert per-entry runtime holder.
- `sensor.py`: one unavailable uric-acid entity associated with the serial-backed HA device; the local device page shows the exact validated serial and the runtime Bluetooth address is connection metadata. No BLE I/O or polling.
- `coordinator.py`: future retrieval and synchronization state; Stage 7A added no runtime coordinator behavior.
- `history_probe.py`: manually invoked Stage 7B fixed two-slot observation through the Stage 4 transport. It selects only the documented User1 count gate and `1 → 0 → 1` pairs, returns structural/equality booleans, and never feeds measurement state.
- `history_semantics_probe.py`: separate manual Stage 7C action using the same fixed count-gated transport sequence and the existing pure parser/model for private in-memory classification. Its result is boolean-only and does not feed measurement state.
- `config_flow.py`: Stage 6B passive candidate, user review, bounded active project/serial confirmation, and private persistent identity.
- `diagnostics.py`: future non-sensitive diagnostics.

[Stage 6A](STAGE6A_DISCOVERY_IDENTITY_POLICY.md) distinguishes a passive candidate from a project-confirmed TD4183 device and from a uniquely identified physical meter. At the Stage 6A checkpoint, advertisement fields and project `0x4183` reached only the first two states; Device Information exposed readable `0x2A25` but its value was not yet read. Later Stage 6A1/6A1b and 6B work established tested-meter serial stability and implemented guarded setup. Address stability and manufacturer-data semantics remain unresolved.

[Stage 6A1](STAGE6A1_SERIAL_IDENTITY_READ.md) adds a separate manually invoked, read-only Device Information `0x2A25` action. It uses HA connectable resolution and the proven connector policy, performs one bounded read, returns structural booleans only, and disconnects. The user-run real GD82 result found usable text with clean cleanup. [Stage 6A1b](STAGE6A1B_SERIAL_STABILITY.md) adds one process-local private reference and a manual exact-byte set/compare action; the user-run comparison matched immediately and after a meter OFF/ON cycle. [Stage 6A1c](STAGE6A1C_SERIAL_IDENTITY_POLICY.md) defines a guarded future serial-identity policy with explicit collision handling. None of these stages registers a persistent identity or Config Flow.

The manually invoked development-only `gatt_probe.py` validated Home Assistant connectable resolution, connection, five-service GATT inventory, and disconnect on the real meter. The separate `notification_observer.py` observed failed standard Glucose subscriptions and a successful custom `1524` subscription with zero notifications during navigation on the only existing uric-acid result. **Stage 2E's real `protocol_probe.py` run succeeded with the meter ON:** Home Assistant subscribed to custom `1524`, validated the captured `0x22` wake and `0x24` project exchanges with project `0x4183`, unsubscribed, and disconnected. An earlier Stage 1C connection while the display appeared off is separate evidence. **Stage 2F's real one-slot probe then succeeded with the meter ON:** User1 `0x2B` metadata and User1/index-zero `0x25`/`0x26` returned valid command-matched frames, followed by clean cleanup. The probe sent no `0x33` and returned no payload, measurement, or timestamp. The selected HA scanner/proxy remains unknown and is deferred to Stage 9; Auto-mode advertisement and address identity remain Stage 6 work. These development actions do not implement production discovery, synchronization, or entities. Stages 2G and 3 are offline parser/model work only. The reusable Stage 4 transport now lives in `bluetooth.py`; `protocol.py` and `models.py` remain independent of Home Assistant and Bluetooth.

**Stage 4 closure:** `protocol_probe.py` uses `Fora6BluetoothTransport` for its established identity and one-slot sequences. The user reported successful real-GD82 runs with the meter ON for both actions, including valid command-matched exchanges and clean notification stop/disconnect. The bounded record action exposed no decoded analyte, value, or timestamp. This validates the transport refactor without identifying the selected HA adapter/proxy or implementing production discovery, synchronization, or entities. [The Stage 4 transport record](STAGE4_BLUETOOTH_TRANSPORT.md) documents lifecycle, limits, and regression evidence. `protocol.py` and `models.py` remain independent of Home Assistant and Bluetooth.

## Documentation and packaging

The custom integration uses `translations/en.json` for runtime localization. `strings.json` is included only to match the requested repository structure; Home Assistant's custom integration guidance does not use it as a runtime translation source. Manifest version `0.0.0` is a development placeholder required for a custom integration, not a release. The repository layout targets HACS; HACS readiness is a Stage 10 gate.

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

The user-run Stage 7C result confirmed the expected index-zero and index-one classifications and repeated index-one semantic equality on the real GD82 in the tested two-slot state. Stage 7C is complete for this bounded scope. General traversal and deduplication remain unresolved. A discovery-card recurrence for an already configured meter makes Stage 6B rediscovery/locator handling the next focused project task; no identity behavior is changed here.
