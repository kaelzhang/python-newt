import asyncio
from concurrent.futures import ThreadPoolExecutor


# def run_two_threads(
#     queue,
#     producer,
#     consumer,
# ):
#     sync_queue = queue.sync_queue
#     threading.Thread(target=producer, args=(sync_queue,)).start()
#     threading.Thread(target=consumer, args=(sync_queue,)).start()


# def run_two_coroutines(
#     queue,
#     producer,
#     consumer
# ):
#     loop = asyncio.get_event_loop()
#     async_queue = queue.async_queue

#     async def main():
#         loop = asyncio.get_event_loop()

#         task1 = loop.create_task(producer(async_queue))
#         task2 = loop.create_task(consumer(async_queue))

#         await asyncio.wait([
#             task1,
#             task2
#         ])

#     loop.run_until_complete(main())


def run_thread_and_coroutine(
    queue,
    producer,
    consumer
):
    async def main():
        await consumer(queue.async_queue)
        queue.close()
        await queue.wait_closed()

    # Use ThreadPoolExecutor to automatically capture thread exceptions
    with ThreadPoolExecutor(max_workers=1) as executor:
        # Submit producer to thread pool
        future = executor.submit(producer, queue.sync_queue)

        # Run the async consumer
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(main())
        finally:
            # Wait for thread completion and get any exception
            future.result()  # This will re-raise any exception from the thread


def run_coroutine_and_thread(
    queue,
    producer,
    consumer
):
    async def main():
        await producer(queue.async_queue)
        queue.close()
        await queue.wait_closed()

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(consumer, queue.sync_queue)

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(main())
        finally:
            future.result()


def create_runner(
    producer_is_async: bool = False
):
    if producer_is_async:
        return run_coroutine_and_thread
    else:
        return run_thread_and_coroutine
