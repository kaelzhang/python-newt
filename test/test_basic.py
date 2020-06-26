import pytest
from newt import (
    Queue
)


def test_basic():
    queue = Queue(2)

    async_queue = queue.async_queue
    sync_queue = queue.sync_queue

    assert async_queue.maxsize == 2
    assert async_queue.empty()

    assert sync_queue.maxsize == 2
    assert sync_queue.empty()


# @pytest.mark.asyncio
# async def test_close_with_pending():
#     q = Queue()

#     await q.async_queue.put(1)

#     q.close()
#     await q.wait_closed()
