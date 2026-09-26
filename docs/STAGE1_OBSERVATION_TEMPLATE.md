# Stage 1 private observation template

**Blank template only.** Copy a completed version to private storage **outside this repository**. Do not commit actual Bluetooth addresses, meter identifiers, personal measurements, raw captures, Home Assistant credentials, or unredacted logs. Use “not shown” when a UI field is unavailable; do not guess it. See [CAPTURE_GUIDE.md](CAPTURE_GUIDE.md).

## A. Environment

- Observation date, local time zone, and observer: [private]
- Home Assistant version and installation type: [record privately]
- Bluetooth panel path and displayed UI labels: [record privately]
- Meter model/label and state during observation: [record privately]
- Capture method and duration: [record privately]

## B. ESPHome proxy

- Hardware: M5Stack Atom Lite (user-supplied description; verify displayed device details)
- Proxy/scanner name and area: [record privately]
- Availability/state: [record privately]
- Scanning mode (Auto/Active/Passive, as displayed): [record privately]
- Active/GATT connection capability shown: [yes/no/not shown]
- Available/total connection slots if exposed: [record privately or not shown]
- ESPHome version if visible: [record privately or not shown]
- Other scanners in range: [record privately]

## C. Advertisement observation #1

- Observation timestamp and time zone: [private]
- Candidate local label: [private label; no raw address in Git]
- Local name: [private or not shown]
- Bluetooth address/identifier: [private, never commit]
- RSSI and scanner/source relationship: [private or not shown]
- Atom Lite received this advertisement: [yes/no/not shown]
- Connectable status: [yes/no/unknown]
- Advertised service UUIDs: [private or not shown]
- Service data: [private or not shown]
- Manufacturer ID/data: [private or not shown]
- TX power: [private or not shown]
- Other displayed fields: [private or not shown]
- Meter state and any relevant timing: [private]

## D. Advertisement observation #2

- Observation timestamp and time zone: [private]
- Candidate local label: [same private label if justified]
- Local name: [private or not shown]
- Bluetooth address/identifier: [private, never commit]
- RSSI and scanner/source relationship: [private or not shown]
- Atom Lite received this advertisement: [yes/no/not shown]
- Connectable status: [yes/no/unknown]
- Advertised service UUIDs: [private or not shown]
- Service data: [private or not shown]
- Manufacturer ID/data: [private or not shown]
- TX power: [private or not shown]
- Other displayed fields: [private or not shown]
- Meter state and any relevant timing: [private]

## E. Address-stability comparison

- Same identifier across observations: [yes/no/unknown]
- Observation interval and meter state comparison: [private]
- Address rotation or platform pseudonym suspected: [observed basis or unknown]

## F. Candidate identification confidence

- Observed facts supporting this candidate: [list]
- Alternative devices or explanations: [list]
- Interpretation/confidence and reasons: [state separately from facts]
- Why the documented UUID pair is insufficient on its own: [record]

## G. Connectability

- Candidate advertisement connectable flag: [yes/no/unknown]
- Scanner/proxy active GATT capability: [yes/no/not shown]
- Connection Monitor observation: [existing connection/source or none shown]
- Reachability conclusion: [not tested in Stage 1A]

## H. GATT inventory — blank private template

The real Stage 1B Home Assistant inventory is recorded in [PROTOCOL.md](PROTOCOL.md). Use this blank section only for an additional, separately authorized private observation; do not fill it from documentation alone.

## I. Passive notifications — not yet collected

Subscription requires separate explicit authorization. No FORA application writes during Stage 1. Keep any future raw notification bytes private.

## J. Privacy/sanitization review

- Raw identifiers/measurements/logs remain outside Git: [confirm]
- Fields redacted for a shareable summary: [list]
- Sanitization transformations and possible effect on interpretation: [list]
- Public fixture created: [no for Stage 1A]

## K. Open questions

- [List unanswered observations without guesses.]

## L. Evidence provenance

- Home Assistant screen/view and exact displayed field labels: [record]
- Observation date/time, software versions, scanner source, and meter state: [record]
- Private source file/location and access restrictions, if any: [record privately; do not commit a path revealing personal data]
- Observed fact versus interpretation for each conclusion: [record]
