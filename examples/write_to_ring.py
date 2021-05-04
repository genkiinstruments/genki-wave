import asyncio
import time

import serial
from bleak import BleakClient
from serial_asyncio import open_serial_connection

from genki_wave.asyncio import bleak_callback
from genki_wave.constants import BAUDRATE
from genki_wave.data.writing import get_start_api_package
from genki_wave.protocols import ProtocolAsyncioSerial
from genki_wave.utils import get_serial_port


def my_callback(data_received):
    def _inner(sender, data):
        data_received.append(data)

    return _inner


async def producer_bluetooth(ble_address: str, api_char: str) -> None:
    protocol = ProtocolAsyncioSerial()
    callback = bleak_callback(protocol)
    async with BleakClient(ble_address) as client:
        print("Start notify")
        await client.start_notify(api_char, callback)
        print("Write gatt")
        await client.write_gatt_char(api_char, get_start_api_package(), False)

        print("Start loop")
        for i in range(100):
            # This `while` loop and `asyncio.sleep` statement is some magic that is required to continually fetch
            # the data from the bluetooth device.
            if i % 100 == 0:
                print(i)
            await asyncio.sleep(0.01)

        time.sleep(1)
        await asyncio.sleep(1)
        print("Done")
        for _ in range(100):
            print(await protocol.queue.get())
        await client.stop_notify(api_char)


async def run(_protocol: ProtocolAsyncioSerial, _serial_port: str):
    print("Trying to open a serial")
    reader, writer = await open_serial_connection(url=_serial_port, baudrate=BAUDRATE, parity=serial.PARITY_EVEN)
    print("Trying to write")
    writer.write(get_start_api_package())
    print("Trying to read")
    while True:
        packet = await reader.read(n=128)
        print(packet)
        await protocol.data_received(packet)


async def fetch(_protocol: ProtocolAsyncioSerial):
    print("Fetcher")
    while True:
        val = await _protocol.queue.get()
        print(val)


new_version = True
use_serial = False

API_CHAR_UUID = "65e92bb1-8dfb-11ea-bc55-0242ac130003" if new_version else "f3402ea2-d017-11e9-bb65-2a2ae2dbcce4"
BLE_ADDRESS = "D3:4B:D9:61:6F:A1" if new_version else "EE:16:6F:7D:70:2A"
#BLE_ADDRESS = "D8:DF:3D:59:E8:F9"


import logging
logging.basicConfig(level=logging.DEBUG)


if use_serial:
    serial_port = get_serial_port()
    protocol = ProtocolAsyncioSerial()
    tasks = asyncio.gather(run(protocol, serial_port), fetch(protocol))
else:
    tasks = asyncio.gather(producer_bluetooth(BLE_ADDRESS, API_CHAR_UUID))

asyncio.get_event_loop().run_until_complete(tasks)
