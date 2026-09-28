# Stage 13A-P3 — Bluetooth absence/return assessment

**Outcome: ABSENCE/RETURN UNSUITABLE as the primary automatic GD82 trigger on Home Assistant Core 2026.9.4.** This is an offline, source-derived architecture conclusion. No Stage 13A-P3 physical observation was run, no observer was added, and production remains manual-only. It does not rule out a separately justified, delayed reachability feature in another product scope.

## Baseline and evidence boundary

The assessment began on clean `main` at `6d223aa6999c53764dacad8f3991357f5263b123` (`docs: close Stage 13A-P2 re-arm validation`), with matching `origin/main`; stable `v1.0.0` still resolves to `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. Stage 13A-P1 physically showed one changed callback during intended repeated wakes on Core 2026.9.4. Stage 13A-P2 physically showed another changed callback after one cache clear while the GD82 stayed continuously ON. Thus neither ordinary changed dispatch nor cache clear alone establishes each physical episode.

The sources for this review are the [Core 2026.9.4 Bluetooth API](https://github.com/home-assistant/core/blob/2026.9.4/homeassistant/components/bluetooth/api.py), [Core Bluetooth callback manager](https://github.com/home-assistant/core/blob/2026.9.4/homeassistant/components/bluetooth/manager.py), and Core's pinned `habluetooth==6.26.11` ([manifest](https://github.com/home-assistant/core/blob/2026.9.4/homeassistant/components/bluetooth/manifest.json), [manager](https://github.com/Bluetooth-Devices/habluetooth/blob/v6.26.11/src/habluetooth/manager.py), [scanner](https://github.com/Bluetooth-Devices/habluetooth/blob/v6.26.11/src/habluetooth/base_scanner.py), [constants](https://github.com/Bluetooth-Devices/habluetooth/blob/v6.26.11/src/habluetooth/const.py)). Current [Home Assistant Bluetooth guidance](https://developers.home-assistant.io/docs/core/bluetooth/api/#subscribing-to-unavailable-callbacks) agrees that unavailable callbacks can lag and considers all connectable controllers. These are source facts, not a user-run GD82 timing result.

## Exact Core 2026.9.4 behavior

- `bluetooth.async_track_unavailable(hass, callback, address, connectable=True)` registers **by address**, not by scanner. The pinned manager collects the discovered addresses across all connectable scanners and removes the address from connectable history only when none still report it. One proxy losing sight or a source switch alone does not necessarily mark it unavailable.
- The pinned remote scanner retains its last device entry until its age exceeds **195 seconds**, checked on a **30-second** scanner schedule. The manager checks aggregate unavailable state every **300 seconds**. These phases are not synchronized; from the last received advertisement, a normal stale-entry path may take several minutes and can approach roughly **195 + 30 + 300 = 525 seconds** before the callback. This is a bound inferred from these schedules, not a measured GD82 delay or a guarantee across scanner teardown/restart paths. Another proxy's later observation postpones it further.
- `bluetooth.async_address_present(..., connectable=True)` queries the manager's current connectable-history entry. It can remain true after the physical meter is OFF until expiry. It is a current cache/presence query, not an OFF event or a dedicated return callback.
- There is **no separate public present/available transition callback** in the reviewed API. A registered changed-data callback is the return path. After the manager has actually removed the address from connectable history, its next connectable advertisement bypasses the identical-data short circuit when `old_connectable_service_info` is absent; Core then dispatches the matching advertisement callback. This is **STATIC-CONFIRMED code behavior** for a true manager-unavailable transition, not physical GD82 return validation. No explicit advertisement-history clear is needed in that branch.
- Cached last-seen information and the Advertisement Monitor's `Updated` field are not live physical state. Core may load scanner/history data during setup. The earlier cross-browser stale-view observation makes frontend timestamps unsuitable as the primary evidence source.

## Multi-proxy and physical-state limits

| Situation | Manager interpretation and risk |
| --- | --- |
| One proxy loses GD82; another still sees it | Aggregate connectable presence remains. A source change is not an OFF/ON boundary. |
| One proxy restarts or briefly loses network; another still sees GD82 | Aggregate presence can remain. Source alias or RSSI changes do not prove meter state. |
| All proxies stop seeing GD82 while it is still ON | After stale expiry, HA may report unavailable. This is a **coverage** loss, indistinguishable through this API from physical OFF. |
| Both proxies restart, network fails, or Core restarts | Scanner and cached-history lifecycles change independently of the meter. A later observation cannot be called a physical wake without external evidence. |
| GD82 OFF → ON before stale expiry | HA may remain continuously present; no unavailable boundary is guaranteed, so the new ON can remain invisible to changed-data callbacks if its data is unchanged. |

An unavailable → return state machine could theoretically allow one attempt after a **long, genuine HA reachability gap**. It cannot identify each physical GD82 power cycle, especially short cycles. It also cannot distinguish meter OFF from loss of all proxy coverage. A false reachability re-arm could lead to a transaction against a still-ON or unsuitable meter state. An opt-in flag, cooldown, or process-local fingerprint does not repair the missing physical boundary. The delayed callback would be poor UX for a user expecting current-state refresh after normal meter use; scanner loss and Core restart add false-boundary risks. Advertisement visibility still does not prove notification-subscription readiness, as the earlier post-measurement failure showed.

## Observer decision and next gate

No development presence observer was added. The exact pinned source already establishes the minutes-scale latency, aggregate scanner behavior, return-dispatch condition, and inability to prove physical OFF. A user-run ON → long OFF → ON observation could measure one deployment's latency but cannot make this mechanism a prompt or physical-episode-safe trigger. No physical Stage 13A-P3 timing, return callback, or source-switch result is claimed.

The narrowest realistic alternative is to retain the v1 manual action (which may be placed on a dashboard) while separately assessing **post-measurement and normal-ON notification readiness** during naturally occurring meter use. A future Stage 13A-P4 should first define a privacy-safe, bounded state-correlation procedure and ask whether any supported BLE signal identifies a transaction-ready session without cache clearing or arbitrary retry. It must not ask for a new medical measurement solely for development, add production connections, or start Stage 13B. If no such signal is found, retain manual-only operation.

**Exact next gate:** separately authorize Stage 13A-P4 offline design of a bounded, naturally occurring meter-state/readiness observation. Stage 13B production automatic sync remains unauthorized.
