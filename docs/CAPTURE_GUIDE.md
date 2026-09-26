# Stage 1 capture guide

This is a procedure for a future authorized discovery session. No captures have been made for Stage 0.

## Before collecting

1. Work only with a meter and Home Assistant environment the user controls.
2. Record capture date, meter model/label, firmware if known, Home Assistant version, adapter or ESPHome proxy path, and capture method in a private log.
3. Keep raw logs in private storage outside this public repository. Disable cloud sharing of personal captures.

## Advertisement and GATT inventory

1. Observe Home Assistant Bluetooth advertisement data for the meter while it is available. Record local name, address/identifier and whether it rotates, manufacturer data, advertised service UUIDs, RSSI, and connectability. Record which adapter or proxy observed it.
2. Compare multiple observations to see whether identifiers or advertisement fields change. Do not assume the documented UUID identifies the meter.
3. In a controlled session, inspect GATT services and characteristics; record exact UUIDs and properties, particularly whether the documented characteristic has write and notify on the actual device.
4. Observe notifications before any application commands and record timing, length, and raw bytes privately. If writes occur in an authorized later protocol session, record the exact write/notify sequence with direction and timestamps. Do not send guessed commands merely to create traffic.

## Public evidence handling

- Raw logs may contain personal measurements, meter identifiers, addresses, and timestamps. Do not commit or publish them.
- Before creating a public fixture, replace or remove identifying fields and personal health values while preserving protocol-relevant bytes and structure. Document each transformation, source type, and why the fixture still tests the intended behavior.
- If sanitization would invalidate the behavior being tested, keep the capture private and describe only the non-sensitive conclusion in `PROTOCOL.md`.
- Store only reviewed fixtures under `tests/fixtures/ble/`; use a separate evidence note for provenance and confidence.

## Stage 1 exit evidence

Record the advertisement profile, identifier behavior, connectability, GATT inventory, properties, and passive notification observations in `PROTOCOL.md` and `CURRENT_STATUS.md`. Mark missing observations explicitly. Stage 1 does not establish application commands unless separately documented and authorized.
