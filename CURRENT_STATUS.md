# Current Status — FORA 6 Connect

**Stage 0: complete. Stage 1: complete (1A, 1B, 1C). Stage 2: in progress. Stage 2A public review, Stage 2B static analysis, and Stage 2C controlled app capture are complete. Stage 2D offline protocol implementation is complete at this pre-commit review.** No production Home Assistant command/write path, pairing, RACP, polling, measurement sync, or entities are implemented.

## Evidence retained and Stage 2C result

Stage 1B validated Home Assistant-side connection, five-service GATT inventory, and clean disconnect. Stage 1C found failed unpaired standard Glucose subscriptions and successful passive custom `1524` subscription with zero notifications during navigation of the only existing uric-acid record. Those bounded observations remain true. Only **uric acid** has been physically measured on this meter. Fresh Auto-mode discovery and address identity remain Stage 6 questions; the exact Home Assistant scanner/proxy selected remains Stage 9 work.

The [Stage 2C privacy-safe capture summary](docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) was supplied by the user from a private HCI capture. A **patched, locally re-signed iFORA HM 1.7.6 research copy** ran on Android 8.1/API 27 and imported the real GD82's existing uric-acid record; the original APK had minimum SDK 30, and the research copy changed it to 27. It was not an untouched officially signed runtime specimen. The original APK SHA-256 is `dd154de094fc28de86c5a153aada1393816159e5c6ba852235938813c449449c`. No raw capture, APK, signing material, measurement value, private timestamp, or device address is in Git.

The live session confirmed custom service `1523`/characteristic `1524` request/notification traffic with CCCD enabled first; eight-byte frames with an 8-bit sum; request marker `A3`, response marker `A5`, and echoed command ID; `0x22` wake and `0x24` project-query exchanges; physical project ID `0x4183` linking GD82 to the Stage 2B `TD4183` branch; and indexed `0x25`/`0x26` participation in the uric-acid import. Uric-acid display scaling as raw value divided by ten is live-confirmed **only for that analyte on this path**. No bonding, SMP exchange, or encryption transition was observed during the successful proprietary import. This does not settle standard Glucose/RACP security or the cause of earlier standard subscription failures.

## Stage 2D implementation boundary

`custom_components/fora6_connect/protocol.py` is Home Assistant and Bluetooth independent. It validates the observed frame length, prefix, markers, checksum, and command echo; offers an immutable frame representation whose `repr` omits payload bytes; constructs only the captured fixed wake and project-query requests in memory; parses the project ID from a validated `0x24` response; and scales an already identified TD4183 uric-acid raw integer by ten. It neither locates an analyte field nor decodes `0x25`/`0x26` record bytes or timestamps. Their public field layout, timezone, status, and other-analyte scaling remain unresolved. No integration code calls the request constructors or sends a FORA write.

## Exact next gate

**Separate authorization for a controlled Stage 2E Home Assistant transport prototype**, limited initially to custom `1524` subscription, the captured `0x22` wake request and response validation, the captured `0x24` project query and `0x4183` response validation, and clean disconnect. Do not start that live prototype under Stage 2D authorization. Record retrieval, production sync, pairing, and RACP remain outside this gate.

## Repository state at pre-commit review

- **Date/branch/checkout:** 2026-09-27 (Europe/London), `main`, this repository's active checkout.
- **Last completed checkpoint:** `8d4105f7180bd8e378b3dd07190094b551bb1ec3` — `docs: analyze iFORA HM protocol evidence`.
- **Starting tree:** clean (`git status --short` empty); last three commits and full HEAD verified before editing.
- **Changes after checkpoint:** yes, the working tree is dirty at this pre-commit review. Verify/report the post-commit SHA and status separately.
- **Files changed:** `AGENTS.md`, `.gitignore`, `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `custom_components/fora6_connect/protocol.py`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `docs/STAGE2_IFORA_HM_STATIC_ANALYSIS.md`, `docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md`, and `tests/test_protocol.py`.
- **Remote/live actions in this task:** no push, tag, release, deployment, BLE connection, pairing, write, record retrieval, or new measurement.

## Checks actually run

- `python3 -m unittest discover -s tests -p test_protocol.py -v` — passed, 9 tests before the later privacy-repr test was added.
- `python3 -m unittest discover -s tests -v` — passed, 52 tests after final code formatting.
- `python3 -m compileall -q custom_components tests` — passed after final code formatting.
- `python3 -m tabnanny custom_components tests` — passed after final code formatting.
- `git diff --check` — passed before this final status update; staged diff check follows.
- Ruff unavailable (`command -v ruff` returned no path), so not run.
- Privacy/proprietary audit: all 18 changed/new files were checked; no private absolute path, MAC-shaped value, capture/APK/keystore/native binary, or raw health value was found. The two request constructors are referenced only in the offline protocol module and tests, not by a Home Assistant transport. Existing capture and APK files were never placed in this checkout. Final staged-file check follows.

Updated 2026-09-27 (Europe/London), pre-commit.
