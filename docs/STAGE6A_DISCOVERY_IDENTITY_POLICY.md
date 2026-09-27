# Stage 6A — Bluetooth discovery and stable identity policy

**State:** Offline evidence/policy review complete. No observed field yet
establishes a stable identifier for one physical GD82. Config Flow, a
Bluetooth manifest matcher, persistent entries, and device registration stay
deferred. No physical observation or GATT read was performed in Stage 6A.

## Evidence reviewed

- [Stage 1 advertisement and GATT register](PROTOCOL.md): user-viewed Home
  Assistant Advertisement Monitor details and the user-run Stage 1B
  metadata-only GATT inventory. The advertisement and connected inventory
  are separate observations. The probe read no characteristic value.
- [Stage 1 roadmap observations](../FORA6_MASTER_ROADMAP.md): Active-mode
  advertisement visibility, inconclusive Auto-mode retest, and a successful
  address-supplied Home Assistant GATT connection. No address sequence across
  restarts, power cycles, proxies, or days is retained.
- [Stage 2A manufacturer review](STAGE2_PROTOCOL_ACQUISITION.md): the cited
  ForaCare FAQ identifies the GD82/iFORA HM custom GATT path, but gives no
  per-meter identifier or advertisement identity rule.
- Retained private iFORA HM 1.7.6 `u3/b.java` and 1.7.9 `Y1/b.java`: both use
  an Android Bluetooth address for their connection path. A bounded search
  found no `getManufacturerSpecificData` call in either decompiled source
  tree. This is not proof that no other app path interprets manufacturer data
  or that the address is stable. No private source was copied into Git.
- Current [Home Assistant Bluetooth API guidance](https://developers.home-assistant.io/docs/core/bluetooth/api/),
  [Bluetooth integration guidance](https://developers.home-assistant.io/docs/bluetooth/),
  and [manifest matcher documentation](https://developers.home-assistant.io/docs/creating_integration_manifest/#bluetooth)
  were reviewed on 2026-09-27. HA supplies discovery callbacks, cached
  service information, connectable device resolution, and manifest matchers.
  Those APIs do not turn a candidate field into a per-device identity.

## Advertisement evidence and candidate policy

| Field | Observed result | Identity use |
| --- | --- | --- |
| Complete local name | `FORA 6 CONNECT` with five trailing NUL characters in one HA popup; normalized `FORA 6 CONNECT` in the real Stage 1B action. **OBSERVED** and **LIVE-CORROBORATED** for those observations. | Remove only trailing NUL padding, then require an exact, case-sensitive canonical name for the narrowest candidate. A partial name is insufficient. Name is not a unique ID. |
| Services | `0x1808` and `0x180A` in the viewed advertisement. Custom `0x1523` was absent there but present in connected GATT. **OBSERVED** once. | Require both advertised standard services for the currently supported candidate shape; do not require custom `0x1523` in an advertisement. Their presence is not unique identity. Packet-to-packet completeness remains **UNRESOLVED**. |
| Connectable | Yes in the viewed popup; the Stage 1B action resolved a connectable HA `BLEDevice` and connected. **OBSERVED** and **LIVE-CORROBORATED** in those states. | Require a connectable candidate before any future bounded confirmation. Do not choose a local adapter or proxy. |
| Manufacturer data | Present in the viewed popup; the payload was withheld. **OBSERVED** presence only. | Optional corroborating metadata, not a required matcher or identifier. Company ID, payload length, byte stability, and meaning are **UNRESOLVED**. No payload hash becomes an ID. |
| Address | Used privately as a runtime locator for successful HA connection. **LIVE-CORROBORATED** for reachability only. | Runtime locator only. Stability, address type, and per-meter permanence are **UNRESOLVED**. Never use it as the final config-entry `unique_id` or `DeviceInfo.identifiers` without separate evidence. |

The narrowest **currently observed candidate shape** is: exact normalized
name `FORA 6 CONNECT`, both advertised services `0x1808` and `0x180A`, and
connectability. This is a proposed passive filter, not a proven reliable
production manifest matcher: only one detailed advertisement is preserved,
and HA may report merged or cached service information. Missing fields in a
later packet should not be reinterpreted as a different meter. No matcher or
callback is enabled in this stage. A future manifest matcher cannot perform
the trailing-NUL normalization by itself; the exact-name decision belongs in
the flow after a cautiously scoped discovery trigger and fresh observation.

## Device Information and active model confirmation

The real Stage 1B GATT inventory observed `0x180A` with the following
**Read-property** characteristics: System ID `0x2A23`, Model Number String
`0x2A24`, Serial Number String `0x2A25`, Firmware Revision `0x2A26`, Hardware
Revision `0x2A27`, Software Revision `0x2A28`, Manufacturer Name String
`0x2A29`, IEEE 11073-20601 Regulatory Certification Data List `0x2A2A`,
and PnP ID `0x2A50`. This is **LIVE-CORROBORATED metadata**. No value was
read. Serial Number String and System ID are plausible per-meter identity
sources, but whether either is present, nonempty, unique, or stable in this
GD82 remains **UNRESOLVED**. Manufacturer name, model number, and revision
alone cannot identify one physical meter.

The Stage 4 real-device regression confirms the existing bounded `0x22` →
`0x24` exchange returns project `0x4183`. This is **LIVE-CORROBORATED** model
or protocol-path confirmation, not a unique-device identifier. A future
two-phase setup can passively select a candidate, then run this exchange
only during explicit setup/confirmation. It must not connect continuously
in the background. Even a confirmed project cannot distinguish two GD82
meters or deduplicate their entries without a separate meter-specific ID.
The shared Nordic-style custom `1523/1524` UUID pair is insufficient for
either passive candidate identity or final device identity.

## Config Flow and one-device policy

Home Assistant's Bluetooth manifest matchers and `async_register_callback`
can surface candidates; `async_ble_device_from_address(..., connectable=True)`
can resolve an eligible local adapter or proxy when an explicit confirmation
is authorized. HA's discovery cache is not a fresh packet guarantee, and the
earlier Auto-mode observation did not confirm a new GD82 advertisement. The
future flow must distinguish a candidate, a project-confirmed GD82, and a
uniquely identified physical meter. Only the last state can supply a stable
config-entry `unique_id` and the shared device-registry identifier for that
meter. Until then, no duplicate-device policy can safely reconcile an
address change or distinguish two meters of the same model. An address,
local name, UUID, project ID, model number, or opaque manufacturer-data hash
must not become the permanent ID.

## Separately authorized physical evidence gates

**Passive Stage 6A follow-up:** the user may privately compare one current
meter-ON advertisement, an OFF/ON cycle, a Home Assistant restart, and a
later observation. If useful, compare observations heard by different
scanners without treating the scanner as device identity. Record privately
whether the address, normalized name, advertised UUIDs, connectability,
manufacturer company ID (if HA exposes it), payload length, and payload
equality change. No raw address or manufacturer payload belongs in Git.
These observations can test address stability in those states; one meter and
one period cannot prove permanent uniqueness.

**Proposed Stage 6A1 — bounded Device Information identity read:** after
separate authorization, connect through the already proven HA path and read
only Serial Number String `00002a25-0000-1000-8000-00805f9b34fb` in service
`0000180a-0000-1000-8000-00805f9b34fb`. It was actually observed with the
Read property and could provide a meter-specific value. Require a short,
bounded read and clean disconnect. Do not send any FORA application command,
pair, or dump other GATT values. The action should report only whether a
nonempty value was readable, its sanitized type/length, and private equality
across controlled repeat reads; no serial text, address, raw bytes, or hash
in a public result or tracked file. If absent or generic, a later separately
authorized System ID `0x2A23` review may be considered. Neither a single
read nor a model string alone proves cross-meter uniqueness.

**Exact next gate:** separately authorize the passive comparison and/or the
bounded Stage 6A1 Serial Number String read. Review their privacy-safe
results before implementing full Stage 6 Config Flow or device registration.
