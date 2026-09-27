# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stages 0, 1, and 3 are complete for their authorized scope; Stage 2 remains in progress with Stages 2A–2G complete. Stage 2F retrieved valid User1/index-zero record frames on the real GD82 with the meter ON. Stage 2G added offline evidence-backed decoding, and Stage 3 added an immutable combined record model and synthetic fixtures. The live action still exposes no analyte, value, or timestamp. Production discovery, record synchronization, and measurement entities remain unimplemented; this project is not ready for health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 2G schema review](docs/STAGE2G_TD4183_RECORD_SCHEMA.md) maps parsed fields; the [Stage 3 record](docs/STAGE3_RECORD_MODEL_AND_FIXTURES.md) explains the offline model and synthetic corpus. **Exact next gate:** separately authorize Stage 4 production Bluetooth transport. Stage 3 authorizes no new physical BLE operation. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B and Stage 1C actions are installed manually for controlled development testing only.

## License

MIT; see [LICENSE](LICENSE).
