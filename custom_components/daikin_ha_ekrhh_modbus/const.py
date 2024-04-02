DOMAIN = "daikin_ha_ekrhh_modbus"

DEFAULT_NAME = "daikin_ekrhh"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 802
DEFAULT_MODBUS_ADDRESS = 1

CONF_MODBUS_ADDRESS = "modbus_address"

ATTR_STATUS_DESCRIPTION = "status_description"
ATTR_MANUFACTURER = "Daikin"

SENSOR_TYPES = {
    "AC_Current": [
        "Leaving water Main Heating setpoint",
        "leave_water_heating_setpoint",
        "A",
        "mdi:temperature-celsius",
    ],
    "AC_CurrentA": [
        "Leaving water Main Cooling setpoint",
        "leave_water_cooling_setpoint",
        "A",
        "mdi:temperature-celsius",
    ],
    "AC_CurrentB": ["Operation mode", "op_mode", "A", None],
    "AC_CurrentC": [
        "Space heating/cooling ON/OFF",
        "space_heating_on_off",
        "A",
        None,
    ],
    "AC_VoltageAB": [
        "Room thermostat control Heating setpoint",
        "room_thermo_setpoint",
        "V",
        "mdi:temperature-celsius",
    ],
}


DEVICE_STATUSSES = {
    1: "Off",
    2: "Sleeping (auto-shutdown) – Night mode",
    3: "Grid Monitoring/wake-up",
    4: "Inverter is ON and producing power",
    5: "Production (curtailed)",
    6: "Shutting down",
    7: "Fault",
    8: "Maintenance/setup",
}
