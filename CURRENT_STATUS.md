# Current Status — FORA 6 Connect

Stage 0 is complete. **Stage 1 remains in progress; Stage 2 and pairing are not authorized.** Stage 1B real Home Assistant transport/GATT validation succeeded: connectable resolution, connection, five services with the expected Glucose and custom GATT structure, and clean disconnect. The selected scanner/adapter is unknown; Auto-mode and production discovery remain separate work.

## Stage 1C real evidence and interpretation

**User-supplied real result:** the installed Stage 1C observer connected and reached notification subscription, then failed on the first target, Glucose Measurement `0x2A18`. The previous implementation aborted on that failure. It therefore collected **no subscription evidence** for Glucose Measurement Context `0x2A34` or FORA custom `0x1524`; no notification payload was observed. This was a subscription/CCCD-layer failure, not a service-discovery failure. Its cause is unknown.

The [Bluetooth SIG Glucose Profile 1.0.1, sections 6.1–6.2](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/GLP_v1.0.1/out/en/index-en.html) requires Sensor/Collector bonding and LE Security Mode 1, Security Level 2 or 3 for supported Glucose Service characteristics. An earlier iPhone connection was observed as bonded. Missing bonding/encryption is a **strong hypothesis**, not a confirmed cause; ESPHome/proxy or descriptor-notify failure remains possible. **Pairing is not authorized.**

The revised development-only action attempts `start_notify` on all three characteristics independently. Each failure returns only a safe exception class and, if available, a structured D-Bus error code; unstructured upstream text is withheld to protect private data. If any subscription succeeds, the action observes for 30 seconds and stops only successful subscriptions. If none succeeds, it returns a normal privacy-safe result and disconnects without waiting. Cleanup outcomes are reported separately as `subscriptions_stopped_cleanly` and `disconnected_cleanly`. Stack-managed CCCD activity from `start_notify`/`stop_notify` remains the sole authorized subscription activity. No characteristic read/write, direct descriptor write, pairing, RACP, record retrieval, decoding, or FORA command was added. Raw payload bytes remain in memory only during the action and are not returned or persisted.

## Exact next gate

Install the complete revised `custom_components/fora6_connect/` directory in Home Assistant, check configuration, and restart Core. Lounge may temporarily be Active. With the meter in its normal Bluetooth transfer state, privately obtain the known FORA address from Advertisement Monitor and run **Developer Tools → Actions → `fora6_connect.observe_notifications`**. Review only the privacy-safe result: the three subscription outcomes, safe error classes/codes, counts/lengths if any notifications arrive, and disconnect outcome. Zero successful subscriptions and zero notifications are valid findings. Do not make a health measurement solely to generate traffic or share the address, raw payloads, or unredacted logs. Review this real retest before any further Stage 1 decision. Stage 2 and pairing remain unauthorized.

## Repository state at pre-commit review

- **Date/branch/checkout:** 2026-09-26 (Europe/London), `main`, `<local checkout>`.
- **Last completed checkpoint:** `368172a3e8f5e26a0dd54550d09bf0eacc4b7b16` — `feat: add Stage 1C notification observer`.
- **Starting tree:** clean (`git status --short` was empty).
- **Changes after checkpoint:** yes; dirty pre-commit state. Post-commit SHA and status will be verified and reported separately.
- **Files changed:** `custom_components/fora6_connect/notification_observer.py`, `tests/test_notification_observer.py`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `docs/PROTOCOL.md`, `docs/CAPTURE_GUIDE.md`, `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`.
- **Remote/BLE actions:** no push, tag, release, or BLE operation from this repository task.

## Checks actually run

- `python3 -m unittest discover -s tests -v` — pass, 44 tests, 0 failures.
- `python3 -m compileall -q custom_components tests` — pass.
- `python3 -m tabnanny custom_components tests` — pass.
- `git diff --check` — pass; final rerun follows.
- Ruff — not installed (`command -v ruff` returned no path); not run.
- Privacy and operation audit — synthetic test address/payloads only; no real address, scanner identifier, raw notification or advertisement, health value, serial, or secret added. Source has no characteristic read/write, direct descriptor write, pairing, or RACP operation. Tests assert response/log privacy and forbidden-operation boundaries.

Updated 2026-09-26 (Europe/London), pre-commit.
