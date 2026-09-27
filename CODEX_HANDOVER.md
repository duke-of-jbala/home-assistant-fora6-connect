# FORA 6 Connect Codex Handover

## Stage 7B implementation checkpoint

The public `main` branch began at `2e59a47763c6d6bd1af3071e5a8d7cfdc4eaefe0` — `docs: refresh rewritten-history references` — with a clean working tree. Stage 7B adds the separately authorized, development-only `fora6_connect.probe_history_window` action. It confirms project `0x4183`, queries User1 raw-slot metadata once, and requires raw count exactly two before the fixed User1 indexed pair sequence `1 → 0 → 1`. It compares the first and last index-one frames privately in memory and returns only structural/equality flags. The action uses the hardened Stage 4 transport and deterministic cleanup. No physical Stage 7B test has been run by Codex.

- **Branch/date:** `main`, 2026-09-27 (Europe/London).
- **Last completed/checkpoint commit:** `2e59a47763c6d6bd1af3071e5a8d7cfdc4eaefe0` — `docs: refresh rewritten-history references`. The public remote matched it before this task; all pre-rewrite SHAs are obsolete.
- **Changes after checkpoint:** yes, implementation, 23 synthetic tests, and documentation at this pre-commit observation. Verify and report the resulting commit SHA, push result, and final tree separately.
- **Files changed:** `custom_components/fora6_connect/__init__.py`, `history_probe.py`, `protocol.py`, `services.yaml`, `translations/en.json`; `tests/test_history_probe.py`, `tests/test_gatt_probe.py`; `docs/STAGE7B_BOUNDED_TRAVERSAL_PROBE.md`, `docs/STAGE7A_HISTORY_TRAVERSAL_DESIGN.md`, `docs/STAGE7_HISTORY_SYNC.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEVELOPMENT.md`, `docs/PROTOCOL.md`; `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`.
- **Boundaries:** no command outside `0x22`, `0x24`, `0x2B`, `0x25`, `0x26`; no more than three record pairs; no physical test, production history loop, coordinator work, entity update, deduplication, persistence, pairing, or extra action input. The existing identity and record probe schemas and sequences remain unchanged.

## Checks before commit

- Full unit suite: **265 passed** (`python3 -m unittest discover -s tests -q`); 23 new Stage 7B tests, 242 baseline tests retained.
- `compileall`, `tabnanny`, four JSON parses, one YAML parse, and `git diff --check`: passed.
- Synthetic tests cover count 0/1/3 stops, project/metadata/part failures, exact sequence and User1 bytes, repeated equality/difference, privacy, no retries, success/failure/cancellation cleanup, and response-enabled writes. Finish full staged diff review, privacy/artifact scan, `git diff --cached --check`, commit, and normal push.

**Exact next gate:** controlled user-run physical Stage 7B validation after review: deploy, restart Home Assistant, turn the GD82 ON, invoke `probe_history_window` once, and share only the sanitized result. Review it before authorizing broader traversal, deduplication, or production sync. The existing uric-acid entity remains unavailable until a separately authorized production measurement path exists.
