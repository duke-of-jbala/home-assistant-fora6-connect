# FORA 6 Connect Codex Handover

## Task and repository checkpoint

Stage 2B static analysis of iFORA HM was explicitly authorized after Stage 2A. This handover records the **dirty pre-commit** state on 2026-09-26 (Europe/London), not the result of the pending commit.

- **Branch/checkout:** `main`, `<local checkout>`.
- **Last completed checkpoint:** `a1dbd18d2e06f77ca32a46d003f1faf5b6aca66a` — `docs: begin Stage 2 protocol acquisition`.
- **Starting tree:** clean; `git status --short`, `git log -3 --oneline`, and `git rev-parse HEAD` checked before edits.
- **Changes after checkpoint:** yes, documentation only. Files: `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `docs/STAGE2_IFORA_HM_STATIC_ANALYSIS.md`, `docs/DEVELOPMENT.md`, `docs/CAPTURE_GUIDE.md`, `docs/ARCHITECTURE.md`. Verify/report post-commit SHA and status separately.
- **Stage state:** Stage 0 complete; Stage 1 complete (1A, 1B, 1C); Stage 2 in progress. Stage 2A public review and Stage 2B static app review have been performed. No independent first live write, pairing, RACP, or record retrieval is authorized.

## Evidence and limits

Official ForaCare sources connect GD82 to iFORA HM and document custom `1523/1524`, but do not supply command bytes. The FAQ-linked Box share was inaccessible in Stage 2A. Stage 2B had no official direct package or Android export route. It statically inspected APKPure-distributed 1.7.6 APK (SHA-256 `dd154de094fc28de86c5a153aada1393816159e5c6ba852235938813c449449c`, version code 130) and 1.7.9 XAPK (SHA-256 `e4705a16dcd5bfab08893fca56d82eacdc097c3d10c3f90bcd9a30666fc34a7d`, version code 136). Computed hashes matched the mirror; valid APK signatures shared certificate SHA-256 `208a0af4de42b9582777a0bb27d746ea9b5087cbc6d62fe5bf0265aa394abf4f`. **No independent official signing-certificate anchor was found.** All proprietary artifacts and decompilation output remain outside Git in `<private temporary workspace>`; the app and native libraries were never executed.

The specimens' generic BLE path selects custom `1523/1524`, enables notifications, writes command frames, and handles notification responses. The app maps `TD4183` to a multifunction handler with a uric-acid branch. It uses eight-byte frames with an 8-bit sum; a provisional project-code query appears in the reviewed detection flow. A physical GD82 project-code response was not observed, and the ordinary app flow has an earlier wake-up frame. The real GD82's first request, response, write mode, security, side effects, and record format remain unknown. Treat app bytes as **provisional static evidence**, not permission to send them. See [the detailed provenance and candidate dossier](docs/STAGE2_IFORA_HM_STATIC_ANALYSIS.md) and the [protocol register](docs/PROTOCOL.md).

Stage 1 evidence is unchanged: only uric acid has been measured on the physical meter; custom `1524` subscribed but emitted no notification during passive navigation; standard Glucose subscriptions failed without proven cause. Fresh Auto discovery and address behavior remain Stage 6 unknowns; exact selected scanner/proxy remains Stage 9. No private address, raw advertisement, health reading, raw capture, or proprietary app source was added to Git.

## Checks

- `python3 -m unittest discover -s tests -v` — 44 passed.
- `python3 -m compileall -q custom_components tests` — passed.
- `python3 -m tabnanny custom_components tests` — passed.
- `git diff --check` — passed after the status/handover update; final rerun before commit.
- Ruff unavailable, so not run.
- Privacy/proprietary audit found 12 changed/new Markdown paths only, no proprietary binary/source artifact, MAC-shaped private address, secret assignment, health data, or raw capture. Final staged audit remains before commit.

## Exact next gate

**Separate authorization for a controlled official-app traffic capture (Stage 2C evidence acquisition) to corroborate the physical GD82 path.** An independently authenticated official Play package would strengthen static provenance. Neither static review nor this handover authorizes an independent first write, pairing, RACP, or record retrieval. Stop after the Stage 2B documentation commit.
