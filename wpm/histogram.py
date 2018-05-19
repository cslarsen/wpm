# -*- encoding: utf-8 -*-

"""
This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

import collections
import math
import sys

def unicode_chr(ordinal):
    if sys.version_info.major >= 3:
        return chr(ordinal)
    else:
        return unichr(ordinal)

def histogram(values, slots):
    """Frequency counts values.

    Returns:
        low, width, dict
    """
    histo = collections.defaultdict(int)

    if len(values) == 0:
        return 0, 1 / float(slots), histo

    low = math.floor(min(values))
    high = math.ceil(max(values))
    width = (high - low) / float(slots)

    for value in values:
        slot = int((value - low) / width)
        histo[slot] += 1

    return low, width, histo

def plot(slots, low, width, histo):
    chars = [unicode_chr(0x2580+n) for n in range(1,9)]
    chars = ["_"] + chars

    max_count = max([0] + list(histo.values()))

    for slot in range(slots):
        count = histo[slot]
        if max_count > 0:
            char = int(round((len(chars)-1) * (count / float(max_count))))
        else:
            char = 0
        char = chars[char]
        yield char
