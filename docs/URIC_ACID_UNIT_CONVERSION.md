# Uric-acid display conversion evidence — Stage 7G2

**Stage 8 unit-model decision:** the HA uric-acid sensor keeps the evidence-backed mg/dL native value. It has no unit-converting device class; no HA mmol/L preference conversion is claimed. The app's mmol/L arithmetic and `FLOOR` record-display rule remain presentation evidence and are not applied to the core measurement model. See [the Stage 8 review](STAGE8_CURRENT_STATE_HARDENING_REVIEW.md).

**Stage 7H follow-up:** the existing Home Assistant entity was physically validated displaying its selected mg/dL current state after manual refresh. Stage 7H does not apply the app's mmol/L display conversion; `raw / 10 = mg/dL` remains the entity's base representation. No real value or time is recorded.

This is an offline review of retained private iFORA HM 1.7.6 and 1.7.9 decompilations, the earlier [Stage 5A unit record](STAGE5A_URIC_ACID_UNIT_EVIDENCE.md), and the user's privacy-safe GD82 observation. The private source remains outside Git. No real health value, meter time, identifier, capture, or proprietary code is included here.

## App conversion and formatting

| Layer | Both retained app versions | Classification |
| --- | --- | --- |
| Base number | The TD4183 uric-acid import divides the wire integer by ten before storing an mg/dL base value. The 1.7.9 import worker was not fully reconstructed; see Stage 5A for that provenance limit. | **STATIC-CONFIRMED** for the 1.7.6 import; the 1.7.9 fallback finding and live import corroboration are recorded in Stage 5A. |
| Unit selection | `v0/f.java` and `p016f0/f.java` read `UA_UNIT`: `0` mg/dL, `1` µmol/L, `2` mmol/L. | **STATIC-CONFIRMED**, both versions. |
| mmol/L arithmetic | Their `w()` conversion multiplies the stored mg/dL number by `59.48`, then divides by `1000`. | **STATIC-CONFIRMED**, both versions. |
| Record display | Their `m0()` mmol/L branch passes that converted number to a two-decimal formatter (`#0.00`). The `e.j()` formatter sets Java `DecimalFormat` rounding mode to `FLOOR`. Positive uric-acid values therefore display the largest two-decimal number no greater than the converted number. | **STATIC-CONFIRMED**, both versions. |
| Other app context | The separate `n0()` mmol/L branch uses `e.f()`, whose formatter is `HALF_UP`. Reviewed call sites use `n0()` for settings/range thresholds, whereas 1.7.9's result and list screens and both versions' export path call `m0()`. | **STATIC-CONFIRMED** for the reviewed call sites; all possible UI contexts were not exhaustively traced. |

The app's record-display rule is conceptually `floor((mg/dL × 59.48 ÷ 1000) × 100) ÷ 100` for positive values, formatted to two decimal places. This is **formatting of the app's base measurement**, not a different protocol scale or a change to the Home Assistant mg/dL product value. The `HALF_UP` threshold formatter shows why a general claim that all app mmol/L text is floored would be wrong.

## Physical corroboration and limit

The user privately observed two distinct decoded mg/dL records that the physical GD82 displayed with the same **0.26 mmol/L** text. Both converted quantities fall in the same two-decimal floor interval under the app `m0()` rule. Thus that rule **explains the observed display text arithmetically** (**LIVE-CORROBORATED** for the shared displayed text and distinct decoded records; **INFERRED** for the meter using an equivalent formatter).

The physical meter's firmware is separate from the retained phone app. Its exact conversion constant, intermediate precision, and rounding implementation are **UNRESOLVED**; the app source alone cannot prove them. The observation also does not establish whether the meter uses `m0()` itself. Home Assistant continues to represent the evidence-backed mg/dL base value. No mmol/L conversion is implemented in this review.
