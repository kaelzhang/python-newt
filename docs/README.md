[![](https://travis-ci.org/kaelzhang/python-newt.svg?branch=master)](https://travis-ci.org/kaelzhang/python-newt)
[![](https://codecov.io/gh/kaelzhang/python-newt/branch/master/graph/badge.svg)](https://codecov.io/gh/kaelzhang/python-newt)
[![](https://img.shields.io/pypi/v/newt.svg)](https://pypi.org/project/newt/)
[![](https://img.shields.io/pypi/l/newt.svg)](https://github.com/kaelzhang/python-newt)

# [newt](https://github.com/kaelzhang/python-newt)

Thread-safe, mixed-threading-and-asyncio, producer-consumer queue for Python.

Heavily based on [janus](https://github.com/aio-libs/janus), but [newt](https://github.com/kaelzhang/python-newt) lazily initializes event loop which makes the queue much more flexible.

## Install

```sh
$ pip install newt
```

## Usage

Suppose there is a threaded target function which produces items, and a coroutine which consumes items.

```py
from newt import Queue


def threaded(sync_queue):
    for i in range(100):
        sync_queue.put(i)
    sync_queue.join()
```

`sync_queue` follows the interface of Python built-in [synchronized queue class](https://docs.python.org/3/library/queue.html)

```py
async def coroutine(async_queue):
    for i in range(100):
        assert await async_queue.get() == i
        async_queue.task_done()
```

`async_queue` follows the vanilla Python [`asyncio.Queue`](https://docs.python.org/3/library/asyncio-queue.html)

### Thread in an executor -> Coroutine

The following example shows how to produce item in a thread which executed in the executor, and consume the item in a coroutine.

```py
import asyncio

loop = asyncio.get_event_loop()


async def main():
    future = loop.run_in_executor(None, threaded, queue.sync_queue)
    await coroutine(queue.async_queue)
    await future

    queue.close()
    await queue.wait_closed()

loop.run_until_complete(main())
```

### Normal thread -> Coroutine

`newt.Queue` also supports to produce item in a normal threading,

```py
loop = asyncio.get_event_loop()


async def main():
    await coroutine(queue.async_queue)
    queue.close()
    await queue.wait_closed()

t = threading.Thread(target=threaded, args=(queue.sync_queue,))
t.start()

loop.run_until_complete(main())
```

## License

[MIT](LICENSE)
