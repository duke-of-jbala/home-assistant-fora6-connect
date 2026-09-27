# Current Status — FORA 6 Connect

## Post-Stage-3 QC semantics correction

The protocol-level convenience property now reports `is_qc`, matching the app-mapped category only. QC is not labeled as a control solution; that meaning and any related policy remain unresolved. Stage 2A–2G are complete for their authorized scopes, and remaining semantics are open/deferred without invalidating Stage 3. This correction changes no parser fields, fixture bytes, BLE behavior, action schema, or command set.

**Correction checkpoint:** based on `98c84a5f5b46bdace0e00a92d043afb3ebe3d3f8` (`feat: add offline TD4183 record model and synthetic fixtures`), branch `main`, clean starting tree. Files changed for this correction: `custom_components/fora6_connect/protocol.py`, `tests/test_record_schema.py`, `docs/STAGE2G_TD4183_RECORD_SCHEMA.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `CURRENT_STATUS.md`, and `CODEX_HANDOVER.md`. Checks run and commit SHA are recorded in the final report; this file describes the pre-commit state.

**Stages 0, 1, and 3 are complete for their authorized scope.** Stage 2 remains in progress, with Stages 2A–2G complete. Stage 3 added only an offline combined TD4183 record model and ten synthetic fixture cases. The live development actions, BLE command set, and response schemas remain unchanged. There is no production record synchronization or measurement entity.

## Stage 3 result

`models.py` now combines the validated `0x25` and `0x26` protocol parts in a frozen, Home Assistant-independent `TD4183Record`. It preserves meter-local time, transmitted status, raw integer, analyte selector, category, auxiliary byte, overlapping app code number, and both opaque payloads. Raw `0xFFFF` remains visible as wire data but has no usable numeric value. Contextual raw/10 scaling is available only for an identified valid uric-acid record. Unknown analyte selectors stay unknown; QC, AC, PC, and General remain distinct. No timezone, unit, sync time, record ID, or production exclusion policy was invented.

[The Stage 3 record](docs/STAGE3_RECORD_MODEL_AND_FIXTURES.md) documents the ten entirely synthetic, checksummed pair fixtures and field evidence. They cover supported category, analyte, status, timestamp, and sentinel variants; no captured frame or private health data was copied. The stale roadmap statement about having no record parser was corrected: Stage 2G has an offline parser, while production decoding and synchronization remain absent.

## Exact next gate

Separately authorize **Stage 4 — Home Assistant Bluetooth transport**, with its exact evidence-bound behavior defined before implementation. Stage 3 does not authorize any new BLE command, physical meter test, `0x2F` or `0x33` query, record loop, decoded real-result action, polling, production sync, config flow, or entity.

## Repository state at Stage 3 pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `338d1b759dbc7f60a0eb305de09442856a5950c0` — `feat: add evidence-backed TD4183 record parser`.
- **Starting tree:** clean (`git status --short` returned no entries before Stage 3 edits).
- **Changes after checkpoint:** yes; offline model, synthetic fixtures/tests, and durable Markdown are changed at this pre-commit point. Report the task commit SHA and post-commit status separately.
- **Files changed:** `custom_components/fora6_connect/models.py`, `tests/fixtures_td4183.py`, `tests/test_record_model.py`, `docs/STAGE3_RECORD_MODEL_AND_FIXTURES.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, and `docs/PROTOCOL.md`.
- **Live actions by Codex:** none. No physical meter test, deployment, push, tag, or release.

## Checks actually run

- `python3 -m unittest discover -s tests -q`: 119 passed (106 prior plus 13 new model tests).
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Manifest, translation, and strings JSON parsing plus `services.yaml` YAML parsing: passed.
- `git diff --check` and `git diff --cached --check`: passed. The full 14-file staged diff was inspected.
- Staged privacy/artifact scan found no private path, address, captured frame, capture/package artifact, proprietary source, real health value, or timestamp. All 21 generated synthetic frames had zero exact matches in the retained private capture; only the match count was reported. No untracked file remained after staging.
- AST import review confirmed `protocol.py` and `models.py` have no Home Assistant, Bleak, ESPHome, or Bluetooth dependency. The only staged integration code file is `models.py`; `protocol.py`, `protocol_probe.py`, `__init__.py`, service definitions, and translations have no diff. No BLE command ID or live action result schema changed.
