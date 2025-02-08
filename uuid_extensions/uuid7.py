"""
Implementation of UUID v7 per the October 2021 draft update
to RFC4122 from 2005:
https://datatracker.ietf.org/doc/html/draft-peabody-dispatch-new-uuid-format

Stephen Simmons, v0.1.0, 2021-12-27
"""

__all__ = (
    "uuid7",
    "uuid7str",
    "time_ms",
    "check_timing_precision",
    "uuid_to_datetime",
    "uuidfromvalues",
    "format_byte_array_as_uuid"
)

import datetime
import os
import struct
import time
from typing import Callable, Optional, Union
import uuid

# Expose function used by uuid7() to get current time in milliseconds
# since the Unix epoch.
time_ms = lambda: time.time_ns() // 1_000_000

def uuid7(
    ms: Optional[int] = None,
    as_type: Optional[str] = None,
    time_func: Callable[[], int] = time_ms,
    _last=[0, 0, 0, 0],
    _last_as_of=[0, 0, 0, 0],
) -> Union[uuid.UUID, str, int, bytes]:
    """
    UUID v7, following the proposed extension to RFC4122 described in
    https://www.ietf.org/id/draft-peabody-dispatch-new-uuid-format-02.html.
    All representations (string, byte array, int) sort chronologically,
    with a potential time resolution of 50ns (if the system clock
    supports this).

    Parameters
    ----------

    ms      - Optional integer with the whole number of milliseconds
                since Unix epoch, to set the "as of" timestamp.

    as_type - Optional string to return the UUID in a different format.
                A uuid.UUID (version 7, variant 0x10) is returned unless
                this is one of 'str', 'int', 'hex' or 'bytes'.

    time_func - Set the time function, which must return integer
                milliseconds since the Unix epoch, midnight on 1-Jan-1970.
                Defaults to time.time_ns()/1e6. This is exposed because
                time.time_ns() may have a low resolution on Windows.

    Returns
    -------

    A UUID object, or if as_type is specified, a string, int or
    bytes of length 16.

    Implementation notes
    --------------------

    The 128 bits in the UUID are allocated as follows:
    - 36 bits of whole seconds
    - 24 bits of fractional seconds, giving approx 50ns resolution
    - 14 bits of sequential counter, if called repeatedly in same time tick
    - 48 bits of randomness
    plus, at locations defined by RFC4122, 4 bits for the
    uuid version (0b111) and 2 bits for the uuid variant (0b10).

     0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                           unix_ts_ms                          |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |          unix_ts_ms           |  ver  |       rand_a          |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |var|                        rand_b                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                            rand_b                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    Indicative timings:
    - uuid.uuid4()            2.4us
    - uuid7()                 3.7us
    - uuid7(as_type='int')    1.6us
    - uuid7(as_type='str')    2.5us

    Examples
    --------

    >>> uuid7()
    UUID('061cb26a-54b8-7a52-8000-2124e7041024')

    >>> for fmt in ('bytes', 'hex', 'int', 'str', 'uuid', None):
    ...     print(fmt, repr(uuid7(as_type=fmt)))
    bytes b'\x06\x1c\xb8\xfe\x0f\x0b|9\x80\x00\tjt\x85\xb3\xbb'
    hex '061cb8fe0f0b7c3980011863b956b758'
    int 8124504378724980906989670469352026642
    str '061cb8fe-0f0b-7c39-8003-d44a7ee0bdf6'
    uuid UUID('061cb8fe-0f0b-7c39-8004-0489578299f6')
    None UUID('061cb8fe-0f0f-7df2-8000-afd57c2bf446')
    """
    if ms is None:
        ms = time_func()
    else:
        ms = int(ms)  # Fail fast if not an int

    rand_a = int.from_bytes(os.urandom(2))
    rand_b = int.from_bytes(os.urandom(8))
    uuid_bytes = uuidfromvalues(ms, rand_a, rand_b)

    uuid_int = int.from_bytes(uuid_bytes)
    if as_type == "int":
        return int.from_bytes(uuid_bytes)
    elif as_type == "bin":
        return bin(int.from_bytes(uuid_bytes))
    elif as_type == "hex":
        return f"{uuid_int:>032x}"
    elif as_type == "bytes":
        return uuid_int.to_bytes(16, "big")
    elif as_type == "str":
        return format_byte_array_as_uuid(uuid_bytes)
    else:
        return uuid.UUID(int=uuid_int)


def uuidfromvalues(unix_ts_ms: int, rand_a: int, rand_b: int):
    version = 0x07
    var = 2
    rand_a &= 0xfff
    rand_b &= 0x3fffffffffffffff

    final_bytes = unix_ts_ms.to_bytes(6)
    final_bytes += ((version<<12)+rand_a).to_bytes(2)
    final_bytes += ((var<<62)+rand_b).to_bytes(8)

    return final_bytes

def format_byte_array_as_uuid(arr: bytes):
    return f"{arr[:4].hex()}-{arr[4:6].hex()}-{arr[6:8].hex()}-{arr[8:10].hex()}-{arr[10:].hex()}"

def uuid7str(ms: Optional[int] = None) -> str:
    "uuid7() as a string without creating a UUID object first."
    return uuid7(ms, as_type="str")  # type: ignore


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
            datetime.datetime.utcnow().timestamp() * 1_000_000_000)),
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


def timestamp_ms(
    s: Union[str, uuid.UUID, int],
    suppress_error=True,
) -> Optional[int]:
    """
    Recover the timestamp from a UUIDv7, passed in
    as a string, integer or a UUID object.

    If the UUID is not a version 7 UUID, either raise a ValueError
    or return None, depending on suppress_error.

    Usage:
    >>> uuid_to_datetime("017f22e2-79b0-7cc3-98c4-dc0c0c07398f")
    datetime.datetime(2022, 2, 23, 6, 22, 22)
    """
    if isinstance(s, uuid.UUID):
        x = s.bytes
    elif not s:
        x = b"\0" * 16
    elif isinstance(s, int):
        x = int.to_bytes(s, length=16, byteorder="big")
    else:  # String form that should look like a UUID
        int_uuid = int(str(s).replace("-", ""), base=16)
        x = int.to_bytes(int_uuid, length=16, byteorder="big")

    uuid_version = x[6] >> 4
    if uuid_version == 7:
        return int.from_bytes(x[:6])
    elif suppress_error:
        return None
    else:
        raise ValueError(
            f"{str(s)} is a version {uuid_version} UUID, \
not v7 so we cannot extract the timestamp."
        )


def uuid_to_datetime(
    s: Union[str, uuid.UUID, int],
    suppress_error=True,
) -> Optional[datetime.datetime]:
    ms_since_epoch = timestamp_ms(s, suppress_error=suppress_error)
    if ms_since_epoch is None:
        return None
    else:
        return datetime.datetime.fromtimestamp(
            ms_since_epoch / 1_000,
            tz=datetime.timezone.utc,
        )
