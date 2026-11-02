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
)

_LOGGER = logging.getLogger(__name__)


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
        self.altherma_version = altherma_version

    def checkAvailability(self, key):
        if self._is_air2air:
            return True
        if key in (
            f"{DOMAIN}_altherma3_input_21",
            f"{DOMAIN}_altherma3_input_22",
            f"{DOMAIN}_altherma3_input_23",
            f"{DOMAIN}_altherma4_input_21",
            f"{DOMAIN}_altherma4_input_22",
            f"{DOMAIN}_altherma4_input_23",
        ):
            return True
        if self.altherma_version == "Altherma 3 (EKRHH)":
            if f"{DOMAIN}_altherma3_input_21" not in self.data or (
                self.data[f"{DOMAIN}_altherma3_input_21"] != 0
                and self.data[f"{DOMAIN}_altherma3_input_21"] != 2
            ):
                return False
            if (
                f"{DOMAIN}_altherma3_input_23" not in self.data
                or self.data[f"{DOMAIN}_altherma3_input_23"] != 32766
            ):
                return False
        else:
            if f"{DOMAIN}_altherma4_input_21" not in self.data or (
                self.data[f"{DOMAIN}_altherma4_input_21"] != 0
                and self.data[f"{DOMAIN}_altherma4_input_21"] != 2
            ):
                return False
            if (
                f"{DOMAIN}_altherma4_input_23" not in self.data
                or self.data[f"{DOMAIN}_altherma4_input_23"] != 32766
            ):
                return False
        return True

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
            if self.altherma_version != "Altherma 3 (EKRHH)":
                _LOGGER.warning(f"Holding registers: {item[0]} - {item[1]}")
            offset = item[0] - 1
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
            offset = item[0] - 20 - 1
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
        if self.altherma_version == "Altherma 3 (EKRHH)":
            return self.data

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

        sorted_list = sorted(ALTHERMA_4_DISCRETE_INPUTS, key=lambda x: x[0])

        # Iterate over the sorted list
        decoded_values = await self._unit.read_discrete_inputs(address=0, count=26)
        for item in sorted_list:
            offset = item[0] - 1
            self.data[item[2]] = decoded_values[offset]
        return self.data
