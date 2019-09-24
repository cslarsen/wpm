"""
Setup script for WPM.

This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

import os
import sys
import runpy

from setuptools import setup

def get_version():
    """Reads current WPM version from disk."""
    filename = os.path.join(os.path.dirname(__file__), "wpm", "__init__.py")
    var = runpy.run_path(filename)
    return var["__version__"]

_VERSION = get_version()

setup(
    name="wpm",
    entry_points = {
        "console_scripts": ['wpm = wpm.commandline:main']
    },
    version=_VERSION,
    description="Console app for measuring typing speed in words per minute (WPM)",
    author="Christian Stigen Larsen",
    author_email="csl@csl.name",
    packages=["wpm"],
    package_dir={"wpm": "wpm"},
    package_data={"wpm": ["data/examples.json.gz"]},
    include_package_data=True,
    install_requires=(["windows-curses"] if sys.platform.startswith("win") else []),
    url="https://github.com/cslarsen/wpm",
    download_url="https://github.com/cslarsen/wpm/tarball/v%s" % _VERSION,
    license="https://www.gnu.org/licenses/agpl-3.0.html",
    long_description=open("README.rst").read(),
    install_requires=["setuptools"],
    zip_safe=True,
    test_suite="tests",
    keywords=["wpm", "typing", "typist"],
    platforms=["unix", "linux", "osx", "cygwin", "win32"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
