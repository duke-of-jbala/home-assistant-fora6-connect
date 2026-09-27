# Stage 5A — GD82 uric-acid display-unit evidence

**State:** Complete for the authorized offline evidence review. The TD4183
uric-acid number produced by raw `/10` is the app's **mg/dL base value**. The
app may display that value in mg/dL, µmol/L, or mmol/L according to its own
`UA_UNIT` preference. The unit selected during the retained physical import was
not recorded. No meter BLE command, physical test, or real result exposure was
performed in this stage.

## Sources and provenance

1. Tracked [Stage 2C](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md) and
   [Stage 2G](STAGE2G_TD4183_RECORD_SCHEMA.md) establish the real GD82 TD4183
   path, uric-acid selector, raw integer, and observed raw `/10` number. They
   deliberately omitted the displayed unit and private specimen details.
2. Retained private iFORA HM 1.7.6 and 1.7.9 decompiled source and resources
   were read in place. Their provenance and authenticity limit are in the
   [Stage 2B record](STAGE2_IFORA_HM_STATIC_ANALYSIS.md). The relative class
   paths below identify inspected call sites without including proprietary
   source or a private filesystem path.
3. The English FORA 6 Connect manual bundled with both app specimens was
   searched for uric acid and measurement units. It specifies glucose and
   ketone units, but supplies no uric-acid unit or GD82 uric-acid unit mode.
   It does not support an independent meter-display unit claim.
4. The retained private import evidence corroborates the raw `/10` number and
   TD4183 path only. It does not record the app's `UA_UNIT` preference or the
   unit label shown during that import. No private value, time, bytes, address,
   or identifier is published here.

## TD4183 to app display call path

| Step | 1.7.6 | 1.7.9 | Conclusion and class |
| --- | --- | --- | --- |
| Parse `0x26` | `b4/a.java` `L()`/`M()` constructs the uric-acid record | `f2/a.java` `L()`/`M()` constructs `e2/u` from the raw integer, analyte, category, and auxiliary byte | TD4183 uric-acid identification and raw extraction: **STATIC-ANALYSIS-SUPPORTED** in both; private GD82 classification **LIVE-CORROBORATED**. |
| Import value | `ImportMeterRecordService.java`, around lines 1290 and 2530, divides the uric-acid object's raw number by ten before storage | The large import worker is not fully decompiled in the retained 1.7.9 source; the earlier Stage 2B fallback analysis recorded `/10` in its uric-acid branch | Import `/10`: **STATIC-ANALYSIS-SUPPORTED** by 1.7.6 source and the recorded 1.7.9 fallback finding; **LIVE-CORROBORATED** by the private 1.7.6 import. The 1.7.9 worker line was not independently reconstructed here. |
| Select unit | `v0/f.java` `l0()` reads `UA_UNIT`, default `0`; `p0/p0.java` offers three radio choices | `p016f0/f.java` `l0()` reads the same setting; `Z/P.java` offers the same choices | App unit is configurable: **STATIC-ANALYSIS-SUPPORTED** in both. |
| Display value | `v0/f.java` `m0()` formats the base value or converts it; `v0/j.java` uses it for uric-acid export | `p016f0/f.java` `m0()` has the same branches; `Z/X.java` around lines 663–685 labels and formats the uric-acid result; `Z/C0172l.java` and `p016f0/j.java` also call `m0()` | mg/dL branch formats the stored number without a unit conversion; other branches convert it: **STATIC-ANALYSIS-SUPPORTED** in both. |

Both versions map `UA_UNIT=0` to `mg/dL`, `1` to `µmol/L`, and `2` to
`mmol/L`. Their `m0()` paths format the stored number directly for mg/dL,
multiply it by `59.48` for µmol/L, or multiply it by `59.48/1000` for mmol/L.
This establishes the app's **mg/dL base unit** for the already-supported
raw `/10` TD4183 uric-acid number. These app conversions are documented as
evidence, not implemented in Home Assistant; Home Assistant uses only the
unconverted mg/dL base number.

## Selection, locale, record data, and auxiliary byte

| Question | Result | Class |
| --- | --- | --- |
| Fixed or configurable? | Configurable in the app. The `UA_UNIT` setting defaults to `0` (mg/dL) unless changed. The setting UI offers the three units above. | **STATIC-ANALYSIS-SUPPORTED**, both versions. |
| Locale or region? | Both `MainActivity.java` versions set `UA_UNIT=1` on first login when the app locale country is `ZA`. A user can subsequently change the unit through settings. No other automatic UA locale selection was established in the traced path. | ZA rule **STATIC-ANALYSIS-SUPPORTED**; complete regional policy **UNRESOLVED**. |
| When is conversion applied? | The 1.7.6 import divides raw by ten before storage. The app's `m0()` applies the optional µmol/L or mmol/L conversion when formatting that stored value. | `/10` **LIVE-CORROBORATED** for the private import; display conversion **STATIC-ANALYSIS-SUPPORTED** in both versions. |
| Can the GD82 meter itself select a different UA unit? | The examined `0x25`/`0x26` record path contains no established UA-unit selector. The app can display the same stored record in different units. The physical meter's own UA unit modes, if any, are not established. | App selection **STATIC-ANALYSIS-SUPPORTED**; meter setting **UNRESOLVED**. |
| Where does the app obtain the label? | `UA_UNIT` application preference selects a resource string. The traced result screens do not select the unit from the `0x26` auxiliary byte, category, project code, or device configuration. | Preference selection **STATIC-ANALYSIS-SUPPORTED** in both; untraced device-unit behavior **UNRESOLVED**. |
| Does `0x26` byte 4 choose the unit? | The TD4183 parser preserves byte 4 as an auxiliary/ambient value in the record object. The traced UA formatter takes the stored number and app unit preference, without that byte. Its physical meaning remains unknown. | No role in this app display path **STATIC-ANALYSIS-SUPPORTED**; physical meaning **UNRESOLVED**. |
| Which unit was visible in the physical import? | Not recorded in the sanitized or retained validation summary. The numeric match alone does not establish the active app preference. | **UNRESOLVED**. |

The app's unit labels and conversion branches establish a base value suitable
for an explicit mg/dL Home Assistant mapping. They do **not** prove that the
GD82 meter display itself uses mg/dL or that the user's iFORA HM screen was
set to mg/dL during the private capture.

## Implementation decision and remaining gate

`Fora6Measurement` now labels only valid identified uric-acid raw `/10`
numbers as mg/dL. Invalid `0xFFFF`, unknown selectors, and other analytes
remain without a numeric value or unit. The inert sensor mapper admits only
General-category valid uric acid. QC, AC, and PC records cannot update its
ordinary numeric state. No app-style conversion or locale selection is added.

An actual `SensorEntity` remains unregistered: Stage 6 has not established a
stable meter identity, config entry, or device attachment. `sensor.py` starts
no BLE work. **Exact next gate:** separately authorize Stage 6 discovery and
identity policy before registering an mg/dL uric-acid entity, or a separate
evidence task for unresolved meter-native unit modes. Stage 6 has not started.
