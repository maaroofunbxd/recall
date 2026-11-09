#!/usr/bin/env python3
"""
Tests for recall.

    python3 tests.py

Everything runs against a throwaway journal file, so your real one is never
touched.
"""

import datetime
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RECALL = os.path.join(HERE, "recall.py")
PYTHON = sys.executable

TODAY = datetime.date.today()
MONTH_DAY = TODAY.isoformat()[5:]
THIS_DAY_2019 = "2019-" + MONTH_DAY
THIS_DAY_2022 = "2022-" + MONTH_DAY

SAMPLE = """# Journal

## 2019-01-03

Cold. Walked to the shop. The man at the counter was arguing about football.

## %s

She had the fish.

## 2021-11-20

Long day. Finished the book, did not like the ending.

## %s

Rained all afternoon.
""" % (THIS_DAY_2019, THIS_DAY_2022)


def run(journal, *args, **kwargs):
    env = dict(os.environ, RECALL_FILE=journal)
    return subprocess.run(
        [PYTHON, RECALL] + list(args),
        input=kwargs.get("stdin"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        env=env,
    )


def main():
    folder = tempfile.mkdtemp(prefix="recall-test-")
    journal = os.path.join(folder, "journal.md")
    with open(journal, "w") as handle:
        handle.write(SAMPLE)

    passed = 0
    failed = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print("ok   %s" % label)
        else:
            failed += 1
            print("FAIL %s\n%s" % (label, detail))

    result = run(journal, "count")
    check("count reports every entry",
          "4 entries" in result.stdout, result.stdout)

    result = run(journal, "day")
    check("day finds this date in earlier years",
          THIS_DAY_2019 in result.stdout
          and THIS_DAY_2022 in result.stdout
          and "She had the fish." in result.stdout,
          result.stdout)

    result = run(journal, "find", "fish")
    check("find looks inside entries",
          "She had the fish." in result.stdout, result.stdout)

    result = run(journal, "find", "football")
    check("find works on older entries too",
          "arguing about football" in result.stdout, result.stdout)

    result = run(journal, "random")
    check("random shows one of the entries",
          "one of 4" in result.stdout, result.stdout)

    before = open(journal).read()
    result = run(journal, "add", "Ate", "outside.")
    after = open(journal).read()
    check("add appends the words",
          "Ate outside." in after, after)
    check("add writes today's date",
          TODAY.isoformat() in after, after)
    check("add only appends, never rewrites",
          after.startswith(before), after)
    check("add shows this day in earlier years",
          "She had the fish." in result.stdout, result.stdout)

    before = open(journal).read()
    result = run(journal, "add", stdin="piped in from somewhere\n")
    after = open(journal).read()
    check("add reads piped text",
          "piped in from somewhere" in after, after)
    check("piped add only appends too",
          after.startswith(before), after)

    result = run(journal, "count")
    check("count sees the new entries",
          "6 entries" in result.stdout, result.stdout)

    result = run(journal)
    check("running with no arguments asks questions",
          "What happened?" in result.stdout, result.stdout)

    result = run(journal, stdin="\n\n\n\n")
    check("answering nothing saves nothing",
          "nothing saved" in result.stdout, result.stdout)

    check("nothing was added by the empty session",
          "6 entries" in run(journal, "count").stdout)

    result = run(journal, "find", "nothingmatchesthis")
    check("find says so when there is nothing",
          "nothing matches" in result.stdout, result.stdout)

    before = open(journal).read()
    run(journal, "--on", "2001-02-03", "add", "A backdated entry.")
    after = open(journal).read()
    check("--on writes to the day you name",
          "## 2001-02-03" in after, after)
    check("--on only appends", after.startswith(before), after)
    check("a backdated entry still counts as old",
          run(journal, "count").stdout.index("2001-02-03")
          < run(journal, "count").stdout.index("2026"),
          run(journal, "count").stdout)

    result = run(journal, "--on", "yesterday", "add", "nope")
    check("--on refuses a date it cannot read",
          result.returncode == 2 and "2026-10-14" in result.stderr,
          result.stderr)

    shutil.rmtree(folder)
    print()
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
