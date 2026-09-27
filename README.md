# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stage 0 and Stage 1 are complete; Stage 2 is in progress. Stage 1B validated Home Assistant GATT transport, and Stage 1C observed passive custom `1524` subscription. A controlled research-app capture confirmed an indexed uric-acid import path. **Stage 2E's real Home Assistant identity probe succeeded with the meter ON:** custom `1524` subscription, captured wake and project exchanges, project `0x4183`, and clean disconnect. Stage 2F is authorized for offline record-path evidence review before any new command. Home Assistant does not retrieve records or expose measurement entities. Production discovery and measurement synchronization remain unimplemented; this project is not ready for health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 2E record](docs/STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md) distinguishes the successful Home Assistant identity result from the earlier [Stage 2C app capture](docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md). **Exact next gate:** Stage 2F offline review of TD4183 record commands and their safety; no new live record command is enabled by the identity result. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B and Stage 1C actions are installed manually for controlled development testing only.

## License

MIT; see [LICENSE](LICENSE).
