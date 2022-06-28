import abc
import asyncio
import logging
import struct
from queue import Queue
from typing import Callable, List, Optional, Union

from bleak import BleakClient
from cobs import cobs
from serial.threaded import Packetizer

from genki_wave.constants import API_CHAR_UUID
from genki_wave.data import ButtonAction, ButtonEvent, ButtonId, DataPackage
from genki_wave.data.organization import process_byte_data
from genki_wave.data.structures import QueueWithPop
from genki_wave.data.writing import get_start_api_package
from genki_wave.utils import get_or_create_event_loop

logger = logging.getLogger(__name__)


class CommunicateCancel:
    """
    Class that handles how to cancel asyncio loops with a button press and how to communicate it. Usually defined as
    a global and sends messages to each part of the script
    """

    cancel = False
    is_connected = False

    @staticmethod
    def is_cancel(button_event: Union[ButtonEvent, DataPackage]) -> bool:
        """Checks for a hard coded cancel event"""
        if isinstance(button_event, DataPackage):
            return False
        return button_event.button_id == ButtonId.TOP and button_event.action == ButtonAction.EXTRALONG


class ProtocolAbc(abc.ABC):
    """A protocol decodes raw data and connects producers and consumers af data from the input device

    It's a common abstraction that might be slightly abused here.

    A protocol:
        1) It defines methods that take the raw data-stream and transform it into a useful representation
        2) Since the methods that process the data-stream usually have to register the transformed data in
           a queue, these protocols defined here also have an instance of a Queue and allow consumer and
           producer, or different threads, to communicate.

    The flow of data is `data_received` -> `handle_packet`, see docstrings for explanations
    """

    @abc.abstractmethod
    def data_received(self, data: Union[bytearray, bytes]) -> None:
        """Gets the raw stream into a buffer and splits it up if needed"""
        pass

    @abc.abstractmethod
    def handle_packet(self, packet: Union[bytearray, bytes]) -> None:
        """Decodes and transforms the data into a useful representation and registers it in a queue"""
        pass

    @property
    @abc.abstractmethod
    def queue(self) -> Union[asyncio.Queue, Queue]:
        """The 'global' queue that is used to communicate between producer/consumer or between threads"""
        pass


def _handle_packet(packet: Union[bytearray, bytes]) -> Optional[Union[ButtonEvent, DataPackage]]:
    try:
        data = cobs.decode(packet)
        data = process_byte_data(data)
    except cobs.DecodeError:
        logger.debug("Got an exception decoding serial packet", exc_info=True)
        return None
    except (struct.error, ValueError):
        # Sometimes in the beginning we get garbage data
        logger.debug("Got input data error", exc_info=True)
        return None

    return data


class ProtocolAsyncio(ProtocolAbc, Packetizer):
    """Defines how to handle the bytes from the serial connection

    Note: This is a slight abuse of subclassing since we are pulling in more functionality than is needed
    """

    def __init__(self):
        super().__init__()
        get_or_create_event_loop()
        self._queue = asyncio.Queue()

    async def data_received(self, data: Union[bytearray, bytes]) -> None:
        """Buffer received data, find TERMINATOR, call handle_packet"""
        self.buffer.extend(data)
        while self.TERMINATOR in self.buffer:
            packet, self.buffer = self.buffer.split(self.TERMINATOR, 1)
            await self.handle_packet(packet)

    async def handle_packet(self, packet: Union[bytearray, bytes]) -> None:
        data = _handle_packet(packet)
        if data is None:
            return
        await self.queue.put(data)

    @property
    def queue(self) -> asyncio.Queue:
        return self._queue


class ProtocolThread(ProtocolAbc, Packetizer):
    def __init__(self):
        super().__init__()
        self._queue = QueueWithPop()

    def data_received(self, data: Union[bytearray, bytes]) -> None:
        """Buffer received data, find TERMINATOR, call handle_packet"""
        self.buffer.extend(data)
        while self.TERMINATOR in self.buffer:
            packet, self.buffer = self.buffer.split(self.TERMINATOR, 1)
            self.handle_packet(packet)

    def handle_packet(self, packet: Union[bytearray, bytes]) -> None:
        data = _handle_packet(packet)
        if data is None:
            return
        self.queue.put(data)

    @property
    def queue(self) -> Queue:
        return self._queue


def prepare_protocol_as_bleak_callback_asyncio(protocol: ProtocolAsyncio) -> Callable:
    async def _inner(sender: str, data: bytearray) -> None:
        # NOTE: `bleak` expects a function with this signature
        await protocol.data_received(data)

    return _inner


async def bluetooth_task(ble_address: str, comm: CommunicateCancel, callbacks: List[Callable]) -> None:
    protocol = ProtocolAsyncio()
    callback = prepare_protocol_as_bleak_callback_asyncio(protocol)
    print(f"Connecting to wave at address {ble_address}")
    async with BleakClient(ble_address) as client:
        await client.start_notify(API_CHAR_UUID, callback)
        await client.write_gatt_char(API_CHAR_UUID, get_start_api_package(), False)

        print("Connected to Wave")
        comm.is_connected = True
        while True:
            package = await protocol.queue.get()

            if comm.is_cancel(package) or comm.cancel:
                print("Got a cancel message, exiting.")
                comm.cancel = True
                break

            for callback in callbacks:
                callback(package)

        await client.stop_notify(API_CHAR_UUID)
