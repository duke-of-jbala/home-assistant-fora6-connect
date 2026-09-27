# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stage 0 and Stage 1 are complete; Stage 2 is in progress. Stage 1B validated Home Assistant GATT connection and five-service inventory; Stage 1C found successful passive custom `1524` subscription but no notification, while standard Glucose subscriptions failed for an unresolved reason. A later controlled app capture on the real GD82 confirmed custom `1524` request/notification traffic, eight-byte summed frames, wake and project-query exchanges, project ID `0x4183`, and a uric-acid import path. Stage 2D implemented offline frame and project helpers. Stage 2E adds a manually invoked **development-only** Home Assistant action that can send only the captured wake and project queries; its physical Home Assistant result is pending. Home Assistant does not retrieve records or expose measurement entities. Production discovery and measurement synchronization remain unimplemented; this project is not ready for health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 2C sanitized capture record](docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) distinguishes live confirmation from [Stage 2B static analysis](docs/STAGE2_IFORA_HM_STATIC_ANALYSIS.md). **Exact next gate:** install and run the [Stage 2E controlled identity action](docs/STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md) on the real GD82, then review its privacy-safe result. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state; [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains the boundaries.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B and Stage 1C actions are installed manually for controlled development testing only.

## License

MIT; see [LICENSE](LICENSE).
