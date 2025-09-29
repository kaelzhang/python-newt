import pytest

from asyncio import QueueEmpty

from newt import (
    Queue
)


def test_basic():
    queue = Queue(2)

    async_queue = queue.async_queue
    sync_queue = queue.sync_queue

    assert async_queue.maxsize == 2
    assert async_queue.empty()
    assert not async_queue.full()

    assert sync_queue.maxsize == 2
    assert sync_queue.empty()
    assert not sync_queue.full()


@pytest.mark.asyncio
async def test_close_with_pending_and_not_full():
    q = Queue(0)

    await q.async_queue.put(1)

    assert not q.async_queue.full()
    assert q.async_queue.qsize() == 1
    assert await q.async_queue.get() == 1

    with pytest.raises(QueueEmpty):
        q.async_queue.get_nowait()

    q.close()
    await q.wait_closed()
