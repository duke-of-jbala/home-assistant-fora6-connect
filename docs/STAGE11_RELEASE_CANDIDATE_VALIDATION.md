# Stage 11 — release candidate validation

**Status: complete for the applicable real HACS custom-repository and GD82
manual-refresh gate.** The user observed a successful HACS download over the
previous manual component installation, successful Home Assistant restart and
integration reload, preserved configured objects, and a real manual refresh
with direct connection-specific ESPHome proxy Source evidence. HACS did not
offer a safe re-download option; versioned update behavior remains untested.

## Baseline and evidence classes

The clean `main` checkpoint entering this gate was
`a7a1d37c805af6e5567efefaf837e88a6bdbfc9b` (`docs: close Stage 10 HACS readiness`);
`origin/main` matched. The user reports that HACS is installed but the working
FORA component was copied manually before the controlled HACS test. The later
user-supplied real observations are recorded below without health fields or
device identifiers.

| Evidence | Result | Limit |
| --- | --- | --- |
| Repository/package | One `custom_components/fora6_connect/` package, root `hacs.json`, valid manifest/resources, MIT license and public metadata. | Does not prove HACS UI installation. |
| Synthetic | 375 unit tests pass; isolated package copy resolves 27 Python modules and bundled resources. | Does not prove a physical BLE path. |
| Official validators | Fresh [HACS and hassfest run](https://github.com/duke-of-jbala/home-assistant-fora6-connect/actions/runs/36355057262) passed on the exact baseline SHA. | Validates the repository, not the user's installation. |
| Earlier physical evidence | Stage 7H manual count-four refresh and Stage 9 direct Bluetooth Connections Source observation succeeded through the Lounge Atom Lite proxy. | Predates the HACS-managed installation. |
| Stage 11 HACS/Home Assistant | User reported HACS download success, same FORA config entry, one GD82 device, one uric-acid entity, unavailable-before-refresh state after restart, working action selector, successful entry reload, and no relevant startup/reload log errors. | User observation; no config-entry or device identifier is published. |
| Stage 11 physical BLE | User reported a successful count-four manual refresh, existing sensor update, null action error stage/code, empty cleanup errors, no duplicate device/entity, and no relevant HA log errors. Bluetooth Connections named the Atom Lite ESPHome proxy as the active FORA connection Source, and the row disappeared after completion. | Direct connection-specific evidence for this HACS-installed run only. |

Local static checks also passed: compileall, tabnanny, four JSON/two YAML/one
TOML parses, both whitespace diff checks, changed-Markdown privacy scan,
tracked-artifact scan, and a no-runtime-diff review. `pytest` is not installed
locally; the established `unittest` suite is the regression gate. None of
these tests exercised the user's HACS UI or meter.

Current [HACS repository requirements](https://www.hacs.xyz/docs/publish/integration/)
allow a custom integration on the default branch without a GitHub release.
[HACS version guidance](https://www.hacs.xyz/docs/publish/start/) uses a
published release tag for release-based versions, or the default-branch commit
when no release exists. A tag alone does not create a HACS release version.
[Home Assistant's manifest guidance](https://developers.home-assistant.io/docs/creating_integration_manifest/)
requires a custom integration version recognized by AwesomeVersion.

## Candidate version and release policy

Keep manifest version `0.1.0` during this real custom-repository install test.
Changing it only to force an update indication would obscure what HACS
actually installed. No tag or release is needed for the default-branch test.
For a future explicitly authorized RC publication, use one consistent
prerelease version in manifest, Git tag, and GitHub release; `1.0.0-rc.1` is
the proposed SemVer spelling, subject to validator and HACS acceptance on the
candidate commit. That publication is not authorized by this gate. A HACS
**re-download of the default branch** can test package replacement; it is not
evidence that a release-based update notification works. Versioned-update
behavior remains untested without a published RC release.

## Controlled manual-copy to HACS handoff

HACS [does not adopt existing local elements by scanning the filesystem](https://www.hacs.xyz/docs/faq/existing_elements/);
it must download this repository again. Both methods use Home Assistant's
`custom_components/fora6_connect/` location. The user's existing config entry
and device/entity registrations are Home Assistant configuration state, not
files within that component folder.
The following is the controlled procedure and retained validation recipe. The
user reported the successful download, restart, reload, and refresh checks;
backup details and exact registry IDs were kept private and are not asserted
here:

1. Record privately the current FORA config-entry count and identity, device
   count and association, and uric-acid entity ID. Make a normal Home Assistant
   backup. Keep a private copy of the current component folder **outside**
   `custom_components/` so Home Assistant cannot load a duplicate copy. Do
   not share the backup or identifiers in public issues.
2. In HACS, add `https://github.com/duke-of-jbala/home-assistant-fora6-connect`
   as a **Custom repository → Integration** and download the default branch.
   Do not delete the existing FORA integration/config entry. If HACS refuses
   because files already exist, stop and record its sanitized error; do not
   manually delete the working entry or guess at HACS metadata.
3. Confirm HACS lists FORA 6 Connect as downloaded, then restart Home
   Assistant. Check the FORA integration loads without component import,
   manifest/schema, deprecated-API, or duplicate-unique-ID errors.
4. Confirm the **same** config entry, one GD82/ForaCare device, one uric-acid
   entity with its prior entity ID and device association, Bluetooth connection
   metadata, no false serial number, and no duplicate Add card. The sensor is
   expected to start unavailable because current measurement state is
   intentionally process-local. Check Developer Tools → Actions for
   `fora6_connect.refresh_current_uric_acid`, its configured-entry selector,
   and no required MAC field. Reload the entry once if Home Assistant offers
   that control; expect the same unavailable-before-refresh state and no
   duplicate object.
5. With the GD82 normally ON, do not press its history arrows. Run the manual
   action targeting the existing entry. Verify successful supported count two
   or four, `sensor_updated: true`, null `error_stage`/`error_code`, and empty
   `cleanup_errors`. Confirm the same sensor updates. During the connection,
   use Home Assistant Bluetooth → Connections to identify the active FORA row
   and its ESPHome proxy **Source**; a successful refresh alone is not route
   proof. Confirm the row disappears after disconnect. Keep the response's
   health value, meter-local time, and address private.
6. In HACS, re-download the same default branch once if the UI offers this
   safely. In this tested HACS UI, no safe re-download option was offered, so
   no replacement/update test was performed. Do not create a tag or release
   to manufacture an update.
7. Do not uninstall the working component merely for completeness. Removal
   risks the user's configured installation and adds little beyond the
   re-download/restart test. A later isolated Home Assistant instance can
   exercise uninstall/reinstall without disturbing this meter's registry.

If the HACS handoff fails, use the private Home Assistant backup or the saved
component folder to restore the known working manual build, then restart.
Keep the config entry/device/entity; investigate the exact error before any
other change. The backup/rollback has not been physically exercised in this
gate.

## Real result, limitations, and pass decision

The real run established HACS download, successful restart and entry reload,
the same config entry, one device/entity, initial unavailable state, a working
existing-entry action selector, a successful supported count-four manual
refresh, the existing sensor update, and direct proxy Source evidence. The
user observed no relevant startup, reload, or refresh log error. The
connection row's disappearance after the action is consistent with expected
disconnect; the action also reported empty cleanup errors. The user did not
report a duplicate device or entity. Exact registry IDs, private selected
health fields, and screenshots were not collected into Git.

The test did **not** establish HACS release-based update notification or
same-branch package replacement, because no safe re-download option was
offered. It did not test uninstall/reinstall, a new config entry on a clean
Home Assistant instance, every Bluetooth scanner/proxy, count two after HACS
installation, or counts above four. These limits are documented rather than
treated as a mandatory blocker: the default-branch HACS installation and
the already validated manual product path worked, while a future published
release can be independently checked under separate authorization. No RC or
v1 release is created here.

The current compatibility assumption is Home Assistant with supported
Bluetooth APIs and an active-connection-capable local adapter or ESPHome
proxy. No minimum Home Assistant version is declared because this gate has
not established an exact minimum API version. The manifest has no Python
`requirements`; `bluetooth` and `bluetooth_adapters` are Home Assistant
integration dependencies. Stage 10's HACS/hassfest checks and Stage 9's
tested Atom Lite path remain the bounded evidence.

## Proposed release candidate notes — draft only

FORA 6 Connect GD82 custom integration for Home Assistant. Bluetooth
discovery and config flow create one GD82/ForaCare device with one native
mg/dL uric-acid sensor. The manually invoked
`fora6_connect.refresh_current_uric_acid` action supports only raw counts
two and four. A real count-four run through an M5Stack Atom Lite ESPHome
Bluetooth Proxy has been validated. Run the action with the meter normally
ON and without browsing its history. Install as a HACS custom Integration;
restart Home Assistant after download. Health value and meter-local time in
the action response are private. There is no background refresh, history
import, persistent deduplication/resume, recorder backfill, count-six-plus
support, or other analyte entity. The printed proprietary serial remains
unresolved. This text is not published release notes.

## Closure and next gate

Stage 11 is **complete for its applicable release-candidate validation
scope**. No mandatory integration or packaging blocker remains in the tested
HACS custom-repository route. A versioned HACS release-update test is not
claimed. The exact next proposed gate is separately authorized Stage 12
v1.0.0 release preparation/publication, including a release version, final
release-note review, and explicit approval before tag or release creation.
Stage 8H is optional and has not started.
