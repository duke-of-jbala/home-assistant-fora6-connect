# Current Status — FORA 6 Connect

**Stage 0: complete. Stage 1: complete (1A, 1B, 1C). Stage 2: in progress — public protocol evidence acquisition.** The user explicitly authorized Stage 2A on 2026-09-26 after the Stage 1 closure. This task involved source review and documentation only. No new live BLE operation, pairing, RACP, characteristic I/O, record retrieval, new measurement, or FORA application command occurred.

## Stage 1 evidence retained

- Stage 1A: real name/connectability and controlled Home Assistant Advertisement Monitor visibility in Active mode; fresh Auto-mode behavior remains deferred to Stage 6.
- Stage 1B: Home Assistant resolved a connectable BLEDevice, connected, enumerated five GATT services including standard Glucose and custom `1523`/`1524`, and disconnected cleanly. The selected scanner/proxy remains unknown and is deferred to Stage 9.
- Stage 1C: standard `2A18`/`2A34` subscriptions failed with sanitized `BleakError`; custom `1524` subscribed but emitted zero notifications over 30 seconds while the user navigated the only stored uric-acid result. Cleanup was clean. **Only uric acid has been measured on this physical meter.** A request requirement and the cause of standard subscription failures remain unproven. Pairing was not attempted.

Bluetooth address identity and fresh Auto-mode discovery remain Stage 6 questions. Manufacturer-data meaning remains unknown and may be revisited in Stage 6 if useful or sooner only with relevant protocol evidence. The exact connection scanner/proxy remains a Stage 9 question. These Stage 1 deferrals are not resolved by Stage 2A.

## Stage 2A source review

The independently reviewed [ForaCare FAQ Rev 5.5, Q36–Q37](https://www.foracare.ch/wp-content/uploads/2023/03/3.1-BGM-FAQ_Rev5.5_230313.pdf) documents the BLE custom `1523` service and Write/Notify `1524` characteristic and associates GD82 with iFORA HM. The [GD82 manual](https://switzerland.foracare.ch/wp-content/uploads/2021/10/FORA-6-Connect-GD82-4183D_meter-manual_311-4183400-070.pdf) describes Bluetooth transfer after meter shutoff. The [official iFORA HM Play listing](https://play.google.com/store/apps/details?id=com.foracare.tdlink.hm) identifies package `com.foracare.tdlink.hm`. The FAQ-linked Box share could not be inspected in this environment (browser internal error; sandbox command-line DNS failure). No source file or APK was downloaded, and no exact GD82 command bytes, frame, checksum, response, or record layout was verified. Public TaiDoc material for other models and Nordic UUID-collision examples are not GD82 command evidence. Full source provenance, confidence, licensing limits, and a Stage 2B plan are in [docs/STAGE2_PROTOCOL_ACQUISITION.md](docs/STAGE2_PROTOCOL_ACQUISITION.md).

## Exact next gate

**Explicit authorization of Stage 2B — acquire and statically inspect a provenance-verified iFORA HM package.** Prefer an official Google Play acquisition route, preserve package/signature/hash provenance, and keep proprietary app files outside Git. No live command, pairing, or capture is authorized by this task. If static evidence is insufficient, a controlled official-app capture would require a separate scope. A first real write requires evidence for exact bytes and expected behavior plus a separate authorization.

## Repository state at pre-commit review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `865dc7f7f20769d40284159365fbae7dd8f7628d` — `docs: close Stage 1 discovery`.
- **Starting tree:** clean (`git status --short` empty; `git log -3 --oneline` and full HEAD verified).
- **Changes after checkpoint:** yes; documentation-only dirty pre-commit state. Verify/report the post-commit SHA and tree status separately.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/ARCHITECTURE.md`.
- **Remote/BLE actions:** no push, tag, release, app installation/execution, or live BLE interaction.

## Checks actually run

- `python3 -m unittest discover -s tests -v` — pass, 44 tests, 0 failures.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before final documentation update; final rerun required.
- Ruff unavailable (`command -v ruff` returned no path), so not run.
- Source/privacy audit: no APK or copyrighted source added; no private address, raw capture, manufacturer payload, serial number, health value, or secret added to the Stage 2A evidence. Historical Stage 1 status in `CHANGELOG.md` remains labeled as historical.

Updated 2026-09-26 (Europe/London), pre-commit.
