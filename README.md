# Daikin EKRHH Modbus for Home Assistant
Version 0.1 of the integration. 
It is usable, but additional zone could not be tested so far. 
The latest information can be found: [EKRHH Daikin Homepage](https://www.daikin.at/de_at/produktsuche/product.html/EKRHH.html#Installer-reference-guide-documents-b7f056ea11)
In this document also the modbus registers can be found. 

## Installation
Do not use it as of now. This is just a first working version, that reads all the sensors

### Working modes
EKRHH supports 3 modes. 
1. Use case 1 – PV self-consumption for Daikin Altherma
2. Use case 2 - PV self-consumption for Multi+(DHW)
3. Use case 3 - Modbus RTU/IP for Daikin Altherma
4. Use case 4 - Modbus TCP/IP or RTU for air-to-air heat pump
   
The integration only works with use case 3 and 4.

### Enabling Modbus TCP on Daikin Altherma
The following can be done in the ONECTA app:
▪ Add / remove the Daikin HomeHub to your home,
▪ Select a use case,
▪ Change the Modbus settings (for use case 3 and 4),

Modbus settings
Modbus protocol: RTU or TCP/IP (default)
In case of TCP/IP protocol, set the following:
▪ Encryption: none (default) or TLS

You have to set it to TCP/IP for the integration to work. 

Select the right port at configuration: 
▪ No encryption: 502
▪ TLS encryption: 802

On the unit it is possible to set the smart grid setting via HomeHub (if desired)

## Special thanks

Special thanks to [Solaredge Modbus](https://github.com/binsentsu/home-assistant-solaredge-modbus) and [Daikin Onecta](https://github.com/jwillemsen/daikin_onecta). 
A lot of this code is based off those repositories.
