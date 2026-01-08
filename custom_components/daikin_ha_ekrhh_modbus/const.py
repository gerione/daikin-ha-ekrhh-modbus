DOMAIN = "daikin_ha_ekrhh_modbus"
DEFAULT_NAME = "daikin_ekrhh"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 502
DEFAULT_MODBUS_ADDRESS = 1
DEFAULT_ADDITIONAL_ZONE = False
CONF_MODBUS_ADDRESS = "modbus_address"
CONF_ADDITIONAL_ZONE = "additional_zone"
CONF_MAX_POWER = "max_power"
CONF_MAX_WATER_TEMP = "max_water_temp"
ATTR_STATUS_DESCRIPTION = "status_description"
ATTR_MANUFACTURER = "Daikin"
CONF_ISAIR2AIR = "is_air_to_air_heatpump"
DEFAULT_AIR2AIR = False
DEFAULT_MAX_POWER = 19
DEFAULT_MAX_WATER_TEMP = 60
CONF_ALTHERMA_VERSION = "altherma_version"
DEFAULT_ALTHERMA_VERSION = 3


ALTHERMA_3_HOLDING = [
    [1,"Leaving water Main Heating setpoint","leave_water_heating_setpoint","INT16",],
    [2,"Leaving water Main Cooling setpoint","leave_water_cooling_setpoint","INT16",],
    [3, "Operation mode", "op_mode","INT16",],
    [4,"Space heating/cooling ON/OFF","space_heating_on_off","INT16",],
    [6,"Room thermostat control Heating setpoint","room_thermo_setpoint_heating","INT16",],
    [7,"Room thermostat control Cooling setpoint","room_thermo_setpoint_cooling","INT16",],
    [9,"Quiet mode operation","quiet_mode_operation","INT16",],
    [10,"DHW reheat setpoint","DHW_reheat_setpoint","INT16",],
    [12,"DHW reheat ON/OF","DHW_reheat_ON_OFF","INT16",],
    [13,"DHW booster mode ON/OFF","DHW_booster_mode_ON_OFF","INT16",],
    [53,"Weather dependent mode Main","Weather_dependent_mode_Main","INT16",],
    [54,"Weather dependent mode Main LWT Heating setpoint offset","Weather_dependent_mode_main_setpoint_offset","INT16",],
    [55,"Weather dependent mode Main LWT Cooling setpoint offset","Weather_dependent_mode_cooling_setpoint_offset","INT16",],
    [56,"Smart Grid operation mode","Smart_Grid_operation_mode","INT16",],
    [57,"Power limit during Recommended on / buffering","Power_limit_during_Recommended_on_buffering","POW16",],
    [58,"General power limit","General_power_limit","POW16",],
    [59,"Thermostat Main Input A","Thermostat_Main_Input_A","INT16",],
    [61, "Thermostat Add Input A","Thermostat_Add_Input_A",None,None,],
    [63, "Leaving water Add Heating setpoint","Leaving_water_Add_Heating_setpoint","°C","mdi:temperature-celsius",],
    [64, "Leaving water Add Cooling setpoint","Leaving_water_Add_Cooling_setpoint","°C","mdi:temperature-celsius",],
    [65, "Weather dependent mode Add","Weather_dependent_mode_Add",None,None,],
    [66, "Weather dependent mode Add LWT Heating setpoint offset","Weather_dependent_mode_Add_LWT_Heating_setpoint_offset","°C","mdi:temperature-celsius",],
    [67, "Weather dependent mode Add LWT Cooling setpoint offset","Weather_dependent_mode_Add_LWT_Cooling_setpoint_offset","°C","mdi:temperature-celsius",],
]


ALTHERMA_3_INPUT = [
    [21,"Unit error","Unit error","INT16",],
    [22,"Unit error code","Unit error code","TEXT16",],
    [23,"Unit error sub code","Unit error sub code","INT16",],
    [30,"Circulation pump running","Circulation pump running","INT16",],
    [31,"Compressor run","Compressor run","INT16",],
    [32,"Booster heater run","Booster heater run","INT16",],
    [33,"Disinfection operation","Disinfection operation","INT16",],
    [35,"Defrost/Startup","Defrost/Startup","INT16",],
    [36,"Hot Start","Hot Start","INT16",],
    [37,"3-way valve","3-way valve","INT16",],
    [38,"Operation mode read","Operation mode","INT16",],
    [40,"Leaving water temperature PHE","Leaving water temperature PHE", "TEMP16",],
    [41,"Leaving water temperature BUH","Leaving water temperature BUH","TEMP16",],
    [42,"Return water temperature","Return water temperature","TEMP16",],
    [43,"Domestic Hot Water temperature","Domestic Hot Water temperature","TEMP16",],
    [44,"Outside air temperature","Outside air temperature","TEMP16",],
    [45,"Liquid refrigerant temperature","Liquid refrigerant temperature","TEMP16",],
    [49,"Flow rate","Flow rate","FLOW16",],
    [50,"Remote controller room temperature","Remote controller room temperature","TEMP16",],
    [51,"Heat pump power consumption","Heat pump power consumption","POW16",],
    [52,"DHW normal operation","DHW normal operation","INT16",],
    [53,"Space heating/cooling normal operation","Space heating/cooling normal operation","INT16",],
    [54,"Leaving water Main Heating setpoint Lower limit","Leaving water Main Heating setpoint Lower limit","TEMP16",],
    [55,"Leaving water Main Heating setpoint Upper limit","Leaving water Main Heating setpoint Upper limit","TEMP16",],
    [56,"Leaving water Main Cooling setpoint Lower limit","Leaving water Main Cooling setpoint Lower limit","TEMP16",],
    [57,"Leaving water Main Cooling setpoint Upper limit","Leaving water Main Cooling setpoint Upper limit","TEMP16",],
    [58,"Leaving Water Add Heating Setpoint Lower limit","Leaving Water Add Heating Setpoint Lower limit","TEMP16",],
    [59,"Leaving Water Add Heating Setpoint Upper limit","Leaving Water Add Heating Setpoint Upper limit","TEMP16",],
    [60,"Leaving Water Add Cooling Setpoint Lower limit","Leaving Water Add Cooling Setpoint Lower limit","TEMP16",],
    [61,"Leaving Water Add Cooling Setpoint Upper limit","Leaving Water Add Cooling Setpoint Upper limit","TEMP16",],
    [84,"Room Heating Setpoint Lower limit","Room Heating Setpoint Lower limit","TEMP16",],
    [85,"Room Heating Setpoint Upper limit","Room Heating Setpoint Upper limit","TEMP16",],
    [86,"Room Cooling Setpoint Lower limit","Room Cooling Setpoint Lower limit","TEMP16",],
    [87,"Room Cooling Setpoint Upper limit","Room Cooling Setpoint Upper limit","TEMP16",],
]

SENSOR_TYPES = {
    "H1": ["Leaving water Main Heating setpoint","leave_water_heating_setpoint","°C","mdi:temperature-celsius",],
    "H2": ["Leaving water Main Cooling setpoint","leave_water_cooling_setpoint","°C","mdi:temperature-celsius",],
    "H3": ["Operation mode", "op_mode", None, None],
    "H6": ["Room thermostat control Heating setpoint","room_thermo_setpoint_heating","°C","mdi:temperature-celsius",],
    "H7": ["Room thermostat control Cooling setpoint","room_thermo_setpoint_cooling","°C","mdi:temperature-celsius",],
    "H10": ["DHW reheat setpoint","DHW_reheat_setpoint","°C","mdi:temperature-celsius",],
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
    "I38": ["Operation mode read","Operation mode",None,None,],
    "I40": ["Leaving water temperature PHE","Leaving water temperature PHE","°C","mdi:temperature-celsius",],
    "I41": ["Leaving water temperature BUH","Leaving water temperature BUH","°C","mdi:temperature-celsius",],
    "I42": ["Return water temperature","Return water temperature","°C","mdi:temperature-celsius",],
    "I43": ["Domestic Hot Water temperature","Domestic Hot Water temperature","°C","mdi:temperature-celsius",],
    "I44": ["Outside air temperature","Outside air temperature","°C","mdi:temperature-celsius",],
    "I45": ["Liquid refrigerant temperature","Liquid refrigerant temperature","°C","mdi:temperature-celsius",],
    "I49": ["Flow rate","Flow rate","L/min","mdi:waves",],
    "I50": ["Remote controller room temperature","Remote controller room temperature","°C","mdi:temperature-celsius",],
    "I51": ["Heat pump power consumption","Heat pump power consumption","kW","mdi:lightning-bolt",],
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
    "I61": ["Leaving water Add Cooling setpoint Upper limit","Leaving water Add Cooling setpoint Upper limit","°C","mdi:temperature-celsius",], }

ALTHERMA_3_BINARY_SENSOR_TYPES = [
    ["DHW reheat ON/OF","DHW_reheat_ON_OFF",None,None,],
    ["DHW booster mode ON/OFF","DHW_booster_mode_ON_OFF",None,None,],
    ["Circulation pump running","Circulation pump running",None,"mdi:pump",],
    ["Compressor run","Compressor run",None,"mdi:heat-pump-outline",],
    ["Booster heater run","Booster heater run",None,"mdi:water-boiler",],
    ["Disinfection operation","Disinfection operation",None,"mdi:spray",],
    ["Defrost/Startup","Defrost/Startup",None,"mdi:snowflake-melt",],
    ["Hot Start","Hot Start",None,None,],
    ["3-way valve","3-way valve",None,"mdi:pipe-valve",],
    ["DHW normal operation","DHW normal operation",None,None,],
    ["Space heating/cooling normal operation","Space heating/cooling normal operation",None,None,], 
]


DEVICE_STATUSES = {1: "Off",2: "Sleeping (auto-shutdown) / Night mode",3: "Grid Monitoring/wake-up",4: "Inverter is ON and producing power",5: "Production (curtailed)",6: "Shutting down",7: "Fault",8: "Maintenance/setup", }
DAIKIN_OP_MODE_OPTIONS = {0: "Auto",1: "Heating",2: "Cooling", }
DAIKIN_SG_MODE_OPTIONS = {0: "Free",1: "Forced off",2: "Recommended on",3: "Forced on", }
DAIKIN_ON_OFF_OPTIONS = {0: "Off",1: "On", }
DAIKIN_WEATHER_DEPENDEND_OPTIONS = {0: "Fixed",1: "Weather dependent",2: "Fixed + scheduled",3: "Weather dependent + scheduled", }
DAIKIN_SELECT_TYPES = [
    ["Operation mode", "op_mode", 2, DAIKIN_OP_MODE_OPTIONS],
    ["Space heating / cooling", "space_heating_on_off", 3, DAIKIN_ON_OFF_OPTIONS],
    ["Quiet mode operation", "quiet_mode_operation", 8, DAIKIN_ON_OFF_OPTIONS],
    ["DHW reheat ON/OFF", "DHW_reheat_ON_OFF", 11, DAIKIN_ON_OFF_OPTIONS],
    ["DHW booster mode ON/OFF", "DHW_booster_mode_ON_OFF", 12, DAIKIN_ON_OFF_OPTIONS],
    ["Weather dependent mode Main","Weather_dependent_mode_Main",52,DAIKIN_WEATHER_DEPENDEND_OPTIONS,],
    ["Smart grid", "Smart_Grid_operation_mode", 55, DAIKIN_SG_MODE_OPTIONS],
    ["Thermostat Main Input A", "Thermostat_Main_Input_A", 58, DAIKIN_ON_OFF_OPTIONS], ]

DAIKIN_ADDITIONAL_ZONE_SELECT_TYPES = [
    ["Thermostat Add Input A", "Thermostat_Add_Input_A", 60, DAIKIN_ON_OFF_OPTIONS],
    ["Weather dependent mode Add","Weather_dependent_mode_Add",64,DAIKIN_WEATHER_DEPENDEND_OPTIONS,], 
]

DAIKIN_NUMBER_TYPES = [
    ["Leaving water Main Heating setpoint","leave_water_heating_setpoint",0,"u16",{"min": 12, "max": 65, "step": 1, "unit": "°C"},],
    ["Leaving water Main Cooling setpoint","leave_water_cooling_setpoint",1,"u16",{"min": 5, "max": 30, "step": 1, "unit": "°C"},],
    ["Room thermostat control Heating setpoint","room_thermo_setpoint_heating",5,"u16",{"min": 12, "max": 30, "step": 1, "unit": "°C"},],
    ["Room thermostat control Cooling setpoint","room_thermo_setpoint_cooling",6,"u16",{"min": 15, "max": 35, "step": 1, "unit": "°C"},],
    ["DHW reheat setpoint","DHW_reheat_setpoint",9,"u16",{"min": 30, "max": 60, "step": 1, "unit": "°C"},],
    ["Weather dependent mode Main LWT Heating setpoint offset","Weather_dependent_mode_main_setpoint_offset",53,"i16",{"min": -10, "max": 10, "step": 1, "unit": "°C"},],
    ["Weather dependent mode Main LWT Cooling setpoint offset","Weather_dependent_mode_cooling_setpoint_offset",54,"i16",{"min": -10, "max": 10, "step": 1, "unit": "°C"},],
    ["Power limit during Recommended on / buffering","Power_limit_during_Recommended_on_buffering",56,"pow",{"min": 0, "max": 20, "step": 0.1, "unit": "kW"},],
    ["General power limit","General_power_limit",57,"pow",{"min": 0, "max": 20, "step": 0.1, "unit": "kW"},], 
]


DAIKIN_ADDITIONAL_ZONE_NUMBER_TYPES = [
    ["Leaving water Add Heating setpoint","Leaving_water_Add_Heating_setpoint",62,"u16",{"min": 12, "max": 65, "step": 1, "unit": "°C"},],
    ["Leaving water Add Cooling setpoint","Leaving_water_Add_Cooling_setpoint",63,"u16",{"min": 5, "max": 30, "step": 1, "unit": "°C"},],
    ["Weather dependent mode Add LWT Heating setpoint offset","Weather_dependent_mode_Add_LWT_Heating_setpoint_offset",65,"i16",{"min": -10, "max": 10, "step": 1, "unit": "°C"},],
    ["Weather dependent mode Add LWT Cooling setpoint offset","Weather_dependent_mode_Add_LWT_Cooling_setpoint_offset",66,"i16",{"min": -10, "max": 10, "step": 1, "unit": "°C"},],
]


A2A_SENSOR_TYPES = {
    "H1001": ["Smart Grid operation mode","A2A_Smart_Grid_operation_mode",None,None,],
    "H1002": ["Power limit for Demand Control","Power_limit_for_Demand_Control","kW","mdi:lightning-bolt",],
}

DAIKIN_A2A_SELECT_TYPES = [
    ["Smart grid", "A2A_Smart_Grid_operation_mode", 1000, DAIKIN_SG_MODE_OPTIONS]
]
DAIKIN_A2A_NUMBER_TYPES = [
    ["Power limit for Demand Control"," Power_limit_for_Demand_Control",1001,"pow",{"min": 0, "max": 20, "step": 0.1, "unit": "kW"},] 
]


# Discrete outputs ("coils"), read/write
ALTHERMA_4_COILS = [
    [1,"Domestic Hot Water On/Off","Domestic_Hot_Water_On_Off"],
    [2,"Main zone On/Off","Main_zone_On_Off"],
    [4,"Enable room heating schedule Main","Enable room heating schedule Main"],
    [5,"Enable room cooling schedule Main","Enable room cooling schedule Main"], 
]

ALTHERMA_4_COILS_ADDITIONAL_ZONE = [
    [3,"Additional zone On/Off","Additional_zone_On_Off"],
    [6,"Enable room heating schedule Add","Enable_room_heating_schedule_Add"],
    [7,"Enable room cooling schedule Add","Enable_room_cooling_schedule_Add"],
]

# Discrete inputs ("contacts"), read-only # Excel formula for generating this list:="["&A3&"," & """"&B3& """,""" &B3 & """,None, None,],"

ALTHERMA_4_DISCRETE_INPUTS = [
    [1,"Shutoff valve","Shutoff_valve"],
    [2,"Backup Heater Relay 1","Backup_Heater_Relay_1"],
    [3,"Backup Heater Relay 2","Backup_Heater_Relay_2"],
    [4,"Backup Heater Relay 3","Backup_Heater_Relay_3"],
    [5,"Backup Heater Relay 4","Backup_Heater_Relay_4"],
    [6,"Backup Heater Relay 5","Backup_Heater_Relay_5"],
    [7,"Backup Heater Relay 6","Backup_Heater_Relay_6"],
    [8,"Booster Heater","Booster_Heater"],
    [9,"Tank Boiler","Tank_Boiler"],
    [10,"Bivalent","Bivalent"],
    [11,"Compressor Run","Compressor_Run"],
    [12,"Quiet mode active","Quiet_mode_active"],
    [13,"Holiday active","Holiday_active"],
    [14,"Antifrost status","Antifrost_status"],
    [15,"Water pipe freeze prevention status","Water_pipe_freeze_prevention_status"],
    [16,"Disinfection Operation","Disinfection_Operation"],
    [17,"Defrost","Defrost"],
    [18,"Hot start","Hot_start"],
    [19,"DHW running","DHW_running"],
    [20,"Main zone running","Main_zone_running"],
    [21,"Additional zone running","Additional_zone_running"],
    [22,"Powerful tank heatup request","Powerful_tank_heatup_request"],
    [23,"Manual tank heatup request","Manual_tank_heatup_request"],
    [24,"Emergency active","Emergency_active"],
    [25,"Circulation Pump Running","Circulation_Pump_Running"],
    [26,"Imposed limit acceptance","Imposed_limit_acceptance"],
]

ALTHERMA_4_BINARY_SENSOR_TYPES = [
    ["Shutoff valve","Shutoff_valve", None, None],
    ["Backup Heater Relay 1","Backup_Heater_Relay_1", None, None],
    ["Backup Heater Relay 2","Backup_Heater_Relay_2", None, None],
    ["Backup Heater Relay 3","Backup_Heater_Relay_3", None, None],
    ["Backup Heater Relay 4","Backup_Heater_Relay_4", None, None],
    ["Backup Heater Relay 5","Backup_Heater_Relay_5", None, None],
    ["Backup Heater Relay 6","Backup_Heater_Relay_6", None, None],
    ["Booster Heater","Booster_Heater", None, "mdi:water-boiler"],
    ["Tank Boiler","Tank_Boiler", None, "mdi:water-boiler"],
    ["Bivalent","Bivalent", None, None],
    ["Compressor Run","Compressor_Run", None, "mdi:compressor"],
    ["Quiet mode active","Quiet_mode_active", None, "mdi:volume"],
    ["Holiday active","Holiday_active", None, None],
    ["Antifrost status","Antifrost_status", None, None],
    ["Water pipe freeze prevention status","Water_pipe_freeze_prevention_status", None, None],
    ["Disinfection Operation","Disinfection_Operation", None, None],
    ["Defrost","Defrost", None, None],
    ["Hot start","Hot_start", None, None],
    ["DHW running","DHW_running", None, None],
    ["Main zone running","Main_zone_running", None, None],
    ["Additional zone running","Additional_zone_running", None, None],
    ["Powerful tank heatup request","Powerful_tank_heatup_request", None, None],
    ["Manual tank heatup request","Manual_tank_heatup_request", None, None],
    ["Emergency active","Emergency_active", None, None],
    ["Circulation Pump Running","Circulation_Pump_Running", None, "mdi:pump"],
    ["Imposed limit acceptance","Imposed_limit_acceptance", None, None],
]

# Analog input registers, read-only
ALTHERMA_4_INPUT = [
    [21,"Unit abnormality","Unit abnormality",None,None,],
    [22,"Unit abnormality Code","Unit abnormality Code",None,None,],
    [23,"Unit abnormality Sub Code","Unit abnormality Sub Code",None,None,],
    [30,"Circulation Pump Running","Circulation Pump Running",None,None,],
    [31,"Compressor Run","Compressor Run",None,None,],
    [32,"Booster Heater Run","Booster Heater Run",None,None,],
    [33,"Disinfection Operation","Disinfection Operation",None,None,],
    [35,"Defrost/restart","Defrost/restart",None,None,],
    [36,"Hot Start","Hot Start",None,None,],
    [37,"3-Way Valve","3-Way Valve",None,None,],
    [38,"Operation Mode","Operation Mode",None,None,],
    [40,"Leaving Water Temperature pre-PHE","Leaving Water Temperature pre-PHE",None,None,],
    [41,"Leaving Water Temperature pre-BUH","Leaving Water Temperature pre-BUH",None,None,],
    [42,"Return Water Temperature","Return Water Temperature",None,None,],
    [43,"Domestic Hot Water Temperature","Domestic Hot Water Temperature",None,None,],
    [44,"Outside Air Temperature","Outside Air Temperature",None,None,],
    [45,"Liquid Refrigerant Temperature","Liquid Refrigerant Temperature",None,None,],
    [49,"Flow Rate","Flow Rate",None,None,],[50,"Remote controller room temperature (main)","Remote controller room temperature (main)",None,None,],
    [51,"Heatpump power consumption","Heatpump power consumption",None,None,],
    [52,"DHW normal operation","DHW normal operation",None,None,],
    [53,"Space heating/cooling normal operation","Space heating/cooling normal operation",None,None,],
    [54,"Leaving Water Main Heating Setpoint Lower limit","Leaving Water Main Heating Setpoint Lower limit",None,None,],
    [55,"Leaving Water Main Heating Setpoint Upper limit","Leaving Water Main Heating Setpoint Upper limit",None,None,],
    [56,"Leaving Water Main Cooling Setpoint Lower limit","Leaving Water Main Cooling Setpoint Lower limit",None,None,],
    [57,"Leaving Water Main Cooling Setpoint Upper limit","Leaving Water Main Cooling Setpoint Upper limit",None,None,],
    [58,"Leaving Water Add Heating Setpoint Lower limit","Leaving Water Add Heating Setpoint Lower limit",None,None,],
    [59,"Leaving Water Add Heating Setpoint Upper limit","Leaving Water Add Heating Setpoint Upper limit",None,None,],
    [60,"Leaving Water Add Cooling Setpoint Lower limit","Leaving Water Add Cooling Setpoint Lower limit",None,None,],
    [61,"Leaving Water Add Cooling Setpoint Upper limit","Leaving Water Add Cooling Setpoint Upper limit",None,None,],
    [63,"Disinfaction state","Disinfaction state",None,None,],[64,"Holiday mode","Holiday mode",None,None,],
    [65,"Demand response mode","Demand response mode",None,None,],[66,"Bypass Valve Position","Bypass Valve Position",None,None,],
    [67,"Tank Valve Position","Tank Valve Position",None,None,],
    [68,"Circulation Pump Speed","Circulation Pump Speed",None,None,],[69,"Mixed Pump PWM in Mixing kit","Mixed Pump PWM in Mixing kit",None,None,],
    [70,"Direct Pump PWM in Mixing kit","Direct Pump PWM in Mixing kit",None,None,],
    [71,"Mixing Valve Position in Mixing kit","Mixing Valve Position in Mixing kit",None,None,],
    [72,"Mixing Leaving Water Temperature in Mixing kit","Mixing Leaving Water Temperature in Mixing kit",None,None,],
    [73,"Spaceheating/cooling target for main zone in Mixing kit","Spaceheating/cooling target for main zone in Mixing kit",None,None,],
    [74,"Leaving Water Temperature pre-PHE outdoor","Leaving Water Temperature pre-PHE outdoor",None,None,],
    [75,"Leaving Water Temperature Tank valve","Leaving Water Temperature Tank valve",None,None,],
    [76,"Domestic Hot Water Upper Temperature","Domestic Hot Water Upper Temperature",None,None,],
    [77,"Domestic Hot Water Lower Temperature","Domestic Hot Water Lower Temperature",None,None,],
    [78,"Remote controller room temperature (add)","Remote controller room temperature (add)",None,None,],
    [79,"Water pressure","Water pressure",None,None,],
    [80,"Spaceheating/cooling target for main zone","Spaceheating/cooling target for main zone",None,None,],
    [81,"Spaceheating/cooling target for add zone","Spaceheating/cooling target for add zone",None,None,],
    [82,"Abnormality counter (user)","Abnormality counter (user)",None,None,],
    [83,"Unit operation mode","Unit operation mode",None,None,],
    [84,"Room Heating Setpoint Lower limit","Room Heating Setpoint Lower limit",None,None,],
    [85,"Room Heating Setpoint Upper limit","Room Heating Setpoint Upper limit",None,None,],
    [86,"Room Cooling Setpoint Lower limit","Room Cooling Setpoint Lower limit",None,None,],
    [87,"Room Cooling Setpoint Upper limit","Room Cooling Setpoint Upper limit",None,None,], 
]

ALTHERMA_4_HOLDING = [
    [1,"Leaving Water Main Heating Setpoint","Leaving Water Main Heating Setpoint",None,None,],
    [2,"Leaving Water Main Cooling Setpoint","Leaving Water Main Cooling Setpoint",None,None,],
    [3,"Operation Mode","Operation Mode",None,None,],[4,"Space Heating/Cooling On/Off","Space Heating/Cooling On/Off",None,None,],
    # Leave the next two out as they are outdated (see Excel)
    # [6,"Room Thermostat Control Heating Setpoint Main","Room Thermostat Control Heating Setpoint Main",None,None,],
    # [7,"Room Thermostat Control Cooling Setpoint Main","Room Thermostat Control Cooling Setpoint Main",None,None,],
    [9,"Quiet Mode Operation","Quiet Mode Operation",None,None,],
    [10,"DHW reheat Setpoint","DHW reheat Setpoint",None,None,],
    [13,"DHW Booster Mode On/Off (powerful)","DHW Booster Mode On/Off (powerful)",None,None,],
    [14,"DHW Boost setpoint (powerful)","DHW Boost setpoint (powerful)",None,None,],
    [15,"DHW Single heat-up On/Off (manual)","DHW Single heat-up On/Off (manual)",None,None,],
    [16,"DHW Single heat-up  setpoint (manual)","DHW Single heat-up  setpoint (manual)",None,None,],
    [54,"Weather Dependent Mode Main LWT Heating Setpoint Offset","Weather Dependent Mode Main LWT Heating Setpoint Offset",None,None,],
    [55,"Weather Dependent Mode Main LWT Cooling Setpoint Offset","Weather Dependent Mode Main LWT Cooling Setpoint Offset",None,None,],
    [56,"Smart grid operation mode","Smart grid operation mode",None,None,],
    [58,"General power limit","General power limit",None,None,],
    [63,"Leaving Water Add Heating Setpoint","Leaving Water Add Heating Setpoint",None,None,],
    [64,"Leaving Water Add Cooling Setpoint","Leaving Water Add Cooling Setpoint",None,None,],
    [66,"Weather Dependent Mode Add LWT Heating Setpoint Offset","Weather Dependent Mode Add LWT Heating Setpoint Offset",None,None,],
    [67,"Weather Dependent Mode Add LWT Cooling Setpoint Offset","Weather Dependent Mode Add LWT Cooling Setpoint Offset",None,None,],
    [68,"Weather Dependent Mode heating Main","Weather Dependent Mode heating Main",None,None,],
    [69,"Weather Dependent Mode cooling Main","Weather Dependent Mode cooling Main",None,None,],
    [71,"Weather Dependent Mode heating Add","Weather Dependent Mode heating Add",None,None,],
    [72,"Weather Dependent Mode cooling Add","Weather Dependent Mode cooling Add",None,None,],
    [74,"Thermostat request main","Thermostat request main",None,None,],
    [75,"Thermostat request add","Thermostat request add",None,None,],
    [76,"Room Thermostat Control Heating Setpoint Main","Room Thermostat Control Heating Setpoint Main",None,None,],
    [77,"Room Thermostat Control Cooling Setpoint Main","Room Thermostat Control Cooling Setpoint Main",None,None,],
    [78,"Room Thermostat Control Heating Setpoint Add","Room Thermostat Control Heating Setpoint Add",None,None,],
    [79,"Room Thermostat Control Cooling Setpoint Add","Room Thermostat Control Cooling Setpoint Add",None,None,],
    [80,"DHW Mode setting","DHW Mode setting",None,None,],
]

DAIKIN_4_NUMBER_TYPES = [
    ["Leaving water Main Heating setpoint","Leaving Water Main Heating Setpoint",0,"i16",{"min": 0, "max": 100, "step": 1, "unit": "°C"},],
    ["Leaving water Main Cooling setpoint","Leaving Water Main Cooling Setpoint",1,"i16",{"min": 0, "max": 100, "step": 1, "unit": "°C"},],
    ["DHW reheat Setpoint","DHW reheat Setpoint",9,"i16",{"min": 30, "max": 85, "step": 1, "unit": "°C"},],
    ["DHW Boost setpoint (powerful)","DHW Boost setpoint (powerful)",9,"pow",{"min": 30, "max": 85, "step": 1, "unit": "°C"},],
    ["DHW Single heat-up  setpoint (manual)","DHW Single heat-up  setpoint (manual)",9,"pow",{"min": 30, "max": 85, "step": 1, "unit": "°C"},],

    ["Weather dependent mode Main LWT Heating setpoint offset","Weather Dependent Mode Main LWT Heating Setpoint Offset",53,"pow",{"min": -10, "max": 10, "step": 1, "unit": "°C"},],
    ["Weather dependent mode Main LWT Cooling setpoint offset","Weather Dependent Mode Main LWT Cooling Setpoint Offset",54,"pow",{"min": -10, "max": 10, "step": 1, "unit": "°C"},],

    ["General power limit","General power limit",57,"pow",{"min": 0, "max": 20, "step": 0.1, "unit": "kW"},],
    ["Room Thermostat Control Heating Setpoint Main","Room Thermostat Control Heating Setpoint Main",9,"pow",{"min": 12, "max": 35, "step": 1, "unit": "°C"},],
    ["Room Thermostat Control Cooling Setpoint Main","Room Thermostat Control Cooling Setpoint Main",9,"pow",{"min": 12, "max": 35, "step": 1, "unit": "°C"},],
]

DAIKIN_4_ADDITIONAL_ZONE_NUMBER_TYPES = [
    ["Leaving Water Add Heating Setpoint","Leaving Water Add Heating Setpoint",5,"pow",{"min": 3, "max": 85, "step": 1, "unit": "°C"},],
    ["Leaving Water Add Cooling Setpoint","Leaving Water Add Cooling Setpoint",5,"pow",{"min": 3, "max": 85, "step": 1, "unit": "°C"},],
    ["Weather Dependent Mode Add LWT Heating Setpoint Offset","Weather Dependent Mode Add LWT Heating Setpoint Offset",5,"pow",{"min": -10, "max": 10, "step": 1, "unit": "°C"},],
    ["Weather Dependent Mode Add LWT Cooling Setpoint Offset","Weather Dependent Mode Add LWT Cooling Setpoint Offset",6,"pow",{"min": -10, "max": 10, "step": 1, "unit": "°C"},],
    ["Room Thermostat Control Heating Setpoint Add","Room Thermostat Control Heating Setpoint Add",9,"pow",{"min": 12, "max": 35, "step": 1, "unit": "°C"},],
    ["Room Thermostat Control Cooling Setpoint Add","Room Thermostat Control Cooling Setpoint Add",9,"pow",{"min": 12, "max": 35, "step": 1, "unit": "°C"},],
]