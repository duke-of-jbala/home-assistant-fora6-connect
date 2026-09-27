# Roadmap

The authoritative stage plan, gates, project facts, architecture decisions, and release strategy are in [FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md).

Stage 0 and **Stage 1 — FORA 6 Connect BLE discovery** are complete. Stage 1B validated Home Assistant GATT transport, and Stage 1C recorded bounded passive-notification behavior. Fresh Auto-mode advertisement and Bluetooth address identity behavior remain deferred to Stage 6; the exact selected Home Assistant scanner/proxy remains Stage 9 work. **Stage 2 is in progress:** Stages 2A–2D are complete, and Stage 2E's development-only wake/project identity action is implemented. [The sanitized Stage 2C record](docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) identifies the confirmed `0x4183` app path and unresolved record fields. **Exact next gate: run the controlled Stage 2E action on the real GD82 and review its privacy-safe result.** No production sync, polling, pairing, RACP, or record retrieval is authorized.
