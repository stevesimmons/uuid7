#!/usr/bin/env python
"""
Tests for `uuid7` package.
"""
import time

from uuid_extensions import uuid7, uuid7str

def test_uuid7():
    """
    Some simple tests
    """
    # Note the sequence value increments by 1 between each of these uuid7(...) calls
    ns = time.time_ns()
    out1 = str(uuid7(ns))
    out2: str = uuid7(ns, as_type='str') # type: ignore
    out3 = uuid7str(ns)

    assert out1[:20] == out2[:20]
    assert out2[:20] == out3[:20]


def test_monotonicity():
    last = ''
    for n in range(100_000):
        i = uuid7str()
        if n > 0 and i <= last:
            raise RuntimeError(f"UUIDs are not monotonic: {last} versus {i}")
