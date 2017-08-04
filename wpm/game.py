#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Measures your typing speed in words per minute (WPM).
"""

import codecs
import json
import random
import time
import urwid

def load(filename):
    """Loads texts from JSON file."""
    with codecs.open(filename, encoding="utf-8") as f:
        return json.load(f)

class Game(object):
    def __init__(self, texts):
        self.texts = texts
        self.ignore_next_key = False
        self.quote = random.choice(self.texts)
        self.text = self.quote["text"].strip().replace("  ", " ")
        self.start = None
        self.position = 0
        self.incorrect = 0
        self.total_incorrect = 0
        self._edit = ""
        self.scores = []
        self.average = 0

        self.txt_stats = urwid.Text(self.get_stats(), align="left")
        self.txt_text = urwid.Text("")
        self.txt_author = urwid.Text("", align="left")
        self.txt_edit = urwid.Text("")
        self.edit_buffer = ""
        self.txt_status = urwid.Text(("status",
            "Start typing or hit SPACE for another text or hit ESC to quit"))
        self.filler = urwid.Filler(
            urwid.Pile([
                self.txt_stats,
                urwid.Divider(),
                self.txt_text,
                urwid.Divider(),
                self.txt_author,
                urwid.Divider(),
                self.txt_edit,
                urwid.Divider(),
                self.txt_status,
            ]),
            valign="top",
            height="pack")

        self.tab_spaces = None

    def set_tab_spaces(self, spaces):
        self.tab_spaces = spaces

    def update(self):
        if self.finished:
            if self.start is not None:
                self.scores.append(self.wpm)
                self.average = sum(self.scores)/float(len(self.scores))
            self.txt_status.set_text(("status",
                "Press any key to continue, CTRL+R to redo, SPACE for another text, ESC to quit"))
        self.update_stats()
        self.update_text()
        if not self.finished:
            self.loop.event_loop.alarm(0.01, self.update)

    def run(self):
        self.loop = urwid.MainLoop(
                self.filler,
                unhandled_input=self.handle_key,
                screen=urwid.raw_display.Screen(),
                handle_mouse=False,
                palette=[
                    ("stats", "bold,dark green", "default", "default"),
                    ("cursor", "bold", "dark green", "underline"),
                    ("normal", "default", "default", "white"),
                    ("done", "dark gray", "default", "bold"),
                    ("wrong", "white,bold", "dark red", "bold,underline"),
                    ("edit", "bold,dark gray", "default", "white"),
                    ("status", "bold,default", "default", "default"),
                    ("author", "dark gray", "default", "default")
                ])
        try:
            self.update()
            self.loop.run()
        except KeyboardInterrupt:
            raise urwid.ExitMainLoop()

    @property
    def elapsed(self):
        """Elapsed game round time."""
        if self.start is None:
            return 0
        return time.time() - self.start

    @property
    def wpm(self):
        """Words per minute."""
        if self.start is None:
            return 0
        value = (60.0 * self.position / 5.0) / self.elapsed
        if value > 1000:
            # Happens at start of match. Keep it to three digits.
            value = 999
        return value

    @property
    def cps(self):
        """Characters per second."""
        if self.start is None:
            return 0
        value = float(self.position) / self.elapsed
        if value > 99:
            # As for WPM, clamp at 99
            value = 99
        return value

    @property
    def accuracy(self):
        if self.start is None:
            return 0
        n = len(self.text)
        i = self.total_incorrect
        return float(n) / (n+i)

    def get_stats(self):
        return "%3.0f wpm   %4.1f cps   %5.1fs   %5.1f%% acc   %3.0f avg wpm" % (self.wpm,
                self.cps, self.elapsed, 100.0*self.accuracy, self.average)

    def update_text(self):
        p = self.position
        i = self.incorrect

        content = [
            ("done", self.text[:p]),
            ("cursor", self.text[p:p+1]),
            ("wrong", self.text[p:p+1+i]),
            ("normal", self.text[p+1+i:])
        ]

        if i == 0:
            # Bug in urwid set_text? Printing an emptry string seems to mess up
            # everything (e.g. ("wrong", "") => rest of line won't print
            del content[2]

        if self.incorrect > 0:
            del content[1]

        self.txt_text.set_text(content)
        if len(self.quote["author"]) + len(self.quote["title"]) > 0:
            self.txt_author.set_text(("author",
                u"    — %s, %s" % (self.quote["author"], self.quote["title"])))
        else:
            self.txt_author.set_text("")

    @property
    def finished(self):
        return self.incorrect == 0 and (self.position == len(self.text))

    def update_stats(self):
        self.txt_stats.set_text(("stats", self.get_stats()))

    @property
    def edit_buffer(self):
        return self._edit

    @edit_buffer.setter
    def edit_buffer(self, value):
        self._edit = value
        self.txt_edit.set_text(("edit", "> " + self._edit))

    def reset(self, new_quote=True):
        self.start = None
        self.position = 0
        self.incorrect = 0
        self.total_incorrect = 0
        self.edit_buffer = ""
        self.txt_status.set_text("")
        if new_quote:
            self.quote = random.choice(self.texts)
            self.text = self.quote["text"].strip().replace("  ", " ")
        self.ignore_next_key = True

    def handle_key(self, key):
        if (self.finished or self.start is None) and key == "ctrl r":
            self.reset(new_quote=False)
            self.update()
            self.ignore_next_key = False
            return

        if self.finished or (self.start is None and key == " "):
            self.reset()
            self.update()

        if key == "esc":
            if self.start is not None:
                # Escape during typing gets you back to the "menu"
                self.incorrect = 0
                self.position = len(self.text)
                self.start = None
                self.update()
                return
            raise urwid.ExitMainLoop()

        if self.ignore_next_key:
            self.ignore_next_key = False
            return

        if key == "backspace":
            if self.incorrect > 0:
                self.incorrect -= 1
            elif len(self.edit_buffer) > 0:
                self.position -= 1
            self.edit_buffer = self.edit_buffer[:-1]
            return

        # Start recording upon first ordinary key press
        if self.start is None:
            self.start = time.time()
            self.txt_status.set_text("")

        # Correct key at correct location?
        if len(key) == 1:
            self.edit_buffer += key

        if key == "enter":
            key = "\n"
        elif key == "tab" and self.tab_spaces is not None:
            key = " "*self.tab_spaces
        elif len(key) > 1:
            return

        if (self.incorrect == 0 and
                self.text[self.position:self.position+len(key)] == key):
            self.position += len(key)
            if key.startswith(" ") or key == "\n":
                self.edit_buffer = ""
        else:
            self.incorrect += 1
            self.total_incorrect += 1
