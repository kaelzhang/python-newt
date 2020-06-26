import pytest
import asyncio

from newt import (
    Queue
)

from .runner import create_runner
from .factory import create


def test_modify_closed_queue():
    producer = create()
    consumer = create(consumer=True, is_async=True)
    runner = create_runner()

    queue = Queue()
    queue.close()

    with pytest.raises(
        RuntimeError,
        match='closed queue is forbidden'
    ):
        runner(
            queue,
            producer,
            consumer
        )


def test_init_fail():
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(None)

    with pytest.raises(
        RuntimeError,
        match='not an issue of newt'
    ):
        Queue()

    asyncio.set_event_loop(loop)


@pytest.mark.asyncio
async def test_await_for_unclosed_queue():
    q = Queue()

    with pytest.raises(
        RuntimeError,
        match='waiting for non-closed queue'
    ):
        await q.wait_closed()
