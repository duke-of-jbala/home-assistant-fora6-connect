# Home Assistant – FORA 6 Connect

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stages 0–6B and 7A are complete for their authorized scopes. Stage 7B's fixed two-slot probe was validated by the user on the real GD82: count two, successful `1 → 0 → 1` pairs, equal repeated index one, and clean cleanup. This does not establish general history traversal or deduplication. There is no production record synchronization or polling, so the uric-acid entity remains unavailable and the project is not ready for health monitoring. Proposed next gate: separately authorize Stage 7C bounded semantic pair confirmation.

Only uric acid currently has evidence-backed numeric scaling and a display unit (mg/dL). Other analytes are not exposed as numeric entities. The uric-acid entity remains unavailable until a later synchronization stage supplies measurements. Meter serials and Bluetooth addresses are used internally for identity and transport; private captures and health results are excluded from public fixtures and documentation.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes the reusable session and physical regression closure. The [Stage 5 model](docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md), [Stage 5A unit evidence](docs/STAGE5A_URIC_ACID_UNIT_EVIDENCE.md), and [Stage 6A identity policy](docs/STAGE6A_DISCOVERY_IDENTITY_POLICY.md) document the product and discovery boundaries. The [Stage 7A review](docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md) records the history evidence and blockers; the [Stage 7B probe](docs/STAGE7B_BOUNDED_TRAVERSAL_PROBE.md) records successful bounded physical validation. **Exact next proposed gate:** separately authorize Stage 7C bounded semantic pair confirmation. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B and Stage 1C actions are installed manually for controlled development testing only.

This is a development integration, not a validated installation or release. The current [branding](docs/BRANDING.md) is original temporary placeholder artwork, not official ForaCare branding.

## License

MIT; see [LICENSE](LICENSE).
