# Stage 2A — public protocol evidence acquisition

Reviewed 2026-09-26. Stage 2 is authorized for evidence acquisition, but this review involved no live BLE operation, APK execution, pairing, RACP, characteristic I/O, record retrieval, or new measurement. **No verified GD82 application command bytes, response frames, checksum, or record layout were found.** The linked sources establish transport metadata and identify a manufacturer application for later static study. The Stage 1 real-device evidence remains in [PROTOCOL.md](PROTOCOL.md).

## Source register

### ForaCare blood glucose and multifunctional monitoring FAQ, Rev 5.5

- **Organization / date / type / retrieval:** ForaCare Suisse AG; editor Joey Yang; released 2023-03-13; manufacturer PDF; reviewed 2026-09-26.
- **URL:** [ForaCare BGM FAQ Rev 5.5](https://www.foracare.ch/wp-content/uploads/2023/03/3.1-BGM-FAQ_Rev5.5_230313.pdf), Q36–Q37 (PDF pages 33–34).
- **Model applicability / confidence:** Q36 describes ForaCare Bluetooth V4 generally; Q37 explicitly lists FORA 6 Connect **GD82** with built-in Bluetooth and iFORA HM. **Documented**, with the custom GATT pair also independently **observed** on this meter in Stage 1.
- **Supported facts:** BLE UUID base `1212-efde-1523-785feabcd123`; service `0x1523`; characteristic `0x1524` with Write/Notify properties. Q37 maps GD82 to iFORA HM. Q36 mentions iFORA BG in a general pairing discussion; that is not the GD82 app mapping.
- **Not supported / open questions:** No GD82 request bytes, opcode, frame, checksum, response, analyte code, record layout, or security behavior. Whether the linked Box material contains protocol details is unknown.
- **Redistribution:** Publicly retrievable PDF bears a confidential marking; no PDF or substantial excerpt was copied into Git. Redistribution permission is unclear.

### FAQ-linked ForaCare Box share

- **Organization / date / type / retrieval:** ForaCare Suisse AG link from FAQ Q36; publication date unknown; manufacturer-linked file share; attempted 2026-09-26.
- **URL:** [FAQ-linked Box share](https://foracare-suisse-ag.box.com/s/h54mphhr6r92wnzw5x9hrtbs7xx1qn9r).
- **Model applicability / confidence:** Contents **unverified**. It may relate to the FAQ's general Bluetooth V4 section; GD82 applicability cannot be assessed.
- **Access result:** Browser retrieval returned an internal error; the sandboxed command-line request could not resolve the Box host. No file listing, redirect target, document, or bytes were obtained. This is an environment access failure, not proof that the share is gone.
- **Supported facts:** Only that the manufacturer FAQ links to this share.
- **Not supported / open questions:** File names, exact contents, commands, and rights. No download or local SHA-256 exists. Recheck access in a later authorized research task.
- **Redistribution:** Unknown until contents and license can be inspected; keep any later download outside tracked Git.

### FORA 6 Connect GD82 user manual

- **Organization / date / type / retrieval:** ForaCare Suisse AG; online file path dated 2021-10 (manual revision date not established here); manufacturer manual; reviewed 2026-09-26.
- **URL:** [FORA 6 Connect GD82 user manual](https://switzerland.foracare.ch/wp-content/uploads/2021/10/FORA-6-Connect-GD82-4183D_meter-manual_311-4183400-070.pdf), English Bluetooth/data-transfer instructions.
- **Model applicability / confidence:** Explicit GD82 manual; **documented**.
- **Supported facts:** Describes iFORA HM data download and Bluetooth transmission when the meter is turned off; the blue indicator flashes during transfer.
- **Not supported / open questions:** No packet bytes, transfer request, security diagnosis, or mapping of non-glucose results to a GATT path.
- **Redistribution:** Publicly available manual; redistribution rights not established. Only short factual summaries are retained.

### iFORA HM official Android listing

- **Organization / date / type / retrieval:** FORACARE, INC.; Google Play listing showed last update 2025-12-30; official application listing; reviewed 2026-09-26.
- **URL:** [iFORA HM on Google Play](https://play.google.com/store/apps/details?id=com.foracare.tdlink.hm).
- **Model applicability / confidence:** FAQ Q37 and GD82 manual identify iFORA HM as the supported client for GD82; Google Play identifies package `com.foracare.tdlink.hm`. **Documented application identity**, not protocol behavior.
- **Supported facts:** Official app/package candidate for Stage 2B static analysis.
- **Not supported / open questions:** The reviewed official listing did not expose a verifiable version, APK hash, signing certificate, downloadable APK, command bytes, or implementation details. No direct vendor-hosted APK was located in this review; this does not prove one does not exist.
- **Redistribution:** Proprietary app; no APK was acquired or committed. Obtain and inspect only under a later scoped task and applicable terms.

### Third-party iFORA HM package metadata leads

- **Organization / date / type / retrieval:** APKPure and APKFab, third-party package indexes; listing dates vary; reviewed 2026-09-26.
- **URLs:** [APKPure iFORA HM listing](https://apkpure.net/ifora-hm/com.foracare.tdlink.hm/download), [APKFab iFORA HM listing](https://apkfab.com/ifora-hm/com.foracare.tdlink.hm).
- **Model applicability / confidence:** They report the official package name but their binaries and metadata have **not been verified** against Google Play or the manufacturer. **Third-party acquisition leads only**.
- **Reported versions / hashes:** APKPure reports 1.7.9 as an XAPK and SHA-256 `e4705a16dcd5bfab08893fca56d82eacdc097c3d10c3f90bcd9a30666fc34a7d`; its "Signature" field displays `9208c77b15c71e443c04f3d6ab1d4c800b1293c4` without independent validation here. It also lists 1.7.8 and 1.7.7 as XAPK and 1.7.6 as APK; its [1.7.8 page](https://apkpure.net/ifora-hm/com.foracare.tdlink.hm/download/1.7.8) reports SHA-256 `b0a49101e008a7b3d29b1bffc7e548f52029a109f6ec22e60ad9914896e128f7`. These are *mirror-reported*, not locally computed. Listing dates differ across indexes, so do not infer the official current version from them.
- **Supported facts:** Candidate version and hash claims to check if a later task considers mirror acquisition.
- **Not supported / open questions:** Authenticity, equivalence to an official Play build, signature lineage, split-APK composition, and all protocol details. No APK/XAPK was downloaded, installed, or executed.
- **Redistribution / supply chain:** Third-party mirrors may repackage apps or carry incomplete splits; do not acquire or trust automatically. Keep any separately authorized package outside Git and verify its signing certificate and computed file hashes.

### Bluetooth SIG Glucose Profile 1.0.1

- **Organization / date / type / retrieval:** Bluetooth SIG; version 1.0.1 (publication date not checked in Stage 2A); standard; reviewed 2026-09-26.
- **URL:** [Glucose Profile specification](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/GLP_v1.0.1/out/en/index-en.html).
- **Model applicability / confidence:** Defines the standard Glucose Service profile, which the GD82 exposes, but does not document this meter's custom service implementation. **Documented standard**, not an observed GD82 security diagnosis.
- **Supported facts:** Standard Glucose Sensor/Collector bonding and LE security requirements; the standard RACP path is distinct from the FORA custom 1524 path.
- **Not supported / open questions:** Why the unpaired Home Assistant 2A18/2A34 subscriptions failed, whether this GD82 enforces the profile in the tested path, and whether the custom service requires pairing. No RACP transaction was attempted or authorized.
- **Redistribution:** Public specification; link and paraphrase only.

### Public TaiDoc and glucometer code

- **Organization / date / type / retrieval:** [AndroidAppPCLink TaiDoc PCLinkLibrary mirror](https://github.com/BaiyuY/AndroidAppPCLink) (TaiDoc 2014 material mirrored by BaiyuY), [glucometerutils](https://github.com/glucometers-tech/glucometerutils), and [kolos/glucometer](https://github.com/kolos/glucometer); public source repositories; reviewed 2026-09-26. Publication dates for individual revisions were not established in this review.
- **Model applicability / confidence:** PCLinkLibrary describes older TaiDoc models and BLE support, but does **not** list GD82. The other repositories describe TaiDoc TD42xx or TD-4235 USB/HID paths, not FORA 6 Connect BLE. **Documented for those listed devices only**.
- **Supported facts:** Related software exists and may guide where to search for manufacturer ecosystem material.
- **Not supported / open questions:** No verified GD82 `1524` request, response, frame, checksum, or analyte mapping. Older TaiDoc commands and USB/HID framing cannot be transferred to GD82 by association.
- **Redistribution:** Repository/source licenses and proprietary bundled components require separate review. No code, JAR, or APK was copied into Git.

### Nordic UUID collision

- **Organization / date / type / retrieval:** Nordic Semiconductor, [Android nRF Blinky](https://github.com/NordicSemiconductor/Android-nRF-Blinky) and [iOS nRF Blinky](https://github.com/NordicSemiconductor/iOS-nRF-Blinky); vendor example source; reviewed 2026-09-26; exact publication versions not pinned.
- **Model applicability / confidence:** **No FORA/GD82 applicability.** The examples use the same UUID namespace but assign Nordic demo semantics.
- **Supported facts:** The shared `1523`/`1524` UUID base is not unique to FORA; UUID equality cannot establish command semantics or device identity.
- **Not supported / open questions:** Every Nordic button/LED value and callback meaning is unrelated to the GD82 until independent FORA-specific evidence shows otherwise.
- **Redistribution:** Link only; no example code copied.

## Search outcome and interpretation

Searches combined FORA 6 Connect, GD82, TaiDoc, ForaCare BLE, iFORA, the package name, `1523`/`1524` UUIDs, and meter command or memory-download terms across manufacturer pages, public code, SDK leads, and application indexes. The strongest **GD82-specific** sources are the manufacturer FAQ Q37, GD82 manual, and the Stage 1 physical observations. The FAQ Q36 and real GATT inventory establish the custom characteristic's existence and properties. They **do not establish a safe first application request**. No exact GD82 command bytes or response structure were verified. Standard Glucose Service/RACP and FORA custom `1524` remain distinct possible protocol paths; no RACP operation is authorized here.

## Proposed Stage 2B gate — static analysis of iFORA HM

This is a plan, not work performed in Stage 2A. A **separately scoped authorization** should permit acquisition and static inspection of the manufacturer app; it should not automatically authorize live meter traffic.

1. Prefer obtaining the official Google Play build through a controlled Android/Play installation and lawful export of the installed package and splits, if feasible. Record package name, version code/name, download source/date, exact file SHA-256, split composition, and signing-certificate digest. If only a third-party mirror is feasible, review its supply-chain limitations and obtain explicit scope before acquisition. Compare computed hashes and signing identity against independently available trusted evidence; do not treat a mirror-reported hash as authenticity proof.
2. Keep APK/XAPK, extracted files, and working notes with proprietary code outside tracked Git and away from private health data. Do not install or execute a mirror APK. Unpack/decompile statically (for example, archive listing, resource inspection, DEX decompilation, native-library symbol/string inspection) in an isolated working directory; record tool versions and inputs.
3. Search resources, bytecode, and native libraries for the exact `1523`/`1524` UUIDs, BLE writes and notification handlers, command/opcode constants, frame assembly, checksum/CRC routines, record structures, analyte and GD82 identifiers, and pairing/security handling. Trace call sites and meter-model selection before assigning any operation to GD82. Keep standard Glucose/RACP activity separate from FORA custom traffic.
4. For every candidate operation, record package version/hash, file/class/method or native symbol and offset, relevant control flow, evidence strength, model applicability, expected response, and unresolved ambiguity. Commit only concise paraphrases/minimal permissible excerpts and non-sensitive provenance, never proprietary application source or patient data.
5. Review an exact request and its expected behavior before proposing any first live write. If static evidence remains insufficient, propose a separately authorized controlled official-app traffic capture. **Do not choose a speculative first command.**

**Exact next gate:** explicit authorization of **Stage 2B static acquisition and inspection of iFORA HM**, with a verified acquisition route and package provenance. Stage 2 remains in progress; no live protocol operation has been sent.

## Stage 2B follow-up — 2026-09-26

The gate above records the **Stage 2A decision at that time**. Stage 2B was subsequently authorized and performed: mirror-distributed iFORA HM 1.7.6 and 1.7.9 were acquired for static inspection outside Git. Both locally computed hashes matched the mirror's listings, and all inspected APKs had valid signatures with one shared certificate. No independent official Google Play/ForaCare certificate fingerprint was available, so the packages remain corroborated mirror specimens rather than officially authenticated binaries. The [Stage 2B evidence register](STAGE2_IFORA_HM_STATIC_ANALYSIS.md) records their URLs, full hashes, signatures, versions, tools, call paths, qualified command candidates, and unresolved GD82 applicability. These later findings do not retroactively turn Stage 2A's public-source search into command evidence.

**Current exact next gate:** separate authorization of a controlled official-app traffic capture for physical GD82 corroboration, or acquisition of an independently authenticated official package for further static review. Neither option authorizes an independent first write to the meter.
