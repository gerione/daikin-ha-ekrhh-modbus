# Daikin EKRHH Modbus for Home Assistant
[![GitHub Release](https://img.shields.io/github/v/release/gerione/daikin-ha-ekrhh-modbus)](https://github.com/gerione/daikin-ha-ekrhh-modbus/releases)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Integration for the Daikin Home Hub (modbus gateway) for Altherma 3 and Air 2 Air heat pumps. 

The newest release also adds experimental support for the Altherma 4 heatpump. 

The latest information about the gateway can be found here: [EKRHH Daikin Homepage](https://www.daikin.at/de_at/produktsuche/product.html/EKRHH.html#Installer-reference-guide-documents-b7f056ea11)
In this document also the modbus registers can be found. 
## Features
- **Altherma 3 and 4 support ** 
- **Real-time monitoring** of heat pump status, temperatures, and energy usage.
- **Climate control** (set target temperatures, modes, and fan speeds).
- **Energy tracking** (power consumption, efficiency metrics).
- **Modbus TCP/RTU** support.

## Installation
### HACS
1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant.
2. Add this repository as a **custom repository** in HACS:
   - Go to **HACS > Integrations > + (Add) > Custom Repository**.
   - Enter `https://github.com/gerione/daikin-ha-ekrhh-modbus` and select **Integration**.
3. Click **Install** and restart Home Assistant.

### Manually
You can install the code manually by copying the Daikin_EKRHH_Modbus folder and all of its contents into your Home Assistant's custom_components folder. 

## Daikin Altherma 3 settings
### Working modes
EKRHH supports 3 modes. 
1. Use case 1 – PV self-consumption for Daikin Altherma
2. Use case 2 - PV self-consumption for Multi+(DHW)
3. Use case 3 - Modbus RTU/IP for Daikin Altherma
4. Use case 4 - Modbus TCP/IP or RTU for air-to-air heat pump
   
The integration only works with use case 3 and 4.

### Enabling Modbus TCP on Daikin Altherma 3
The following can be done in the ONECTA app:
▪ Add / remove the Daikin HomeHub to your home,
▪ Select a use case,
▪ Change the Modbus settings (for use case 3 and 4),

Modbus settings
Modbus protocol: RTU or TCP/IP (default)
In case of TCP/IP protocol, set the following:
▪ Encryption: none (default) or TLS (not tested)

You have to set it to TCP/IP for the integration to work. 

Select the right port at configuration: 
▪ No encryption: 502
▪ TLS encryption: 802

On the unit it is possible to set the smart grid setting via HomeHub (if desired).

## Special thanks

Special thanks to [Solaredge Modbus](https://github.com/binsentsu/home-assistant-solaredge-modbus) and [Daikin Onecta](https://github.com/jwillemsen/daikin_onecta). 
A lot of this code is based off those repositories.
