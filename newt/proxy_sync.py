from typing import Generic
from queue import Empty
from queue import Full

from .common import (
    T,
    OptInt,
    check_closing
)
from .queue import AbstractQueue


class SyncQueueProxy(Generic[T]):
    """Create a queue object with a given maximum size.

    If maxsize is <= 0, the queue size is infinite.
    """

    def __init__(
        self,
        parent: AbstractQueue[T]
    ) -> None:
        self._parent = parent

    @property
    def maxsize(self) -> int:
        return self._parent._maxsize

    @property
    def closed(self) -> bool:
        return self._parent.closed

    @check_closing
    def task_done(self) -> None:
        """Indicate that a formerly enqueued task is complete.

        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        for every item that had been put() into the queue).

        Raises a ValueError if called more times than there were items
        placed in the queue.
        """

        with self._parent._all_tasks_done:
            unfinished = self._parent._unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self._parent._all_tasks_done.notify_all()
                self._parent._loop.call_soon_threadsafe(
                    self._parent._finished.set)
            self._parent._unfinished_tasks = unfinished

    def join(self) -> None:
        """Blocks until all items in the Queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved and all work on it is complete.

        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        with self._parent._all_tasks_done:
            while self._parent._unfinished_tasks:
                self._parent._all_tasks_done.wait()

    def qsize(self) -> int:
        """Return the approximate size of the queue (not reliable!)."""
        return self._parent._qsize()

    @property
    def unfinished_tasks(self) -> int:
        """Return the number of unfinished tasks."""
        return self._parent._unfinished_tasks

    @check_closing
    def put(
        self,
        item: T,
        block: bool = True,
        timeout: OptInt = None
    ) -> None:
        """Put an item into the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).
        """

        with self._parent._sync_not_full:
            if self._parent._maxsize > 0:
                if not block:
                    if self._parent._qsize() >= self._parent._maxsize:
                        raise Full
                elif timeout is None:
                    while self._parent._qsize() >= self._parent._maxsize:
                        self._parent._sync_not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    time = self._parent._loop.time
                    endtime = time() + timeout
                    while self._parent._qsize() >= self._parent._maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self._parent._sync_not_full.wait(remaining)
            self._parent._put_internal(item)
            self._parent._sync_not_empty.notify()
            self._parent._notify_async_not_empty(threadsafe=True)

    @check_closing
    def get(
        self,
        block: bool = True,
        timeout: OptInt = None
    ) -> T:
        """Remove and return an item from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """

        with self._parent._sync_not_empty:
            if not block:
                if not self._parent._qsize():
                    raise Empty
            elif timeout is None:
                while not self._parent._qsize():
                    self._parent._sync_not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                time = self._parent._loop.time
                endtime = time() + timeout
                while not self._parent._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self._parent._sync_not_empty.wait(remaining)
            item = self._parent._get()
            self._parent._sync_not_full.notify()
            self._parent._notify_async_not_full(threadsafe=True)
            return item
