from typing import (
    TypeVar,
    Optional,
    Callable
)
import asyncio


T = TypeVar('T')
OptInt = Optional[int]


def lazy_property(fn: Callable[..., T]):
    """Lazily initialize a property
    """
    def helper(self, *args, **kwargs) -> T:
        name = fn.__name__
        key = f'_{name}'

        value = getattr(self, key, None)

        if value is None:
            value = fn(self, *args, **kwargs)
            setattr(self, key, value)

        return value

    return property(helper)


def has_loop(fn):
    """
    Only execute fn when there is a loop
    """
    def helper(self, *args, **kwargs) -> None:
        if self.__loop is None:
            return

        fn(self, *args, **kwargs)

    return helper


def check_closing(fn: Callable[..., T]):
    def helper(self, *args, **kwargs) -> T:
        if self._parent._closing:
            raise RuntimeError('modification of closed queue is forbidden')

        return fn(self, *args, **kwargs)

    return helper


if getattr(asyncio, 'get_running_loop', None) is None:
    def _get_running_loop() -> asyncio.AbstractEventLoop:
        loop = asyncio.get_event_loop()

        if not loop.is_running():
            raise RuntimeError('no running event loop')

        return loop

    get_running_loop = _get_running_loop

else:
    get_running_loop = asyncio.get_running_loop
