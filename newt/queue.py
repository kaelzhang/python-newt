import asyncio
from asyncio import (
    AbstractEventLoop,
    Future
)
import threading
from abc import ABC, abstractmethod

from typing import (
    Generic,
    Any,
    Set,
    Callable,
    Optional,
    Awaitable
)

from .common import (
    T,
    lazy_property,
    has_loop,
    get_running_loop
)


class AbstractQueue(Generic[T], ABC):
    _loop_: Optional[AbstractEventLoop]
    _pending: Set[Future]

    def __init__(self, maxsize: int = 0) -> None:
        self._loop_ = None
        self._maxsize = maxsize

        self._init(maxsize)

        self._unfinished_tasks = 0

        sync_mutex = threading.Lock()
        self._sync_mutex = sync_mutex

        self._sync_not_empty = threading.Condition(sync_mutex)
        self._sync_not_full = threading.Condition(sync_mutex)
        self._all_tasks_done = threading.Condition(sync_mutex)

        try:
            async_mutex = asyncio.Lock()
        except RuntimeError as e:
            raise RuntimeError(f'''{e}

This is usually not an issue of newt.
You should make sure there is a event loop in the current thread, especially after running `asyncio.run()`.

Check https://github.com/kaelzhang/python-newt for details.''')

        self._async_mutex = async_mutex

        self._async_not_empty = asyncio.Condition(async_mutex)
        self._async_not_full = asyncio.Condition(async_mutex)
        self._finished = asyncio.Event()
        self._finished.set()

        self._closing = False
        self._pending = set()

    @lazy_property
    def _loop(self) -> asyncio.AbstractEventLoop:
        return get_running_loop()

    def close(self) -> None:
        with self._sync_mutex:
            self._closing = True
            for fut in self._pending:
                fut.cancel()

    async def wait_closed(self) -> None:
        # should be called from loop after close().
        # Nobody should put/get at this point,
        # so lock acquiring is not required
        if not self._closing:
            raise RuntimeError("waiting for non-closed queue")
        # give execution chances for the task-done callbacks
        # of async tasks created inside
        # _notify_async_not_empty, _notify_async_not_full
        # methods.
        await asyncio.sleep(0)
        if not self._pending:
            return
        await asyncio.wait(self._pending)

    @property
    def closed(self) -> bool:
        return self._closing and not self._pending

    @property
    def maxsize(self) -> int:
        return self._maxsize

    def _put_internal(self, item: T) -> None:
        self._put(item)
        self._unfinished_tasks += 1
        self._finished.clear()

    # Override these methods to implement other queue organizations
    # --------------------------------------------------------------

    # (e.g. stack or priority queue).
    # These will only be called with appropriate locks held

    @abstractmethod
    def _init(self, maxsize: int) -> None:
        ...

    @abstractmethod
    def _qsize(self) -> int:
        ...

    @abstractmethod
    def _put(self, item: T) -> None:
        """Put a new item in the queue
        """
        ...

    @abstractmethod
    def _get(self) -> T:
        """Get an item from the queue
        """
        ...

    # Utilities for async queue to notify sync queue
    # --------------------------------------------------------------

    # This method is always called in a event loop,
    # so we do not need to check loop initialization
    def _notify_sync_not_empty(self) -> None:
        def f() -> None:
            with self._sync_mutex:
                self._sync_not_empty.notify()

        self._loop.run_in_executor(None, f)

    def _notify_sync_not_full(self) -> None:
        def f() -> None:
            with self._sync_mutex:
                self._sync_not_full.notify()

        fut = self._loop.run_in_executor(None, f)
        fut.add_done_callback(self._pending.discard)  # type: ignore
        self._pending.add(fut)  # type: ignore

    # Utilities for sync queue to notify async queue
    # --------------------------------------------------------------

    # If loop is not initialized, then do nothing
    @has_loop
    def _notify_async_not_empty(self, *, threadsafe: bool) -> None:
        async def f() -> None:
            async with self._async_mutex:
                self._async_not_empty.notify()

        def task_maker() -> None:
            task = self._loop.create_task(f())
            task.add_done_callback(self._pending.discard)
            self._pending.add(task)

        if threadsafe:
            self._call_soon_threadsafe(task_maker)
        else:
            self._call_soon(task_maker)

    @has_loop
    def _notify_async_not_full(self, *, threadsafe: bool) -> None:
        async def f() -> None:
            async with self._async_mutex:
                self._async_not_full.notify()

        def task_maker() -> None:
            task = self._loop.create_task(f())
            task.add_done_callback(self._pending.discard)
            self._pending.add(task)

        if threadsafe:
            self._call_soon_threadsafe(task_maker)
        else:
            self._call_soon(task_maker)

    def _call_soon_threadsafe(
        self,
        callback: Callable[..., None],
        *args: Any
    ) -> None:
        try:
            self._loop.call_soon_threadsafe(callback, *args)
        except RuntimeError:
            pass

    def _call_soon(
        self,
        callback: Callable[..., None],
        *args: Any
    ) -> None:
        if not self._loop.is_closed():
            self._loop.call_soon(callback, *args)
