"""The Uconnect homeassistant integration"""
from __future__ import annotations
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_PIN, CONF_PASSWORD, CONF_USERNAME, CONF_ROOM, Platform

import homeassistant.helpers.config_validation as cv

from .coordinator import PollingCoordinator
from .uconnect_api import Uconnect_API

DOMAIN = 'uconnect_sensor'
COORDINATOR = 'coordinator'
API = 'api'

PLATFORMS = [
    #Platform.BINARY_SENSOR,
    #Platform.BUTTON,
    #Platform.LOCK,
    #Platform.NOTIFY,
    #Platform.NUMBER,
    #Platform.SELECT,
    Platform.SENSOR,
    #Platform.SWITCH,
    Platform.DEVICE_TRACKER 
]

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration

SERVICE_SCHEMA = vol.Schema(
    vol.Any(
        {vol.Required(CONF_USERNAME): cv.string},
        {vol.Required(CONF_PASSWORD): cv.string},
        {vol.Required(CONF_PIN): cv.string},
    )
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:

    hass.data[DOMAIN] = {
        'username': config[DOMAIN][CONF_USERNAME],
        'password': config[DOMAIN][CONF_PASSWORD],
        'pin': config[DOMAIN][CONF_PIN]
    }
    api = Uconnect_API(
                            hass.data[DOMAIN][CONF_USERNAME],
                            hass.data[DOMAIN][CONF_PASSWORD],
                            hass.data[DOMAIN][CONF_PIN]
                            )

    hass.data[DOMAIN][API] = api


    hass.data[DOMAIN][COORDINATOR] = PollingCoordinator(hass, api )
    
    await hass.data[DOMAIN][COORDINATOR].async_config_entry_first_refresh()

    for p in PLATFORMS:
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform(p, DOMAIN, {}, config)
        )

    return True