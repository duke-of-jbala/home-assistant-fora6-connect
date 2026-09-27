# Home Assistant – FORA 6 Connect

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stages 0–6B and 7A–7C are complete for their authorized scopes. Stage 7C confirmed the expected classifications in one real two-slot state. Stage 6B3 adds an offline-tested, in-place migration from the generic serial placeholder to the factory Bluetooth MAC identity; real Home Assistant migration validation remains pending. There is no production record synchronization or polling, so the uric-acid entity remains unavailable and the project is not ready for health monitoring.

Only uric acid currently has evidence-backed numeric scaling and a display unit (mg/dL). Other analytes are not exposed as numeric entities. The uric-acid entity remains unavailable until a later synchronization stage supplies measurements. On the tested GD82, standard Device Information identifiers were unusable as meter-specific identity; the factory-printed Bluetooth MAC matched the Home Assistant address and is the guarded fallback identity. Private captures and health results are excluded from public fixtures and documentation.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect. The [Stage 6B3 identity record](docs/STAGE6B3_FACTORY_MAC_IDENTITY.md) explains the factory MAC fallback and pending real HA migration check.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes the reusable session and physical regression closure. The [Stage 5 model](docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md), [Stage 5A unit evidence](docs/STAGE5A_URIC_ACID_UNIT_EVIDENCE.md), and [Stage 6A identity policy](docs/STAGE6A_DISCOVERY_IDENTITY_POLICY.md) document the product and discovery boundaries. The [Stage 7A review](docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md) records the history evidence and blockers; the [Stage 7B probe](docs/STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) and [Stage 7C semantic confirmation](docs/STAGE7C_SEMANTIC_PAIR_CONFIRMATION.md) record their bounded physical results. The next gate is controlled real Home Assistant validation of the Stage 6B3 identity migration; production synchronization remains unauthorized.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; development actions are manually invoked for controlled testing only. The next project gate is controlled user-run HA identity migration and rediscovery validation.

This is a development integration, not a validated installation or release. The current [branding](docs/BRANDING.md) is original temporary placeholder artwork, not official ForaCare branding.

## License

MIT; see [LICENSE](LICENSE).
