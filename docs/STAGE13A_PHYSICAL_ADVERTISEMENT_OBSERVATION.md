# Stage 13A-P — bounded GD82 advertisement-state observation

**Gate status: partial user-run physical evidence; callback-level observation needed.** The starting
checkpoint is clean `main` at `c858338481031e9c0090705666af664b72e5260d`
(`docs: review automatic refresh trigger architecture`); `origin/main`
matched. The released `v1.0.0` tag still resolves to
`dd26b65ab467381db58ba7a525c6b8eabca8e00a`. Production remains
manual-only. This document is an observation plan and evidence table, not an
automatic-sync implementation or claim that the states were observed.

## Evidence method and UI boundary

Use Home Assistant **Settings → Connectivity → Bluetooth → Advertisements**
(Advertisement Monitor), with its **Adapters** and **Connections** views for
source/capability context. The [current HA Bluetooth documentation](https://www.home-assistant.io/integrations/bluetooth/)
describes those views. The monitor can show devices currently advertising,
but a visible row or scanner edge does not prove a fresh callback, exact
packet contents, transaction readiness, or the eventual GATT route. Observe
which fields the installed HA version actually shows; mark missing fields
`not shown` rather than guessing. Do not copy raw advertisement text or an
unredacted screenshot into Git. The [HA callback API](https://developers.home-assistant.io/docs/core/bluetooth/api/)
has separate changed-data and per-packet callbacks if a later development-only
observer becomes necessary; those are not installed by this gate.

**User-supplied UI finding:** the overview first appeared to show only a basic
row, but **clicking that row exposes structural details**. In the fully OFF
state, the retained row's `Updated` age continued increasing; this is cached
last-seen data, not evidence of a live OFF advertisement. The displayed name
was the public `FORA 6 CONNECT` label; one manufacturer-data entry and a
service UUID set including standard Glucose were shown, with no service data.
The source and RSSI were retained from the earlier observation. This UI did
not explicitly show connectability. The raw-advertisement field was available
but neither shared nor copied. No private address, RSSI number, payload, or
measurement was supplied. Manufacturer key/length and other UUIDs remain
unreported, not absent.

**User-supplied observation-quality caveat:** on the first normal-ON attempt,
the FORA Advertisement Monitor row did **not** update, although the user had
previously seen it update. After an HAOS restart, the Bluetooth view resumed
updating. This failed UI refresh is **inconclusive about the meter's radio**;
it may reflect cached/stale UI or HA Bluetooth state. It is not evidence that
the GD82 failed to advertise. A new controlled OFF → ON comparison after the
restart was then performed. After updating to Home Assistant Core 2026.9.4 and
restarting HAOS, the first normal power-on appeared in the monitor almost
immediately. Subsequent normal OFF → ON cycles did not reset its `Updated`
time. The displayed name and shape remained stable: two service UUIDs, one
manufacturer-data entry, no service data, `connectable: true`, and the same
proxy source. Neither the second UUID nor private payload was reported.
The UI cannot distinguish absent packets, Home Assistant deduplication, and
a stale frontend/monitor row. The recent Core update makes a regression
possible, but **no regression is established**. Monitor liveness cannot be
assumed for a future episode.

The user has at least two Atom Lite proxies. Give them private source aliases
`Proxy A` and `Proxy B`; keep their actual addresses and deployment details
outside Git. Do not disable a proxy merely to simplify this observation.
No GATT connection or FORA command is required for the advertisement study.

## Controlled observation procedure

1. With the GD82 fully **OFF**, open the advertisement view and note whether
   a current row remains, whether it is explicitly live/cached, and relative
   time until disappearance. Do not equate a retained row with a live packet.
2. Power **ON normally** without touching history arrows. Before a manual
   refresh, note first appearance/change, available structural fields,
   connectability, source alias, and relative timing. Repeat after a clear OFF
   interval to test whether HA surfaces another fresh event.
3. In a safe non-measurement state, enter **history-arrow mode**. Note whether
   the row disappears, changes structure or source, or loses connectability.
   Do not send protocol commands in that mode.
4. Let the meter turn **OFF normally** if possible. Record only relative
   disappearance timing. A missing UI update is `unknown`, not immediate
   disappearance.
5. At a later measurement taken for ordinary use, observe the immediate and
   later **post-measurement flashing** period. Do not take a new health
   measurement solely for this gate. If no such occasion occurs, keep this
   state pending. Do not automatically connect based on flashing or visibility.
6. Throughout, note whether both proxies show the same episode separately,
   whether the integration-level monitor appears to merge them, and whether a
   source/RSSI switch causes an extra visible change. Source observations are
   not proof that a later GATT connection used that source.

Share only a sanitized structural summary: local name or `not shown`, service
UUID set/shape, manufacturer company/key IDs and data lengths (no bytes),
service-data UUID keys and lengths, connectable `yes/no/unknown`, live/cached
indicator if actually shown, `Proxy A/B` source behavior, relative times such
as `T+3 s`, and appearance/change/disappearance labels only when HA shows or
the observer directly establishes them. Do not share the meter MAC, health
value, measurement time, private IP/HA URL, proxy address, credentials,
screenshot, raw log, or payload bytes.

## Sanitized physical evidence table

The OFF row uses the earlier detail-view observation. The two later ON rows
use the post-update observation. `Pending` means **not observed**, not an
inferred result. No packet receipt or callback was directly observed.

| State | Fresh event | Local name | Service UUID shape | Manufacturer shape | Service-data shape | Connectable | Source behavior | Relative appearance/disappearance | Distinct from normal ON? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fully OFF | No live update seen; cached row | FORA 6 CONNECT | Includes standard Glucose; full set not reported | One entry; key/length not reported | Absent | Not shown | Previous proxy source retained | `Updated` age increased; row retained | Unresolved |
| Normal manual ON, first attempt | Inconclusive: monitor did not update; HAOS restart restored view updates | Pending | Pending | Pending | Pending | Not shown before restart | Pending | No reliable live timing | Reference unresolved |
| Normal manual ON after HAOS restart | First ON appeared in monitor; callback/packet unknown | FORA 6 CONNECT | Two UUIDs; second not reported | One entry; key/length not reported | Absent | Yes, as displayed | Same proxy source displayed | Almost immediate UI appearance; no measured interval | Reference state, UI only |
| Post-measurement flashing | Pending naturally appropriate session | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Unresolved |
| History-arrow mode | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Unresolved |
| Normal power-off | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Unresolved |
| Repeated normal OFF → ON after restart | `Updated` did not reset; packet/callback unknown | Unchanged | Two UUIDs displayed, unchanged | One entry displayed, unchanged | Absent | Yes, as displayed | Same proxy source displayed | No new UI update; actual appearance/disappearance unknown | No structural UI difference shown |

## Critical comparisons and current limits

1. **Normal ON vs post-measurement:** unresolved. The later normal-ON view is
   a useful reference, but no post-measurement advertisement was captured.
   The earlier post-measurement subscription failure is live connection
   evidence, not an advertisement comparison.
2. **Normal ON vs history mode:** unresolved. The prior observation that
   history-arrow use stopped the Bluetooth light does not establish a packet
   change or disappearance.
3. **OFF → ON fresh episode:** the first ON after restart reached the UI almost
   immediately, but subsequent OFF → ON cycles did not refresh `Updated`.
   This does **not** establish whether packets reached Home Assistant or a
   live callback. The monitor cannot establish an episode boundary.
4. **Multi-proxy deduplication:** unresolved. The same proxy source was shown
   throughout this UI observation; that does not exclude packets from the
   other proxy or show callback-level deduplication.
5. **Transaction readiness:** not inferable from connectability alone; one
   flashing state connected but failed notification subscription.
6. **One bounded attempt per episode:** not yet justified. It needs a
   repeatable episode boundary and an explicit acceptance of any residual
   pre-connection readiness uncertainty.

No debounce or cooldown value is chosen without actual observed timing. The
current manual action remains the validated fallback and no production
callback, retry, polling, or connection is added by this record.

## Observer decision and next gate

The repeated unchanged `Updated` time makes the UI insufficient to decide
whether Home Assistant receives a new episode. The smallest next gate is
**Stage 13A-P1: a separately authorized, development-only Bluetooth callback
observer**. The [current Home Assistant Bluetooth API](https://developers.home-assistant.io/docs/core/bluetooth/api/)
documents the key distinction: `async_register_callback` reports changed
advertisement data and can replay cache unless `BluetoothCallbackReplay.DISABLED`
is selected; `async_register_advertisement_callback` reports every delivered
advertisement for one address, including unchanged packets, once per scanner.
Its non-raw advertisement fields can be merged across packets. These two
callbacks, observed together, can distinguish packet delivery from changed-data
dispatch without relying on the monitor's `Updated` field. The packet callback
still only proves delivery through Home Assistant, not GATT readiness.

Use the configured entry's private address only as an in-memory callback
filter. Explicitly start one bounded session; do not register at startup.
Observe an OFF → normal ON → OFF → normal ON sequence, with safe history mode
separately and post-measurement only during natural use. Report bounded
packet and changed-callback counts, session-relative monotonic timing,
structural field shapes, and per-session `Proxy A/B` aliases. Do not return
addresses, source identifiers, payloads, hashes, RSSI values, health data,
wall-clock times, or logs. Cap events and memory; cancel both subscriptions on
normal completion, failure, cancellation, and unload. No GATT connection,
write, FORA command, active scan request, cache clearing, production refresh,
or persistent state. Tests should prove these boundaries and callback cleanup.
No timing constant for a production trigger is selected. The observer is
**not implemented in this gate**.

**Current category: PARTIAL EVIDENCE.** The exact next gate is separate
authorization for Stage 13A-P1, then user-run sanitized callback observation.
Post-measurement advertising and history-mode behavior remain pending. Stage
13B automatic synchronization is not authorized or implemented.
