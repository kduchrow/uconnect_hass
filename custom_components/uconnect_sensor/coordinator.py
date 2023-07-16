import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

import async_timeout
from .uconnect import Uconnect_Information, Uconnect_location

_LOGGER = logging.getLogger(__name__)


class PollingCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="uconnect",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=1800),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            async with async_timeout.timeout(20):
                fetch_data_result = await self.hass.async_add_executor_job(
                    self.api.fetch_data
                )
                # fetch_location_result = await self.hass.async_add_executor_job(self.api.fetch_location)
                print(fetch_data_result)
                data = {
                    "sensor": Uconnect_Information(
                        fetch_data_result["status"]
                    ).get_data(),
                    "device_tracker": Uconnect_location(
                        fetch_data_result["location"]
                    ).get_data(),
                }

                print(data)

                return data
        except Exception as e:
            raise UpdateFailed(f"Error communicating with API: {e}")
