# Stage 2C — GD82 live protocol evidence

Reviewed 2026-09-27 from a **user-supplied, privacy-safe summary** of a private Android HCI capture. The raw capture was not provided to this repository and remains private. Its exact collection date was not supplied. This document records protocol-level facts only; it contains no BLE address, private device identifier, measurement value, measurement timestamp, APK, signing material, or raw capture. Stage 2D uses these facts for an offline, Home Assistant-independent parser. No Home Assistant command/write path is authorized by this evidence record.

## Capture provenance and conditions

The physical device was a FORA 6 Connect **GD82**. The research application was derived from iFORA HM 1.7.6, package `com.foracare.tdlink.hm`; the **original** APK SHA-256 was `dd154de094fc28de86c5a153aada1393816159e5c6ba852235938813c449449c` (the Stage 2B mirror specimen). The original manifest had minimum SDK 30 and target SDK 34. For private protocol research, minimum SDK was changed to 27, and the app was rebuilt and **locally re-signed**. The runtime app was therefore a **patched research copy**, not the original officially signed APK. It launched on Android 8.1/API 27, scanned, connected to the real GD82, and imported its existing uric-acid record. The modified APK, original APK, signing material, and raw traffic are not tracked here.

The captured proprietary path used service `00001523-1212-efde-1523-785feabcd123` and Write/Notify characteristic `00001524-1212-efde-1523-785feabcd123`. The app enabled the characteristic's CCCD before application traffic, wrote requests to `1524`, and received responses through its notification path. In this successful proprietary import session there was **no BLE bonding, SMP pairing exchange, or observed encryption transition**. That observation does not resolve the security requirements of the separate standard Glucose Service/RACP path or every possible custom operation.

## Live-confirmed frame envelope

The observed requests and responses were eight bytes. In the captured frames, byte 0 was `0x51`; byte 1 was the command identifier and was echoed in the response; byte 6 was `0xA3` for requests or `0xA5` for responses. Byte 7 equals `sum(bytes[0:7]) mod 256`. This envelope agrees with the Stage 2B static command builder. Bytes 2–5 remain command-specific and are **not** given general-purpose field names.

| Operation | Request | Response | Live-supported interpretation |
| --- | --- | --- | --- |
| `0x22` wake / initial activation | `51 22 00 00 00 00 A3 16` | `51 22 00 00 FF FF A5 16` | Exchange observed at the start of this import path. The meaning of the non-command response bytes is unresolved. |
| `0x24` project/model query | `51 24 00 00 00 00 A3 18` | `51 24 83 41 04 00 A5 E2` | Response bytes 2–3 decode little-endian to project ID `0x4183`. Bytes 4–5 are retained as opaque. |

The physical GD82's `0x4183` response **live-confirms** its link to the `TD4183` branch traced in Stage 2B; the prior manual-filename inference is no longer the sole support. These exchanges confirm their observed sequence, not the safety or efficacy of sending either command independently from Home Assistant. The BLE write type and behavior under other meter states remain unresolved.

## Additional observed command identifiers

| Identifier | Evidence-supported role | Boundary |
| --- | --- | --- |
| `0x27`, `0x28` | Metadata/project/device-related responses appeared in the import workflow. | Exact fields and semantics unresolved. |
| `0x2B` | Record/index/count-related metadata in the multifunction workflow. | Exact field layout and semantics unresolved. |
| `0x25` | First part of indexed record retrieval; response contained packed date/time information consistent with the stored meter timestamp. | No public byte/bit map, timezone rule, or private timestamp is available here. |
| `0x26` | Second part of indexed record retrieval; response contained measurement/analyte payload. | No public byte positions or general analyte dispatcher are established. |
| `0x2F` | Additional metadata/status operation in the import sequence. | Exact semantics unresolved. |
| `0x50` | Finishing/end-of-session operation observed before disconnect. | Exact semantics beyond the observed sequence unresolved. |

The real uric-acid record was obtained through the `0x25` + `0x26` indexed retrieval sequence. The app's displayed uric-acid value equaled the parsed raw numeric value divided by ten, corroborating the Stage 2B app-code path **for uric acid on this GD82/TD4183 path**. The private specimen's value and timestamp are deliberately omitted. Only uric acid has been physically tested on this meter; the scaling is not assigned to glucose, ketone, cholesterol, haemoglobin, haematocrit, or another analyte.

## Evidence classes and implementation boundary

- **LIVE-CONFIRMED from user-supplied capture summary:** custom `1523/1524` request/notification transport; CCCD enabled before traffic; eight-byte summed envelope and marker/echo behavior in observed frames; `0x22` and `0x24` exchanges; physical project ID `0x4183`; indexed `0x25`/`0x26` participation in the uric-acid import; uric-acid raw-value `/10` display scaling; successful proprietary import without bonding or observed encryption.
- **STATIC-ANALYSIS-SUPPORTED:** iFORA HM's `TD4183` multifunction branch and uric-acid handler, generic custom BLE transport, and summed frame construction. The runtime was a patched, locally re-signed copy of the analyzed 1.7.6 specimen, so this is corroboration of the captured research workflow, not proof about an untouched official build.
- **INFERRED:** `0x25`/`0x26` responses likely form a paired indexed record for this workflow, based on app call paths and the live import sequence. A general multi-analyte record schema is not established.
- **UNRESOLVED:** precise `0x25` timestamp bit layout and timezone; `0x26` raw-value/analyte field positions; meanings of other response bytes; write type, retries, error handling, and other meter states; standard Glucose/RACP use and its security; all non-uric-acid scaling; production discovery and scanner identity.

Stage 2D may implement the confirmed frame envelope, fixed wake/model-query request construction, project-ID extraction, and a **separate contextual uric-acid scaling helper**. It cannot yet parse a `0x25` timestamp, extract an analyte/raw field from `0x26`, or dispatch arbitrary records from the sanitized evidence alone. Tracked tests must use the non-private protocol exchanges above or explicitly synthetic data. No production BLE write, automatic connection, record retrieval, polling, entity, or coordinator is authorized.
