# Current Status — FORA 6 Connect

Stages 0, 1, 2A–2G, 3, 4, 5, 5A, 6A, 6A1, 6A1b, and the Stage 6A1c
serial-identity policy review are complete for their authorized scopes.
**Stage 6B Config Flow, persistent meter identity, device/entity registration,
production sync, and polling have not started.**

## Physical identity result and policy

The user-run real-GD82 Stage 6A1b test set a private `0x2A25` reference,
matched it immediately, and matched again after one meter OFF/ON cycle. All
reads and disconnects succeeded. No serial, hash, length, address, or
recoverable representation was published. This supports stability for this
meter across those tested conditions; population uniqueness remains unknown.

[Stage 6A1c](docs/STAGE6A1C_SERIAL_IDENTITY_POLICY.md) documents Bluetooth
SIG instance-serial semantics, the FORA manual's SN marking and its limits,
retained app source findings, privacy, and a guarded future identity design.
Exact validated `0x2A25` text is the conditional preferred ConfigEntry
unique ID within this integration and `(DOMAIN, text)` the proposed DeviceInfo
identifier. A future Stage 6B implementation must reject unusable or
colliding identities and must not silently merge devices or fall back to the
Bluetooth address. The address remains a runtime locator; project `0x4183`
confirms model/protocol only. This task changed documentation/status only;
no serial was persisted or registry/config-flow behavior enabled.

## Repository observation before Stage 6A1c commit

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `7d768854b7b4a4e5121ea44940937369a0666749` — `feat: add private serial stability probe`.
- **Starting tree:** clean; `git status --short` returned no entries before edits.
- **Changes after checkpoint:** yes, Stage 6A1c evidence/policy and status documentation only at this pre-commit observation. Report task commit SHA and post-commit status separately.
- **Files changed:** `docs/STAGE6A1C_SERIAL_IDENTITY_POLICY.md`, `docs/STAGE6A1B_SERIAL_STABILITY.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`.
- **Live actions:** none during this review. No physical test, Config Flow, device registration, deployment, push, tag, or release.

## Checks actually run

- Full existing unit suite: 209 tests passed.
- See `CODEX_HANDOVER.md` for final quality and privacy checks actually run.

**Exact next gate:** separately authorize Stage 6B guarded Config Flow and
one-device association implementation, with exact-serial preservation,
privacy, duplicate/ambiguous-identity handling, and controlled validation.
Do not infer global serial uniqueness or start Stage 6B automatically.
