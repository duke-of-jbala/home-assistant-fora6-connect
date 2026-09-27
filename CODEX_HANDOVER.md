# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stage 0, Stage 1, and Stages 2A–2E are complete. Stage 2F is in progress. The user-supplied real Stage 2E action succeeded with the GD82 **ON**: custom `1524` subscription, captured wake/project exchanges, project `0x4183`, and clean cleanup. The separate Stage 1C connection while the display appeared off is not off-state Stage 2E evidence.

- **Branch:** `main`.
- **Last completed checkpoint:** `c791a3ec3523478bb9dc2697eb557e6ba342d8f1` — `docs: record successful Stage 2E identity probe`.
- **Starting tree after checkpoint:** clean, verified with `git status --short`.
- **Changes after checkpoint:** yes; this handover describes the dirty Stage 2F pre-commit state. The changed files are listed in `CURRENT_STATUS.md`; report the Stage 2F commit SHA and post-commit status separately.
- **Live actions:** none performed by Codex. No deployment, push, tag, or release.

## Offline evidence decision

The retained, private iFORA HM 1.7.6/1.7.9 decompilations link physical project `0x4183` to the TD4183 handler. They construct a current-user `0x2B` slot query and indexed `0x25` then `0x26` read calls. The app import loop begins at raw index zero, which remains zero even under the handler's possible multi-parameter index mapping. Stage 2C corroborated those command IDs but its private record frames remain outside Git. Exact index-zero requests and command classifications are in `docs/STAGE2F_TD4183_RECORD_PROBE.md`.

The same static import path calls `0x33` to set the clock. Its necessity for subsequent record reads remains unknown, so the Stage 2F action **never sends it** and fails closed if the smaller sequence does not work. `0x27`/`0x28` handle a private serial/device identifier; `0x2F` is category metadata; `0x50` finish effects are unresolved. All are omitted. Read orientation of the three included commands is supported by the inspected app path; meter-internal effects cannot be excluded with certainty.

## Stage 2F prototype and next gate

`fora6_connect.probe_protocol_record` is manually invoked with a private runtime address. It requires the unchanged Stage 2E wake/project/`0x4183` identity gate, then performs only `0x2B`, `0x25` raw index zero, and `0x26` raw index zero, one write each with response. It validates the response frame and command, subscribes/unsubscribes custom `1524`, and disconnects. No analyte, measurement, timestamp, or private bytes are returned or persisted. No production sync, config flow, entities, polling, pairing, or RACP path was added. `protocol.py` remains Home Assistant/Bleak independent.

**Exact next gate:** user installs the development build and runs `fora6_connect.probe_protocol_record` once against the existing stored record, then returns only the privacy-safe result. Stage 2F is not physically validated or complete. If it fails, do not retry commands, add clock setting, or advance stages without a new evidence review.

## Checks actually run at this pre-commit point

- `python3 -m unittest discover -s tests -v`: 94 passed.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- `git diff --check` and `git diff --cached --check`: passed.
- Manifest/translation JSON and service YAML parsed. Ruff was not installed.
- Reviewed the 22-file staged diff. Staged privacy and artifact checks found no private path, MAC-like address, actual health value, raw capture, APK/keystore, or production sync path. `protocol.py` imports only standard-library modules.
