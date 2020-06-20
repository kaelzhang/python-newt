import asyncio
import threading

from collections import deque

from typing import (
    Generic,
    Any,
    Deque,
    Set,
    Callable,
    Optional
)

from .common import (
    T,
    lazy_property,
    has_loop,
    get_running_loop
)


class AbstractQueue(Generic[T]):
    __loop: Optional[asyncio.AbstractEventLoop]

    def __init__(self, maxsize: int = 0) -> None:
        self.__loop = None
        self._maxsize = maxsize

        self._init(maxsize)

        self._unfinished_tasks = 0

        self._sync_mutex = threading.Lock()
        self._sync_not_empty = threading.Condition(self._sync_mutex)
        self._sync_not_full = threading.Condition(self._sync_mutex)
        self._all_tasks_done = threading.Condition(self._sync_mutex)

        self._async_mutex = asyncio.Lock()
        self._async_not_empty = asyncio.Condition(self._async_mutex)
        self._async_not_full = asyncio.Condition(self._async_mutex)
        self._finished = asyncio.Event()
        self._finished.set()

        self._closing = False
        self._pending = set()  # type: Set[asyncio.Future[Any]]

    @lazy_property
    def _loop(self) -> asyncio.AbstractEventLoop:
        return get_running_loop()

    def _call_soon_threadsafe(
        self,
        callback: Callable[..., None],
        *args: Any
    ) -> None:
        try:
            self._loop.call_soon_threadsafe(callback, *args)
        except RuntimeError:
            # swallowing agreed in #2
            pass

    def _call_soon(self, callback: Callable[..., None], *args: Any) -> None:
        if not self._loop.is_closed():
            self._loop.call_soon(callback, *args)

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
            raise RuntimeError("Waiting for non-closed queue")
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

    # Override these methods to implement other queue organizations
    # (e.g. stack or priority queue).
    # These will only be called with appropriate locks held

    def _init(self, maxsize: int) -> None:
        self._queue = deque()  # type: Deque[T]

    def _qsize(self) -> int:
        return len(self._queue)

    # Put a new item in the queue
    def _put(self, item: T) -> None:
        self._queue.append(item)

    # Get an item from the queue
    def _get(self) -> T:
        return self._queue.popleft()

    def _put_internal(self, item: T) -> None:
        self._put(item)
        self._unfinished_tasks += 1
        self._finished.clear()

    # This method is always called in a event loop
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