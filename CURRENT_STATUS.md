# Current Status — FORA 6 Connect

Stages 0–6B and 7A–7C are complete for their earlier authorized scopes. Stage 6B1's user-run HA regression passed. Stage 6B2 has an offline-tested, manually invoked System ID evidence probe awaiting user-run physical validation. Production identity migration, general history traversal, Stage 7D, and synchronization remain absent. The uric-acid entity remains unavailable.

## Stage 6B2 implementation observation

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed/checkpoint commit before this task:** `39bfabb760fbf8f501bbadc8d34e4d8d6196710b` — `fix: suppress duplicate FORA rediscovery`.
- **Starting tree:** clean (`git status --short` returned no entries); origin points to the public GitHub repository.
- **Changes after checkpoint:** yes; two development-only System ID actions, synthetic tests, and documentation are present before this task's commit. Verify/report post-commit/push state separately.
- **User-run Stage 6B1 result:** existing device and unavailable uric-acid entity preserved, false literal serial display removed, repeat Add card suppressed, Bluetooth connection metadata retained. User privately confirmed the HA Bluetooth locator matches the meter's printed BT MAC. No actual identifier is tracked; printed/GATT serial equality is still unknown.
- **Standard evidence:** Bluetooth SIG Device Information Service v1.2 §3.7 defines `0x2A23` as an optional read-only System ID intended for an individual product instance. SIG material gives a `uint40` manufacturer identifier plus `uint24` OUI, eight octets. This establishes format and intended meaning, not actual GD82 provisioning or stability.
- **Implementation:** `probe_system_id` performs one bounded read-only `0x180A`/`0x2A23` acquisition and reports structural flags only. `probe_system_id_stability` holds one exact raw-byte reference at `hass.data[DOMAIN]["system_id_stability"]`, behind an asyncio lock, and reports only exact equality. The reference disappears on HA restart. Neither action writes, subscribes, pairs, issues a FORA command, persists identity, or changes ConfigEntry/DeviceInfo. No physical `0x2A23` read has been performed by Codex.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `custom_components/fora6_connect/__init__.py`, `services.yaml`, `system_id_probe.py`, `system_id_stability.py`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE6B1_REDISCOVERY_LOCATOR_FIX.md`, `docs/STAGE6B2_SYSTEM_ID_REVIEW.md`, `docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md`, `tests/test_gatt_probe.py`, `tests/test_system_id_probe.py`, and `tests/test_system_id_stability.py`.

## Checks run

- Full unit suite: **312 passed** (`python3 -m unittest discover -s tests -v`); baseline 294.
- Compileall and tabnanny: passed.
- Four JSON and one YAML file parsed successfully.
- `git diff --check`: passed before staging. Final staged review and `git diff --cached --check` remain to be verified before commit.
- Tracked-artifact inventory and command/write/notify audit of the new probe modules found no private artifact or application command. Tests use only synthetic values.

**Exact next gate:** after review, user-run `probe_system_id` once, set one private reference, compare immediately, power-cycle meter, then compare again; share sanitized results only. A separately authorized Stage 6B3 identity-policy/migration review must evaluate those results before any canonical identity change. Do not begin Stage 7D or production synchronization.
