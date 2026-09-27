# Current Status — FORA 6 Connect

Stages 0–6B are complete for their authorized scopes, including the real GD82 setup validation. Stage 7A's offline history review is complete. **Stage 7B's bounded development action is implemented and synthetic-tested; its physical validation is pending.** The configured meter still has one unavailable uric-acid entity. There is no production history synchronization, polling, deduplication, or persistence.

## Stage 7B pre-commit repository observation

- **Date/branch:** 2026-09-27 (Europe/London), `main`.
- **Last completed/checkpoint commit:** `2e59a47763c6d6bd1af3071e5a8d7cfdc4eaefe0` — `docs: refresh rewritten-history references`. Public `origin/main` matched this checkpoint before work began. Older pre-rewrite SHAs are obsolete.
- **Starting tree:** clean; `git status --short` returned no entries before this task.
- **Changes after checkpoint:** yes. This is a pre-commit observation with tracked edits and new files; report the task commit SHA and post-commit status separately.
- **Files changed:** `custom_components/fora6_connect/__init__.py`, `history_probe.py`, `protocol.py`, `services.yaml`, `translations/en.json`; `tests/test_history_probe.py`, `tests/test_gatt_probe.py`; `docs/STAGE7B_BOUNDED_TRAVERSAL_PROBE.md`, `docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md`, `docs/STAGE7_HISTORY_SYNC.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`; `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`.
- **Behavior:** one manually invoked `probe_history_window` action, fixed User1 `0x22 → 0x24 → 0x2B` identity/metadata prefix, then only if raw count equals two, three `0x25`/`0x26` pairs at indexes `1 → 0 → 1`. Index-one requests and the `0x2B` app-labeled newest-index parser are pure protocol additions. Results expose structure and repeat equality only. Existing identity/record action schemas, Config Flow, transport, coordinator, and entity state are unchanged. Codex ran no physical test.

## Checks actually run before commit

- Full unit suite: **265 passed** (`python3 -m unittest discover -s tests -q`), including 23 new Stage 7B tests; prior public baseline was 242.
- `python3 -m compileall -q custom_components tests` and `python3 -m tabnanny custom_components tests`: passed.
- Four JSON files and one services YAML file parsed successfully; `git diff --check` passed.
- Synthetic tests confirm the exact nine-write maximum, exact User1 requests, count mismatch stopping after metadata, per-part fail-closed stops, no command retry, equality-only repeat comparison, privacy-safe output, `response=True`, and cleanup/cancellation. Full staged diff, privacy/artifact, and command audits are required before commit and push.

**Exact next gate:** after code review, the user deploys the committed integration, restarts Home Assistant, turns the GD82 ON, runs `fora6_connect.probe_history_window` once, and shares only the sanitized result. Review that result separately before any broader traversal or production synchronization authorization.
