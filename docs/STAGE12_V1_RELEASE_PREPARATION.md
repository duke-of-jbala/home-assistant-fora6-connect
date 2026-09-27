# Stage 12 — v1.0.0 release preparation

**Phase A only.** This record prepares and validates the first stable release.
No `v1.0.0` tag, GitHub release, or release asset is created in Phase A.
Phase B requires separate explicit user authorization after reviewing the
Phase A commit and report.

## Baseline and evidence boundary

The clean public `main` baseline was
`9cb9a22c46c9c1842eb7916c6edcb02be322a3be` (`docs: close Stage 11 HACS validation`),
with `origin/main` matching. Stage 11 supplied real HACS custom-repository
installation, restart/reload, stable entry/device/entity counts, and a
successful count-four manual refresh through an Atom Lite proxy identified
as the active Bluetooth connection Source. These are user-supplied physical
observations. Unit tests and package validators remain separate evidence.
HACS versioned update notification and uninstall/reinstall were not tested.

## Version and distribution decision

The custom integration manifest changes from development `0.1.0` to stable
`1.0.0`. The proposed Git tag is **`v1.0.0`** and the proposed GitHub release
title is **`FORA 6 Connect v1.0.0`**. The release would be public, stable,
non-prerelease, and marked latest. The leading `v` is only a tag convention;
[AwesomeVersion](https://github.com/ludeeus/awesomeversion) exposes the
version string without that prefix. [Home Assistant requires a valid custom
integration manifest version](https://developers.home-assistant.io/docs/creating_integration_manifest/).

[HACS uses a published release tag as its remote version](https://www.hacs.xyz/docs/publish/start/);
a tag by itself is insufficient. [HACS's normal integration layout](https://www.hacs.xyz/docs/publish/integration/)
uses `custom_components/fora6_connect/` directly from the tagged repository
and does not require a custom ZIP. Root `hacs.json` remains the minimal
supported `name` metadata; no `zip_release` or `filename` key is added.
After an approved GitHub release, HACS is expected to offer that release
version alongside the default branch. This expected update behavior must be
checked after publication; Stage 11 did not observe a versioned update.

The exact release body is [RELEASE_NOTES_V1.0.0.md](RELEASE_NOTES_V1.0.0.md).
The changelog has a concise 1.0.0 section and retains the detailed stage
history separately. The README describes the user install, manual action,
restart behavior, and scope limits without claiming automatic history sync.

## Release-facing claims and limits

Supported v1 product behavior is one GD82/ForaCare device and one native
mg/dL uric-acid sensor, Bluetooth discovery/config flow, and explicit manual
refresh for exactly two or four raw slots. A count-four tie at meter-local
minute precision fails closed. A later failed refresh retains valid process
memory; restart/reload begins unavailable until another successful action.
The ESPHome proxy claim is bounded to real tested Atom Lite sessions, including
the post-HACS run. Local Bluetooth is a supported Home Assistant transport
path, but no claim is made for every adapter or proxy.

The release does **not** provide count-six-plus traversal, general history
import or exposure, persistent deduplication/resume, recorder/statistics
backfill, automatic/startup/advertisement/post-measurement refresh, polling,
other analyte entities, or proprietary printed-serial retrieval. The app's
mmol/L formatting evidence is not a claim about meter firmware or the HA
sensor, which remains in mg/dL. Private action responses may contain the
selected value and meter-local time; these must not enter public Git or logs.

## Legal, dependencies, and privacy

The repository has an MIT [LICENSE](../LICENSE), reflected in the README and
GitHub metadata. The local [brand files](BRANDING.md) are documented as
original neutral placeholders, not copied ForaCare artwork or an official
endorsement. No proprietary app, source decompilation, raw capture, manual,
or manufacturer artwork is bundled. This is a repository content audit, not a
legal opinion about the FORA name or third-party rights.

The manifest declares Home Assistant `bluetooth` and `bluetooth_adapters`
integration dependencies and no extra Python `requirements`. The runtime
imports `bleak_retry_connector` through Home Assistant's existing BLE stack;
no development-only library or repository-root module is distributed. No
minimum HA version is invented. The release privacy scan checks tracked files,
release notes, fixtures, metadata, logs, credentials, private identifiers,
and artifacts; the action's private result remains the only intended health
value/time exposure beyond normal sensor state.

## Validation record

On the modified Phase A tree, the full unittest suite passed **375/375**;
compileall and tabnanny passed. All four JSON, two YAML, and one TOML tracked
resources parsed; manifest key order was unchanged from the Stage 11
hassfest-passing baseline. An isolated copy
of the 27-module component passed its manifest/resource/relative-import check.
The diff whitespace checks, tracked-artifact scan, and privacy, identifier,
credential, logging, automatic-sync, and history-import reviews passed. The
only component change is the manifest version. MAC-shaped strings in tracked
source/tests were reviewed as sentinel or synthetic fixture values; the lone
IPv4-shaped documentation hit was a software version. No real identifier,
health value/time, private path, credential, raw capture, or prohibited binary
artifact was introduced. Final staged checks and official HACS/hassfest jobs
on the pushed Phase A commit are separately verified in the task report.
Package simulation and validators do not replace Stage 11's real HACS install
and physical proxy evidence.

## Phase B execution recipe — proposed, NOT executed

After explicit approval, from a clean `main` checkout:

1. Verify the approved Phase A SHA is both `HEAD` and `origin/main`; confirm
   there is no existing `v1.0.0` tag or GitHub release. Recheck manifest
   `1.0.0`, the release-note body, the full tests, and official CI.
2. Create an **annotated** tag pointing to the approved SHA:
   `git tag -a v1.0.0 -m "FORA 6 Connect v1.0.0" <approved-phase-a-sha>`.
3. Push only that tag: `git push origin v1.0.0`.
4. Publish the prepared body from the existing remote tag:
   `gh release create v1.0.0 --verify-tag --title "FORA 6 Connect v1.0.0" --notes-file docs/RELEASE_NOTES_V1.0.0.md --latest`.
   Do not pass `--prerelease` or an asset path.
5. Verify the release is published, latest, non-prerelease, and points to the
   approved SHA. Confirm HACS sees the release/version when its metadata
   refreshes, then check a controlled HACS update and Home Assistant restart
   without deleting the existing config entry. Keep private health data out
   of the public report.

If a packaging defect appears after publication, prefer a corrected follow-up
patch release such as `v1.0.1`; do not rewrite or replace a published tag.
Withdrawing or drafting a release may be appropriate for a severe distribution
error, but only after an explicit decision based on the actual defect.

## Stop point

Phase A ends with a clean pushed preparation commit and a report of all gates.
No tag, release, or post-v1 feature work is authorized by Phase A. The exact
next decision is **authorize the v1.0.0 tag/release, request a narrow
correction, or hold release**.
