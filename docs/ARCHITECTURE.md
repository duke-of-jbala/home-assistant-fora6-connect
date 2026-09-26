# Architecture

## Intended data path

```text
FORA 6 Connect GD82 --BLE--> Home Assistant Bluetooth stack
                                 ^
                                 | optional generic transport
                         ESPHome Bluetooth Proxy

Home Assistant Bluetooth stack --> custom_components/fora6
                                   |-- Bluetooth transport
                                   |-- HA-independent FORA protocol parser
                                   |-- measurement synchronization
                                   |-- entities and diagnostics
```

The ESPHome proxy forwards Bluetooth activity; it has no FORA-specific code. The integration will resolve connectable devices through Home Assistant's Bluetooth APIs so either a local adapter or an eligible proxy can carry a future connection. The exact connection and retry design belongs to Stage 4 and must follow the APIs available then.

## Boundaries

- `bluetooth.py`: future HA Bluetooth transport and notifications. No FORA frame decoding.
- `protocol.py`: future pure-Python frame parsing and validation, testable with raw bytes alone. No HA, ESPHome, adapter, or physical meter requirement.
- `models.py`: future validated measurement structures. Keep original meter time separate from sync time and distinguish control-solution readings when available.
- `coordinator.py`: future retrieval and synchronization state.
- `sensor.py`: future entities associated with one HA device per physical meter.
- `config_flow.py`: future setup and discovery after device identity can be established beyond the documented UUID pair.
- `diagnostics.py`: future non-sensitive diagnostics.

As of Stage 1A, no connection, parser, config flow, or entities are active. Expected analytes, subject to exact GD82 support and protocol validation, are glucose, haematocrit, haemoglobin, beta-ketone/beta-hydroxybutyrate, total cholesterol, and uric acid. Potential diagnostics include last measurement time, last successful sync, sync state, record position/count, and signal strength.

## Documentation and packaging

The custom integration uses `translations/en.json` for runtime localization. `strings.json` is included only to match the requested repository structure; Home Assistant's custom integration guidance does not use it as a runtime translation source. Manifest version `0.0.0` is a development placeholder required for a custom integration, not a release. The repository layout targets HACS; HACS readiness is a Stage 10 gate.
