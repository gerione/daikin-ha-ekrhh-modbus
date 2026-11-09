"""Coordinator for Modbus HA EKRHH integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from modbus_connection import ModbusError, ModbusExceptionError, ModbusUnit
from modbus_connection.decode import decode_int16

from .const import (
    ALTHERMA_4_HOLDING_ADDITIONAL_ZONE,
    ALTHERMA_4_HOLDING_SELECT,
    ALTHERMA_4_HOLDING_SELECT_ADDITIONAL_ZONE,
    DOMAIN,
    ALTHERMA_3_HOLDING,
    ALTHERMA_3_HOLDING_ADDITIONAL_ZONE,
    ALTHERMA_3_HOLDING_SELECT,
    ALTHERMA_3_HOLDING_SELECT_ADDITIONAL_ZONE,
    ALTHERMA_3_INPUT,
    ALTHERMA_3_INPUT_ADDITIONAL_ZONE,
    ALTHERMA_3_INPUT_BINARY,
    ALTHERMA_4_COILS,
    ALTHERMA_4_COILS_ADDITIONAL_ZONE,
    ALTHERMA_4_HOLDING,
    ALTHERMA_4_INPUT,
    ALTHERMA_4_INPUT_BINARY,
    ALTHERMA_4_INPUT_ADDITIONAL_ZONE,
    ALTHERMA_4_DISCRETE_INPUTS,
    ALTHERMA_4_DISCRETE_INPUTS_ADDITIONAL_ZONE,
    FAULT_CODE_SENSOR,
    NO_SUB_CODE,
    UNAVAILABLE_RAW_VALUES,
)

_LOGGER = logging.getLogger(__name__)

ERROR_KEYS = {
    f"{DOMAIN}_{model}_input_{address}"
    for model in ("altherma3", "altherma4")
    for address in (21, 22, 23)
}


class DaikinEKRHHModbusHub(DataUpdateCoordinator):
    """Poll the heat pump over a Modbus unit shared through the modbus integration."""

    def __init__(
        self,
        hass,
        entry,
        name,
        unit: ModbusUnit,
        scan_interval,
        additional_zone,
        is_air2air,
        altherma_version,
    ) -> None:
        """Initialize the Modbus hub."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self._hass = hass
        self._unit = unit
        self._name = name
        self._scan_interval = timedelta(seconds=scan_interval)
        self._additional_zone = additional_zone
        self._is_air2air = is_air2air
        self._unsub_interval_method = None
        self._sensors = []
        self.data = {}
        self._unavailable_keys = set()
        self.altherma_version = altherma_version

    def checkAvailability(self, key):
        """Return False for values the unit reported as not available."""
        return key not in self._unavailable_keys

    def _store(self, item, raw):
        """Decode one register of a register table and store its value."""
        key = item[2]
        # The error registers carry their own meaning in every value.
        if raw in UNAVAILABLE_RAW_VALUES and key not in ERROR_KEYS:
            self._unavailable_keys.add(key)
            return
        self._unavailable_keys.discard(key)
        if item[3] == "INT16":
            self.data[key] = raw
        elif item[3] == "TEMP16":
            self.data[key] = self.calculate_temp(raw)
        elif item[3] == "POW16":
            self.data[key] = self.calculate_power(raw)
        elif item[3] == "FLOW16":
            self.data[key] = raw / 100.0
        elif item[3] == "TEXT16":
            self.data[key] = chr((raw >> 8) & 0xFF) + chr(raw & 0xFF)

    def _fault_code(self, model):
        """Combine error code and sub code the way the unit displays them."""
        if self.data.get(f"{DOMAIN}_{model}_input_21") == 0:
            return "No error"
        code = self.data.get(f"{DOMAIN}_{model}_input_22", "").strip("\x00 ")
        if not code:
            return None
        sub_code = self.data.get(f"{DOMAIN}_{model}_input_23")
        if sub_code is None or sub_code == NO_SUB_CODE:
            return code
        return f"{code}-{sub_code:02d}"

    def calculate_value(self, value, sf):
        return value * 10**sf

    def calculate_temp(self, value):
        # Scaling: /100, Range –327.68~327.67°C
        return value * 1.0 / 100.0

    def calculate_power(self, value):
        # Scaling: /100, Range –327.68~327.67 kW
        return value * 1.0 / 100.0

    async def _read_int16(self, read, address, count):
        """Read a block of registers and decode each one as a signed 16-bit value."""
        registers = await read(address=address, count=count)
        return [decode_int16([register]) for register in registers]

    async def async_write_register(self, address, value) -> bool:
        """Write one holding register, returning whether the device accepted it."""
        try:
            await self._unit.write_register(address, value)
        except ModbusError as err:
            _LOGGER.error("Could not write register %s: %s", address, err)
            return False
        return True

    async def async_write_value(self, address, fmt, value) -> bool:
        """Encode a value in a register table format and write it."""
        if fmt in ("POW16", "TEMP16"):
            payload = round(value * 100)
        elif fmt == "INT16":
            payload = int(value)
        else:
            _LOGGER.error("Invalid encoding format %s for register %s", fmt, address)
            return False
        # Two's complement for negative numbers.
        return await self.async_write_register(address, payload & 0xFFFF)

    async def async_write_coil(self, address, value) -> bool:
        """Write one coil, returning whether the device accepted it."""
        try:
            await self._unit.write_coil(address, value)
        except ModbusError as err:
            _LOGGER.error("Could not write coil %s: %s", address, err)
            return False
        return True

    async def _async_update_data(self):
        """Read all registers block by block."""
        try:
            return await self._async_read_all()
        except ModbusExceptionError as err:
            # The device answered but refused a block; keep the last known values.
            _LOGGER.warning("Registers not readable: %s", err)
            return self.data
        except ModbusError as err:
            raise UpdateFailed(f"Error communicating with the Daikin unit: {err}") from err

    async def _async_read_all(self):
        # Read only air2air data, which is limited right now
        if self._is_air2air:
            decoded_values = await self._read_int16(
                self._unit.read_holding_registers, 1000, 2
            )
            self.data["A2A_Smart_Grid_operation_mode"] = decoded_values[0]
            self.data["Power_limit_for_Demand_Control"] = self.calculate_power(
                decoded_values[1]
            )
            return self.data

        if self.altherma_version != "Altherma 3 (EKRHH)":
            ALL_HOLDING = []
            ALL_HOLDING.extend(ALTHERMA_4_HOLDING)
            ALL_HOLDING.extend(ALTHERMA_4_HOLDING_SELECT)
            if self._additional_zone:
                ALL_HOLDING.extend(ALTHERMA_4_HOLDING_ADDITIONAL_ZONE)
                ALL_HOLDING.extend(ALTHERMA_4_HOLDING_SELECT_ADDITIONAL_ZONE)

            sorted_list = sorted(ALL_HOLDING, key=lambda x: x[0])
            MAX_COUNT = 80
            decoded_values = await self._read_int16(
                self._unit.read_holding_registers, 0, MAX_COUNT
            )
        else:
            ALL_HOLDING = []
            ALL_HOLDING.extend(ALTHERMA_3_HOLDING)
            ALL_HOLDING.extend(ALTHERMA_3_HOLDING_SELECT)

            if self._additional_zone:
                ALL_HOLDING.extend(ALTHERMA_3_HOLDING_ADDITIONAL_ZONE)
                ALL_HOLDING.extend(ALTHERMA_3_HOLDING_SELECT_ADDITIONAL_ZONE)
            sorted_list = sorted(ALL_HOLDING, key=lambda x: x[0])

            decoded_values = await self._read_int16(
                self._unit.read_holding_registers, 0, 60
            )
            decoded_values.extend(
                await self._read_int16(self._unit.read_holding_registers, 60, 7)
            )

        # Iterate over the sorted list
        for item in sorted_list:
            self._store(item, decoded_values[item[0] - 1])

        if self.altherma_version != "Altherma 3 (EKRHH)":
            ALL_INPUT = []
            ALL_INPUT.extend(ALTHERMA_4_INPUT)
            ALL_INPUT.extend(ALTHERMA_4_INPUT_BINARY)
            if self._additional_zone:
                ALL_INPUT.extend(ALTHERMA_4_INPUT_ADDITIONAL_ZONE)
            sorted_list = sorted(ALL_INPUT, key=lambda x: x[0])
            decoded_values = await self._read_int16(
                self._unit.read_input_registers, 20, 67
            )
        else:
            ALL_INPUT = []
            ALL_INPUT.extend(ALTHERMA_3_INPUT)
            ALL_INPUT.extend(ALTHERMA_3_INPUT_BINARY)
            if self._additional_zone:
                ALL_INPUT.extend(ALTHERMA_3_INPUT_ADDITIONAL_ZONE)

            sorted_list = sorted(ALL_INPUT, key=lambda x: x[0])
            decoded_values = await self._read_int16(
                self._unit.read_input_registers, 20, 41
            )

        # Iterate over the sorted list
        for item in sorted_list:
            self._store(item, decoded_values[item[0] - 20 - 1])
        if self.altherma_version == "Altherma 3 (EKRHH)":
            self.data[FAULT_CODE_SENSOR[1]] = self._fault_code("altherma3")
            return self.data
        self.data[FAULT_CODE_SENSOR[1]] = self._fault_code("altherma4")

        ALL_COILS = []
        ALL_COILS.extend(ALTHERMA_4_COILS)
        if self._additional_zone:
            ALL_COILS.extend(ALTHERMA_4_COILS_ADDITIONAL_ZONE)

        sorted_list = sorted(ALL_COILS, key=lambda x: x[0])
        # Iterate over the sorted list
        decoded_values = await self._unit.read_coils(address=0, count=7)
        for item in sorted_list:
            offset = item[0] - 1
            self.data[item[2]] = decoded_values[offset]

        ALL_D_INPUTS = []
        ALL_D_INPUTS.extend(ALTHERMA_4_DISCRETE_INPUTS)
        
        if self._additional_zone:
            ALL_D_INPUTS.extend(ALTHERMA_4_DISCRETE_INPUTS_ADDITIONAL_ZONE )
        sorted_list = sorted(ALL_D_INPUTS, key=lambda x: x[0])    
        # Iterate over the sorted list
        decoded_values = await self._unit.read_discrete_inputs(address=0, count=26)
        for item in sorted_list:
            offset = item[0] - 1
            self.data[item[2]] = decoded_values[offset]
        return self.data
