"""Example integration using DataUpdateCoordinator."""
from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout

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
from . import DOMAIN
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
    
    coordinator = MyCoordinator(hass, 
                        Uconnect_API(
                            hass.data[DOMAIN][CONF_USERNAME],
                            hass.data[DOMAIN][CONF_PASSWORD],
                            hass.data[DOMAIN][CONF_PIN]
                            ))
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        UconnectSensor(coordinator, key) for key in coordinator.data
    )

class Car_Information():
    def __init__(   self, value: str, 
                    device_class: str, 
                    display_name: str,
                    unit_of_measurement: str = None) -> None:
        self.value = value
        self.device_class = device_class
        self.unit_of_measurement = unit_of_measurement
        self.display_name = display_name


class Uconnect_Information():
    def __init__(self, data: str) -> None:
        
        battery_infos = data['evInfo']['battery']

        self.charging_level = Car_Information(
                                battery_infos['chargingLevel'],
                                'enum',
                                'Charging Level'
                                )
        self.charging_status = Car_Information(
                                battery_infos['chargingStatus'],
                                'enum',
                                'Charging Status'
                                )
        self.distance_to_empty = Car_Information(
                                battery_infos['distanceToEmpty']['value'],
                                'distance',
                                'Distance to empty',
                                UnitOfLength.KILOMETERS 
                                )
        self.plug_in_status = Car_Information(
                                battery_infos['plugInStatus'],
                                'distance',
                                'Plug in status'
                                )
        self.state_of_charge = Car_Information(
                                battery_infos['stateOfCharge'],
                                'battery',
                                'State of Charge',
                                PERCENTAGE
                                )
        self.total_range = Car_Information(
                                battery_infos['totalRange'],
                                'distance',
                                'Total Range',
                                UnitOfLength.KILOMETERS
                                )
    
    
    def get_data(self) -> dict:
        
        return_dict = {
            'chargingLevel' : self.charging_level,             
            'chargingStatus': self.charging_status, 
            #'distanceToEmpty_unit': self.distance_to_empty_unit,    
            'distanceToEmpty': self.distance_to_empty,   
            'plugInStatus' : self.plug_in_status,        
            'stateOfCharge' : self.state_of_charge,
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
            update_interval=timedelta(seconds=600),
        )
        self.api = api
        

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:

            async with async_timeout.timeout(10):

                result = await self.hass.async_add_executor_job(self.api.fetch_data)

                Uconnect_Information(result).get_data()

                data = Uconnect_Information(result).get_data()

                return data
        except Exception as e:
            raise UpdateFailed(f"Error communicating with API: {e}")


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
        data = self.coordinator.data[self.key]

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


    