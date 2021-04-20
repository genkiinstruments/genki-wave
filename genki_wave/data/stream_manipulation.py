import logging
import struct
from typing import Any, Union
from typing import Tuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
