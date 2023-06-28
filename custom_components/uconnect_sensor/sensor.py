"""Example integration using DataUpdateCoordinator."""
from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout

from homeassistant.const import PERCENTAGE
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
#from . import DOMAIN
from requests import get
#from requests import async
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'uconnect_sensor'

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Config entry example."""
    # assuming API object stored here by __init__.py
    
    coordinator = MyCoordinator(hass, Uconnect_API())
    await coordinator.async_config_entry_first_refresh()

    #for key in coordinator.data:
    #    async_add_entities(
    #        UconnectSensor(coordinator, key) 
    #    )

    async_add_entities(
        UconnectSensor(coordinator, key) for key in coordinator.data
    )


class Uconnect_Information():
    def __init__(self, data: str) -> None:
        
        battery_infos = data['evInfo']['battery']
        self.charging_level             = battery_infos['chargingLevel']
        self.charging_status            = battery_infos['chargingStatus']
        #self.distance_to_empty_unit     = battery_infos['distanceToEmpty']['unit']
        self.distance_to_empty_value    = battery_infos['distanceToEmpty']['value']
        self.plug_in_status             = battery_infos['plugInStatus']
        self.state_of_charge            = battery_infos['stateOfCharge']
        self.total_range                = battery_infos['totalRange']
    
    
    def get_data(self) -> dict:
        
        return_dict = {
            'chargingLevel' : self.charging_level,             
            'chargingStatus':self.charging_status, 
            #'distanceToEmpty_unit': self.distance_to_empty_unit,    
            'distanceToEmpty_value': self.distance_to_empty_value ,   
            'plugInStatus' : self.plug_in_status    ,        
            'stateOfCharge' : self.state_of_charge ,
            'totalRange' :  self.total_range
        }
        
        
        return return_dict
        
    def __str__(self) -> str:
        
        return json.dumps(self.get_data(), indent=4, sort_keys=True)


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="uconnect",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
        )
        self.api = api
        

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                
                
                result = await self.hass.async_add_executor_job(self.api.fetch_data)

                Uconnect_Information(result).get_data()

                data = Uconnect_Information(result).get_data()

                return data
        except Exception as e:
            raise UpdateFailed(f"Error communicating with API: {e}")


class UconnectSensor(CoordinatorEntity, SensorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, coordinator, key):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._state = None
        self.key = key
        self.sensor_name = key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = self.coordinator.data[self.key]
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
        return PERCENTAGE


    