"""Example integration using DataUpdateCoordinator."""
from __future__ import annotations


import logging
from typing import Any


import async_timeout


from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from custom_components.uconnect_sensor.uconnect import Uconnect_location

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
        CarTracker(coordinator, 'device_tracker')
    )


class CarTracker(CoordinatorEntity, TrackerEntity):
    """Base class for a tracked device."""
    
    def __init__(self, coordinator: Any, context: Any = None) -> None:
        super().__init__(coordinator, context)
        self._latitude = None
        self._longitude = None
        
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data[self.key]['device_tracker']
        location = Uconnect_location(data).get_data()
        self._latitude = location['latitude']
        self._longitude = location['longitude']
        self.async_write_ha_state()
        
    @property
    def source_type(self) -> SourceType | str:
        return 'Uconnect Car'

    @property
    def should_poll(self) -> bool:
        """No polling for entities that have location pushed."""
        return False

    @property
    def force_update(self) -> bool:
        """All updates need to be written to the state machine if we're not polling."""
        return not self.should_poll

    @property
    def location_accuracy(self) -> int:
        """Return the location accuracy of the device.

        Value in meters.
        """
        return 0

    @property
    def location_name(self) -> str | None:
        """Return a location name for the current location of the device."""
        return None

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        raise NotImplementedError

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        raise NotImplementedError
