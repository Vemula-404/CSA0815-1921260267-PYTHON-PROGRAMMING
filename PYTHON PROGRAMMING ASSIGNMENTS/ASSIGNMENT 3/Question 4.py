import random
import time
import string
from collections import Counter

calls = [
    "seeds not received seeds delayed",
    "fertiliser price high",
    "seeds price high subsidy not received",
]
STOP = {"not", "high"}

def clean(text):
    return text.lower().translate(str.maketrans("", "", string.punctuation)).split()

def frequencies(texts, stop):
    counts = {}
    for text in texts:
        for w in clean(text):
            if w not in stop:
                counts
" = counts.get(w, 0) + 1
    return counts

def top(counts, k):
    return sorted(counts.items(), key=lambda p: (-p[1], p[0]))[:k]

print(top(frequencies(calls, STOP), 3))
# [('seeds', 3), ('price', 2), ('received', 2)]
# Ties are broken alphabetically: 'price' < 'received' because 'p' comes before 'r'.

# Grouping complaints by district using setdefault
complaints = [("Salem", "seeds delayed"), ("Erode", "price high"), ("Salem", "no subsidy")]
by_district = {}
for district, text in complaints:
    by_district.setdefault(district, []).append(text)
print(by_district)

# Alternative methods
def freq_listcount(texts, stop):
    words = [w for t in texts for w in clean(t) if w not in stop]
    return {w: words.count(w) for w in set(words)}

def freq_counter(texts, stop):
    return Counter(w for t in texts for w in clean(t) if w not in stop)

# Experiment
vocab = ["seeds", "price", "subsidy", "rain", "pest", "loan", "water", "crop", "soil", "power"] + \
        [f"word{i}" for i in range(200)]

def gen(n):
    return [" ".join(random.choice(vocab) for _ in range(5)) for _ in range(n)]

for n in (1000, 10000, 100000):
    data = gen(n)
    t = time.perf_counter(); frequencies(data, STOP); t1 = time.perf_counter() - t
    t = time.perf_counter(); freq_counter(data, STOP); t2 = time.perf_counter() - t
    if n <= 10000:
        t = time.perf_counter(); freq_listcount(data, STOP); t3 = time.perf_counter() - t
    else:
        t3 = None   # list.count() version is too slow at this size
    print(n, f"dict={t1:.3f}s counter={t2:.3f}s listcount={t3}")

# Edge cases
print(frequencies([""], STOP))
print(frequencies(["Seeds SEEDS, seeds!"], STOP))