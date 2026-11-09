#!/usr/bin/env python3
"""
recall - a plain text place for what you would otherwise forget.

The design rules, and the reason for each:

  * One file, plain text, yours.  Any editor opens it.  If this program
    disappears tomorrow, the journal does not.  It is not a database.

  * It only ever appends.  It never rewrites the file, so it cannot lose
    what you wrote.  There is no "save" that can fail halfway.

  * No tags, no moods, no scores, no streaks, no summaries.  Every one of
    those imposes a reading that a future you may not share.  Facts age;
    verdicts do not.

  * Resurfacing beats searching.  You cannot search for what you have
    forgotten, so the tool shows you things instead of waiting to be asked.

  * Asking is easier than facing a blank page.  A narrow question can be
    answered in five seconds; "write about your day" cannot be answered at
    all.

Usage:
    recall                 answer a few short questions
    recall add <text>      write one line
    recall day             what you wrote on this day in earlier years
    recall random          one entry, chosen at random
    recall find <words>    entries containing words
    recall count           how much is there
    recall edit            open the file in your editor
"""

import datetime
import os
import random
import re
import subprocess
import sys


ENTRY_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})")
DEFAULT_PATH = "~/diary/journal.md"

QUESTIONS = [
    "What happened?",
    "Who was there?",
    "What did you notice?",
    "What would you otherwise forget?",
]

HELP = """recall - a plain text place for what you would otherwise forget.

  recall                 answer a few short questions
  recall add <text>      write one line
  recall day             what you wrote on this day in earlier years
  recall random          one entry, chosen at random
  recall find <words>    entries containing words
  recall count           how much is there
  recall where           where the file is, and how to keep it
  recall edit            open the file in your editor

  --file <path>          use a different journal file
  --on <date>            write to a different day, like 2026-10-14

Your journal is one plain text file:

  %s

Nothing is ever rewritten. The program only appends, so it cannot lose
what you wrote. If the program disappears, the journal does not.
"""


# ---------------------------------------------------------------------------
# the file
# ---------------------------------------------------------------------------

def journal_path():
    return os.path.expanduser(os.environ.get("RECALL_FILE", DEFAULT_PATH))


def weekday(iso):
    try:
        return datetime.date.fromisoformat(iso).strftime("%A")
    except ValueError:
        return ""


def read_entries(path):
    """Every entry, oldest first, as (date, text)."""
    if not os.path.exists(path):
        return []
    entries = []
    date = None
    body = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            found = ENTRY_RE.match(line)
            if found:
                if date is not None:
                    entries.append((date, "\n".join(body).strip()))
                date = found.group(1)
                body = []
            elif date is not None:
                body.append(line.rstrip("\n"))
    if date is not None:
        entries.append((date, "\n".join(body).strip()))
    # Entries are written in whatever order they were typed. Kept in date
    # order here so a backdated entry still counts as an old one. The sort
    # is stable, so two entries on the same day stay in the order written.
    entries.sort(key=lambda pair: pair[0])
    return entries


def append_entry(path, date, text):
    """Add one entry.  Appends only; never rewrites what is there."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("\n## %s %s\n\n" % (date, weekday(date)))
        handle.write(text.strip() + "\n")


def entries_on(entries, month_and_day, before=None):
    found = []
    for date, text in entries:
        if date[5:] == month_and_day:
            if before is None or date < before:
                found.append((date, text))
    return found


def show(date, text):
    print()
    print("  ## %s %s" % (date, weekday(date)))
    print()
    for line in text.split("\n"):
        print("      " + line)
    print()


# ---------------------------------------------------------------------------
# the things you can do
# ---------------------------------------------------------------------------

def add(path, text, on=None):
    today = on or datetime.date.today().isoformat()
    append_entry(path, today, text)
    print("  saved.")

    earlier = entries_on(read_entries(path), today[5:], before=today)
    if earlier:
        print()
        print("  On this day:")
        for date, old in earlier:
            show(date, old)


def ask(path, on=None):
    date = on or datetime.date.today().isoformat()
    print()
    print("  %s, %s" % (weekday(date), date))
    print()
    print("  Answer any of these, or none.")
    print("  Enter on its own skips a question. Answer nothing and nothing")
    print("  is saved.")
    print()

    answers = []
    for question in QUESTIONS:
        try:
            reply = input("  %s\n  > " % question).strip()
        except EOFError:
            reply = ""
        print()
        if reply:
            answers.append(reply)

    if not answers:
        print("  nothing saved.")
        return
    add(path, "\n".join(answers), on=on)


def day(path):
    month_and_day = datetime.date.today().isoformat()[5:]
    earlier = entries_on(read_entries(path), month_and_day)
    if not earlier:
        print("  nothing from this day in earlier years.")
        return
    for date, text in earlier:
        show(date, text)


def pick(path):
    entries = read_entries(path)
    if not entries:
        print("  nothing yet.")
        return
    date, text = random.choice(entries)
    print("  (one of %d)" % len(entries))
    show(date, text)


def find(path, words):
    needle = " ".join(words).lower()
    hits = [(d, t) for d, t in read_entries(path) if needle in t.lower()]
    if not hits:
        print("  nothing matches %r." % needle)
        return
    print("  %d found. Most recent:" % len(hits))
    for date, text in hits[-5:]:
        show(date, text)


def count(path):
    entries = read_entries(path)
    if not entries:
        print("  nothing yet.")
        return
    dates = sorted(d for d, _ in entries)
    first, last = dates[0], dates[-1]
    try:
        span = (datetime.date.fromisoformat(last)
                - datetime.date.fromisoformat(first)).days + 1
    except ValueError:
        span = 0

    print()
    print("  %d entries" % len(entries))
    print("  %d different days written" % len(set(dates)))
    print("  %s to %s" % (first, last))
    if span:
        print("  %d days in that stretch" % span)
    print()
    print("  %s" % path)
    print()


def edit(path):
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if not editor:
        print("  no editor set. Either do:")
        print("      export EDITOR=nano")
        print("  or just open this file yourself:")
        print("      %s" % path)
        return
    subprocess.call([editor, path])


def where(path):
    entries = read_entries(path)
    print()
    print("  %s" % path)
    if os.path.exists(path):
        print("  the file is there. %d entries." % len(entries))
    else:
        print("  nothing written yet -- it appears the first time you save.")
    print()
    print("  To keep it when you change computer, put it in a folder that")
    print("  already syncs -- iCloud Drive, Dropbox, OneDrive -- and point")
    print("  at it from anywhere:")
    print()
    print("      export RECALL_FILE=~/Dropbox/journal.md")
    print("      python3 recall.py --file ~/Dropbox/journal.md add ...")
    print()
    print("  The file is plain text. Any editor opens it, and if this")
    print("  program ever goes away you can keep writing in it by hand.")
    print()


# ---------------------------------------------------------------------------

def main(argv):
    args = argv[1:]
    path = journal_path()

    if "--file" in args:
        index = args.index("--file")
        try:
            path = os.path.expanduser(args[index + 1])
        except IndexError:
            sys.stderr.write("  --file needs a path after it\n")
            return 2
        del args[index:index + 2]

    on = None
    if "--on" in args:
        index = args.index("--on")
        try:
            on = args[index + 1]
        except IndexError:
            sys.stderr.write("  --on needs a date after it, like 2026-10-14\n")
            return 2
        del args[index:index + 2]
        try:
            datetime.date.fromisoformat(on)
        except ValueError:
            sys.stderr.write("  --on needs a date like 2026-10-14, "
                             "not %r\n" % on)
            return 2

    if not args:
        if not sys.stdin.isatty():
            piped = sys.stdin.read().strip()
            if piped:
                add(path, piped, on=on)
                return 0
        ask(path, on=on)
        return 0

    command = args[0]
    rest = args[1:]

    if command in ("add", "a", "write"):
        if rest:
            add(path, " ".join(rest), on=on)
        elif not sys.stdin.isatty():
            piped = sys.stdin.read().strip()
            if piped:
                add(path, piped, on=on)
            else:
                print("  nothing to save.")
        else:
            ask(path, on=on)
    elif command in ("day", "on"):
        day(path)
    elif command in ("random", "rand", "r"):
        pick(path)
    elif command == "find":
        if rest:
            find(path, rest)
        else:
            print("  find needs something to look for.")
    elif command in ("count", "stats"):
        count(path)
    elif command == "where":
        where(path)
    elif command == "edit":
        edit(path)
    elif command in ("help", "-h", "--help"):
        sys.stdout.write(HELP % path)
    else:
        sys.stderr.write(HELP % path)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
