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

DAIKIN_OP_MODE_OPTIONS = {0: "Auto",1: "Heating",2: "Cooling", }
DAIKIN_SG_MODE_OPTIONS = {0: "Free",1: "Forced off",2: "Recommended on",3: "Forced on", }
DAIKIN_ON_OFF_OPTIONS = {0: "Off",1: "On", }
DAIKIN_ON_ONAUTO_OFF_OPTIONS = {0: "Off",1: "On (Automatic)",2: "On (Manual)", }
DAIKIN_WEATHER_DEPENDEND_OPTIONS = {0: "Fixed",1: "Weather dependent",2: "Fixed + scheduled",3: "Weather dependent + scheduled", }
DAIKIN_WEATHER_DEPENDEND_OPTIONS_2 = {0: "Fixed",1: "Weather dependent" }
DAIKIN_4_OP_MODE_OPTIONS = {0: "None",1: "Heating",2: "Cooling", }
DAIKIN_4_DHW_MODE_OPTIONS = {0: "Reheat",1: "Schedule and reheat",2: "Scheduled", }


ALTHERMA_3_HOLDING = [
    [1,"Leaving water Main Heating setpoint",f"{DOMAIN}_altherma3_holding_1","INT16","°C","mdi:temperature-celsius",{"min": 12, "max": 65, "step": 1, "unit": "°C"}],
    [2,"Leaving water Main Cooling setpoint",f"{DOMAIN}_altherma3_holding_2","INT16","°C","mdi:temperature-celsius",{"min": 5, "max": 30, "step": 1, "unit": "°C"}],
    [6,"Room thermostat control Heating setpoint",f"{DOMAIN}_altherma3_holding_6","INT16","°C","mdi:temperature-celsius",{"min": 12, "max": 30, "step": 1, "unit": "°C"}],
    [7,"Room thermostat control Cooling setpoint",f"{DOMAIN}_altherma3_holding_7","INT16","°C","mdi:temperature-celsius",{"min": 15, "max": 35, "step": 1, "unit": "°C"}],
    [10,"DHW reheat setpoint",f"{DOMAIN}_altherma3_holding_10","INT16","°C","mdi:temperature-celsius",{"min": 30, "max": 60, "step": 1, "unit": "°C"}],
    [54,"Weather dependent mode Main LWT Heating setpoint offset",f"{DOMAIN}_altherma3_holding_54","INT16","°C","mdi:temperature-celsius",{"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    [55,"Weather dependent mode Main LWT Cooling setpoint offset",f"{DOMAIN}_altherma3_holding_55","INT16","°C","mdi:temperature-celsius",{"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    [57,"Power limit during Recommended on / buffering",f"{DOMAIN}_altherma3_holding_57","POW16","kW","mdi:lightning-bolt",{"min": 0, "max": 20, "step": 0.1, "unit": "kW"}],
    [58,"General power limit",f"{DOMAIN}_altherma3_holding_58","POW16","kW","mdi:lightning-bolt",{"min": 0, "max": 20, "step": 0.1, "unit": "kW"}],
]

ALTHERMA_3_HOLDING_ADDITIONAL_ZONE = [
    [63,"Leaving water Add Heating setpoint",f"{DOMAIN}_altherma3_holding_63","INT16","°C","mdi:temperature-celsius",{"min": 12, "max": 65, "step": 1, "unit": "°C"}],
    [64, "Leaving water Add Cooling setpoint",f"{DOMAIN}_altherma3_holding_64","INT16","°C","mdi:temperature-celsius",{"min": 5, "max": 30, "step": 1, "unit": "°C"}],
    [66, "Weather dependent mode Add LWT Heating setpoint offset",f"{DOMAIN}_altherma3_holding_66","INT16","°C","mdi:temperature-celsius",{"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    [67, "Weather dependent mode Add LWT Cooling setpoint offset",f"{DOMAIN}_altherma3_holding_67","INT16","°C","mdi:temperature-celsius",{"min": -10, "max": 10, "step": 1, "unit": "°C"}],
]

ALTHERMA_3_HOLDING_SELECT = [
    [3, "Operation mode", f"{DOMAIN}_altherma3_holding_3", "INT16",None,None, DAIKIN_OP_MODE_OPTIONS],
    [4, "Space heating / cooling ON/OFF", f"{DOMAIN}_altherma3_holding_4", "INT16", None,None, DAIKIN_ON_OFF_OPTIONS],
    [9, "Quiet mode operation", f"{DOMAIN}_altherma3_holding_9", "INT16",None,"mdi:volume-mute", DAIKIN_ON_OFF_OPTIONS],
    [12, "DHW reheat ON/OFF", f"{DOMAIN}_altherma3_holding_12", "INT16", None, None,  DAIKIN_ON_OFF_OPTIONS],
    [13, "DHW booster mode ON/OFF", f"{DOMAIN}_altherma3_holding_13", "INT16", None, None,  DAIKIN_ON_OFF_OPTIONS],
    [53, "Weather dependent mode Main", f"{DOMAIN}_altherma3_holding_53", "INT16",None,None, DAIKIN_WEATHER_DEPENDEND_OPTIONS],
    [56, "Smart grid", f"{DOMAIN}_altherma3_holding_56", "INT16",None,None, DAIKIN_SG_MODE_OPTIONS],
    [59, "Thermostat Main Input A", f"{DOMAIN}_altherma3_holding_59", "INT16",None,None, DAIKIN_ON_OFF_OPTIONS],
]

ALTHERMA_3_HOLDING_SELECT_ADDITIONAL_ZONE = [
    [61, "Thermostat Add Input A", f"{DOMAIN}_altherma3_holding_61", "INT16", None, None,  DAIKIN_ON_OFF_OPTIONS],
    [65, "Weather dependent mode Add", f"{DOMAIN}_altherma3_holding_65", "INT16", None, None,  DAIKIN_WEATHER_DEPENDEND_OPTIONS],
]

ALTHERMA_3_INPUT = [
    [21,"Unit error",f"{DOMAIN}_altherma3_input_21","INT16",None,"mdi:alert-circle",],
    [22,"Unit error code",f"{DOMAIN}_altherma3_input_22","TEXT16",None,"mdi:alert-circle",],
    [23,"Unit error sub code",f"{DOMAIN}_altherma3_input_23","INT16",None,"mdi:alert-circle",],
    [38,"Operation mode read",f"{DOMAIN}_altherma3_input_38","INT16",None,None, DAIKIN_OP_MODE_OPTIONS],
    [40,"Leaving water temperature PHE",f"{DOMAIN}_altherma3_input_40", "TEMP16","°C","mdi:temperature-celsius",],
    [41,"Leaving water temperature BUH",f"{DOMAIN}_altherma3_input_41","TEMP16","°C","mdi:temperature-celsius",],
    [42,"Return water temperature",f"{DOMAIN}_altherma3_input_42","TEMP16","°C","mdi:temperature-celsius",],
    [43,"Domestic Hot Water temperature",f"{DOMAIN}_altherma3_input_43","TEMP16","°C","mdi:temperature-celsius",],
    [44,"Outside air temperature",f"{DOMAIN}_altherma3_input_44","TEMP16","°C","mdi:temperature-celsius",],
    [45,"Liquid refrigerant temperature",f"{DOMAIN}_altherma3_input_45","TEMP16","°C","mdi:temperature-celsius",],
    [49,"Flow rate",f"{DOMAIN}_altherma3_input_49","FLOW16","L/min",None,],
    [50,"Remote controller room temperature",f"{DOMAIN}_altherma3_input_50","TEMP16","°C","mdi:temperature-celsius",],
    [51,"Heat pump power consumption",f"{DOMAIN}_altherma3_input_51","POW16","kW","mdi:lightning-bolt"],
    [54,"Leaving water Main Heating setpoint Lower limit",f"{DOMAIN}_altherma3_input_54","TEMP16","°C","mdi:temperature-celsius",],
    [55,"Leaving water Main Heating setpoint Upper limit",f"{DOMAIN}_altherma3_input_55","TEMP16","°C","mdi:temperature-celsius",],
    [56,"Leaving water Main Cooling setpoint Lower limit",f"{DOMAIN}_altherma3_input_56","TEMP16","°C","mdi:temperature-celsius",],
    [57,"Leaving water Main Cooling setpoint Upper limit",f"{DOMAIN}_altherma3_input_57","TEMP16","°C","mdi:temperature-celsius",],
 #   [84,"Room Heating Setpoint Lower limit",f"{DOMAIN}_altherma3_input_84","TEMP16","°C","mdi:temperature-celsius",],
 #   [85,"Room Heating Setpoint Upper limit",f"{DOMAIN}_altherma3_input_85","TEMP16","°C","mdi:temperature-celsius",],
 #   [86,"Room Cooling Setpoint Lower limit",f"{DOMAIN}_altherma3_input_86","TEMP16","°C","mdi:temperature-celsius",],
 #   [87,"Room Cooling Setpoint Upper limit",f"{DOMAIN}_altherma3_input_87","TEMP16","°C","mdi:temperature-celsius"],
]

ALTHERMA_3_INPUT_ADDITIONAL_ZONE = [
    [58,"Leaving water Add Heating setpoint Lower limit",f"{DOMAIN}_altherma3_input_58","TEMP16","°C","mdi:temperature-celsius",],
    [59,"Leaving water Add Heating setpoint Upper limit",f"{DOMAIN}_altherma3_input_59","TEMP16","°C","mdi:temperature-celsius",],
    [60,"Leaving water Add Cooling setpoint Lower limit",f"{DOMAIN}_altherma3_input_60","TEMP16","°C","mdi:temperature-celsius",],
    [61,"Leaving water Add Cooling setpoint Upper limit",f"{DOMAIN}_altherma3_input_61","TEMP16","°C","mdi:temperature-celsius",],
]

ALTHERMA_3_INPUT_BINARY = [
    [30,"Circulation pump running",f"{DOMAIN}_altherma3_input_30","INT16",None,"mdi:pump",],
    [31,"Compressor run",f"{DOMAIN}_altherma3_input_31","INT16",None,"mdi:fan",],
    [32,"Booster heater run",f"{DOMAIN}_altherma3_input_32","INT16",None,"mdi:fire",],
    [33,"Disinfection operation",f"{DOMAIN}_altherma3_input_33","INT16",None,"mdi:water-pump",],
    [35,"Defrost/Startup",f"{DOMAIN}_altherma3_input_35","INT16",None,"mdi:thermometer",],
    [36,"Hot Start",f"{DOMAIN}_altherma3_input_36","INT16",None,"mdi:fire",],
    [37,"3-way valve",f"{DOMAIN}_altherma3_input_37","INT16",None,"mdi:valve",],
    [52,"DHW normal operation",f"{DOMAIN}_altherma3_input_52","INT16",None,None,],
    [53,"Space heating/cooling normal operation",f"{DOMAIN}_altherma3_input_53","INT16",None,None,],
]

A2A_SENSOR_TYPES = {
    "H1001": ["Smart Grid operation mode","A2A_Smart_Grid_operation_mode",None,None,],
    "H1002": ["Power limit for Demand Control","Power_limit_for_Demand_Control","kW","mdi:lightning-bolt",],
}

DAIKIN_A2A_SELECT_TYPES = [
    ["Smart grid", "A2A_Smart_Grid_operation_mode", 1000, DAIKIN_SG_MODE_OPTIONS, ]
]
DAIKIN_A2A_NUMBER_TYPES = [
    ["Power limit for Demand Control"," Power_limit_for_Demand_Control",1001,"POW16",{"min": 0, "max": 20, "step": 0.1, "unit": "kW"},]
]

# Discrete outputs ("coils"), read/write
ALTHERMA_4_COILS = [
    [1,"Domestic Hot Water On/Off",f"{DOMAIN}_altherma4_coil_1", "BIT", None, None],
    [2,"Main zone On/Off",f"{DOMAIN}_altherma4_coil_2", "BIT", None, None],
    [4,"Enable room heating schedule Main",f"{DOMAIN}_altherma4_coil_4", "BIT", None, None],
    [5,"Enable room cooling schedule Main",f"{DOMAIN}_altherma4_coil_5", "BIT", None, None],
]

ALTHERMA_4_COILS_ADDITIONAL_ZONE = [
    [3,"Additional zone On/Off",f"{DOMAIN}_altherma4_coil_3", "BIT", None, None],
    [6,"Enable room heating schedule Add",f"{DOMAIN}_altherma4_coil_6", "BIT", None, None],
    [7,"Enable room cooling schedule Add",f"{DOMAIN}_altherma4_coil_7", "BIT", None, None],
]

# Discrete inputs ("contacts"), read-only # Excel formula for generating this list:="["&A3&"," & """"&B3& """,""" &B3 & """,None, None,],"

ALTHERMA_4_DISCRETE_INPUTS = [
    [1,"Shutoff valve",f"{DOMAIN}_altherma4_discrete_input_1","BIT", None, None],
    [2,"Backup Heater Relay 1",f"{DOMAIN}_altherma4_discrete_input_2", "BIT", None, None],
    [3,"Backup Heater Relay 2",f"{DOMAIN}_altherma4_discrete_input_3", "BIT", None, None],
    [4,"Backup Heater Relay 3",f"{DOMAIN}_altherma4_discrete_input_4", "BIT", None, None],
    [5,"Backup Heater Relay 4",f"{DOMAIN}_altherma4_discrete_input_5", "BIT", None, None],
    [6,"Backup Heater Relay 5",f"{DOMAIN}_altherma4_discrete_input_6", "BIT", None, None],
    [7,"Backup Heater Relay 6",f"{DOMAIN}_altherma4_discrete_input_7", "BIT", None, None],
    [8,"Booster Heater",f"{DOMAIN}_altherma4_discrete_input_8", "BIT", None, None],
    [9,"Tank Boiler",f"{DOMAIN}_altherma4_discrete_input_9", "BIT", None, None],
    [10,"Bivalent",f"{DOMAIN}_altherma4_discrete_input_10", "BIT", None, None],
    [11,"Compressor Run",f"{DOMAIN}_altherma4_discrete_input_11", "BIT", None, None],
    [12,"Quiet mode active",f"{DOMAIN}_altherma4_discrete_input_12", "BIT", None, None],
    [13,"Holiday active",f"{DOMAIN}_altherma4_discrete_input_13", "BIT", None, None],
    [14,"Antifrost status",f"{DOMAIN}_altherma4_discrete_input_14", "BIT", None, None],
    [15,"Water pipe freeze prevention status",f"{DOMAIN}_altherma4_discrete_input_15", "BIT", None, None],
    [16,"Disinfection Operation",f"{DOMAIN}_altherma4_discrete_input_16", "BIT", None, None],
    [17,"Defrost",f"{DOMAIN}_altherma4_discrete_input_17", "BIT", None, None],
    [18,"Hot start",f"{DOMAIN}_altherma4_discrete_input_18", "BIT", None, None],
    [19,"DHW running",f"{DOMAIN}_altherma4_discrete_input_19", "BIT", None, None],
    [20,"Main zone running",f"{DOMAIN}_altherma4_discrete_input_20", "BIT", None, None],
    [22,"Powerful tank heatup request",f"{DOMAIN}_altherma4_discrete_input_22", "BIT", None, None],
    [23,"Manual tank heatup request",f"{DOMAIN}_altherma4_discrete_input_23", "BIT", None, None],
    [24,"Emergency active",f"{DOMAIN}_altherma4_discrete_input_24", "BIT", None, None],
    [25,"Circulation Pump Running",f"{DOMAIN}_altherma4_discrete_input_25", "BIT", None, None],
    [26,"Imposed limit acceptance",f"{DOMAIN}_altherma4_discrete_input_26", "BIT", None, None],
]

ALTHERMA_4_DISCRETE_INPUTS_ADDITIONAL_ZONE = [
    [21,"Additional zone running",f"{DOMAIN}_altherma4_discrete_input_21", None, None],
]


# Analog input registers, read-only
ALTHERMA_4_INPUT = [
    [21,"Unit abnormality",f"{DOMAIN}_altherma4_input_21","INT16",None,None,],
    [22,"Unit abnormality Code",f"{DOMAIN}_altherma4_input_22","TEXT16",None,None,],
    [23,"Unit abnormality Sub Code",f"{DOMAIN}_altherma4_input_23","INT16",None,None,],
    [40,"Leaving Water Temperature pre-PHE",f"{DOMAIN}_altherma4_input_40","TEMP16",None,None,],
    [41,"Leaving Water Temperature pre-BUH",f"{DOMAIN}_altherma4_input_41","TEMP16",None,None,],
    [42,"Return Water Temperature",f"{DOMAIN}_altherma4_input_42","TEMP16",None,None,],
    [43,"Domestic Hot Water Temperature",f"{DOMAIN}_altherma4_input_43","TEMP16",None,None,],
    [44,"Outside Air Temperature",f"{DOMAIN}_altherma4_input_44","TEMP16",None,None,],
    [45,"Liquid Refrigerant Temperature",f"{DOMAIN}_altherma4_input_45","TEMP16",None,None,],
    [49,"Flow Rate",f"{DOMAIN}_altherma4_input_49","INT16",None,None,],
    [50,"Remote controller room temperature (main)",f"{DOMAIN}_altherma4_input_50","TEMP16",None,None,],
    [51,"Heatpump power consumption",f"{DOMAIN}_altherma4_input_51","POW16",None,None,],
    [54,"Leaving Water Main Heating Setpoint Lower limit",f"{DOMAIN}_altherma4_input_54","TEMP16",None,None,],
    [55,"Leaving Water Main Heating Setpoint Upper limit",f"{DOMAIN}_altherma4_input_55","TEMP16",None,None,],
    [56,"Leaving Water Main Cooling Setpoint Lower limit",f"{DOMAIN}_altherma4_input_56","TEMP16",None,None,],
    [57,"Leaving Water Main Cooling Setpoint Upper limit",f"{DOMAIN}_altherma4_input_57","TEMP16",None,None,],
    [63,"Disinfaction state",f"{DOMAIN}_altherma4_input_63","INT16",None,None,],
    [65,"Demand response mode",f"{DOMAIN}_altherma4_input_65","INT16",None,None,],
    [66,"Bypass Valve Position",f"{DOMAIN}_altherma4_input_66","INT16",None,None,],
    [67,"Tank Valve Position",f"{DOMAIN}_altherma4_input_67","INT16",None,None,],
    [68,"Circulation Pump Speed",f"{DOMAIN}_altherma4_input_68","INT16",None,None,],
    [69,"Mixed Pump PWM in Mixing kit",f"{DOMAIN}_altherma4_input_69","INT16",None,None,],
    [70,"Direct Pump PWM in Mixing kit",f"{DOMAIN}_altherma4_input_70","INT16",None,None,],
    [71,"Mixing Valve Position in Mixing kit",f"{DOMAIN}_altherma4_input_71","INT16",None,None,],
    [72,"Mixing Leaving Water Temperature in Mixing kit",f"{DOMAIN}_altherma4_input_72","TEMP16",None,None,],
    [73,"Spaceheating/cooling target for main zone in Mixing kit",f"{DOMAIN}_altherma4_input_73","TEMP16",None,None,],
    [74,"Leaving Water Temperature pre-PHE outdoor",f"{DOMAIN}_altherma4_input_74","TEMP16",None,None,],
    [75,"Leaving Water Temperature Tank valve",f"{DOMAIN}_altherma4_input_75","TEMP16",None,None,],
    [76,"Domestic Hot Water Upper Temperature",f"{DOMAIN}_altherma4_input_76","TEMP16",None,None,],
    [77,"Domestic Hot Water Lower Temperature",f"{DOMAIN}_altherma4_input_77","TEMP16",None,None,],
    [79,"Water pressure",f"{DOMAIN}_altherma4_input_79","INT16",None,None,],
    [80,"Spaceheating/cooling target for main zone",f"{DOMAIN}_altherma4_input_80","TEMP16",None,None,],
    [82,"Abnormality counter (user)",f"{DOMAIN}_altherma4_input_82","INT16",None,None,],
    [83,"Unit operation mode",f"{DOMAIN}_altherma4_input_83","INT16",None,None,],
    [84,"Room Heating Setpoint Lower limit",f"{DOMAIN}_altherma4_input_84","TEMP16",None,None,],
    [85,"Room Heating Setpoint Upper limit",f"{DOMAIN}_altherma4_input_85","TEMP16",None,None,],
    [86,"Room Cooling Setpoint Lower limit",f"{DOMAIN}_altherma4_input_86","TEMP16",None,None,],
    [87,"Room Cooling Setpoint Upper limit",f"{DOMAIN}_altherma4_input_87","TEMP16",None,None,],
]

ALTHERMA_4_INPUT_ADDITIONAL_ZONE = [
    [58,"Leaving Water Add Heating Setpoint Lower limit",f"{DOMAIN}_altherma4_input_58","TEMP16",None,None,],
    [59,"Leaving Water Add Heating Setpoint Upper limit",f"{DOMAIN}_altherma4_input_59","TEMP16",None,None,],
    [60,"Leaving Water Add Cooling Setpoint Lower limit",f"{DOMAIN}_altherma4_input_60","TEMP16",None,None,],
    [61,"Leaving Water Add Cooling Setpoint Upper limit",f"{DOMAIN}_altherma4_input_61","TEMP16",None,None,],
    [78,"Remote controller room temperature (add)",f"{DOMAIN}_altherma4_input_78","TEMP16",None,None,],
    [81,"Spaceheating/cooling target for add zone",f"{DOMAIN}_altherma4_input_81","TEMP16",None,None,],
]

ALTHERMA_4_INPUT_BINARY = [
    [30,"Circulation Pump Running",f"{DOMAIN}_altherma4_input_30","INT16",None,None,],
    [31,"Compressor Run",f"{DOMAIN}_altherma4_input_31","INT16",None,None,],
    [32,"Booster Heater Run",f"{DOMAIN}_altherma4_input_32","INT16",None,None,],
    [33,"Disinfection Operation",f"{DOMAIN}_altherma4_input_33","INT16",None,None,],
    [35,"Defrost/restart",f"{DOMAIN}_altherma4_input_35","INT16",None,None,],
    [36,"Hot Start",f"{DOMAIN}_altherma4_input_36","INT16",None,None,],
    [37,"3-Way Valve",f"{DOMAIN}_altherma4_input_37","INT16",None,None,],
    [38,"Operation Mode",f"{DOMAIN}_altherma4_input_38","INT16",None,None,],
    [52,"DHW normal operation",f"{DOMAIN}_altherma4_input_52","INT16",None,None,],
    [53,"Space heating/cooling normal operation",f"{DOMAIN}_altherma4_input_53","INT16",None,None,],
    [64,"Holiday mode",f"{DOMAIN}_altherma4_input_64","INT16",None,None,],
]

ALTHERMA_4_HOLDING = [
    [1,"Leaving Water Main Heating Setpoint",f"{DOMAIN}_altherma4_holding_1","INT16",None, None, {"min": 0, "max": 100, "step": 1, "unit": "°C"}],
    [2,"Leaving Water Main Cooling Setpoint",f"{DOMAIN}_altherma4_holding_2","INT16",None, None, {"min": 0, "max": 100, "step": 1, "unit": "°C"}],
    # Leave the next two out as they are outdated (see Excel)
    # [6,"Room Thermostat Control Heating Setpoint Main","Room Thermostat Control Heating Setpoint Main",None,None,],
    # [7,"Room Thermostat Control Cooling Setpoint Main","Room Thermostat Control Cooling Setpoint Main",None,None,],
    [10,"DHW reheat Setpoint",f"{DOMAIN}_altherma4_holding_10","INT16",None, None, {"min": 30, "max": 85, "step": 1, "unit": "°C"},],
    [14,"DHW Boost setpoint (powerful)",f"{DOMAIN}_altherma4_holding_14","TEMP16",None, None, {"min": 30, "max": 85, "step": 0.1, "unit": "°C"}],
    [16,"DHW Single heat-up  setpoint (manual)",f"{DOMAIN}_altherma4_holding_16","TEMP16",None, None,{"min": 30, "max": 85, "step": 0.1, "unit": "°C"}],
    [54,"Weather Dependent Mode Main LWT Heating Setpoint Offset",f"{DOMAIN}_altherma4_holding_54","INT16",None, None,{"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    [55,"Weather Dependent Mode Main LWT Cooling Setpoint Offset",f"{DOMAIN}_altherma4_holding_55","INT16",None, None,{"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    [58,"General power limit",f"{DOMAIN}_altherma4_holding_58","POW16","kW","mdi:lightning-bolt",{"min": 0, "max": 20, "step": 0.1, "unit": "kW"}],
    [76,"Room Thermostat Control Heating Setpoint Main",f"{DOMAIN}_altherma4_holding_76","TEMP16",None, None, {"min": 12, "max": 30, "step": 0.1, "unit": "°C"}],
    [77,"Room Thermostat Control Cooling Setpoint Main",f"{DOMAIN}_altherma4_holding_77","TEMP16",None, None, {"min": 12, "max": 30, "step": 0.1, "unit": "°C"}],
]

ALTHERMA_4_HOLDING_ADDITIONAL_ZONE = [
    [63,"Leaving Water Add Heating Setpoint",f"{DOMAIN}_altherma4_holding_63","INT16",None,None,{"min": 3, "max": 65, "step": 1, "unit": "°C"}],
    [64,"Leaving Water Add Cooling Setpoint",f"{DOMAIN}_altherma4_holding_64","INT16",None,None,{"min": 3, "max": 65, "step": 1, "unit": "°C"}],
    [66,"Weather Dependent Mode Add LWT Heating Setpoint Offset",f"{DOMAIN}_altherma4_holding_66","INT16",None,None,{"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    [67,"Weather Dependent Mode Add LWT Cooling Setpoint Offset",f"{DOMAIN}_altherma4_holding_67","INT16",None,None,{"min": -10, "max": 10, "step": 1, "unit": "°C"}],
    [78,"Room Thermostat Control Heating Setpoint Add",f"{DOMAIN}_altherma4_holding_78","TEMP16",None, None, {"min": 12, "max": 30, "step": 0.1, "unit": "°C"}],
    [79,"Room Thermostat Control Cooling Setpoint Add",f"{DOMAIN}_altherma4_holding_79","TEMP16",None, None, {"min": 12, "max": 30, "step": 0.1, "unit": "°C"}],
]

ALTHERMA_4_HOLDING_SELECT = [
    [3,"Operation Mode",f"{DOMAIN}_altherma4_holding_3","INT16", None,None,DAIKIN_OP_MODE_OPTIONS],
    [4,"Space Heating/Cooling On/Off",f"{DOMAIN}_altherma4_holding_4","INT16",None,None,DAIKIN_ON_OFF_OPTIONS],
    [9,"Quiet Mode Operation",f"{DOMAIN}_altherma4_holding_9","INT16",None,None,DAIKIN_ON_ONAUTO_OFF_OPTIONS],
    [13,"DHW Booster Mode On/Off (powerful)",f"{DOMAIN}_altherma4_holding_13","INT16",None,None,DAIKIN_ON_OFF_OPTIONS],
    [15,"DHW Single heat-up On/Off (manual)",f"{DOMAIN}_altherma4_holding_15","INT16",None, None,DAIKIN_ON_OFF_OPTIONS],
    [56,"Smart grid operation mode",f"{DOMAIN}_altherma4_holding_56","INT16",None,None, DAIKIN_SG_MODE_OPTIONS],
    [68,"Weather Dependent Mode heating Main",f"{DOMAIN}_altherma4_holding_68","INT16",None,None,DAIKIN_WEATHER_DEPENDEND_OPTIONS_2],
    [69,"Weather Dependent Mode cooling Main",f"{DOMAIN}_altherma4_holding_69","INT16",None,None,DAIKIN_WEATHER_DEPENDEND_OPTIONS_2],
    [74,"Thermostat request main",f"{DOMAIN}_altherma4_holding_74","INT16",None,None,DAIKIN_4_OP_MODE_OPTIONS],
    [80,"DHW Mode setting",f"{DOMAIN}_altherma4_holding_80","INT16",None,None,DAIKIN_4_DHW_MODE_OPTIONS],
]

ALTHERMA_4_HOLDING_SELECT_ADDITIONAL_ZONE = [
    [75,"Thermostat request add",f"{DOMAIN}_altherma4_holding_75","INT16",None,None,DAIKIN_4_OP_MODE_OPTIONS],
]