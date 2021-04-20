from functools import partial

import pytest

from genki_wave.protocols import ProtocolAsyncioSerial, ProtocolAsyncioBluetooth
from genki_wave.wave_asyncio import run_asyncio
from tests.constants import BLUETOOTH_DATA, SERIAL_DATA


async def producer_mock(protocol, comm, data):
    for packet in data:
        # The number of bytes read here is an arbitrary power of 2 on the order of a size of a single package
        await protocol.data_received(packet)

    # Only the consumer can cancel, it calls `is_cancel` so this is a hack to make sure the consumer cancels
    # after this point
    comm.is_cancel = lambda x: True


@pytest.mark.parametrize(
    "protocol_factory, data", ((ProtocolAsyncioBluetooth, BLUETOOTH_DATA), (ProtocolAsyncioSerial, SERIAL_DATA))
)
def test_run_asyncio(protocol_factory, data):
    # An 'integration' test
    run_asyncio([], partial(producer_mock, data=data), protocol_factory())
