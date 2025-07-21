import sys
import time
from queue import Queue
from threading import Thread

from cow_modbus.logger import logger
from cow_modbus.protocol.frame_message import Message

from cow_modbus.modbus_client import ModbusClient

def reader(m_queue: Queue) -> None :
    while True:
        m: Message =   m_queue.get(timeout=1)
        logger.info(f' is valid = {m.is_valid}; time_stamp = {m.time_stamp}')
        logger.info(f' fdx: time = {m.fdx_time}; id = {m.fdx_id}; rssi = {m.fdx_rssi}')
        logger.info(f' hdx: time = {m.hdx_time}; id = {m.hdx_id}; rssi = {m.hdx_rssi}')
        time.sleep(1)

def main():
    """setup serial port and run."""
    q=Queue(maxsize=10)

    logger.info("seting up serial port")
    client_serial = ModbusClient(connection_type="serial", m_queue=q)

    if client_serial.get_status():
        logger.info("run modbus client")
        client_serial.start()
    else:
        logger.error(" no connection ")

    th_read = Thread(target=reader, args=(q,))
    th_read.start()

    client_serial.join()
    th_read.join()

if __name__ == "__main__":
    main()