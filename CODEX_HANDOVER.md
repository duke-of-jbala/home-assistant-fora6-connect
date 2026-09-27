# FORA 6 Connect Codex Handover

## Stage, evidence, and checkpoint

Stages through 6A1b are complete for their bounded scopes, and Stage 6A1c
identity-policy review is complete. The real GD82's private standard
`0x2A25` value matched on an immediate repeat and after one meter OFF/ON
cycle; all reads disconnected cleanly. This is evidence of tested-meter
stability, not population uniqueness. No serial or recoverable representation
was published. No Stage 6B Config Flow or persistent device identifier exists.

- **Branch:** `main`.
- **Last completed checkpoint:** `7d768854b7b4a4e5121ea44940937369a0666749` — `feat: add private serial stability probe`.
- **Starting tree:** clean, verified with `git status --short` before edits.
- **Changes after checkpoint:** yes; evidence/policy/status documentation only at this pre-commit observation. Report task commit SHA and post-commit status separately.
- **Files changed:** `docs/STAGE6A1C_SERIAL_IDENTITY_POLICY.md`, `docs/STAGE6A1B_SERIAL_STABILITY.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`.
- **Live actions:** none during this review. No physical test, Config Flow, registry entry, deployment, push, tag, or release.

## Decision boundary

[The Stage 6A1c review](docs/STAGE6A1C_SERIAL_IDENTITY_POLICY.md) finds
Bluetooth SIG documents `0x2A25` as the serial for a particular device
instance, while neither the standard nor reviewed FORA materials guarantee
that all GD82 GATT serial values are collision-free. Home Assistant accepts
serials as domain-scoped unique IDs. The review conditionally selects exact
validated UTF-8 text for a future ConfigEntry ID and `(DOMAIN, text)`
DeviceInfo identifier, with fail-closed duplicate, unavailable, and changed
identity handling. Address stays a runtime transport locator; project
`0x4183` is only model confirmation. Any future internal HA persistence of
the serial is deliberate and must exclude public logs/diagnostics. None is
implemented in Stage 6A1c.

## Checks actually run

- Full existing unit suite: 209 tests passed.
- `compileall`, `tabnanny`, integration JSON/YAML parsing, `git diff --check`, and `git diff --cached --check` passed.
- The staged privacy scan found no private address, private source path, serial-like fixture, or capture/package artifact; the tracked artifact scan found no prohibited file.
- The staged diff is documentation/status only. Stage 4 transport/probes, Stage 5/5A measurement files, manifest, Config Flow scaffold, actions, and tests are unchanged; no serial or address was persisted.

**Exact next gate:** separately authorize Stage 6B guarded Config Flow
implementation and tests. It must confirm candidate/model/serial in stages,
preserve exact identity text, handle collisions without silent merging, keep
address transport-only, and validate privacy and device association before
any production claim. Population uniqueness, reset/update stability,
Auto-mode discovery, and address rotation remain unresolved.
