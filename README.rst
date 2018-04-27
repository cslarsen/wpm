wpm — measure and improve your typing speed
===========================================
|versions| |license| |pypi|

``wpm`` is a UNIX terminal program for measuring and improving your typing
speed, which is measured in words per minute (WPM). It depends only on standard
Python libraries, particularly curses, and thus works with Python 2.7, 3+, PyPy
and probably others.

Features
--------

- Over 4900 quotes in the database, shamelessly stolen from typeracerdata.com
- Extremely low typing latency!
- Timer starts when you strike the first key
- Completed text is *darkened*, helping you to focus ahead
- Keep separate stats for, e.g. type of keyboard, layout etc.
- Saves race scores in a CSV file that is a superset of TypeRacer's export
  format. Loads fine in Excel as well.
- Launches quickly in your terminal window for "in-between moments"

Demo
----

.. image:: https://asciinema.org/a/Ipk7ft1048SEMTbXzzlOo0VUb.png
  :width: 480 px
  :height: 230 px
  :alt: Screen recording of WPM in action
  :target: https://asciinema.org/a/Ipk7ft1048SEMTbXzzlOo0VUb?size=medium&autoplay=1


How to install
--------------

The recommended way is to install via PyPi

.. code:: bash

    $ pip install wpm

The above usually requires ``sudo``. If you don't want to install it
system-wide, you can use ``pip install wpm --user``.

Remember to check for upgrades with ``pip install --upgrade wpm``. You can also
install it from the source repository with

.. code:: bash

    $ python setup.py install [--user]

To just test the app without installing, type ``make run``.

How to run
----------

Just type ``wpm`` to start the program. The timer will start when you press the
first key. At any time, you can hit ESCAPE to quit.

You can backspace for the current word you're editing, if you make a mistake.
Mistakes will lower the accuracy score.

If you have problems finding the ``wpm`` file, you can also start it by typing
``python -m wpm``. You can also see options with ``python -m wpm --help``.

Calculating WPM
---------------

The WPM is calculated by dividing characters per second by five and then
multiplying that with 60. This is a well-known formula, but gives slightly
higher scores than on sites like typeracer.com. It is, however, good enough to
gauge your typing speed. And it works offline, and with your own texts.

Regarding TypeRacer, I really suggest everyone check it out. I use this program
merely to warm up before heading over to typeracer.com, where you can race
against others.

How to get the lowest typing latency
------------------------------------

Run outside of tmux, and use a really speedy terminal window. On my macOS
system, I found the best latency using the built-in Terminal.app, which easily
beats iTerm. I also found the Kitty terminal to provide very low latency.

I also feel that running it under PyPy provides a little lower latency as well,
but I haven't timed it. You can install it under PyPy with ``pypy -m pip
install wpm``.

On Linux, the ultimate typing latency is achieved if you open up one of the
virtual consoles. For example, hit CTRL+ALT+F2 and log in, set your
``TERM=xterm-color`` and run ``wpm``. Many terms also have quite a high
latency. Try using uxterm if you need to run it inside X.

Loading custom texts
--------------------

If you want to type a custom text, run

.. code:: bash

    $ wpm --load yourfile.txt

If you use ``--load``, the author will currently be empty, the title will be
the basename of the file. The text ID will be its inode, just to make them
somewhat unique, so your stats will work.

You can also bundle up several texts into a single JSON file, using ``wpm
--load-json yourfile.json``. It must have the following format:

.. code:: json

    [
      {
        "author": "Author Name",
        "title": "Title of Work",
        "text": "The text to type here ..."
        "id": 123,
      },
      ...
    ]

The ``id`` is an optional integer. If you leave it out, an increasing,
zero-based integer will be used.

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
accuracy   float    From 0 to 1, where 1 means no mistakes
rank       int      Always 1
racers     int      Always 1
text_id    int      Item number of text in given database
timestamp  str      UTC timestamp in strptime format `%Y-%m-%d %H:%M:%S.%f`
database   str      Either "default" or the basename of the file used
keyboard   str      A user supplied tag for that score
========== ======== =======================================================

Should there be any problem saving or loading the score history, it will copy
the existing file into `~/.wpm.csv.backup` and create a new one.

If you use `--keyboard=...` to specify a keyboard, the next time wpm is
launched, it will assume that this is the keyboard you are still using. Just
specify `--keyboard=...` again. The keyboard setting is really just a string
label you can use to tag races. For example, you could call the keyboard
`realforce-colemak` or `cherry-red-qwerty` and use that as a basis to perform
statistical analysis on your typing performance with various setups.

The ~/.wpmrc file
-----------------

The first time you start wpm, it writes a `.wpmrc` file to your home directory.
It contains user settings that you can change. They are given in the table
below.

============== =========================== ======= =============================================================================
Section        Name                        Default Description
-------------- --------------------------- ------- -----------------------------------------------------------------------------
curses         escdelay                         15 Time in ms to wait for follow-up key after ESC
curses         window_timeout                   20 Time in ms until giving up waiting for a keypress. If negative, wait forever.
wpm            max_quote_width                  -1 If positive, wrap text at this width
wpm            confidence_interval_percent      95 The confidence interval percentage to use for WPM and accuracy reports
xterm-256color                                     Color codes for 256-color terminals
xterm-color                                        Color codes for ordinary terminals
============== =========================== ======= =============================================================================

License
-------

Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!

.. |license| image:: https://img.shields.io/badge/license-AGPL%20v3%2B-blue.svg
    :target: https://www.gnu.org/licenses/agpl-3.0.html
    :alt: Project License

.. |versions| image:: https://img.shields.io/badge/python-2.7%2B%2C%203%2B%2C%20pypy-blue.svg
    :target: https://pypi.python.org/pypi/wpm/
    :alt: Supported Python versions

.. |pypi| image:: https://badge.fury.io/py/wpm.svg
    :target: https://badge.fury.io/py/wpm
