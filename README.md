# 🧩 LeetCode Practice

Daily, genuine practice. **One problem → real notes → one commit.** No bots, no padding — every green square here is a problem I actually solved.

## Daily workflow

After you get **Accepted** on leetcode.com, it's three steps — **no login required**:

```bash
cd ~/leetcode
python3 lc.py pull majority-element     # 1. scaffold the folder — auto-detects #169 + difficulty
#   → paste your accepted code into solutions/0169-majority-element/solution.py
#   → jot your approach + O(time)/O(space) in notes.md
python3 lc.py done 169 majority-element # 2. rebuild table + commit + push, one step
```

Handy variants:
- `python3 lc.py pull` (no slug) grabs your **latest** accepted solve; `python3 lc.py pull --list` shows recent ones.
- Prefer to scaffold by hand? `python3 lc.py new 169 majority-element easy` does the same folder step.
- `python3 lc.py stats` refreshes your live LeetCode counts (below); `python3 lc.py sync` rebuilds the table.

### Optional: auto-fill your code (most people skip this)
By default you **paste your code** — reliable and zero setup. If you'd rather have `pull` drop your **actual submitted code** in automatically, give it your LeetCode login via a **git-ignored** `.lcsecret.json`:
```json
{ "leetcode_session": "PASTE_LEETCODE_SESSION", "csrf": "PASTE_csrftoken" }
```
Get both from DevTools → Application → Cookies → `https://leetcode.com`.

> ⚠️ That cookie is basically your LeetCode password (git-ignored, stays on your machine). It also **expires ~every 2 weeks**, so pasting your code by hand is usually less hassle — hence the default flow above skips it.

## Why this exists
Tying the daily-commit habit to LeetCode means the streak *forces* real practice — the commit is a side effect of doing the work, not the goal. If a day is green here, I earned it.

## My LeetCode profile (live from leetcode.com)

<!-- STATS:START -->
**[Lgoyal6](https://leetcode.com/u/Lgoyal6/)** — Solved **2/3999**  ·  🟢 2/955  ·  🟡 0/2089  ·  🔴 0/955  ·  Rank ~5,000,001

_Live from leetcode.com · last synced 2026-07-25 · run `python3 lc.py stats` to refresh_
<!-- STATS:END -->

## Progress

<!-- PROGRESS:START -->
**Total solved: 1**  ·  🟢 1 Easy  ·  🟡 0 Medium  ·  🔴 0 Hard

| # | Problem | Difficulty | Lang | Notes |
| ---: | --- | --- | --- | --- |
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/) | 🟢 Easy | `py` | [notes](solutions/0001-two-sum/notes.md) |
<!-- PROGRESS:END -->

## Conventions
- One folder per problem: `solutions/NNNN-slug/` (zero-padded number).
- `solution.<ext>` = the code; `notes.md` = the thinking; `meta.json` = metadata for the table.
- Default language is Python; pass `cpp` or `java` as the 4th arg to `new`.
- The **Retry** checkbox in each `notes.md` is a cue to redo hard problems from scratch a week later — spaced repetition beats one-and-done.
