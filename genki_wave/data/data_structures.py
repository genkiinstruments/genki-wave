from queue import Queue
from typing import Optional, Any


class QueueWithPop(Queue):
    """A Queue that implements convenience methods"""

    def __init__(self, maxsize=0):
        super().__init__(maxsize=maxsize)

    def pop(self) -> Optional[Any]:
        """'safe' `pop`. Returns `None` if the queue is empty"""
        if self.qsize() != 0:
            val = self.get()
        else:
            val = None

        return val

    def pop_all(self):
        """Fetches everything on the Queue"""
        results = []
        while self.qsize() > 0:
            results.append(self.pop())
        return results
