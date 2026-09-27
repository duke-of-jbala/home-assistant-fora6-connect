# FORA 6 Connect Codex Handover

## Stage, evidence, and checkpoint

Stage 6A1b private comparison code is implemented and synthetic-tested; no
Stage 6A1b physical test has run. Prior stages through 6A1 are complete for
their bounded scopes. The user-run Stage 6A1 single read on the real GD82
with the meter ON found structurally usable `0x2A25` UTF-8 text and clean
disconnect, but did not establish equality across reads or uniqueness.

- **Branch:** `main`.
- **Last completed checkpoint:** `fb2f76e50e0e85d5d51264b94f982e8f0d88109d` — `feat: add bounded serial identity probe`.
- **Starting tree:** clean, verified with `git status --short` before edits.
- **Changes after checkpoint:** yes, private comparison action, shared internal read result, synthetic tests, and documentation at this pre-commit observation. Report the task commit SHA and post-commit status separately.
- **Files changed:** `custom_components/fora6_connect/serial_stability.py`, `custom_components/fora6_connect/serial_probe.py`, `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/services.yaml`, `tests/test_serial_stability.py`, `tests/test_gatt_probe.py`, `docs/STAGE6A1B_SERIAL_STABILITY.md`, `docs/STAGE6A1_SERIAL_IDENTITY_READ.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`.
- **Live actions:** none during implementation. No physical comparison, FORA command, deployment, push, tag, or release.

## Implementation boundary

The existing bounded read code returns private bytes only to the
integration-local Stage 6A1b comparison function. The public Stage 6A1
`probe_serial_identity` schema remains unchanged. The new manual
`probe_serial_stability` action stores one exact reference in
`hass.data[DOMAIN]["serial_stability"]` under an asyncio lock, replaces it
only after a usable read and clean disconnect, and returns exact-byte match
as a boolean. A missing reference returns `no_reference` without connecting.
No serial, digest, length, address, or raw bytes appear in results, logs,
exceptions, config entries, storage, diagnostics, or device identifiers.
The reference disappears with the HA process. Stage 4 transport/probes and
Stage 5/5A measurement behavior are unchanged; no Config Flow is enabled.

## Checks actually run

- Full unit suite: 209 tests passed.
- `compileall`, `tabnanny`, integration JSON/YAML parsing, `git diff --check`, and `git diff --cached --check` passed.
- Staged privacy scan found no private address, private path, or capture/package artifact; tracked artifact scan found no prohibited file. Source audit confirmed one shared `read_gatt_char` call site and no write, notification, pairing call, hash, config-entry access, or device registration in the comparison module.
- Staged diff confirms unchanged Stage 4 transport/probes, Stage 5/5A measurement files, manifest, and Config Flow scaffold.

**Exact next gate:** user-run Stage 6A1b set/compare with the meter ON,
including one comparison after OFF/ON. Matching supports stability only for
tested conditions and requires a separate uniqueness and production-policy
review. A mismatch blocks this identity route pending investigation; an
unreadable/unusable serial may lead to separately authorized System ID review.
