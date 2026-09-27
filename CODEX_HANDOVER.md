# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stages 0, 1, 2A–2G, 3, 4, 5, 5A, and the focused Stage 6A discovery and
identity-policy review are complete for their authorized scopes. Full Stage 6
Config Flow and device registration have not started. Production sync,
polling, and HA measurement entities remain inactive.

- **Branch:** `main`.
- **Last completed checkpoint:** `b073f68da858404624b68d311e5a9301d5df4df8` — `feat: expose evidence-backed uric-acid measurement`.
- **Starting tree:** clean, verified with `git status --short` before Stage 6A edits.
- **Changes after checkpoint:** yes; documentation/status only at this pre-commit observation. Report the task commit SHA and post-commit status separately.
- **Files changed:** `docs/STAGE6A_DISCOVERY_IDENTITY_POLICY.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/DECISIONS.md`.
- **Live actions:** none. No physical observation, GATT value read, application command, automatic discovery, deployment, push, tag, or release.

## Discovery and identity result

[The Stage 6A policy record](docs/STAGE6A_DISCOVERY_IDENTITY_POLICY.md)
separates a passive candidate, a project-confirmed TD4183/GD82, and a
uniquely identified physical meter. The observed exact normalized name,
advertised `0x1808` and `0x180A`, and connectability support the candidate
shape only. Custom `0x1523` was absent from that advertisement, although
present in connected GATT. The existing `0x22`/`0x24` project `0x4183`
exchange confirms the model/protocol path but is shared by that model and
cannot distinguish two meters.

No retained address series proves stability. Address remains a runtime
locator, never a permanent config-entry or device identifier. Manufacturer
data was present in one advertisement; no company ID, payload length, stable
bytes, or identity meaning was retained. The real Stage 1B GATT metadata
lists readable Device Information Serial Number String `0x2A25` and System
ID `0x2A23`, but the probe read no values. The reviewed app transport uses
Bluetooth addresses for connection; it provides no proof of persistence,
and the bounded source search found no manufacturer-data parsing call.
Current HA Bluetooth documentation supports callback and manifest candidate
matching and connectable device resolution, but does not supply per-meter
identity. No Config Flow or duplicate-device policy can safely be finalized.

## Implementation boundary and checks

This Stage 6A task changed documentation only. `manifest.json` still has no
Bluetooth matcher or `config_flow` flag; `config_flow.py` remains a scaffold.
No callback, connection, sensor, `DeviceInfo`, unique ID, persistence, or
Stage 4/5/5A runtime behavior was added. Private source was read in place;
no private address, payload, serial, capture, or proprietary source is in Git.

- Full existing unit suite: 179 tests passed.
- `compileall`, `tabnanny`, integration JSON/YAML parsing, `git diff --check`, and `git diff --cached --check` passed. Staged privacy/artifact audits found no private path, address, raw response, capture/package artifact, or prohibited tracked file. The staged diff contains no runtime or test file.
- **Exact next gate:** separately authorize private passive address/advertisement comparison and/or a bounded Stage 6A1 read of observed `0x2A25`. Review sanitized evidence before full Stage 6 Config Flow or device registration. Stage 6B/full Config Flow has not started.
