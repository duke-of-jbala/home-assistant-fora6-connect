# Stage 6A1c — serial uniqueness and production identity policy

**State:** Evidence and policy review complete. The user-run Stage 6A1b
comparison found one GD82's `0x2A25` value unchanged on an immediate repeat
and after one meter OFF/ON cycle. No Config Flow, persisted serial, matcher,
device registration, or automatic probe is implemented by this review.

## Evidence and classification

| Question | Finding | Class |
| --- | --- | --- |
| Standard meaning | Bluetooth SIG Device Information Service v1.2 §3.3 defines Serial Number String `0x2A25` as the serial number for a particular instance of a device. It is optional and readable. The specification does **not** state that every deployed product's value is globally distinct. Its §3.7 System ID wording explicitly says unique for each individual instance; that is a different field, not evidence about this meter's `0x2A25`. [SIG DIS specification](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/DIS_v1.2/out/en/index-en.html). | **STANDARD-DOCUMENTED** |
| Privacy | The same specification advises authentication when Serial Number String, System ID, or medical UDI is present because a fixed unique number can be personally identifying. The tested meter allowed an unpaired read; Stage 6A1c does not add pairing or alter security. [SIG DIS specification](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/DIS_v1.2/out/en/index-en.html). | **STANDARD-DOCUMENTED** for caution; **LIVE-CORROBORATED** for this unpaired read |
| Manufacturer | The [FORA 6 Connect GD82 manual](https://foracare.ch/wp-content/uploads/2021/10/FORA-6-Connect-GD82-4183D_meter-manual_311-4183400-070.pdf) recognizes an SN/serial-number marking in its symbol legend. The reviewed manual and [manufacturer product page](https://www.foracare.ch/fora-6-connect/) do not say that the GATT `0x2A25` value equals the printed marking, is unique across GD82 meters, or survives reset/firmware changes. | **MANUFACTURER-DOCUMENTED** marking; **UNRESOLVED** GATT mapping/uniqueness |
| App/static path | Retained private iFORA HM 1.7.6 `b4/a.java` and 1.7.9 `f2/a.java` each have a proprietary two-response “Serial Number” parser for command numbers 39/40. Their Bluetooth transport classes `u3/b.java` and `Y1/b.java` use Android addresses for connection. A bounded search found no literal `0x2A25`/standard-UUID reference in those source paths. No source evidence equates the proprietary result with GATT `0x2A25` or proves app identity policy. No private source is tracked. | **STATIC-ANALYSIS-SUPPORTED** for those paths; relationship **UNRESOLVED** |
| Physical GD82 | Stage 6A1 found a readable, nonempty usable UTF-8 `0x2A25` value. Stage 6A1b private in-memory comparison matched on an immediate read and after one OFF/ON cycle; all three bounded reads disconnected cleanly. No value, digest, length, address, or recoverable representation was published. | **LIVE-CORROBORATED** stability for this meter and tested conditions |
| Wider population | No second physical GD82, factory-reset test, firmware-update test, or manufacturer per-unit assignment guarantee is available. Blank/default values and collisions on other meters remain possible. No evidence shows the tested value changed or collided. | **UNRESOLVED** |

## Identity judgment

`0x2A25` is the **preferred conditional production identity source** for the
TD4183/GD82 path: its standard semantics are instance-specific, the real
meter returns usable text, and the value remained stable across the tested
repeat and power cycle. This supports implementing a guarded Stage 6B setup
flow after separate authorization. It does **not** establish global
uniqueness or permit silent merging of two physical meters with a colliding
value. Collision-safe behavior is a requirement of Stage 6B and its tests.

[Home Assistant Config Flow guidance](https://developers.home-assistant.io/docs/core/integration/config_flow/)
accepts a device serial number as a unique-ID source, requires a stable
string within the integration domain, and provides `async_set_unique_id` plus
`_abort_if_unique_id_configured` for duplicate prevention. [Home Assistant
device-registry guidance](https://developers.home-assistant.io/docs/device_registry_index/)
defines `DeviceInfo.identifiers` as `(domain, identifier)` pairs and notes
that matching identifiers associate an entity with a registered device.
These HA rules guide future implementation; they do not prove manufacturer
assignment quality.

**Future exact namespace, if the guarded Stage 6B flow is approved:** decode
the validated `0x2A25` bytes as UTF-8 without changing the text, then use
`ConfigEntry.unique_id = exact_serial_text` within the `fora6_connect`
domain and `DeviceInfo.identifiers = {(DOMAIN, exact_serial_text)}` for all
entities of that meter. Validation may reject invalid/blank text, but must
not trim, fold case, alter punctuation, drop leading zeroes, normalize
Unicode, or replace the value with a public digest. The existing Stage 6A1b
comparison uses exact bytes; a future implementation must explicitly test
that its UTF-8 identity mapping preserves those bytes. No actual serial is
written by Stage 6A1c.

This future choice deliberately persists a private identifier inside HA's
config-entry/device-registry data. Do not surface it as a sensor attribute,
`DeviceInfo.serial_number` display field, action response, log, diagnostics
field, issue report, or screenshot. Do not add the Bluetooth address as a
`DeviceInfo.connection` or identifier. Limit access to setup and internal
registry matching, and redact serials and addresses from errors. This is an
internal identity policy, not a claim that HA storage is anonymous.

## Discovery, reconnection, and failure policy for Stage 6B

1. Treat the normalized exact local name, advertised `0x1808`/`0x180A`, and
   connectability as a **candidate shape** based on one detailed observed
   advertisement. Manufacturer-data presence is corroboration only; custom
   `0x1523` need not appear in the advertisement. Do not claim a candidate as
   a GD82 or assume every future packet contains every field.
2. During explicit setup/confirmation, use the already proven bounded
   `0x22` → `0x24` exchange to require project `0x4183` as model/protocol
   confirmation. Project ID, name, services, and address are never unique IDs.
3. Read standard Device Information `0x2A25` once, validate usable exact
   UTF-8 text, and establish the future domain-scoped unique ID before
   creating an entry. No persistent entry is created on identity failure.
4. Keep the Bluetooth address as a **current runtime transport locator**.
   Do not promote it to `ConfigEntry.unique_id`, `DeviceInfo.identifiers`, or
   a fallback identity. An address change must not by itself create another
   meter. Reconfirm project and serial before any deliberate locator change.

| Case | Required policy |
| --- | --- |
| Empty, padding-only, malformed UTF-8, control-character, or unreadable serial during setup | Fail closed with a privacy-safe retry reason; create no entry or device. Do not substitute MAC, model, project, or manufacturer bytes. Do not invent a placeholder blacklist without evidence. |
| Duplicate serial already configured | Abort duplicate setup through HA unique-ID handling. If two simultaneously reachable candidates claim it, quarantine the collision; do not silently merge them or update either locator. Require explicit user investigation. |
| Same serial at a new address | Do not create a second entry. After explicit model/serial confirmation, allow a user-reviewed runtime locator update only when no simultaneous conflicting candidate is present. Automatic reassociation needs a separately tested Stage 6B policy. |
| Same address with a different serial | Treat as a different or ambiguous physical device. Do not overwrite the existing entry's ID or measurements; require explicit setup/investigation. |
| Project/identity confirmation fails | Stop setup; no entry, device, or measurement exposure. |
| Serial temporarily unavailable for an existing entry | Keep the existing identity, mark connection unavailable/retry later under future policy, and avoid creating a replacement entry or falling back to address. |

The exact selected HA adapter/proxy remains Stage 9 work. Fresh Auto-mode
advertisement behavior and address rotation are unproven. Stage 6B must test
candidate discovery without a UUID-only claim and must avoid continuous
background identity probes.

## Stage 6B entry gate

Stage 6B **implementation is justified after separate authorization** for a
guarded Config Flow and one-device association using the conditional serial
policy above. Before any production claim or deployment, its tests and
controlled validation must cover: exact serial preservation, privacy-safe
storage and diagnostics, duplicate and ambiguous serial handling, address
changes, identity/read failures, candidate versus model confirmation, and
one-device-per-meter association. Population-wide uniqueness, reset/update
stability, and equality with the printed SN remain unresolved; do not state
them as facts or silently auto-merge on their assumption.

## Stage 6B follow-up

[Stage 6B](STAGE6B_CONFIG_FLOW_DEVICE_IDENTITY.md) implements this conditional policy with exact validated serial text in private Home Assistant entry/device identity, a mutable locator, collision checks, and one unavailable uric-acid sensor. It has synthetic validation only. Population uniqueness, reset/update stability, and controlled real Config Flow behavior remain unresolved.
