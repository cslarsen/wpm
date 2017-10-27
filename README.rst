wpm — console app that measures your typing speed
=================================================
|versions| |license| |pypi|

``wpm`` is a simple terminal program that measures your typing speed in words
per minute (WPM).

It uses only standard Python library (curses), has very low keyboard latency
and works at least with Python 2.7, 3+ and PyPy.

Features
--------

- Timer starts when you strike the first key
- Over 3700 quotes in the database, shamelessly stolen from typeracerdata.com
- Completed text is *darkened*, helping you to focus ahead
- Keeps separate stats for, e.g. type of keyboard, layout etc.
- Launches quickly in your terminal window for "in-between moments"
- Extremely low typing latency!

Demo
----

.. image:: https://asciinema.org/a/vJCg0dtITUAvLOD9XUY4FaYxt.png
  :width: 480 px
  :height: 230 px
  :alt: Screen recording of WPM in action
  :target: https://asciinema.org/a/vJCg0dtITUAvLOD9XUY4FaYxt?size=medium

Calculating WPM
---------------

The WPM is calculated by dividing characters per second by five and then
multiplying that with 60. This is a well-known formula, but gives slightly
higher scores than on sites like typeracer.com. It is, however, good enough to
gauge your typing speed. And it works offline, and with your own texts.


How to get the lowest typing latency
------------------------------------

On my machine, wpm *easily* beats typeracer.com on latency. For the absolutely
best experience, I recommend the following: Use Terminal.app that comes with
macOS, don't use tmux or screen, and run with pypy. Try it, and you'll
definitely feel that every single key you strike is instantly updated on the
screen.

This comment is not meant to disregard TypeRacer, which I do love. But it's
nice to have a little terminal program to practice whenever you have a minute
to spare (for example, while compiling).

How to install
==============

The recommended way is to install via PyPi

.. code:: bash

    $ pip install wpm

But you can also install from the source with

.. code:: bash

    $ python setup.py install [--user]

To just test the app without installing, type ``make run``.

How to run
==========

Just type ``wpm`` to start the program. The timer will start when you press the
first key. At any time, you can hit ESCAPE to quit.

You can backspace for the current word you're editing, if you make a mistake.
Mistakes will lower the accuracy score.

If you have problems finding the ``wpm`` file, you can also start it by typing
``python -m wpm``. You can also see options with ``python -m wpm --help``.

If you want to type a custom text, run

.. code:: bash

    $ wpm --load yourfile.txt

You can also bundle up several texts into a single JSON file, using ``wpm
--load-json yourfile.json``. It must have the following format:

.. code:: json

    [
      {
        "author": "Author Name",
        "title": "Title of Work",
        "text": "The text to type here ..."
      },
      ...
    ]

License
=======

Copyright 2017 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.

.. |license| image:: https://img.shields.io/badge/license-GPL%20v3%2B-blue.svg
    :target: http://www.gnu.org/licenses/old-licenses/gpl-3.en.html
    :alt: Project License

.. |versions| image:: https://img.shields.io/badge/python-2.7%2B%2C%203%2B%2C%20pypy-blue.svg
    :target: https://pypi.python.org/pypi/wpm/
    :alt: Supported Python versions

.. |pypi| image:: https://badge.fury.io/py/wpm.svg
    :target: https://badge.fury.io/py/wpm
