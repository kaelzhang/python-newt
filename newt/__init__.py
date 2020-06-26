from heapq import heappop, heappush
from typing import (
    List,
    Deque
)

from collections import deque

from .common import (
    T,
    lazy_property
)
from .queue import AbstractQueue
from .proxy_sync import SyncQueueProxy
from .proxy_async import AsyncQueueProxy

__all__ = (
    'Queue',
    'PriorityQueue',
    'LifoQueue'
)


# The first beta version
__version__ = '0.1.0'


class _AbstractQueue(AbstractQueue[T]):
    @lazy_property
    def sync_queue(self) -> SyncQueueProxy[T]:
        return SyncQueueProxy(self)

    @lazy_property
    def async_queue(self) -> AsyncQueueProxy[T]:
        return AsyncQueueProxy(self)


class Queue(_AbstractQueue[T]):
    _queue: Deque

    def _init(self, maxsize: int) -> None:
        self._queue = deque()

    def _qsize(self) -> int:
        return len(self._queue)

    # Put a new item in the queue
    def _put(self, item: T) -> None:
        self._queue.append(item)

    # Get an item from the queue
    def _get(self) -> T:
        return self._queue.popleft()


class PriorityQueue(_AbstractQueue[T]):
    """Variant of Queue that retrieves open entries in priority order
    (lowest first).

    Entries are typically tuples of the form: (priority number, data).
    """

    _heap_queue: List[T]

    def _init(self, maxsize: int) -> None:
        self._heap_queue = []

    def _qsize(self) -> int:
        return len(self._heap_queue)

    def _put(self, item: T) -> None:
        heappush(self._heap_queue, item)

    def _get(self) -> T:
        return heappop(self._heap_queue)


class LifoQueue(_AbstractQueue[T]):
    """Variant of Queue that retrieves most recently added entries first.
    """

    _queue: Deque

    def _init(self, maxsize: int) -> None:
        self._queue = deque()

    def _qsize(self) -> int:
        return len(self._queue)

    def _put(self, item: T) -> None:
        self._queue.append(item)

    def _get(self) -> T:
        return self._queue.pop()
