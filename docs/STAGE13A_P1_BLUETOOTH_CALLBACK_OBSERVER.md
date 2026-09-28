# Stage 13A-P1 — read-only Bluetooth callback observer

**Status: development action implemented; physical evidence pending.** This is
post-`v1.0.0` development. The stable release and production manual refresh
are unchanged. The starting clean `main` checkpoint was
`84f6362d0cabca5e9e45905e6fffe75a9b69556d` (`docs: assess GD82
advertisement callback observation`), with `origin/main` matching and the
released tag still resolving to `dd26b65ab467381db58ba7a525c6b8eabca8e00a`.

## Core 2026.9.x compatibility correction

The user's first physical action invocation failed immediately with a generic
`ServiceValidationError`; no callback evidence was collected. The action
wrapper had suppressed the underlying exception. An audit of the **Home
Assistant Core 2026.9.4 [Bluetooth exports](https://github.com/home-assistant/core/blob/2026.9.4/homeassistant/components/bluetooth/__init__.py)
and [API implementation](https://github.com/home-assistant/core/blob/2026.9.4/homeassistant/components/bluetooth/api.py)**, rather than only the current
developer documentation, found that `bluetooth.async_register_callback`,
`BluetoothCallbackReplay.DISABLED`, and
`async_clear_advertisement_history` are exported, but
`async_register_advertisement_callback` is **not**. The first registration
expression therefore raises `AttributeError: module
'homeassistant.components.bluetooth' has no attribute
'async_register_advertisement_callback'`. This is source-deduced from the
exact first call; the erased Home Assistant traceback cannot be recovered.

The compatibility fix feature-detects the public per-advertisement callback.
When unavailable, it registers the released changed-data callback only,
reports `packet_callback_supported: false`, and returns `null` rather than a
misleading zero for packet counts and samples. The live changed-data callback
still uses passive matching and disabled cache replay. On an HA version with
the per-advertisement API, both callbacks are compared as originally designed.
Registration or wait failures now surface a sanitized action error containing
only `stage` and exception `type`; private exception messages are never
returned or logged. No deprecated shared-scanner detection callback or
private manager API was added. On Core 2026.9.4, a changed-only result cannot
settle whether identical packets were received; that limitation must remain
explicit when reviewing the physical rerun.

## Reason and evidence boundary

After Home Assistant Core 2026.9.4 and an HAOS restart, the first normal GD82
ON appeared in Advertisement Monitor almost immediately. Repeated OFF → ON
cycles did not reset `Updated`; navigating away/back or hard-refreshing could
show a recent observation. Chrome showed the same behavior. These are
user-supplied physical UI observations. They do not establish whether the
backend received each packet, whether unchanged advertisements were
deduplicated, or whether only the view failed to refresh. A Home Assistant
regression remains possible, not demonstrated.

The [current Home Assistant Bluetooth API](https://developers.home-assistant.io/docs/core/bluetooth/api/)
provides two useful mechanisms:

- `async_register_callback` dispatches when advertisement data changes. Its
  default may replay cached data; this observer sets
  `BluetoothCallbackReplay.DISABLED` and uses a passive, address-scoped
  matcher. It does not request an active scan window.
- Where present, `async_register_advertisement_callback` delivers repeated advertisements
  for one address, including identical ones, once per scanner. Thus packet
  callback counts can differ from changed-data callback counts. The API may
  merge name, service UUID, manufacturer data, and service data across packets;
  those fields are **not** an exact per-packet snapshot. Raw bytes are neither
  read from the callback object nor returned.

The action is `fora6_connect.observe_advertisements`. It is manual and
development-only. Select the existing configured FORA entry; no Bluetooth
address is entered. One invocation observes for at most 60 seconds. It
registers no startup listener and performs no BLE connection, GATT read or
write, FORA command, notification subscription, active scan request,
advertisement-cache mutation, or sensor refresh. Unload ends an active
observation. An overlapping observation for the same entry is rejected.

## Privacy-safe result

The result contains packet/changed callback counts where supported; counts by ephemeral
source aliases; up to 32 event samples for each callback type with source
alias and elapsed time rounded to tenths of a second; sampled packet shapes;
first and last structural shapes; a shape-change count; whether unload ended
the session; and whether callback unsubscription completed. Counts and source aliases are
bounded. Structural shape consists only of a public-name equality flag,
service UUID count, manufacturer-entry count, service-data-entry count, and
connectable status as supplied by HA. It exposes no address, scanner
identifier, raw payload, manufacturer bytes, RSSI value, health value,
measurement time, absolute timestamp, or hash. Do not publish a private
action response without reviewing it.

**Interpretation:** packet callbacks on repeated ON cycles with few or no
changed-data callbacks would establish delivery despite changed-data
deduplication. A recent monitor row without packet callbacks during the
observer window does not prove the meter was silent: scanning/source coverage
and session timing must be considered. Multiple source aliases represent
scanner delivery, not multiple meters or multiple GATT sessions. Neither
callback proves notification subscription or current-state transaction
readiness.

On Core 2026.9.4, `packet_callback_supported: false` is expected; its packet
fields are `null`, not evidence of zero packets. Only changed-data delivery
can be physically tested there through the supported callback API.

## `async_clear_advertisement_history()` assessment

Home Assistant documents this as clearing the cached advertisement data for
one address, so the **next** otherwise identical advertisement can be treated
as changed and delivered to `async_register_callback`. It does not itself
cause a new packet, does not clear integration matcher history, and does not
establish a new physical OFF → ON episode. Calling it after a future completed
GATT transaction may be relevant to detecting the next wake-up, but using it
inside this observer would disturb the comparison and could make repeated
identical packets look like new episodes. **Stage 13A-P1 never calls it.**
Any production use needs separate evidence and guards against repeated
callback-triggered connections.

## User-run physical procedure

1. Deploy this post-v1 development build and restart Home Assistant. Confirm
   the existing FORA entry, device, and single uric-acid entity remain.
2. Leave the meter OFF. In Developer Tools → Actions select
   `fora6_connect.observe_advertisements` and the configured FORA entry.
   Start the action. During its 60-second window, turn the meter ON normally,
   allow it to turn OFF, then turn it ON once more if timing permits. Do not
   take a new measurement solely for the probe; do not press history arrows
   during this first comparison.
3. Report only sanitized callback counts, relative sample times, structural
   shape changes, and Source A/B alias counts. Note privately the approximate
   sequence of ON/OFF events relative to action start; no wall-clock time,
   address, RSSI, payload, or health data is needed.
4. A separate safe history-arrow observation may be run later. Observe
   post-measurement flashing only during naturally occurring meter use.

No callback result has yet been observed on the real meter. The exact next
gate is user-run Stage 13A-P1 physical callback observation and evidence
review. Do not authorize or implement Stage 13B automatic sync from synthetic
tests alone.
