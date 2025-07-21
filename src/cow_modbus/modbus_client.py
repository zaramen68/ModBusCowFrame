
import sys
import time
import pymodbus.client as modbusClient
from pymodbus import ModbusException, FramerType
from serial import SerialException

from dataclasses import dataclass
import bitarray
from bitarray.util import  ba2int

from cow_modbus.logger import logger

MAX_CONNECT = 4

""" Структура сообщения от рамки, заполняется при каждом опросе рамки"""
@dataclass
class Message:
    """Время *20 ms прошедшее с последнего срабатывания метки fdx. макимальное значение 255"""
    fdx_time: int | None = None
    """id fdx метки"""
    fdx_id: int | None = None
    """rssi fdx метки"""
    fdx_rssi: int | None = None
    """Время *20 ms прошедшее с последнего срабатывания метки hdx. макимальное значение 255"""
    hdx_time: int | None = None
    """id hdx метки"""
    hdx_id: int | None = None
    """rssi hdx метки"""
    hdx_rssi: int | None = None
    """Состояние ответа. Если ошибка -  false"""
    is_valid: bool = False
    """Текст последней ошибки"""
    last_error: str | None = None


class ModbusClient:
    client: modbusClient.ModbusBaseSyncClient | None = None
    message: Message
    connection_type: str
    framer: FramerType
    host: str | None
    port: int | str
    slave: int
    baudrate: int | None
    parity: str
    stopbits: int
    bytesize: int
    timeout: int 
    status: bool
    reconnect_num: int


    def __init__(self, connection_type, 
                 host="127.0.0.1", 
                 framer=FramerType.RTU, 
                 port="COM6", 
                 slave=2, 
                 baudrate=19200, 
                 parity="E", 
                 bytesize=8, 
                 stopbits=1, 
                 timeout=5) -> None:
        self.connection_type = connection_type
        self.framer = framer
        self.host = host
        self.port = port
        self.slave = slave
        self.baudrate = baudrate
        self.parity = parity
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.timeout = timeout
        self.message = Message()
        self.status = False
        self.reconnect_num = 0
    
        if connection_type == "tcp":
            self.client = modbusClient.ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout,
                #    retries=3,
                # TCP setup parameters
                #    source_address=("localhost", 0),
            )
        elif connection_type == "serial":  # pragma: no cover
            self.client = modbusClient.ModbusSerialClient(
                port=self.port,         # "COM6"
                # Common optional parameters:
                framer=self.framer,     # FramerType.RTU
                timeout=self.timeout,   # 3 sec
                #    retries=3,
                # Serial setup parameters
                baudrate=self.baudrate, # 19200
                bytesize=self.bytesize, # 8
                parity=self.parity,     # "E"
                stopbits=self.stopbits, # 1
                #    handle_local_echo=False,
            )
        else:
            self.status = False
            logger.error("Не подходящий тип соединения")
            raise Exception("Не подходящий тип соединения")
        
        try:
            self.status = self.client.connect()
            if not self.status:
                logger.error(" no connection ")
            else:
                logger.info(" client connected")

        except SerialException as ex:
            self.status = False
            logger.error(ex)
            self.message = Message(is_valid=False, last_error=ex)
        except Exception as ex:
            logger.error(ex)
            self.message = Message(is_valid=False, last_error=ex)
            print(ex)

    def __del__(self) -> None:
        self.client.close()

    def reconnect_client(self) -> None:
        logger.info(" reconnecting ")

        for i in range(MAX_CONNECT):
            try:
                self.reconnect_num = i+1
                self.status = self.client.connect() 
                if self.status:
                    break
                else:
                    logger.error(" no connection ")

            except SerialException as ex:
                self.status = False
                logger.error(ex)
                self.message = Message(is_valid=False, last_error=ex)

            except Exception as ex:
                logger.error(ex)
                self.message = Message(is_valid=False, last_error=ex)
                print(ex)

            time.sleep(3)

    def get_status(self) -> bool:
        return self.status
    
    def get_message(self) -> Message:
        return self.message


    def run(self) -> None:
        while(self.reconnect_num < MAX_CONNECT):

            if not self.status:
                self.reconnect_client()

            try: 
                rr = self.client.read_holding_registers(address=22, count=10, slave=2)    
                assert not rr.isError()  # test that call was OK
                assert len(rr.registers) == 10
                fdx_ba_time = bitarray.bitarray(rr.registers[5].to_bytes(2))[:8]
                fdx_time_20ms = ba2int(fdx_ba_time)

                fdx_ba_rssi = bitarray.bitarray(rr.registers[5].to_bytes(2))[8:]
                fdx_rssi = ba2int(fdx_ba_rssi)

                # ba_b = bitarray.bitarray(rr.registers[9].to_bytes(2))[:8]
                fdx_id_ba =  bitarray.bitarray(rr.registers[7].to_bytes(2))
                fdx_id_ba.extend(bitarray.bitarray(rr.registers[8].to_bytes(2))) 
                fdx_id_ba.extend( bitarray.bitarray(rr.registers[9].to_bytes(2))[:8])
                fdx_id = ba2int(fdx_id_ba)

                hdx_ba_time = bitarray.bitarray(rr.registers[0].to_bytes(2))[:8]
                hdx_time_20ms = ba2int(hdx_ba_time)

                hdx_ba_rssi = bitarray.bitarray(rr.registers[0].to_bytes(2))[8:]
                hdx_rssi = ba2int(hdx_ba_rssi)

                # ba_b = bitarray.bitarray(rr.registers[4].to_bytes(2))[:8]
                hdx_id_ba =  bitarray.bitarray(rr.registers[2].to_bytes(2))
                hdx_id_ba.extend(bitarray.bitarray(rr.registers[3].to_bytes(2))) 
                hdx_id_ba.extend( bitarray.bitarray(rr.registers[4].to_bytes(2))[:8])
                hdx_id = ba2int(hdx_id_ba)

                self.message = Message(fdx_time=fdx_time_20ms, fdx_id=fdx_id, fdx_rssi=fdx_rssi, 
                                       hdx_time=hdx_time_20ms, hdx_id=hdx_id, hdx_rssi=hdx_rssi,
                                       is_valid=True)
                
                logger.info(f' fdx: time = {fdx_time_20ms}; id = {fdx_id}; rssi = {fdx_rssi}')
                logger.info(f' hdx: time = {hdx_time_20ms}; id = {hdx_id}; rssi = {hdx_rssi}')

            except SerialException as ex:
                self.status = False
                logger.error(ex)
                self.message = Message(is_valid=False, last_error=ex)
                # print(ex)

            except Exception as ex:
                logger.error(ex)
                self.message = Message(is_valid=False, last_error=ex)
                # print(ex)

            time.sleep(0.5)

        sys.exit(-1)
            
                