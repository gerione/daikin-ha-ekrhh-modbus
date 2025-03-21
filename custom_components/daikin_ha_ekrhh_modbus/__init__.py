import asyncio
import logging
import operator
import threading
from datetime import timedelta
from typing import Optional

import voluptuous as vol
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_MODBUS_ADDRESS,
    CONF_MODBUS_ADDRESS,
    CONF_ADDITIONAL_ZONE,
    CONF_ISAIR2AIR,
)

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["number", "sensor", "select"]
# PLATFORMS = ["number", "select", "sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Daikin EKRHH Modbus component."""
    # @TODO: Add setup code.
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a daikin_ekrhh mobus."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    port = entry.data[CONF_PORT]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]
    additional_zone = entry.data[CONF_ADDITIONAL_ZONE]
    is_air2air = entry.data[CONF_ISAIR2AIR]

    hub = DaikinEKRHHModbusHub(
        hass,
        name,
        host,
        port,
        scan_interval,
        additional_zone,
        is_air2air,
    )

    hass.data[DOMAIN][name] = {"hub": hub}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    """Unload daikin_ekrhh mobus entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if not unload_ok:
        return False

    hass.data[DOMAIN].pop(entry.data["name"])
    return True


# Example migration function
async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating configuration from version %s.%s",
        config_entry.version,
        config_entry.minor_version,
    )

    if config_entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    if config_entry.version == 1:
        new_data = {**config_entry.data}
        if config_entry.minor_version < 2:
            # TODO: modify Config Entry data with changes in version 1.2
            new_data[CONF_ISAIR2AIR] = False

        hass.config_entries.async_update_entry(
            config_entry, data=new_data, minor_version=2, version=1
        )

    _LOGGER.debug(
        "Migration to configuration version %s.%s successful",
        config_entry.version,
        config_entry.minor_version,
    )

    return True


class DaikinEKRHHModbusHub:
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self, hass, name, host, port, scan_interval, additional_zone, is_air2air
    ):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._client = ModbusTcpClient(
            host=host, port=port, timeout=max(3, (scan_interval - 1))
        )
        self._lock = threading.Lock()
        self._name = name
        self._scan_interval = timedelta(seconds=scan_interval)
        self._additional_zone = additional_zone
        self._is_air2air = is_air2air
        self._unsub_interval_method = None
        self._sensors = []
        self.data = {}

    @callback
    def async_add_daikin_ekrhh_sensor(self, update_callback):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        if not self._sensors:
            # self.connect()
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self.async_refresh_modbus_data, self._scan_interval
            )

        self._sensors.append(update_callback)

    @callback
    def async_remove_daikin_ekrhh_sensor(self, update_callback):
        """Remove data update."""
        self._sensors.remove(update_callback)

        if not self._sensors:
            """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None
            self.close()

    async def async_refresh_modbus_data(self, _now: Optional[int] = None) -> dict:
        """Time to update."""
        result: bool = await self._hass.async_add_executor_job(
            self._refresh_modbus_data
        )
        if result:
            for update_callback in self._sensors:
                update_callback()

    def _refresh_modbus_data(self, _now: Optional[int] = None) -> bool:
        """Time to update."""
        if not self._sensors:
            return False

        if not self._check_and_reconnect():
            # if not connected, skip
            return False

        try:
            update_result = self.read_modbus_data()
        except Exception as e:
            _LOGGER.exception("Error reading modbus data", exc_info=True)
            update_result = False
        return update_result

    @property
    def name(self):
        """Return the name of this hub."""
        return self._name

    def close(self):
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def _check_and_reconnect(self):
        if not self._client.connected:
            _LOGGER.info("modbus client is not connected, trying to reconnect")
            return self.connect()

        return self._client.connected

    def connect(self):
        """Connect client."""
        result = False
        with self._lock:
            result = self._client.connect()

        if result:
            _LOGGER.info(
                "successfully connected to %s:%s",
                self._client.comm_params.host,
                self._client.comm_params.port,
            )
        else:
            _LOGGER.warning(
                "not able to connect to %s:%s",
                self._client.comm_params.host,
                self._client.comm_params.port,
            )
        return result

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        with self._lock:
            return self._client.read_holding_registers(
                address=address, count=count, slave=unit
            )

    def read_input_registers(self, unit, address, count):
        """Read input registers."""
        with self._lock:
            return self._client.read_input_registers(
                address=address, count=count, slave=unit
            )

    def write_registers(self, unit, address, payload):
        """Write registers."""
        try:
            with self._lock:
                return self._client.write_register(
                    address=address, value=payload, slave=unit
                )
        except:
            with self._lock:
                return self._client.write_registers(
                    address=address, values=payload, slave=unit
                )

    def calculate_value(self, value, sf):
        return value * 10**sf

    def calculate_temp(self, value):
        # Scaling: /100, Range –327.68~327.67°C
        return value * 1.0 / 100.0

    def calculate_power(self, value):
        # Scaling: /100, Range –327.68~327.67 kW
        return value * 1.0 / 100.0

    def read_modbus_data(self):
        # Read only air2air data, which is limited right now
        if self._is_air2air:
            heatpump_data = self.read_holding_registers(address=1000, count=2, unit=1)
            if heatpump_data.isError():
                return False
            decoded_values = self._client.convert_from_registers(
                heatpump_data.registers, data_type=self._client.DATATYPE.INT16, word_order: 'big' 
            )
            self.data["A2A_Smart_Grid_operation_mode"] = decoded_values[0]
            self.data["Power_limit_for_Demand_Control"] = self.calculate_power(
                decoded_values[1]
            )

        heatpump_data = self.read_holding_registers(address=0, count=60, unit=1)
        if heatpump_data.isError():
            return False

        decoded_values = self._client.convert_from_registers(
            heatpump_data.registers, data_type=self._client.DATATYPE.INT16, word_order: 'big' 
        )

        self.data["leave_water_heating_setpoint"] = decoded_values[0]
        self.data["leave_water_cooling_setpoint"] = decoded_values[1]
        self.data["op_mode"] = decoded_values[2]
        self.data["space_heating_on_off"] = decoded_values[3]
        self.data["room_thermo_setpoint_heating"] = decoded_values[5]
        self.data["room_thermo_setpoint_cooling"] = decoded_values[6]
        self.data["quiet_mode_operation"] = decoded_values[8]
        self.data["DHW_reheat_setpoint"] = decoded_values[9]
        self.data["DHW_reheat_ON_OFF"] = decoded_values[11]
        self.data["DHW_booster_mode_ON_OFF"] = decoded_values[12]

        self.data["Weather_dependent_mode_Main"] = decoded_values[52]
        self.data["Weather_dependent_mode_main_setpoint_offset"] = decoded_values[53]
        self.data["Weather_dependent_mode_cooling_setpoint_offset"] = decoded_values[54]
        self.data["Smart_Grid_operation_mode"] = decoded_values[55]
        self.data["Power_limit_during_Recommended_on_buffering"] = self.calculate_power(
            decoded_values[56]
        )
        self.data["General_power_limit"] = self.calculate_power(decoded_values[57])
        self.data["Thermostat_Main_Input_A"] = decoded_values[58]

        heatpump_data = self.read_holding_registers(address=61, count=7, unit=1)
        if heatpump_data.isError():
            return False
        decoded_values = self._client.convert_from_registers(
            heatpump_data.registers, data_type=self._client.DATATYPE.INT16, word_order: 'big' 
        )

        self.data["Thermostat_Add_Input_A"] = decoded_values[0]
        self.data["Leaving_water_Add_Heating_setpoint"] = decoded_values[2]
        self.data["Leaving_water_Add_Cooling_setpoint"] = decoded_values[3]
        self.data["Weather_dependent_mode_Add"] = decoded_values[4]
        self.data["Weather_dependent_mode_Add_LWT_Heating_setpoint_offset"] = (
            decoded_values[5]
        )
        self.data["Weather_dependent_mode_Add_LWT_Cooling_setpoint_offset"] = (
            decoded_values[6]
        )

        heatpump_data = self.read_input_registers(address=20, count=41, unit=1)
        if heatpump_data.isError():
            return False

        decoded_values = self._client.convert_from_registers(
            heatpump_data.registers, data_type=self._client.DATATYPE.INT16
        )

        self.data["Unit error"] = decoded_values[0]
        decoded_values = self._client.convert_from_registers(
            heatpump_data.registers, data_type=self._client.DATATYPE.INT16, word_order: 'big' 
        )

        self.data["Unit error code"] = chr((decoded_values[1] >> 8) & 0xFF) + chr(
            decoded_values[1] & 0xFF
        )
        self.data["Unit error sub code"] = decoded_values[2]

        self.data["Circulation pump running"] = decoded_values[9]
        self.data["Compressor run"] = decoded_values[10]
        self.data["Booster heater run"] = decoded_values[11]
        self.data["Disinfection operation"] = decoded_values[12]
        self.data["Defrost/Startup"] = decoded_values[14]
        self.data["Hot Start"] = decoded_values[15]
        self.data["3-way valve"] = decoded_values[16]
        self.data["Operation mode"] = decoded_values[17]

        self.data["Leaving water temperature PHE"] = self.calculate_temp(
            decoded_values[19]
        )
        self.data["Leaving water temperature BUH"] = self.calculate_temp(
            decoded_values[20]
        )
        self.data["Return water temperature"] = self.calculate_temp(decoded_values[21])
        self.data["Domestic Hot Water temperature"] = self.calculate_temp(
            decoded_values[22]
        )
        self.data["Outside air temperature"] = self.calculate_temp(decoded_values[23])
        self.data["Liquid refrigerant temperature"] = self.calculate_temp(
            decoded_values[24]
        )

        self.data["Flow rate"] = decoded_values[28] / 100.0
        self.data["Remote controller room temperature"] = self.calculate_temp(
            decoded_values[29]
        )
        self.data["Heat pump power consumption"] = self.calculate_power(
            decoded_values[30]
        )
        self.data["DHW normal operation"] = decoded_values[31]
        self.data["Space heating/cooling normal operation"] = decoded_values[32]
        self.data["Leaving water Main Heating setpoint Lower limit"] = (
            self.calculate_temp(decoded_values[33])
        )
        self.data["Leaving water Main Heating setpoint Upper limit"] = (
            self.calculate_temp(decoded_values[34])
        )
        self.data["Leaving water Main Coolin setpoint Lower limit"] = (
            self.calculate_temp(decoded_values[35])
        )
        self.data["Leaving water Main Cooling setpoint Upper limit"] = (
            self.calculate_temp(decoded_values[36])
        )
        self.data["Leaving water Add Heating setpoint Lower limit"] = (
            self.calculate_temp(decoded_values[37])
        )
        self.data["Leaving water Add Heating setpoint Upper limit"] = (
            self.calculate_temp(decoded_values[38])
        )
        self.data["Leaving water Add Cooling setpoint Lower limit"] = (
            self.calculate_temp(decoded_values[39])
        )
        self.data["Leaving water Add Cooling setpoint Upper limit"] = (
            self.calculate_temp(decoded_values[40])
        )
        return True
