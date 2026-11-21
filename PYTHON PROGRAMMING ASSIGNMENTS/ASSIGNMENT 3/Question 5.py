import random
import time
import sys

# Generate sample readings: valid between -50 and 50, others are errors
readings = [random.uniform(-60, 60) for _ in range(1000)]

# 1. Using for loop with append
valid_loop = []
for r in readings:
    if -50 <= r <= 50:
        valid_loop.append(r)

# 2. Using list comprehension (TODO implementation)
valid_comp = [r for r in readings if -50 <= r <= 50]

# 3. Using map() and filter() with lambda (TODO implementation)
valid_map = list(map(lambda x: x, filter(lambda x: -50 <= x <= 50, readings)))

# 4. Produce list of alarm minutes (outside 2-8 C) using enumerate
# Let's assume 'readings' is the list of minutes
alarms = [m for m, temp in enumerate(readings) if temp < 2 or temp > 8]

# Verification
print("Loop matches Comprehension:", valid_loop == valid_comp)
print("Comprehension matches Map/Filter:", valid_comp == valid_map)

# Memory comparison (Experimental Investigation)
gen_expr = (r for r in readings if -50 <= r <= 50)
print(f"List comprehension size: {sys.getsizeof(valid_comp)} bytes")
print(f"Generator expression size: {sys.getsizeof(gen_expr)} bytes")