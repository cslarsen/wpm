"""
Development features for wpm.

To enable, set the environment variable ``WPM_DEVFEAUTRES=feature1:feature2``.
"""

import os

WPM_DEVFEATURES =os.getenv("WPM_DEVFEATURES", "").lower().split(":")

histogram = "histogram" in WPM_DEVFEATURES
