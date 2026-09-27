# Stage 6B — guarded Config Flow and persistent device identity

**Scope:** offline implementation and synthetic validation. No physical Config Flow run, production record synchronization, polling, pairing, RACP, or new FORA command occurred in this stage. The controlled Home Assistant setup test remains a separate gate.

## Evidence and boundaries

[Stage 6A1c](STAGE6A1C_SERIAL_IDENTITY_POLICY.md) records the standard, manufacturer, static, and user-run evidence. Bluetooth SIG assigns `0x2A25` Serial Number String to a particular device instance. The tested GD82 returned usable UTF-8 text that matched on an immediate repeat and after one OFF/ON cycle. Population-wide uniqueness, reset/update behavior, printed-label equality, address stability, and the selected HA scanner/proxy remain unresolved.

The integration persists the **exact validated UTF-8 serial text** internally as the domain-scoped `ConfigEntry.unique_id` and as `DeviceInfo.identifiers={(DOMAIN, serial)}`. It does not trim, case-fold, normalize Unicode, or hash it. This is deliberate private Home Assistant storage, not a public identifier. The serial is absent from the entry title, entity name and attributes, action output, errors, and integration logs. The entity unique ID uses the HA entry ID plus an analyte suffix; `DeviceInfo.serial_number` is unset.

The Bluetooth address is stored only in `ConfigEntry.data["address"]` and the entry's inert runtime holder as a mutable connection locator. It is neither a unique ID nor a `DeviceInfo` identifier/connection. Project `0x4183` confirms the TD4183/GD82 protocol path, not an individual meter. Manufacturer data is neither required nor interpreted.

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

`async_setup_entry` validates the internal serial and locator, creates an inert `MeterRuntime` with `MeasurementState`, and forwards only the sensor platform. The single `Fora6UricAcidSensor` attaches to `DeviceInfo.identifiers={(DOMAIN, exact_serial)}`, uses the evidenced mg/dL base unit, and starts unavailable with no value. It has no polling, device class, state class, Bluetooth I/O, or startup measurement fetch. Only a later evidence-backed feed may set a valid ordinary General-category uric-acid product measurement. QC, AC, PC, invalid sentinel, and unsupported analytes yield unavailable numeric state under the existing Stage 5/5A mapper. Meter-local time stays in the product model, separate from HA state/update time. Unload forwards only the sensor platform.

The Home Assistant APIs followed are [Bluetooth manifest matchers](https://developers.home-assistant.io/docs/creating_integration_manifest/), [Config Flow unique IDs](https://developers.home-assistant.io/docs/core/integration/config_flow/), [entry setup forwarding](https://developers.home-assistant.io/docs/config_entries_index/), [device identifiers](https://developers.home-assistant.io/docs/device_registry_index/), and [sensor entities](https://developers.home-assistant.io/docs/core/entity/sensor/).

## Next gate

After code review, separately authorize a controlled real Home Assistant Bluetooth discovery/setup test with the meter ON. Observe whether the manifest candidate reaches the confirmation form, complete one guarded setup, check that one unavailable uric-acid entity belongs to one generic FORA device, and repeat discovery to confirm duplicate abort. Report only privacy-safe booleans/status; do not share the serial, address, raw bytes, or health result. Any Auto-mode/proxy-path claim remains Stage 9 evidence. Stage 7 historical synchronization requires separate authorization and a further evidence-backed record traversal/deduplication policy.
