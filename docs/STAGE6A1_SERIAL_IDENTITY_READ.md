# Stage 6A1 — bounded Device Information serial identity read

**State:** Development-only action implemented and hardware-free tested. No
physical read has yet been run; stable per-meter identity remains unresolved.

## Evidence and exact scope

[Stage 6A](STAGE6A_DISCOVERY_IDENTITY_POLICY.md) records the real Stage 1B
GATT metadata: Device Information service `0x180A` contained readable Serial
Number String `0x2A25`. Its value was never read. This standard characteristic
is a plausible meter-specific identifier, not yet proof of one. The action
`fora6_connect.probe_serial_identity` accepts the privately supplied runtime
Bluetooth address, resolves a connectable device through Home Assistant,
connects with the existing HA/Bleak connector policy (`max_attempts=2`,
`pair=False`), locates service `0x180A` and characteristic `0x2A25`, verifies
the Read property, reads that characteristic **exactly once**, and disconnects.
All connection, read, and disconnect waits are bounded. Connection cancellation
owns and disconnects any client returned while cancellation is processed.

There is no custom `0x1524` write, FORA command, notification subscription,
pairing, System ID `0x2A23` read, record retrieval, or background retry. The
development action is manually invoked and adds no discovery matcher, Config
Flow, config entry, device-registry identifier, or production identity rule.

## Privacy and result semantics

The serial is held only while classifying one read. It is never returned,
logged, hashed, stored in an entry, or saved in a module-wide cache. The
address is used only to locate a device and is absent from errors/results.
No token or serial length is returned. The action reports these safe fields:

| Field | Meaning |
| --- | --- |
| `device_found`, `connectable_device_resolved` | HA supplied a connectable runtime BLEDevice. |
| `connection_successful` | The returned client reported connected. |
| `device_information_service_found`, `serial_characteristic_found`, `serial_readable` | Required GATT metadata was present. |
| `serial_read_successful` | One read returned bytes without an exception. |
| `serial_value_present` | Returned byte sequence was not empty. |
| `serial_value_utf8_valid` | Bytes decoded as UTF-8. |
| `serial_value_nonempty`, `serial_value_usable` | Decoded text contained printable non-padding characters and no control characters. These classify structure only, not uniqueness. |
| `disconnected_cleanly` | Bounded disconnect succeeded. |
| `error_stage`, `error_code`, `cleanup_errors` | Stable privacy-safe failure categories; no raw exception text. |

An empty, padding-only, invalid UTF-8, or control-character value is unusable
under this conservative text rule. A successful and usable read still does
**not** prove a stable or meter-specific serial. Repeating this action gives
structural outcomes only; it cannot compare the private values. A later
separately authorized, privacy-safe in-memory equality design or other private
comparison evidence is required to establish stability across a power cycle,
HA restart, and preferably more than one physical meter. No persistent ID
should be selected from the current result alone.

## Controlled user-run test after review

With the meter ON and its address copied privately from HA Advertisement
Monitor, invoke `fora6_connect.probe_serial_identity` once and retain only
the sanitized response. After an OFF/ON cycle, optionally after an HA restart,
invoke it once again. Do not share the address, serial, logs containing either,
or screenshots that expose them. Compare only structural status at this gate;
equality and cross-meter uniqueness remain unresolved. If `0x2A25` is absent,
unreadable, empty, or otherwise unusable, stop. A bounded `0x2A23` System ID
read would require separate Stage 6A2 authorization.

**Exact next gate:** user-run controlled Stage 6A1 read and sanitized result
review. If structurally usable, separately design/authorize private stability
comparison before persistent Config Flow or device registration. If unusable,
consider a separately authorized Stage 6A2 System ID evidence review.
