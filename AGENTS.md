# FORA 6 repository instructions

- Work only in `<former local checkout>`. Do not access, inspect, modify, or depend on unrelated repositories, including `<unrelated local checkout>`.
- Develop in the stages in `FORA6_MASTER_ROADMAP.md`; `ROADMAP.md` is only a pointer. Stop at each stage gate until the user authorizes the next stage.
- Never invent FORA BLE commands, packet formats, checksums, record layouts, analyte codes, timestamps, flags, or responses. Record the documentary or captured evidence and its provenance before implementing protocol behavior.
- Keep `custom_components/fora6/protocol.py` independent of Home Assistant, ESPHome, and Bluetooth hardware. Require sanitized, evidence-derived regression fixtures and decoding tests for protocol changes.
- Keep ESPHome as a generic Bluetooth proxy. FORA-specific communication and decoding belong in the Home Assistant integration and its protocol layer.
- Treat service/characteristic UUIDs alone as insufficient device identification. Use supported Home Assistant Bluetooth APIs for future local and proxy transport.
- Preserve original meter measurement time separately from sync/ingestion time. Keep control-solution results distinct where the device provides that status.
- Never commit private health data or identifiable raw captures. Sanitize real BLE captures before adding public fixtures; document the sanitization and provenance.
- At the end of **every substantive Codex task**, update `CURRENT_STATUS.md` and refresh `CODEX_HANDOVER.md` for that task. Update `FORA6_MASTER_ROADMAP.md` if a roadmap or gate status changed, and `CHANGELOG.md` if a notable project change occurred.
- In tracked Markdown, record the branch, last completed/checkpoint commit SHA and message, whether this task changed files after that checkpoint, files changed, tests/checks actually run and their results, and the exact next gate. Do not require a tracked file to contain the SHA of the commit that contains it. After committing, report that task commit's full SHA and final `git status --short` in the terminal/final response.
- The Markdown handover files must describe actual observed repository state at a stated point, not intended state. Never claim the working tree is clean without checking it. If a commit will change the live state, record the pre-commit observation in Markdown and verify/report the post-commit state separately.
- Stop at authorization boundaries. Do not require screenshots as the primary handover mechanism; durable Markdown files must be sufficient for ChatGPT to review progress.
- Avoid destructive Git actions and history rewriting without explicit authorization. Do not push, merge, tag, publish, or create releases without explicit authorization.
