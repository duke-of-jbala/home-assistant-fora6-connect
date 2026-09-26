"""Temporary Stage 1B GATT inventory probe; no characteristic I/O."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from bleak_retry_connector import (
    BleakClientWithServiceCache,
    BleakOutOfConnectionSlotsError,
    establish_connection,
)
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import CHARACTERISTIC_UUID, NAME, SERVICE_UUID

TARGET_LOCAL_NAME = "FORA 6 CONNECT"
CONNECTION_TIMEOUT = 20.0
DISCONNECT_TIMEOUT = 10.0
ADVERTISEMENT_TIMEOUT = 20
ADVERTISEMENT_POLL_INTERVAL = 1.0
SIG_BASE = "-0000-1000-8000-00805f9b34fb"
_LOGGER = logging.getLogger(__name__)


class ProbeError(Exception):
    """A privacy-safe failure message for the manual service action."""


def _uuid128(value: str) -> str:
    """Normalize standard 16-bit UUIDs for comparison with Bleak UUIDs."""
    value = str(value).lower()
    return f"0000{value}{SIG_BASE}" if len(value) == 4 else value


def normalize_local_name(name: str | None) -> str | None:
    """Remove only trailing NUL padding from an advertised local name."""
    return name.rstrip("\x00") if name is not None else None


def _advertised_local_name(info: Any) -> str | None:
    """Get the normalized packet name, separate from HA's resolved name."""
    return normalize_local_name(
        getattr(getattr(info, "advertisement", None), "local_name", None)
    )


def _enumerate_services(services: Any) -> list[dict[str, Any]]:
    """Copy only public GATT UUIDs and characteristic properties."""
    return [
        {
            "uuid": str(service.uuid).lower(),
            "characteristics": [
                {
                    "uuid": str(characteristic.uuid).lower(),
                    "properties": sorted(
                        str(prop).lower() for prop in characteristic.properties
                    ),
                }
                for characteristic in service.characteristics
            ],
        }
        for service in services
    ]


def _expected_gatt(observed: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare observed metadata with the prior iPhone GATT inventory."""
    by_service = {_uuid128(item["uuid"]): item for item in observed}
    expected_chars = (
        ("1808", "2a18", ("notify",)),
        ("1808", "2a34", ("notify",)),
        ("1808", "2a51", ("read",)),
        ("1808", "2a52", ("write", "indicate")),
        (SERVICE_UUID, CHARACTERISTIC_UUID, ("write", "notify")),
    )
    comparisons = []
    for service_uuid, char_uuid, properties in expected_chars:
        service = by_service.get(_uuid128(service_uuid), {})
        characteristics = {
            _uuid128(item["uuid"]): item
            for item in service.get("characteristics", ())
        }
        found = characteristics.get(_uuid128(char_uuid))
        observed_properties = found["properties"] if found else []
        comparisons.append(
            {
                "service_uuid": _uuid128(service_uuid),
                "uuid": _uuid128(char_uuid),
                "present": found is not None,
                "expected_properties": list(properties),
                "observed_properties": observed_properties,
                "expected_properties_present": (
                    set(properties) <= set(observed_properties)
                ),
            }
        )
    return {
        "device_information_service_present": _uuid128("180a") in by_service,
        "glucose_service_present": _uuid128("1808") in by_service,
        "fora_custom_service_present": _uuid128(SERVICE_UUID) in by_service,
        "characteristics": comparisons,
    }


async def async_probe_gatt(hass: HomeAssistant, address: str) -> dict[str, Any]:
    """Find a fresh advertisement, connect through HA, and list GATT metadata."""
    scanner_count = bluetooth.async_scanner_count(hass, connectable=True)
    _LOGGER.debug("GATT probe: connectable scanners=%d", scanner_count)
    if not scanner_count:
        _LOGGER.debug("GATT probe: no connectable Home Assistant scanner")
        raise ProbeError(
            "No connectable Home Assistant Bluetooth scanner is available."
        )

    try:
        baseline = bluetooth.async_last_service_info(hass, address, connectable=False)
        baseline_time = baseline.time if baseline is not None else float("-inf")
        wait_started = bluetooth.MONOTONIC_TIME()
        bluetooth.async_clear_advertisement_history(hass, address)
    except Exception:
        raise ProbeError(
            "Home Assistant could not prepare the targeted advertisement wait."
        ) from None

    targeted_callback_received = False
    latest_service_info_advanced = False

    def _is_fresh_fora(info: Any) -> bool:
        # async_process_advertisements may replay cached history on registration.
        # A live packet may omit the local name; the user selected its address
        # privately from the previously identified Advertisement Monitor row.
        if info.address != address:
            return False
        local_name = _advertised_local_name(info)
        return (
            (not local_name or local_name == TARGET_LOCAL_NAME)
            and info.time > max(wait_started, baseline_time)
        )

    def _matches_callback(info: Any) -> bool:
        nonlocal targeted_callback_received
        if info.address == address:
            targeted_callback_received = True
        return _is_fresh_fora(info)

    fresh_info = None
    freshness_source = None
    wait_failed = False
    _LOGGER.debug("GATT probe: targeted active advertisement wait started")
    wait_task = asyncio.create_task(
        bluetooth.async_process_advertisements(
            hass,
            _matches_callback,
            # HA's callback matcher defaults to connectable-only when omitted.
            {"address": address, "connectable": False},
            bluetooth.BluetoothScanningMode.ACTIVE,
            ADVERTISEMENT_TIMEOUT,
        )
    )
    try:
        while fresh_info is None:
            done, _ = await asyncio.wait(
                {wait_task}, timeout=ADVERTISEMENT_POLL_INTERVAL
            )
            if done:
                try:
                    callback_info = wait_task.result()
                except TimeoutError:
                    pass
                except Exception:
                    wait_failed = True
                else:
                    if callback_info.address == address:
                        targeted_callback_received = True
                    if _is_fresh_fora(callback_info):
                        fresh_info = callback_info
                        freshness_source = "targeted_callback"

            latest_info = bluetooth.async_last_service_info(
                hass, address, connectable=False
            )
            if (
                latest_info is not None
                and latest_info.address == address
                and latest_info.time > max(wait_started, baseline_time)
            ):
                latest_service_info_advanced = True
                if fresh_info is None and _is_fresh_fora(latest_info):
                    fresh_info = latest_info
                    freshness_source = "latest_service_info"

            if done:
                break
    except Exception:
        _LOGGER.debug("GATT probe: latest advertisement check failed")
        raise ProbeError(
            "Home Assistant could not check the latest advertisement."
        ) from None
    finally:
        if not wait_task.done():
            wait_task.cancel()
            await asyncio.gather(wait_task, return_exceptions=True)

    _LOGGER.debug(
        "GATT probe: targeted callback received=%s; latest service info advanced=%s; "
        "fresh observation established=%s",
        targeted_callback_received,
        latest_service_info_advanced,
        fresh_info is not None,
    )
    if fresh_info is None:
        _LOGGER.debug(
            "GATT probe: fresh observation=false; connectable BLEDevice resolved=false; "
            "GATT connection attempted=false; connection successful=false"
        )
        if wait_failed:
            raise ProbeError(
                "Home Assistant could not complete the targeted active wait."
            )
        raise ProbeError(
            "No fresh FORA 6 CONNECT advertisement was observed during the "
            "targeted active wait."
        )

    local_name = _advertised_local_name(fresh_info)
    _LOGGER.debug("GATT probe: fresh observation established via %s", freshness_source)
    ble_device = bluetooth.async_ble_device_from_address(
        hass, fresh_info.address, connectable=True
    )
    _LOGGER.debug("GATT probe: connectable BLEDevice resolved: %s", ble_device is not None)
    if ble_device is None:
        _LOGGER.debug(
            "GATT probe: GATT connection attempted=false; connection successful=false"
        )
        raise ProbeError(
            "FORA 6 CONNECT was seen, but no connectable BLEDevice is available."
        )

    _LOGGER.debug("GATT probe: connection attempted")
    try:
        client = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            NAME,
            max_attempts=2,
            use_services_cache=False,
            timeout=CONNECTION_TIMEOUT,
            pair=False,
        )
    except BleakOutOfConnectionSlotsError:
        _LOGGER.debug("GATT probe: connection successful=false (no slot)")
        raise ProbeError(
            "No Bluetooth proxy/adapter connection slot is available."
        ) from None
    except Exception:
        _LOGGER.debug("GATT probe: connection successful=false")
        raise ProbeError(
            "Bluetooth connection failed or the device disappeared; "
            "check reachability privately."
        ) from None

    result: list[dict[str, Any]] | None = None
    failure: ProbeError | None = None
    try:
        if not client.is_connected:
            raise ProbeError("The meter disconnected before GATT discovery.")
        _LOGGER.debug("GATT probe: connection successful=true")
        services = client.services
        _LOGGER.debug("GATT probe: GATT enumeration reached")
        if services is None:
            raise ProbeError("GATT services were unavailable after connection.")
        result = _enumerate_services(services)
        if not result:
            raise ProbeError("No GATT services were returned after connection.")
        if not client.is_connected:
            raise ProbeError("The meter disconnected during GATT discovery.")
    except ProbeError as err:
        failure = err
    except Exception:
        failure = ProbeError("GATT service discovery failed or the peer disconnected.")
    finally:
        _LOGGER.debug("GATT probe: disconnect attempted")
        try:
            await asyncio.wait_for(client.disconnect(), timeout=DISCONNECT_TIMEOUT)
        except Exception:
            _LOGGER.debug("GATT probe: disconnect did not complete cleanly")
            raise ProbeError(
                "GATT probe could not confirm a clean disconnect."
            ) from None
        _LOGGER.debug("GATT probe: disconnect completed")

    if failure is not None:
        raise failure
    assert result is not None
    return {
        "device_found": True,
        "local_name": local_name,
        "advertised_name_confirmed": local_name == TARGET_LOCAL_NAME,
        "active_scan_requested": True,
        "targeted_callback_received": targeted_callback_received,
        "latest_service_info_advanced": latest_service_info_advanced,
        "freshness_source": freshness_source,
        "fresh_advertisement_observed": True,
        "connectable_device_resolved": True,
        "connectable_scanner_count": scanner_count,
        "gatt_connection_attempted": True,
        "connection_successful": True,
        "connected_via_ha_bluetooth": True,
        "gatt_service_count": len(result),
        "services": result,
        "expected_gatt": _expected_gatt(result),
        "disconnected_cleanly": True,
    }
