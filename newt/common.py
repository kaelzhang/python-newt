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

    name = fn.__name__
    key = f'{name}_'

    def helper(self, *args, **kwargs) -> T:
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
        if self._loop_ is None:
            return

        fn(self, *args, **kwargs)

    return helper


def check_closing(fn: Callable[..., T]):
    def helper(self, *args, **kwargs) -> T:
        if self._parent._closing:
            raise RuntimeError('modification of closed queue is forbidden')

        return fn(self, *args, **kwargs)

    return helper


get_running_loop = asyncio.get_event_loop \
    if getattr(asyncio, 'get_running_loop', None) is None \
    else asyncio.get_running_loop
