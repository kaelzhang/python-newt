import pytest

from newt import (
    Queue
)

from .runner import create_runner
from .factory import create


def test_closing():
    producer = create()
    consumer = create(consumer=True, is_async=True)
    runner = create_runner()

    queue = Queue()
    queue.close()

    with pytest.raises(
        RuntimeError,
        match=''
    ):
        runner(
            queue,
            producer,
            consumer
        )
