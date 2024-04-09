import asyncio
import logging
import operator
import threading
from datetime import timedelta
from typing import Optional

import voluptuous as vol
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

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
)

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["sensor"]
# PLATFORMS = ["number", "select", "sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Daikin EKRHH Modbus component."""
    # @TODO: Add setup code.
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a solaredge mobus."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    port = entry.data[CONF_PORT]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    hub = SolaredgeModbusHub(
        hass,
        name,
        host,
        port,
        scan_interval,
    )

    hass.data[DOMAIN][name] = {"hub": hub}

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
    return True


async def async_unload_entry(hass, entry):
    """Unload Solaredge mobus entry."""
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


class SolaredgeModbusHub:
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self,
        hass,
        name,
        host,
        port,
        scan_interval,
    ):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._client = ModbusTcpClient(
            host=host, port=port, timeout=max(3, (scan_interval - 1))
        )
        self._lock = threading.Lock()
        self._name = name
        self._scan_interval = timedelta(seconds=scan_interval)
        self._unsub_interval_method = None
        self._sensors = []
        self.data = {}

    @callback
    def async_add_solaredge_sensor(self, update_callback):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        if not self._sensors:
            # self.connect()
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self.async_refresh_modbus_data, self._scan_interval
            )

        self._sensors.append(update_callback)

    @callback
    def async_remove_solaredge_sensor(self, update_callback):
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
        with self._lock:
            return self._client.write_registers(
                address=address, values=payload, slave=unit
            )

    def calculate_value(self, value, sf):
        return value * 10**sf

    def calculate_temp (self, value):
        # Scaling: /100, Range –327.68~327.67°C
        return value*1.0/100.0

    def calculate_power (self, value):
        # Scaling: /100, Range –327.68~327.67 kW
        return value*1.0/100.0

    def read_modbus_data(self):
        inverter_data = self.read_holding_registers(address=0, count=60, unit=1)
        if inverter_data.isError():
            return False

        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, byteorder=Endian.BIG
        )
        leave_water_heating_setpoint = decoder.decode_16bit_int()
        leave_water_cooling_setpoint = decoder.decode_16bit_int()
        op_mode = decoder.decode_16bit_int()
        space_heating_on_off = decoder.decode_16bit_int()
        decoder.skip_bytes(2)
        room_thermo_setpoint_heating = decoder.decode_16bit_int()
        room_thermo_setpoint_cooling = decoder.decode_16bit_int()

        self.data["leave_water_heating_setpoint"] = leave_water_heating_setpoint
        self.data["leave_water_cooling_setpoint"] = leave_water_cooling_setpoint
        self.data["op_mode"] = op_mode
        self.data["space_heating_on_off"] = space_heating_on_off
        self.data["room_thermo_setpoint_heating"] = room_thermo_setpoint_heating
        self.data["room_thermo_setpoint_cooling"] = room_thermo_setpoint_cooling

        decoder.skip_bytes(2)
        self.data["quiet_mode_operation"] = decoder.decode_16bit_int()
        self.data["DHW_reheat_setpoint"] = decoder.decode_16bit_int()
        decoder.skip_bytes(2)
        self.data["DHW_reheat_ON_OFF"] = decoder.decode_16bit_int()
        self.data["DHW_booster_mode_ON_OFF"] = decoder.decode_16bit_int()
        decoder.skip_bytes(10 * 2)
        self.data["Weather_dependent_mode_Main"] = decoder.decode_16bit_int()
        self.data["Weather_dependent_mode_main_setpoint_offset"] = (
            decoder.decode_16bit_int()
        )
        self.data["Weather_dependent_mode_cooling_setpoint_offset"] = (
            decoder.decode_16bit_int()
        )
        self.data["Smart_Grid_operation_mode"] = decoder.decode_16bit_int()
        self.data["Power_limit_during_Recommended_on_buffering"] = self.calculate_power(
            decoder.decode_16bit_int())
        self.data["General_power_limit"] = self.calculate_power(decoder.decode_16bit_int())
        self.data["Thermostat_Main_Input_A"] = decoder.decode_16bit_int()
        decoder.skip_bytes(2)

        inverter_data = self.read_holding_registers(address=61, count=7, unit=1)
        if inverter_data.isError():
            return False

        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, byteorder=Endian.BIG
        )
        self.data["Thermostat_Add_Input_A"] = decoder.decode_16bit_int()
        decoder.skip_bytes(2)
        self.data["Leaving_water_Add_Heating_setpoint"] = decoder.decode_16bit_int()
        self.data["Leaving_water_Add_Cooling_setpoint"] = decoder.decode_16bit_int()
        self.data["Weather_dependent_mode_Add"] = decoder.decode_16bit_int()
        self.data["Weather_dependent_mode_Add_LWT_Heating_setpoint_offset"] = (
            decoder.decode_16bit_int()
        )
        self.data["Weather_dependent_mode_Add_LWT_Cooling_setpoint_offset"] = (
            decoder.decode_16bit_int()
        )

        inverter_data = self.read_input_registers(address=20, count=41, unit=1)
        if inverter_data.isError():
            return False

        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, byteorder=Endian.BIG
        )

        self.data["Unit error"] = decoder.decode_16bit_int()
        self.data["Unit error code"] = decoder.decode_string(2)
        self.data["Unit error sub code"] = decoder.decode_16bit_int()
        decoder.skip_bytes(2*6)
        self.data["Circulation pump running"] = decoder.decode_16bit_int()
        self.data["Compressor run"] = decoder.decode_16bit_int()
        self.data["Booster heater run"] = decoder.decode_16bit_int()
        self.data["Disinfection operation"] = decoder.decode_16bit_int()
        decoder.skip_bytes(2)
        self.data["Defrost/Startup"] = decoder.decode_16bit_int()
        self.data["Hot Start"] = decoder.decode_16bit_int()
        self.data["3-way valve"] = decoder.decode_16bit_int()
        self.data["Operation mode"] = decoder.decode_16bit_int()
        decoder.skip_bytes(2)
        self.data["Leaving water temperature PHE"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Leaving water temperature BUH"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Return water temperature"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Domestic Hot Water temperature"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Outside air temperature"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Liquid refrigerant temperature"] = self.calculate_temp(decoder.decode_16bit_int())
        decoder.skip_bytes(2*3)
        self.data["Flow rate"] = decoder.decode_16bit_int()/100.0
        self.data["Remote controller room temperature"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Heat pump power consumption"] = self.calculate_power(decoder.decode_16bit_int())
        self.data["DHW normal operation"] = decoder.decode_16bit_int()
        self.data["Space heating/cooling normal operation"] = decoder.decode_16bit_int()
        self.data["Leaving water Main Heating setpoint Lower limit"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Leaving water Main Heating setpoint Upper limit"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Leaving water Main Coolin setpoint Lower limit"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Leaving water Main Cooling setpoint Upper limit"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Leaving water Add Heating setpoint Lower limit"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Leaving water Add Heating setpoint Upper limit"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Leaving water Add Cooling setpoint Lower limit"] = self.calculate_temp(decoder.decode_16bit_int())
        self.data["Leaving water Add Cooling setpoint Upper limit"] = self.calculate_temp(decoder.decode_16bit_int())
        return True
