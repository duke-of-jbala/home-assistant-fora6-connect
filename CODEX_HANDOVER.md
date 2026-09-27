# FORA 6 Connect Codex Handover

## Task and repository checkpoint

Stage 2D live-evidence consolidation and offline protocol implementation was explicitly authorized after the user completed a controlled Stage 2C app capture. This handover describes the **dirty pre-commit** state on 2026-09-27 (Europe/London), not the result of the pending commit.

- **Branch/checkout:** `main`, this repository's active checkout. Private absolute paths and usernames are omitted.
- **Last completed checkpoint:** `8d4105f7180bd8e378b3dd07190094b551bb1ec3` — `docs: analyze iFORA HM protocol evidence`.
- **Starting tree:** clean (`git status --short` empty); `git log -3 --oneline` and `git rev-parse HEAD` confirmed the checkpoint.
- **Changes after checkpoint:** yes. Files: `AGENTS.md`, `.gitignore`, `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `custom_components/fora6_connect/protocol.py`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `docs/STAGE2_IFORA_HM_STATIC_ANALYSIS.md`, `docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md`, and `tests/test_protocol.py`. Verify the post-commit SHA and tree status separately.
- **Stage state:** Stage 0 and Stage 1 complete; Stage 2 in progress; Stage 2A, 2B, and 2C complete; Stage 2D offline protocol work complete at this review. Stage 2E is not authorized.

## Evidence and implementation

The user supplied privacy-safe findings from a private HCI capture: a **patched, locally re-signed research copy** of iFORA HM 1.7.6 (original APK SHA-256 `dd154de094fc28de86c5a153aada1393816159e5c6ba852235938813c449449c`) was made compatible with Android 8.1/API 27 by changing minimum SDK 30 to 27. It connected to the physical GD82 and imported the existing uric-acid record. This is not an untouched officially signed runtime specimen. The raw capture, patched APK, signing material, actual health value, timestamp, and identifiers are absent from Git.

The user-supplied capture confirms proprietary `1523/1524` request/notification transport, an eight-byte summed envelope, `0x22` wake, `0x24` model query, and a physical project response of `0x4183` that confirms the Stage 2B `TD4183` association. Indexed `0x25`/`0x26` retrieval participated in the uric-acid import; the displayed uric-acid value was the parsed raw numeric value divided by ten. No bonding, SMP exchange, or observed encryption transition occurred in that successful proprietary session. This does not establish security for standard Glucose/RACP. See [the sanitized Stage 2C record](docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) and [protocol register](docs/PROTOCOL.md) for evidence classes and unresolved bytes.

`protocol.py` now provides immutable frame validation, checksum and marker checks, command-ID extraction/echo, two fixed captured request constructors, project-ID parsing, and a **contextual** uric-acid scaling helper. Its `repr` omits payload data. Tests use only the non-private wake/project exchanges and a synthetic uric-acid value. The sanitized summary does **not** establish the `0x25`/`0x26` field positions, an analyte code, a timestamp timezone, or other analyte scaling; no record parser or dispatch was added. The module has no Home Assistant/Bluetooth imports. No production integration path calls these constructors or writes a FORA characteristic.

The `.gitignore` now also excludes APK/XAPK/split archives and signing keystores; existing rules already excluded btsnoop/pcap captures. Private absolute paths were removed from tracked project-status guidance. No BLE operation was performed in Stage 2D.

## Checks actually run

- Targeted protocol suite: 9 passed before the later privacy-repr test.
- Full `python3 -m unittest discover -s tests -v`: 52 passed after final code formatting.
- `python3 -m compileall -q custom_components tests`: passed after final code formatting.
- `python3 -m tabnanny custom_components tests`: passed after final code formatting.
- `git diff --check`: passed before this final handover update; staged diff check follows.
- Ruff unavailable, so not run.
- Privacy/proprietary audit found 18 changed/new files with no private absolute path, MAC-shaped value, raw health value, capture/APK/keystore/native binary, or proprietary artifact. The request constructors are referenced only in offline `protocol.py` and its tests, not by Home Assistant transport code. Final staged review follows.

## Exact next gate

**Separate authorization for a controlled Stage 2E Home Assistant transport prototype** limited to custom `1524` subscription, captured `0x22` wake and response validation, captured `0x24` project query and `0x4183` response validation, then clean disconnect. No pairing, RACP, record retrieval, automatic connection, polling, sync, or entity work is authorized by Stage 2D. Stop after this task's focused commit.
