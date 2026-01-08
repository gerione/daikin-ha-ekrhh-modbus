from .const import (
    CONF_ADDITIONAL_ZONE,
    CONF_ISAIR2AIR,
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_ADDITIONAL_ZONE,
    DEFAULT_AIR2AIR,
    CONF_MAX_POWER,
    CONF_MAX_WATER_TEMP,
    DEFAULT_MAX_POWER,
    DEFAULT_MAX_WATER_TEMP,
    CONF_ALTHERMA_VERSION,
    DEFAULT_ALTHERMA_VERSION,
)
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import callback
import ipaddress
import re
import voluptuous as vol


DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_ALTHERMA_VERSION, default=DEFAULT_ALTHERMA_VERSION): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_ISAIR2AIR, default=DEFAULT_AIR2AIR): bool,
        vol.Required(CONF_ADDITIONAL_ZONE, default=DEFAULT_ADDITIONAL_ZONE): bool,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        vol.Optional(CONF_MAX_POWER, default=DEFAULT_MAX_POWER): vol.All(
            int, vol.Range(min=2, max=20)
        ),
        vol.Optional(CONF_MAX_WATER_TEMP, default=DEFAULT_MAX_WATER_TEMP): vol.All(
            int, vol.Range(min=50, max=80)
        ),
    }
)


def host_valid(host):
    """Return True if hostname or IP address is valid."""
    try:
        if ipaddress.ip_address(host).version == (4 or 6):
            return True
    except ValueError:
        disallowed = re.compile(r"[^a-zA-Z\d\-]")
        return all(x and not disallowed.search(x) for x in host.split("."))


OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT): int,
        vol.Required(CONF_ALTHERMA_VERSION): str,
        vol.Required(CONF_ISAIR2AIR): bool,
        vol.Required(CONF_ADDITIONAL_ZONE): bool,
        vol.Required(CONF_MAX_POWER): vol.All(int, vol.Range(min=2, max=20)),
        vol.Required(CONF_MAX_WATER_TEMP): vol.All(int, vol.Range(min=50, max=80)),
        vol.Optional(CONF_SCAN_INTERVAL): int,
    }
)


class OptionsFlowHandler(config_entries.OptionsFlowWithReload):
    async def async_step_init(
        self,
        user_input: dict[str, any] | None = None,  # type: ignore
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            if CONF_NAME in self.config_entry.data:
                user_input[CONF_NAME] = self.config_entry.data[CONF_NAME]
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input, options=self.config_entry.options
            )
            # return self.async_create_entry(title="", data={})
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.data
            ),
        )


class DaikinHaEkrhhModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 4
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            valid_host = host_valid(user_input[CONF_HOST])
            if not valid_host:
                errors[CONF_HOST] = "invalid host IP"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler()
