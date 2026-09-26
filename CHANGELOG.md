# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [Unreleased]

### Added
- Initial Home Assistant FORA 6 Connect integration project structure.
- Initial architecture and development documentation.
- Initial BLE protocol discovery framework and roadmap.
- Durable master roadmap, repository status, and Codex handover workflow.
- Stage 1A Home Assistant Bluetooth observation guide and blank private capture template.
- Sanitized Stage 1 real-device discovery, GATT, and Home Assistant/ESPHome proxy observations with provenance and a controlled next gate.
- Stage 1 controlled proxy retest: Home Assistant detected FORA through Lounge in Active mode after the scan override was removed and firmware reflashed; Auto-mode freshness remains unconfirmed.
- Development-only Stage 1B Home Assistant action for fresh on-demand discovery, read-only GATT inventory, and privacy-safe response; hardware validation pending.

### Changed
- Standardized the project and integration name to FORA 6 Connect and the domain to `fora6_connect`.
- Revised the Stage 1B development probe to wait for a newer address-targeted advertisement through Home Assistant after real attempts stopped at the previous fresh-advertisement gate; no Home Assistant GATT connection or FORA operation occurred in those attempts.
- Separated the Stage 1B probe's general advertisement lookup from connectable-device resolution after the installed targeted-wait build stopped at its connectable-only candidate gate; no targeted wait or Home Assistant GATT connection occurred in that retest.
- Added a private runtime address field to the Stage 1B development probe after a real general-cache retest found 214 devices, zero FORA name matches, and two connectable scanners. Automatic discovery remains deferred; no GATT connection or FORA operation occurred in that retest.
- Corrected the Stage 1B evidence source: a name with five trailing NULs, connectability, BLE flags, advertised Glucose/Device Information services, and manufacturer-data presence were seen in Home Assistant's Advertisement Monitor popup, not returned by the probe. The probe now removes trailing NUL padding when comparing a live packet name; whether its targeted wait receives such a packet remains unverified.
