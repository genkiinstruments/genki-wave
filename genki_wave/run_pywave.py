import argparse
import asyncio
import logging
import struct
from pathlib import Path
from typing import Union, Iterable, List

import serial
from bleak import BleakClient, discover
from serial_asyncio import open_serial_connection

from genki_wave.callbacks import ButtonAndDataPrint, DataCallback, CsvOutput
from genki_wave.data_organization import (
    ButtonAction,
    ButtonEvent,
    ButtonId,
    DataPackage,
    process_byte_data,
)
from genki_wave.data_stream_manipulation import PacketizerSerial
from genki_wave.utils import get_serial_port

API_CHAR_UUID = "f3402ea2-d017-11e9-bb65-2a2ae2dbcce4"
BAUDRATE = 921600


logging.basicConfig(format="%(levelname).4s:%(asctime)s [%(filename)s:%(lineno)d] - %(message)s ")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Communication:
    cancel = False
    queue = asyncio.Queue()


# A singleton that encapsulates all the communication happening between the producer and consumer and should
# be the only object that has global state
COMM = Communication()


def is_cancel(button_event: Union[ButtonEvent, DataPackage]) -> bool:
    """Checks for a hard coded cancel event"""
    if isinstance(button_event, DataPackage):
        return False
    return button_event.button_id == ButtonId.TOP and button_event.action == ButtonAction.EXTRALONG


async def read_data_callback(sender: str, data: bytearray) -> None:
    # NOTE: `bleak` expects a function with this signature
    await COMM.queue.put(data)


async def producer_bluetooth(address: str) -> None:
    async with BleakClient(address) as client:
        await client.start_notify(API_CHAR_UUID, read_data_callback)

        while True:
            # This `while` loop and this `sleep` statement is some magic that is required to continually fetch
            # the data from the bluetooth device.
            await asyncio.sleep(0.1)

            if COMM.cancel:
                print("Recieved a cancel signal, stopping ble client")
                break


async def producer_serial():
    reader, _ = await open_serial_connection(url=get_serial_port(), baudrate=BAUDRATE, parity=serial.PARITY_EVEN)
    packetizer = PacketizerSerial(read_data_callback)
    while True:
        # The number of bytes read here is an arbitrary power of 2 on the order of a size of a single package
        packet = await reader.read(n=128)
        packetizer.data_received(packet)

        if COMM.cancel:
            print("Recieved a cancel signal, stopping serial connection")
            break


async def consumer(callbacks: Iterable[DataCallback]) -> None:
    while True:
        data = await COMM.queue.get()
        try:
            package = process_byte_data(data)
        except (struct.error, ValueError):
            # Sometimes in the beginning we get garbage data
            logger.debug("Got input data error", exc_info=True)
            continue

        # TODO(robert): Allow users to inject custom actions to cancel or catch with an event from the Terminal
        if is_cancel(package):
            print("Got a cancel message. Exiting consumer loop...")
            COMM.cancel = True
            break

        for callback in callbacks:
            callback.register(package)


def run(callbacks: List[DataCallback], ble_address: str = None) -> None:
    """Runs a producer and a consumer, hooking into the data using the supplied callbacks

    Args:
        callbacks: Callbacks that handle the data from wave
        ble_address: Address of the bluetooth device to connect to. E.g. 'D5:73:DB:85:B4:A1'. If `None` it
                     connects via serial
    """
    producer = producer_bluetooth(ble_address) if ble_address is not None else producer_serial()

    # TODO(robert): Catch a keyboard interrupt and gracefully shut down. Non-trivial to implement.
    tasks = asyncio.gather(*[producer, consumer(callbacks)])
    asyncio.get_event_loop().run_until_complete(tasks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ble-address", type=str)
    parser.add_argument("--use-serial", action="store_true")
    parser.add_argument("--button", action="store_true", help="Handler that prints the button and the action")
    parser.add_argument(
        "--csv", type=str, default=None, help="Path to the output csv. If none is given no csv is written"
    )
    args = parser.parse_args()

    callbacks = []
    if args.button:
        callbacks.append(ButtonAndDataPrint(5))
    if args.csv is not None:
        callbacks.append(CsvOutput(Path(args.csv)))

    if not callbacks:
        print("Warning: no callbacks supplied, the data received won't be processed in any way")

    if args.ble_address is None and not args.use_serial:
        run_discover_bluetooth()
    else:
        ble_address = None if args.use_serial else args.ble_address
        run(callbacks, ble_address)


async def discover_bluetooth():
    print("No bluetooth address (--ble-address) supplied. Searching for bluetooth devices...")
    devices = await discover()
    wave_devices = [device for device in devices if "Wave" in device.name]
    print("Found the following devices" if wave_devices else "Found no devices")
    for device in wave_devices:
        print(f"Address: {device.address} - Name: {device.name}")


def run_discover_bluetooth():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(discover_bluetooth())


if __name__ == "__main__":
    main()
