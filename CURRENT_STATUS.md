# Current Status — FORA 6 Connect

**Stage 0, Stage 1, and Stages 2A–2E: complete. Stage 2F: in progress; physical record testing paused.** The Stage 2F selector/parameter evidence gate was reopened when direct reinspection of the successful Stage 2C wire traffic contradicted the first committed record constructors. Both app builders and the import call sites now support corrected User1/index-zero requests, pending review of this corrective commit. No production record synchronization, measurement decoding, persistence, or entities exist.

## Confirmed Stage 2E result

The user ran the development identity probe on the real GD82 **with the meter ON**. Home Assistant resolved and connected to it, subscribed to custom `1524`, sent the captured `0x22` wake and `0x24` project requests, validated both responses, confirmed project `16771` (`0x4183`), then stopped notifications and disconnected cleanly. The exact scanner/proxy was not identified. An earlier, separate Stage 1C observer connected while the display appeared off; that does not establish off-state success for Stage 2E.

## Stage 2F evidence and implementation

Retained iFORA HM 1.7.6 and 1.7.9 static artifacts trace the TD4183 handler to read-oriented `0x2B` raw-slot metadata and paired `0x25`/`0x26` retrieval. The first Stage 2F implementation commit `4ae3efa7a1993140afbfe4575b35917a11192dfd` assumed the `CurrentUser = 0` selector. The retained successful Stage 2C wire requests instead use `User1 = 1`, directly encoded by both static builders. The import call path selects `User1` for the `0x4183` project. [The reopened evidence review](docs/STAGE2F_TD4183_RECORD_PROBE.md) records exact corrected request bytes, response-count parsing, index ordering, and unresolved branch/meter-state questions. The discrepancy was found **before any Home Assistant Stage 2F record request reached the physical meter**. `0x33` sets the clock in the static path and is prohibited; `0x27`, `0x28`, `0x2F`, and `0x50` remain excluded.

The development-only `fora6_connect.probe_protocol_record` action still reuses the Stage 2E wake/project/`0x4183` identity gate, then writes at most one `0x2B`, one `0x25`, and one `0x26`, each explicitly with response. Corrected constructors select **only User1 raw index zero**. There is no retry, record loop, adjacent-index fallback, or record-value/timestamp decoding. Only uric acid has been measured on this physical meter, but that history cannot establish analyte identity from an opaque response. No Stage 2F Home Assistant physical result exists yet.

## Exact next gate

Review the corrected selector evidence and code. **Do not install or invoke `fora6_connect.probe_protocol_record` against the physical meter in this task.** Decide separately whether physical Stage 2F validation may resume. Stage 2F remains in progress; no later stage starts automatically.

## Repository state at corrective pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `8801751cb5d52ff05829127ca35e1e00144cb27e` — `docs: align Stage 2F roadmap gate`. The prior Stage 2F implementation commit is `4ae3efa7a1993140afbfe4575b35917a11192dfd`.
- **Starting tree after checkpoint:** clean (`git status --short` empty before this corrective task).
- **Changes after checkpoint:** yes; selector constructors, synthetic tests, and durable status/evidence documents are changed at this pre-commit point. Report the corrective SHA and post-commit tree state separately. The two prior commits are preserved.
- **Live actions in this repository task:** none. The Stage 2E physical success is user-supplied evidence; Codex did not connect, deploy, push, tag, or release.
- **Files changed:** `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/protocol.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE2F_TD4183_RECORD_PROBE.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `tests/test_protocol.py`, and `tests/test_record_probe.py`. No new command ID or production path is introduced.

## Checks actually run

- `python3 -m unittest discover -s tests -v`: 94 passed with corrected live-request fixtures.
- `python3 -m compileall -q custom_components tests`, `python3 -m tabnanny custom_components tests`, manifest/translation JSON and service YAML parsing, and `git diff --check`: passed.
- Reviewed the 19-file staged diff; `git diff --cached --check`, command-scope, and staged privacy/artifact checks passed. `protocol.py` imports only standard-library modules. The earlier 94-test result covered internally consistent all-zero fixtures and did **not** validate agreement with the successful live wire requests.

Updated 2026-09-27 (Europe/London), pre-commit.
