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

The manually invoked development-only `gatt_probe.py` validated Home Assistant connectable resolution, connection, five-service GATT inventory, and disconnect on the real meter. The separate `notification_observer.py` observed failed standard Glucose subscriptions and a successful custom `1524` subscription with zero notifications during navigation on the only existing uric-acid result. **Stage 2E's real `protocol_probe.py` run succeeded with the meter ON:** Home Assistant subscribed to custom `1524`, validated the captured `0x22` wake and `0x24` project exchanges with project `0x4183`, unsubscribed, and disconnected. An earlier Stage 1C connection while the display appeared off is separate evidence. Stage 2F adds a separately invoked, still physically untested, one-slot read-oriented probe after that identity gate; its selector correction awaits review and physical testing is paused. It returns no record payload, measurement, or timestamp. The selected HA scanner/proxy remains unknown and is deferred to Stage 9; Auto-mode advertisement and address identity remain Stage 6 work. These development actions do not implement production discovery, synchronization, or entities. Future production transport still belongs in `bluetooth.py`; `protocol.py` remains independent of Home Assistant and Bluetooth.

## Documentation and packaging

The custom integration uses `translations/en.json` for runtime localization. `strings.json` is included only to match the requested repository structure; Home Assistant's custom integration guidance does not use it as a runtime translation source. Manifest version `0.0.0` is a development placeholder required for a custom integration, not a release. The repository layout targets HACS; HACS readiness is a Stage 10 gate.
