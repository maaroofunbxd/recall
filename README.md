# recall

One plain text file for the things you would otherwise forget.

```
$ recall
  Thursday, 2024-06-11

  Answer any of these, or none.
  Enter on its own skips a question.
  Answer nothing and nothing is saved.

  What happened?
  > walked home the long way, bought peaches

  Who was there?
  >

  What did you notice?
  > the man at the stall said they'd be better next week

  What would you otherwise forget?
  >

  saved.

  On this day:

  ## 2019-06-11

      Warm. Took the long way home past the market. Bought peaches, they
      were not good. The man at the stall said they would be better next
      week. He was right.
```

That last part is the whole point. You write today, and it hands you back
what you wrote on this day in 2019.

## Using it

```sh
python3 recall.py                 # answer a few short questions
python3 recall.py add <text>      # write one line
python3 recall.py day             # this day in earlier years
python3 recall.py random          # one entry, at random
python3 recall.py find <words>    # entries containing words
python3 recall.py count           # how much is there
python3 recall.py edit            # open the file in your editor
```

Make it one letter, in your shell's startup file:

```sh
alias r="python3 /path/to/recall/recall.py"
```

Then `r` is the whole interface, and `r day` is the good one.

Your journal lives at `~/diary/journal.md`. The folder is made for you the
first time you save something. Set `RECALL_FILE` to put it somewhere else.

## How you actually use it, day to day

Most days it is one line:

```sh
r add walked home the long way, bought peaches
```

That is the whole thing. Three seconds, and it is saved.

When you have more to say, or you do not know what to say, type `r` on its
own. It asks four short questions, you answer whichever ones you feel like,
and pressing enter on its own skips one. Answer none and nothing is saved.

**Missed a day?** Nothing breaks — there is no streak to lose. If you want to
fill it in, name the day:

```sh
r --on 2026-10-13 add forgot to write this yesterday
```

**Longer entries, or fixing a typo:** `r edit` opens the file in your editor.

**Once in a while, let it surprise you:** `r random`, or `r day` for what you
wrote on this date in earlier years.

There is no right frequency. Once a week for thirty years is a better journal
than once a day for a month.

## What to write

Not a summary of the day — that decays immediately. Write like a **witness**,
not a narrator:

| instead of | write |
|---|---|
| "A good day." | "Warm. Took the long way home past the market." |
| "Saw an old friend." | "Ran into A. outside the station, she had a new coat." |
| "Bad day at work." | "Spent two hours on a problem that turned out to be a typo." |

The second kind is worthless as meaning and priceless as a hook. In thirty
years "she had the fish" is still true. "The best day of my life" is
embarrassing in three.

You are not writing for meaning. You are leaving something specific enough
that a stranger — you, later, having forgotten everything — can find their
way back.

## What it will never do

- **No tags, moods, scores, or streaks.** Every one of those imposes a
  reading that a future you may not share, and a streak turns a nice habit
  into a debt. If you skip three months, nothing is broken.
- **No summaries, no analysis.** It does not know what any of it means and
  will not pretend to.
- **No rewriting, ever.** It only appends. There is no save that can fail
  halfway and no operation that can corrupt what is already there.
- **No database, no account, no sync, no network.** One file on your disk.

## Taking it with you

Your journal is one file. The program is 300 lines and disposable. That
split is the whole answer to "what if I don't have this computer any more".

**The file.** Put it in a folder that already syncs — iCloud Drive, Dropbox,
OneDrive, whatever you use — and point recall at it:

```sh
export RECALL_FILE=~/Dropbox/journal.md
alias r="python3 ~/bin/recall.py"
```

Now it is on every machine that syncs, and backed up without you having to
think about it. Run `recall where` to see where it currently is.

**The phone.** This is the real gap, and no code fixes it. Use any editor
that opens a file in that synced folder — Obsidian, iA Writer, or anything
that reads plain text. Type the date, then write:

```
## 2026-10-15

Rained. Missed the bus, walked instead.
```

That is a complete, valid entry. No tool required. It is exactly why the
format is what it is: **the file is writable without the program.**

**A borrowed or new computer.** Copy the one file, or just point at the
synced one:

```sh
python3 recall.py --file ~/Dropbox/journal.md day
```

**Never lose it.** A synced folder means it is already in the cloud. If you
want full history — every version, for ever — put it in a private git
repository and commit it once a month.

**The insurance is the format.** No schema, no version number, no database.
Dates and UTF-8 text. Anything can read it, including a person.

## Why it will still work in thirty years

The journal is plain text. Any editor opens it. `grep` reads it. If Python
disappears, the file is unaffected — you can keep writing in it by hand.

The program itself is one file with no dependencies beyond Python 3, which is
already on every Mac and most Linux machines. It is short enough to read in
one sitting and rewrite from memory if you ever have to.

Recurring software dies of format rot, dependency rot, and maintenance cost
exceeding value in a busy month. Everything above is aimed at those three.
