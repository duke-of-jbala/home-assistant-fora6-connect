# Architecture

## Intended data path

```text
FORA 6 Connect (GD82) --BLE--> Home Assistant Bluetooth stack
                                 ^
                                 | optional generic transport
                         ESPHome Bluetooth Proxy

Home Assistant Bluetooth stack --> custom_components/fora6_connect
                                   |-- Bluetooth transport
                                   |-- HA-independent FORA protocol parser
                                   |-- measurement synchronization
                                   |-- entities and diagnostics
```

The ESPHome proxy forwards Bluetooth activity; it has no FORA-specific code. Production transport will resolve connectable devices through Home Assistant's Bluetooth APIs so either a local adapter or an eligible proxy can carry a future connection. The exact production connection and retry design belongs to Stage 4 and must follow the APIs available then.

## Boundaries

- `bluetooth.py`: future HA Bluetooth transport and notifications. No FORA frame decoding.
- `protocol.py`: future pure-Python frame parsing and validation, testable with raw bytes alone. No HA, ESPHome, adapter, or physical meter requirement.
- `models.py`: future validated measurement structures. Keep original meter time separate from sync time and distinguish control-solution readings when available.
- `coordinator.py`: future retrieval and synchronization state.
- `sensor.py`: future entities associated with one HA device per physical meter.
- `config_flow.py`: future setup and discovery after device identity can be established beyond the documented UUID pair.
- `diagnostics.py`: future non-sensitive diagnostics.

The manually invoked development-only `gatt_probe.py` has validated Home Assistant-side connectable-device resolution, connection, five-service GATT enumeration, and clean disconnect on the real meter. The exact scanner/adapter selected is unknown. The separate development-only `notification_observer.py` is authorized to subscribe to three observed Notify characteristics for 30 seconds and return metadata only; the first real run stopped at a failed `2A18` subscription. A revised real run failed `2A18`/`2A34` subscriptions, succeeded on custom `1524`, and received no notifications during 30 seconds of navigation on the only existing uric-acid result. Stage 1A, 1B, and 1C are complete; Stage 2A public review and Stage 2B static app analysis have been performed; pairing and independent live protocol operations remain unauthorized. Auto-mode advertisement and address identity behavior are deferred to Stage 6 production discovery; the selected HA scanner/proxy is deferred to Stage 9 end-to-end proxy validation. Manufacturer-data meaning remains unknown and may be revisited for Stage 6 identification if useful, or earlier only if later protocol evidence makes it relevant. Bleak/Home Assistant may configure CCCDs for subscription, but no FORA application characteristic write is authorized. These temporary actions establish transport observations, not production discovery or FORA application protocol behavior. Future production transport still belongs in `bluetooth.py`. No parser, production config flow, synchronization, or entities are active. Expected analytes, subject to exact GD82 support and protocol validation, are glucose, haematocrit, haemoglobin, beta-ketone/beta-hydroxybutyrate, total cholesterol, and uric acid. Potential diagnostics include last measurement time, last successful sync, sync state, record position/count, and signal strength.

## Documentation and packaging

The custom integration uses `translations/en.json` for runtime localization. `strings.json` is included only to match the requested repository structure; Home Assistant's custom integration guidance does not use it as a runtime translation source. Manifest version `0.0.0` is a development placeholder required for a custom integration, not a release. The repository layout targets HACS; HACS readiness is a Stage 10 gate.
