# FORA 6 for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect GD82** blood-testing meter. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stage 0 repository bootstrap. The FORA application protocol has not been established or implemented. There is no working meter setup, synchronization, or measurement entity yet. This project is under active development and is not ready for production health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6.

## Project plan

[ROADMAP.md](ROADMAP.md) lists the stage gates. The next gate after bootstrap is **Stage 1 — FORA 6 BLE discovery**. [CURRENT_STATUS.md](CURRENT_STATUS.md) is the current handover. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains the planned boundaries.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support is a target for a later stage; installation and device operation are not offered at Stage 0.

## License

MIT; see [LICENSE](LICENSE).
