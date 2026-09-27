# Current Status — FORA 6 Connect

**Stages 0, 1, 2A–2G, 3, 4, 5, and the separately authorized Stage 5A
uric-acid unit review are complete for their stated scopes.** Stage 6 has not
started. Production discovery, synchronization, and Home Assistant entities
remain inactive.

## Stage 5A unit result

[The Stage 5A evidence record](docs/STAGE5A_URIC_ACID_UNIT_EVIDENCE.md) traces
the TD4183 uric-acid import, app preference, display formatter, and resource
labels in retained iFORA HM 1.7.6 and 1.7.9 static evidence. The app treats
the supported raw `/10` number as an **mg/dL base value**. Its `UA_UNIT`
preference can display that stored number in mg/dL, µmol/L, or mmol/L; the
other labels use later app conversion. Both versions have a first-login
South Africa locale rule that can select µmol/L. The unit active during the
private GD82 import was not recorded, and the physical meter's own uric-acid
unit modes remain unknown. The `0x26` auxiliary byte is not used by the
traced app display formatter; its physical meaning remains unresolved.

`measurement.py` now assigns mg/dL only to a valid, positively identified
uric-acid record. `sensor.py` returns that unconverted number only for a
General-category record. Invalid `0xFFFF`, unknown/unsupported analytes, QC,
AC, and PC yield no ordinary numeric state. Meter-local time stays naive and
separate from ingestion time. No `SensorEntity` or device registration exists:
Stage 6 must supply stable identity and a config entry. The existing
development probes still expose no decoded real measurement.

## Exact next gate

Separately authorize **Stage 6 — discovery and identity policy** before
registering an mg/dL uric-acid entity or a device. A separate evidence task
would be needed to establish any physical meter-native uric-acid unit mode.
No Stage 6, BLE command, physical test, or production synchronization is
authorized by Stage 5A.

## Repository observation before Stage 5A commit

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `8de037a10e723a9e2a7afdf325bee204ec9b4221` — `feat: add evidence-bounded measurement model`.
- **Starting tree:** clean; `git status --short` produced no entries before edits.
- **Changes after checkpoint:** yes, Stage 5A product/state mapping, synthetic tests, and documentation. This is a pre-commit observation; the task commit SHA and post-commit status are reported separately.
- **Files changed:** `custom_components/fora6_connect/measurement.py`, `custom_components/fora6_connect/sensor.py`, `tests/test_measurement.py`, `docs/STAGE5A_URIC_ACID_UNIT_EVIDENCE.md`, `docs/STAGE5_MEASUREMENT_ENTITY_MODEL.md`, `docs/PROTOCOL.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`.
- **Live actions:** none. No physical meter test, Home Assistant action, deployment, push, tag, or release.

## Checks actually run

- Full unit suite after the final test addition: 179 tests passed (one new Stage 5A test; one Stage 5 test updated for the mg/dL conclusion). The targeted measurement suite passed 15 tests before that addition.
- `compileall`, `tabnanny`, integration JSON/YAML parsing, and `git diff --check` passed. `git diff --cached --check` follows staging.
- Stage 4 transport/probe, protocol and wire model, service/action schema, and integration entry-point files have no diff from the checkpoint. The new product/state code contains no Bluetooth I/O or new command ID.
- Private source and bundled manual were inspected in place. No private source, package, capture, value, timestamp, address, identifier, or private absolute path was copied into Git.
