#!/usr/bin/env python3
"""Tiny helper for a genuine daily LeetCode practice repo.

The solving is yours — this just removes the busywork so committing daily is easy.

Commands:
  python3 lc.py new <number> <slug> [difficulty] [lang]
      Scaffold solutions/<NNNN>-<slug>/ with a solution + notes template,
      then refresh the README progress table.
      difficulty: easy | medium | hard   (default: medium)
      lang:       py | cpp | java         (default: py)

  python3 lc.py sync
      Rescan solutions/ and rebuild the README progress table.

Examples:
  python3 lc.py new 1 two-sum easy
  python3 lc.py new 146 lru-cache hard cpp
  python3 lc.py sync
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOL = ROOT / "solutions"
README = ROOT / "README.md"

START = "<!-- PROGRESS:START -->"
END = "<!-- PROGRESS:END -->"

LANG_EXT = {"py": "py", "cpp": "cpp", "java": "java"}
DIFF_LABEL = {"easy": "🟢 Easy", "medium": "🟡 Medium", "hard": "🔴 Hard"}

SOLUTION_TEMPLATES = {
    "py": '''"""{num}. {title}
LeetCode: https://leetcode.com/problems/{slug}/
"""
from typing import List  # noqa: F401  (handy for LeetCode signatures)


class Solution:
    def solve(self):
        # TODO: implement
        raise NotImplementedError


if __name__ == "__main__":
    # Scratch space to try your solution on the examples.
    print(Solution().solve())
''',
    "cpp": '''// {num}. {title}
// LeetCode: https://leetcode.com/problems/{slug}/
#include <bits/stdc++.h>
using namespace std;

class Solution {{
public:
    // TODO: implement
}};

int main() {{
    // Scratch space to try your solution on the examples.
    return 0;
}}
''',
    "java": '''// {num}. {title}
// LeetCode: https://leetcode.com/problems/{slug}/
class Solution {{
    // TODO: implement
}}
''',
}

NOTES_TEMPLATE = '''# {num}. {title}

- **Link:** https://leetcode.com/problems/{slug}/
- **Difficulty:** {difficulty}
- **First solved:** {today}

## Approach
_Explain your idea in plain words — what pattern is this (two pointers, hashing,
DP, BFS, ...), and why it works._

## Complexity
- **Time:** O(?)
- **Space:** O(?)

## Mistakes / gotchas
- _What tripped you up? Edge cases you missed?_

## Retry
- [ ] Redo this from scratch in ~1 week without looking.
'''


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def folder_name(number: int, slug: str) -> str:
    return f"{number:04d}-{slug}"


def cmd_new(args: list[str]) -> None:
    if len(args) < 2:
        die("usage: python3 lc.py new <number> <slug> [difficulty] [lang]")
    try:
        number = int(args[0])
    except ValueError:
        die("<number> must be an integer, e.g. 1")
    slug = args[1].strip().lower()
    difficulty = (args[2].lower() if len(args) > 2 else "medium")
    lang = (args[3].lower() if len(args) > 3 else "py")

    if difficulty not in DIFF_LABEL:
        die("difficulty must be one of: easy, medium, hard")
    if lang not in LANG_EXT:
        die("lang must be one of: py, cpp, java")

    title = slug.replace("-", " ").title()
    folder = SOL / folder_name(number, slug)
    if folder.exists():
        die(f"{folder.relative_to(ROOT)} already exists")
    folder.mkdir(parents=True)

    fmt = {"num": number, "title": title, "slug": slug}
    (folder / f"solution.{LANG_EXT[lang]}").write_text(SOLUTION_TEMPLATES[lang].format(**fmt))
    (folder / "notes.md").write_text(
        NOTES_TEMPLATE.format(difficulty=DIFF_LABEL[difficulty], today=date.today().isoformat(), **fmt)
    )
    (folder / "meta.json").write_text(
        json.dumps(
            {
                "number": number,
                "slug": slug,
                "title": title,
                "difficulty": difficulty,
                "lang": lang,
                "created": date.today().isoformat(),
            },
            indent=2,
        )
    )

    sync()
    rel = folder.relative_to(ROOT)
    print(f"Created {rel}/")
    print(f"  1. Solve it:   {rel}/solution.{LANG_EXT[lang]}")
    print(f"  2. Write notes: {rel}/notes.md")
    print("  3. Commit:")
    print(f'       git add . && git commit -m "solve {number}. {title}" && git push')


def collect() -> list[dict]:
    rows = []
    if not SOL.exists():
        return rows
    for meta in SOL.glob("*/meta.json"):
        try:
            rows.append(json.loads(meta.read_text()))
        except (ValueError, OSError):
            continue
    rows.sort(key=lambda r: r.get("number", 0))
    return rows


def build_table(rows: list[dict]) -> str:
    if not rows:
        return "_No problems yet — run_ `python3 lc.py new 1 two-sum easy`"

    counts = {"easy": 0, "medium": 0, "hard": 0}
    for r in rows:
        counts[r.get("difficulty", "medium")] = counts.get(r.get("difficulty", "medium"), 0) + 1

    lines = [
        f"**Total solved: {len(rows)}**  ·  🟢 {counts['easy']} Easy  ·  "
        f"🟡 {counts['medium']} Medium  ·  🔴 {counts['hard']} Hard",
        "",
        "| # | Problem | Difficulty | Lang | Notes |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for r in rows:
        fname = folder_name(r["number"], r["slug"])
        lines.append(
            f"| {r['number']} "
            f"| [{r['title']}](https://leetcode.com/problems/{r['slug']}/) "
            f"| {DIFF_LABEL.get(r.get('difficulty', 'medium'))} "
            f"| `{r.get('lang', 'py')}` "
            f"| [notes](solutions/{fname}/notes.md) |"
        )
    return "\n".join(lines)


def sync() -> None:
    table = build_table(collect())
    text = README.read_text()
    if START not in text or END not in text:
        die(f"README.md is missing the {START} / {END} markers")
    pre = text.split(START)[0]
    post = text.split(END)[1]
    README.write_text(f"{pre}{START}\n{table}\n{END}{post}")
    print("Updated README progress table.")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "new":
        cmd_new(sys.argv[2:])
    elif cmd == "sync":
        sync()
    else:
        die(f"unknown command {cmd!r} (expected: new, sync)")


if __name__ == "__main__":
    main()
