# Stage 5 — measurement and entity model

**State:** Complete for the separately authorized evidence-bounded product and entity architecture. No numeric Home Assistant sensor is exposed: tracked evidence does not establish the uric-acid display unit. No physical test, Bluetooth action, production synchronization, or polling was performed or added.

## Evidence boundary and unit conclusion

The tracked Stage 2C evidence says the private iFORA HM import's displayed uric-acid number matched the parsed raw number divided by ten. It deliberately omits the specimen value and timestamp, and names no displayed unit. The Stage 2G schema likewise says no uric-acid unit is assigned; byte 4's physical meaning and unit are unresolved. The auxiliary byte is therefore not a unit source. The tracked repository establishes the `/10` numeric transformation for identified valid uric-acid records, but does **not** establish the displayed unit for the GD82/iFORA HM path.

Consequently, no numeric Home Assistant SensorEntity is created in this stage. The product model carries the evidence-backed scaled number for uric acid with `unit=None` and an explicit unit-unresolved status. The entity mapping returns no numeric state while the unit is absent. This avoids turning a scaled number with unknown dimensional meaning into a public sensor.

The other app-mapped analytes—General, hematocrit, ketone, uric acid, cholesterol, hemoglobin, lactate, and triglyceride—remain identifiable as protocol enums where their selector is known. Only uric acid receives numeric scaling. The other analytes have no supported product numeric value because their scaling and units are not both established. Unknown selector values remain unknown.

## Model and boundary

The layers are:

```text
ProtocolFrame
  → TD4183RecordPartOne / TD4183RecordPartTwo
  → TD4183Record
  → Fora6Measurement
  → in-memory entity-state mapping
  → future Home Assistant SensorEntity, only after its evidence gates
```

`measurement.py` is pure Python and maps only an already validated `TD4183Record`. `Fora6Measurement` contains:

- known analyte enum or `None` for an unknown selector;
- `scaled_number`, populated only for a valid identified uric-acid record;
- `unit`, fixed to `None` until evidence establishes it;
- the original app-mapped category and derived `is_qc` flag;
- the transmitted flag;
- `meter_local_time` as a naive, minute-precision wall-clock `datetime`;
- `value_status`, distinguishing invalid raw sentinel, unknown analyte, unsupported analyte scaling, and unresolved uric-acid unit.

The product model omits raw wire value, record identifiers, deduplication keys, sync time, addresses, clinical interpretation, and normal/abnormal classifications. It does not attach a timezone or convert meter time to Home Assistant ingestion time.

## Invalid values and category policy

The raw `0xFFFF` sentinel maps to `scaled_number=None` with invalid status. It is never divided, converted to zero, or passed to the sensor state. `MeasurementState.replace()` replaces the previous product record, including when the new record is invalid or unsupported; its derived sensor value is then `None`, so an older numeric state cannot be retained accidentally.

Categories remain distinct. QC is only the evidence-backed app category; it is not given another meaning or policy. The state mapper excludes QC from the ordinary measurement sensor. AC and PC remain separate categories with no expansion or clinical interpretation. The ordinary measurement mapping currently accepts only General category records, but still returns no number while unit evidence is missing. A future QC-specific exposure decision remains separate.

## Entity and device architecture

`sensor.py` contains only an inert measurement-to-native-value mapping, a replaceable in-memory `MeasurementState`, and `meter_device_identifier()`. It defines no `SensorEntity`, platform setup hook, polling/update method, background task, or Bluetooth dependency. The integration does not forward a sensor platform. Sensor properties will later read in-memory product state only; record retrieval belongs to a separately authorized synchronization stage.

Stage 6 must provide an evidence-backed stable meter identity. `meter_device_identifier(stable_identifier)` returns the shared `(DOMAIN, stable_identifier)` key that each future entity for that meter will use in its `DeviceInfo.identifiers`. It derives nothing from a Bluetooth address, local name, UUID, or manufacturer data. There is no current device registration: Home Assistant device attachment requires a config entry and entity unique ID, which await Stage 6 setup. This follows the current [Home Assistant device registry guidance](https://developers.home-assistant.io/docs/device_registry_index/) and [entity registry properties](https://developers.home-assistant.io/docs/core/entity/).

No device class or state class is selected. A future numeric sensor must use the supported Home Assistant sensor API only after its measurement unit is established; device class and state class will be chosen only if their semantics and requirements fit the evidence. Sensor properties must remain memory-only and must not initiate BLE I/O, consistent with [Home Assistant sensor guidance](https://developers.home-assistant.io/docs/core/entity/sensor/).

## Deferred work

- Establish the uric-acid display unit from evidence specific to the GD82/iFORA HM path before creating a numeric uric-acid sensor.
- Establish both unit and scaling independently for every other analyte before mapping numeric values.
- Resolve auxiliary-byte meaning, code-number independent meaning, and AC/PC semantics without inference.
- Keep QC-specific exposure policy separate; do not imply QC means a control solution.
- Stage 6 must establish stable device identity, config entry setup, and one-device association before device registration or entity creation.
- Later synchronization work must feed product measurements without giving entities responsibility for Bluetooth, polling, record iteration, persistence, or deduplication.

**Exact next gate:** separately authorize Stage 6 device discovery and identity policy, or a focused evidence follow-up to establish the uric-acid display unit. Do not begin Stage 6 automatically. No private health data or captured frames are used in the tests.
