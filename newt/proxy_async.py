from typing import Generic
from asyncio import QueueEmpty
from asyncio import QueueFull

from .common import (
    T,
    check_closing
)
from .queue import AbstractQueue


class AsyncQueueProxy(Generic[T]):
    """Create a queue object with a given maximum size.

    If maxsize is <= 0, the queue size is infinite.
    """

    def __init__(
        self,
        parent: AbstractQueue[T]
    ) -> None:
        self._parent = parent

    @property
    def closed(self) -> bool:
        return self._parent.closed

    def qsize(self) -> int:
        """Number of items in the queue."""
        return self._parent._qsize()

    @property
    def unfinished_tasks(self) -> int:
        """Return the number of unfinished tasks."""
        return self._parent._unfinished_tasks

    @property
    def maxsize(self) -> int:
        """Number of items allowed in the queue."""
        return self._parent._maxsize

    @check_closing
    async def put(self, item: T) -> None:
        """Put an item into the queue.

        Put an item into the queue. If the queue is full, wait until a free
        slot is available before adding item.

        This method is a coroutine.
        """

        async with self._parent._async_not_full:
            self._parent._sync_mutex.acquire()
            locked = True
            try:
                if self._parent._maxsize > 0:
                    do_wait = True
                    while do_wait:
                        do_wait = (
                            self._parent._qsize() >= self._parent._maxsize
                        )
                        if do_wait:
                            locked = False
                            self._parent._sync_mutex.release()
                            await self._parent._async_not_full.wait()
                            self._parent._sync_mutex.acquire()
                            locked = True

                self._parent._put_internal(item)
                self._parent._async_not_empty.notify()
                self._parent._notify_sync_not_empty()
            finally:
                if locked:
                    self._parent._sync_mutex.release()

    @check_closing
    def put_nowait(self, item: T) -> None:
        """Put an item into the queue without blocking.

        If no free slot is immediately available, raise QueueFull.
        """

        with self._parent._sync_mutex:
            if self._parent._maxsize > 0:
                if self._parent._qsize() >= self._parent._maxsize:
                    raise QueueFull

            self._parent._put_internal(item)
            self._parent._notify_async_not_empty(threadsafe=False)
            self._parent._notify_sync_not_empty()

    @check_closing
    async def get(self) -> T:
        """Remove and return an item from the queue.

        If queue is empty, wait until an item is available.

        This method is a coroutine.
        """

        async with self._parent._async_not_empty:
            self._parent._sync_mutex.acquire()
            locked = True
            try:
                do_wait = True
                while do_wait:
                    do_wait = self._parent._qsize() == 0

                    if do_wait:
                        locked = False
                        self._parent._sync_mutex.release()
                        await self._parent._async_not_empty.wait()
                        self._parent._sync_mutex.acquire()
                        locked = True

                item = self._parent._get()
                self._parent._async_not_full.notify()
                self._parent._notify_sync_not_full()
                return item
            finally:
                if locked:
                    self._parent._sync_mutex.release()

    def get_nowait(self) -> T:
        """Remove and return an item from the queue.

        Return an item if one is immediately available, else raise QueueEmpty.
        """

        with self._parent._sync_mutex:
            if self._parent._qsize() == 0:
                raise QueueEmpty

            item = self._parent._get()
            self._parent._notify_async_not_full(threadsafe=False)
            self._parent._notify_sync_not_full()
            return item

    @check_closing
    def task_done(self) -> None:
        """Indicate that a formerly enqueued task is complete.

        Used by queue consumers. For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items have
        been processed (meaning that a task_done() call was received for every
        item that had been put() into the queue).

        Raises ValueError if called more times than there were items placed in
        the queue.
        """

        with self._parent._all_tasks_done:
            if self._parent._unfinished_tasks <= 0:
                raise ValueError('task_done() called too many times')
            self._parent._unfinished_tasks -= 1
            if self._parent._unfinished_tasks == 0:
                self._parent._finished.set()
                self._parent._all_tasks_done.notify_all()

    async def join(self) -> None:
        """Block until all items in the queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer calls task_done() to
        indicate that the item was retrieved and all work on it is complete.
        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        while True:
            with self._parent._sync_mutex:
                if self._parent._unfinished_tasks == 0:
                    break
            await self._parent._finished.wait()
