wpm — measure and improve your typing speed
===========================================
|versions| |license| |pypi|

``wpm`` is a UNIX terminal program for measuring and improving your typing
speed, which is measured in words per minute (WPM). It depends only on standard
Python libraries, particularly curses, and thus works with Python 2.7, 3+, PyPy
and probably others.

Features
--------

- Over 3700 quotes in the database, shamelessly stolen from typeracerdata.com
- Extremely low typing latency!
- Timer starts when you strike the first key
- Completed text is *darkened*, helping you to focus ahead
- Keeps separate stats for, e.g. type of keyboard, layout etc.
- Saves race scores in a CSV file that is compatible with Excel and TypeRacer
- Launches quickly in your terminal window for "in-between moments"

Demo
----

.. image:: https://asciinema.org/a/JHgfVrf1jIxxl099hdnRcG4Lf.png
  :width: 480 px
  :height: 230 px
  :alt: Screen recording of WPM in action
  :target: https://asciinema.org/a/JHgfVrf1jIxxl099hdnRcG4Lf?size=medium&autoplay=1

Calculating WPM
---------------

The WPM is calculated by dividing characters per second by five and then
multiplying that with 60. This is a well-known formula, but gives slightly
higher scores than on sites like typeracer.com. It is, however, good enough to
gauge your typing speed. And it works offline, and with your own texts.


How to get the lowest typing latency
------------------------------------

Run outside of tmux, and use a really speedy terminal window. On my macOS
system, I found the best latency using the built-in Terminal.app, which easily
beats iTerm. I also found the Kitty terminal to provide very low latency.

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

Format of race history
----------------------

wpm will save scores in a CSV file in `~/.wpm.csv`. This file can be loaded
directly into Excel. It uses the same format as TypeRacer, with the addition of
a few extra columns at the end. That means is should be possible to use
existing TypeRacer score history tools with this file with minor modifications.

The column order is:

========== ======== =======================================================
Column     Datatype Explanation
---------- -------- -------------------------------------------------------
race       int      Race number, always increasing and tied to timestamp
wpm        float    The average WPM for that quote that single time
accuracy   float    0 to 1
rank       int      Always 1
racers     int      Always 1
text_id    int      Item number of text in given database
timestamp  str      UTC timestamp in strptime format `%Y-%m-%d %H:%M:%S.%f`
database   str      Either "default" or the basename of the file used
keyboard   str      A user supplied, arbitrary for that score
========== ======== =======================================================

Should there be any problem saving or loading the score history, it will copy
the existing file into `~/.wpm.csv.backup`.

If you use `--keyboard=...` to specify a keyboard, the next time wpm is
launched, it will assume that this is the keyboard you are still using. Just
specify `--keyboard=...` again. The keyboard setting is really just a string
label you can use to tag races. For example, you could call the keyboard
`realforce-colemak` or `cherry-red-qwerty` and use that as a basis to perform
statistical analysis on your typing performance with various setups.

License
=======

Copyright 2018 Christian Stigen Larsen

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
