# Stage 11 — release candidate validation

**Status: pending real HACS and Home Assistant validation.** Repository and
synthetic checks alone cannot establish that HACS installed the integration in
the user's Home Assistant, that the existing registry objects survived the
handoff, or that a subsequent BLE connection used the ESPHome proxy.

## Baseline and evidence classes

The clean `main` checkpoint entering this gate was
`a7a1d37c805af6e5567efefaf837e88a6bdbfc9b` (`docs: close Stage 10 HACS readiness`);
`origin/main` matched. The user reports that HACS is installed but the working
FORA component was copied manually. No Stage 11 HACS UI installation, restart,
reload, update, uninstallation, or physical meter operation has yet been
reported.

| Evidence | Result | Limit |
| --- | --- | --- |
| Repository/package | One `custom_components/fora6_connect/` package, root `hacs.json`, valid manifest/resources, MIT license and public metadata. | Does not prove HACS UI installation. |
| Synthetic | 375 unit tests pass; isolated package copy resolves 27 Python modules and bundled resources. | Does not prove a physical BLE path. |
| Official validators | Fresh [HACS and hassfest run](https://github.com/duke-of-jbala/home-assistant-fora6-connect/actions/runs/36355057262) passed on the exact baseline SHA. | Validates the repository, not the user's installation. |
| Earlier physical evidence | Stage 7H manual count-four refresh and Stage 9 direct Bluetooth Connections Source observation succeeded through the Lounge Atom Lite proxy. | Predates the HACS-managed installation. |
| Stage 11 physical evidence | Pending. | Required before closure. |

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
The following is a user-run procedure, not a result already observed:

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
   safely. Restart, verify the same entry/device/entity and action, and review
   logs again. This tests HACS-managed replacement/reload, not versioned
   update detection. Do not create a tag or release to manufacture an update.
7. Do not uninstall the working component merely for completeness. Removal
   risks the user's configured installation and adds little beyond the
   re-download/restart test. A later isolated Home Assistant instance can
   exercise uninstall/reinstall without disturbing this meter's registry.

If the HACS handoff fails, use the private Home Assistant backup or the saved
component folder to restore the known working manual build, then restart.
Keep the config entry/device/entity; investigate the exact error before any
other change. The backup/rollback has not been physically exercised in this
gate.

## Review and pass criteria

The real run must establish HACS ownership/download, successful restart and
one reload if supported, stable config entry/device/entity IDs, initial
unavailable state, correct action UI, manual refresh, and direct proxy Source
evidence. Review sanitized HA logs for import, schema, deprecated API,
Bluetooth, cleanup, duplicate-ID, and private-data logging errors. Separate
any upstream HACS/HA/ESPHome warning from an integration defect. Do not
publish raw logs, screenshots, addresses, values, or timestamps.

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

## Closure gate

Stage 11 remains **pending real HACS/manual validation** until the user
reports the installation, restart/reload, object counts/associations, action,
manual refresh, proxy Source, and sanitized log observations above. A
versioned HACS release-update test is not claimed. No Stage 8H or Stage 12
work follows automatically.
