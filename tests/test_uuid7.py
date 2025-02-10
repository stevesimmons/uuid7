"""
Tests for `uuid7` package.
"""

import time

from uuid_extensions import uuid7, uuid7_str, id25, to_datetime

def test_uuid7():
    """
    Some simple tests
    """
    # Note the sequence value increments by 1 between each of these uuid7(...) calls
    ns = time.time_ns()
    out1 = str(uuid7(ns))
    out2 = uuid7_str(ns)
    out3 = uuid7_str(ns)

    assert out1[:20] == out2[:20]
    assert out2[:20] == out3[:20]


def test_monotonicity():
    last = ''
    for n in range(100_000):
        i = uuid7_str()
        if n > 0 and i <= last:
            raise RuntimeError(f"UUIDs are not monotonic: {last} versus {i}")
