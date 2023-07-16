from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity

from homeassistant.config_entries import ConfigEntry

from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from . import DOMAIN, COORDINATOR


# from requests import async
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    # config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Config entry example."""
    # assuming API object stored here by __init__.py

    coordinator = hass.data[DOMAIN][COORDINATOR]

    async_add_entities(
        UconnectSensor(coordinator, key, hass) for key in coordinator.data["sensor"]
    )


class UconnectSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, hass):
        super().__init__(coordinator)
        self._state = None
        self.key = key
        self.sensor_name = key
        self._unit = None
        self._attr_unique_id = generate_entity_id(f"41369481_{key}", key, hass=hass)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data["sensor"][self.key]
        self._state = data.value
        self._unit = data.unit_of_measurement
        self._attr_device_class = data.device_class
        self.sensor_name = data.display_name
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Uconnect " + self.sensor_name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit
