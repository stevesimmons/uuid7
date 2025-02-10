"""
Implementation of time-ordered UUID v7 per RFC9562 

Stephen Simmons, v1.0.0-alpha, 2025-02-09

This conforms to the finalized version of RFC9562,
dated May 2024 (https://www.rfc-editor.org/rfc/rfc9562), 
which replaced the original UUID RFC4122 from 2005.


Warning:
* This version is a breaking change from the original version 0.1.0,
  which was based on the October 2021 draft of RFC9562. 
  Later drafts changed the time resolution and bit layout.
* This means old UUIDs generated with the earlier release will have
  higher values than new UUID generated with this release.
  So monotonicity is not preserved across the two versions.
"""

__all__ = (
    "uuid7",     # Returns UUIDv7 as a UUID object
    "uuid7_bytes",
    "uuid7_int",
    "uuid7_hex",
    "uuid7_str",
    "uuid7_uuid",
)

import os
import time
import uuid
from typing import Optional

# Function used by uuid7() to get current time in nanoseconds since the Unix epoch.
# Exposed as a module global so a different timer can be set globally if desired.
time_ns = time.time_ns

# Options for returning UUID v7 as a UUID object, hex string, UUID string, integer or bytes.
# Internally these all start with uuid7_int().

def uuid7(ns: Optional[int] = None) -> uuid.UUID:
    "uuid7() as a UUID object."
    return uuid.UUID(int=uuid7_int(ns))

uuid7_uuid = uuid7 # Alias for consistency

def uuid7_hex(ns: Optional[int] = None) -> str:
    "uuid7() as a hex string."
    return f"{uuid7_int(ns):032x}" # 32 lower case hex digits long

def uuid7_str(ns: Optional[int] = None) -> str:
    "uuid7() as a lower-case UUID string, without creating a UUID object first."
    s = f"{uuid7_int(ns):032x}" # 32 lower case hex digits long
    return f"{s[0:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:32]}"

def uuid7_bytes(ns: Optional[int] = None) -> bytes:
    "uuid7() as a 128-bit long byte string."
    return uuid7_int(ns).to_bytes(length=16)


# Primary implementation, returning a UUID v7 as an integer.

def uuid7_int(
    ns: Optional[int] = None,
    _last: list[int]=[0, 0],
    _last_as_of: list[int]=[0, 0],
) -> int:
    """
    UUID v7 is a time-ordered UUID, as described in RFC9562 (May 2024):
    https://www.rfc-editor.org/rfc/rfc9562

    This version returns integer UUIDs. The other library functions
    call this one and return proper UUID objects, UUID strings, byte arrays 
    or hex strings. All of the same type will sort chronologically,
    with a potential time resolution of 100-200ns.

    Parameters
    ----------

    ns          - Optional integer with the whole number of nanoseconds
                  since Unix epoch to use as an "as of" timestamp.
                  As special cases, uuid7(ns=0) returns the "nil UUID"
                  with all bits zero. uuid7(ns=-1) return "max UUID" 
                  with all bits set.

    _last       - Mutable list used internally to track the last call's 
                  values so that monotonic uuids can be returned.
                  Used for calls 'now' when `ns` is None.
    _last_as_of - Similar to _last, but used when `ns` is not None
                  or the fixed nil and max UUIDs.

    Returns
    -------

    UUID v7 as a 128-bit integer.

    Implementation notes
    --------------------

    The 128 bits in the UUID are allocated as follows:
    - 48 bits of whole milliseconds, from midnight on 1-Jan-1970.
    - 20 bits for fractional milliseconds, which are also 
      used as a sequential counter to ensure monotonicity if
      the underlying timer has a resolution less than the 
      time to call this function.
    - 54 bits of randomness
    plus, at locations defined by RFC9562, 4 bits for the
    uuid version (0b111) and 2 bits for the uuid variant (0b10).

     0                   1                   2                   3
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                     unix_ts_ms (upper 32 bits)                |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |   unix_ts_ms (lower 16 bits)  |  ver  |   rand_a (12 bits)    |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |var|                        rand_b                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                            rand_b                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    unix_ts_ms:
       48-bit big-endian unsigned number of the Unix Epoch timestamp in milliseconds.

    ver:
       The 4-bit version field, set to 0b0111 (7) to identify this as UUID v7.

    rand_a:
       Top 12 bits of a 20 bit field that combines fractional milliseconds with 
       a sequence counter that increments if the time is unchanged. 
       This gives strong monotonicity guarantees (see RFC9562, section 6.2).
    
    var:
       The 2-bit variant field as defined by Section 4.1 of RFC9562, set to 0b10.

    rand_b:
       The top 8 bits are the remainder of the 20 bit field from rand_a.
       The bottom 54 bits are random to provide uniqueness.

    Examples
    --------

    >>> uuid7()
    UUID('0194ef93-1036-73e6-8046-b7efdb0bdaf9')

    >>> uuid7(0)
    UUID('00000000-0000-0000-0000-00000000000')

    >>> uuid7_str()
    '0194ef93-1036-73e6-8046-b7efdb0bdaf9'
    
    >>> uuid7_to_datetime('0194ef93-1036-73e6-8046-b7efdb0bdaf9')
    datetime.datetime(2025, 2, 10, 11, 16, 20, 150244, tzinfo=datetime.timezone.utc)
    """
    # Get the values returned in the last call, using separate history
    # for 'now' and 'as of' UUID7 calls. This ensure 'now' calls remain
    # strictly monotonic even if some intervening 'as of' calls are made.
    if ns is None:
        ns = time_ns()
        last = _last
    else:
        ns = int(ns)  # Fail fast if not an int
        last = _last_as_of

    # Special cases for the Nil UUID and Max UUID defined in RFC9562.
    # Strictly speaking, neither are UUID v7.
    if ns == 0:
        return 0 # All bits zero
    elif ns == -1:
        return (1 << 128) - 1 # All bits set
    
    # Let's aim to generate uuid7s separated by an apparent 1ns before 
    # the lower purely random bits may break monotonicity.
    #
    # By comparison:
    # - Highest resolution timestamps have precision of ~200ns on Linux.
    #   Windows uses 100ns ticks, though actual resolution may be quite a bit lower.
    # - This uuid7int() function takes about 1.6us to generate a UUID.
    # 
    # 1ns is 1/1,000,000 of a millisecond, or around 20 bits of precision.
    # Since rand_a has 12 bits, we'd need to use the top 8 bits of rand_b.
    # This corresponds "Replace leftmost random bits with increased clock
    # precision (Method 3)" of the RFC's section 6.1 Timestamp Considerations.
    # This leaves 56 bits of pure randomness in the lower 7 bytes of rand_b.
    t_ms, rest = divmod(ns, 1_000_000)          # 48 bits of whole milliseconds
    t_ns = (rest * (1 << 20)) // 1_000_000      # 20 bits for fractional milliseconds plus a sequence counter
    rand = int.from_bytes(os.urandom(7))        # 56 bits of randomness
    
    # If the timestamps are the same as the last one, increment the ns timestamp
    # as a sequence counter, but only if it won't overflow 20 bits.
    if t_ms == last[0] and t_ns == last[1] and t_ns < 0x3FFFF:
        t_ns += 1
    last[:] = (t_ms, t_ns) # Cache for next call in _last or _last_as_of

    # Build the UUIDv7 integer
    rand_a = t_ns >> 8
    rand_b = ((t_ns & 0xFF) << 32) | rand
    out = (t_ms << 80) | (7 << 76) | (rand_a << 64) | (2 << 62) | rand_b
    return out



