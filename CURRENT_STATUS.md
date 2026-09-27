# Current Status — FORA 6 Connect

**Stage 0, Stage 1, and Stages 2A–2E: complete. Stage 2F: in progress, awaiting one physical Home Assistant record-probe result.** The Stage 2F offline evidence gate passed for a bounded, development-only current-user raw-index-zero query. No production record synchronization, measurement decoding, persistence, or entities exist.

## Confirmed Stage 2E result

The user ran the development identity probe on the real GD82 **with the meter ON**. Home Assistant resolved and connected to it, subscribed to custom `1524`, sent the captured `0x22` wake and `0x24` project requests, validated both responses, confirmed project `16771` (`0x4183`), then stopped notifications and disconnected cleanly. The exact scanner/proxy was not identified. An earlier, separate Stage 1C observer connected while the display appeared off; that does not establish off-state success for Stage 2E.

## Stage 2F evidence and implementation

Retained iFORA HM 1.7.6 and 1.7.9 static artifacts trace the TD4183 handler to read-oriented `0x2B` raw-slot metadata and paired `0x25`/`0x26` retrieval at raw index zero. Stage 2C independently observed those command identifiers during an import. [The evidence review](docs/STAGE2F_TD4183_RECORD_PROBE.md) records exact request construction and the remaining uncertainty about whether the physical meter accepts record queries without the app's clock-set operation. `0x33` sets the clock in the static path and is prohibited here; `0x27`, `0x28`, `0x2F`, and `0x50` are also excluded. The prototype fails closed if the minimal path does not work.

The development-only `fora6_connect.probe_protocol_record` action reuses the Stage 2E wake/project/`0x4183` identity gate, then writes at most one `0x2B`, one `0x25`, and one `0x26`, each explicitly with response. It requests **only current-user raw index zero**, has no retries or record loop, validates response envelopes, and returns only status flags. It does not identify an analyte, decode or return a health value or timestamp, pair, issue RACP, or implement production discovery/sync. No Stage 2F physical result exists yet. Only uric acid has been measured on this physical meter, but that history cannot establish analyte identity from an opaque response.

## Exact next gate

Install the development build in Home Assistant and invoke `fora6_connect.probe_protocol_record` **once** against the existing stored record, sharing only its privacy-safe structured result. Stage 2F remains in progress until that physical result is reviewed. If any request fails, do not retry, send `0x33`, or infer a missing prerequisite without further evidence. Do not start a later stage automatically.

## Repository state at documentation-correction review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `4ae3efa7a1993140afbfe4575b35917a11192dfd` — `feat: add bounded TD4183 single-record probe` (the 22-file Stage 2F implementation commit).
- **Starting tree after checkpoint:** clean (`git status --short` empty before this wording correction).
- **Changes after checkpoint:** yes; this follow-up changes only `FORA6_MASTER_ROADMAP.md`, `CURRENT_STATUS.md`, and `CODEX_HANDOVER.md` to align the opening roadmap state and handover. Report the follow-up SHA and post-commit tree state separately.
- **Live actions in this repository task:** none. The Stage 2E physical success is user-supplied evidence; Codex did not connect, deploy, push, tag, or release.
- **Stage 2F implementation file set:** the exact 22-file set remains in the preceding commit, verified with `git show --name-only`; no implementation file changed in this correction.

## Checks actually run

- `python3 -m unittest discover -s tests -v`: 94 passed.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- `git diff --check` and `git diff --cached --check`: passed.
- Manifest/translation JSON and service YAML parsed successfully. Ruff was not installed.
- The preceding 22-file implementation diff, action write scope, and privacy/artifact audit passed before its commit. For this documentation-only correction, the full suite was rerun (94 passed); compileall, tabnanny, manifest/translation JSON, service YAML, and `git diff --check` passed. The correction's staged diff check follows this pre-commit observation and is reported separately.

Updated 2026-09-27 (Europe/London), pre-commit.
