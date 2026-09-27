# Current Status — FORA 6 Connect

Stages 0–6B and 7A–7C are complete for their authorized scopes. Stage 6B1 passed a user-run Home Assistant regression. Stage 6B2's user-run System ID read classified `0x2A23` as structurally plausible but unusable for this GD82. Stage 6B3 now has an offline-tested factory BT MAC fallback and in-place migration for the legacy placeholder entry, awaiting controlled real HA validation. Stage 7D, production synchronization, and polling remain absent; the uric-acid entity remains unavailable.

## Stage 6B3 pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Last completed/checkpoint commit before this task:** `cf1b7632a0759f880867d2713ec77943649c91a0` — `feat: add bounded System ID identity probe`.
- **Starting tree:** clean (`git status --short` returned no entries); origin pointed to the public GitHub repository.
- **Changes after checkpoint:** yes; Stage 6B3 code, synthetic tests and documentation are present before this task's commit. Post-commit/push state must be checked and reported separately.
- **User-run Stage 6B2 result:** `0x2A23` was present, readable and read successfully; the eight-byte format was plausible but its private value was unusable. Set-reference returned `unusable_system_id`, compare returned `no_reference`, and cleanup was clean. No value entered Git. The prior `0x2A25` text is the generic literal “Serial Number”.
- **Factory-label evidence:** the user privately matched the printed BT MAC with HA's address and observed that address unchanged over several meter OFF/ON cycles. This establishes a fallback candidate for this meter under tested conditions, not population-wide fixed-address behavior. The printed serial's GATT relationship remains unresolved.
- **Policy and implementation:** only a project-confirmed GD82 with the exact `0x2A25` placeholder falls back to a valid six-octet factory Bluetooth MAC. The unique ID, DeviceInfo identifier and Bluetooth connection use lowercase colon form. The original HA locator remains in entry data for transport. The existing placeholder entry migrates before sensor forwarding using supported ConfigEntry and device-registry update APIs; preflight requires its old device, matching connection and attached entity. No entry/device/entity is removed or re-created. Ambiguity fails closed.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `custom_components/fora6_connect/__init__.py`, `config_flow.py`, `device_metadata.py`, `identity_migration.py`, `mac_identity.py`, `sensor.py`, `sensor_state.py`, `docs/ARCHITECTURE.md`, `DECISIONS.md`, `DEVELOPMENT.md`, `PROTOCOL.md`, `STAGE6A1C_SERIAL_IDENTITY_POLICY.md`, `STAGE6B1_REDISCOVERY_LOCATOR_FIX.md`, `STAGE6B2_SYSTEM_ID_REVIEW.md`, `STAGE6B3_FACTORY_MAC_IDENTITY.md`, `STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md`, `tests/test_config_flow.py`, `test_mac_identity_migration.py`, `test_stage6b_entity.py`, and `test_stage6b_setup.py`.

## Checks run at this observation

- Full suite: **326 passed** (`python3 -m unittest discover -s tests -v`); starting baseline 312. Compileall and tabnanny passed; four JSON and one YAML parsed. Both diff whitespace checks passed at staged review. Synthetic MACs were the only MAC-shaped added text; no private paths, serials, System ID bytes, health data, binary artifacts, new FORA command, or Stage 7 code appeared in the staged change.
- Home Assistant API review: current Config Flow guidance accepts a discovered MAC as unique ID and recommends lowercase `format_mac`; device-registry guidance supports in-place `new_identifiers`/`new_connections`; config-entry changes require `async_update_entry`. See [Stage 6B3 evidence](docs/STAGE6B3_FACTORY_MAC_IDENTITY.md).
- No physical migration, BLE read, or Stage 7 operation was performed by Codex.

**Exact next gate:** after code review, user-run HA install/reload and verify the same ConfigEntry, one device, one uric-acid entity, stable entity ID/area/customizations, absent bogus serial, retained Bluetooth connection, and no Add card after meter OFF/ON. Report sanitized status only. Do not begin Stage 7D or production synchronization.
