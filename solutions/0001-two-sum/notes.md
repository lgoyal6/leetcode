# 1. Two Sum

- **Link:** https://leetcode.com/problems/two-sum/
- **Difficulty:** 🟢 Easy
- **First solved:** 2026-07-24

## Approach
Brute force is checking every pair — O(n²). The trick is to trade space for time
with a hash map: as you scan left to right, store each value's index. For the
current number, its "partner" must be `target - num`; if you've already seen that
partner, you're done. Single pass.

## Complexity
- **Time:** O(n) — one pass, hash lookups are O(1) average.
- **Space:** O(n) — the map can hold up to n entries.

## Mistakes / gotchas
- Insert into the map *after* checking for the complement, otherwise a single
  element could match itself (e.g. `target = 2*num`).
- Return the indices, not the values.

## Retry
- [ ] Redo this from scratch in ~1 week without looking.
