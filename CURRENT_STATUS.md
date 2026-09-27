# Current Status — FORA 6 Connect

Stages 0, 1, 2A–2G, 3, 4, 5, 5A, 6A, and the Stage 6A1 action implementation
are complete for their authorized scopes. **Stage 6A1 has not been physically
run.** Stable per-meter identity, full Stage 6 Config Flow, device
registration, production synchronization, and polling remain deferred.

The [Stage 6A1 record](docs/STAGE6A1_SERIAL_IDENTITY_READ.md) describes the
manual development-only `fora6_connect.probe_serial_identity` action. It
resolves a connectable device through Home Assistant, connects without pairing,
checks Device Information `0x180A` / readable Serial Number String `0x2A25`,
reads `0x2A25` once, and disconnects. It returns structural status and safe
error codes, never the serial, address, digest, or length. There is no FORA
command, write, notification subscription, automatic read, Config Flow,
matcher, config entry, or device registration.

The Stage 1B inventory supports the characteristic's presence and Read
property but contains no serial value. A future structurally usable read
alone cannot establish stability or uniqueness. Address remains a runtime
locator, and manufacturer-data identity remains unresolved. Stage 4
transport/probes and Stage 5/5A measurement behavior are unchanged.

## Repository observation before Stage 6A1 commit

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `5b1ee153ed768892116bccdde969277b6974d478` — `docs: define FORA discovery and identity policy`.
- **Starting tree:** clean; `git status --short` returned no entries before edits.
- **Changes after checkpoint:** yes, the Stage 6A1 development action, synthetic tests, and documentation. This is a pre-commit observation; the task commit SHA and post-commit status are reported separately.
- **Files changed:** `custom_components/fora6_connect/serial_probe.py`, `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/services.yaml`, `tests/test_serial_probe.py`, `tests/test_gatt_probe.py`, `docs/STAGE6A1_SERIAL_IDENTITY_READ.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`.
- **Live actions:** none. No physical read, FORA application command, deployment, push, tag, or release.

## Checks actually run

- Full unit suite: 195 tests passed.
- See `CODEX_HANDOVER.md` for final quality and privacy checks actually run.

**Exact next gate:** controlled user-run Stage 6A1 read and privacy-safe result
review. If structurally usable, separately authorize private stability/equality
comparison before permanent identity. If unusable, separately authorize a
bounded Stage 6A2 System ID `0x2A23` review. Do not begin Config Flow yet.
