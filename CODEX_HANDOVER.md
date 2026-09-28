# FORA 6 Connect Codex Handover

## Stage 13A-P2 — development one-clear re-arm observer, pre-commit

Started from clean `main` at `64ade3c7667648fefcebd8b3624de570bc895501` (`docs: record bounded GD82 callback observation`) on 2026-09-28 (Europe/London), with `origin/main` matching; `v1.0.0` still peels to `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. The new configured-entry action `fora6_connect.observe_advertisement_rearm` listens to Core 2026.9.4-compatible changed-data callbacks, clears HA advertisement history once only after the first live callback, and observes until the bounded 60-second window ends. If no callback arrives, no clear occurs. It is exclusive with the existing observer for that entry and unload stops either observation. No GATT, active scan, FORA command, sensor update, or production automatic sync is involved.

The separate existing `observe_advertisements` action is used for the later physical OFF → ON comparison and performs no clear. The first action's result alone cannot tell whether the GD82 remained ON; user physical confirmation is essential. [Stage 13A-P2 instructions and interpretation](docs/STAGE13A_P2_ADVERTISEMENT_REARM_TEST.md) distinguish a false same-ON re-dispatch from bounded later-wake evidence and Core 2026.9.4's lack of per-packet visibility. Physical re-arm semantics remain **pending**.

Changed files are listed in `CURRENT_STATUS.md`; the tree is modified at this pre-commit observation. At this point 24/24 targeted observer tests and 399/399 full tests passed. Compileall, tabnanny, four JSON/two YAML/one TOML parses, staged and unstaged diff checks, and added-line privacy/credential/identifier/health-data/private-path/no-GATT/no-auto/artifact audits passed. Pushed HACS/hassfest must be reported after completion. Report actual commit, remote, and clean-tree status separately. Released `v1.0.0` is untouched.

**Exact next gate:** user deploys this development build, restarts HA, performs one continuous-ON cache-clear observation, and if needed a separate no-clear later OFF → ON observation; only then classify the result. No Stage 13B implementation.

## Stage 13A-P1 — physical callback evidence and re-arm assessment, pre-commit

Starting state was clean `main` at `56fec412a2d39ac1cf9ee24ff269dd0a70894e61` (`fix: support older Home Assistant Bluetooth callbacks`) on 2026-09-28 (Europe/London), with matching `origin/main`; released `v1.0.0` still peels to `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. The user ran the 60-second observer on Core 2026.9.4. It reported no supported per-packet callback, one changed-data callback at relative `T+17.7 s`, one sanitized source, successful cleanup, and no unload stop. The intended OFF → ON → OFF → ON sequence did not produce a demonstrated callback per wake. This does not prove the second episode emitted no packets or that Home Assistant received none.

The event's shape had two service UUIDs and connectable true but zero manufacturer/service-data entries and no exact name match. Earlier Advertisement Monitor detail showed the public name and one manufacturer entry. The callback's partial/merged representation cannot be equated to the UI or raw radio packet. [The Stage 13A-P1 document](docs/STAGE13A_P1_BLUETOOTH_CALLBACK_OBSERVER.md) records these **LIVE-CORROBORATED** facts and proposes Stage 13A-P2: one explicitly user-controlled `async_clear_advertisement_history()` while the meter remains ON, then a separate later OFF → ON observation. A same-ON callback after clear would show a false wake signal; silence before OFF is inconclusive without per-packet receipt telemetry. No cache clear or automatic sync is implemented in this task.

This documentation task changes the five Markdown files listed in `CURRENT_STATUS.md`; the tree is modified at this pre-commit observation. No private measurement, timestamp, identifier, payload, screenshot, or raw log is included. Full **388/388** tests, compileall, tabnanny, four JSON/two YAML/one TOML parses, unstaged diff check, and five-file added-line privacy/artifact/no-runtime-diff audit passed. Staged check and any pushed CI remain to be verified. Report actual commit, remote and clean-tree status after commit/push.

**Exact next gate:** separate authorization for Stage 13A-P2 bounded development-only one-time re-arm semantics test. Stage 13B production auto-sync remains unauthorized.

## Stage 13A-P1 — 2026.9.x callback compatibility follow-up, pre-commit

The task began on clean `main` at `068a6fa8d7ac2926cad349fda7efb3ea646a2d2b` (`feat: add bounded Bluetooth callback observer`) on 2026-09-28 (Europe/London), with matching `origin/main`; `v1.0.0` still targets `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. The user's first physical observer invocation failed immediately with a generic action error and no callback result. Core 2026.9.4's released Bluetooth module does not export the observer's first-call `async_register_advertisement_callback`; that call necessarily raises a missing-attribute `AttributeError`. The wrapper erased the traceback, so the exact physical traceback itself is unavailable. `async_register_callback`, replay-disable support, and `async_clear_advertisement_history` do exist in that release.

The [Stage 13A-P1 record](docs/STAGE13A_P1_BLUETOOTH_CALLBACK_OBSERVER.md) now distinguishes old-Core changed-only mode from newer per-packet comparison. Missing per-packet support is explicit and packet counts are `null`, not zero. Other registration/wait failures preserve only sanitized `stage`/exception `type` in the action error. The cache-clear API is assessed but never called; no deprecated scanner callback, GATT operation, protocol command, active scan, sensor update, or auto-sync was introduced. Physical callback receipt remains unvalidated.

Changed files are listed in `CURRENT_STATUS.md`; this is a modified pre-commit tree observation. Core 2026.9.4 source comparison and targeted **13/13** synthetic tests passed; full suite **388/388** passed. Compileall, tabnanny, four JSON/two YAML/one TOML parses, unstaged diff check, and changed-line privacy/artifact/no-GATT/no-auto audit passed. Staged check and pushed HACS/hassfest remain to be verified. Report actual final commit, remote and tree separately.

**Exact next gate:** deploy compatibility fix and rerun bounded observer, sharing sanitized `packet_callback_supported` and changed-callback counts/relative samples only. Do not infer repeated packet receipt from a changed-only result or begin Stage 13B.

## Stage 13A-P1 — development-only callback observer, pre-commit

Starting state was clean `main` at `84f6362d0cabca5e9e45905e6fffe75a9b69556d` (`docs: assess GD82 advertisement callback observation`) on 2026-09-28 (Europe/London), with `origin/main` matching; released `v1.0.0` still peels to `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. The user reproduced the Advertisement Monitor issue in Chrome and found that navigation/hard refresh can show a more recent row than the live open view. This does not prove packet delivery, Home Assistant deduplication, or a frontend defect.

[Stage 13A-P1](docs/STAGE13A_P1_BLUETOOTH_CALLBACK_OBSERVER.md) adds a manually invoked, configured-entry-targeted, 60-second read-only observer. It compares HA per-advertisement callbacks with changed-data callbacks using passive matching and disabled cached replay. Results contain only bounded counts, relative times, structural shapes, and ephemeral source aliases. It makes no GATT connection, write, protocol request, active-scan request, cache mutation, sensor update, or automatic refresh. Unload and cancellation remove callbacks. `async_clear_advertisement_history()` is documented but not called. No physical observer result exists yet; production remains manual-only.

Files changed are listed in `CURRENT_STATUS.md`; this is a modified pre-commit tree observation. Dedicated synthetic observer tests **10/10** and the full suite **385/385** passed (released baseline 375). Compileall, tabnanny, four JSON/two YAML/one TOML parses, unstaged diff check, and added-line privacy/artifact audit passed; only an explicitly synthetic test address matched the identifier scan. Final staged check and pushed HACS/hassfest still need verification. Report the actual task commit, remote, and final tree status separately.

**Exact next gate:** user-run bounded Stage 13A-P1 physical callback observation with sanitized output. Compare normal OFF → ON episodes first; history mode and post-measurement state remain separately pending. Do not begin Stage 13B auto-sync.

## Stage 13A-P — callback observer assessment, pre-commit

The starting checkpoint was clean `main` at `1c05d62165879f32b85dfb4dbab7f7ac0bed8714` (`docs: note inconclusive Bluetooth monitor refresh`) on 2026-09-28 (Europe/London), with matching `origin/main`; released `v1.0.0` still peels to `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. After the user's Home Assistant Core 2026.9.4 update and HAOS restart, the first normal meter ON appeared in Advertisement Monitor almost immediately, but subsequent normal OFF → ON cycles did not reset `Updated`. Stable displayed name/structural fields, connectable flag, and one proxy source cannot distinguish absent packets, Bluetooth deduplication, or a stale UI. A Core/frontend regression is unproven. History and post-measurement advertisements remain unobserved.

The [Stage 13A-P evidence table](docs/STAGE13A_PHYSICAL_ADVERTISEMENT_OBSERVATION.md) and current official HA API review support **a separately authorized development-only callback observer** as the next smallest evidence tool. It would compare per-packet callbacks with live changed-data callbacks, with no GATT, command, write, refresh, startup registration, or persistent state. This task implements no observer and does not authorize Stage 13B. Production remains manual-only.

This task changes `docs/STAGE13A_PHYSICAL_ADVERTISEMENT_OBSERVATION.md`, `CURRENT_STATUS.md`, `CODEX_HANDOVER.md`, `FORA6_MASTER_ROADMAP.md`, and `ROADMAP.md`; the tree is modified at this pre-commit observation. The full `unittest` suite passed **375/375**; compileall, tabnanny, four JSON/two YAML/one TOML parses, unstaged diff check, changed-Markdown private-data/credential/artifact audit, and no-runtime-diff check passed. Verify staged diff and post-push CI/state separately.

**Exact next gate:** separate authorization for Stage 13A-P1 bounded development-only Bluetooth callback observer, followed by sanitized user-run OFF/ON/history and naturally occurring post-measurement observations. No automatic sync.

## Stage 13A-P — HA monitor-liveness caveat, pre-commit

The prior partial-evidence checkpoint was clean pushed `main` at `66dcdb35716794cda7b8410b15e358af96ac3f6a` (`docs: record partial GD82 advertisement observation`) on 2026-09-28 (Europe/London), with `origin/main` matching and HACS/hassfest green. The released `v1.0.0` target remains `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. The user's first normal-ON attempt did not refresh the HA Advertisement Monitor row; an HAOS restart restored view updates. Treat that attempt as an **inconclusive UI/Bluetooth observability failure**, never as evidence of no GD82 broadcast. [The Stage 13A-P table](docs/STAGE13A_PHYSICAL_ADVERTISEMENT_OBSERVATION.md) now separates the stale-view attempt from the pending post-restart comparison.

This follow-up changes `docs/STAGE13A_PHYSICAL_ADVERTISEMENT_OBSERVATION.md`, `CURRENT_STATUS.md`, and `CODEX_HANDOVER.md`; the working tree is modified at this pre-commit observation. No observer, GATT operation, auto-sync callback, or released ref changes. Follow-up **375/375** tests, compileall, tabnanny, four JSON/two YAML/one TOML parses, unstaged diff check, and changed-Markdown privacy/artifact/no-runtime-diff audit passed. The prior checkpoint's official validators passed; follow-up staged check and CI remain to be verified.

**Exact next gate:** user-run post-restart normal ON → OFF → second ON structural/timing observation, then safe history mode; post-measurement remains pending until normal use. Stage 13B is not authorized.

## Stage 13A-P — physical advertisement observation with partial OFF evidence

Started from clean `main` on 2026-09-28 (Europe/London) at `c858338481031e9c0090705666af664b72e5260d` (`docs: review automatic refresh trigger architecture`), with `origin/main` matching and `v1.0.0` still peeling to `dd26b65ab467381db58ba7a525c6b8eabca8e00a`. The installed HA Advertisement Monitor first showed a basic row; clicking it exposed details. In the user-run fully OFF state, `Updated` age increased on a cached last-seen row, with public name, one manufacturer entry, standard Glucose among service UUIDs, no service data, and retained prior proxy source. Connectability was not shown; raw advertisement bytes were not shared. The [Stage 13A-P document](docs/STAGE13A_PHYSICAL_ADVERTISEMENT_OBSERVATION.md) records this OFF row and leaves the other five pending. Earlier normal-ON/light and post-measurement subscription evidence is not passed off as advertisement data. No observer or automatic callback has been added.

This task changes the five Markdown files listed in `CURRENT_STATUS.md`. The tree is modified at this pre-commit observation. Baseline/ref checks and official HA UI/API guidance review were run. Full **375/375** tests, compileall, tabnanny, four JSON/two YAML/one TOML parses, unstaged diff check, and changed-Markdown privacy/artifact audit passed. Staged privacy/diff review and post-push HACS/hassfest remain to be verified if a documentation checkpoint is committed.

**Exact next gate:** sanitized user-run detail-view normal-ON/history/off/repeated-ON timing and shape comparison, plus a naturally occurring post-measurement state when available; consider a development-only observer only for material gaps left by the UI. Do not begin Stage 13B or Stage 8H.

## Stage 13A — post-v1 auto-trigger review, pre-commit

Started from clean `main` on 2026-09-28 (Europe/London) at `dd26b65ab467381db58ba7a525c6b8eabca8e00a` (`chore: prepare FORA 6 Connect v1.0.0`), with `origin/main` matching and local/remote `v1.0.0` peeling to that released commit. The release remains unchanged. [The Stage 13A record](docs/STAGE13A_AUTOMATIC_SYNC_ARCHITECTURE.md) audits current HA Bluetooth callbacks and ESPHome proxy guidance against the configured-entry manual coordinator, compares trigger candidates, and defines a privacy-safe physical state-observation gate. The observed post-measurement notification-subscription failure means advertisement visibility is not a readiness guarantee. Current-state refresh remains manual-only.

This task changes the nine Markdown files listed in `CURRENT_STATUS.md`; the tree is modified at this pre-commit observation. No runtime, test, protocol, identity, or v1 release artifact changes are made. Baseline/ref checks and official documentation/code review were completed. Full **375/375** tests, compileall, tabnanny, four JSON/two YAML/one TOML parses, unstaged diff check, and changed-Markdown privacy/artifact audit passed. Staged diff review and post-push official validators must be verified before reporting completion.

**Exact next gate:** separately authorize privacy-safe physical advertisement-state observation (and a bounded development-only structural observer only if needed), then reassess whether a Stage 13B opt-in auto-refresh trigger can be safely specified. Stage 8H remains unstarted.

## Stage 12 Phase A — prepared for final release review, pre-commit

Starting state was clean `main` at `9cb9a22c46c9c1842eb7916c6edcb02be322a3be` (`docs: close Stage 11 HACS validation`) on 2026-09-27 (Europe/London), with `origin/main` matching. The user authorized Phase A release preparation only. [The Stage 12 record](docs/STAGE12_V1_RELEASE_PREPARATION.md) defines manifest `1.0.0`, a future annotated `v1.0.0` tag and stable latest GitHub release, no custom HACS asset, exact release commands, rollback policy, and known limits. [The release body](docs/RELEASE_NOTES_V1.0.0.md) is prepared but unpublished. The changelog has a concise 1.0.0 section and preserves stage history separately. No runtime Python or test behavior changed; no tag or release exists.

Files changed are listed in `CURRENT_STATUS.md`; this is a modified pre-commit tree observation. Local **375/375** tests, compileall, tabnanny, four JSON/two YAML/one TOML parses, and isolated component copy passed. GitHub metadata/license and HACS release rules were reviewed. Finish the staged privacy/artifact/diff audits, commit/push normally, then confirm HACS and hassfest on the pushed SHA and report the actual commit, remote, and final clean tree. Do not treat local tests as real HACS update evidence; Stage 11's real install/proxy result remains the physical basis.

**Exact next gate:** after Phase A passes, ask for explicit authorization to create/push `v1.0.0` and publish the prepared stable GitHub release, or accept a narrow correction/hold decision. Do not execute Phase B in this task. Stage 8H and post-v1 features remain unstarted.

## Stage 11 release candidate — physically validated closure, pre-commit

The clean, pushed starting checkpoint for this closure was `bab4bed9e7d2159a237f2c462f7c379ea1f2f599` (`docs: prepare Stage 11 HACS validation`) on `main`, 2026-09-27 (Europe/London). `origin/main` matched. [Official HACS and hassfest jobs](https://github.com/duke-of-jbala/home-assistant-fora6-connect/actions/runs/36355458767) passed on that exact SHA. The user then downloaded the custom Integration through HACS over the earlier manual copy, restarted Home Assistant, and reloaded the existing FORA entry. The same entry, one GD82 device, and one uric-acid entity remained. The sensor initially appeared unavailable; the manual action selected the existing entry. No relevant startup/reload error was observed.

The user ran one real post-HACS count-four manual refresh. It updated the existing sensor with no action or cleanup error and no duplicate device/entity or relevant log error. Home Assistant Bluetooth Connections identified the Atom Lite ESPHome proxy as the active FORA connection Source; the row disappeared after the action. This is direct evidence for the tested HACS-installed proxy transaction. No real measurement value, timestamp, address, screenshot, or raw log is committed. HACS offered no safe re-download option, so update detection/replacement is untested; uninstall/reinstall is deferred. Stage 11 is complete for the applicable RC validation scope, with no RC tag/release or v1 publication.

This closure changes only the Markdown files listed in `CURRENT_STATUS.md`; the tree is modified at this pre-commit observation. Full **375/375** tests, compileall, tabnanny, resource parsing, and isolated copy passed again. Report the actual closure commit, remote verification, and final tree status after commit/push.

**Exact next proposed gate:** separately authorize Stage 12 v1.0.0 release preparation/publication and approve the final version/notes before any tag or GitHub release. Stage 8H is optional and unstarted.

## Stage 11 release candidate — pending physical HACS install

Starting state was clean public `main` at `a7a1d37c805af6e5567efefaf837e88a6bdbfc9b` (`docs: close Stage 10 HACS readiness`) on 2026-09-27 (Europe/London); `origin/main` matched. The user confirmed HACS is installed but the active FORA component was manually copied. A fresh [official HACS/hassfest run](https://github.com/duke-of-jbala/home-assistant-fora6-connect/actions/runs/36355057262) passed on the baseline. Local **375/375** tests, compileall, tabnanny, resource parsing, and isolated package copy passed. Stage 9's physical proxy result is prior evidence, not proof of a HACS-installed run.

This task changes only the Markdown files listed in `CURRENT_STATUS.md`, including [the controlled Stage 11 procedure](docs/STAGE11_RELEASE_CANDIDATE_VALIDATION.md) and a draft RC note. Keep manifest `0.1.0` for the default-branch HACS test. HACS does not adopt manual files automatically; it must download the custom repository into the same component path. Back up the installation, preserve the config entry and registry objects, and stop if HACS reports a file conflict. Do not tag or release to simulate an update. This is a pre-commit observation; verify the actual commit, remote, CI, and clean tree afterward.

**Exact next gate:** user-run HACS download of the custom Integration, restart/reload, registry and action checks, real manual refresh with direct Bluetooth Connections proxy Source, safe re-download if offered, and sanitized log review. Stage 11 remains pending those results. Stage 8H and Stage 12 are not started.

## Stage 10 HACS packaging — validated closure, pre-commit

Public `main` was clean at `cc06e9666fbb305a7433509f5ec7706b911db8f1` (`fix: satisfy hassfest packaging checks`) on 2026-09-27 (Europe/London), with origin/main matching. [GitHub Actions run 36354523910](https://github.com/duke-of-jbala/home-assistant-fora6-connect/actions/runs/36354523910) completed **successfully** for this SHA: both official HACS Integration validation and Home Assistant hassfest passed. Stage 10 is complete for repository packaging and validation. The initial manifest-order failure was addressed by the later narrow follow-up. No HACS UI install/update is claimed; that controlled user-facing exercise belongs to Stage 11.

The validated package uses one self-contained integration directory, root HACS metadata, original local icon, MIT license, `0.1.0` development manifest version, read-only pinned CI, and documented install/update/remove steps. The full synthetic suite passed **375/375**; compileall, tabnanny, JSON/YAML/TOML parsing, isolated copy, diff/privacy/artifact checks passed. BLE transport, record selection, sensor behavior, and Stage 9 physical evidence remain unchanged.

This documentation closure changes the files listed in `CURRENT_STATUS.md`; the tree is modified at this pre-commit observation. Verify its own commit/push, GitHub workflow, remote main, and final status separately.

**Exact next proposed gate:** separately authorize Stage 11 release-candidate validation with a controlled HACS custom-repository install/update and restart. Stage 8H remains optional and unstarted.

## Stage 10 validator follow-up — pre-commit

The first Stage 10 commit `d60aa576d2ab9d19ef237329b5e9bc116de8b1f8` (`chore: prepare HACS integration packaging`) was pushed to `main` on 2026-09-27 (Europe/London) and had a clean local tree before this follow-up. The official HACS integration job passed; hassfest failed on manifest key order and warned about the missing config-entry-only schema. That is a genuine packaging validation finding.

This follow-up changes the files listed in `CURRENT_STATUS.md`: sort manifest keys without value changes, declare the supported Home Assistant config-entry-only schema, add a synthetic schema check, refresh the checkout action pin, and document the finding. The targeted setup group passed **26/26** and the full suite **375/375**; compileall, tabnanny, resource parsing, manifest order, isolated copy, whitespace, and new-line privacy checks passed. The tree is currently modified at this pre-commit observation. Review the staged diff and inspect the second GitHub workflow run before calling Stage 10 complete. No meter operation, automatic synchronization, history import, or sensor-selection change is involved.

**Exact next proposed gate after the official validators pass:** separately authorize Stage 11 release-candidate validation with controlled HACS installation and update. Stage 8H remains optional.

## Stage 10 package and release readiness — pre-commit

Starting checkpoint: clean `main` at `f27035b011b2c8d85a94467f96a73b98b2c9b89f` (`docs: close Stage 9 Atom Lite proxy validation`) on 2026-09-27 (Europe/London), with the expected origin. This task has changed the files listed in `CURRENT_STATUS.md`; the working tree is modified at this pre-commit observation. Verify and report the eventual commit SHA, remote main, GitHub validation jobs, and clean post-push state separately.

Current HACS documentation accepts the repository's single integration package, root `hacs.json`, required manifest keys, original local icon, and default-branch custom-repository installation before a release. Authenticated GitHub metadata inspection found a public active main, description, topics, issues, and MIT license. Stage 10 replaces the bootstrap manifest version with `0.1.0`, adds pinned HACS/hassfest CI, corrects stale Stage 2F action wording, and gives users install/update/removal and privacy guidance. No validated runtime behavior changes. The [Stage 10 record](docs/STAGE10_HACS_PACKAGING_READINESS.md) explains versioning, evidence limits, and Stage 11 criteria.

The established synthetic suite passed **374/374**. Compileall, tabnanny, four JSON/two YAML/one TOML parses, unstaged whitespace check, changed-file privacy scan, artifact scan, and no-Python-diff audit passed. An isolated component copy validated 27 Python modules and the bundled manifest, translations, service descriptions, and brand icon. HACS/hassfest workflow results must be checked on the pushed commit; no real HACS UI install is claimed. Review and check the staged diff before committing.

**Exact next proposed gate after Stage 10 validators pass:** separately authorize Stage 11 release-candidate validation with a controlled HACS custom-repository install/update. Stage 8H is optional and unstarted.

## Stage 9 Atom Lite proxy validation — physical closure, pre-commit

Starting checkpoint: clean public `main` at `26f464f69091b944d9e75a4c854c6eafd63c0329` (`docs: define Atom Lite proxy validation`) on 2026-09-27 (Europe/London), with the expected origin. The user supplied direct connection-source evidence: HA Bluetooth → Connections showed active `FORA 6 CONNECT` with Source explicitly `(Lounge) M5Stack Atom Lite ESPHome Bluetooth Proxy` during `fora6_connect.refresh_current_uric_acid`; the row disappeared shortly after completion. The sanitized action succeeded at count four, updated the existing sensor, found two eligible primaries, and reported no ambiguity/error/cleanup errors. No duplicate device/entity was observed. Private measurement value/time/address are not recorded.

This is **LIVE-CORROBORATED** direct evidence that this tested BLE/GATT transaction traversed the named Atom Lite proxy. Stage 9 is complete for that bounded path and run. It does not establish other adapters/proxies, meter states, counts, or hardware. No runtime code changed. Prior synthetic tests are not evidence of physical route selection; the user-supplied HA Source observation is the physical evidence. Stage 8H and Stage 10 are not started.

Files changed are listed in `CURRENT_STATUS.md`. The full synthetic unit suite passed **374/374**; compileall, tabnanny, JSON/YAML parsing, whitespace and privacy/artifact checks passed. Synthetic tests do not establish proxy traversal; the direct HA Connections Source observation is the physical evidence. No real measurement value, measurement time, device address, screenshot, raw log, credential, or private path is included. Review and run the cached diff check before committing.

**Exact next proposed gate:** separately authorize Stage 10 HACS packaging/readiness. Stage 8H history exposure is optional and not a prerequisite; neither gate is started by this closure.

## Stage 9 proxy-route preparation — pre-commit observation

At the start, public `main` was clean at `9b4be25b396bee63a3b1c66c06fa2b1ec3935e81` (`fix: harden manual uric acid refresh`), on 2026-09-27 (Europe/London), with the expected origin. This task changes the documentation/status files listed in `CURRENT_STATUS.md`; the working tree is currently modified. This is a pre-commit observation. The task commit SHA, remote result, and final status belong in the post-commit report.

Stage 9 **remains pending physical validation**. The integration still resolves a connectable GD82 `BLEDevice` via HA Bluetooth and passes it to its existing connector. HA can choose between reachable local adapters and proxies. The offline review did not observe the Atom Lite carrying an active GATT connection and found no justified runtime fix or diagnostic instrumentation. The [Stage 9 validation document](docs/STAGE9_ESPHOME_BLUETOOTH_PROXY_VALIDATION.md) separates advertisement/source metadata from actual connection evidence, defines direct Atom Lite connection evidence or valid sole-route isolation as proof, and gives the user a reversible run/restoration procedure and sanitized checklist.

No physical meter operation, Stage 8H exposure, automatic refresh, history import, protocol expansion, or production identity/unit change occurred. The full verbose suite passed **374/374** (baseline 374). Compileall, tabnanny, four JSON and one YAML parse, and the unstaged diff check passed. `pytest` is unavailable; unittest is the established suite. Privacy, artifact, logging, automatic-sync, and historical-import scans found no newly introduced prohibited content or code. Stage and inspect the final diff, then run `git diff --cached --check` before the authorized documentation commit.

**Exact next gate:** user-run controlled Stage 9 M5Stack Atom Lite proxy connection-path validation and sanitized result review. Do not close Stage 9 from a successful refresh alone. Stage 8H and Stage 10 are not started.

## Stage 8 current-state hardening — pre-commit observation

At the start, public `main` was clean at `0775869d2fd7daf5a904795f4d468ac40bcc7798` (`docs: close Stage 7H manual refresh validation`), on 2026-09-27 (Europe/London), with the expected origin. This task has changed files after that checkpoint; the working tree is currently modified. This is a pre-commit observation. The task commit SHA, remote result, and final status belong in the post-commit report.

Stage 8 is **complete for its authorized offline/synthetic review**. The only runtime change is a one-condition error-precedence fix in `coordinator.py`: if a refresh failed before cleanup and cleanup also failed, retain the original error stage/code and return cleanup errors separately. Successful refresh, count-two/four fixed commands, timestamp selection, privacy boundary, configured-entry target, and manual-only triggering are unchanged. New synthetic tests cover repeat same-measurement refresh, prior-state retention after later failures, combined primary/cleanup failures, unload/reload fresh runtime, and two independent entries/locks. The full verbose suite passed **374/374** (baseline 369). Compileall, tabnanny, four JSON and one YAML parse passed. Unstaged and staged diff checks passed, and the complete staged diff was reviewed before this final handover wording update; recheck the final cached diff before committing.

The process-local current value intentionally becomes unavailable on reload/restart until manual refresh. No `RestoreSensor`, measurement-time or status attribute, diagnostic entity, history store, dedup/resume, startup/advertisement/post-measurement trigger, or polling was added. Action response already supplies selected private value/time and bounded status. The mg/dL native sensor value is separate from app mmol/L display formatting. Device identity/metadata is unchanged. Source review and synthetic tests support two-entry isolation at the coordinator/state level; a real multi-device HA validation has not occurred. The exact selected ESPHome proxy path is still unverified.

Files changed are listed in `CURRENT_STATUS.md`; the new durable review is [Stage 8](docs/STAGE8_CURRENT_STATE_HARDENING_REVIEW.md). Changed-file privacy scan found no private paths, real health examples, or secret assignments; MAC-shaped strings occur only in explicitly synthetic test fixtures. Artifact and runtime command/automation/logging scans found no new prohibited path. No physical meter test was run.

**Exact next proposed gate:** separately authorize Stage 9 explicit ESPHome Bluetooth Proxy path validation. Optional Stage 8H bounded manual uric-acid history exposure is a separate future gate, not a prerequisite. Do not start either from this handover.

## Stage 7H real-device closure — pre-commit observation

Starting checkpoint: clean public `main` at `b5b21ceeaa933d10195febf82f333f74874cf766` (`feat: add manual uric acid refresh`) on 2026-09-27 (Europe/London). Origin is the expected public repository and no tags are present. This task changes Markdown status/evidence files only; this is a **pre-commit observation**. The working tree is currently modified, so report its post-commit/push state separately.

The user validated `fora6_connect.refresh_current_uric_acid` against the existing configured GD82. They powered it on normally, avoided the history arrows, and ran the action once. At raw count four, both candidate primaries were eligible and the parsed meter-local ordering selected index zero. The action succeeded and cleanup was clean. The existing GD82/ForaCare device and single uric-acid entity remained; the entity became available and showed the selected mg/dL state. No duplicate appeared. The private result's value and timestamp, screenshot, MAC, serial, and System ID are intentionally absent from the repository.

Stage 7H is **complete for its authorized scope**: exact count-two indexes `0 → 1`; exact count-four indexes `0 → 1 → 2 → 3`; count-four selection by strictly later minute-precision meter-local time when two primaries qualify; equal-minute ties fail closed. Manual refresh only. Counts above four, history import, recorder/statistics backfill, persistent record identity/dedup/resume, automatic triggers, mixed-analyte support, and meter-state automation remain out of scope. Meter-local time has unknown timezone and the meter clock can affect apparent order; raw-index magnitude is never a chronology rule.

Full suite: **369/369 passed** (baseline 369). Compileall, tabnanny, five JSON/YAML parses, diff checks, and privacy/health/identifier/artifact/path/proprietary-source audits passed. Only Markdown changed; no physical operation was performed by Codex during this closure.

**Exact next proposed gate:** Stage 8 offline/synthetic/design-first hardening and product-behavior review. Stage 9 proxy-path validation and later release gates remain pending. Do not begin them from this closure.

## Previous Stage 7G2 checkpoint

## Stage 7G2 physical closure and offline unit-format review

Starting checkpoint: clean public `main` at `623c343429c26f931b2885252b8af56d6fda19db` (`feat: expose private chronology probe values`) on 2026-09-27 (Europe/London). The task changed only the Markdown files listed in `CURRENT_STATUS.md`. This is a **pre-commit observation**; verify and report post-commit/push state separately.

[Stage 7G's bounded physical result](docs/STAGE7G_PRIMARY_CHRONOLOGY_PROBE.md) confirmed count four, project identity, two valid General uric-acid primaries, and clean cleanup. Raw primary 0 was later than raw primary 2 by their parsed meter-local times in that real snapshot. Stage 7G is **complete for this bounded scope**. Highest raw index was not newest there, but arbitrary-count ordering, clock reset, buffer wrap, and durable record identity remain unresolved. The user also saw history-arrow browsing stop the Bluetooth light after normal manual ON had produced flashing light; the internal reason is unknown.

[The two-version app conversion review](docs/URIC_ACID_UNIT_CONVERSION.md) finds `mg/dL × 59.48 ÷ 1000` followed by two-decimal `FLOOR` formatting in the uric-acid record-display path; settings/range thresholds use a separate `HALF_UP` formatter. This app behavior explains why distinct base records can share one two-decimal mmol/L display text. The physical meter firmware's exact arithmetic remains unproven. No real value, date, time, private path, proprietary source, identifier, or capture was added to Git.

[The Stage 7F reassessment](docs/STAGE7F_MINIMUM_PRODUCTION_SYNC_REASSESSMENT.md) conditionally supports a separately authorized manual-only current-state refresh at exact raw counts two/four. At count four, select the strict maximum naive meter-local time among eligible General uric-acid primaries only after complete fixed-plan validation; ties fail closed. A meter-clock change remains a residual limitation. A second metadata query can be deferred for the first manually ON/no-arrow procedure because it cannot guarantee atomicity and its placement lacks physical validation. The sensor remains unavailable; Stage 7H production implementation has not begun.

Files changed: see `CURRENT_STATUS.md`. Full verbose suite: **353 passed** (baseline 353). Compileall, tabnanny, four JSON parses, one YAML parse, `git diff --check`, and `git diff --cached --check` passed. Changed-file/added-line privacy and tracked artifact scans found no prohibited data or file. The staged diff was reviewed; only Markdown changed.

**Exact next gate:** separately authorize Stage 7H strict manual current-state uric-acid refresh for raw counts two/four with full fixed-plan validation, meter-local timestamp selection and equal-minute tie rejection, previous-state retention on failure, and no history import, persistence, resume, polling, or automatic trigger.
