# Stage 6A1b — private in-memory serial stability comparison

**State:** Development-only set/compare action implemented and hardware-free
tested. No Stage 6A1b physical comparison has been performed.

## Evidence and boundary

The user-run [Stage 6A1 bounded read](STAGE6A1_SERIAL_IDENTITY_READ.md) on
the real GD82 with the meter ON found readable Device Information `0x2A25`.
One read succeeded, returned nonempty usable UTF-8 text, and disconnected
cleanly. The privacy-safe result contained no serial. This proves presence
and structural usability in that tested state, **not** repeatability,
power-cycle stability, or uniqueness across meters.

The manual `fora6_connect.probe_serial_stability` action accepts only a
private runtime Bluetooth address and `operation: set_reference | compare`.
Both successful operations reuse Stage 6A1's bounded Home Assistant
connectable resolution, unpaired connection, `0x180A`/`0x2A25` Read-property
check, exactly one characteristic read, and clean disconnect. There is no
custom characteristic operation, FORA command, write, notification,
pairing, RACP, automated retry, polling, discovery matcher, Config Flow,
device registration, or production identity rule. `compare` without a
reference returns `comparison` / `no_reference` without connecting.

## Process-local reference and comparison

The integration holds exactly one private reference byte sequence in
`hass.data[DOMAIN]["serial_stability"]`. This is integration-local runtime
memory; it is not serialized to a config entry, storage, `.storage`, an
entity, diagnostics, or Git. It disappears when Home Assistant restarts.
The holder's representation omits the bytes. A single integration-local
`asyncio.Lock` serializes set and compare across the entire read and update.

`set_reference` replaces the previous value only after a structurally usable
UTF-8 read **and** successful disconnect. A failed, unusable, or cancelled
read preserves the old reference. `compare` reads anew and tests **exact raw
byte equality** with the stored reference. UTF-8 validation and printable
nonpadding classification establish usability only; neither operation
normalizes whitespace, case, punctuation, leading zeroes, or Unicode. A
comparison never overwrites the reference. There is no user-supplied serial.

The result preserves Stage 6A1's privacy-safe structural and lifecycle
booleans, then adds `reference_set`, `reference_available`, and
`serial_matches_reference` (`null` when no comparison completed). It returns
no serial text, bytes, digest, hash, length, prefix, suffix, address, or
recoverable representation. Stable error codes include `no_reference` and
`unusable_serial`; raw exceptions are suppressed. The original
`probe_serial_identity` action keeps its prior result schema and behavior.

## Controlled user-run physical sequence

1. Meter ON: run `set_reference` once; expect `reference_set: true` and
   `reference_available: true`.
2. Without power cycling: run `compare` once; expect
   `serial_matches_reference: true`.
3. Switch the meter OFF, then ON; wait for a connectable advertisement.
   Run `compare` once. A true result supports stability across this tested
   power cycle. A false result is a real mismatch and blocks this identity
   route pending investigation.
4. Optionally restart Home Assistant. `compare` should return `no_reference`;
   then run `set_reference` and `compare` again. This checks process-local
   reference loss and meter-side repeatability without exposing the value.

Share only privacy-safe action responses. Do not publish the runtime address,
serial, raw GATT data, logs containing either, or identifying screenshots.

## Identity conclusion and next gate

Matching reads before and after a power cycle would support: **`0x2A25`
appears stable for this physical meter across the tested conditions.** It
would not prove that every GD82 has a distinct serial. Serial Number String
is intended as a device-specific standard field, but production uniqueness,
duplicate-device handling, and any transformation into a config-entry ID
still require a separately reviewed evidence and policy gate. No Config Flow
or DeviceInfo identifier is enabled here.

**Exact next gate:** user-run controlled Stage 6A1b comparison and sanitized
result review. If repeated and power-cycle comparisons match, review the
uniqueness basis and production identity policy before Config Flow. If they
mismatch, investigate the identity source without registering the meter. If
the serial becomes unreadable or unusable, consider separately authorizing a
bounded `0x2A23` System ID review.
