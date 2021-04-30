import asyncio
import time

from bleak import BleakClient
import struct

import serial
from cobs import cobs
from serial_asyncio import open_serial_connection

from genki_wave.asyncio import bleak_callback
from genki_wave.constants import API_CHAR_UUID, BAUDRATE
from genki_wave.data.organization import DeviceMode, PackageId, PackageMetadata, PackageType
from genki_wave.protocols import ProtocolAsyncioBluetooth, ProtocolAsyncioSerial
from genki_wave.utils import get_serial_port


def pad_with_zero_byte(b: bytes) -> bytes:
    return b + struct.pack("<B", 0)


def create_package_to_write(p: PackageMetadata, data: bytes) -> bytes:
    # TODO(robert): `data` should probably be a class that has a `to_bytes` method
    if p.payload_size != len(data):
        raise ValueError(
            f"Expected payload_size and the size of the data to match. Got {p.payload_size} and {len(data)}"
        )
    b_tot = p.to_bytes() + data
    b_encoded = cobs.encode(b_tot)
    b_buffer = pad_with_zero_byte(b_encoded)
    return b_buffer


def start_api_package():
    return create_package_to_write(
        PackageMetadata(type=PackageType.REQUEST, id=PackageId.DEVICE_MODE, payload_size=1),
        struct.pack("<B", DeviceMode.API.value),
    )


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
        await client.write_gatt_char(api_char, start_api_package(), False)

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
    writer.write(start_api_package())
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
