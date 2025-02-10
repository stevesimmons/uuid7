# uuid7 - time-sortable UUIDs

This module implements the version 7 UUIDs, 
proposed by Peabody and Davis and codified as RFC9562,
dated May 2024 (https://www.rfc-editor.org/rfc/rfc9562).

Version 7 has the nice characteristic that the start of a UUID encodes
the time with a chronological sort order and potentially ~100ns time
resolution, while the end of the UUID includes sufficient random bits to
ensure consecutive UUIDs will remain unique.

RFC9562 replaces the original UUID spec RFC4122 from 2005.

Warning:
* This is a breaking change from the previous version 0.1.0,
  which was based on the October 2021 draft of RFC9562. 
  Subsequent drafts changed the time resolution and bit layout.
* This means old UUIDs generated with the earlier release will have
  higher values than new UUID generated with this release.
  So monotonicity is not preserved across the two versions.

## Implementation notes

The 128 bits in the UUID are allocated as follows:
* 48 bits of whole milliseconds, from midnight on 1-Jan-1970.
* 20 bits for fractional milliseconds, which are also 
  used as a sequential counter to ensure monotonicity if
  the underlying timer has a resolution less than the 
  time to call this function.
* 54 bits of randomness
* plus 4 bits for the uuid version (0b111) and 2 bits for the uuid variant (0b10).

```text


     0                   1                   2                   3
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                     unix_ts_ms (upper 32 bits)                |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |   unix_ts_ms (lower 16 bits)  |  ver  |   rand_a (12 bits)    |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |var|                  rand_b (upper 30 bits)                   |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                      rand_b (lower 32 bits)                   |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

```

Here:

* `unix_ts_ms`: 48-bit big-endian unsigned number of the Unix Epoch timestamp in milliseconds.
* `ver`: 4-bit version field, set to 0b0111 (7) to identify this as UUID v7.
* `rand_a`: Top 12 bits of a 20-bit field that combines fractional milliseconds with a sequence counter that increments if the time is unchanged. This gives strong monotonicity guarantees (see RFC9562, section 6.2).
* `var`: 2-bit variant field as defined by Section 4.1 of RFC9562, set to 0b10.
* `rand_b`: The top 8 bits are the remainder of the 20-bit field from `rand_a`. The bottom 54 bits are random to provide uniqueness.

## Usage

```python
>>> from uuid_extensions import uuid7, uuid7_str, uuid7_to_datetime, id25

>>> uuid7()
UUID('0194ef93-1036-73e6-8046-b7efdb0bdaf9')

>>> uuid7(0)
UUID('00000000-0000-0000-0000-00000000000')

>>> uuid7(-1)
UUID('ffffffff-ffff-ffff-ffff-ffffffffffff')

>>> uuid7_str()
'0194ef93-1036-73e6-8046-b7efdb0bdaf9'

>>> uuid7_to_datetime('0194ef93-1036-73e6-8046-b7efdb0bdaf9')
datetime.datetime(2025, 2, 10, 11, 16, 20, 150244, tzinfo=datetime.timezone.utc)

>>> # A compact representation of UUID7, 25 chars long. 
>>> # Useful as visually distinct from UUIDs which in general aren't monontonic.
>>> id25() 
'06fjcz77e515x6seqg5z6ry9w'
>>> uuid7_to_datetime('06fjcz77e515x6seqg5z6ry9w')
datetime.datetime(2025, 2, 10, 12, 4, 34, 719623, tzinfo=datetime.timezone.utc)
```

## Indicative timings

* `uuid4()` - 2.1us (imported from `uuid`)
* `uuid7()` - 2.3us
* `uuid7int()` - 1.5us
* `uuid7str()` - 2.4us
* `id25()` - 5.1us

### Installation

```bash
pip install uuid7
```

## Licence

* Free software: MIT license
