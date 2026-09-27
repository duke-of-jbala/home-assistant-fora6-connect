# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stage 0 and Stage 1 are complete; Stage 2 is in progress. Stage 2E's real Home Assistant identity probe succeeded with the meter ON and confirmed project `0x4183`. Stage 2F's offline review supports a development-only probe for **one raw record slot**; that probe has not yet been run on the physical meter. It returns only response-status flags, with no measurement or timestamp decoding. Production discovery, record synchronization, and measurement entities remain unimplemented; this project is not ready for health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 2F evidence record](docs/STAGE2F_TD4183_RECORD_PROBE.md) separates static request construction from the pending physical test. **Exact next gate:** one controlled user-run Home Assistant invocation of `fora6_connect.probe_protocol_record` on the existing stored record, followed by review of its privacy-safe result. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B and Stage 1C actions are installed manually for controlled development testing only.

## License

MIT; see [LICENSE](LICENSE).
