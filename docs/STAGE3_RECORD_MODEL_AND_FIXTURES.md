# Stage 3 — offline TD4183 record model and synthetic fixtures

**State:** Complete for the authorized offline scope. No Bluetooth command, physical test, Home Assistant action result, synchronization, entity, or private health-data persistence was added.

## Purpose and evidence boundary

Stage 2G established the two validated response parts and their field map in [the schema review](STAGE2G_TD4183_RECORD_SCHEMA.md). Stage 3 pairs one parsed `0x25` part with one parsed `0x26` part in pure Python. The two command-specific parsers validate frame length, prefix, response marker, checksum, and command echo before combination. The combiner accepts only those typed parts. Evidence establishes their pairing, but no additional cross-part relation, stable record ID, or production deduplication rule; none is imposed.

The immutable `TD4183Record` in `models.py` retains both parts, including their opaque payload bits. Its properties expose meter-local time, transmitted status, analyte code and known enum if any, category, raw wire integer, auxiliary byte, and app code number. The latter is byte 5's low six bits and **overlaps** the analyte selector; it is not a separate wire field. The model deliberately has no unit, timezone, sync time, identifier, clinical interpretation, or generic displayed-value property.

| Model field or behavior | Evidence |
| --- | --- |
| Parsed `0x25`/`0x26` roles and paired call path | Static analysis in both retained app versions; Stage 2F live response roles corroborated |
| Meter-local year/month/day/hour/minute and transmitted flag | Static analysis in both versions; private capture fields were calendar-valid |
| Raw integer, analyte selector, category, auxiliary byte, overlapping app code number | Static analysis in both versions; private capture corroborated uric-acid/General and hematocrit/QC classifications |
| Invalid `0xFFFF` raw sentinel | Static analysis in both versions; private QC companion corroborated |
| Uric-acid raw / 10 | Prior Stage 2C private import evidence, applied only after `0x26` identifies uric acid and raw is valid |
| Unknown selectors remain `analyte=None`; QC stays a distinct category | Evidence-preserving model policy |

`raw_value` preserves the exact wire integer, including `0xFFFF`; `is_valid_value` and `usable_raw_value` make the sentinel unavailable as a numeric measurement. `uric_acid_scaled_value` returns a `Decimal` only for a positively identified, valid uric-acid record. It returns `None` for all other analytes, unknown selectors, and invalid raw values. QC is available as `is_qc`, with no policy to exclude it from a future product layer.

`meter_local_time` retains minute-precision wall-clock fields. Its optional Python `datetime` is naive (`tzinfo=None`), with no inferred timezone, UTC conversion, DST rule, seconds from the meter, or sync timestamp. Parsing rejects invalid calendar fields instead of normalizing them.

## Synthetic fixture construction and coverage

`tests/fixtures_td4183.py` defines **ten entirely synthetic named cases** and a builder for checksummed `0x25`/`0x26` response frames. It packs artificial date/time fields, analyte and category selectors, the overlapping low code bits, and raw values according to the Stage 2G map, then computes the observed modulo-256 checksum. No fixture is a captured GD82 response or a redaction of one. Tests also build an artificial, checksummed month-zero frame to exercise parser rejection.

The corpus covers uric acid/General/valid, uric acid/QC/valid, ketone/General, hematocrit/QC/`0xFFFF`, unknown analyte selector, AC, PC, transmitted true and false, the minimum representable valid timestamp, a future synthetic timestamp, and uric acid/`0xFFFF`. The model tests check every pair's command IDs, response markers, and checksum. Fixture numbers and dates were chosen for tests, not copied from private captures.

## Intentionally unresolved

Reserved `0x25` bits, auxiliary-byte physical meaning or unit, app code number's independent meaning, scaling and units for other analytes, exact AC/PC clinical meaning, timezone, wider multi-parameter and meter states, and production record identity/deduplication remain unknown. The model preserves available raw fields without assigning these meanings.

**Next gate:** separately authorize Stage 4 production Bluetooth transport design and implementation. That gate must first decide the exact supported behavior from existing protocol evidence and Home Assistant APIs. Stage 3 does not authorize new commands, a physical `0x2F` or `0x33` operation, record loops, decoded-result exposure through the development action, or production sync. Later measurement/entity and synchronization policies remain separate stage gates.
