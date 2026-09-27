# FORA 6 Connect Codex Handover

## Stage 6B2 implementation checkpoint

The task started on clean public `main` at `39bfabb760fbf8f501bbadc8d34e4d8d6196710b` (`fix: suppress duplicate FORA rediscovery`). The user supplied successful physical Stage 6B1 regression facts: one existing device and unavailable uric-acid entity preserved, false generic serial text hidden, repeat Add card suppressed, Bluetooth connection metadata retained, and a private match between the HA locator and printed BT MAC. Printed/GATT serial equality and actual System ID behavior remain unknown. No actual identifier or photo entered Git.

Bluetooth SIG Device Information Service v1.2 defines optional read-only `0x2A23` System ID as intended for an individual product instance; SIG material specifies an eight-octet `uint40` plus `uint24` structure. Stage 6B2 adds manually invoked `probe_system_id` and `probe_system_id_stability` actions. The first reads once and returns structure/status only. The second stores one exact private raw-byte reference in `hass.data[DOMAIN]` for this HA process and compares subsequent one-read results without returning bytes, hashes, or lengths. No production ConfigEntry, DeviceInfo, sensor, Stage 7 probe, or synchronization behavior was changed. No physical `0x2A23` read was run by Codex.

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Last completed/checkpoint commit before task:** `39bfabb760fbf8f501bbadc8d34e4d8d6196710b` — `fix: suppress duplicate FORA rediscovery`.
- **Starting observation:** clean working tree; public origin configured.
- **Changes after checkpoint:** yes, before this task's commit. Post-commit and push state must be checked separately.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `custom_components/fora6_connect/__init__.py`, `services.yaml`, `system_id_probe.py`, `system_id_stability.py`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE6B1_REDISCOVERY_LOCATOR_FIX.md`, `docs/STAGE6B2_SYSTEM_ID_REVIEW.md`, `docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md`, `tests/test_gatt_probe.py`, `tests/test_system_id_probe.py`, and `tests/test_system_id_stability.py`.
- **Checks actually run:** verbose full suite **312 passed** (baseline 294); compileall and tabnanny passed; four JSON and one YAML parsed; unstaged `git diff --check` passed. Final staged diff/privacy review remains before commit.

**Exact next gate:** controlled user-run System ID presence/structure read, process-local set, immediate compare, and OFF/ON compare. Share privacy-safe booleans only. Then separately authorize Stage 6B3 identity-policy and non-destructive migration review. Stage 7D and production synchronization remain unauthorized.
