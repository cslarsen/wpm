wpm — console app that measures your typing speed
=================================================
|versions| |license| |pypi|

WPM is a simple terminal program that measures your typing speed in words per
minute (WPM).

The WPM is calculated by taking characters per second (CPS) and dividing by
five. That gives a slightly higher score than on sites than typeracer.com, but
is good enough to gauge your typing speed.

How to install
==============

The recommended way is to install via PyPi

.. code:: bash

    $ pip install wpm

But you can also do a local installation with

.. code:: bash

    $ python setup.py install [--user]

How to run
==========

Just type

.. code:: bash

    $ wpm

To cancel typing, just hit the ESCAPE key.

You can also train a single custom text. In that case, just do

.. code:: bash

    $ wpm --load yourfile.txt

If you want to bundle up several texts into one file, just create a JSON file
with the following format

.. code:: json

    [
      {
        "author": "Author Name",
        "title": "Title of Work",
        "text": "The text to type here ..."
      },

      {
        "author": "Author Name",
        "title": "Title of Work",
        "text": "The text to type here ..."
      }
    ]

You load your JSON files with

.. code:: bash

    $ wpm --load-json yourfile.json

License
=======

Copyright 2017 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.

.. |license| image:: https://img.shields.io/badge/license-GPL%20v3%2B-blue.svg
    :target: http://www.gnu.org/licenses/old-licenses/gpl-3.en.html
    :alt: Project License

.. |versions| image:: https://img.shields.io/badge/python-2.7%2B%2C%203%2B-blue.svg
    :target: https://pypi.python.org/pypi/wpm/
    :alt: Supported Python versions

.. |pypi| image:: https://badge.fury.io/py/wpm.svg
    :target: https://badge.fury.io/py/wpm
