import pytest

from newt import Queue

from .runner import create_runner
from .factory import create


@pytest.mark.parametrize(
    'queue,producer_options,consumer_options', [
        (Queue(), True, True)
    ]
)
def test_newt(
    queue,
    producer_options,
    consumer_options
):
