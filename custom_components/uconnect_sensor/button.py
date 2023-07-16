"""Implementation of a Switch for HAVAC"""
from __future__ import annotations
import logging


from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import ButtonEntity


from homeassistant.helpers.entity import generate_entity_id


from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from . import DOMAIN, COORDINATOR, API, Uconnect_API
from requests import get

# from requests import async
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    entities: list[UconnectButtonEntity] = []

    entities.extend([UconnectButtonEntity(hass.data[DOMAIN][API], hass)])

    async_add_entities(entities)


class UconnectButtonEntity(ButtonEntity):
    """Representation of Uconnect entity."""

    def __init__(self, api: Uconnect_API, hass) -> None:
        self.api = api
        self.hass = hass
        self._attr_icon = "mdi:air-conditioner"
        self._attr_unique_id = generate_entity_id("351354", "35", hass=hass)

    @property
    def is_on(self) -> bool:
        """Return the entity value to represent the entity state."""
        return False

    @property
    def name(self) -> str:
        """Return the name"""
        return "Uconnect HAVAC"

    async def async_press(self) -> None:
        # self.api.precond_on()
        # await self.hass.async_create_task(self.api.precond_on)
        await self.hass.async_add_executor_job(self.api.precond_on)
