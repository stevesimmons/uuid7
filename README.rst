uuid7 - time-sortable UUIDs
===========================

This module implements the version 7 UUIDs, proposed by Peabody and Davis in
https://www.ietf.org/id/draft-peabody-dispatch-new-uuid-format-02.html
as an extension to RFC4122.

Version 7 has the nice characteristic that the start of a UUID encodes
the time with a chronological sort order and potentially ~50ns time
resolution, while the end of the UUID includes sufficient random bits to
ensure consecutive UUIDs will remain unique.

Implementation notes
--------------------

The 128 bits in the UUID are allocated as follows: 

* 36 bits of whole seconds
* 24 bits of fractional seconds, giving approx 50ns resolution
* 14 bits of sequential counter, if called repeatedly in same time tick
* 48 bits of randomness

plus, at locations defined by RFC4122, 4 bits for the uuid version (0b111) and 2 bits for the uuid variant (0b10).

.. code:: text

                0                   1                   2                   3
                0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       t1      |                 unixts (secs since epoch)                     |
               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       t2/t3   |unixts |  frac secs (12 bits)  |  ver  |  frac secs (12 bits)  |
               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       t4/rand |var|       seq (14 bits)       |          rand (16 bits)       |
               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       rand    |                          rand (32 bits)                       |
               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

Indicative timings:

* `uuid.uuid4()` - 2.4us
* `uuid7()` - 3.7us
* `uuid7(as_type='int')` - 1.6us
* `uuid7(as_type='str')` - 2.5us

Installation
------------

.. code:: bash

   > pip install uuid7

Usage
-----

.. code:: ipython

   >>> from uuid_extensions import uuid7, uuid7str
   >>> uuid7()
   UUID('061cb26a-54b8-7a52-8000-2124e7041024')

   >>> uuid7(0)
   UUID('00000000-0000-0000-0000-00000000000')

   >>> for fmt in ('bytes', 'hex', 'int', 'str', 'uuid', None):
   ...     print(fmt, repr(uuid7(as_type=fmt)))
   bytes b'\x06\x1c\xb8\xfe\x0f\x0b|9\x80\x00\tjt\x85\xb3\xbb'
   hex '061cb8fe0f0b7c3980011863b956b758'
   int 8124504378724980906989670469352026642
   str '061cb8fe-0f0b-7c39-8003-d44a7ee0bdf6'
   uuid UUID('061cb8fe-0f0b-7c39-8004-0489578299f6')
   None UUID('061cb8fe-0f0f-7df2-8000-afd57c2bf446')

   >>> uuid7str() # Shorthand for uuid7(as_type='str')
   '061cb26a-54b8-7a52-8000-2124e7041024'

Licence
-------

-  Free software: MIT license
