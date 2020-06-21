import asyncio
from newt import Queue

def test_example():
    queue = Queue()

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
        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(None, threaded, queue.sync_q)
        await coroutine(queue.async_q)
        await fut

        queue.close()
        await queue.wait_closed()

    asyncio.run(main())
