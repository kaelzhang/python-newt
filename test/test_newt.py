import pytest

from newt import Queue

from .runner import create_runner
from .factory import create


def map_args(queue, producer_options, consumer_options):
    if type(producer_options) is bool:
        producer_options = {
            'is_async': producer_options
        }

    if type(consumer_options) is bool:
        consumer_options = {
            'is_async': consumer_options
        }

    return (queue, producer_options, consumer_options)


CASES = [
    (Queue(), True, False),
    (Queue(), False, True)
]


@pytest.mark.parametrize(
    'queue,producer_options,consumer_options', [
        map_args(*c)
        for c in CASES
    ]
)
def test_newt(
    queue,
    producer_options: dict,
    consumer_options: dict
):
    producer_is_async = producer_options.get('is_async', False)
    consumer_is_async = consumer_options.get('is_async', False)

    producer = create(**producer_options)
    consumer = create(**consumer_options)

    runner = create_runner(producer_is_async, consumer_is_async)

    runner(queue, producer, consumer)
