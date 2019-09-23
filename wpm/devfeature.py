"""
Development features for wpm.

To enable, set the environment variable ``WPM_DEVFEAUTRES=feature1:feature2``.

This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

import os

DEVFEATURES = os.getenv("WPM_DEVFEATURES", "").lower().split(":")

histogram = "histogram" in DEVFEATURES
