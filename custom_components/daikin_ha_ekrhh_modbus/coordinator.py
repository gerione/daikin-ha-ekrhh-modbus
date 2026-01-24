"""Coordinator for Modbus HA EKRHH integration."""

from __future__ import annotations

import logging
from datetime import timedelta
import asyncio

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pymodbus.client import AsyncModbusTcpClient

from .const import (
    DOMAIN,
    ALTHERMA_3_INPUT,
    ALTHERMA_3_HOLDING,
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
        # Read only air2air data, which is limited right now
        if self._is_air2air:
            heatpump_data = await self._client.read_holding_registers(
                address=1000, count=2
            )
            if heatpump_data.isError():
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
                heatpump_data = await self._client.read_holding_registers(
                    address=adress, count=MAX_COUNT
                )
                if heatpump_data.isError():
                    return self.data

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
                heatpump_data = await self._client.read_input_registers(
                    address=adress, count=MAX_COUNT
                )
                if heatpump_data.isError():
                    return self.data

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
            return self.data

        sorted_list = sorted(ALTHERMA_4_COILS, key=lambda x: x[0])

        # Iterate over the sorted list
        adress = 0
        count = 0
        MAX_COUNT = 41
        for item in sorted_list:
            if adress + count < item[0]:
                adress = item[0] - 1
                count = MAX_COUNT
                heatpump_data = await self._client.read_coils(
                    address=adress, count=MAX_COUNT
                )
                if heatpump_data.isError():
                    return self.data

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
                    heatpump_data = await self._client.read_coils(
                        address=adress, count=MAX_COUNT
                    )
                    if heatpump_data.isError():
                        return self.data

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
                heatpump_data = self._client.read_discrete_inputs(
                    address=adress, count=MAX_COUNT
                )
                if heatpump_data.isError():
                    return self.data

                decoded_values = heatpump_data.bits
            offset = item[0] - adress - 1
            self.data[item[2]] = decoded_values[offset]
        return self.data
