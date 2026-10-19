#!/usr/bin/env python3
"""
Draw the word NAATLABS in your GitHub contribution graph.

How it works:
- The graph has 7 rows (Sunday to Saturday) and ~53 columns (weeks).
- Every "#" in the letters below = one day with commits.
- The script makes empty commits with old dates in a git repo.

Usage:
  python3 naatlabs_graph.py --preview              # only shows the drawing
  python3 naatlabs_graph.py --year 2015            # makes the commits
  python3 naatlabs_graph.py --year 2015 --commits 20
"""

import argparse
import datetime as dt
import os
import subprocess

FONT = {
    "N": ["#...#",
          "##..#",
          "##..#",
          "#.#.#",
          "#..##",
          "#..##",
          "#...#"],
    "A": [".###.",
          "#...#",
          "#...#",
          "#####",
          "#...#",
          "#...#",
          "#...#"],
    "T": ["#####",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#.."],
    "L": ["#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#####"],
    "B": ["####.",
          "#...#",
          "#...#",
          "####.",
          "#...#",
          "#...#",
          "####."],
    "S": [".####",
          "#....",
          "#....",
          ".###.",
          "....#",
          "....#",
          "####."],
}

WORD = "NAATLABS"


def build_grid(word):
    """Return 7 strings (rows), one column per week."""
    rows = [""] * 7
    for i, letter in enumerate(word):
        for r in range(7):
            rows[r] += FONT[letter][r]
            if i < len(word) - 1:
                rows[r] += "."  # space between letters
    return rows


def first_sunday(year):
    d = dt.date(year, 1, 1)
    while d.weekday() != 6:  # 6 = Sunday
        d += dt.timedelta(days=1)
    return d


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=2015,
                   help="Year to draw in (use an empty year)")
    p.add_argument("--offset", type=int, default=2,
                   help="Empty weeks before the word starts")
    p.add_argument("--commits", type=int, default=15,
                   help="Commits per day (more = darker green)")
    p.add_argument("--preview", action="store_true",
                   help="Only print the drawing, make no commits")
    args = p.parse_args()

    grid = build_grid(WORD)
    width = len(grid[0])

    print(f"Word width: {width} weeks (graph has ~52)\n")
    for row in grid:
        print(row.replace("#", "█").replace(".", "·"))
    print()

    if args.preview:
        return

    if not os.path.isdir(".git"):
        raise SystemExit("Run this inside a new git repo (git init first).")

    start = first_sunday(args.year) + dt.timedelta(weeks=args.offset)
    last = start + dt.timedelta(weeks=width - 1, days=6)
    if last.year != args.year:
        raise SystemExit("The word does not fit in this year. Use a smaller --offset.")

    total = 0
    for col in range(width):
        for row in range(7):
            if grid[row][col] != "#":
                continue
            day = start + dt.timedelta(weeks=col, days=row)
            stamp = f"{day.isoformat()}T12:00:00-06:00"
            env = dict(os.environ,
                       GIT_AUTHOR_DATE=stamp,
                       GIT_COMMITTER_DATE=stamp)
            for n in range(args.commits):
                subprocess.run(
                    ["git", "commit", "--allow-empty", "-q",
                     "-m", f"NAATLABS {day} #{n + 1}",
                     "-m", "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
                           "Claude-Session: https://claude.ai/code/session_014M8ueiR9cqYQnE8fY2usHY"],
                    env=env, check=True)
                total += 1
    print(f"Done: {total} commits from {start} to {last}.")
    print("Now run: git push -u origin main")


if __name__ == "__main__":
    main()
