# Stage 13A-P4 — bounded transaction-readiness observation

**Status:** development-only probe implemented and synthetically validated; physical comparison pending. Production remains explicit manual refresh only. Stable `v1.0.0` remains at `dd26b65ab467381db58ba7a525c6b8eabca8e00a`.

## Why test subscription readiness

[Stage 13A-P1](STAGE13A_P1_BLUETOOTH_CALLBACK_OBSERVER.md) found that Core 2026.9.4 changed-data callbacks did not demonstrate a new event for each intended physical wake. [Stage 13A-P2](STAGE13A_P2_ADVERTISEMENT_REARM_TEST.md) found a changed callback after one history clear during the **same** continuous ON episode. [Stage 13A-P3](STAGE13A_P3_ABSENCE_RETURN_ASSESSMENT.md) found that Home Assistant's aggregate unavailable transition is delayed and cannot prove the meter was physically OFF. None supplies a safe automatic trigger.

The existing validated current-state refresh resolves a Home Assistant-selected connectable device, connects, locates the custom service/characteristic, subscribes to notifications, then sends wake and history commands. A prior real post-measurement flashing state connected but failed at custom notification subscription; normal manual ON has repeatedly supported subscription and the full refresh, including through an Atom Lite ESPHome proxy. This makes successful subscription to the **existing custom characteristic** the narrowest useful transaction-prerequisite discriminator for a bounded physical comparison. One success or failure does not prove all future states.

## Development action and privacy

`fora6_connect.probe_transaction_readiness` selects the existing configured FORA entry; it accepts no MAC, index, count, selector, or proxy pin. It reuses `Fora6BluetoothTransport` with a probe-only `connect_max_attempts=1`; the validated manual refresh keeps its default connection behavior. One invocation resolves the connectable BLE device once, attempts one connection, checks the already known custom service/characteristic and its properties, attempts one notification subscription, then unsubscribes and disconnects. The shared per-entry GATT lock prevents overlap with manual refresh; unload cancels the probe and its bounded transport cleanup runs. Home Assistant remains free to choose a local adapter or proxy.

No FORA application command, characteristic write/read, measurement read, sensor update, cache clear, active-scan request, retry, arbitrary sleep, automatic callback, or persistent readiness state is added. An unsolicited notification is discarded by the shared transport; no payload, digest, length, or content is returned or logged.

The private action response contains only booleans for resolution, connection, custom service/characteristic, subscription, and cleanup; stable failure stage/code or sanitized exception type; and bounded cleanup error codes. It contains no address, proxy identifier, RSSI, health value, measurement time, raw frame, private URL, or upstream exception message. The original failure stage remains when cleanup also fails. A successful subscription with failed unsubscribe/disconnect is reported as a cleanup failure, not a fully successful probe. No source alias is needed because the action makes one HA-selected attempt; Home Assistant's Bluetooth Connections view can separately establish route if necessary.

## User-run physical validation

### Control: normal manual ON

1. Deploy this development build and restart Home Assistant. Leave the GD82 OFF initially.
2. Turn the meter ON normally. Do not take a measurement or press the history arrows.
3. Run `fora6_connect.probe_transaction_readiness` once against the existing config entry in Developer Tools → Actions.
4. Share only the sanitized operational response: resolution/connection/service/characteristic/subscription booleans, cleanup result, and failure stage/code or exception type. Confirm the FORA connection disappears after completion if visible in Bluetooth Connections. Do not share a screenshot, address, health reading, or measurement time.

Expected from earlier manual refreshes, but **not yet validated for this new probe**: connection and custom notification subscription succeed with clean cleanup. If the control fails, investigate that specific stage before interpreting a post-measurement run.

### Comparison: naturally occurring post-measurement flashing

Only when the user takes a measurement for normal use, prepare the action if convenient, complete the measurement normally, and run the same probe **once** during the immediate Bluetooth-flashing state after strip ejection. Do not press history arrows. The user may note privately an approximate elapsed delay from measurement completion to probe start (for example, relative T+ seconds), without recording actual clock time, value, or meter-local measurement timestamp. Share only the sanitized response and relative delay. If no natural measurement occurs, this comparison remains **pending**. Do not take an unnecessary measurement for development.

If the post-measurement subscription fails, a later separate normal manual-ON run may serve as a control; do not repeatedly probe. The action sends no FORA command in either state.

## Interpretation and next gate

| Physical comparison | Supported conclusion |
| --- | --- |
| Normal ON subscribes; post-measurement connects but subscription fails | Bounded live support that custom-notification subscription distinguishes these two observed states. It still supplies **no automatic trigger**. |
| Both subscribe | The prior post-measurement failure was not reproduced; subscription alone does not distinguish the sampled states. |
| Both fail | Probe/environment inconsistency needs a narrowly scoped diagnosis against the validated manual path. |
| Natural post-measurement test unavailable | Keep P4 physical comparison pending; do not infer it from the normal-ON control. |

Even if subscription discriminates these states, **readiness is not a trigger**. A future production design would still need an independently justified bounded attempt rule, per-entry manual/automatic exclusion, no retry loop, and an episode or cooldown guard that cannot create a connection storm. This gate implements none of those. It does not claim advertisement visibility or BLE connection proves readiness.

The task started from clean `main` at `dc81954b6fa0d1f38f7fb33a66ecfb2a5692809e` (`docs: assess GD82 absence return trigger`), with matching `origin/main` and released tag unchanged. Synthetic tests cover one-attempt transport, result sanitation, stage-specific failure and cleanup, cancellation/unload, entry isolation, and no FORA I/O. **Exact next gate:** user-run normal-ON readiness control first; after it succeeds, wait for a naturally occurring post-measurement comparison. Review both physical results before considering any Stage 13B architecture.
