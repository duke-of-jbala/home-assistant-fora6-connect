# Stage 13A-P2 — one-time advertisement-history re-arm test

**Status: physically complete for the bounded continuous-ON test. Outcome: REARM UNSAFE AS EPISODE SIGNAL.**

## Scope and evidence

This post-v1 development action tests Home Assistant changed-data dispatch on Core 2026.9.4. The prior physical Stage 13A-P1 run produced one changed callback during an intended OFF → ON → OFF → ON sequence. That Core version does not offer the observer's per-packet callback API. The changed callback and Advertisement Monitor exposed different structural views, so neither is a complete radio-packet record.

The manually invoked `fora6_connect.observe_advertisement_rearm` action selects one configured FORA entry. It registers a passive changed-data callback with cached replay disabled. After the **first live callback**, it calls `async_clear_advertisement_history()` for that entry's address **once**, immediately at the callback synchronization point. It then watches until the 60-second bounded window ends. If there is no first callback, it does **not** clear history. The action does not infer physical ON/OFF state. It never opens GATT, requests an active scan, sends a FORA command, changes a sensor, or starts production synchronization. Cancellation/unload removes the callback.

[Home Assistant's Bluetooth API documentation](https://developers.home-assistant.io/docs/core/bluetooth/api/#clearing-cached-advertisement-history) says the cache clear makes the next otherwise identical advertisement eligible for changed-data dispatch. It does not create a packet, establish a new wake episode, or show protocol readiness. Core 2026.9.4 cannot count packet receipt in this test.

## User-run physical procedure

1. Deploy this development build and restart Home Assistant. Leave the GD82 fully OFF. Do not measure or press its history arrows.
2. In Developer Tools → Actions, select `fora6_connect.observe_advertisement_rearm` and the existing FORA entry, then run it. Turn the meter ON normally after the action starts.
3. Keep the meter **continuously ON** until the action returns. Watch the meter state privately. If it switches OFF during the window, mark the same-ON comparison inconclusive. Do not share its address or a screenshot.
4. Report only `first_callback_seen`, `clear_performed`, `changed_callback_count`, `callbacks_after_clear_count`, relative callback/clear times, `callback_cleanup_successful`, `stopped_by_unload`, and any sanitized failure stage/type. Confirm separately whether the meter stayed ON after the clear.
5. If no callback followed the clear while continuously ON, turn the meter OFF and allow a clear OFF interval. Run the existing `fora6_connect.observe_advertisements` action with the same entry, then turn the meter ON normally. Report only whether its **changed-data** callback occurred and its relative time and cleanup result. That existing action performs **no** cache clear. The two actions must not overlap.

The second invocation is a separate bounded OFF → ON observation, not an in-action physical transition marker. The first action performs at most one clear; the second performs none. No fixed OFF interval, debounce, or retry value is inferred from this experiment.

## Interpretation

| Result | Supported interpretation |
| --- | --- |
| A callback follows the clear while the meter remained continuously ON | Cache clear can produce a false “new wake” signal inside one ON episode. It is unsafe as a standalone episode boundary. |
| No same-ON callback, then a later physical OFF → ON causes a changed callback | Bounded positive re-arm evidence. It still does not prove packet-level episode detection or notification readiness. |
| No first callback, meter switches OFF during the first window, or no later OFF → ON callback | Inconclusive on the re-arm mechanism. Silence cannot prove absent packets on Core 2026.9.4. |

Only relative times, bounded structural counts/booleans, and temporary source aliases leave the action. The user must correlate physical state. Do not publish a Bluetooth address, proxy identifier, RSSI, packet payload, health value, measurement time, Home Assistant URL, screenshot, or raw log. A failure returns a sanitized stage and exception type without exception text.

## Project gate

Development started from clean `main` at `64ade3c7667648fefcebd8b3624de570bc895501` (`docs: record bounded GD82 callback observation`), with matching `origin/main`. The implementation checkpoint is `fb1d9278834084786484b5b194a6b1cfd6e6efd1` (`feat: add bounded advertisement re-arm observer`). The stable `v1.0.0` tag remains at `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. This action is development-only; released and current production refresh remain manual-only. Synthetic tests cover callback gating, one clear, cleanup, sanitized failures, and no GATT/sensor path.

## User-run physical result — LIVE-CORROBORATED

On Home Assistant Core 2026.9.4, the user kept the GD82 continuously ON for the full 60-second observation, took no measurement, and pressed no history arrow. The first changed-data callback arrived at relative T+13.2 s. The action performed its single history clear at T+13.2 s. A second changed-data callback arrived at T+57.1 s **before any physical OFF transition**. The action reported two changed callbacks, one after clear, from the same sanitized source; callback cleanup succeeded and unload did not stop the observation. Both callback shapes had two service UUIDs, one manufacturer-data entry, no service data, and connectable true. No address, payload, RSSI, private health value, or measurement time is retained here.

This directly demonstrates that clearing advertisement history can re-dispatch a changed callback **inside one continuous physical ON episode**. A post-clear changed callback is therefore **not** a safe standalone “new wake” boundary. No later OFF → ON comparison was needed to settle this false-rearm criterion. The test does not establish actual packet cadence, notification-subscription readiness, or the meter's internal advertising state. It does not justify production automatic sync.

## Narrowest next architecture gate

Propose a separately authorized **Stage 13A-P3 — bounded genuine-absence/return observation**, initially design and development observation only. Verify the exact Core 2026.9.x behavior of `async_track_unavailable(..., connectable=True)` and `async_address_present(..., connectable=True)` for the configured entry. A bounded, no-clear, no-GATT observation would correlate a user-confirmed continuous ON interval, a real OFF interval long enough for Home Assistant to report unavailability, and a later normal ON interval. Record only relative timing, callback/presence booleans, and temporary source aliases. Test whether a genuinely observed unavailable → present transition is delivered without manually clearing advertisement history, across all visible proxies. [Home Assistant documents](https://developers.home-assistant.io/docs/core/bluetooth/api/#subscribing-to-unavailable-callbacks) that unavailable notification can lag by up to five minutes and that connectable availability aggregates controllers. An unavailable event can also reflect lost scanner coverage, so it is a candidate conservative boundary, not proof of physical power-off; a short OFF → ON may not trigger it at all.

If Home Assistant cannot show a useful absence/return transition on Core 2026.9.4, reassess whether a newer Core per-packet API or a narrow proxy-level observation is necessary. Do not implement Stage 13B, add cache-clearing to production, or introduce a timing constant from this result. The post-measurement notification-readiness question remains separate.

**Exact next gate:** separately authorize Stage 13A-P3 offline API/observer design and bounded physical unavailable → available observation, with no GATT or production automatic sync. Manual refresh remains the only production trigger.
