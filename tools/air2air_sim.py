from pymodbus.server import StartTcpServer
from pymodbus.pdu.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer
import logging

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

# Custom data block for logging
class CustomDataBlock(ModbusSequentialDataBlock):
    def getValues(self, address, count=1):
        log.info(f"Read operation at address {address}, count {count}")
        return super().getValues(address, count)

    def setValues(self, address, values):
        log.info(f"Write operation at address {address}, values {values}")
        super().setValues(address, values)

# Create data block for holding registers
data_block = CustomDataBlock(0x00, [0] * 2)

# Create slave context with the data block
slave_context = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0x00, [17] * 100),
    co=ModbusSequentialDataBlock(0x00, [17] * 100),
    hr=data_block,
    ir=ModbusSequentialDataBlock(0x00, [17] * 100)
)

# Create server context
context = ModbusServerContext(slaves=slave_context, single=True)

def run_server():
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = '2.5.3'

    # Start the server
    StartTcpServer(context=context, identity=identity, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_server()