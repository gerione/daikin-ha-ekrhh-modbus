import asyncio
import logging
import threading
from datetime import timedelta
from typing import Optional

from pymodbus.client import ModbusTcpClient
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    ALTHERMA_3_INPUT,
    ALTHERMA_3_HOLDING,
    ALTHERMA_4_COILS,
    ALTHERMA_4_COILS_ADDITIONAL_ZONE,
    ALTHERMA_4_HOLDING,
    ALTHERMA_4_INPUT,
    ALTHERMA_4_DISCRETE_INPUTS,
    DOMAIN,
    CONF_MAX_POWER,
    CONF_MAX_WATER_TEMP,
    CONF_ADDITIONAL_ZONE,
    CONF_ISAIR2AIR,
    CONF_ALTHERMA_VERSION,
)

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["number", "sensor", "select", "binary_sensor"]
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
    altherma_version = entry.data[CONF_ALTHERMA_VERSION]

    hub = DaikinEKRHHModbusHub(
        hass,
        name,
        host,
        port,
        scan_interval,
        additional_zone,
        is_air2air,
        altherma_version,
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
            new_data[CONF_ISAIR2AIR] = False

        if config_entry.minor_version < 3:
            new_data[CONF_MAX_POWER] = 20
            new_data[CONF_MAX_WATER_TEMP] = 60

        if config_entry.minor_version < 4:
            new_data[CONF_ALTHERMA_VERSION] = 3

        hass.config_entries.async_update_entry(
            config_entry, data=new_data, minor_version=3, version=1
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
        self,
        hass,
        name,
        host,
        port,
        scan_interval,
        additional_zone,
        is_air2air,
        altherma_version,
    ) -> None:
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
        self.altherma_version = altherma_version

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
            _LOGGER.info("Modbus client is not connected, trying to reconnect")
            return self.connect()

        return self._client.connected

    def connect(self):
        """Connect client."""
        result = False
        with self._lock:
            result = self._client.connect()

        if result:
            _LOGGER.info(
                "Successfully connected to %s:%s",
                self._client.comm_params.host,
                self._client.comm_params.port,
            )
        else:
            _LOGGER.warning(
                "Not able to connect to %s:%s",
                self._client.comm_params.host,
                self._client.comm_params.port,
            )
        return result

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        with self._lock:
            return self._client.read_holding_registers(
                address=address, count=count, device_id=unit
            )

    def read_input_registers(self, unit, address, count):
        """Read input registers."""
        with self._lock:
            return self._client.read_input_registers(
                address=address, count=count, device_id=unit
            )

    def read_discrete_inputs(self, unit, address, count):
        """Read input registers."""
        with self._lock:
            return self._client.read_discrete_inputs(
                address=address, count=count, device_id=unit
            )

    def read_coils(self, unit, address, count):
        """Read input registers."""
        with self._lock:
            return self._client.read_coils(address=address, count=count, device_id=unit)

    def write_registers(self, unit, address, payload):
        """Write registers."""
        try:
            with self._lock:
                return self._client.write_register(
                    address=address, value=payload, device_id=unit
                )
        except:
            with self._lock:
                return self._client.write_registers(
                    address=address, values=payload, device_id=unit
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
                heatpump_data.registers,
                data_type=self._client.DATATYPE.INT16,
                word_order="big",
            )
            self.data["A2A_Smart_Grid_operation_mode"] = decoded_values[0]
            self.data["Power_limit_for_Demand_Control"] = self.calculate_power(
                decoded_values[1]
            )
            return True

        if self.altherma_version != 3:
            sorted_list = sorted(ALTHERMA_4_HOLDING, key=lambda x: x[0])
        else:
            sorted_list = sorted(ALTHERMA_3_HOLDING, key=lambda x: x[0])

        # Iterate over the sorted list
        adress = 0
        count = 0
        MAX_COUNT = 60
        for item in sorted_list:
            if adress + count < item[0]:
                adress = item[0] - 1
                count = MAX_COUNT
                heatpump_data = self.read_holding_registers(
                    address=adress, count=MAX_COUNT, unit=1
                )
                if heatpump_data.isError():
                    return False

                decoded_values = self._client.convert_from_registers(
                    heatpump_data.registers,
                    data_type=self._client.DATATYPE.INT16,
                    word_order="big",
                )
            offset = item[0] - adress - 1
            if item[3] == "INT16":
                self.data[item[2]] = decoded_values[offset]
            elif item[3] == "TEMP16":
                self.data[item[2]] = self.calculate_temp(decoded_values[offset])
            elif item[3] == "POW16":
                self.data[item[2]] = self.calculate_power(decoded_values[offset])
            elif item[3] == "FLOW16":
                self.data[item[2]] = decoded_values[offset] / 100.0
            elif item[3] == "TEXT16":
                self.data[item[2]] = chr((decoded_values[offset] >> 8) & 0xFF) + chr(
                    decoded_values[offset] & 0xFF
                )

        if self.altherma_version != 3:
            sorted_list = sorted(ALTHERMA_4_INPUT, key=lambda x: x[0])
        else:
            sorted_list = sorted(ALTHERMA_3_INPUT, key=lambda x: x[0])
        # Iterate over the sorted list
        adress = 0
        count = 0
        MAX_COUNT = 41
        for item in sorted_list:
            if adress + count < item[0]:
                adress = item[0] - 1
                count = MAX_COUNT
                heatpump_data = self.read_input_registers(
                    address=adress, count=MAX_COUNT, unit=1
                )
                if heatpump_data.isError():
                    return False

                decoded_values = self._client.convert_from_registers(
                    heatpump_data.registers,
                    data_type=self._client.DATATYPE.INT16,
                    word_order="big",
                )
            offset = item[0] - adress - 1
            if item[3] == "INT16":
                self.data[item[2]] = decoded_values[offset]
            elif item[3] == "TEMP16":
                self.data[item[2]] = self.calculate_temp(decoded_values[offset])
            elif item[3] == "POW16":
                self.data[item[2]] = self.calculate_power(decoded_values[offset])
            elif item[3] == "FLOW16":
                self.data[item[2]] = decoded_values[offset] / 100.0
            elif item[3] == "TEXT16":
                self.data[item[2]] = chr((decoded_values[offset] >> 8) & 0xFF) + chr(
                    decoded_values[offset] & 0xFF
                )
        if self.altherma_version == 3:
            return True

        sorted_list = sorted(ALTHERMA_4_COILS, key=lambda x: x[0])

        # Iterate over the sorted list
        adress = 0
        count = 0
        MAX_COUNT = 41
        for item in sorted_list:
            if adress + count < item[0]:
                adress = item[0] - 1
                count = MAX_COUNT
                heatpump_data = self.read_coils(address=adress, count=MAX_COUNT, unit=1)
                if heatpump_data.isError():
                    return False

                decoded_values = heatpump_data.bits
            offset = item[0] - adress - 1
            self.data[item[2]] = decoded_values[offset]

        if self._additional_zone:
            sorted_list = sorted(ALTHERMA_4_COILS_ADDITIONAL_ZONE, key=lambda x: x[0])

            # Iterate over the sorted list
            adress = 0
            count = 0
            MAX_COUNT = 41
            for item in sorted_list:
                if adress + count < item[0]:
                    adress = item[0] - 1
                    count = MAX_COUNT
                    heatpump_data = self.read_coils(
                        address=adress, count=MAX_COUNT, unit=1
                    )
                    if heatpump_data.isError():
                        return False

                    decoded_values = heatpump_data.bits
                offset = item[0] - adress - 1
                self.data[item[2]] = decoded_values[offset]

        sorted_list = sorted(ALTHERMA_4_DISCRETE_INPUTS, key=lambda x: x[0])

        # Iterate over the sorted list
        adress = 0
        count = 0
        MAX_COUNT = 41
        for item in sorted_list:
            if adress + count < item[0]:
                adress = item[0] - 1
                count = MAX_COUNT
                heatpump_data = self.read_discrete_inputs(
                    address=adress, count=MAX_COUNT, unit=1
                )
                if heatpump_data.isError():
                    return False

                decoded_values = heatpump_data.bits
            offset = item[0] - adress - 1
            self.data[item[2]] = decoded_values[offset]
        return True
