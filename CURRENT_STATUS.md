# Current Status — FORA 6 Connect

**Stage 0: complete. Stage 1: complete (1A, 1B, 1C). Stage 2: in progress.** Stage 2A public-source review and the separately authorized Stage 2B iFORA HM static analysis have been performed. Stage 2B installed or executed no app, contacted no real meter, and performed no pairing, RACP, characteristic I/O, record retrieval, or new measurement. No independent first live write is authorized.

## Established physical-device evidence

- Stage 1A confirmed the real local name, connectable advertisement, and controlled Home Assistant Advertisement Monitor visibility in Active mode. Fresh Auto-mode behavior and address identity remain deferred to Stage 6.
- Stage 1B resolved a connectable BLEDevice through Home Assistant, connected, enumerated five GATT services including standard Glucose and custom `1523`/`1524`, and disconnected cleanly. The selected scanner/proxy is unknown and deferred to Stage 9.
- Stage 1C found failed standard `2A18`/`2A34` subscriptions, successful custom `1524` subscription, and zero notifications over 30 seconds while the user navigated the only stored uric-acid result. The cause of standard subscription failures and whether a custom request is needed remain unknown. **Only uric acid has been measured on this physical meter.** Pairing has not been attempted.

Manufacturer-data meaning remains unknown. Stage 2B did not resolve the deferred production-discovery questions or establish physical application packet semantics.

## Stage 2 evidence and limits

The [Stage 2A register](docs/STAGE2_PROTOCOL_ACQUISITION.md) records the ForaCare FAQ/manual, official iFORA HM package identity, inaccessible ForaCare Box share, and public-source limits. The [Stage 2B static-analysis register](docs/STAGE2_IFORA_HM_STATIC_ANALYSIS.md) records two **mirror-distributed** iFORA HM specimens: 1.7.6 APK and 1.7.9 XAPK. Their locally computed hashes match mirror-published values; each inspected APK has a valid signature, and both versions share one certificate. No independent official Google Play/ForaCare signing fingerprint was available. Package authenticity therefore remains qualified.

The reviewed app path uses custom `1523/1524`, constructs eight-byte summed command frames, and maps project code `TD4183` to a multifunction handler with uric-acid handling. Linking the real GD82 to that project-code branch is a **strong inference** from the official manual identifier, not a measured project-code response. A provisional device/project-code query is documented with call-path provenance in the static-analysis register. Its standalone behavior, required preceding wake-up, write mode, security, actual GD82 response, and physical uric-acid record format remain unknown. It is **not** a ready first live request. Standard Glucose/RACP behavior is separate and unresolved.

## Exact next gate

**Separate authorization for a controlled official-app traffic capture to corroborate the physical GD82 command/response path (Stage 2C evidence acquisition).** An independently authenticated official Play package could also strengthen static provenance before that gate. Capture planning must keep raw traffic private and must separately define any meter interaction; this Stage 2B work does not authorize it. Do not send an independent command, pair, or retrieve records from the real meter.

## Repository state at pre-commit review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `a1dbd18d2e06f77ca32a46d003f1faf5b6aca66a` — `docs: begin Stage 2 protocol acquisition`.
- **Starting tree:** clean (`git status --short` empty); `git log -3 --oneline` and full HEAD checked before editing.
- **Changes after checkpoint:** yes, documentation only; the tree is dirty at this pre-commit review. Post-commit SHA/status must be verified and reported separately.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `docs/STAGE2_IFORA_HM_STATIC_ANALYSIS.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/ARCHITECTURE.md`.
- **Remote/live actions:** no push, tag, release, app installation/execution, or BLE interaction.

## Checks actually run

- `python3 -m unittest discover -s tests -v` — pass, 44 tests.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass after the status/handover update; final rerun before commit.
- Ruff unavailable (`command -v ruff` returned no path), so not run.
- Privacy/proprietary artifact audit: all 12 changed/new paths are Markdown; no APK/XAPK/split, DEX, native library, decompiled source, Bluetooth MAC-shaped value, or secret assignment was found. No private health data or raw capture was added. Proprietary artifacts remain under `<private temporary workspace>`, outside Git. Final staged review remains before commit.

Updated 2026-09-26 (Europe/London), pre-commit.
