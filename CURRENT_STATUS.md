# Current Status — FORA 6 Connect

Stage 0 is complete. **Stage 1 remains in progress. Stage 1B Home Assistant transport/GATT validation succeeded; Stage 1C passive notification observation is complete. Stage 2 and pairing are not authorized.** Production automatic discovery remains Stage 6 work. Fresh Auto-mode advertisement and address behavior remain unresolved; whether either blocks Stage 1 closure awaits explicit review.

## Stage 1C real evidence (user-supplied, privacy-safe)

The first installed Stage 1C observer connected, failed to subscribe to Glucose Measurement `2A18`, and aborted before `2A34` or custom `1524` could be tested. The revised observer was then run on the real meter and reported `device_found`, connectable resolution, connection, and Home Assistant Bluetooth connection as true. In its 30-second window, it attempted three subscriptions: `2A18` and `2A34` each failed with sanitized `BleakError`; custom `1524` subscribed successfully. **Zero notifications** were received. The successful subscription stopped cleanly and disconnect completed cleanly.

During the revised run, the user pressed the meter's arrow/navigation keys while custom `1524` was already subscribed. The display remained on the existing uric-acid result. This new meter has had only one real measurement so far, uric acid; its memory appears to contain only that record. No new measurement was performed. **Observed conclusion:** passive custom subscription plus navigation/display of that existing record produced no custom notification during the 30-second window. This does not show that `1524` requires an application command or establish behavior for glucose, ketone, cholesterol, haemoglobin, or haematocrit, none of which has been tested on this physical meter.

The [Bluetooth SIG Glucose Profile 1.0.1, sections 6.1–6.2](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/GLP_v1.0.1/out/en/index-en.html) requires bonding and LE Security Mode 1, Security Level 2 or 3 for supported Glucose Service characteristics. An earlier iPhone connection was observed as bonded. Missing bonding/encryption remains a strong **hypothesis** for the standard subscription failures; proxy/descriptor failure remains possible. Neither cause is confirmed. An explicit application-level request before `1524` emits stored data is also unproven and belongs to future, separately authorized Stage 2 acquisition. No pairing, characteristic read/write, RACP, record retrieval, decoding, or FORA application command occurred in this documentation task or is authorized now. Only stack-managed CCCD activity from the prior real observer's notification subscriptions was within Stage 1C scope.

## Exact next gate

**Explicitly review the remaining Stage 1 discovery questions and decide whether unresolved fresh Auto-mode advertisement and address behavior block Stage 1 closure or can be deferred to later production discovery.** No additional passive notification run is required for Stage 1C. Keep Stage 1 in progress until that review; do not begin Stage 2 or pairing.

## Repository state at pre-commit review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `bc25c44a5d3673486791ff6ad9bd972f15590eee` — `fix: continue Stage 1C after subscription failure`.
- **Starting tree:** clean; `git status --short` was empty.
- **Changes after checkpoint:** yes; documentation-only dirty pre-commit state. Verify and report post-commit SHA/status separately.
- **Files changed:** `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`.
- **Remote/BLE actions:** none; no push, tag, release, or BLE operation from this repository task.

## Checks actually run

- `python3 -m unittest discover -s tests -v` — pass, 44 tests, 0 failures.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass after correction of one Markdown EOF blank line; final rerun follows.
- Ruff — not installed (`command -v ruff` returned no path); not run.
- Privacy audit — documentation diff inspected; no real Bluetooth/scanner address, raw packet/payload, measurement value, serial number, or secret added. The only long hexadecimal string added is the prior Git checkpoint SHA.

Updated 2026-09-26 (Europe/London), pre-commit.
