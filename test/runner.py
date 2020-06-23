import threading
import asyncio


def run_two_threads(
    queue,
    producer,
    consumer,
):
    sync_queue = queue.sync_queue
    threading.Thread(target=producer, args=(sync_queue,)).start()
    threading.Thread(target=consumer, args=(sync_queue,)).start()


def run_two_coroutines(
    queue,
    producer,
    consumer
):
    loop = asyncio.get_event_loop()
    async_queue = queue.async_queue

    async def main():
        loop = asyncio.get_event_loop()

        task1 = loop.create_task(producer(async_queue))
        task2 = loop.create_task(consumer(async_queue))

        await asyncio.wait([
            task1,
            task2
        ])

    loop.run_until_complete(main())


def run_thread_and_coroutine(
    queue,
    producer,
    consumer
):
    async def main():
        await consumer(queue.async_queue)
        queue.close()
        queue.wait_closed()

    threading.Thread(target=producer, args=(queue.sync_queue,)).start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


def run_coroutine_and_thread(
    queue,
    producer,
    consumer
):
    async def main():
        await producer(queue.async_queue)
        queue.close()
        queue.wait_closed()

    threading.Thread(target=consumer, args=(queue.sync_queue,)).start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


def create_runner(producer_async, consumer_async):
    if producer_async:
        if consumer_async:
            return run_two_coroutines
        else:
            return run_coroutine_and_thread
    else:
        if consumer_async:
            return run_thread_and_coroutine
        else:
            return run_two_threads