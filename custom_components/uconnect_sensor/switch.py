"""Implementation of a Switch for HAVAC"""
from __future__ import annotations
import logging
from homeassistant.const import PERCENTAGE, UnitOfLength, CONF_PIN, CONF_PASSWORD, CONF_USERNAME
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.entity import generate_entity_id


from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from . import DOMAIN, COORDINATOR, API
from requests import get
#from requests import async
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:

    entities: list[UconnectSwitch] = []

    entities.extend([
        UconnectSwitch(hass.data[DOMAIN][API], hass)
    ])

    async_add_entities(
        entities
    )


class UconnectSwitch(SwitchEntity):
    """Representation of Uconnect entity."""

    

    def __init__(
        self, api, hass
    ) -> None:
        self.api = api
        self._attr_icon = 'mdi:air-conditioner'
        self._attr_unique_id = generate_entity_id('12354','65194654', hass=hass)

    @property
    def is_on(self) -> bool:
        """Return the entity value to represent the entity state."""
        return False
    
    @property
    def name(self) -> str:
        """Return the name"""
        return 'Uconnect HAVAC Switch'

    async def async_turn_on(self, **kwargs: Any) -> None:
        _LOGGER.error("TEST")

        self.coordinator.async_update_listeners()

    async def async_turn_off(self, **kwargs: Any) -> None:
        _LOGGER.error("TEST")

        self.coordinator.async_update_listeners()

