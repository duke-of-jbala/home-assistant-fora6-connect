# Development

## Stage discipline

Read `AGENTS.md`, `CURRENT_STATUS.md`, and `PROTOCOL.md` before implementation. The integration code remains a Stage 0 skeleton while Stage 1 discovery continues. Protocol, config flow, transport, and entities are intentionally inactive.

Document every future protocol conclusion with its source, date, capture conditions, confidence, and sanitized fixture when possible. Add parser tests before using decoded data in Home Assistant. Never substitute the time of synchronization for the original meter timestamp.

## Local checks

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q custom_components tests
```

If Ruff is installed:

```bash
ruff check .
ruff format --check .
```

These checks do not validate runtime Home Assistant behavior. Home Assistant and HACS validation belong to later stages once setup and transport exist.

## Integration scaffold

The custom integration manifest has no `config_flow` flag or Bluetooth discovery matcher. This prevents a user flow from claiming an unverified meter identity. No entity platform is forwarded. `translations/en.json` is the runtime translation file for custom integrations. `strings.json` is retained as an empty requested scaffold file, not used at runtime.

The `0.0.0` manifest version is a development placeholder needed for a custom integration, not a release number. HACS packaging and brand assets are deferred to Stage 10.

References checked during bootstrap: [Home Assistant integration manifests](https://developers.home-assistant.io/docs/creating_integration_manifest/), [custom integration localization](https://developers.home-assistant.io/docs/internationalization/custom_integration/), [Bluetooth guidance](https://developers.home-assistant.io/docs/bluetooth/), and [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/). Recheck them at the relevant later stages because APIs and publication requirements can change.
