import asyncio
import threading
import time

from newt import Queue

def test_threaded_in_executor_with_coroutine():
    queue = Queue()

    loop = asyncio.get_event_loop()

    def threaded(q):
        for i in range(100):
            q.put(i)
        q.join()


    async def coroutine(q):
        for i in range(100):
            assert await q.get() == i
            q.task_done()


    async def main():
        future = loop.run_in_executor(None, threaded, queue.sync_q)
        await coroutine(queue.async_q)
        await future

        queue.close()
        await queue.wait_closed()

    loop.run_until_complete(main())


def test_threading_with_coroutine():
    queue = Queue()
    loop = asyncio.get_event_loop()

    def threaded(q):
        for i in range(100):
            q.put(i)
        q.join()

    async def coroutine(q):
        for i in range(100):
            got = await q.get()
            assert got == i
            q.task_done()

    async def main():
        await coroutine(queue.async_q)
        queue.close()
        await queue.wait_closed()

    t = threading.Thread(target=threaded, args=(queue.sync_q,))
    t.start()

    time.sleep(.1)

    loop.run_until_complete(main())
