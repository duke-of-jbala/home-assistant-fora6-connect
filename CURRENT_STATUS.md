# Current Status — FORA 6 Connect

**Stage 0, Stage 1, and Stages 2A–2G: complete for their authorized scope.** Stage 2G added an offline TD4183 parser for evidence-backed `0x25`/`0x26` fields. The development BLE action remains privacy-safe and unchanged. No production record synchronization, entities, or decoded real-result exposure exists.

## Stage 2F physical result

The user ran the corrected one-slot Home Assistant action on the real GD82 with the meter ON. The `0x22`/`0x24`/`0x4183` identity gate, User1 `0x2B` metadata, and User1/raw-index-zero `0x25`/`0x26` command-matched frames all validated; notification stop and disconnect succeeded. No `0x33` was sent or required for this bounded read in the tested meter state. Earlier wake-write and subscription failures stopped before record requests.

## Stage 2G offline result

The retained private iFORA HM 1.7.6 and 1.7.9 decompilations became accessible after the earlier evidence-only checkpoint. Their TD4183 call paths agree on packed `0x25` date/hour/minute, transmitted flag, `0x26` little-endian raw value, analyte selector, category, and invalid `0xFFFF` sentinel. [The Stage 2G evidence record](docs/STAGE2G_TD4183_RECORD_SCHEMA.md) gives the byte maps and source locations. Private in-memory validation against the retained HCI import capture classified raw index zero as uric acid/General with valid time and non-sentinel raw value; repeated index one classified as hematocrit/QC with sentinel raw value. No private value, timestamp, address, or raw response was published. The displayed result/time could not be independently checked because no separate specimen was available.

`protocol.py` now has immutable offline record-part structures and parsers. `0x25` time stays meter-local with minute precision and unknown timezone; malformed calendar fields are rejected. `0x26` preserves unknown type codes and opaque payload bits, keeps QC distinct, and flags invalid raw values. Existing raw/10 uric-acid scaling is conditional on separately decoded uric-acid identity and a valid raw value. The live probe, BLE command set, and production behavior were not changed.

## Exact next gate

Review the Stage 2G evidence, implementation, and privacy-safe tests. **Stage 3** wider sanitized fixture/record-model work or a focused evidence follow-up for units, reserved flags, and multi-parameter behavior requires separate authorization. No physical `0x2F` query, decoded real-result exposure, or production synchronization is authorized by Stage 2G.

## Repository state at Stage 2G parser pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `0397e30d9a63c126b1719ee0471969c139fce203` — `docs: record Stage 2G offline schema evidence`.
- **Starting tree:** clean (`git status --short` empty immediately after that commit).
- **Changes after checkpoint:** yes; offline parser, synthetic tests, and durable Markdown are changed at this pre-commit point. Report this task commit SHA and post-commit tree state separately.
- **Live actions by Codex:** none. Private HCI analysis and parser validation were offline only. No deployment, push, tag, or release.
- **Files changed:** `custom_components/fora6_connect/protocol.py`, `tests/test_record_schema.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, and `docs/STAGE2G_TD4183_RECORD_SCHEMA.md`.

## Checks actually run

- `python3 -m unittest discover -s tests -v`: 106 passed, including 12 new synthetic schema tests.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Manifest, translation, and strings JSON parsing plus `services.yaml` YAML parsing: passed.
- `git diff --check`: passed; the parser, synthetic tests, and full Markdown diff were inspected. A private in-memory capture parse confirmed semantic classifications without printing or storing value/time. None of the tracked synthetic four-byte fixture payloads matched the private `0x25`/`0x26` payloads.
- No new BLE command ID or live transport/production sync path was added. `protocol.py` imports only standard-library modules. Privacy/artifact review found no private result, timestamp, address, raw response, capture, APK, keystore, or private absolute path in the changes.
- The 14-file staged diff was inspected and `git diff --cached --check` passed. The staged addition scan and tracked-file artifact audit found no private capture material, identifiers, health values, private paths, or proprietary source. No untracked file was present at this pre-commit review.
