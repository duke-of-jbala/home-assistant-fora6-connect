# Roadmap

Stages are gates. Completing one does not authorize starting the next.

## Stage 0 — Repository/bootstrap

Create the HACS-shaped repository skeleton, architecture decisions, evidence rules, and validation baseline. **Complete.**

## Stage 1 — FORA 6 BLE discovery

Establish advertisement/local name, address behavior, manufacturer data, advertised UUIDs, connectability, GATT structure, characteristic properties, and raw notification behavior. Record provenance and sanitize captures.

## Stage 2 — Protocol acquisition / reverse engineering

Use legitimate public documentation and/or controlled device/app observations to establish the actual command and response protocol.

## Stage 3 — Protocol parser and captured-frame fixtures

Build an HA-independent parser with sanitized, evidence-derived regression fixtures and tests.

## Stage 4 — Home Assistant Bluetooth transport

Implement connection and notification handling through supported HA Bluetooth APIs, compatible with local adapters and ESPHome Bluetooth proxies, with retry-safe connections.

## Stage 5 — Measurement/entity model

Represent validated FORA measurements, units, status, and device association correctly in HA. Keep test/control readings distinct when supported by evidence.

## Stage 6 — Config flow and Bluetooth discovery

Provide robust discovery and setup after a reliable identification method is known. Do not claim unrelated devices sharing similar UUIDs.

## Stage 7 — Historical-memory synchronization

Implement record retrieval, deduplication, resume/sync state, and preservation of original meter timestamps independently of ingestion time.

## Stage 8 — Diagnostics and error handling

Provide non-sensitive diagnostics and predictable recovery from communication failures.

## Stage 9 — ESPHome Bluetooth Proxy validation

Validate end-to-end operation using the user's existing generic proxy architecture.

## Stage 10 — HACS packaging

Verify repository, manifest, brand assets, and installation layout against then-current HACS requirements.

## Stage 11 — Documentation and release candidate

Complete public documentation, installation instructions, compatibility notes, and release candidate validation.

## Stage 12 — v1.0.0 release

Make a stable public release only after validation and explicit authorization.
