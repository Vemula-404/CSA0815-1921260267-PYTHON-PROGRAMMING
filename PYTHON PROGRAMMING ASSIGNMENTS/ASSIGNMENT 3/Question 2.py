import copy
import sys
import time

rows, cols = 3, 4

bad = [[0] * cols] * rows  # every row is the SAME list object
bad[0][1] = 7

# TODO 1
good = [[0] * cols for _ in range(rows)]
good[0][1] = 7

print("bad :", bad)
print("good:", good)
print(bad[0] is bad[1], good[0] is good[1])

# Tuples are immutable, so they can be used as dictionary keys
stops = {(13.0827, 80.2707): "Chennai Central", (13.0418, 80.2341): "T. Nagar"}
print(stops[(13.0418, 80.2341)])

# List as a key gives an error
try:
    d = {[13.0418, 80.2341]: "T. Nagar"}
except TypeError as e:
    print("Error:", e)  # unhashable type: 'list'

# id() demonstration
print(id(bad[0]) == id(bad[1]), id(good[0]) == id(good[1]))

# Aliasing, shallow copy, deep copy
a = [[1, 2], [3, 4]]
alias = a
shallow1 = copy.copy(a)
shallow2 = a[:]
deep = copy.deepcopy(a)
a[0][0] = 99
print("alias   :", alias)      # changed
print("shallow1:", shallow1)   # changed (inner lists shared)
print("shallow2:", shallow2)   # changed
print("deep    :", deep)       # unchanged

# Unpacking tuples in a for loop
for (lat, lon), name in stops.items():
    print(name, lat, lon)

# Memory comparison
lst = list(range(1000000))
tup = tuple(lst)
print("list size :", sys.getsizeof(lst))
print("tuple size:", sys.getsizeof(tup))

# Timing creation and indexing
t = time.perf_counter(); l = list(range(1000000)); tl = time.perf_counter() - t
t = time.perf_counter(); tp = tuple(range(1000000)); tt = time.perf_counter() - t
print(f"create list={tl:.4f}s  create tuple={tt:.4f}s")

t = time.perf_counter()
for i in range(1000000):
    l[i]
tl = time.perf_counter() - t
t = time.perf_counter()
for i in range(1000000):
    tp[i]
tt = time.perf_counter() - t
print(f"index list={tl:.4f}s  index tuple={tt:.4f}s")

# List inside a tuple
t = (1, [2, 3])
t[1].append(4)       # works: the tuple still holds the same list object
print(t)
try:
    t[0] = 9         # fails: the tuple itself is immutable
except TypeError as e:
    print("Error:", e)

# Alternative: sparse dictionary grid
grid = {}
grid[(0, 1)] = 7
grid[(2, 3)] = grid.get((2, 3), 0) + 1
print(grid)