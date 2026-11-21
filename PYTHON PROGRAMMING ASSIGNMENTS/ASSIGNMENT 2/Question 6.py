import sys
from functools import lru_cache

calls = 0

def ways_naive(n):
    global calls
    calls += 1
    if n <= 1:
        return 1
    return ways_naive(n - 1) + ways_naive(n - 2)

@lru_cache(maxsize=None)
def ways_memo(n):
    global calls
    calls += 1
    # TODO 1 (completed): same base case and recursive case, calling ways_memo
    if n <= 1:
        return 1
    return ways_memo(n - 1) + ways_memo(n - 2)

def ways_loop(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

# Correctness check for n = 1..6 (expected: 1, 2, 3, 5, 8, 13)
print([ways_naive(n) for n in range(1, 7)])

calls = 0; print("naive:", ways_naive(25), "calls =", calls)
calls = 0; print("memo :", ways_memo(25), "calls =", calls)

# Growth investigation
for n in (10, 20, 25, 30):
    calls = 0; ways_naive(n); naive_calls = calls
    ways_memo.cache_clear()
    calls = 0; ways_memo(n); memo_calls = calls
    print(f"n={n:2} naive calls={naive_calls:8} memo calls={memo_calls}")

# Deployment decision for n = 1000
print("Recursion limit:", sys.getrecursionlimit())
ways_memo.cache_clear()
try:
    print(ways_memo(1000))
except RecursionError:
    print("RecursionError: depth 1000 exceeds the default limit (about 1000)")

# Fix 1: raise the limit
sys.setrecursionlimit(5000)
ways_memo.cache_clear()
print("memo with raised limit:", ways_memo(1000) % 10**9)

# Fix 2: loop (recommended, O(1) space, no stack risk)
print("loop:", ways_loop(1000) % 10**9)