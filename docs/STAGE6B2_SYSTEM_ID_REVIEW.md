# Stage 6B2 — bounded System ID identity review

## Purpose and evidence

Stage 6B1's user-run Home Assistant regression preserved the existing device and unavailable uric-acid entity, removed the false “Serial Number” display, suppressed repeat Add cards, and retained Bluetooth connection metadata. The user privately confirmed that the HA Bluetooth locator matches the meter's printed BT MAC. The actual MAC and printed serial remain outside Git. GATT `0x2A25` supplies a generic text placeholder for this meter, so the existing ConfigEntry's meter-specific identity remains unresolved.

The earlier sanitized GATT inventory observed a readable standard System ID characteristic `0x2A23` in Device Information service `0x180A`, but no value was read. Stage 6B2 adds manually invoked, read-only evidence actions; it does not migrate the current entry or change discovery, device identifiers, entities, or synchronization.

## Standard and structural rule

The [Bluetooth SIG Device Information Service v1.2, §3.7](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/DIS_v1.2/out/en/index-en.html) defines System ID as an OUI plus a manufacturer-defined identifier, intended to be unique for each individual product instance. The characteristic is optional and read-only. The [Bluetooth SIG Personal Health Devices Transcoding white paper](https://www.bluetooth.com/wp-content/uploads/2019/03/PHD_Transcoding_WP_v16.pdf) describes its wire format as `uint40` manufacturer identifier plus `uint24` OUI: eight octets in total. These are **STANDARD-DOCUMENTED** semantics, not proof that this GD82 contains a correctly provisioned value. The standard notes fixed unique identifiers can be personally identifying; the action treats the bytes as private.

`system_id_format_plausible` means exactly eight octets. `system_id_value_usable` additionally rejects all-zero and all-`0xFF` eight-octet values as conservative placeholder checks. That rejection is **INFERRED local policy**, not a Bluetooth SIG field rule. Neither flag proves uniqueness or any relationship to the printed BT MAC or serial. The probe does not decode the OUI or manufacturer portion, derive a MAC, or expose the length or bytes.

## Bounded actions

`fora6_connect.probe_system_id` takes only a private runtime Bluetooth address. It resolves a connectable device through Home Assistant Bluetooth, uses the established bounded retry-safe connector with `pair=False`, finds service `0x180A` and readable characteristic `0x2A23`, reads it **once**, then disconnects. It returns only structural/lifecycle booleans and stable privacy-safe error codes. It sends no write, notification subscription, FORA command, RACP, or health-data request.

`fora6_connect.probe_system_id_stability` takes that address and either `set_reference` or `compare`. Each operation that needs data repeats the same one-read path. One exact raw-byte reference is held behind an asyncio lock at `hass.data[DOMAIN]["system_id_stability"]`; it is replaced only after a usable read and clean disconnect. `compare` without a reference returns `no_reference` without connecting. Results contain only `reference_set`, `reference_available`, `system_id_matches_reference`, and the same structural/lifecycle flags. No hash, digest, length, prefix, suffix, byte value, or derived identifier is returned. Restarting HA clears the reference. Failed reads and cancellation preserve the previous reference.

Both actions suppress raw exception text. They do not log or persist the System ID, serial, address, or health data. No ConfigEntry or DeviceInfo value changes. Their synthetic tests do not contain real identifiers.

## User-run physical sequence after review

1. With the meter ON, run `probe_system_id` once. Check that the characteristic is present, readable, read successfully, structurally plausible, usable, and cleanly disconnected. Share only the sanitized result.
2. Run `probe_system_id_stability` with `set_reference`; expect `reference_set: true`.
3. Run `compare` immediately; expect `system_id_matches_reference: true`.
4. Switch the meter OFF and ON, wait for it to advertise, then run `compare` once more. A true result supports stability across this tested power cycle.
5. Optionally restart HA. `compare` should return `no_reference`, showing process-local reference cleanup.

These actions do not run automatically. No public comparison with the printed BT MAC or serial is made. Such a comparison, if useful, needs a separate explicitly authorized private procedure.

## Interpretation and next gate

An absent, unreadable, malformed, or constant-filled System ID leaves meter-specific identity unresolved; do not migrate or fall back to MAC. A differing immediate or post-power-cycle value shows instability under that condition and blocks canonical use. Repeated equality of a plausible nonconstant value would provide **LIVE-CORROBORATED** stability for this one meter, while uniqueness across devices, reset/update behavior, and the relationship to the printed label remain **UNRESOLVED**. The SIG's intended instance uniqueness is **STANDARD-DOCUMENTED**; actual manufacturer provisioning still needs review before choosing a canonical ID.

The exact next gate after private physical results is a separately authorized Stage 6B3 identity-policy/migration review. It must decide whether `0x2A23` is suitable, whether a second meter or manufacturer source is needed to test collision risk, and how to preserve the existing ConfigEntry, device, and entity IDs. Stage 7D and production synchronization remain outside this scope.
