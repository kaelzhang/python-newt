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


def map_options(options: Union[dict, bool], consumer: bool) -> dict:
    if type(options) is bool:
        return {
            'consumer': consumer,
            'is_async': options
        }

    return {
        **options,
        'consumer': consumer
    }


def map_two_options(l: list):
    return [
        (
            map_options(a, False),
            map_options(b, True)
        )
        for a, b in l
    ]


def run(
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


@pytest.mark.parametrize(
    'queue_ctor,max_size,options',
    itertools.product(
        [
            Queue
        ],
        [
            -1,
            # 2
        ],
        map_two_options([
            (True, False),
            (False, True),
            (
                {
                    'is_async': True,
                    'sleep_on_every': 2
                },
                {
                    'is_async': False,
                    'sleep_on_every': 3
                }
            )
        ])
    )
)
def test_queue(
    queue_ctor,
    max_size: int,
    options: Tuple[dict, dict]
):
    run(queue_ctor, max_size, options)


priority_queue_sequence = [
    (2, 1),
    (1, 0),
    (4, 3),
    (5, 4),
    (6, 5),
    (3, 2),
]

@pytest.mark.parametrize(
    'queue_ctor,max_size,options',
    itertools.product(
        [
            PriorityQueue
        ],
        [-1],
        map_two_options([
            (
                {
                    'is_async': True,
                    'sequence': priority_queue_sequence
                },
                {
                    'is_async': False,
                    'sequence': sorted(
                        priority_queue_sequence,
                        key=lambda x: x[0]
                    ),
                    'init_delay': 0.2
                }
            )
        ])
    )
)
def test_priority_queue(
    queue_ctor,
    max_size: int,
    options: Tuple[dict, dict]
):
    run(queue_ctor, max_size, options)


lifo_queue_sequence = range(100)
lifo_queue_sequence_got = list(lifo_queue_sequence)

lifo_queue_sequence_got.reverse()


@pytest.mark.parametrize(
    'queue_ctor,max_size,options',
    itertools.product(
        [
            LifoQueue
        ],
        [-1],
        map_two_options([
            (
                {
                    'is_async': False,
                    'sequence': lifo_queue_sequence
                },
                {
                    'is_async': True,
                    'sequence': lifo_queue_sequence_got,
                    'init_delay': 0.2
                }
            )
        ])
    )
)
def test_lifo_queue(
    queue_ctor,
    max_size: int,
    options: Tuple[dict, dict]
):
    run(queue_ctor, max_size, options)
