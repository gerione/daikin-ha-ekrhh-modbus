"""Coordinator for Modbus HA EKRHH integration."""

from __future__ import annotations

import logging
from datetime import timedelta
import asyncio

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pymodbus.client import AsyncModbusTcpClient

from .const import (
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
    ALTHERMA_4_DISCRETE_INPUTS,
)

_LOGGER = logging.getLogger(__name__)


class DaikinEKRHHModbusHub(DataUpdateCoordinator):
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
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self._hass = hass
        self._client: AsyncModbusTcpClient | None = None
        self._host = host
        self._port = port
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

    async def _async_update_data(self):
        """Lese alle Input-Register blockweise."""
        if self._client is None:
            self._client = AsyncModbusTcpClient(self._host, port=self._port)
            await self._client.connect()
            await asyncio.sleep(0.1)
            if not self._client.connected:
                raise UpdateFailed(
                    f"Modbus Verbindung zu {self._host}:{self._port} fehlgeschlagen"
                )
        if not self._client.connected:
            await self._client.connect()
            await asyncio.sleep(0.1)
            if not self._client.connected:
                raise UpdateFailed(
                    f"Modbus Verbindung zu {self._host}:{self._port} fehlgeschlagen"
                )
        # Read only air2air data, which is limited right now
        if self._is_air2air:
            heatpump_data = await self._client.read_holding_registers(
                address=1000, count=2
            )
            if heatpump_data.isError():
                _LOGGER.warning(f"Input registers not readable: {heatpump_data}")
                return self.data
            decoded_values = self._client.convert_from_registers(
                heatpump_data.registers,
                data_type=self._client.DATATYPE.INT16,
                word_order="big",
            )
            self.data["A2A_Smart_Grid_operation_mode"] = decoded_values[0]
            self.data["Power_limit_for_Demand_Control"] = self.calculate_power(
                decoded_values[1]
            )
            return self.data

        if self.altherma_version != "Altherma 3 (EKRHH)":
            sorted_list = sorted(ALTHERMA_4_HOLDING, key=lambda x: x[0])
            MAX_COUNT = 79
            heatpump_data = await self._client.read_holding_registers(
                address=0, count=MAX_COUNT
            )
            if heatpump_data.isError():
                _LOGGER.warning(f"Holding registers not readable: {heatpump_data}")
                return self.data

            decoded_values = self._client.convert_from_registers(
                heatpump_data.registers,
                data_type=self._client.DATATYPE.INT16,
                word_order="big",
            )
        else:
            ALL_HOLDING = []
            ALL_HOLDING.extend(ALTHERMA_3_HOLDING)
            ALL_HOLDING.extend(ALTHERMA_3_HOLDING_SELECT)

            if self._additional_zone:
                ALL_HOLDING.extend(ALTHERMA_3_HOLDING_ADDITIONAL_ZONE)
                ALL_HOLDING.extend(ALTHERMA_3_HOLDING_SELECT_ADDITIONAL_ZONE)
            sorted_list = sorted(ALL_HOLDING, key=lambda x: x[0])

            heatpump_data = await self._client.read_holding_registers(
                address=0, count=60
            )
            if heatpump_data.isError():
                _LOGGER.warning(f"Holding registers not readable: {heatpump_data}")
                return self.data

            decoded_values = self._client.convert_from_registers(
                heatpump_data.registers,
                data_type=self._client.DATATYPE.INT16,
                word_order="big",
            )
            heatpump_data = await self._client.read_holding_registers(
                address=60, count=7
            )
            if heatpump_data.isError():
                _LOGGER.warning(f"Holding registers not readable: {heatpump_data}")
                return self.data

            decoded_values.extend(
                self._client.convert_from_registers(
                    heatpump_data.registers,
                    data_type=self._client.DATATYPE.INT16,
                    word_order="big",
                )
            )

        # Iterate over the sorted list
        for item in sorted_list:
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
            sorted_list = sorted(ALTHERMA_4_INPUT, key=lambda x: x[0])
            heatpump_data = await self._client.read_input_registers(
                address=20, count=67
            )
            if heatpump_data.isError():
                _LOGGER.warning(f"Input registers not readable: {heatpump_data}")
                return self.data

            decoded_values = self._client.convert_from_registers(
                heatpump_data.registers,
                data_type=self._client.DATATYPE.INT16,
                word_order="big",
            )
        else:
            ALL_INPUT = []
            ALL_INPUT.extend(ALTHERMA_3_INPUT)
            ALL_INPUT.extend(ALTHERMA_3_INPUT_BINARY)

            sorted_list = sorted(ALL_INPUT, key=lambda x: x[0])
            heatpump_data = await self._client.read_input_registers(
                address=20, count=41
            )
            if heatpump_data.isError():
                _LOGGER.warning(f"Input registers not readable: {heatpump_data}")
                return self.data

            decoded_values = self._client.convert_from_registers(
                heatpump_data.registers,
                data_type=self._client.DATATYPE.INT16,
                word_order="big",
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
        heatpump_data = await self._client.read_coils(address=0, count=7)
        if heatpump_data.isError():
            return self.data

        decoded_values = heatpump_data.bits
        for item in sorted_list:
            offset = item[0] - 1
            self.data[item[2]] = decoded_values[offset]

        sorted_list = sorted(ALTHERMA_4_DISCRETE_INPUTS, key=lambda x: x[0])

        # Iterate over the sorted list
        heatpump_data = self._client.read_discrete_inputs(address=0, count=MAX_COUNT)
        if heatpump_data.isError():
            return self.data

        decoded_values = heatpump_data.bits
        for item in sorted_list:
            offset = item[0] - 1
            self.data[item[2]] = decoded_values[offset]
        return self.data
