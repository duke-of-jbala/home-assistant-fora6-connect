# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stage 6A1's development-only bounded `0x2A25` action is implemented and
hardware-free tested. Earlier stages through 6A remain complete for their
authorized scopes. Stage 6A1 has **no physical result yet**. Full Stage 6
Config Flow, permanent meter identity, device registration, production sync,
and polling remain deferred.

- **Branch:** `main`.
- **Last completed checkpoint:** `5b1ee153ed768892116bccdde969277b6974d478` — `docs: define FORA discovery and identity policy`.
- **Starting tree:** clean, verified with `git status --short` before edits.
- **Changes after checkpoint:** yes; development-only read action, synthetic tests, and documentation at this pre-commit observation. Report task commit SHA and post-commit status separately.
- **Files changed:** `custom_components/fora6_connect/serial_probe.py`, `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/services.yaml`, `tests/test_serial_probe.py`, `tests/test_gatt_probe.py`, `docs/STAGE6A1_SERIAL_IDENTITY_READ.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`.
- **Live actions:** none. No physical read, FORA command, deployment, push, tag, or release.

## Implementation and evidence boundary

The real Stage 1B inventory observed readable standard Device Information
Serial Number String `0x2A25`; it did not read its value. The new manual
`fora6_connect.probe_serial_identity` action connects through HA Bluetooth,
reads only that characteristic once, and disconnects with bounded cleanup.
Connection task cancellation owns clients returned during cancellation.
The action uses no write, notification subscription, pairing, other GATT
read, FORA command, or application transport. The serial is classified in
memory as present/UTF-8/printable without returning text, digest, length,
or any comparison token. The runtime address is absent from errors/results.
No callback, manifest matcher, config entry, or DeviceInfo identifier exists.

[The Stage 6A1 record](docs/STAGE6A1_SERIAL_IDENTITY_READ.md) explains why
a usable structural response alone cannot prove stability or uniqueness.

## Checks actually run

- Full unit suite: 195 tests passed.
- `compileall`, `tabnanny`, integration JSON/YAML parsing, `git diff --check`, and `git diff --cached --check` passed.
- Staged privacy scan found no private address, private path, or capture/package artifact; the tracked-artifact scan found no prohibited file. Source audit confirmed one `read_gatt_char` call site and no write, notify, pairing call, command constructor, config-entry access, or device registration in the new probe.
- Stage 4 transport/probe and Stage 5/5A measurement files are unchanged.

**Exact next gate:** controlled user-run Stage 6A1 read and privacy-safe result
review. If structurally usable, separately authorize private stability and
uniqueness comparison. If unusable, separately authorize bounded Stage 6A2
System ID review. Do not start Config Flow or device registration yet.
