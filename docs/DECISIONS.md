# Architecture decisions

These decisions are accepted for Stage 0. Revisit only on explicit instruction or documented new evidence.

## ADR-001 — FORA logic in Home Assistant

**Status:** Accepted. Home Assistant performs FORA-specific communication and decoding. This keeps device behavior within the integration that owns its entities and sync state.

## ADR-002 — ESPHome is transport only

**Status:** Accepted. ESPHome Bluetooth Proxy remains generic, allowing the same integration to use local or remote Home Assistant Bluetooth paths.

## ADR-003 — Independent parser

**Status:** Accepted. The FORA protocol parser is independent of Home Assistant, so captured raw frames can be decoded in unit tests without Bluetooth hardware.

## ADR-004 — Evidence before protocol code

**Status:** Accepted. Documented or captured evidence with provenance must precede protocol implementation, preventing guessed packets from becoming production behavior.

## ADR-005 — One meter, one HA device

**Status:** Accepted. One Home Assistant device represents each physical FORA 6 meter; later entities belong to it.

## ADR-006 — Preserve meter time

**Status:** Accepted. Original measurement timestamps must be stored separately from synchronization time, so imported history is not misdated.

## ADR-007 — Protect health data

**Status:** Accepted. Private health data and identifiable raw captures must not enter the public repository. Any public fixture must be sanitized and provenance recorded.
