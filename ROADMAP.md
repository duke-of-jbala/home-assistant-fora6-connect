# Roadmap

The authoritative stage plan, gates, project facts, architecture decisions, and release strategy are in [FORA6_MASTER_ROADMAP.md](FORA6_MASTER_ROADMAP.md).

Stages 0–5A and 6A–6A1c are complete for their authorized scopes. Stage 6B guarded Config Flow and one initially unavailable uric-acid entity are implemented and user-validated on the real GD82. The tested meter's private `0x2A25` serial is stable across an immediate repeat and power cycle; population uniqueness remains unresolved. Stage 7A's offline history/traversal review is complete, but general traversal and deduplication are not established; production synchronization and polling remain absent. **Exact next gate:** separately authorize the bounded Stage 7B probe and user-run physical validation described in the [Stage 7A review](docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md).
