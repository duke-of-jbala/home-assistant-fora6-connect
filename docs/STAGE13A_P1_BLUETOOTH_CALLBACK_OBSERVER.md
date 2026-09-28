# Stage 13A-P1 — read-only Bluetooth callback observer

**Status: bounded Core 2026.9.4 changed-callback run physically observed;
episode semantics unresolved.** This is
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

## User-run Core 2026.9.4 result

The user completed one 60-second action during an intended normal
OFF → ON → OFF → ON observation. It reported **one** changed-data callback at
session-relative `T+17.7 s`, from one sanitized source alias. Callback
unsubscription succeeded; the action ended by its time bound, not entry
unload. Per-packet support was unavailable. This is **LIVE-CORROBORATED**
callback delivery for one event, not proof that only one advertisement was
received or that the second wake emitted no advertisement. The event's
structural view had two service UUIDs, `connectable: true`, zero manufacturer
entries, zero service-data entries, and no exact `FORA 6 CONNECT` name match.
The Advertisement Monitor previously displayed the FORA name and one
manufacturer entry. These surfaces need not expose the same complete or
merged representation; an absent field in this callback is **not** proof of
absence from a physical advertisement. No address, raw bytes, health value,
or measurement timestamp is recorded here.

Across the intended two wake episodes, the supported changed-data callback
did **not demonstrate reliable re-dispatch for each episode** when data stayed
effectively unchanged. That observation does not identify whether the second
episode's packets were received, deduplicated, missed by scanning, or outside
the effective observation window. A production trigger based solely on this
callback is not justified.

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

### Proposed Stage 13A-P2 — one-time re-arm semantics test

The next smallest physical gate is a separately authorized, development-only
test of `async_clear_advertisement_history()` for the configured address.
Its purpose is to determine whether a **single** clear while the GD82 remains
visibly ON permits another changed-data callback in that same continuous ON
episode, rather than only after a later OFF → ON. It must not connect, issue
FORA commands, refresh the sensor, change integration matcher history, or
install a production callback.

The test needs two clearly marked phases within one bounded observation:

1. Start with the meter OFF, live callback registered with cached replay
   disabled. Turn it ON normally and require an observed first callback;
   otherwise mark the run inconclusive and do not clear anything.
2. While the meter **remains ON** and before any OFF transition, invoke one
   explicit user-controlled re-arm. Record its relative time and call the
   public `async_clear_advertisement_history()` **once**. Keep observing
   without an automatic re-arm or callback-triggered clear.
3. Separately mark a later normal OFF → ON and observe whether a callback
   follows. Stop and unregister cleanly; return only phase-relative callback
   counts/times and boolean cleanup status. The user reports meter-state
   transitions without addresses, packet bytes, or health information.

A callback after the clear **while still ON** proves that re-arming can
re-dispatch within one continuous episode in this state; production
one-attempt-per-wake logic must not treat such a callback as a new wake. If
there is no callback until OFF → ON, that is only bounded evidence: Core
2026.9.4 cannot confirm whether advertisements arrived during the ON phase.
If no callback follows either phase, the run is inconclusive. No timing or
cooldown constant for production should be chosen from this one experiment.
Stage 13A-P2 is proposed only; no cache clear is implemented or run here.

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

The procedure above documents the completed Stage 13A-P1 run. The **exact
next gate** is separate authorization for Stage 13A-P2's bounded one-time
re-arm test. Do not implement Stage 13B automatic sync from one changed-data
callback or from the Advertisement Monitor view.
