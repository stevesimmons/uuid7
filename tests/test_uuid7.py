"""
Tests for `uuid7` package.
"""

import datetime
import time
import uuid

from uuid_extensions import uuid7, uuid7_str, id25, uuid7_to_datetime

def test_uuid7():
    """
    Some simple tests
    """
    now1 = datetime.datetime.now(tz=datetime.timezone.utc)
    x = uuid7()
    now2 = datetime.datetime.now(tz=datetime.timezone.utc)
    assert isinstance(x, uuid.UUID)
    assert x.version == 7
    dt = uuid7_to_datetime(x)
    assert now1 < dt < now2
    
    # Note the sequence value increments by 1 between each of these uuid7(...) calls
    ns = time.time_ns()
    out1 = str(uuid7(ns))
    out2 = uuid7_str(ns)
    out3 = uuid7_str(ns)

    # Leading time part is the same
    assert out1[:20] == out2[:20]
    assert out2[:20] == out3[:20]

    # Contain randomness
    assert out1 != out2
    assert out2 != out3

    out1 = str(uuid7())
    out2 = uuid7_str()
    out3 = uuid7_str()
    assert out1 < out2 < out3

def test_monotonicity():
    last = ''
    for n in range(100_000):
        i = uuid7_str()
        if n > 0 and i <= last:
            raise RuntimeError(f"UUIDs are not monotonic: {last} versus {i}")


def test_times_and_id25():
    ns = time.time_ns()
    x = id25(ns)
    assert isinstance(x, str)
    assert len(x) == 25
    assert x.islower()
    assert 'l' not in x

    dt = uuid7_to_datetime(x)
    assert abs(dt.timestamp() - ns / 1_000_000_000) < 0.01

    x1 = id25()
    x2 = id25()
    assert x2 > x1