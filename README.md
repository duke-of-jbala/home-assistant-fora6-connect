# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stages 0, 1, 3, Stage 4 implementation, and Stages 2A–2G are complete for their authorized scopes. Unresolved protocol semantics remain open. Stage 4 added a mock-tested reusable Home Assistant Bluetooth transport and refactored the existing bounded probes; its controlled physical regression is pending. The actions still expose no analyte, value, or timestamp. Production discovery, record synchronization, and measurement entities remain unimplemented; this project is not ready for health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 4 transport record](docs/STAGE4_BLUETOOTH_TRANSPORT.md) describes the reusable session and its tests. **Exact next gate:** review Stage 4 and separately authorize the controlled user-run regression using only the already-proven development actions. Stage 5 needs separate authorization. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B and Stage 1C actions are installed manually for controlled development testing only.

## License

MIT; see [LICENSE](LICENSE).
