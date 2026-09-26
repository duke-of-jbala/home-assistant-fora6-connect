# FORA 6 Connect for Home Assistant

An early-stage custom integration project for the **FORA 6 Connect** blood-testing meter, model **GD82**. The goal is to use Home Assistant's Bluetooth stack, including a local adapter or an ESPHome Bluetooth Proxy, to communicate with the meter. ESPHome will remain a generic proxy.

**Status:** Stage 0 and Stage 1 are complete; Stage 2 is in progress. Stage 2B statically inspected mirror-distributed iFORA HM packages; app-derived commands remain unverified on the real GD82. The development-only direct-connect Stage 1B probe successfully resolved the real meter through Home Assistant Bluetooth, connected, enumerated five GATT services including the expected Glucose and FORA custom characteristics, and disconnected cleanly. Home Assistant-side GATT transport is validated; the selected scanner/adapter is unknown. Stage 1C passive observation is complete: the revised real run could subscribe to custom `1524` but received no notification during navigation of the only existing uric-acid record; standard `2A18` and `2A34` subscriptions failed. The causes remain unconfirmed. The FORA application protocol, measurement synchronization, and entities are not implemented. Fresh Auto-mode discovery and Bluetooth address identity behavior remain unresolved and are deferred to Stage 6; the exact selected scanner/proxy is deferred to Stage 9. Manufacturer-data meaning remains unknown. This project is not ready for production health monitoring.

The documented BLE service and characteristic UUIDs are recorded in [the protocol evidence register](docs/PROTOCOL.md). They do not by themselves prove an observed device is a FORA 6 Connect.

## Project plan

[FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md) is the authoritative stage plan. The [Stage 2A source review](docs/STAGE2_PROTOCOL_ACQUISITION.md) and [Stage 2B static analysis](docs/STAGE2_IFORA_HM_STATIC_ANALYSIS.md) record provenance and qualified app-code findings. The exact next gate is **separate authorization of a controlled official-app traffic capture, or an authenticated official package for further static corroboration**. No independent first live write or pairing is authorized. [CURRENT_STATUS.md](CURRENT_STATUS.md) and [CODEX_HANDOVER.md](CODEX_HANDOVER.md) record the current state; [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains the planned boundaries.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local checks. Future discovery work should follow [docs/CAPTURE_GUIDE.md](docs/CAPTURE_GUIDE.md) and keep private health data out of the public repository.

The repository follows the Home Assistant custom integration layout and includes HACS metadata. HACS support and production device operation are later-stage goals; the Stage 1B and Stage 1C actions are installed manually for controlled development testing only.

## License

MIT; see [LICENSE](LICENSE).
