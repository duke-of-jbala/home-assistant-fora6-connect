# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stage 0, Stage 1, and Stages 2A–2E are complete. Stage 2F is in progress; **physical Stage 2F testing is paused**. The user-supplied real Stage 2E action succeeded with the GD82 **ON**: custom `1524` subscription, captured wake/project exchanges, project `0x4183`, and clean cleanup. The separate Stage 1C connection while the display appeared off is not off-state Stage 2E evidence.

- **Branch:** `main`.
- **Last completed checkpoint:** `8801751cb5d52ff05829127ca35e1e00144cb27e` — `docs: align Stage 2F roadmap gate`. The original Stage 2F implementation is `4ae3efa7a1993140afbfe4575b35917a11192dfd`; both remain intact.
- **Starting tree after checkpoint:** clean, verified with `git status --short` before this task.
- **Changes after checkpoint:** yes; this corrective task changes the record selector constructors, synthetic tests, and project evidence/status documentation. Report its commit SHA and post-commit status separately.
- **Live actions:** none performed by Codex. No deployment, push, tag, or release.

## Offline evidence decision

The retained, private iFORA HM 1.7.6/1.7.9 decompilations link physical project `0x4183` to the TD4183 handler. The first Stage 2F implementation incorrectly selected `CurrentUser = 0` for the record requests; direct reinspection of the successful private Stage 2C capture showed `User1 = 1`. Both app builders encode the enum directly at request byte 2 for `0x2B` and byte 5 for indexed `0x25`/`0x26`. The import call path chooses `User1` for this project. The corrected exact frames and remaining index-order uncertainty are in `docs/STAGE2F_TD4183_RECORD_PROBE.md`. The old requests were **never sent from Home Assistant to the physical meter**.

The same static import path calls `0x33` to set the clock. Its necessity for subsequent record reads remains unknown, so the Stage 2F action **never sends it** and fails closed if the smaller sequence does not work. `0x27`/`0x28` handle a private serial/device identifier; `0x2F` is category metadata; `0x50` finish effects are unresolved. All are omitted. Read orientation of the three included commands is supported by the inspected app path; meter-internal effects cannot be excluded with certainty.

## Stage 2F prototype and next gate

`fora6_connect.probe_protocol_record` requires the unchanged Stage 2E wake/project/`0x4183` identity gate, then performs only User1 `0x2B`, `0x25` raw index zero, and `0x26` raw index zero, one write each with response. It validates the response frame and command, subscribes/unsubscribes custom `1524`, and disconnects. No analyte, measurement, timestamp, or private bytes are returned or persisted. No production sync, config flow, entities, polling, pairing, or RACP path was added. `protocol.py` remains Home Assistant/Bleak independent.

**Exact next gate:** review the corrected selector evidence and code, then decide separately whether physical Stage 2F validation may resume. Do not install or invoke `fora6_connect.probe_protocol_record` against the real meter in this task. Stage 2F is not physically validated or complete. No later stage is authorized.

## Corrective-task checks

- `python3 -m unittest discover -s tests -v`: 94 passed with corrected live-request fixtures.
- Compileall, tabnanny, manifest/translation JSON parsing, services YAML parsing, and `git diff --check`: passed.
- Reviewed the 19-file staged diff; `git diff --cached --check`, command-scope, and staged privacy/artifact checks passed. `protocol.py` imports only standard-library modules. The earlier 94-test result reflected internally consistent all-zero selector fixtures and did not validate agreement with live GD82 import traffic.
