# Stage 2E — Home Assistant proprietary identity probe

**State:** COMPLETE. The user supplied a privacy-safe result from a successful real GD82 Home Assistant run. The meter was **ON** during this Stage 2E exchange.

## Evidence and boundary

The private Stage 2C app capture, summarized in [the sanitized evidence record](STAGE2C_GD82_LIVE_PROTOCOL_CAPTURE.md), confirmed custom service `00001523-1212-efde-1523-785feabcd123`, custom Write/Notify characteristic `00001524-1212-efde-1523-785feabcd123`, wake command `0x22`, project query `0x24`, and GD82 project ID `0x4183`. That capture enabled custom notifications before writing. Stage 2D's HA-independent `protocol.py` constructs and validates those fixed eight-byte frames.

The manually invoked `fora6_connect.probe_protocol_identity` action uses a private runtime-only Bluetooth address and Home Assistant's connectable-device resolver. It checks the custom characteristic's Write and Notify properties, subscribes to it, writes the fixed wake request once, validates its command-matched checksummed response, writes the fixed project request once, validates its response and requires project `0x4183`, then stops notification and disconnects. Its only application writes are to custom `1524`: `0x22` and `0x24`, both with explicit Bleak `response=True`. That write mode is a bounded transport choice supported by the observed Write property, not a universal FORA protocol rule. Stack-managed CCCD activity for the subscription is expected.

All waits are bounded. Invalid, mismatched, or timed-out responses stop the sequence; there is no application-command retry. The action returns flags, the public project ID, and sanitized failure categories. It does not return the supplied address or raw request/notification bytes. It does not pair, issue RACP, access standard Glucose characteristics, retrieve records, parse measurements, or start a production sync. The selected local adapter or ESPHome proxy is chosen by Home Assistant and is not hard-coded.

## Controlled physical test

1. Copy the complete `custom_components/fora6_connect/` directory from this checkpoint into the Home Assistant configuration directory at `custom_components/fora6_connect/`, replacing the installed development copy. Include `protocol_probe.py`, `protocol.py`, `__init__.py`, `services.yaml`, `translations/en.json`, and the other existing integration files. Keep the private address out of Git and shared documentation.
2. If the integration is not already loaded for development, add `fora6_connect:` to `configuration.yaml`. Restart **Home Assistant Core** to load the new Python code, service metadata, and translations. The generic ESPHome proxy firmware does not need to be changed for this action.
3. Put the meter in its normal Bluetooth transfer state. Use Home Assistant's Bluetooth Advertisement Monitor to confirm the meter's row is current; for this controlled test, Lounge may temporarily use Active mode, as in Stage 1B. The action itself does not request or depend on a new advertisement callback. No new health measurement is needed.
4. In **Developer Tools → Actions**, select `fora6_connect.probe_protocol_identity`. Privately enter the already identified meter's Bluetooth address in the required `address` field. Request the action response and invoke it once. Do not place the address in a screenshot, issue, or shared result.
5. Share only the privacy-safe structured action result. The observed Stage 2E run returned `identity_confirmed: true`, `project_id: 16771` (`0x4183`), both response-valid flags true, and clean notification/disconnect flags. An error result's `error_stage`/`error_code` identifies the bounded failure gate without exposing packets.

The response fields are `device_found`, `connectable_device_resolved`, `connection_successful`, `connected_via_ha_bluetooth`, `custom_characteristic_found`, `notification_subscription_successful`, `wake_write_successful`, `wake_response_valid`, `project_query_write_successful`, `project_response_valid`, `project_id`, `expected_project_id`, `project_id_matches`, `notification_stopped_cleanly`, `disconnected_cleanly`, `identity_confirmed`, `error_stage`, `error_code`, and `cleanup_errors`.

## Real Stage 2E observation — user-supplied

With the physical GD82 **ON**, the action reported `device_found`, `connectable_device_resolved`, `connection_successful`, `connected_via_ha_bluetooth`, `custom_characteristic_found`, `notification_subscription_successful`, `wake_write_successful`, `wake_response_valid`, `project_query_write_successful`, `project_response_valid`, `project_id_matches`, `notification_stopped_cleanly`, `disconnected_cleanly`, and `identity_confirmed` all true. `project_id` and `expected_project_id` were both `16771` (`0x4183`). `error_stage` and `error_code` were null; `cleanup_errors` was empty. This confirms the bounded Home Assistant custom identity path. It does not identify the selected scanner/proxy or establish any record operation.

An earlier, separate Stage 1C notification observer connected while the meter display appeared off. That observation does **not** show that the Stage 2E wake/project exchange worked while off. No address, raw notification, health value, or private timestamp is recorded here.

**Next gate:** Stage 2F offline review of exact and non-destructive TD4183 record requests. No new live record command follows automatically from Stage 2E closure.

**Later Stage 2F update:** That offline review has now traced a bounded, read-oriented index-zero request path and a separate development-only action implements it. This Stage 2E action and its successful ON-state result are unchanged. The Stage 2F physical result is pending; see [the Stage 2F evidence record](STAGE2F_TD4183_RECORD_PROBE.md).
