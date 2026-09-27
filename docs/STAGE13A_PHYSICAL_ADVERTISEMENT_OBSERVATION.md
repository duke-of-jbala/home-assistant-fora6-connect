# Stage 13A-P — bounded GD82 advertisement-state observation

**Gate status: partial user-run physical evidence; remaining states pending.** The starting
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

The OFF row below uses the user-supplied detail-view observation. Other rows
remain pending; `pending` means **not observed**, not an inferred result.

| State | Fresh event | Local name | Service UUID shape | Manufacturer shape | Service-data shape | Connectable | Source behavior | Relative appearance/disappearance | Distinct from normal ON? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fully OFF | No live update seen; cached row | FORA 6 CONNECT | Includes standard Glucose; full set not reported | One entry; key/length not reported | Absent | Not shown | Previous proxy source retained | `Updated` age increased; row retained | Unresolved |
| Normal manual ON, first | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Reference |
| Post-measurement flashing | Pending naturally appropriate session | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Unresolved |
| History-arrow mode | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Unresolved |
| Normal power-off | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Unresolved |
| Second OFF → ON | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Unresolved |

## Critical comparisons and current limits

1. **Normal ON vs post-measurement:** unresolved. The earlier post-measurement
   subscription failure is live connection evidence, not an advertisement
   comparison.
2. **Normal ON vs history mode:** unresolved. The prior observation that
   history-arrow use stopped the Bluetooth light does not establish a packet
   change or disappearance.
3. **OFF → ON fresh episode:** unresolved. HA callback replay, duplicate
   suppression, and delayed unavailable tracking cannot be inferred from a
   retained monitor row.
4. **Multi-proxy deduplication:** unresolved for this meter episode. A monitor
   may combine sources while a per-packet callback can fire once per scanner.
5. **Transaction readiness:** not inferable from connectability alone; one
   flashing state connected but failed notification subscription.
6. **One bounded attempt per episode:** not yet justified. It needs a
   repeatable episode boundary and an explicit acceptance of any residual
   pre-connection readiness uncertainty.

No debounce or cooldown value is chosen without actual observed timing. The
current manual action remains the validated fallback and no production
callback, retry, polling, or connection is added by this record.

## Observer decision and next gate

The HA detail view supplies structural information, so an observer is **not
yet justified**. Continue with that UI first. It still may not reveal a
connectable flag, exact live callback delivery, or every per-proxy packet. If
those gaps remain material after the state comparison, the exact possible
tracked change is a development-only, configured-entry-targeted action in the
existing probe convention: an explicitly invoked, bounded registration of
HA's per-packet advertisement callback for the configured address, always
cancelled afterward. A live changed-advertisement callback with cached replay
disabled could be compared. Return only sanitized shape, per-invocation
`Proxy A/B` aliases, relative event timing, and counts, never address, raw
payload, RSSI value, health data, or real clock time. No GATT connection,
FORA command, persistent state, startup registration, or production refresh.
Tests would cover cancellation, time/memory bounds, privacy, multiple
sources, and no connection/protocol calls. This observer is **not implemented**
or approved by the UI observation alone.

**Current category: PARTIAL EVIDENCE — physical observations pending.** The
exact next gate is user-run sanitized detail-view observation of normal ON,
history mode, power-off, and a repeated OFF/ON. Decide about any observer
only after those results. A
naturally occurring post-measurement state remains pending. Stage 13B
automatic synchronization is not authorized or implemented.
