import sys
# import logging

from cow_modbus.logger import logger

from cow_modbus.modbus_client import ModbusClient

def main():
    """setup serial port and run."""

    logger.info("seting up serial port")
    client_serial = ModbusClient(connection_type="serial")

    if client_serial.get_status():
        logger.info("run modbus client")
        client_serial.run()
    else:
        logger.error(" no connection ")


if __name__ == "__main__":
    main()