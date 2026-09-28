# Stage 13A-P2 — one-time advertisement-history re-arm test

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

Development starts from clean `main` at `64ade3c7667648fefcebd8b3624de570bc895501` (`docs: record bounded GD82 callback observation`), with matching `origin/main`. The stable `v1.0.0` tag remains at `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. This action is development-only; released and current production refresh remain manual-only. Synthetic tests cover callback gating, one clear, cleanup, sanitized failures, and no GATT/sensor path. **Physical re-arm behavior is pending the user's run.** Do not implement Stage 13B from synthetic evidence.

**Exact next gate:** user-run Stage 13A-P2 one-clear observation and, if needed, separate later OFF → ON changed-callback observation; classify the result before any new automatic-sync authorization.
