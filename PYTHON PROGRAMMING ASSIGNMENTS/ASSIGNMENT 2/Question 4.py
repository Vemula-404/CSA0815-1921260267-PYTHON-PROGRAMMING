import time
import io

def build_plus(parts):
    text = ""
    for p in parts:
        text += p + ";"
    return text

def build_join(parts):
    return "".join(p + ";" for p in parts)

def build_fstring_join(parts):
    return "".join([f"{p};" for p in parts])

def build_stringio(parts):
    buf = io.StringIO()
    for p in parts:
        buf.write(p + ";")
    return buf.getvalue()

def timed(func, items):
    start = time.perf_counter()
    result = func(items)
    return result, time.perf_counter() - start

for n in (1_000, 10_000, 200_000):
    items = [f"Item{i}:Rs{i % 50}" for i in range(n)]
    a, t_plus = timed(build_plus, items)
    b, t_join = timed(build_join, items)
    c, t_f = timed(build_fstring_join, items)
    d, t_io = timed(build_stringio, items)
    print(f"n={n:7} same={a == b == c == d} len={len(b)}")
    print(f"   += {t_plus:.4f}s | join {t_join:.4f}s | f-string+join {t_f:.4f}s | StringIO {t_io:.4f}s")

# Average of three runs for the 200,000 case
items = [f"Item{i}:Rs{i % 50}" for i in range(200_000)]
plus_avg = sum(timed(build_plus, items)[1] for _ in range(3)) / 3
join_avg = sum(timed(build_join, items)[1] for _ in range(3)) / 3
print(f"Average over 3 runs -> += {plus_avg:.4f}s, join {join_avg:.4f}s")