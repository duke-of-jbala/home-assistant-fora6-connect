# Stage 4 — reusable Home Assistant Bluetooth transport

**State:** Implementation complete for the authorized Stage 4 scope; physical regression has not been run. The existing manual actions were refactored without changing their result keys or command order. No production discovery, synchronization, entity, persistence, pairing, RACP, or additional command was added.

## Boundary and API

`bluetooth.py` owns `Fora6BluetoothTransport(hass, runtime_address)`. Its public coroutine methods are `async_connect()`, `async_subscribe()`, `async_exchange(ProtocolFrame)`, and `async_close()`; it can also be used as an async context manager. `TransportError` exposes only a stable `stage`, `code`, and whether a write completed. `CleanupResult` exposes notification-stop and disconnect outcomes with safe error codes.

The transport accepts any validated request frame; it has no FORA command policy, record parser, scaling, index selection, or queue. `protocol.py` remains pure Python framing/parsing, and `models.py` remains a pure record model. `coordinator.py`, `sensor.py`, `config_flow.py`, and `diagnostics.py` retain their later-stage boundaries.

## Connection and session lifecycle

The caller supplies a runtime address. The transport resolves a `BLEDevice` through `bluetooth.async_ble_device_from_address(hass, address, connectable=True)`, letting Home Assistant select an eligible local adapter or proxy. It does not select a scanner, clear discovery history, or register a discovery matcher. This follows the [Home Assistant Bluetooth API guidance](https://developers.home-assistant.io/docs/core/bluetooth/api/) and [integration best practices](https://developers.home-assistant.io/docs/bluetooth/).

It calls `establish_connection(BleakClientWithServiceCache, ...)` with the previously proven two-attempt connection setting, a 20-second per-attempt timeout, a 50-second outer bound, no pairing, and service cache disabled. This connector retries connection establishment only; see the [connector's documented retry behavior](https://github.com/Bluetooth-Devices/bleak-retry-connector). The transport owns the connector task. If the caller is cancelled or the outer connection wait expires, it cancels that task and waits within a second explicit bound for its result. A client returned while cancellation is being handled is disconnected before cancellation propagates. If a non-cooperative connector returns only after that bound, a completion callback disconnects the late client directly, including when ordinary session cleanup has already finished. The transport validates that a received client is connected, locates the documented custom service and characteristic, and requires Write and Notify properties. It then subscribes once. No adapter/source name or local HCI interface is embedded.

The transport bounds notification start/stop and disconnect to 10 seconds each, writes to 10 seconds, and responses to 15 seconds by default. The development probe retains its existing 15-second response timeout, which tests can shorten without altering production defaults. Synchronous HA address resolution has no asynchronous wait. All caught Bleak/HA exceptions become stable codes; exception text, runtime addresses, and raw notifications are not logged or returned.

## One response at a time

`async_exchange()` requires an already connected and subscribed session and a validated request `ProtocolFrame`. A per-instance `asyncio.Lock` serializes overlapping exchanges without blocking other meters. For each exchange it stores one expected request and one future, writes the request exactly once with `response=True`, then awaits one notification. The callback ignores notifications when no exchange is pending. For a pending exchange it constructs `ProtocolFrame`, checks marker and checksum there, and checks command echo through `protocol.py`. A malformed or mismatched notification completes that exchange as `invalid_response`; a later packet cannot rescue it. Pending state is cleared on success, failure, timeout, and cancellation. No general packet queue retains health data.

The connector may retry a connection up to two attempts. Application writes are never retried by the transport. Each request is one write, one response wait, and a returned validated frame or safe `TransportError`. The transport does not interpret a frame as a measurement.

Once an application write is attempted, a failed exchange poisons that session. This covers write failure, response timeout, invalid response, peer disconnect after the write, and cancellation after the write begins. A later `async_exchange()` returns `invalid_session_state` without writing. The caller must close the session and create a fresh transport before another exchange. The protocol has no established transaction identifier, so a delayed response could otherwise be mistaken for a response to a later request with the same command ID. Invalid requests and exchanges attempted before subscription do not poison the session because no application write was attempted.

## Cleanup and privacy

`async_close()` is idempotent and attempts `stop_notify` only after successful subscription, then attempts disconnect whenever a client exists. It reports both cleanup failures independently. Its bounded cleanup task is shielded so cancellation of a caller during exchange or cleanup does not skip disconnect. The context manager also closes on setup failure. Connection cancellation propagates to the caller after owned-client cleanup.

The address is held only in the live transport instance. Raw notification bytes and validated response frames remain ephemeral in memory. The transport does not persist or log either and does not put them in user-facing exceptions. The manual probes still return only their established semantic status dictionaries.

## Development-action refactor and verification

`protocol_probe.py` now delegates device resolution, connection, GATT validation, subscription, exchange, and cleanup to this transport. It still chooses the existing bounded sequences: identity uses wake and project query; the one-slot record probe adds User1 metadata and raw-index-zero part requests. The service names, input contract, output keys, timeout values, and privacy-safe status behavior remain the same. Existing probe tests continue to assert exact write order, one write per command, and result fields.

Dedicated hardware-free transport tests cover resolution, connection slots/failures, service and property validation, subscription, successful and malformed exchanges, poisoned-session rejection, late notifications, owned-client cleanup on cancellation and timeout, privacy, concurrent exchanges, and bounded cleanup. No physical meter result is claimed by Stage 4 implementation or its hardening pass.

**Controlled regression after review:** with the GD82 ON, the user may run the already-proven `fora6_connect.probe_protocol_identity` once, and optionally the previously proven one-slot `fora6_connect.probe_protocol_record` once. Compare only privacy-safe result flags and cleanup outcomes with the Stage 2E/2F baseline. Do not add commands, record loops, or decoded real-result exposure. The selected adapter/proxy remains unresolved until Stage 9.

**Proposed Stage 5 gate:** after Stage 4 review and any separately approved controlled transport regression, separately authorize measurement/entity modeling using only supported record semantics. Units, QC meaning/policy, unknown analytes, and production sync remain separate decisions; Stage 5 is not started here.
