# FORA 6 Connect v1.0.0

First stable release of the Home Assistant custom integration for the FORA 6
Connect GD82 meter.

## What it does

- Discovers and configures a GD82 over Home Assistant Bluetooth, creating one
  GD82/ForaCare device and one uric-acid sensor with native **mg/dL** units.
- Provides `fora6_connect.refresh_current_uric_acid` to update the existing
  sensor on demand. It supports stored raw slot counts **two and four** only.
  With two eligible readings in a four-slot snapshot, the strictly later
  meter-local minute is selected; a tie does not update the sensor.
- Works with a connectable local Bluetooth adapter or ESPHome Bluetooth Proxy.
  A real manual refresh through an M5Stack Atom Lite proxy was validated after
  installation as a HACS custom Integration.

## Install and use

Add `https://github.com/duke-of-jbala/home-assistant-fora6-connect` to HACS
as a custom **Integration**, install it, and restart Home Assistant. Configure
the discovered meter under Devices & services. For a refresh, turn the meter
on normally, avoid its history arrow buttons, and run
`fora6_connect.refresh_current_uric_acid` for the configured entry. No manual
Bluetooth address is needed.

The sensor starts unavailable after a restart or integration reload until a
successful manual refresh. A later failed refresh retains the last valid
in-process reading.

## Current limits and privacy

There is no automatic/background synchronization, polling, historical import,
recorder/statistics backfill, persistent deduplication or resume, count-six-plus
support, or numeric entity for another analyte. Retrieval of the meter's
printed proprietary serial is not implemented.

The manual action response can contain the selected health value and
meter-local measurement time. Keep it private. The integration does not add
those fields to diagnostic logs or public documentation. Meter-local timezone
is unknown.
