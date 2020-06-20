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

```py
import asyncio

from newt import Queue

queue = Queue()

def threaded(q):
    for i in range(100):
        q.put(i)
    q.join()


async def coroutine(q):
    for i in range(100):
        assert await q.get() == i
        q.task_done()


async def main():
    loop = asyncio.get_running_loop()
    fut = loop.run_in_executor(None, threaded, queue.sync_q)
    await coroutine(queue.async_q)
    await fut

    queue.close()
    await queue.wait_closed()


asyncio.run(main())
```

## License

[MIT](LICENSE)
