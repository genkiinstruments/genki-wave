import asyncio
import logging
import signal
import sys
from functools import partial
from typing import Union, List, Callable, Tuple

import serial
from bleak import BleakClient
from serial_asyncio import open_serial_connection

from genki_wave.callbacks import WaveCallback
from genki_wave.constants import API_CHAR_UUID, BAUDRATE
from genki_wave.data.writing import get_start_api_package
from genki_wave.protocols import ProtocolAsyncio, ProtocolThread, CommunicateCancel
from genki_wave.utils import get_serial_port, get_or_create_event_loop

logger = logging.getLogger(__name__)


def prepare_protocol_as_bleak_callback_asyncio(protocol: ProtocolAsyncio) -> Callable:
    async def _inner(sender: str, data: bytearray) -> None:
        # NOTE: `bleak` expects a function with this signature
        await protocol.data_received(data)

    return _inner


def prepare_protocol_as_bleak_callback(protocol: ProtocolThread) -> Callable:
    def _inner(sender: str, data: bytearray) -> None:
        # NOTE: `bleak` expects a function with this signature
        protocol.data_received(data)

    return _inner


def bleak_callback(protocol: ProtocolAsyncio) -> Callable:
    """Wraps our protocol as a callback with the correct signature bleak expects

    NOTE: 1) Bleak checks if a function is a co-routine so we need to wrap the class method into an `async` function
          and 2) we need to take care that `asyncio.Queue` is correctly handled so we have 2 different wrappers, one
          for a regular `queue.Queue` and one for `asyncio.Queue`.
    """
    if isinstance(protocol, ProtocolAsyncio):
        callback = prepare_protocol_as_bleak_callback_asyncio(protocol)
    elif isinstance(protocol, ProtocolThread):
        callback = prepare_protocol_as_bleak_callback(protocol)
    else:
        raise ValueError(f"Unknown protocol type {type(protocol)}")
    return callback


def make_disconnect_callback(comm: CommunicateCancel):
    def cb(client):
        if not comm.cancel:
            print(f"Client {client.address} disconnected unexpectedly, exiting")
            sys.exit(1)

    return cb


async def producer_bluetooth(
    protocol: Union[ProtocolAsyncio, ProtocolThread],
    comm: CommunicateCancel,
    ble_address: str,
) -> None:
    """Receives data from a serially connected wave ring and passes it to the `protocol`

    Args:
        protocol: An object that knows how to process the raw data sent from the Wave ring into a structured format
                  and passes it along between `producer` and `consumer`.
        comm: An object that allows `producer` and `consumer` to communicate when to cancel the process
        ble_address: Address of the bluetooth device to connect to. E.g. 'D5:73:DB:85:B4:A1'

    Note:
        The producer doesn't return a value, but the data gets added to the `protocol` that can be accessed from other
        parts of the program i.e. some `consumer`
    """
    print(f"Connecting to wave at address {ble_address}")
    callback = bleak_callback(protocol)
    async with BleakClient(ble_address, disconnected_callback=make_disconnect_callback(comm)) as client:
        await client.start_notify(API_CHAR_UUID, callback)
        await client.write_gatt_char(API_CHAR_UUID, get_start_api_package(), False)

        print("Connected to Wave")
        while True:
            # This `while` loop and `asyncio.sleep` statement is some magic that is required to continually fetch
            # the data from the bluetooth device.
            await asyncio.sleep(0.1)

            if comm.cancel:
                print("Recieved a cancel signal, stopping ble client")
                break

        await client.stop_notify(API_CHAR_UUID)


async def producer_serial(protocol: ProtocolAsyncio, comm: CommunicateCancel, serial_port: str):
    """Receives data from a serially connected wave ring and passes it to the `protocol`

    Args:
        protocol: An object that knows how to process the raw data sent from the Wave ring into a structured format
                  and passes it along between `producer` and `consumer`.
        comm: An object that allows `producer` and `consumer` to communicate when to cancel the process
        serial_port: The serial port to read from

    Note:
        The producer doesn't return a value, but the data gets added to the `protocol` that can be accessed from other
        parts of the program i.e. some `consumer`
    """
    reader, writer = await open_serial_connection(url=serial_port, baudrate=BAUDRATE, parity=serial.PARITY_EVEN)
    writer.write(get_start_api_package())
    while True:
        # The number of bytes read here is an arbitrary power of 2 on the order of a size of a single package
        try:
            packet = await asyncio.wait_for(reader.read(n=128), timeout=10)
        except asyncio.TimeoutError:
            print("Failed to read any data for 10 seconds, exiting producer")
            comm.cancel = True
            break

        await protocol.data_received(packet)

        if comm.cancel:
            print("Recieved a cancel signal, stopping serial connection")
            break


async def consumer(
    protocol: ProtocolAsyncio,
    comm: CommunicateCancel,
    callbacks: Union[List[WaveCallback], Tuple[WaveCallback]],
) -> None:
    """Consumes the data from a producer via a protocol

    Args:
        protocol: An object that knows how to process the raw data sent from the Wave ring into a structured format
                  and passes it along between `producer` and `consumer`.
        comm: An object that allows `producer` and `consumer` to communicate when to cancel the process
        callbacks: A list/tuple of callbacks that handle the data passed from the wave ring when available
    """
    while True:
        try:
            package = await asyncio.wait_for(protocol.queue.get(), timeout=10)
        except asyncio.TimeoutError:
            print("Failed to receive valid package in 10 seconds, exiting consumer")
            comm.cancel = True
            break

        if comm.is_cancel(package) or comm.cancel:
            print("Got a cancel message. Exiting consumer loop...")
            comm.cancel = True
            break

        for callback in callbacks:
            callback(package)


def make_sigint_handler(comm: CommunicateCancel):
    """Create a signal handler to cancel an asyncio loop using signals."""

    def handler(*args):
        logger.debug("SIGINT handler called in main thread")
        comm.cancel = True

    return handler


def _run_asyncio(
    callbacks: List[WaveCallback], producer: Union[producer_bluetooth, producer_serial], protocol: ProtocolAsyncio
) -> None:
    """Runs a producer and a consumer, hooking into the data using the supplied callbacks

    Args:
        callbacks: See docs for `consumer`
        producer: A callable that takes 2 arguments, a protocol and a communication object
        protocol: An object that knows how to process the raw data sent from the Wave ring into a structured format
                  and passes it along between `producer` and `consumer`.
    """
    # A singleton that sends messages about whether the data transfer has been canceled.
    comm = CommunicateCancel()
    loop = get_or_create_event_loop()
    loop.add_signal_handler(signal.SIGINT, make_sigint_handler(comm))

    # Note: The consumer and the producer send the data via the instance of `protocol`
    tasks = asyncio.gather(producer(protocol, comm), consumer(protocol, comm, callbacks))
    loop.run_until_complete(tasks)


def run_asyncio_bluetooth(callbacks: List[WaveCallback], ble_address) -> None:
    """Runs an async `consumer-producer` loop using user supplied callbacks for a bluetooth device

    Args:
        callbacks: A list/tuple of callbacks that handle the data passed from the wave ring
        ble_address: Address of the bluetooth device to connect to. E.g. 'D5:73:DB:85:B4:A1'
    """
    _run_asyncio(callbacks, partial(producer_bluetooth, ble_address=ble_address), ProtocolAsyncio())


def run_asyncio_serial(callbacks: List[WaveCallback], serial_port: str = None) -> None:
    """Runs an async `consumer-producer` loop using user supplied callbacks for a serial device

    Args:
        callbacks: A list/tuple of callbacks that handle the data passed from the wave ring
        serial_port: The serial port to read from. If `None` will try to determine it automatically based on the
                     operating system the script is running on
    """
    serial_port = get_serial_port() if serial_port is None else serial_port

    _run_asyncio(callbacks, partial(producer_serial, serial_port=serial_port), ProtocolAsyncio())
