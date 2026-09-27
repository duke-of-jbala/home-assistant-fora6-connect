# Current Status — FORA 6 Connect

Stages 0–5A and 6A–6B are complete for their authorized scopes. Stage 7A's offline history review is complete; production synchronization remains unimplemented pending the separately authorized bounded Stage 7B gate. The configured GD82 has one device and one uric-acid entity, currently Unavailable. This pre-GitHub task refines device metadata only.

The entity's `DeviceInfo` now displays the exact validated `0x2A25` serial as `serial_number` on the authenticated local Home Assistant device page. ConfigEntry unique ID and `(DOMAIN, serial)` device identifier remain exact serial text. The current runtime address is supplied as `CONNECTION_BLUETOOTH` connection metadata at entity registration. It is not the logical identifier. Name, manufacturer, and model remain `FORA 6 Connect`, `ForaCare`, and `GD82`; no IP belongs to the BLE meter. [The Stage 6B record](docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md) documents the metadata and the unresolved pruning of an old registry connection after address rotation.

## Repository observation before metadata commit

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed/checkpoint commit:** `c095475018c1042b85cea284c11af6d2cfd33cc9` — `chore: add temporary integration branding`.
- **Starting tree:** clean; `git status --short` returned no entries before this task.
- **Changes after checkpoint:** yes, focused device metadata, synthetic tests, and documentation at this pre-commit observation. Report the task commit SHA and post-commit state separately.
- **Files changed:** `custom_components/fora6_connect/sensor.py`, `tests/test_stage6b_entity.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md`.
- **Runtime boundary:** Config Flow, transport, development actions, protocol, measurement mapping, BLE command sequences, and synchronization behavior are unchanged.

## Checks actually run

- Full unit suite: **242 passed** (`python3 -m unittest discover -s tests -q`), including three new synthetic entity metadata tests.
- `compileall`, `tabnanny`, four JSON files, and one YAML file: passed.
- `git diff --check` and `git diff --cached --check`: passed after staging. Full eight-file diff reviewed; scope, deprecated-field, serial/address leakage, privacy, and artifact audits passed. Only `sensor.py` changes at runtime, solely in its `DeviceInfo` construction. This pre-commit observation does not claim a clean working tree.

**Exact next gate:** separately authorize Stage 7B bounded history probe implementation and user-run physical validation as specified in [Stage 7A](docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md). Do not begin production history synchronization before traversal, latest ordering, and deduplication have evidence.
