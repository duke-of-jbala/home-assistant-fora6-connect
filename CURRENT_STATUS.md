# Current Status — FORA 6 Connect

**Stage 0, Stage 1, and Stages 2A–2F: complete. Stage 2G: authorized; parser implementation paused at the user's request until the retained decompilations are located.** No semantic record parser, decoded analyte/value/timestamp, or production synchronization exists.

## Confirmed Stage 2F physical result

The user ran the corrected one-slot Home Assistant action on the real GD82 with the meter ON. The `0x22`/`0x24`/`0x4183` identity gate, User1 `0x2B` metadata, and User1/raw-index-zero `0x25`/`0x26` command-matched frames all validated; notification stop and disconnect succeeded. No `0x33` was sent or required for this bounded read in the tested meter state. Earlier wake-write and subscription failures stopped before record requests. The action exposed no health value or measurement timestamp.

## Stage 2G offline finding and exact next gate

The [Stage 2G schema review](docs/STAGE2G_TD4183_RECORD_SCHEMA.md) classifies the shared eight-byte envelope as live corroborated and record payload bytes 2–5 as opaque. Private inspection of the retained HCI import capture corroborated paired indexes `1 → 0 → 1`: the three `0x25` payloads matched, and the two index-one `0x26` payloads matched while index zero differed at offsets 2, 3, and 5. No raw bytes or private result were published. These differences do not establish field meanings. The actual private 1.7.6/1.7.9 decompilation paths were not preserved in durable notes; a suggested workspace path was absent. No separate known-result specimen path was recorded. Exact time bits, numeric bytes, analyte code, flags, and any `0x2F` interpretation dependency remain unresolved. No parser code or speculative tests were added.

**Exact next gate:** locate the actual retained private 1.7.6 and 1.7.9 decompilation directories, then resume Stage 2G on the user's direction. Trace both response parsers and call sites, privately check the known record if its displayed value/time are available, then implement only supported offline fields with synthetic tests. Do not perform another BLE test, send `0x2F`, expose a real measurement, or begin production sync under Stage 2G.

## Repository state at Stage 2G evidence pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `3f4bf9bb0cdde8697736a7ef99d6e2ad8ddedc09` — `docs: record successful Stage 2F record probe`.
- **Starting tree:** clean (`git status --short` empty immediately after that commit).
- **Changes after checkpoint:** yes; this Stage 2G evidence checkpoint changes tracked Markdown only. Report this task commit SHA and post-commit tree state separately.
- **Live actions by Codex:** none. No new BLE operation, deployment, push, tag, or release.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, and new `docs/STAGE2G_TD4183_RECORD_SCHEMA.md`.

## Checks actually run

- `python3 -m unittest discover -s tests -v`: 94 passed.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Manifest, translation, and strings JSON parsing plus `services.yaml` parsing: passed.
- `git diff --check`: passed. The full Markdown diff and new Stage 2G evidence map were inspected. No code, new BLE command, transport change, production sync, private result, timestamp, address, capture, binary artifact, or private absolute path was added.
- `git diff --cached --check`: passed. The staged ten-file diff and added lines were inspected; the staged code/test diff and untracked-file audit were empty. Added-line privacy/artifact scans found no private absolute path, raw capture frame, address, binary filename, result, or timestamp.
