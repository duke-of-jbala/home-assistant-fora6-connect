# Stage 10 — HACS packaging and installation readiness

**Status: complete for repository packaging and validation.** The corrected
package at `cc06e9666fbb305a7433509f5ec7706b911db8f1` passed both
[HACS Integration validation and Home Assistant hassfest](https://github.com/duke-of-jbala/home-assistant-fora6-connect/actions/runs/36354523910).
The controlled HACS UI install/update is the next, separately authorized
Stage 11 exercise. No tag or release was created.

**Scope:** Repository/package validation for the existing GD82 integration. A
validator-driven config-entry-only schema declaration is the sole Python change;
it adds no manual refresh, protocol, discovery, identity, coordinator, sensor,
or Bluetooth behavior. The previous real manual refresh and Lounge Atom Lite proxy results
remain the physical evidence; Stage 10 checks are repository and synthetic
checks. A clean HACS UI install/update on a separate Home Assistant instance
has not yet been observed and belongs to Stage 11 release-candidate validation.

## Current requirements and evidence sources

Reviewed 2026-09-27 against the current [HACS general publication rules](https://www.hacs.xyz/docs/publish/start/),
[HACS integration repository rules](https://www.hacs.xyz/docs/publish/integration/),
[custom-repository procedure](https://www.hacs.xyz/docs/faq/custom_repositories/),
[HACS validation action](https://www.hacs.xyz/docs/publish/action/),
[Home Assistant manifest guidance](https://developers.home-assistant.io/docs/creating_integration_manifest/),
[custom integration localization guidance](https://developers.home-assistant.io/docs/internationalization/custom_integration/),
[Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), and
[local custom brand support](https://developers.home-assistant.io/docs/core/integration/brand_images/).

| Classification | Requirement or recommendation | Repository finding |
| --- | --- | --- |
| Required for HACS integration | Public GitHub repository, one integration under `custom_components/<domain>/`, all runtime files inside it, manifest with domain/name/documentation/issue tracker/codeowners/version, root `hacs.json` name, README, brand icon | Present; package simulation checks the component copy. |
| Required for custom Home Assistant integration | Valid manifest version and domain, valid resources and component imports | Manifest is `fora6_connect`, with one development version; resources and isolated copy are checked below. |
| Repository metadata | Description, issues, and topics | Authenticated GitHub metadata check found all three present; MIT license is present. |
| Recommended | HACS repository action, hassfest, releases for selectable HACS versions | CI workflow added. Releases are deliberately deferred until explicit Stage 11/12 authorization. |
| Optional polish | Further translations, official manufacturer artwork, default HACS listing, security/issue templates | Deferred. Current local artwork is original and neutral; no proprietary asset is copied. |

The HACS **custom repository** route is the distribution target for now. Being
listed among HACS defaults has extra publication checks, including a full
GitHub release, and is not claimed here. HACS can use the default branch when
no release exists. A tag alone is insufficient for HACS's release-based update
version. No tag or release is created at Stage 10.

## Package and metadata audit

- Exactly one domain directory exists under `custom_components/`, with Python,
  manifest, service descriptions, English translations, and local brand files
  inside it. The repo-root documentation and tests are not runtime imports.
- `hacs.json` contains the supported required `name` key. No root-content or
  zip-release override is needed for the standard integration layout.
- The manifest retains the physically validated Bluetooth matcher, `device`
  integration type, config flow, project URLs, and current dependencies. The
  `local_polling` classification describes local pull communication; actual
  updates remain **manual only**, with no polling scheduler. No cloud,
  broader-analyte, or historical-sync support is claimed.
- The first pushed HACS job passed. Hassfest found one manifest key-order error
  and one missing config-schema warning. The follow-up sorts manifest keys
  without changing values and declares the supported config-entry-only schema
  for an integration that is set up through config entries. A synthetic setup
  test checks the declaration; the original service behavior is unchanged.
- `bluetooth_adapters` and `bluetooth` are Home Assistant integration
  dependencies used by the existing discovery/connection path. The Python
  `requirements` list is empty: the external BLE connector used by this
  component is supplied with Home Assistant, and no development tool is
  shipped as a runtime package.
- English `translations/en.json` carries complete config/action text; every
  config key from `strings.json` has a matching English translation. Custom
  integrations use the translation file at runtime. The stale Stage 2F
  “testing paused” wording was removed from action descriptions without
  changing any action schema or behavior.
- The local `brand/icon.png` and logo files meet current custom-brand
  placement. They are original temporary artwork; official ForaCare branding
  and any upstream brands submission are not required for this custom repo.
- GitHub metadata inspection found the public main branch, description,
  topics, issues enabled, active repository, and MIT license. Security/privacy
  bug reports should use GitHub Issues with the README redaction guidance.

## Version and update policy

`custom_components/fora6_connect/manifest.json` now uses **`0.1.0`** as the
single development version in the distributable default branch. The old
`0.0.0` was a bootstrap placeholder. The manifest is the integration version
seen by Home Assistant; the GitHub release tag, when one exists, is the HACS
remote update version. The Stage 10 proposal was to choose a SemVer release
candidate such as **`1.0.0-rc.1`**. The later [Stage 11 decision](STAGE11_RELEASE_CANDIDATE_VALIDATION.md)
keeps `0.1.0` for controlled default-branch HACS installation; an RC version,
tag, and published release require separate authorization and validation.
Stage 12 may use `1.0.0` only after RC acceptance and explicit release
approval. The tag and published GitHub release should use the same version
string as the manifest. Development commits without a release remain
available to custom-repository users from the default branch, which HACS
identifies by commit. Stage 10 creates no tag or release.

## Install, update, and removal behavior

[README installation instructions](../README.md) now give prerequisites,
HACS custom-repository category **Integration**, download, restart, normal
Bluetooth discovery/config flow, and the manual directory-copy fallback.
They state the exact meter procedure and supported counts, the private action
response, process-local state reset after restart, and the absence of history
import and automation. HACS installs to Home Assistant's
`custom_components/fora6_connect/` path.

HACS update and manual replacement both require restarting Home Assistant to
load changed Python. The existing config entry/entity should persist; users
should verify them after an update. Removal guidance first removes the Home
Assistant config entry, then uninstalls HACS/manual files and restarts.
Recorder data is governed by Home Assistant's own retention/deletion controls;
this integration does not implement recorder cleanup.

## Validation and remaining release gate

The repository's full 374-test baseline plus one schema regression test, compileall, tabnanny, all JSON/YAML
parses, whitespace, privacy/identifier/logging/automation/history/artifact
reviews, and a temporary-directory package-copy/relative-import simulation are the
local gates. The new GitHub workflow runs the official HACS repository action
for category `integration` and Home Assistant hassfest on push, PR, and manual
dispatch with immutable action revisions and read-only permissions. These
external validators require GitHub Actions; local availability alone does not
count as a pass. Both official jobs passed on the corrected package commit
above. The first packaging commit's HACS job passed while hassfest found one
manifest error and one config-schema warning; the follow-up resolved them.

The temporary-directory simulation copies only the integration directory into
`custom_components/fora6_connect/`, checks that the manifest/resources parse,
checks local relative-import references and bundled files, and confirms no repository-root
runtime path or private artifact is required. It is not a real Home Assistant
UI install, HACS network download, or new physical BLE test.

**Stage 11 entry criteria:** HACS and hassfest checks pass on the committed
Stage 10 version; an isolated copy and the full local quality gate pass; then
run a separately authorized clean HACS custom-repository install, update, and
restart exercise on a controlled Home Assistant instance. Review the release
candidate's version/tag/release notes and privacy once more. Stage 8H history
exposure is optional and is not part of this release path.
