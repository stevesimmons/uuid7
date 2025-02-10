"""
id25 is a simple compact string representation of a UUIDv7
like '06fjcfdf5g12nfr3ffvzvucic'.

It has the following nice properties:
- Sortable - Maintains UUID7's monotonicity property.
- Short - At 25 characters long, it is the shortest string from an alphabet of 
  single-case letters and digits that can represent the 128 bits of a UUID.
- Easy to copy/paste - By omitting the '-' from UUID strings, whole ID25 
  strings can be selected for copying with a single mouse click.
- Unambiguous - Since the resulting strings are same length whether
  the alphabet has 35 or 36 characters, we omit 'l' to avoid 
  confusion with '1'. And by using lowercase, we avoid confusion between '0' and 'o'.
- Distinguishable - As it's not easy to tell that a UUID field only contains
  UUIDv7, using ID25 instead makes it clear that the field is time-sorted. 
"""

__all__ = ('id25', 'ID25', 'uuid7_id25')

import uuid
from typing import Optional, Union

from .uuid7 import uuid7_int

# Digits must be first. Omit 'l' or 'O' depending on case
ID25_ALPHABET_LOWER = '0123456789abcdefghijkmnopqrstuvwxyz' # Omits 'l' since similar to '1'.
ID25_ALPHABET_UPPER = '0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ' # Omits 'O' since similar to '0'. 

def uuid7_id25(ns_or_uuid: Optional[Union[int, uuid.UUID]] = None, upper_case: bool = False) -> str:
    """
    UUIDv7 as sortable string of length 25 with chars from 0-9/a-k/m-z.
    (or 0/9/A-N/P-Z for upper case).
    
    In lower case, 'l' is omitted because it is similar to '1'. '0' and 'o' are distinct.
    In upper case, 'O' is omitted because it is similar to '0'. 'L' and '1' are distinct.

    >>> id25(), id25(), id25(0), id25(-1), id25(uuid.uuid4())
    ('06fjcfdf5g12nfr3ffvzvucic',
    '06fjcfdf5g1pn51b75ens9ee3',
    '0000000000000000000000000',
    'usz5xbbiqsfq7s727n0pzr2xa',
    'mvmrfsn4uik7aj25yto09fbb6')
    """
    
    if ns_or_uuid is None:
        uuid_int = uuid7_int()
    elif isinstance(ns_or_uuid, int):
        uuid_int = uuid7_int(ns_or_uuid)
    elif isinstance(ns_or_uuid, uuid.UUID):
        uuid_int = ns_or_uuid.int
    else:
        raise ValueError("Invalid type for ns_or_uuid. Must be int or UUID.")
    
    # Convert integer UUID7 to base 35 string with 25 characters
    out: list[str] = []
    length = 25
    alphabet = ID25_ALPHABET_UPPER if upper_case else ID25_ALPHABET_LOWER
    rest = uuid_int
    for _ in range(length):
        rest, i = divmod(rest, 35)
        out.append(alphabet[i])
    return ''.join(reversed(out))
    
# Shortcuts for using the upper or lower case alphabets

id25 = uuid7_id25 # Using the lower-case alphabet.

def ID25(ns_or_uuid: Optional[Union[int, uuid.UUID]] = None) -> str:
    "UUID7 in id25 format using the upper case alphabet (hence ID25)."
    return uuid7_id25(ns_or_uuid, upper_case=True)