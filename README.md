# Home Assistant – FORA 6 Connect

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stages 0–6B3, 7A–7H, and Stage 8 are complete for their authorized scopes. The user physically validated the manual-only current-state uric-acid refresh on the real GD82. The existing device and single entity remained, and the entity became available after refresh. Stage 8 reviewed and synthetically hardened this path. Counts other than two/four, historical import, automatic sync, and broader count handling are not implemented. Address identity behavior across GD82 units, factory resets, and firmware updates remains unresolved.

Only uric acid currently has evidence-backed numeric scaling and a display unit (mg/dL). Other analytes are not exposed as numeric entities. To refresh the uric-acid entity, turn the meter on normally, leave its history arrows untouched, then run `fora6_connect.refresh_current_uric_acid` for the configured entry. This manual path was validated on one real GD82. On the tested GD82, standard Device Information identifiers were unusable as meter-specific identity; the factory-printed Bluetooth MAC matched the Home Assistant address and is the guarded fallback identity. Private captures and health results are excluded from public fixtures and documentation.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect. The [Stage 6B3 identity record](docs/STAGE6B3_FACTORY_MAC_IDENTITY.md) explains the factory MAC fallback and its validation on this meter.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes the reusable session and physical regression closure. The [Stage 5 model](docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md), [Stage 5A unit evidence](docs/STAGE5A_URIC_ACID_UNIT_EVIDENCE.md), and [Stage 6A identity policy](docs/STAGE6A_DISCOVERY_IDENTITY_POLICY.md) document the product and discovery boundaries. The [Stage 7A review](docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md) records the history evidence and blockers; the [Stage 7B probe](docs/STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) and [Stage 7C semantic confirmation](docs/STAGE7C_SEMANTIC_PAIR_CONFIRMATION.md) record their bounded physical results. The [Stage 7D offline review](docs/STAGE7D_GENERAL_TRAVERSAL_DEDUP_REVIEW.md) found no proven general order, wrap rule, or collision-safe deduplication key. The [Stage 7E probe](docs/STAGE7E_FOUR_SLOT_TRAVERSAL_PROBE.md) confirmed one fixed four-slot state. The [Stage 7F review](docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md) defined a conditional sensor-refresh path; Stage 7G later supplied bounded timestamp-order evidence. Stage 7H implements the narrow manual current-state path. General traversal, historical import, and durable deduplication remain unimplemented.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; development actions are manually invoked for controlled testing only.

This is a development integration, not a validated installation or release. The current [branding](docs/BRANDING.md) is original temporary placeholder artwork, not official ForaCare branding.

## License

MIT; see [LICENSE](LICENSE).

The [Stage 7G/G1 probe](docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md) compares two fixed primary slots when raw count is four. Its private development response may include valid uric-acid mg/dL values and timezone-unknown meter-local times for direct comparison with the meter display. It does not update the sensor; the response contains health data and should remain private.

The real bounded comparison found raw primary 0 later than raw primary 2 in one snapshot. [Stage 7G2](docs/URIC_ACID_UNIT_CONVERSION.md) also reviews the app's mmol/L display formatting. [Stage 7H](docs/STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md) records the successful manual current-state refresh validation. [Stage 8](docs/STAGE8_CURRENT_STATE_HARDENING_REVIEW.md) reviews repeat refresh, failure retention, reload, UX, and future-gate readiness. Reload/restart deliberately returns the sensor to unavailable until another manual refresh. [Stage 9](docs/STAGE9_ESPHOME_BLUETOOTH_PROXY_VALIDATION.md) records direct Home Assistant connection-source evidence that the tested refresh traversed the Lounge M5Stack Atom Lite ESPHome Bluetooth Proxy. Stage 9 is complete for that run only. The next proposed gate is Stage 10 HACS packaging/readiness; Stage 8H bounded history exposure remains optional. There is no historical import or automatic sync.
