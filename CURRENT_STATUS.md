# Current Status — FORA 6 Connect

## Stage 10 HACS packaging — pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Starting checkpoint:** `f27035b011b2c8d85a94467f96a73b98b2c9b89f` — `docs: close Stage 9 Atom Lite proxy validation`. Starting `git status --short` was empty and origin was the expected public repository.
- **Changes after checkpoint:** yes. The current working tree is modified for this task; the final commit, GitHub workflow results, remote SHA, and post-push tree state must be checked separately.
- **Package finding:** current official HACS rules support this one-domain `custom_components/fora6_connect/` layout, root `hacs.json`, public GitHub metadata, manifest, README, and local brand icon. The old `0.0.0` bootstrap manifest version was replaced with one `0.1.0` development version. No release/tag is needed for custom-repository default-branch installation.
- **Files changed:** `.github/workflows/validate.yml`, `custom_components/fora6_connect/manifest.json`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `README.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, and new `docs/STAGE10_HACS_PACKAGING_READINESS.md`.
- **Checks actually run:** 374/374 synthetic unit tests passed; compileall and tabnanny passed; four JSON, two YAML, and one TOML file parsed; temporary-directory component-copy simulation validated 27 Python modules, relative imports, manifest/resources, and original brand icon. Unstaged diff and changed-file privacy/identifier/credential scans passed; no prohibited artifact or Python/test diff was found. Official HACS and hassfest checks are configured for the pushed commit and are not claimed as passed before their GitHub run. Final staged diff review/check remains before commit.
- **Runtime boundary:** only manifest version and non-behavioral action descriptions change inside the component. No protocol, Bluetooth, identity, coordinator, sensor, automatic sync, history import, or physical meter operation changed.

**Exact next proposed gate after validator results pass:** separately authorize Stage 11 release-candidate validation with a controlled HACS custom-repository install/update. Stage 8H remains optional and unstarted.

**Stage 9 is complete for the tested M5Stack Atom Lite proxy path.** The user observed the active `FORA 6 CONNECT` row in Home Assistant Bluetooth → Connections with Source explicitly naming the (Lounge) M5Stack Atom Lite ESPHome Bluetooth Proxy during `refresh_current_uric_acid`; the connection disappeared shortly after completion. The sanitized count-four action succeeded, updated the existing sensor, and reported no cleanup errors. No duplicate entry/device/entity appeared. Real value, timestamp, and address remain private. See [the Stage 9 closure](docs/STAGE9_ESPHOME_BLUETOOTH_PROXY_VALIDATION.md).

## Stage 9 proxy-path closure — pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Starting checkpoint:** `26f464f69091b944d9e75a4c854c6eafd63c0329` — `docs: define Atom Lite proxy validation`.
- **Starting tree:** clean (`git status --short` returned no entries); origin was the expected public repository.
- **Changes after checkpoint:** yes, documentation/status only. This is a pre-commit observation; verify/report post-commit and remote state separately.
- **Physical evidence:** user supplied direct HA Bluetooth Connections evidence naming the Lounge M5Stack Atom Lite as Source for the active FORA connection during the manual refresh; the row disappeared shortly afterward. The sanitized refresh succeeded at supported raw count four, sensor updated, two eligible primaries, no ambiguity/error/cleanup errors. Existing device/entity remained with no duplicate observed. This establishes proxy traversal for the tested transaction, not population-wide behavior.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, and `docs/STAGE9_ESPHOME_BLUETOOTH_PROXY_VALIDATION.md`.
- **Checks actually run:** `python3 -m unittest discover -s tests -v` passed **374/374**; compileall and tabnanny passed; four JSON and one YAML file parsed; diff whitespace check passed; changed-doc privacy and artifact scans passed; no runtime source/config/test files changed. The test suite is synthetic and does not prove proxy routing; the direct HA Connections Source observation is the physical route evidence. Final cached-diff review/check remains before commit.

**Exact next proposed gate:** separately authorize Stage 10 HACS packaging/readiness. Stage 8H remains optional and is not started.

## Stage 9 route-evidence preparation — pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Starting checkpoint:** `9b4be25b396bee63a3b1c66c06fa2b1ec3935e81` — `fix: harden manual uric acid refresh`.
- **Starting tree:** clean (`git status --short` returned no entries); origin was the expected public repository.
- **Changes after checkpoint:** yes, documentation/status only. This is a pre-commit observation; verify/report post-commit and remote state separately.
- **Findings:** the existing transport resolves a connectable `BLEDevice` through HA Bluetooth and passes it to the connector without scanner pinning. Current source/advertisement metadata can show reachability but cannot by itself prove the completed GATT route. The Atom Lite physical connection, selected source, and proxy cleanup remain unobserved. The review defined two acceptable proof methods and a reversible user procedure. No runtime behavior, protocol command, test, entity, or action changed.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, and new `docs/STAGE9_ESPHOME_BLUETOOTH_PROXY_VALIDATION.md`.
- **Checks actually run:** full verbose unit suite **374/374 passed** (baseline 374); compileall and tabnanny passed; four JSON and one YAML file parsed; unstaged diff check passed. `pytest` is not installed, so the established unittest suite is the test gate. Changed-file privacy scan found no real MAC, IP, health value/time, private path, or secret assignment; tracked/untracked artifact scan found no prohibited artifact. Source/diff review found no logging, automatic-sync, history-import, or runtime change. Final staged diff check/review remains to be recorded after staging.

**Exact next gate:** user-run controlled Stage 9 Atom Lite connection-path validation followed by sanitized result review. Do not mark Stage 9 complete without direct connection evidence or valid sole-route isolation. Stage 8H and Stage 10 remain unstarted.

**Stage 8 is complete for its authorized offline/synthetic scope.** The Stage 7H manual count-two/four current-state behavior remains the only production-facing refresh. A simultaneous cleanup failure no longer hides the primary refresh failure; cleanup errors remain separately visible. Repeat refresh, failure retention, reload, and two-entry isolation received additional synthetic coverage. No physical operation, history import, automatic trigger, identity change, or new command was made.

## Stage 8 hardening — pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Starting checkpoint:** `0775869d2fd7daf5a904795f4d468ac40bcc7798` — `docs: close Stage 7H manual refresh validation`.
- **Starting tree:** clean (`git status --short` returned no entries); origin was the expected public repository.
- **Changes after checkpoint:** yes. This is a pre-commit observation; verify/report post-commit and remote state separately.
- **Code:** only `coordinator.py` changes: preserve the original stage/code if cleanup also fails. The count gates, command plans, selection, state update, transport, and triggers are unchanged.
- **Product decisions:** repeated same reading updates the same current-state holder/entity without integration-driven historical import. Later failures retain a prior valid in-process reading. Reload/restart deliberately starts unavailable until another manual refresh; no HA restoration, measurement-time/status attribute, or diagnostic entity is introduced. The private action response is the current status/time surface. Native value remains mg/dL; app mmol/L floor formatting remains separate. Device metadata and canonical MAC identity are unchanged.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `custom_components/fora6_connect/coordinator.py`, `tests/test_manual_refresh.py`, `tests/test_stage6b_setup.py`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md`, `docs/STAGE7_HISTORY_SYNC.md`, `docs/URIC_ACID_UNIT_CONVERSION.md`, and new `docs/STAGE8_CURRENT_STATE_HARDENING_REVIEW.md`.
- **Checks actually run:** full verbose suite **374/374 passed** (baseline 369); compileall, tabnanny, four JSON and one YAML parses passed; unstaged and staged diff checks passed. The complete staged diff was reviewed. Changed-file privacy scan found no private paths, real health examples, or secret assignments; MAC-shaped strings were the explicitly synthetic test fixtures. Tracked/untracked artifact scan and runtime command/automation/logging scans found no new prohibited path.

**Exact next proposed gate:** separately authorize Stage 9 explicit ESPHome Bluetooth Proxy path validation. Stage 8H bounded manual uric-acid history exposure is optional and separately gated; neither has begun. Broader history, persistent dedup/resume, counts above four, and automatic refresh remain out of scope.

**Stage 7H is complete for its authorized scope.** The user validated the manual current-state refresh on the real GD82 in a four-slot state. The configured-entry action selected the later eligible primary by meter-local time, updated the existing uric-acid entity, and completed cleanup. The same device and single sensor remained; the sensor became available. No real measurement value, timestamp, screenshot, or identifier is recorded here.

## Stage 7H physical closure — pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Starting checkpoint:** `b5b21ceeaa933d10195febf82f333f74874cf766` — `feat: add manual uric acid refresh`.
- **Starting tree:** clean (`git status --short` returned no entries); origin is the expected public repository; no tags are present.
- **Changes after checkpoint:** yes, documentation/status only. This is a pre-commit observation; verify/report post-commit and remote state separately.
- **Physical result:** the user manually powered on the meter, avoided its history arrows, and ran the configured-entry action once. It succeeded at raw count four with two eligible primary candidates; the later meter-local time selected raw index 0. The action reported successful state update and clean cleanup. Private value/time are excluded.
- **Home Assistant UI:** the existing device remains GD82 by ForaCare with Bluetooth connection metadata. The same single uric-acid sensor is now available and populated; no duplicate sensor appeared. No screenshot is tracked.
- **Scope:** count two uses raw `0 → 1`; count four uses `0 → 1 → 2 → 3`. Count-four ties at minute precision fail closed. Manual action only. No historical import, persistent dedup/resume, polling, startup, advertisement, or post-measurement trigger.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md`, `docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md`, `docs/STAGE7H_MANUAL_CURRENT_STATE_REFRESH.md`, `docs/STAGE7_HISTORY_SYNC.md`, and `docs/URIC_ACID_UNIT_CONVERSION.md`.
- **Checks:** full verbose suite **369/369 passed** (baseline 369); compileall and tabnanny passed; all five JSON/YAML files parsed; `git diff --check` and `git diff --cached --check` passed. Privacy, health-data, identifier, screenshot/artifact, private-path, proprietary-source, and changed-file audits passed. Only Markdown is changed; runtime, action metadata, tests, and translations are unchanged.

**Exact next proposed gate:** Stage 8 — offline/synthetic/design-first current-state refresh hardening and product-behavior review. Stage 9 proxy validation, Stage 10 HACS readiness, Stage 11 release candidate, and Stage 12 v1.0.0 remain later gates. Historical import and broader analyte support need not block v1. No later stage is started by this closure.

## Earlier Stage 7G2 checkpoint

## Stage 7G2 pre-commit observation

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Starting checkpoint:** `623c343429c26f931b2885252b8af56d6fda19db` — `feat: expose private chronology probe values`.
- **Starting tree:** clean (`git status --short` returned no entries); origin is the public project repository.
- **Changes after checkpoint:** yes, Markdown evidence/status only. This is a pre-commit observation; verify post-commit and remote state separately.
- **Real chronology:** the manually ON meter passed count-four, project, both General uric-acid primary gates, relative comparison, and cleanup. Raw primary **0** had the later parsed meter-local time than raw primary **2** in this snapshot. A higher raw index was not newer here. No private health value, date, time, or identifier is tracked.
- **Meter state:** the user observed normal power-on with flashing Bluetooth light, and history-arrow browsing stopped that light. The cause is unresolved; no runtime change was made.
- **Conversion review:** both retained app versions use the `mg/dL × 59.48 ÷ 1000` mmol/L conversion and two-decimal `FLOOR` formatting in the record-display path. A separate threshold formatter uses `HALF_UP`. Two distinct private base measurements showed the same two-decimal mmol/L meter text. Equivalent firmware formatting is inferred, not proven.
- **Design outcome:** count two remains ready for a narrow manual current-state implementation review. Count four is conditionally ready with complete fixed-plan validation, strict greatest meter-local timestamp among eligible primaries, and fail-closed equal-minute ties. Manual meter-on/no-arrow trigger only. Stage 7H requires separate authorization.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md`, `docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md`, `docs/STAGE7_HISTORY_SYNC.md`, `docs/URIC_ACID_UNIT_CONVERSION.md`.

## Checks

Full verbose unit suite: **353 tests passed** (baseline 353). Compileall and tabnanny passed. Four JSON and one YAML file parsed. `git diff --check` and `git diff --cached --check` passed. Changed-file and added-line scans found no real health value, meter timestamp, MAC, serial, private path, proprietary source, or capture. Tracked artifact scan found no prohibited file. The staged diff was reviewed. Only Markdown changed; no physical operation was performed by Codex.

**Exact next gate:** separately authorize Stage 7H strict manual current-state uric-acid refresh for raw counts two/four only, with full fixed-plan semantic validation, strict meter-local timestamp selection for two eligible count-four primaries, equal-minute tie rejection, and prior-state retention on failure. No historical import, persistent dedup/resume, polling, or automatic trigger.
