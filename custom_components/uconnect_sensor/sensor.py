"""Example integration using DataUpdateCoordinator."""
from __future__ import annotations

import logging
import json



from homeassistant.const import PERCENTAGE, UnitOfLength, CONF_PIN, CONF_PASSWORD, CONF_USERNAME
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .uconnect_api import Uconnect_API

from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from . import DOMAIN, COORDINATOR
from requests import get
#from requests import async
_LOGGER = logging.getLogger(__name__)

#DOMAIN = 'uconnect_sensor'

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Config entry example."""
    # assuming API object stored here by __init__.py
    
    coordinator = hass.data[DOMAIN][COORDINATOR]

    async_add_entities(
        UconnectSensor(coordinator, key) for key in coordinator.data['sensor']
    )



class UconnectSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, key):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._state = None
        self.key = key
        self.sensor_name = key
        self._unit = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data[self.key]['sensor']

        self._state = data.value
        self._unit = data.unit_of_measurement
        self._attr_device_class = data.device_class
        self.sensor_name = data.display_name
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return 'Uconnect ' + self.sensor_name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit


    