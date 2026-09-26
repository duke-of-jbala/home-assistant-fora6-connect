# FORA 6 Connect Codex Handover

## Task and repository checkpoint

Stage 2A public protocol evidence acquisition/source review was explicitly authorized after Stage 1 closure. This handover describes the **dirty pre-commit** state on 2026-09-26 (Europe/London), not the result of the pending commit.

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `865dc7f7f20769d40284159365fbae7dd8f7628d` — `docs: close Stage 1 discovery`.
- **Starting tree:** clean (`git status --short` empty). `git log -3 --oneline` and `git rev-parse HEAD` verified the checkpoint.
- **Changes after checkpoint:** yes, documentation only. Files changed: `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/ARCHITECTURE.md`. Post-commit SHA/status must be checked separately.
- **Stage state:** Stage 0 complete; Stage 1 complete (1A, 1B, 1C); Stage 2 in progress for evidence acquisition. Stage 2A did not authorize a live write, pairing, RACP, or record retrieval.

## Evidence and limits

Manufacturer FAQ Rev 5.5 Q36 independently documents the BLE `1523` service and Write/Notify `1524` characteristic; Q37 maps GD82 to iFORA HM. The GD82 manual documents its Bluetooth transfer state. Official Google Play identifies iFORA HM package `com.foracare.tdlink.hm`. The FAQ-linked ForaCare Box share was inaccessible from this environment; no contents, file name, or hash were obtained. Third-party app mirrors report versions/hashes but were not downloaded or verified. Public TaiDoc code found relates to other models, and Nordic examples collide in UUID namespace without sharing FORA semantics. **No exact GD82 command bytes or response format were found.** See [the acquisition register](docs/STAGE2_PROTOCOL_ACQUISITION.md) for URLs, source classes, applicability, confidence, licensing, and the Stage 2B plan.

Stage 1 evidence remains unchanged: only uric acid has been measured on the real meter; custom `1524` accepted subscription but emitted no notification during passive navigation; standard Glucose subscription failures do not establish a bonding cause. Fresh Auto discovery and address behavior remain Stage 6 unknowns; selected scanner/proxy remains Stage 9; manufacturer-data meaning remains unknown. No APK, raw packet, private identifier, or health data was added to Git.

## Checks actually run

- `python3 -m unittest discover -s tests -v` — pass, 44 tests, 0 failures.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass before final documentation update; final rerun required.
- Ruff unavailable (`command -v ruff` returned no path), so not run.
- Source/privacy review found no app binary/proprietary source or private capture added. No live BLE operation, push, tag, or release occurred.

## Exact next gate

**Explicit authorization of Stage 2B — acquire and statically inspect a provenance-verified iFORA HM package.** Keep package artifacts outside Git and verify package/signature/hash. A traffic capture or first real write requires a separately scoped authorization and evidence for the operation. Stop after the Stage 2A documentation commit.
