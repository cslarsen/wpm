"""
Contains custom exception types.

This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

class WpmError(RuntimeError):
    """General WPM errors."""
    pass

class ConfigError(WpmError):
    """Incorrect .wpmrc option."""
    pass
