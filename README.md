# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stages 0, 1, 2A–2G, 3, 4, and the Stage 5 evidence-bounded product/entity model are complete for their authorized scopes. Stage 4's reusable Home Assistant Bluetooth transport passed user-run real-GD82 identity and bounded record regressions with the meter ON. Uric-acid `/10` scaling is supported, but its displayed unit is not established, so no numeric Home Assistant sensor is exposed. Unresolved protocol semantics remain open. Production discovery and record synchronization remain unimplemented; this project is not ready for health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes the reusable session and physical regression closure. [The Stage 5 model record](docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md) documents product mapping and why numeric sensor exposure is deferred. **Exact next gate:** separately authorize Stage 6 device discovery and identity policy, or a focused evidence follow-up for the uric-acid display unit before adding a numeric sensor. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B and Stage 1C actions are installed manually for controlled development testing only.

## License

MIT; see [LICENSE](LICENSE).
