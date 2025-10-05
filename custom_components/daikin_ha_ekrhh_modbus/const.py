DOMAIN = "daikin_ha_ekrhh_modbus"

DEFAULT_NAME = "daikin_ekrhh"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 502
DEFAULT_MODBUS_ADDRESS = 1
DEFAULT_ADDITIONAL_ZONE=False
CONF_MODBUS_ADDRESS = "modbus_address"
CONF_ADDITIONAL_ZONE = "additional_zone"
CONF_MAX_POWER="max_power"
CONF_MAX_WATER_TEMP="max_water_temp"

ATTR_STATUS_DESCRIPTION = "status_description"
ATTR_MANUFACTURER = "Daikin"

CONF_ISAIR2AIR="is_air_to_air_heatpump"
DEFAULT_AIR2AIR=False

SENSOR_TYPES = {
    "H1": ["Leaving water Main Heating setpoint","leave_water_heating_setpoint","°C","mdi:temperature-celsius",],
    "H2": ["Leaving water Main Cooling setpoint","leave_water_cooling_setpoint","°C","mdi:temperature-celsius",],
    "H3": ["Operation mode", "op_mode", None, None],
    "H4": ["Space heating/cooling ON/OFF","space_heating_on_off",None,None,],
    "H6": ["Room thermostat control Heating setpoint","room_thermo_setpoint_heating","°C","mdi:temperature-celsius",],
    "H7": ["Room thermostat control Cooling setpoint","room_thermo_setpoint_cooling","°C","mdi:temperature-celsius",],
    "H9": ["Quiet mode operation","quiet_mode_operation","","mdi:volume-quiet",],
    "H10": ["DHW reheat setpoint","DHW_reheat_setpoint","°C","mdi:temperature-celsius",],
    "H12": ["DHW reheat ON/OF","DHW_reheat_ON_OFF",None,None,],
    "H13": ["DHW booster mode ON/OFF","DHW_booster_mode_ON_OFF",None,None,],
    "H53": ["Weather dependent mode Main","Weather_dependent_mode_Main",None,None,],
    "H54": ["Weather dependent mode Main LWT Heating setpoint offset","Weather_dependent_mode_main_setpoint_offset","°C","mdi:temperature-celsius",],
    "H55": ["Weather dependent mode Main LWT Cooling setpoint offset","Weather_dependent_mode_cooling_setpoint_offset","°C","mdi:temperature-celsius",],
    "H56": ["Smart Grid operation mode","Smart_Grid_operation_mode",None,None,],
    "H57": ["Power limit during Recommended on / buffering","Power_limit_during_Recommended_on_buffering","kW","mdi:lightning-bolt",],
    "H58": ["General power limit","General_power_limit","kW","mdi:lightning-bolt",],
    "H59": ["Thermostat Main Input A","Thermostat_Main_Input_A",None,None,],


    "I21": ["Unit error","Unit error",None,"mdi:alert-circle",],
    "I22": ["Unit error code","Unit error code",None,"mdi:alert-circle",],
    "I23": ["Unit error sub code","Unit error sub code",None,"mdi:alert-circle",],
    "I30": ["Circulation pump running","Circulation pump running",None,"mdi:pump",],
    "I31": ["Compressor run","Compressor run",None,"mdi:heat-pump-outline",],

    "I32": ["Booster heater run","Booster heater run",None,"mdi:water-boiler",],
    "I33": ["Disinfection operation","Disinfection operation",None,"mdi:spray",],
    "I35": ["Defrost/Startup","Defrost/Startup",None,"mdi:snowflake-melt",],
    "I36": ["Hot Start","Hot Start",None, None,],
    "I37": ["3-way valve","3-way valve",None,"mdi:pipe-valve",],

    "I38": ["Operation mode read","Operation mode",None, None, ],
    "I40": ["Leaving water temperature PHE","Leaving water temperature PHE","°C","mdi:temperature-celsius",],
    "I41": ["Leaving water temperature BUH","Leaving water temperature BUH","°C","mdi:temperature-celsius",],
    "I42": ["Return water temperature","Return water temperature","°C","mdi:temperature-celsius",],
    "I43": ["Domestic Hot Water temperature","Domestic Hot Water temperature","°C","mdi:temperature-celsius",],

    "I44": ["Outside air temperature","Outside air temperature","°C","mdi:temperature-celsius",],
    "I45": ["Liquid refrigerant temperature","Liquid refrigerant temperature","°C","mdi:temperature-celsius",],
    "I49": ["Flow rate","Flow rate","L/min","mdi:waves",],
    "I50": ["Remote controller room temperature","Remote controller room temperature","°C","mdi:temperature-celsius",],
    "I51": ["Heat pump power consumption","Heat pump power consumption","kW","mdi:lightning-bolt",],

    "I52": ["DHW normal operation","DHW normal operation",None, None,],
    "I53": ["Space heating/cooling normal operation","Space heating/cooling normal operation",None, None,],
    "I54": ["Leaving water Main Heating setpoint Lower limit","Leaving water Main Heating setpoint Lower limit","°C","mdi:temperature-celsius",],
    "I55": ["Leaving water Main Heating setpoint Upper limit","Leaving water Main Heating setpoint Upper limit","°C","mdi:temperature-celsius",],
    "I56": ["Leaving water Main Cooling setpoint Lower limit","Leaving water Main Cooling setpoint Lower limit","°C","mdi:temperature-celsius",],

    "I57": ["Leaving water Main Cooling setpoint Upper limit","Leaving water Main Cooling setpoint Upper limit","°C","mdi:temperature-celsius",],
}

ADDITIONAL_ZONE_SENSOR_TYPES = {
    "H61": ["Thermostat Add Input A","Thermostat_Add_Input_A",None,None,],
    "H63": ["Leaving water Add Heating setpoint","Leaving_water_Add_Heating_setpoint","°C","mdi:temperature-celsius",],
    "H64": ["Leaving water Add Cooling setpoint","Leaving_water_Add_Cooling_setpoint","°C","mdi:temperature-celsius",],
    "H65": ["Weather dependent mode Add","Weather_dependent_mode_Add",None,None,],
    "H66": ["Weather dependent mode Add LWT Heating setpoint offset","Weather_dependent_mode_Add_LWT_Heating_setpoint_offset","°C","mdi:temperature-celsius",],
    "H67": ["Weather dependent mode Add LWT Cooling setpoint offset","Weather_dependent_mode_Add_LWT_Cooling_setpoint_offset","°C","mdi:temperature-celsius",],

    "I58": ["Leaving water Add Heating setpoint Lower limit","Leaving water Add Heating setpoint Lower limit","°C","mdi:temperature-celsius",],
    "I59": ["Leaving water Add Heating setpoint Upper limit","Leaving water Add Heating setpoint Upper limit","°C","mdi:temperature-celsius",],
    "I60": ["Leaving water Add Cooling setpoint Lower limit","Leaving water Add Cooling setpoint Lower limit","°C","mdi:temperature-celsius",],
    "I61": ["Leaving water Add Cooling setpoint Upper limit","Leaving water Add Cooling setpoint Upper limit","°C","mdi:temperature-celsius",],
}


DEVICE_STATUSSES = {
    1: "Off",
    2: "Sleeping (auto-shutdown) / Night mode",
    3: "Grid Monitoring/wake-up",
    4: "Inverter is ON and producing power",
    5: "Production (curtailed)",
    6: "Shutting down",
    7: "Fault",
    8: "Maintenance/setup",
}


DAIKIN_OP_MODE_OPTIONS = {
    0: "Auto",
    1: "Heating",
    2: "Cooling",
}

DAIKIN_SG_MODE_OPTIONS = {
    0: "Free",
    1: "Forced off",
    2: "Recommended on",
    3: "Forced on",
}

DAIKIN_ON_OFF_OPTIONS = {
    0: "Off",
    1: "On",
}

DAIKIN_WEATHER_DEPENDEND_OPTIONS = {
    0: "Fixed",
    1: "Weather dependent",
    2: "Fixed + scheduled",
    3: "Weather dependent + scheduled",
}

DAIKIN_SELECT_TYPES = [
    ["Operation mode", "op_mode", 2, DAIKIN_OP_MODE_OPTIONS],
    ["Space heating / cooling", "space_heating_on_off", 3, DAIKIN_ON_OFF_OPTIONS],
    ["Quiet mode operation", "quiet_mode_operation", 8, DAIKIN_ON_OFF_OPTIONS],
    ["DHW reheat ON/OFF", "DHW_reheat_ON_OFF", 11, DAIKIN_ON_OFF_OPTIONS],
    ["DHW booster mode ON/OFF", "DHW_booster_mode_ON_OFF", 12, DAIKIN_ON_OFF_OPTIONS],
    ["Weather dependent mode Main", "Weather_dependent_mode_Main", 52, DAIKIN_WEATHER_DEPENDEND_OPTIONS],
    ["Smart grid", "Smart_Grid_operation_mode", 55, DAIKIN_SG_MODE_OPTIONS],
    ["Thermostat Main Input A", "Thermostat_Main_Input_A", 58, DAIKIN_ON_OFF_OPTIONS],
]

DAIKIN_ADDITIONAL_ZONE_SELECT_TYPES = [
    ["Thermostat Add Input A", "Thermostat_Add_Input_A", 60, DAIKIN_ON_OFF_OPTIONS],
    ["Weather dependent mode Add", "Weather_dependent_mode_Add", 64, DAIKIN_WEATHER_DEPENDEND_OPTIONS],

]

DAIKIN_NUMBER_TYPES = [
    ["Room thermostat control Heating setpoint", "room_thermo_setpoint_heating", 5, "u16", {"min": 12, "max": 30, "step": 1, "unit": "°C"}],
    ["Room thermostat control Cooling setpoint", "room_thermo_setpoint_cooling", 6, "u16", {"min": 15, "max": 35, "step": 1,"unit": "°C"}],
    ["DHW reheat setpoint", "DHW_reheat_setpoint", 9, "u16", {"min": 30, "max": 60, "step": 1, "unit": "°C"}],
    ["Weather dependent mode Main LWT Heating setpoint offset", "Weather_dependent_mode_main_setpoint_offset", 53, "i16", {"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    ["Weather dependent mode Main LWT Cooling setpoint offset", "Weather_dependent_mode_cooling_setpoint_offset", 54, "i16", {"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    ["Power limit during Recommended on / buffering", "Power_limit_during_Recommended_on_buffering", 56, "pow", {"min": 0, "max": 20, "step": 0.1,"unit": "kW"}],
    ["General power limit", "General_power_limit", 57, "pow", {"min": 0, "max": 20, "step": 0.1,"unit": "kW"}],
]

DAIKIN_ADDITIONAL_ZONE_NUMBER_TYPES = [
    ["Weather dependent mode Add LWT Heating setpoint offset", "Weather_dependent_mode_Add_LWT_Heating_setpoint_offset", 65, "i16", {"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    ["Weather dependent mode Add LWT Cooling setpoint offset", "Weather_dependent_mode_Add_LWT_Cooling_setpoint_offset", 66, "i16", {"min": -10, "max": 10, "step": 1, "unit": "°C"}],
]


A2A_SENSOR_TYPES = {
    "H1001": ["Smart Grid operation mode","A2A_Smart_Grid_operation_mode",None,None,],
    "H1002": ["Power limit for Demand Control","Power_limit_for_Demand_Control","kW","mdi:lightning-bolt",]
}

DAIKIN_A2A_SELECT_TYPES = [
    ["Smart grid", "A2A_Smart_Grid_operation_mode", 1000, DAIKIN_SG_MODE_OPTIONS]
]

DAIKIN_A2A_NUMBER_TYPES = [
    ["Power limit for Demand Control", " Power_limit_for_Demand_Control", 1001, "pow", {"min": 0, "max": 20, "step": 0.1,"unit": "kW"}]
]