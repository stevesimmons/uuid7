"""
Extract the timestamp component from a UUIDv7.
"""

import datetime
import functools
import time
import uuid
from typing import Callable, Optional, Union

from .id25 import ID25_ALPHABET_LOWER, ID25_ALPHABET_UPPER


def uuid7_to_datetime(
    uuid7: Union[str, uuid.UUID, int],
    ms_only: bool = False,
) -> Optional[datetime.datetime]:
    """
    Datetime in UTC with the timestamp from a UUIDv7, 
    passed in as a string, integer or a UUID object.
    If the UUID is not a version 7 UUID, return None.
    
    Allowable string formats are:
    - UUIDv7 with or without "-"s
    - ID25 format string, length 25 from either the upper case or lower case 35-character alphabet.

    Usage:
    >>> uuid7_to_datetime("1eb22fe4-3f0c-62b1-a88c-8dc55231702f")
    datetime.datetime(2020, 11, 10, 2, 41, 42, 182162)
    """
    ns_since_epoch = timestamp_ns(uuid7, ms_only=ms_only)
    if ns_since_epoch is None:
        return None
    return datetime.datetime.fromtimestamp(
        ns_since_epoch / 1_000_000_000,
        tz=datetime.timezone.utc,
    )


def timestamp_ns(
    uuid7: Union[str, uuid.UUID, int],
    ms_only: bool = False,
) -> Optional[int]:
    """
    Extract the timestamp from a UUIDv7.
    Set ms_only to True to ignore any sub-ms timestamp 
    in the 12 bits of field rand_a. 
    """
    if isinstance(uuid7, uuid.UUID):
        x: int = uuid7.int
    elif isinstance(uuid7, str):
        s = uuid7.replace('-', '')
        if len(s) == 32:
            x = int(s, base=16) # Hex string
        elif len(s) == 25:
            alphabet = ID25_ALPHABET_LOWER if s.islower() else ID25_ALPHABET_UPPER
            x = functools.reduce((lambda x, y: 35 * x + y), map(alphabet.index, s))
        else:
            raise ValueError(f"UUIDv7 string {uuid7!r} is the wrong length")
    else:
        x = uuid7

    uuid_version = (x >> 76) & 0xF
    if uuid_version != 7:
        return None
    t_ms = (x >> 80) & 0xFFFFFFFFFFFF
    if ms_only:
        t_ns = 0
    else:
        rand_a = (x >> 64) & 0x0FFF
        t_ns = (rand_a * 1_000_000) // 4096 # Ignore any sub-microsecond time bits that may be in rand_b
    ns_since_epoch = t_ms * 1_000_000 + t_ns
    return ns_since_epoch
    
###############################################################
# Time checking utility

def check_timing_precision(
    timing_func: Optional[Callable[[], int]] = None,
) -> str:
    """
    Message indicating the timing precision from various time/clock
    functions that might be used for UUIDv7 generation.

    This tests time.time_ns(), time.perf_counter_ns()
    and datetime.datetime.utcnow converted to ns.

    A user-supplied timing function may also be provided.
    It must return the number of ns since the Unix Epoch
    (midnight at 1-Jan-1970).

    Note that time.time_ns() updates every 200us under Linux
    and potentially as infrequently as every 5ms under Windows.

    Usage:
    >>> check_timing_precision()
    # Under Linux
    time.time_ns()           has a timing precision of   221ns rather than 221ns (1,000 distinct samples in 0.00s)
    time.perf_counter_ns()   has a timing precision of   215ns rather than 215ns (1,000 distinct samples in 0.00s)
    datetime.datetime.utcnow has a timing precision of 1,046ns rather than 679ns (1,000 distinct samples in 0.00s)
    # Under Windows
    time.time_ns()           has a timing precision of 4,950,500ns rather than   709ns (705,068 samples of which 101 are distinct, in 0.50s)
    time.perf_counter_ns()   has a timing precision of       823ns rather than   823ns (1,000 samples of which 1,000 are distinct, in 0.00s)
    datetime.datetime.utcnow has a timing precision of 5,882,365ns rather than 2,812ns (177,792 samples of which 85 are distinct, in 0.50s)
    """
    timing_funcs = [
        ("time.time_ns()", time.time_ns),
        ("time.perf_counter_ns()", time.perf_counter_ns),
        ("datetime.datetime.utcnow", lambda: int(
            datetime.datetime.now(datetime.timezone.utc).timestamp() * 1_000_000_000)),
    ]
    if timing_func is not None:
        timing_funcs.append(("user-supplied", timing_func))

    lines = []
    for desc, fn in timing_funcs:
        started_ns = time.perf_counter_ns()
        values = set()
        ctr = 0
        while True:
            values.add(fn())
            ctr += 1
            elapsed_ns = time.perf_counter_ns() - started_ns
            if elapsed_ns > 500_000_000 or len(values) >= 1000:
                break
        precision_ns = elapsed_ns / len(values)
        ideal_precision_ns = elapsed_ns / ctr
        lines.append(
            f"{desc} has a timing precision of {precision_ns:0,.0f}ns \
rather than {ideal_precision_ns:0,.0f}ns ({ctr:,} samples of which \
{len(values):,} are distinct, in {elapsed_ns / 1_000_000_000:0.2f}s)"
        )

    return "\n".join(lines)



