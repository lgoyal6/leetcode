# 🧩 LeetCode Practice

Daily, genuine practice. **One problem → real notes → one commit.** No bots, no padding — every green square here is a problem I actually solved.

## Workflow (two commands)

**1. Start a problem** — scaffolds the folder, solution stub, and a notes template:
```bash
python3 lc.py new 1 two-sum easy
#            └ number └ slug (from the URL) └ easy|medium|hard  [optional: py|cpp|java]
```
Then solve it in `solutions/0001-two-sum/solution.py` and fill in `notes.md` (approach, complexity, what tripped you up — this is where the real learning sticks).

**2. Commit it** (the `new` command prints this exact line for you):
```bash
git add . && git commit -m "solve 1. Two Sum" && git push
```

Refactored an old one or edited notes? Rebuild the table with:
```bash
python3 lc.py sync
```

## Why this exists
Tying the daily-commit habit to LeetCode means the streak *forces* real practice — the commit is a side effect of doing the work, not the goal. If a day is green here, I earned it.

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
