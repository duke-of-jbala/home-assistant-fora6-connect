# Current Status — FORA 6 Connect

Stages 0, 1, 2A–2G, 3, 4, 5, 5A, 6A, and 6A1 are complete for their authorized
scopes. Stage 6A1b private comparison code is implemented and hardware-free
tested; **no physical comparison has been run**. Full Stage 6 Config Flow,
permanent device identity, device registration, production sync, and polling
remain deferred.

## Identity evidence and Stage 6A1b boundary

The user-run Stage 6A1 read on the real GD82 with the meter ON returned
readable, nonempty, usable UTF-8 text from standard Device Information
`0x2A25`, followed by clean disconnect and no errors. The private serial was
not published. One result establishes structural usability in that state,
not stability or global uniqueness.

[Stage 6A1b](docs/STAGE6A1B_SERIAL_STABILITY.md) adds manual
`fora6_connect.probe_serial_stability` operations `set_reference` and
`compare`. One exact private byte sequence lives only in
`hass.data[DOMAIN]["serial_stability"]` for this HA process. A lock serializes
reads and updates. Failed, unusable, or cancelled reads preserve the current
reference; successful comparison returns only equality. No serial, address,
digest, length, or raw bytes enter action results or logs. There is no FORA
command, write, notification, pairing, persistent config entry, DeviceInfo
identifier, or automatic probe. The existing Stage 6A1 action retains its
result schema. Stage 4 transport/probes and Stage 5/5A measurement behavior
are unchanged.

## Repository observation before Stage 6A1b commit

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `fb2f76e50e0e85d5d51264b94f982e8f0d88109d` — `feat: add bounded serial identity probe`.
- **Starting tree:** clean; `git status --short` returned no entries before edits.
- **Changes after checkpoint:** yes, private comparison action, shared internal read result, synthetic tests, and documentation at this pre-commit observation. Report the task commit SHA and post-commit status separately.
- **Files changed:** `custom_components/fora6_connect/serial_stability.py`, `custom_components/fora6_connect/serial_probe.py`, `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/services.yaml`, `tests/test_serial_stability.py`, `tests/test_gatt_probe.py`, `docs/STAGE6A1B_SERIAL_STABILITY.md`, `docs/STAGE6A1_SERIAL_IDENTITY_READ.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`.
- **Live actions:** none during implementation. No physical comparison, deployment, push, tag, or release.

## Checks actually run

- Full unit suite: 209 tests passed.
- Final quality, privacy, and artifact checks are recorded in `CODEX_HANDOVER.md`.

**Exact next gate:** controlled user-run Stage 6A1b set/compare before and
after a meter OFF/ON cycle. If matching, review stability evidence and the
separate uniqueness basis before Config Flow. If mismatching, investigate
without registering the meter. If unreadable/unusable, consider a separately
authorized bounded System ID `0x2A23` review.
