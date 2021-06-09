import asyncio
from functools import partial

import pytest

from genki_wave.callbacks import ButtonAndDataPrint
from genki_wave.protocols import ProtocolAsyncio
from genki_wave.asyncio_runner import _run_asyncio
from tests.constants import BLUETOOTH_DATA, SERIAL_DATA


async def producer_mock(protocol, comm, data):
    for packet in data:
        # This `sleep` is a hack to make sure consumer and producer take turns
        await asyncio.sleep(0.001)
        await protocol.data_received(packet)

    # Only the consumer can cancel, it calls `is_cancel` so this is a hack to make sure the consumer cancels
    # after this point
    comm.is_cancel = lambda x: True


@pytest.mark.parametrize("data", (BLUETOOTH_DATA, SERIAL_DATA), ids=["bluetooth", "serial"])
def test_run_asyncio(data):
    # An 'integration' test
    _run_asyncio([ButtonAndDataPrint(5)], partial(producer_mock, data=data), ProtocolAsyncio())
