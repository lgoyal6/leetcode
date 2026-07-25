"""1. Two Sum
LeetCode: https://leetcode.com/problems/two-sum/
"""
from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Map each value -> its index as we scan. For each number, check whether
        # its complement (target - num) was already seen. One pass, O(n).
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []


if __name__ == "__main__":
    s = Solution()
    print(s.twoSum([2, 7, 11, 15], 9))   # [0, 1]
    print(s.twoSum([3, 2, 4], 6))        # [1, 2]
    print(s.twoSum([3, 3], 6))           # [0, 1]
