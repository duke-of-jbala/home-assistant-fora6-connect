# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stages 0, 1, 2A–2G, 3, 4, 5, and the focused Stage 5A uric-acid unit review
are complete for their authorized scopes. Stage 4 includes user-run real-GD82
identity and bounded record regressions with the meter ON. Stage 6 has not
started. Unresolved protocol semantics and production discovery/sync remain
open.

- **Branch:** `main`.
- **Last completed checkpoint:** `8de037a10e723a9e2a7afdf325bee204ec9b4221` — `feat: add evidence-bounded measurement model`.
- **Starting tree:** clean, verified with `git status --short` before Stage 5A edits.
- **Changes after checkpoint:** yes; this pre-commit task changed the product measurement model, inert sensor mapping, synthetic tests, and Stage 5A documentation. Report the task commit SHA and post-commit tree status separately.
- **Files changed:** `custom_components/fora6_connect/measurement.py`, `custom_components/fora6_connect/sensor.py`, `tests/test_measurement.py`, `docs/STAGE5A_URIC_ACID_UNIT_EVIDENCE.md`, `docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md`, `docs/PROTOCOL.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`.
- **Live actions:** none. Stage 5A used retained private static material in place and performed no physical test, BLE action, deployment, push, tag, or release.

## Evidence result

[The Stage 5A evidence record](docs/STAGE5A_URIC_ACID_UNIT_EVIDENCE.md) gives
relative app class/resource paths, cross-version findings, and evidence
classes. In iFORA HM 1.7.6 the TD4183 uric-acid import divides the raw value
by ten before storage. Both app versions use mg/dL for that unconverted base
number and apply display conversion when the `UA_UNIT` preference selects
µmol/L or mmol/L. Their UI has three unit choices and a first-login South
Africa rule can choose µmol/L. The actual active preference during the
private physical import was not recorded. The traced app formatter does not
use the `0x26` auxiliary byte for unit selection; that byte's physical
meaning and meter-native unit modes remain unresolved. The bundled meter
manual gives no uric-acid unit specification. No private specimen details or
proprietary source were added to Git.

## Implementation boundary

`Fora6Measurement` now carries the evidenced mg/dL base unit only for valid
identified uric acid. Its raw `/10` `Decimal` remains unchanged; no locale
selection or app-style conversion is implemented. Unsupported/unknown
analytes and `0xFFFF` remain without a numeric value or unit. The inert
`sensor.py` mapper admits only General-category valid uric acid and returns
`None` for QC, AC, PC, invalid, or unsupported inputs. Replacement of the
latest state clears a prior numeric state when the new record is unusable.
Meter-local time remains naive and separate from any ingestion time.

The integration still registers no `SensorEntity`, device, or config entry.
Stage 6 owns stable meter identity and setup; later synchronization owns BLE
record feeding. `bluetooth.py`, `protocol_probe.py`, `protocol.py`,
`models.py`, service/action schemas, fixtures, and command sequences are
unchanged. The development record action still returns no decoded result.

## Checks and next gate

- Final full suite: 179 tests passed, including one new Stage 5A QC state test; the targeted measurement suite passed 15 tests before that addition.
- `compileall`, `tabnanny`, integration JSON/YAML parsing, and `git diff --check` passed. `git diff --cached --check` follows staging.
- A checkpoint diff shows no changes to Stage 4 transport/probe, protocol/wire model, service/action schema, or integration entry point. The Stage 5A product/state code has no Bluetooth I/O or new command ID.
- No private value, timestamp, address, identifier, raw frame, capture, app package, decompiled source, or private absolute path is introduced in tracked files.
- **Exact next gate:** separately authorize Stage 6 discovery and identity policy before registering an mg/dL uric-acid entity or device. A separate evidence task would be needed for meter-native UA unit modes. Stage 6 has not started.
