# Protocol evidence register

This page records what is established before any FORA application protocol implementation. The source for the GATT UUID and property claims is the FORA 6 Connect GD82 documentation supplied in the Stage 0 project brief; the underlying document has not yet been independently inspected in this repository.

## Confirmed for this project brief

- Product: FORA 6 Connect; model/variant: GD82.
- Documented BLE service UUID: `00001523-1212-efde-1523-785feabcd123`.
- Documented BLE characteristic UUID: `00001524-1212-efde-1523-785feabcd123`.
- The documentation describes the characteristic as supporting write and notify.

The UUID pair alone cannot establish that an observed BLE device is a FORA 6 Connect. Stage 1 must verify the actual device's advertisement and GATT behavior.

## Working hypotheses

- The meter may expose historical measurements over the documented write/notify characteristic. This is a product goal, not a verified protocol fact.
- The meter may be reachable through a connectable ESPHome Bluetooth proxy via Home Assistant's stack. End-to-end behavior remains untested.

## Unknown

- Commands and responses.
- Framing and checksums.
- Device identification response.
- Memory retrieval protocol.
- Measurement record format and analyte codes.
- Timestamp representation.
- Measurement status and control-solution flags.
- Units, scaling, and error responses.
- Which expected analytes are supported by the exact GD82 variant.

Do not add protocol behavior until evidence, provenance, sanitized frames, and regression tests are available. See `CAPTURE_GUIDE.md`.
