import asyncio
import time

RANGE = 100


def async_producer(
    sleep_on_every,
    sleep,
    sequence,
    init_delay
):
    async def p(queue):
        if init_delay:
            await asyncio.sleep(init_delay)

        for i, item in enumerate(sequence):
            await queue.put(item)

            if (i + 1) % sleep_on_every == 0:
                await asyncio.sleep(sleep)

        await queue.join()

    return p


def async_consumer(
    sleep_on_every,
    sleep,
    sequence,
    init_delay
):
    async def c(queue):
        if init_delay:
            await asyncio.sleep(init_delay)

        for i, item in enumerate(sequence):
            print(i, item)
            assert await queue.get() == item

            if (i + 1) % sleep_on_every == 0:
                await asyncio.sleep(sleep)

            queue.task_done()

    return c


def sync_producer(
    sleep_on_every,
    sleep,
    sequence,
    init_delay
):
    def p(queue):
        if init_delay:
            time.sleep(init_delay)

        for i, item in enumerate(sequence):
            queue.put(item)

            if (i + 1) % sleep_on_every == 0:
                time.sleep(sleep)

        queue.join()

    return p


def sync_consumer(
    sleep_on_every,
    sleep,
    sequence,
    init_delay
):
    def c(queue):
        if init_delay:
            time.sleep(init_delay)

        for i, item in enumerate(sequence):
            assert queue.get() == item

            if (i + 1) % sleep_on_every == 0:
                time.sleep(sleep)

            queue.task_done()

    return c


def create(
    consumer=False,
    is_async=False,
    sleep_on_every=RANGE,
    sleep=0.1,
    sequence=range(RANGE),
    init_delay=0
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

    return factory(
        sleep_on_every,
        sleep,
        sequence,
        init_delay
    )
