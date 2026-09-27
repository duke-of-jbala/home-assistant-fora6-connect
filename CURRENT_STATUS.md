# Current Status — FORA 6 Connect

Stages 0–6B and 7A–7C are complete for their earlier authorized scopes. Stage 6B1 is an implementation checkpoint awaiting controlled Home Assistant validation. Production synchronization, general history traversal, and Stage 7D remain absent. The uric-acid entity remains unavailable.

## Stage 6B1 identity and rediscovery observation

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed/checkpoint commit before this task:** `3ae30e318e3299b0dea1dbe411d571bfc6f5f072` — `docs: record successful Stage 7C semantics`.
- **Starting tree:** clean; `git status --short` returned no entries. Origin pointed to the public GitHub repository.
- **Changes after checkpoint:** yes. One focused runtime identity/metadata correction, synthetic tests, and documentation are in the working tree before commit. Post-commit/push state must be verified separately.
- **Real observations supplied by user:** a discovery card later reappeared for the already configured meter; the HA connection locator privately matched the printed BT MAC; the physical label also bears a serial, but printed/GATT serial equality is unconfirmed. The HA device page displayed “Serial Number” as serial. A subsequent private check found the existing ConfigEntry unique ID itself is exactly that generic literal. No actual serial, MAC, photo, or health datum was supplied for Git.
- **Interpretation:** the original setup flow obtains unique ID solely from its GATT `0x2A25` read. The generic label therefore explains the device display and shows that earlier UTF-8/structural/repeat stability checks did not establish a meter-specific identifier for this configured entry. The original raw GATT read is not published. A genuinely meter-specific identity and safe migration remain a separate gate.
- **Implementation:** known locators abort discovery before a form or active connection; the confirmation step checks again for races. New setup rejects the generic serial placeholder. Existing ConfigEntry/device/entity IDs are retained, while the false visible serial field is cleared on reload. A new locator can update an existing entry only with non-placeholder exact serial confirmation, prior conflict checks, and registry connection replacement; a failed entry update attempts registry rollback. No MAC fallback, new command, BLE read for display, or sensor update was added.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `custom_components/fora6_connect/__init__.py`, `config_flow.py`, `const.py`, `device_metadata.py`, `sensor.py`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE6A1C_SERIAL_IDENTITY_POLICY.md`, `docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md`, `docs/STAGE6B1_REDISCOVERY_LOCATOR_FIX.md`, `tests/test_config_flow.py`, `tests/test_device_metadata.py`, `tests/test_stage6b_entity.py`, and `tests/test_stage6b_setup.py`.

## Checks run for this implementation checkpoint

- Full unit suite: **294 passed** (`python3 -m unittest discover -s tests -v`). Baseline was 285.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Four JSON and one YAML file parsed successfully.
- `git diff --check`: passed at the implementation checkpoint. Stage/review and `git diff --cached --check` still need final verification before commit.
- Tests used synthetic identifiers only. No physical meter test was run by Codex.

**Exact next gate:** user-run HA reload/restart and meter OFF/ON rediscovery regression: verify no repeat card, one preserved device/entity, and no false serial display. Then separately authorize bounded private meter-specific identity evidence, potentially standard System ID `0x2A23` and printed-label comparison, followed by a non-destructive migration design. Do not begin Stage 7D or production sync.
