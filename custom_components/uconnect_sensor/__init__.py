"""The Uconnect homeassistant integration"""
from __future__ import annotations
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_PIN, CONF_PASSWORD, CONF_USERNAME, CONF_ROOM

import homeassistant.helpers.config_validation as cv

DOMAIN = 'uconnect_sensor'
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
    """Your controller/hub specific code."""

    hass.data[DOMAIN] = {
        'username': config[DOMAIN][CONF_USERNAME],
        'password': config[DOMAIN][CONF_PASSWORD],
        'pin': config[DOMAIN][CONF_PIN]
    }
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {}, config)
    )
    return True