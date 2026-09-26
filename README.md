# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stage 0 is complete and Stage 1 BLE discovery is in progress. A user-supplied, screenshot-reviewed observation confirmed the real meter's local name, iPhone connectability, and GATT inventory. Home Assistant's Advertisement Monitor did not show the meter in the tested ESPHome proxy configuration; the Home Assistant discovery and connection paths remain unvalidated. The FORA application protocol has not been established or implemented. There is no working meter setup, synchronization, or measurement entity. This project is under active development and is not ready for production health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The next action is obtaining a private Home Assistant Advertisement Monitor observation using [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md). [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains the planned boundaries.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support is a target for a later stage; installation and device operation are not offered during Stage 1A.

## License

MIT; see [LICENSE](LICENSE).
