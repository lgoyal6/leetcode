#!/usr/bin/env python3
"""Tiny helper for a genuine daily LeetCode practice repo.

The solving is yours — this just removes the busywork so committing daily is easy.

Commands:
  python3 lc.py new <number> <slug> [difficulty] [lang]
      Scaffold solutions/<NNNN>-<slug>/ with a solution + notes template,
      then refresh the README progress table.
      difficulty: easy | medium | hard   (default: medium)
      lang:       py | cpp | java         (default: py)

  python3 lc.py pull [slug]
      Fetch your latest accepted LeetCode submission into a new folder (number +
      difficulty auto-detected). If LEETCODE_SESSION is set locally, your actual
      code is pulled in too; otherwise a template is left for you to paste into.
      `pull --list` shows your recent accepted problems.

  python3 lc.py done <number> <slug>
      After you've written your solution + notes: refresh the table and
      git add + commit + push in one step (commit message "solve N. Title").

  python3 lc.py sync
      Rescan solutions/ and rebuild the README progress table.

  python3 lc.py stats [username]
      Pull your REAL leetcode.com solved-counts (read-only, no login) into the
      README. Username is saved after the first run, so later just `lc.py stats`.

Examples:
  python3 lc.py new 1 two-sum easy
  python3 lc.py new 146 lru-cache hard cpp
  python3 lc.py sync
  python3 lc.py stats your-leetcode-username
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOL = ROOT / "solutions"
README = ROOT / "README.md"

START = "<!-- PROGRESS:START -->"
END = "<!-- PROGRESS:END -->"
STATS_START = "<!-- STATS:START -->"
STATS_END = "<!-- STATS:END -->"
CONFIG = ROOT / ".lcconfig.json"

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


def replace_block(start: str, end: str, content: str) -> None:
    text = README.read_text()
    if start not in text or end not in text:
        die(f"README.md is missing the {start} / {end} markers")
    pre = text.split(start)[0]
    post = text.split(end)[1]
    README.write_text(f"{pre}{start}\n{content}\n{end}{post}")


def sync() -> None:
    replace_block(START, END, build_table(collect()))
    print("Updated README progress table.")


# ---------------------------------------------------------------------------
# `stats`: mirror your REAL leetcode.com profile counts into the README.
# Read-only, username only, no login/cookie — it just reflects your app progress.
# ---------------------------------------------------------------------------
def load_config() -> dict:
    if CONFIG.exists():
        try:
            return json.loads(CONFIG.read_text())
        except (ValueError, OSError):
            return {}
    return {}


def save_config(**updates) -> None:
    cfg = load_config()
    cfg.update(updates)
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n")


def fetch_leetcode_stats(username: str) -> dict | None:
    query = """
    query userStats($username: String!) {
      allQuestionsCount { difficulty count }
      matchedUser(username: $username) {
        profile { ranking }
        submitStatsGlobal { acSubmissionNum { difficulty count } }
      }
    }
    """
    body = json.dumps({"query": query, "variables": {"username": username}}).encode()
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0 (leetcode-practice-repo)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode())
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        die(f"could not reach LeetCode: {exc}")
    matched = (payload.get("data") or {}).get("matchedUser")
    if not matched:
        return None
    totals = {d["difficulty"]: d["count"] for d in payload["data"].get("allQuestionsCount", [])}
    solved = {d["difficulty"]: d["count"] for d in matched["submitStatsGlobal"]["acSubmissionNum"]}
    return {
        "username": username,
        "ranking": (matched.get("profile") or {}).get("ranking"),
        "solved": solved,
        "totals": totals,
    }


def build_stats_block(s: dict) -> str:
    solved, totals = s["solved"], s["totals"]

    def frac(diff: str) -> str:
        return f"{solved.get(diff, 0)}/{totals.get(diff, 0)}"

    rank = f"  ·  Rank ~{s['ranking']:,}" if s.get("ranking") else ""
    return (
        f"**[{s['username']}](https://leetcode.com/u/{s['username']}/)** — "
        f"Solved **{solved.get('All', 0)}/{totals.get('All', 0)}**  ·  "
        f"🟢 {frac('Easy')}  ·  🟡 {frac('Medium')}  ·  🔴 {frac('Hard')}{rank}\n\n"
        f"_Live from leetcode.com · last synced {date.today().isoformat()} "
        f"· run `python3 lc.py stats` to refresh_"
    )


def cmd_stats(args: list[str]) -> None:
    username = (args[0].strip() if args else "") or load_config().get("username", "")
    if not username:
        die("usage: python3 lc.py stats <your-leetcode-username>  (saved for next time)")
    stats = fetch_leetcode_stats(username)
    if not stats:
        die(f"LeetCode user {username!r} not found (or the profile is private)")
    save_config(username=username)
    replace_block(STATS_START, STATS_END, build_stats_block(stats))
    print(f"Synced {username}: {stats['solved'].get('All', 0)} solved on leetcode.com.")


# ---------------------------------------------------------------------------
# `done`: one command to commit + push a problem you just solved.
# You run it (it's your solve) -> genuine commit. Set LC_NO_PUSH=1 to skip push.
# ---------------------------------------------------------------------------
def cmd_done(args: list[str]) -> None:
    if len(args) < 2:
        die("usage: python3 lc.py done <number> <slug>")
    try:
        number = int(args[0])
    except ValueError:
        die("<number> must be an integer")
    slug = args[1].strip().lower()
    folder = SOL / folder_name(number, slug)
    if not folder.exists():
        die(f"{folder.relative_to(ROOT)} not found — run `python3 lc.py new {number} {slug}` first")

    try:
        title = json.loads((folder / "meta.json").read_text()).get("title")
    except (ValueError, OSError):
        title = None
    title = title or slug.replace("-", " ").title()

    sync()  # keep the progress table current
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    commit = subprocess.run(["git", "commit", "-m", f"solve {number}. {title}"], cwd=ROOT)
    if commit.returncode != 0:
        die("nothing new to commit — did you save your solution/notes?")
    if os.environ.get("LC_NO_PUSH"):
        print(f"Committed (push skipped): solve {number}. {title}")
        return
    subprocess.run(["git", "push"], cwd=ROOT, check=True)
    print(f"✅ Committed & pushed: solve {number}. {title}")


# ---------------------------------------------------------------------------
# `pull`: fetch your latest accepted LeetCode submission into the repo.
# Metadata (number/difficulty) is public; the CODE needs your login cookie
# (LEETCODE_SESSION) set locally via env var or a git-ignored .lcsecret.json.
# You still run `lc.py done` to commit — this just removes the copy-paste.
# ---------------------------------------------------------------------------
LANG_TO_EXT = {
    "python3": "py", "python": "py", "cpp": "cpp", "c": "c", "java": "java",
    "javascript": "js", "typescript": "ts", "golang": "go", "kotlin": "kt",
    "swift": "swift", "rust": "rs", "ruby": "rb", "csharp": "cs", "scala": "scala",
    "php": "php", "dart": "dart", "elixir": "ex", "erlang": "erl", "racket": "rkt",
}
COMMENT_HASH = {"py", "rb", "ex", "erl"}


def _leetcode_creds() -> tuple:
    session = os.environ.get("LEETCODE_SESSION")
    csrf = os.environ.get("LEETCODE_CSRF")
    secret = ROOT / ".lcsecret.json"
    if not session and secret.exists():
        try:
            data = json.loads(secret.read_text())
            session = data.get("leetcode_session")
            csrf = csrf or data.get("csrf")
        except (ValueError, OSError):
            pass
    return session, csrf


def _gql(query: str, variables: dict, authed: bool = False):
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0 (leetcode-practice-repo)",
    }
    if authed:
        session, csrf = _leetcode_creds()
        if not session:
            return None
        cookie = f"LEETCODE_SESSION={session}"
        if csrf:
            cookie += f"; csrftoken={csrf}"
            headers["x-csrftoken"] = csrf
        headers["Cookie"] = cookie
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, ValueError, TimeoutError):
        return None


def _fetch_recent_ac(username: str, limit: int = 20) -> list:
    q = ("query recentAc($u:String!,$n:Int!){recentAcSubmissionList(username:$u,limit:$n)"
         "{id title titleSlug timestamp}}")
    data = _gql(q, {"u": username, "n": limit})
    if data is None:
        die("could not reach LeetCode (network/API).")
    return (data.get("data") or {}).get("recentAcSubmissionList") or []


def _fetch_question_meta(slug: str) -> dict:
    q = "query q($s:String!){question(titleSlug:$s){questionFrontendId title difficulty}}"
    data = _gql(q, {"s": slug})
    node = (data or {}).get("data", {}).get("question") if data else None
    if not node:
        die(f"could not fetch metadata for {slug!r}")
    return node


def _fetch_submission_code(submission_id: int):
    session, _ = _leetcode_creds()
    if not session:
        return None
    q = ("query sd($id:Int!){submissionDetails(submissionId:$id)"
         "{code lang{name} runtimeDisplay memoryDisplay}}")
    data = _gql(q, {"id": submission_id}, authed=True)
    sd = (data or {}).get("data", {}).get("submissionDetails") if data else None
    if not sd or not sd.get("code"):
        return None
    return {
        "code": sd["code"],
        "lang": (sd.get("lang") or {}).get("name", "python3"),
        "runtime": sd.get("runtimeDisplay"),
        "memory": sd.get("memoryDisplay"),
    }


def cmd_pull(args: list[str]) -> None:
    username = load_config().get("username")
    if not username:
        die("run `python3 lc.py stats <your-username>` once first to save your username")

    recent = _fetch_recent_ac(username)
    if not recent:
        die(f"no recent accepted submissions found for {username!r}")

    if args and args[0] in ("--list", "-l"):
        print(f"Recent accepted submissions for {username}:")
        for s in recent:
            print(f"  - {s['titleSlug']}   (submission {s['id']})")
        print("\nPull one with:  python3 lc.py pull <slug>   (or just `pull` for the latest)")
        return

    if args:
        slug = args[0].strip().lower()
        sub = next((s for s in recent if s["titleSlug"] == slug), None)
        if not sub:
            die(f"{slug!r} isn't in your recent accepted list — try `python3 lc.py pull --list`")
    else:
        sub = recent[0]
        slug = sub["titleSlug"]

    meta = _fetch_question_meta(slug)
    number = int(meta["questionFrontendId"])
    title = meta["title"]
    difficulty = meta["difficulty"].lower()
    if difficulty not in DIFF_LABEL:
        difficulty = "medium"

    folder = SOL / folder_name(number, slug)
    if folder.exists():
        die(f"{folder.relative_to(ROOT)} already exists — you've already pulled this one")

    code_info = _fetch_submission_code(int(sub["id"]))
    folder.mkdir(parents=True)

    if code_info:
        ext = LANG_TO_EXT.get(code_info["lang"], "py")
        prefix = "#" if ext in COMMENT_HASH else "//"
        header = f"{prefix} {number}. {title} — https://leetcode.com/problems/{slug}/\n\n"
        (folder / f"solution.{ext}").write_text(header + code_info["code"].rstrip() + "\n")
        code_status = f"pulled your accepted {code_info['lang']} submission"
        if code_info.get("runtime"):
            code_status += f" (runtime {code_info['runtime']}, memory {code_info['memory']})"
    else:
        ext = "py"
        (folder / "solution.py").write_text(
            SOLUTION_TEMPLATES["py"].format(num=number, title=title, slug=slug)
        )
        code_status = ("NO code pulled — set LEETCODE_SESSION to auto-fill (see README); "
                       "paste your solution manually for now")

    (folder / "notes.md").write_text(
        NOTES_TEMPLATE.format(
            num=number, title=title, slug=slug,
            difficulty=DIFF_LABEL[difficulty], today=date.today().isoformat(),
        )
    )
    (folder / "meta.json").write_text(
        json.dumps(
            {"number": number, "slug": slug, "title": title,
             "difficulty": difficulty, "lang": ext, "created": date.today().isoformat()},
            indent=2,
        )
    )
    sync()
    rel = folder.relative_to(ROOT)
    print(f"Pulled {number}. {title}  [{difficulty}]  ->  {rel}/")
    print(f"  code: {code_status}")
    print(f"  next: skim the solution, add your notes in {rel}/notes.md, then:")
    print(f"        python3 lc.py done {number} {slug}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "new":
        cmd_new(sys.argv[2:])
    elif cmd == "sync":
        sync()
    elif cmd == "stats":
        cmd_stats(sys.argv[2:])
    elif cmd == "done":
        cmd_done(sys.argv[2:])
    elif cmd == "pull":
        cmd_pull(sys.argv[2:])
    else:
        die(f"unknown command {cmd!r} (expected: new, pull, done, sync, stats)")


if __name__ == "__main__":
    main()
