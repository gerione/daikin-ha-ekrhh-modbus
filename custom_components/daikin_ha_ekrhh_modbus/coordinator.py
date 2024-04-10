"""Coordinator for Modbus HA EKRHH integration."""
from __future__ import annotations

import logging
from datetime import datetime
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .device import DaikinOnectaDevice

_LOGGER = logging.getLogger(__name__)


class OnectaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self.options = config_entry.options

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=self.determine_update_interval(hass),
        )

        _LOGGER.info(
            "Daikin coordinator initialized with %s interval.",
            self.update_interval,
        )

    async def _async_update_data(self):
        _LOGGER.debug("Daikin coordinator start _async_update_data.")

        devices = self.hass.data[DOMAIN][DAIKIN_DEVICES]


    def update_settings(self, config_entry: ConfigEntry):
        _LOGGER.debug("Daikin coordinator updating settings.")
        self.options = config_entry.options
