"""Implementation of a Switch for HAVAC"""
from __future__ import annotations
import logging

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.core import callback

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)


from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from . import DOMAIN, COORDINATOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    _LOGGER.info('dsfasd')
    coordinator = hass.data[DOMAIN][COORDINATOR]
    entities: list[UconnectTracker] = []

    entities.extend([
        UconnectTracker(coordinator, 'device_tracker')
    ])

    async_add_entities(
        entities
    )





class UconnectTracker(CoordinatorEntity, TrackerEntity):
    """Base class for a tracked device."""
    
    def __init__(self, coordinator: Any, context: Any = None) -> None:
        super().__init__(coordinator, context)
        self._latitude = None
        self._longitude = None
        
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data['device_tracker'][self.key]
        location = Uconnect_location(data).get_data()
        self._latitude = location['latitude']
        self._longitude = location['longitude']
        self.async_write_ha_state()
        
    @property
    def source_type(self) -> SourceType:
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS

    @property
    def should_poll(self) -> bool:
        """No polling for entities that have location pushed."""
        return True

    @property
    def force_update(self) -> bool:
        """All updates need to be written to the state machine if we're not polling."""
        return not self.should_poll

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
