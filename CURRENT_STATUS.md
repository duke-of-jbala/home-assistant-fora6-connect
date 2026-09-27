# Current Status — FORA 6 Connect

**Stages 0, 1, 2A–2G, 3, 4, 5, 5A, and Stage 6A's separately authorized
discovery/identity-policy review are complete for their bounded scopes.**
Full Stage 6 Config Flow, persistent device identity, entities, production
synchronization, and polling have not started.

## Stage 6A conclusion

[The Stage 6A evidence record](docs/STAGE6A_DISCOVERY_IDENTITY_POLICY.md)
reviews the observed advertisement, real Stage 1B GATT inventory, retained
app transport code, manufacturer notes, and current Home Assistant APIs.
Exact local name after stripping trailing NUL padding, advertised `0x1808`
and `0x180A`, and connectability describe a passive **candidate** in the one
recorded advertisement shape. The already proven project `0x4183` exchange
can confirm a TD4183/GD82 protocol path. Neither step identifies one physical
meter.

The Bluetooth address is a runtime connection locator only; stability across
power cycles, restarts, proxies, or time is untested. Manufacturer data was
observed as present, but its company ID, payload length, contents, and
stability were not retained. The real connected `0x180A` inventory includes
readable Serial Number String `0x2A25` and System ID `0x2A23`; no value was
read. Thus no stable per-meter ID, duplicate-device policy, config-entry
`unique_id`, or `DeviceInfo.identifiers` is supported yet. No manifest
matcher, callback, Config Flow, device registration, or automatic connection
was enabled by Stage 6A.

Stage 5A remains intact: valid identified uric-acid raw `/10` maps to the
app's mg/dL base value in the product model, while QC/AC/PC, invalid, and
unsupported records do not become ordinary numeric state. There is still
no registered `SensorEntity` or decoded real-result action.

## Exact next gate

Separately authorize a private passive address/advertisement comparison
and/or **Stage 6A1 — one bounded read of the already observed Device
Information Serial Number String `0x2A25`**. Review the sanitized result
before authorizing full Stage 6 Config Flow and device registration. No
physical test or new BLE command was performed in Stage 6A.

## Repository observation before Stage 6A commit

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed checkpoint:** `b073f68da858404624b68d311e5a9301d5df4df8` — `feat: expose evidence-backed uric-acid measurement`.
- **Starting tree:** clean; `git status --short` returned no entries before edits.
- **Changes after checkpoint:** yes, Stage 6A documentation and status files only. This is a pre-commit observation; the task commit SHA and post-commit status are reported separately.
- **Files changed:** `docs/STAGE6A_DISCOVERY_IDENTITY_POLICY.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/DECISIONS.md`.
- **Live actions:** none. No physical observation, GATT read, FORA command, Home Assistant action, deployment, push, tag, or release.

## Checks actually run

- Full existing unit suite: 179 tests passed.
- `compileall`, `tabnanny`, integration JSON/YAML parsing, `git diff --check`, and `git diff --cached --check` passed.
- The staged privacy scan found no private absolute path, Bluetooth address, raw response sequence, or capture/package artifact. The tracked artifact scan found no prohibited files.
- No runtime or test file was edited. The staged diff confirms transport, probes, measurement mapping, manifest, and config-flow scaffold remain unchanged; no new callback, connection, `DeviceInfo` identifier, or command was added.
