WPM
===

A terminal program that measures your typing speed in words per minute (WPM).

The WPM is calculated using the usual formula CPS/5, where CPS is characters
per second, or the number of correct characters you've typed so far, divided by
elapsed time.

Compared to sites like typeracer.com, this WPM is a little bit higher, but is a
very common way to gauge your typing speed.

How to install
==============

::

    $ pip install wpm

How to run
==========

Just type::

    $ wpm

You can also train a single custom text. In that case, just do::

    $ wpm --load yourfile.txt

If you want to bundle up several texts into one file, just create a JSON file
with the following format::

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
      },

      ...
    ]

You load JSON files by doing::

    $ wpm --load-json yourfile.json

Author and license
==================

Copyright 2017 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later.
