# Current Status — FORA 6 Connect

**Stage 0 and Stage 1: complete. Stage 2: in progress. Stages 2A–2D: complete. Stage 2E: authorized; development-only identity probe implemented, physical Home Assistant test pending.**

Stage 1B validated Home Assistant connection, five-service GATT inventory, and clean disconnect. Stage 1C found failed unpaired standard Glucose subscriptions, successful custom `1524` subscription, and zero notifications during navigation of the sole existing uric-acid result. Fresh Auto-mode discovery and address identity remain Stage 6 work; the exact selected scanner/proxy remains Stage 9 work.

The user-supplied [Stage 2C capture summary](docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) came from a patched, locally re-signed iFORA HM 1.7.6 research copy. It confirmed custom `1523/1524` traffic, eight-byte checksummed frames, `0x22` wake and `0x24` project exchanges, and physical project `0x4183`. The proprietary import showed no bonding, SMP exchange, or observed encryption transition. Standard Glucose/RACP security remains unresolved. Private capture data, addresses, health values, and timestamps remain outside Git.

`protocol.py` remains Home Assistant and Bluetooth independent. Stage 2E adds a manually invoked `fora6_connect.probe_protocol_identity` action. It resolves a privately supplied runtime address through Home Assistant, subscribes only to custom `1524`, sends the two captured requests with explicit write-with-response, validates notifications through `protocol.py`, requires project `0x4183`, and cleans up. It returns status fields only. **It has not yet been run on the physical meter.** There is no production discovery, pairing, polling, record retrieval, measurement sync, or entity path.

## Exact next gate

Install this development build in Home Assistant and run the [controlled Stage 2E action](docs/STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md) against the real GD82. Review only its privacy-safe result. Stage 2E remains open until that result is returned and reviewed. Further commands and production behavior require separate authorization.

## Repository state at pre-commit review

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `0d293b3d37ef867670468566f14eac55f347be5b` — `feat: add evidence-backed GD82 protocol primitives`.
- **Starting tree:** clean (`git status --short` empty) at that checkpoint.
- **Changes after checkpoint:** yes; this describes a dirty pre-commit Stage 2E state. The task commit SHA and post-commit status are reported separately.
- **Files changed:** `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/protocol_probe.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `docs/STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md`, `tests/test_gatt_probe.py`, and `tests/test_protocol_probe.py`.
- **Live actions in this task:** none; no deployment, connection, pairing, write, record retrieval, push, tag, or release.

## Checks actually run

- Focused Stage 2E suite: 19 passed after the connection-slot and log-privacy tests were added.
- Full `python3 -m unittest discover -s tests -v`: 72 passed after the implementation and documentation edits.
- `python3 -m compileall -q custom_components tests`, `python3 -m tabnanny custom_components tests`, and `git diff --check`: passed.
- Integration translation/manifest JSON and service YAML parsed successfully.
- Ruff unavailable (`command -v ruff` returned no path), so not run.
- Staged diff check passed. The staged file list contains exactly the 19 files above, all text. The final privacy/scope audit found no private path, real Bluetooth address, health value, timestamp, raw capture, APK, or signing artifact in those files. An older GATT test contains only an `AA`-repeated synthetic address. `protocol.py` remains HA/Bluetooth independent; the new action reaches only the two captured writes with `response=True`.

Updated 2026-09-27 (Europe/London), pre-commit.
