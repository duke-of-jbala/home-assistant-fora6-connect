# FORA 6 Connect Codex Handover

## Stage 6B3 physical migration closure

This task began on clean public `main` at `1549ca208b2ec771f50f128fc915e46a8c9d6187` (`fix: migrate FORA identity to factory Bluetooth MAC`). The user installed the migration and restarted Home Assistant. The existing integration entry remained; exactly one FORA device and one uric-acid entity remained; the entity stayed Unavailable; the existing device association and Bluetooth connection metadata remained; bogus serial metadata was absent; the device still showed GD82 by ForaCare; and no discovery Add card appeared. A privacy-safe `/config/.storage/core.config_entries` inspection returned only “canonical bluetooth mac,” confirming the entry unique ID changed from the generic placeholder to canonical MAC form. No actual MAC was shared or recorded.

This confirms the migration preserved the existing Home Assistant object graph for this GD82. **Stage 6B3 is complete for its authorized migration scope.** For this meter, `0x2A25` is unusable placeholder text and `0x2A23` was structurally plausible but unusable. Project `0x4183` remains model/protocol identity. The factory BT MAC matches the HA Bluetooth locator and remained unchanged across multiple observed OFF/ON cycles. That does not establish fixed-address or population-wide uniqueness for all GD82 meters. Factory reset/firmware-update behavior, relationship of the proprietary printed serial to app serial behavior, manufacturer-data semantics, and exact scanner/proxy path remain unresolved.

No code, service, translation, manifest, protocol, entity, probe, or Stage 7 runtime behavior changed. Production synchronization and polling remain absent. The uric-acid entity remains unavailable.

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Last completed/checkpoint commit before this task:** `1549ca208b2ec771f50f128fc915e46a8c9d6187` — `fix: migrate FORA identity to factory Bluetooth MAC`.
- **Starting observation:** clean working tree; public origin configured.
- **Changes after checkpoint:** yes, documentation/status only; verify/report post-commit and push state separately.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE6B1_REDISCOVERY_LOCATOR_FIX.md`, `docs/STAGE6B2_SYSTEM_ID_REVIEW.md`, `docs/STAGE6B3_FACTORY_MAC_IDENTITY.md`, and `docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md`.
- **Checks actually run:** full verbose suite **326 passed**; compileall and tabnanny passed; four JSON and one YAML parsed; both diff whitespace checks passed. Documentation privacy scan found no private MAC, serial, health data/timestamp, or private path. Tracked artifact scan found no prohibited artifact/cache. Changed paths are documentation/status only.

**Exact next proposed gate:** separately authorize a Stage 7D offline review of general traversal ordering, circular-buffer/index behavior, and deduplication evidence gaps. Do not treat this as authorization for production synchronization or polling.
