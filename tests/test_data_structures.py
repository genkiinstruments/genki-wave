import pytest

from genki_wave.data.data_structures import QueueWithPop


@pytest.mark.parametrize("insert", [[1, 2, 3], []])
def test_queue_with_pop_pop_all(insert):
    q = QueueWithPop()
    for val in insert:
        q.put(val)

    assert q.pop_all() == insert


def test_queue_with_pop_none():
    q = QueueWithPop()
    assert q.pop() is None
