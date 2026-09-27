# Stage 13A — automatic current-state refresh trigger review

**Status:** Offline architecture review complete; physical advertisement-state
evidence is required before an automatic trigger is implemented. Released
`v1.0.0` remains at `dd26b65ab467381db58ba7a525c6b8eabca8e00a`.
Production behavior remains explicit manual `refresh_current_uric_acid`, for
raw counts two/four only. This review changes no runtime code or protocol.

## Evidence and current boundary

**Repository-confirmed:** `manifest.json` supplies a connectable Bluetooth
discovery matcher. `config_flow.py` accepts a passive candidate, suppresses a
configured address, and performs guarded confirmation only after user review.
Configured-entry setup creates process-local `MeterRuntime` and one manual
`Fora6CurrentRefreshCoordinator`; it registers no Bluetooth event callback.
The action resolves the selected entry without a MAC input. On invocation the
transport calls HA `async_ble_device_from_address(..., connectable=True)`, then
the connector establishes one HA-selected GATT session. The coordinator has a
per-entry lock, rejects overlap, reads only validated counts/slots, commits
state after clean cleanup, and retains the previous value on failure. Unload
disables manual refresh. No scanner is pinned.

**Live-corroborated:** normal manual power-on allowed subscription and the
validated refresh, including two sessions through the Atom Lite proxy. One
immediate post-measurement flashing state allowed a connection but failed at
custom notification subscription before any command. Pressing history arrows
stopped the Bluetooth light. These observations do not identify an
advertisement signature, the exact internal cause, or the readiness of every
post-measurement episode. Visible/advertising is not proof of GATT readiness.

**Current HA/ESPHome guidance:** HA's
[Bluetooth callback API](https://developers.home-assistant.io/docs/core/bluetooth/api/)
offers `async_register_callback` with `BluetoothServiceInfoBleak` and
`BluetoothChange`, an address/connectability matcher, and an unload
unsubscriber. The callback receives changed advertisement data, with cached
history replay by default; `BluetoothCallbackReplay.DISABLED` can skip replay.
HA deduplicates unchanged advertisement fields. The separate per-packet
`async_register_advertisement_callback` can be used briefly for observation,
but fires per scanner and must be unsubscribed promptly. Service/manufacturer
data in service info can be merged across packets, so it must not be assumed
to describe one atomic broadcast. `async_track_unavailable` may lag by up to
five minutes and considers any connectable controller when requested. HA's
`async_scanner_devices_by_address` shows per-scanner reception, while
`async_last_service_info` selects the strongest requested kind; neither alone
proves a later GATT route. The scanner-object interface is read-only and not
stable for long-term integration storage. HA's
[active Bluetooth coordinator guidance](https://developers.home-assistant.io/docs/core/bluetooth/bluetooth_fetching_data/)
can poll on advertisement changes, but cannot make a GD82 advertisement a
validated readiness signal. ESPHome
[proxy guidance](https://esphome.io/components/bluetooth_proxy/) distinguishes
advertisement reception from limited active GATT connection slots. No
per-proxy pinning or scan-parameter change is justified here.

Do not call `async_clear_advertisement_history` after every session merely to
force another event: with an unchanged broadcast it could create a
connect/disconnect loop. A future design must first prove a new episode or
bounded rearm rule. Neither `BluetoothChange` labels nor RSSI changes are
treated as meter-state semantics without physical evidence.

## Trigger candidates

| Candidate | Benefit | Current blocker / risk |
| --- | --- | --- |
| New connectable appearance | Narrow, battery-conscious event | HA may have cached/replayed it; disappearance can lag; post-measurement state may also appear. |
| Advertisement change | Native changed-data callback | No GD82 readiness field identified; RSSI/proxy changes may spuriously fire; unchanged next power-on may be deduplicated. |
| Unavailable → available | Conceptually one episode | HA unavailable can lag up to five minutes and aggregate multiple proxies; short OFF/ON may not reset it. |
| Post-measurement signature | Would target desired user flow | No reproducible signature or subscription-ready evidence; one failing subscription is contrary evidence. |
| Short debounced event | Can coalesce scanner bursts | Delay does not by itself prove readiness; duration must be measured, not guessed. |
| Opt-in automatic mode | Preserves manual fallback and limits rollout | User control cannot solve an unknown trigger or post-measurement readiness state. |

**Recommendation:** retain manual-only v1 behavior until a state-specific
advertisement/transaction correlation is observed. If that evidence identifies
a safe event, prefer a configured-address, connectable, live-only HA callback
with an explicit opt-in options flag, one attempt per verified episode, and
the existing refresh coordinator. Treat callback data as a candidate trigger,
not identity or readiness proof; the transport still validates the configured
MAC and project. If advertisements cannot distinguish normal ON from the
problematic post-measurement state, do not auto-connect on mere visibility.
Test a separate next-normal-power-on trigger only after evidence establishes
episode rearming and acceptable user behavior. Do not add arbitrary sleeps,
retry loops, forced active scans, or protocol changes.

## Privacy-safe physical observation gate

No physical operation was performed in Stage 13A. A separately authorized
observation should collect **structural** HA Bluetooth facts in this order:

1. Note whether the configured GD82 is present while OFF and which HA sources
   see it. Confirm the Atom Lite remains online and active-connection capable.
2. Turn the meter ON normally, without history-arrow use. Observe appearance,
   change and disappearance events and the corresponding light state. A single
   manual refresh may be correlated with that state; HA Bluetooth Connections
   must identify the actual source if route attribution matters.
3. On a later measurement made for normal use, observe the immediate
   post-measurement flashing period without commanding an automatic attempt.
   Do not take a measurement merely to satisfy this gate. If a separate
   manual test is authorized, record only its bounded failure stage and
   cleanup result, not health content.
4. Observe history-arrow mode separately, then automatic power-off if it
   occurs. Do not infer power state merely from absence of a light.
5. Repeat a normal OFF/ON episode to see whether an identical advertisement
   produces a new HA callback. If a proxy changes, note only a sanitized
   source label and whether HA reports one or multiple scanner observations.

For each state record only: whether local name matches, service UUID set
shape, manufacturer/service-data key sets and value lengths (no values),
connectability, sanitized source label, event type, relative appearance/change
and disappearance intervals, and optional bounded subscription success/failure
stage. HA UI may not expose every field. If necessary, a separately reviewed,
short-lived development observer could use the documented per-packet callback
and return those structural facts only; it must not log or persist raw
advertisements, address, manufacturer bytes, measurements, or timestamps.
Because per-packet callbacks fire for each scanner and service-info fields can
be merged, the observer must distinguish packet timing/source from merged
metadata. Keep any raw HA/ESPHome logs, screenshots, MAC, IP, credentials,
health values, and measurement times private and outside Git.

Required comparison: is there a reproducible advertisement/state transition
that distinguishes **normal ON and subscription-ready** from **post-measurement
flashing and possibly subscription-failing**, across repeated episodes and
the actual proxy path? If not, the advertisement-only trigger remains
unjustified. A single successful transaction cannot prove general readiness.

## Future implementation guard design (not implemented)

- One callback registration per loaded entry, cancelled on unload and
  re-established once on reload. Disable cached replay to avoid a startup
  fetch. The callback does no GATT work synchronously and retains no scanner
  object or private advertisement payload.
- Require configured canonical address match, valid candidate shape,
  connectable reachability, Home Assistant running, opt-in enabled, and a
  physically supported state/episode discriminator. HA remains free to choose
  local or proxy transport; the callback's scanner source is not a pinned
  connection route.
- Coalesce advertisements across sources into one entry-wide pending attempt.
  Use the existing per-entry coordinator lock for manual/automatic exclusion.
  Manual refresh remains available; overlap is rejected or scheduled only by
  a separately specified policy, never run concurrently.
- Maintain process-local episode/cooldown state only. One bounded attempt per
  validated episode, no retry loop or periodic wake-up. A failed attempt does
  not clear the previous sensor value and does not immediately rearm on the
  next duplicate advertisement. Determine any debounce/cooldown duration from
  physical timing rather than inventing a constant. HA's lagged unavailable
  event alone cannot be the sole rearm signal.
- On unload cancel pending timers/tasks and unsubscribe the callback; do not
  create a startup refresh on reload or restart. Two configured entries own
  separate locks and trigger state. Multiple proxies for one MAC do not create
  multiple attempts.
- Automatic success may replace the same current-state value, just as manual
  refresh does. A process-local duplicate-write suppression could be assessed
  after trigger evidence, but raw index alone and minute timestamp alone are
  unsafe durable identities. Do not add persistent dedup/history/resume.

Background transient failures should retain the last in-process measurement,
stay debug-level or summarized without health/identifier payloads, and avoid
repairs/notifications for one absent or unready episode. Manual action results
remain the detailed private troubleshooting path. A bounded error counter is
only a future UX candidate; no new entity or diagnostics payload is justified.
Connection-slot exhaustion is a failure, not permission to spin or pin another
proxy.

## Synthetic tests required for implementation

Test live-only callback registration and cancellation; one verified episode
giving one attempt; repeated/unchanged and multi-proxy events giving no storm;
measured debounce/cooldown; HA startup/replay not fetching; manual-vs-auto
overlap in both directions; failure retention and first-ever unavailability;
unload cancellation; reload one registration; two-entry isolation; scanner
roaming; slot/connection/subscription failure with no retry loop; supported
count-two/four behavior; unsupported count and equal-minute ambiguity fail
closed; no private payload in logs/diagnostics. Synthetic tests will validate
the state machine, not physical meter readiness or proxy traversal.

**Exact next gate:** separately authorize a bounded, privacy-safe physical
advertisement-state observation (and, only if the HA UI is insufficient, a
development-only structural observer). Review normal-ON versus post-measurement
readiness and episode rearming before authorizing Stage 13B automatic refresh.
If no reliable distinction emerges, retain manual-only behavior or define one
narrow BLE-state investigation. Stage 8H and other post-v1 features remain
separately gated.
