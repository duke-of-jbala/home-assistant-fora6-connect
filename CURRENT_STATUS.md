# Current Status — FORA 6 Connect

Stages 0–6B and 7A–7C are complete for their authorized scopes. Stage 6B3's factory Bluetooth MAC identity migration is now physically validated by the user on the configured GD82. The same integration entry, one GD82 device, and one unavailable uric-acid entity remain; Bluetooth connection metadata remains, bogus serial metadata is absent, and rediscovery is suppressed. Stage 7D, production synchronization, and polling have not started.

## Stage 6B3 physical closure observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Last completed/checkpoint commit before this task:** `1549ca208b2ec771f50f128fc915e46a8c9d6187` — `fix: migrate FORA identity to factory Bluetooth MAC`.
- **Starting tree:** clean (`git status --short` returned no entries); public origin pointed to the expected GitHub repository.
- **Changes after checkpoint:** yes; documentation/status files are updated for this closure before the documentation commit. No runtime file changed.
- **User-run Home Assistant result:** after installing the Stage 6B3 build and restarting HA, the existing integration entry remained; exactly one FORA device and one uric-acid entity remained; the sensor remained Unavailable; device association was preserved; bogus serial metadata was absent; Bluetooth connection metadata remained; device metadata still showed GD82 by ForaCare; and no discovery Add card appeared.
- **Identity confirmation:** a privacy-safe storage inspection reported only that ConfigEntry `unique_id` now has canonical six-octet lowercase colon-separated MAC form. The actual MAC was not supplied or recorded.
- **Identity limits:** `0x2A25` is the generic placeholder “Serial Number”; `0x2A23` was structurally plausible but unusable; project `0x4183` is model/protocol identity only. The factory BT MAC matched HA's locator and was observed unchanged over multiple OFF/ON cycles on this meter. This does not establish behavior for all GD82 units, after reset/update, or population-wide uniqueness. Printed/proprietary app serial relationship, manufacturer-data meaning, and proxy/scanner path remain open.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE6B1_REDISCOVERY_LOCATOR_FIX.md`, `docs/STAGE6B2_SYSTEM_ID_REVIEW.md`, `docs/STAGE6B3_FACTORY_MAC_IDENTITY.md`, and `docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md`.

## Checks run at this observation

- Full unit suite: **326 passed** (`python3 -m unittest discover -s tests -v`); baseline 326. Compileall and tabnanny passed. Four JSON and one YAML file parsed. `git diff --check` and `git diff --cached --check` passed. Documentation diff privacy scan found no MAC-shaped value, private absolute path, serial, health result, or health timestamp. Tracked artifact scan found no prohibited binaries/caches. Changed-file audit confirmed documentation-only scope.
- No physical operation was performed by Codex. No runtime code, service schema, translations, protocol, entity, or Stage 7 behavior changed.

**Stage 6B3 status:** complete for its authorized migration scope on this configured meter.

**Exact next proposed gate:** separately authorize Stage 7D as an offline review of general traversal ordering, circular-buffer/index behavior, and deduplication evidence gaps. This proposal does not authorize production synchronization or polling.
