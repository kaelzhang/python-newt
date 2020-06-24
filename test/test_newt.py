import pytest
import itertools
from typing import (
    Tuple,
    Union
)

from newt import (
    LifoQueue,
    PriorityQueue,
    Queue
)

from .runner import create_runner
from .factory import create


def map_options(options: Union[dict, bool]) -> dict:
    if type(options) is bool:
        return {
            'is_async': options
        }

    return options


def map_two_options(l: list):
    return [
        (map_options(a), map_options(b))
        for a, b in l
    ]


@pytest.mark.parametrize(
    'queue_ctor,max_size,options',
    itertools.product(
        [
            Queue,
            PriorityQueue,
            # LifoQueue
        ],
        [-1, 2],
        map_two_options([
            (True, False),
            (False, True)
        ])
    )
)
def test_newt(
    queue_ctor,
    max_size: int,
    options: Tuple[dict, dict]
):
    queue = queue_ctor(max_size)

    producer_options, consumer_options = options

    producer_is_async = producer_options.get('is_async', False)

    producer = create(**producer_options)
    consumer = create(**consumer_options)

    runner = create_runner(producer_is_async)

    runner(queue, producer, consumer)
