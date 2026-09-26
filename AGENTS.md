# FORA 6 repository instructions

- Work only in `<former local checkout>`. Do not access, inspect, modify, or depend on unrelated repositories, including `<unrelated local checkout>`.
- Develop in the stages in `ROADMAP.md`. Stop at each stage gate until the user authorizes the next stage.
- Never invent FORA BLE commands, packet formats, checksums, record layouts, analyte codes, timestamps, flags, or responses. Record the documentary or captured evidence and its provenance before implementing protocol behavior.
- Keep `custom_components/fora6/protocol.py` independent of Home Assistant, ESPHome, and Bluetooth hardware. Require sanitized, evidence-derived regression fixtures and decoding tests for protocol changes.
- Keep ESPHome as a generic Bluetooth proxy. FORA-specific communication and decoding belong in the Home Assistant integration and its protocol layer.
- Treat service/characteristic UUIDs alone as insufficient device identification. Use supported Home Assistant Bluetooth APIs for future local and proxy transport.
- Preserve original meter measurement time separately from sync/ingestion time. Keep control-solution results distinct where the device provides that status.
- Never commit private health data or identifiable raw captures. Sanitize real BLE captures before adding public fixtures; document the sanitization and provenance.
- Update `ROADMAP.md`, `CHANGELOG.md`, and `CURRENT_STATUS.md` during material stages.
- Avoid destructive Git actions and history rewriting without explicit authorization. Do not push, merge, tag, publish, or create releases without explicit authorization.
