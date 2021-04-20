import asyncio
import logging
import struct
from typing import Any, Union
from typing import Tuple, Callable

from cobs import cobs
from serial.threaded import Packetizer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PacketizerSerial(Packetizer):
    """Defines how to handle the bytes from the serial connection

    Note: This is a slight abuse of subclassing since we are pulling in more functionality than is needed
    """

    def __init__(self, callback: Callable, sender="serial"):
        super().__init__()
        self._callback = callback
        self._sender = sender

    def handle_packet(self, packet: bytearray) -> None:
        try:
            data = cobs.decode(packet)
            # This way of calling the callback assumes the callback is async. Update if the callback passed
            # is not async.
            asyncio.create_task(self._callback(self._sender, data))
        except cobs.DecodeError:
            logger.debug("Got an exception decoding serial packet", exc_info=True)


def unpack_bytes(dtype: str, raw_bytes: Union[bytearray, bytes]) -> Any:
    """Unpack raw bytes based on the datatype"""
    raw_bytes = struct.unpack(dtype, raw_bytes)
    if len(raw_bytes) == 1:
        raw_bytes = raw_bytes[0]
    return raw_bytes


RAW_BYTE_SPLIT_IDX = 4


def split_byte_data(raw_bytes: Union[bytearray, bytes]) -> Tuple[int, int, int, bytearray]:
    """Split the data from the wave ring into metadata and the actual data"""
    q_type, q_id, length = unpack_bytes("<BBH", raw_bytes[:RAW_BYTE_SPLIT_IDX])
    data_raw = raw_bytes[RAW_BYTE_SPLIT_IDX:]
    return q_type, q_id, length, data_raw
