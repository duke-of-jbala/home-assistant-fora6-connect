# FORA 6 Connect for Home Assistant

Home Assistant custom integration for the FORA 6 Connect (GD82) meter over
Bluetooth. It creates one uric-acid sensor. The current measurement is fetched
only when you run the manual refresh action. A real GD82 refresh has been
validated through an M5Stack Atom Lite ESPHome Bluetooth Proxy. Home Assistant
can also select a connectable local Bluetooth adapter; the Stage 9 physical
route proof applies to the tested Atom Lite session.

## Requirements

- Home Assistant with Bluetooth enabled.
- A FORA 6 Connect GD82 within range of a connectable local Bluetooth adapter
  or an ESPHome Bluetooth Proxy that supports active connections.
- HACS for the HACS installation route below.

The supported stored-record snapshot has exactly two or four raw slots.
Other counts fail safely and leave the previous in-process sensor value intact.
This integration currently exposes uric acid only, in mg/dL. It does not poll,
import history, or synchronize automatically.

## Install with HACS

1. In HACS, open the menu (three dots) and choose **Custom repositories**.
2. Enter `https://github.com/duke-of-jbala/home-assistant-fora6-connect`,
   choose **Integration**, and add it.
3. Open **FORA 6 Connect** in HACS and download it.
4. Restart Home Assistant to load the custom integration.
5. Turn the meter on normally. In **Settings → Devices & services**, use the
   discovered FORA 6 Connect card and confirm setup. If the card is not shown,
   keep the meter on and check Home Assistant's Bluetooth discovery and
   connectable adapter/proxy availability.

HACS installs the integration under
`<Home Assistant configuration directory>/custom_components/fora6_connect/`.
Until a GitHub release is published, HACS uses this repository's default
branch. Installing through HACS does not add the Home Assistant config entry
by itself.

### Manual installation

Copy the entire `custom_components/fora6_connect/` directory into
`<Home Assistant configuration directory>/custom_components/fora6_connect/`,
restart Home Assistant, and complete the same Bluetooth discovery setup.
Keep the directory contents together, including the manifest, translations,
action descriptions, and brand assets.

## Refresh the uric-acid sensor

1. Turn the GD82 on normally.
2. Do not browse stored records with the meter's arrow buttons.
3. Run `fora6_connect.refresh_current_uric_acid` in Home Assistant, selecting
   the configured FORA 6 Connect entry. No Bluetooth address entry is needed.

The action response contains the selected private health value and meter-local
measurement time. Keep that response private. Before the first successful
refresh, the sensor is unavailable. A later failed refresh retains the last
valid value in process memory; reload or restart begins unavailable again
until another manual refresh.

Only the current sensor state is updated. No historical observations are
imported, and no other analyte has a numeric entity. Equal-minute candidates
at a four-slot count are treated as ambiguous and do not update the sensor.
The meter-local timezone is unknown. The tested GD82 uses its factory
Bluetooth MAC as the guarded canonical identity. Its standard GATT serial
and System ID were unusable; retrieval of the printed serial is unresolved.

## Update or remove

For updates, install the offered version in HACS and restart Home Assistant
to load the changed Python integration. Manual installations require replacing
the full component directory and restarting. The existing config entry and
entity are intended to remain in place during an update; verify them after
the restart.

To stop using the integration, remove its config entry from **Settings →
Devices & services**. If installed through HACS, then remove the repository
through HACS and restart Home Assistant. For a manual installation, remove the
component directory after removing the config entry, then restart. Review any
Home Assistant recorder data separately under Home Assistant's own retention
and deletion controls.

## Support and development

Report issues at [GitHub Issues](https://github.com/duke-of-jbala/home-assistant-fora6-connect/issues).
Include your Home Assistant and integration versions, Bluetooth connection
path (local adapter or proxy), the action's non-sensitive error stage/code,
and steps to reproduce. Redact Bluetooth addresses, health values,
measurement times, tokens, IP addresses, and unredacted logs/screenshots.

The [Stage 10 packaging review](docs/STAGE10_HACS_PACKAGING_READINESS.md)
records installation and release evidence. The
[master roadmap](FORA6_MASTER_ROADMAP.md) tracks separately authorized work.
The [protocol evidence register](docs/PROTOCOL.md) explains the bounded
command and measurement model. Local [brand assets](docs/BRANDING.md) are
original placeholders, not official ForaCare artwork or endorsement.

MIT licensed; see [LICENSE](LICENSE).
