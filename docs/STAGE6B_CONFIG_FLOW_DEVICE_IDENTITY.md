# Stage 6B — guarded Config Flow and persistent device identity

**Stage 6B1 correction:** [the rediscovery and metadata follow-up](STAGE6B1_REDISCOVERY_LOCATOR_FIX.md) records a later repeat card and a private check that the existing entry's unique ID is the generic literal “Serial Number.” This limits the earlier claim of meter-specific serial identity for that entry. New flows reject the placeholder; the existing entry is preserved pending a separate identity gate.

**Scope:** implementation, synthetic validation, and user-run real Home Assistant discovery/setup validation on one GD82. No production record synchronization, polling, pairing, RACP, or new FORA command was introduced.

## Evidence and boundaries

[Stage 6A1c](STAGE6A1C_SERIAL_IDENTITY_POLICY.md) records the standard, manufacturer, static, and user-run evidence. Bluetooth SIG assigns `0x2A25` Serial Number String to a particular device instance. The tested GD82 returned usable UTF-8 text that matched on an immediate repeat and after one OFF/ON cycle. Population-wide uniqueness, reset/update behavior, printed-label equality, address stability, and the selected HA scanner/proxy remain unresolved.

The integration persists the **exact validated UTF-8 serial text** internally as the domain-scoped `ConfigEntry.unique_id` and as `DeviceInfo.identifiers={(DOMAIN, serial)}`. It does not trim, case-fold, normalize Unicode, or hash it. This is deliberate private Home Assistant storage, not a public identifier. A later metadata refinement also sets `DeviceInfo.serial_number` to the same exact text, intentionally displaying it on the authenticated local HA device page. The serial remains absent from the entry title, entity name and attributes, action output, errors, diagnostics, and integration logs. The entity unique ID uses the HA entry ID plus an analyte suffix.

The Bluetooth address is stored in `ConfigEntry.data["address"]` and the entry's inert runtime holder as a mutable connection locator. A later metadata refinement also supplies the current runtime address in `DeviceInfo.connections={(CONNECTION_BLUETOOTH, address)}` when the entity is registered. Home Assistant defines this Bluetooth connection type; its registry matches an existing device by identifiers first, then connections. The exact serial remains the canonical `ConfigEntry.unique_id` and `DeviceInfo` identifier, so a new confirmed address does not change logical identity. The address is not placed in `DeviceInfo.identifiers` or the entry unique ID. Project `0x4183` confirms the TD4183/GD82 protocol path, not an individual meter. Manufacturer data is neither required nor interpreted. The meter has no independent IP address; no proxy or host IP is attributed to it. [Home Assistant's device registry](https://developers.home-assistant.io/docs/device_registry_index/) defines `DeviceInfo.connections`, `serial_number`, `model`, and `model_id`; [Core's registry module](https://github.com/home-assistant/core/blob/dev/homeassistant/helpers/device_registry.py) defines `CONNECTION_BLUETOOTH`.

## Candidate and guarded confirmation

The manifest requests a connectable `FORA 6 CONNECT*` local-name candidate advertising Glucose `0x1808`. Home Assistant's manifest matcher cannot require both service UUIDs in one rule. `discovery.is_fora_candidate` therefore requires the exact name after removing only trailing NUL padding, `0x1808`, `0x180A`, and connectability. It does not require custom `0x1523` in the advertisement and performs no I/O. This is candidate selection only.

The Bluetooth flow displays a generic confirmation form before connecting. After user confirmation, `setup_identity` uses the Stage 4 transport to connect through HA, validate custom `1524`, subscribe, exchange only captured wake `0x22` and project `0x24`, require project `0x4183`, and stop notifications/disconnect. It then reuses the bounded Stage 6A1 Device Information path in a separate connection to read `0x2A25` once and disconnect. The second connection preserves both previously tested session boundaries. A failed exchange, malformed/project-mismatched response, unusable serial, or failed cleanup aborts setup. No record command, write other than the two authorized identity requests, pairing, or background probe is added.

## Collision and locator policy

| Situation | Outcome |
| --- | --- |
| Same confirmed serial, same locator | Abort `already_configured`; no second entry. |
| Same confirmed serial, new locator | Show a second user review. Recheck entries; if another entry owns the new locator or the old locator remains HA-connectable, abort `identity_conflict`. Otherwise update only the existing entry's locator and inert runtime locator, then abort the new flow as `locator_updated`. No second entry/device. HA cache staleness can conservatively block an update; retry after it clears. |
| Same locator, different confirmed serial | Abort `identity_conflict`; do not merge or overwrite. |
| Concurrent flows claiming one serial | HA `async_set_unique_id` arbitrates in-progress flows; the flow also checks existing entries and calls `_abort_if_unique_id_configured` before new entry creation. Only one entry may be created. |
| Empty, malformed, unreadable, or temporarily unavailable serial | Abort `serial_unavailable`; no MAC, project, name, or manufacturer-data fallback. |
| Project mismatch or identity/connection failure | Abort with a stable, privacy-safe reason; create no entry/device. |

Collision handling cannot prove global serial uniqueness. Any suspected two-meter serial collision needs private investigation; this implementation does not silently merge a simultaneously reachable old locator.

## Device and entity

`async_setup_entry` validates the internal serial and locator, creates an inert `MeterRuntime` with `MeasurementState`, and forwards only the sensor platform. The single `Fora6UricAcidSensor` attaches to `DeviceInfo.identifiers={(DOMAIN, exact_serial)}`, displays that serial through `DeviceInfo.serial_number`, and supplies its current runtime Bluetooth address as connection metadata. It retains `name="FORA 6 Connect"`, `manufacturer="ForaCare"`, and `model="GD82"`. `GD82` remains the displayed model; setting the same value as `model_id` would duplicate it without better evidence. The entity uses the evidenced mg/dL base unit and starts unavailable with no value. It has no polling, device class, state class, Bluetooth I/O, or startup measurement fetch. Only a later evidence-backed feed may set a valid ordinary General-category uric-acid product measurement. QC, AC, PC, invalid sentinel, and unsupported analytes yield unavailable numeric state under the existing Stage 5/5A mapper. Meter-local time stays in the product model, separate from HA state/update time. Unload forwards only the sensor platform.

The connection value is a snapshot of the confirmed runtime locator when the entity is registered. The guarded Config Flow can subsequently change that locator after serial reconfirmation; the entity's serial-backed identifier remains unchanged. Home Assistant may retain an earlier connection alongside a new one after later entity registration, so automatic removal of stale registry connection metadata is deferred until address rotation is physically observed and a safe registry update policy is reviewed. No new connection or sync action is initiated by this metadata refinement.

The Home Assistant APIs followed are [Bluetooth manifest matchers](https://developers.home-assistant.io/docs/creating_integration_manifest/), [Config Flow unique IDs](https://developers.home-assistant.io/docs/core/integration/config_flow/), [entry setup forwarding](https://developers.home-assistant.io/docs/config_entries_index/), [device identifiers](https://developers.home-assistant.io/docs/device_registry_index/), and [sensor entities](https://developers.home-assistant.io/docs/core/entity/sensor/).

## Real Home Assistant validation and conclusion

The user deployed this implementation and observed automatic discovery of FORA 6 Connect, the discovery card, the confirmation flow, and successful setup. Home Assistant created one device with metadata `GD82` by `ForaCare` and exactly one uric-acid entity whose state was Unavailable, as expected without Stage 7 data. No serial or Bluetooth address appeared in the observed UI. After a meter OFF/ON cycle, no discovery card reappeared and the totals remained one device and one uric-acid entity.

This validates production discovery, guarded identity confirmation, private serial identity, ConfigEntry creation, DeviceInfo association, and one-device/entity registration for this meter. The explicit duplicate-abort flow was not exercised because Home Assistant did not offer the already-configured meter again. Do not claim that branch was physically tested or infer population-wide serial uniqueness.

**Stage 6B is complete for its authorized scope.** Population-wide serial uniqueness, factory-reset/firmware-update behavior, long-term Bluetooth address stability, manufacturer-data semantics, exact scanner/proxy path (Stage 9), historical record synchronization, deduplication/resume policy, and automatic measurement retrieval remain unresolved or deferred. **Exact next gate:** separately authorize Stage 7 synchronization design and implementation.
