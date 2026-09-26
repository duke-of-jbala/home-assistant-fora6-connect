# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stage 0 is complete and Stage 1 remains in progress. The development-only direct-connect Stage 1B probe successfully resolved the real meter through Home Assistant Bluetooth, connected, enumerated five GATT services including the expected Glucose and FORA custom characteristics, and disconnected cleanly. Home Assistant-side GATT transport is validated; the selected scanner/adapter is unknown. The FORA application protocol, measurement synchronization, and entities are not implemented. Auto-mode discovery remains unresolved, and production automatic discovery is deferred to Stage 6. This project is not ready for production health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The next Stage 1 gate is reviewing remaining discovery evidence and planning a separately authorized, privacy-safe raw-notification observation. Stage 2 is not authorized. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state; [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains the planned boundaries.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B probe is installed manually for controlled development testing only.

## License

MIT; see [LICENSE](LICENSE).
