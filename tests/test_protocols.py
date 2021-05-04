import pytest

from genki_wave.protocols import ProtocolAsyncio, ProtocolThread
from tests.constants import DATA, EXPECTED


@pytest.mark.parametrize("data, expected, protocol_factory", ((DATA, EXPECTED, ProtocolThread),))
def test_protocol_thread_serial(data, expected, protocol_factory):
    protocol = protocol_factory()
    for input_raw in data:
        protocol.data_received(input_raw)
    actual = protocol.queue.pop_all()

    # pytest provides a much nicer output if we loop and compare each individually
    for i, j in zip(actual, expected):
        assert i == j

    # Still good to finally make sure everything matches (number of elements etc)
    assert actual == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("data, expected, protocol_factory", ((DATA, EXPECTED, ProtocolAsyncio),))
async def test_protocol_asyncio_serial(data, expected, protocol_factory):
    protocol = protocol_factory()
    for input_raw in data:
        await protocol.data_received(input_raw)

    actual = []
    for i in range(len(expected)):
        actual.append(await protocol.queue.get())

    # pytest provides a much nicer output if we loop and compare each individually
    for i, j in zip(actual, expected):
        assert i == j

    # Still good to finally make sure everything matches (number of elements etc)
    assert actual == expected
