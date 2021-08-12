"""
This file is part of the wpm software.
Copyright 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

def wpm_to_cps(wpm):
    """Converts WPM to CPS (characters per second)."""
    return (wpm/60.0)*5.0

def wpm_to_cpm(wpm):
    """Converts WPM to CPM (characters per minute)."""
    return wpm*5.0
