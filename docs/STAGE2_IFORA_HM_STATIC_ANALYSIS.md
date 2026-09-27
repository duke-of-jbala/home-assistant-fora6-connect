# Stage 2B — iFORA HM static analysis

Reviewed 2026-09-26. This is a **static-only** analysis of two mirror-distributed iFORA HM packages. The app was never installed or executed; no real-meter connection, pairing, RACP, characteristic write, record retrieval, or new measurement occurred. APKs, XAPK splits, decompiled output, and native libraries are in a private temporary analysis directory outside Git. This document contains only package provenance and concise findings, not proprietary source or captured health data.

## Acquisition and provenance

The [official Google Play listing](https://play.google.com/store/apps/details?id=com.foracare.tdlink.hm) and [ForaCare FAQ Q37](https://www.foracare.ch/wp-content/uploads/2023/03/3.1-BGM-FAQ_Rev5.5_230313.pdf) identify iFORA HM / `com.foracare.tdlink.hm` as the manufacturer-supported GD82 client. No official direct APK URL or controlled Android/ADB export was available in this environment. The Google Play Developer download API is for the publishing account, which is unavailable here. Two [APKPure 1.7.6](https://apkpure.net/ifora-hm/com.foracare.tdlink.hm/download/1.7.6) and [1.7.9](https://apkpure.net/ifora-hm/com.foracare.tdlink.hm/download) artifacts were acquired **only for static analysis** at approximately 20:27–20:28 UTC on 2026-09-26. Both locally computed top-level SHA-256 values match the mirror's published values.

| Artifact | Source endpoint / type | Local SHA-256 | Manifest and composition |
| --- | --- | --- | --- |
| iFORA HM 1.7.6 APK | [APKPure version page](https://apkpure.net/ifora-hm/com.foracare.tdlink.hm/download/1.7.6), [binary endpoint](https://d.apkpure.net/b/APK/com.foracare.tdlink.hm?versionCode=130); third-party mirror | `dd154de094fc28de86c5a153aada1393816159e5c6ba852235938813c449449c` | Package `com.foracare.tdlink.hm`; version name `1.7.6`, code `130`; one APK/one DEX; mirror calls it universal; min SDK 30, target SDK 34; no `.so` in this APK. |
| iFORA HM 1.7.9 XAPK | [APKPure version page](https://apkpure.net/ifora-hm/com.foracare.tdlink.hm/download), [binary endpoint](https://d.apkpure.net/b/XAPK/com.foracare.tdlink.hm?version=latest); third-party mirror | `e4705a16dcd5bfab08893fca56d82eacdc097c3d10c3f90bcd9a30666fc34a7d` | Package `com.foracare.tdlink.hm`; version name `1.7.9`, code `136`; base APK plus `config.arm64_v8a.apk`, `config.en.apk`, and `config.mdpi.apk`; one base DEX; min SDK 30, target SDK 35. ARM64 split contains `libhm.so` and `libsqlcipher.so`. |

The 1.7.9 base APK SHA-256 is `4b0756e19fed1d7340384f70c13030ea21df8a2cf1bfefcf4ec430d51847f052`. Split SHA-256 values, in the order ARM64, English, MDPI, are `7e06283e6ce0906432a4cace4ec8a0052acf8e3155d9ca556e6ae44b27288cf9`, `a3152d04f9b5269ec976ba005549a0a2c463539f5509daaf2afdb6570dd27516`, and `dee752981abd17e79f6973946176cc3b26653609349c9d43cb428de5921f84ea`. The XAPK is an archive, not a single signed APK; each contained APK was checked separately.

Google's `apksig` verifier reported valid signatures, zero errors, and zero warnings for both main APKs and all three 1.7.9 splits. 1.7.6 used APK Signature Scheme v2; the 1.7.9 base used v3; its splits reported v1/v2/v3. All examined APKs carried the **same** signing certificate:

- Subject: `CN=Jay Lee, OU=ForaCare Inc., O=Software Team, L=New Taipei City, ST=Wugu Dist., C=24888` (self-declared certificate fields).
- Certificate SHA-256: `208a0af4de42b9582777a0bb27d746ea9b5087cbc6d62fe5bf0265aa394abf4f`.
- Certificate SHA-1: `9208c77b15c71e443c04f3d6ab1d4c800b1293c4`; this equals the mirror's published signature fingerprint.

Both manifests request Bluetooth permissions, including Bluetooth scan/connect and older Bluetooth/location permissions. The 1.7.6 APK contains a FORA 6 Connect manual asset. These checks establish package identity, internal consistency across versions, and integrity relative to mirror-reported hashes. **They do not independently bind this self-signed certificate to an official Google Play or ForaCare release.** The app is a reasonably corroborated *mirror specimen for provisional static findings*, not an officially authenticated binary. No command below is promoted to confirmed physical-GD82 behavior on package evidence alone.

## Static tools and coverage

- `curl` for retrieval to `<private temporary workspace>`; `sha256sum` for local file hashes; `unzip` 6.00 for archive inventory and extraction.
- Google `apksig` library 9.4.1 (small local Java verifier, no app execution) for signature verification and certificate digests; OpenJDK 21.0.12.1.
- Androguard 4.1.4 / Python 3.12.3 for manifest, version, permission, and certificate inspection.
- Official JADX CLI 1.5.6 for static DEX decompilation. Each main APK produced seven JADX decompilation errors; the very large import thread required fallback mode, and its findings are qualified accordingly.
- `rg` 15.2.0 for source searches; GNU `strings` and `readelf` 2.42 for native inventory. No native library was loaded or executed.

Searches covered the exact custom and standard Glucose UUIDs, Android GATT write/notification/descriptor APIs, `TD4183`/GD82/FORA identifiers, analytes, command/frame/checksum terms, import and history paths, bonding, and native symbols. Across both versions’ decompiled source and resources, exact standard Glucose `1808`/`2A18`/`2A34`/`2A51`/`2A52` UUID strings were **not found**, while the custom UUID pair appeared in each BLE transport class. This is a bounded static string-search result, not proof that the application can never use the standard profile through a constructed value or unreviewed path. No RACP path was assigned to GD82.

## Evidence trail and classification

| Finding | Provenance within reviewed specimen | Class and limit |
| --- | --- | --- |
| Custom BLE transport uses service `00001523-1212-efde-1523-785feabcd123` and characteristic `00001524-1212-efde-1523-785feabcd123`; after service discovery it enables notifications, writes byte arrays to the selected characteristic, and forwards received notifications to its response stream. | 1.7.9 DEX `Y1/b.java` (UUID fields, service-discovery callback, notification setup, write queue, notification callback); corroborated by 1.7.6 `u3/b.java`. | **STATICALLY OBSERVED** in both mirror specimens. Selection is shared by many meter models, not uniquely GD82. |
| Import workflow calls the meter-detection factory, obtains a model-specific handler, then queries record count and records. | 1.7.9 `ImportMeterRecordService.c.run` fallback output, `g2/a.java`, `d2/AbstractC0426a.java`; 1.7.6 has the corresponding factory. | **STATICALLY OBSERVED**, with JADX fallback qualification for the large import thread. No real GD82 response was captured. |
| Project-code detection maps `TD4183` to `d2/w`, which inherits the multifunction `d2/C0428c` handler. | 1.7.9 `g2/a.java` enum/switch and `d2/w.java`; analogous 1.7.6 `c4/a.java`, `z3/u.java`. The official GD82 manual's file identifier contains `4183D`. | Mapping is **STATICALLY OBSERVED**; equating a physical GD82 response to project code `4183` is a **STRONG INFERENCE**, still unverified on the real meter. |
| The shared command builder forms eight-byte frames: seven literal/parameter bytes followed by an 8-bit sum of those seven bytes. The response validator also checks its final byte against an 8-bit sum and checks the command identifier. | 1.7.9 `f2/a.java` command constructors and checksum/response validators; same construction in 1.7.6 `b4/a.java`. | **STATICALLY OBSERVED** for these app paths. No independent real frame validates the framing or retry behavior on GD82. |
| The multifunction handler queries record count, retrieves indexed records through two response parts, and dispatches analyte classes including uric acid. The uric-acid enum is selected in the handler's analyte-range query, and a response type selector maps one branch to uric acid. | 1.7.9 `d2/C0428c.java`, `f2/a.java`, `e2/u.java`, `ImportMeterRecordService.c.run` fallback; analogous 1.7.6 `z3/c.java`, `b4/a.java`. | **STATICALLY OBSERVED** in the TD4183-linked shared handler. Exact physical GD82 UA frames and unit remain **UNKNOWN**. |
| In the 1.7.9 import path, a parsed uric-acid numeric value is divided by ten before storage. | 1.7.9 `ImportMeterRecordService.c.run` fallback, uric-acid object branch. | **STATICALLY OBSERVED** app processing, but not yet a verified GD82 unit/scaling rule. Do not decode the real meter from this alone. |
| The BLE transport listens for Android bond-state changes and reacts by restarting service discovery or disconnecting. No direct `createBond` call or GD82-specific authentication-failure branch was found in the reviewed path. | 1.7.9 `Y1/b.java`; manifest Bluetooth permissions. | **STATICALLY OBSERVED** bounded search. Whether standard Glucose or custom `1524` operations require bonding remains **UNKNOWN**. Stage 1 unpaired custom subscription proves subscription only. |
| The 1.7.9 ARM64 split has `libhm.so` and `libsqlcipher.so`. The reviewed `libhm.so` JNI exports relate to application configuration/account strings; targeted UUID, GD82, analyte, and GATT strings were not found there. | Split inventory; `readelf`/`strings` on `libhm.so`; `NdkModule` JNI declarations. | **STATICALLY OBSERVED** bounded native scan. Do not publish embedded credentials or infer that all native behavior has been ruled out. |

### Standard Glucose and custom FORA remain separate

The **standard** Glucose Service `0x1808` and RACP `0x2A52` are observed on the real GD82, but this static review traced the app's identified generic BLE transfer path through the **custom** `1523/1524` pair. The custom route includes a TD4183 handler whose numeric code is strongly associated with GD82 by the manual identifier, without an observed meter project-code response. Whether iFORA HM also uses standard RACP for a different state, model, or analyte remains unknown. No Nordic Blinky meaning is imported from the colliding UUID namespace.

## Candidate request dossier — **not ready for a live write**

The strongest potentially read-only candidate is the app's device/project-code query constructor, **not a verified standalone first operation**:

| Dossier item | Static evidence / unresolved point |
| --- | --- |
| Exact candidate request | `51 24 00 00 00 00 A3 18` (hex). The last byte is the sum of the preceding seven bytes modulo 256, derived from 1.7.9 `f2/a.n()` and `f2/a.a()/b()` and corroborated in 1.7.6 `b4/a.java`. This is **app-construction evidence**, not a physical GD82 capture. |
| Intended meaning and response | The app's detection routine parses the response as project/model code; its parser requires the matching `0x24` response identifier and valid trailing sum, then derives a project-code string and user mode. Actual GD82 response bytes and behavior are unknown. |
| Target and subscription | The common Android BLE path selects custom `1524` under `1523`, enables its notification descriptor, writes the constructed bytes to that characteristic, and processes its notifications through a response stream. The exact GD82 device-selected path remains an inference until its project code is observed. |
| Write mode | The reviewed Java path does not explicitly set a GATT write type. Do not assume the required write-with-response setting for a future Bleak operation. |
| App sequence | The ordinary detector sends a separately named WakeUpMeter frame (`51 22 00 00 00 00 A3 16`) before another identification request; it may then send the project-code query conditionally. The wake frame could alter meter state and is **not established as read/query-only**. Sending the project-code query without that sequence is untested. |
| Meter state, security, side effects | The GD82 manual describes transfer after meter shutoff. The app's bonding-state handling does not establish a required GD82 security level. The query appears non-mutating by its parser role, but no physical response or side-effect observation proves this. |
| Model applicability and confidence | TD4183-to-GD82 is a strong inference from the manual identifier and app branch, not a measured project code. Mirror-signature provenance is corroborated but lacks an independent official trust anchor. **Provisional only.** |

An indexed-record request exists in the TD4183-linked handler, and the code has uric-acid dispatch, but this review does **not** nominate record retrieval as a first write. No first-write candidate currently meets the full gate for a live Stage 2C operation: official-package provenance or independent app-traffic corroboration, physical GD82 model response, sequence/meter-state requirements, security, write mode, and expected non-mutating behavior are unresolved.

## Exact next gate

Request separate authorization for a **controlled official-app traffic capture** (Stage 2C evidence acquisition), or obtain an officially exported Play package and confirm its signing identity first. A capture should establish the physical GD82's selected characteristic, actual first command and response, connection security, and whether uric-acid records follow the custom path. Preserve raw traffic privately and commit only sanitized, provenance-rich findings. **No independent first live write is proposed or authorized by this Stage 2B result.**

## Stage 2C follow-up — user-supplied live capture summary, 2026-09-27

The Stage 2B dossier above is preserved as the **pre-capture static assessment**. A later controlled session used a **patched, locally re-signed research copy** derived from the reviewed 1.7.6 APK. The original minimum SDK 30 was changed to 27 for Android 8.1/API 27; the runtime was not the untouched signed mirror specimen or an authenticated official Play build. The user reports a successful physical GD82 connection and import. The private HCI capture is not in Git. See [the sanitized Stage 2C evidence record](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md).

That capture confirms the custom `1523/1524` path, observed eight-byte summed wake and project-query exchanges, and the GD82's `0x4183` project response. The `TD4183` association is therefore live-confirmed, replacing the earlier filename-only inference for this physical unit. The uric-acid import used the `0x25`/`0x26` indexed path, and the displayed uric-acid value corroborated raw-value `/10` scaling. No bonding, SMP exchange, or encryption transition was observed in this proprietary import session. The first-write dossier's earlier unknown physical response is resolved for **this captured sequence**, but the exact Home Assistant write type, other meter states, record field positions, and standard Glucose/RACP behavior remain unresolved. A later independently authorized Home Assistant transport prototype must still validate its own path; no Stage 2D code sends these requests.
