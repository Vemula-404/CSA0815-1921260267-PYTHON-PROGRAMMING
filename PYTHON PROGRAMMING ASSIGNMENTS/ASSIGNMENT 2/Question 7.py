import time

calls = 0

def ways_naive(n):
    global calls
    calls += 1
    if n <= 1:
        return 1
    return ways_naive(n - 1) + ways_naive(n - 2)

iterations = 0

def ways_loop(n):
    global iterations
    a, b = 1, 1
    for _ in range(n - 1):
        iterations += 1
        a, b = b, a + b
    return b

print(f"{'n':>3} | {'naive calls':>12} | {'naive time (s)':>14} | {'loop iters':>10} | {'loop time (s)':>13}")
for n in (10, 20, 25, 30):
    calls = 0
    t0 = time.perf_counter(); r1 = ways_naive(n); t_naive = time.perf_counter() - t0
    iterations = 0
    t0 = time.perf_counter(); r2 = ways_loop(n); t_loop = time.perf_counter() - t0
    print(f"{n:>3} | {calls:>12} | {t_naive:>14.6f} | {iterations:>10} | {t_loop:>13.8f}   same={r1 == r2}")

# Scale test only the redesign can handle
t0 = time.perf_counter()
big = ways_loop(1000)
print(f"n=1000 loop time: {time.perf_counter() - t0:.6f}s, digits in answer: {len(str(big))}")