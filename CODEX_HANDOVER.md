# FORA 6 Connect Codex Handover

## Stage and checkpoint

Stage 0 and Stage 1 are complete. Stage 2A public review, 2B static analysis, 2C controlled app capture, and 2D offline primitives are complete. **Stage 2E is authorized and its development-only Home Assistant identity probe is implemented, but no physical Stage 2E result exists yet.** Production synchronization, record retrieval, pairing, standard Glucose/RACP operations, and entities remain out of scope.

- **Branch:** `main`.
- **Last completed checkpoint:** `0d293b3d37ef867670468566f14eac55f347be5b` — `feat: add evidence-backed GD82 protocol primitives`.
- **Starting tree:** clean at the verified checkpoint.
- **Changes after checkpoint:** yes; this handover describes the dirty pre-commit state. Report the task commit SHA and final working-tree status separately.
- **Files changed:** `CHANGELOG.md`, `CODEX_HANDOVER.md`, `CURRENT_STATUS.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `custom_components/fora6_connect/__init__.py`, `custom_components/fora6_connect/protocol_probe.py`, `custom_components/fora6_connect/services.yaml`, `custom_components/fora6_connect/translations/en.json`, `docs/ARCHITECTURE.md`, `docs/CAPTURE_GUIDE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`, `docs/STAGE2_PROTOCOL_ACQUISITION.md`, `docs/STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md`, `tests/test_gatt_probe.py`, and `tests/test_protocol_probe.py`.

## Implementation boundary

`fora6_connect.probe_protocol_identity` takes a private runtime-only address, resolves a connectable BLEDevice through Home Assistant, subscribes only to custom `1524`, writes the fixed Stage 2C `0x22` wake request and then the fixed `0x24` project request with `response=True`, validates matching checksummed notification frames using HA-independent `protocol.py`, requires project `0x4183`, and cleans up. Each wait is bounded; errors are stable sanitized categories. The action contains no record command or RACP/standard Glucose path. No automatic invocation, config flow, entity, polling, pairing, measurement parsing, or production synchronization was added. `protocol.py` was not changed.

The first real Home Assistant run is **pending**. The prior patched research-app capture confirmed the corresponding proprietary exchange on GD82, but does not prove this Home Assistant path succeeds. See [Stage 2C evidence](docs/STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md), [protocol register](docs/PROTOCOL.md), and [Stage 2E procedure](docs/STAGE2E_HA_PROTOCOL_IDENTITY_PROBE.md). Raw notification bytes and the private address are neither returned nor persisted.

## Checks actually run

- Focused new probe suite: 19 passed after connection-slot and log-privacy tests were added.
- Full unit suite: 72 passed after implementation and documentation edits.
- Compileall, tabnanny, and `git diff --check`: passed. Translation/manifest JSON and service YAML parsed successfully.
- Ruff unavailable. Staged diff check passed; the 19 intended text files were staged and reviewed. Final privacy/scope audit found no private path, real Bluetooth address, health value, timestamp, capture/APK/signing artifact, or new production path. An older GATT test's `AA`-repeated address is synthetic. `protocol.py` remains HA/Bluetooth independent, and the new action references only the captured wake and project constructors.

## Exact next gate

Privately install the development build in Home Assistant; invoke `fora6_connect.probe_protocol_identity` on the real GD82 and return only the action's privacy-safe structured result. Review that result before closing Stage 2E or authorizing further protocol or production work. No new health measurement is needed.
