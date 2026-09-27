# Roadmap

The authoritative stage plan, gates, project facts, architecture decisions, and release strategy are in [FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md).

Stages 0–6B3 and 7A–7G are complete for their authorized bounded/review scopes. [Stage 7H](docs/STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md) implements a manual-only current uric-acid sensor refresh for raw counts two/four, with synthetic validation; real-device validation remains open. General traversal, historical import, durable deduplication, and polling remain absent. **Exact next gate:** user-run Stage 7H manual-refresh validation on the configured GD82. Historical import and automatic refresh remain separate authorization gates.
