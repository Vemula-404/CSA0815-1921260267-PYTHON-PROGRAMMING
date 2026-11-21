import random
import time
from collections import deque

random.seed(1)

def make_readings(n):
    # about 40% dry days, otherwise rainfall between 0.1 and 50 mm
    return [0 if random.random() < 0.4 else round(random.uniform(0.1, 50), 1) for _ in range(n)]

readings = make_readings(365)

# Weekly totals using slicing
weekly = [sum(readings[i:i + 7]) for i in range(0, len(readings), 7)]
print("Number of weeks:", len(weekly))
print("First 3 weekly totals:", [round(w, 1) for w in weekly[:3]])

# Wettest and driest weeks (positions are week numbers starting at 1)
wet = max(weekly)
dry = min(weekly)
print("Wettest week:", weekly.index(wet) + 1, round(wet, 1))
print("Driest week :", weekly.index(dry) + 1, round(dry, 1))

# Max / min reading with positions (day number)
mx, mn = max(readings), min(readings)
print("Max:", mx, "on day", readings.index(mx) + 1)
print("Min:", mn, "on day", readings.index(mn) + 1)

# Naive 7-day moving average: about 7 additions per window
def moving_naive(r, w=7):
    if len(r) < w:
        return []
    return [sum(r[i:i + w]) / w for i in range(len(r) - w + 1)]

# Running-sum moving average: about 1 add and 1 subtract per step
def moving_running(r, w=7):
    if len(r) < w:
        return []
    s = sum(r[:w])
    out = [s / w]
    for i in range(w, len(r)):
        s += r[i] - r[i - w]
        out.append(s / w)
    return out

# deque version
def moving_deque(r, w=7):
    d = deque(maxlen=w)
    out = []
    s = 0
    for x in r:
        if len(d) == w:
            s -= d[0]
        d.append(x)
        s += x
        if len(d) == w:
            out.append(s / w)
    return out

# Dry days
dry_days = [i + 1 for i, x in enumerate(readings) if x == 0]
print("Dry days count:", len(dry_days), "First 10:", dry_days[:10])

# Slicing demo
print("readings[7:14] :", readings[7:14])   # days 8 to 14 (second week)
print("readings[-7:]  :", readings[-7:])    # last 7 days
print("readings[::7]  :", readings[::7][:5], "...")  # every 7th day starting at index 0

# Experiment
for n in (365, 36500, 365000):
    data = make_readings(n)
    t = time.perf_counter(); a = moving_naive(data); t1 = time.perf_counter() - t
    t = time.perf_counter(); b = moving_running(data); t2 = time.perf_counter() - t
    ok = all(abs(x - y) < 1e-6 for x, y in zip(a, b))
    print(f"n={n:>7}  naive={t1:.4f}s  running={t2:.4f}s  same={ok}")

# Edge cases
print("Empty list:", moving_naive([]), moving_running([]))
print("Short list:", moving_naive([1, 2, 3]), moving_running([1, 2, 3]))

# Late reading insertion: list.insert is O(n) because later items shift
readings.insert(100, 5.5)
print("Length after insert:", len(readings))