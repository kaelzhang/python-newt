import asyncio
import time

RANGE = 100


def async_producer(sleep_on_every, sleep):
    async def p(queue):
        for i in range(RANGE):
            await queue.put(i)

            if (i + 1) % sleep_on_every == 0:
                await asyncio.sleep(sleep)

        queue.join()

    return p


def async_consumer(sleep_on_every, sleep):
    async def c(queue):
        for i in range(RANGE):
            assert await queue.get() == i

            if (i + 1) % sleep_on_every == 0:
                await asyncio.sleep(sleep)

            queue.task_done()

    return c


def sync_producer(sleep_on_every, sleep):
    def p(queue):
        for i in range(RANGE):
            queue.put(i)

            if (i + 1) % sleep_on_every == 0:
                time.sleep(sleep)

        queue.join()

    return p


def sync_consumer(sleep_on_every, sleep):
    def c(queue):
        for i in range(RANGE):
            assert queue.get() == i

            if (i + 1) % sleep_on_every == 0:
                time.sleep(sleep)

            queue.task_done()

    return c


def create(
    consumer=False,
    is_async=False,
    sleep_on_every=RANGE,
    sleep=0.1
):
    if consumer:
        if is_async:
            factory = async_consumer
        else:
            factory = sync_consumer
    else:
        if is_async:
            factory = async_producer
        else:
            factory = sync_consumer

    return factory(sleep_on_every, sleep)
