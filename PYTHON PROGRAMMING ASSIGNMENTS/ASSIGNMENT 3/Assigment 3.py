"""
Q7 CAPSTONE: Contact-Merge System
Each stage consumes a skill built in Q1-Q6.
"""
import re, sys, time, string
from collections import Counter, deque
import copy

# ============================================================
# Q5 -- LIST COMPREHENSION: clean & validate sensor-grade records
# ============================================================
def clean(text):
    return text.lower().translate(str.maketrans("", "", string.punctuation)).split()

def valid_stream(records):
    """Generator (Q5 laziness): yield records with any usable identifier."""
    for r in records:
        if (r.get("phone") or "").strip() or (r.get("email") or "").strip():
            yield r

def valid_list(records):                      # list-comp version (Q5)
    return [r for r in records
            if (r.get("phone") or "").strip() or (r.get("email") or "").strip()]

def valid_mapfilter(records):                 # map/filter version (Q5)
    ok = lambda r: bool((r.get("phone") or "").strip() or (r.get("email") or "").strip())
    return list(map(lambda r: r, filter(ok, records)))

# ============================================================
# Q7 -- NORMALIZATION primitives
# ============================================================
def norm_phone(p):  return re.sub(r"\D", "", p or "")
def norm_name(n):   return (n or "").lower().strip()
def norm_email(e):  return (e or "").lower().strip()

# ============================================================
# Q2 -- TUPLES & MUTABILITY: immutable contact key + hashable location
# ============================================================
def contact_key(rec):
    """Return an immutable, hashable key. Tuples can be dict keys; lists cannot (Q2)."""
    phone = norm_phone(rec.get("phone"))
    email = norm_email(rec.get("email"))
    return (phone, email) if phone else ("", email)   # tuple => hashable

def loc_tuple(rec):
    """(lat, lon) tuple as hashable dict key -- Q2 bus-stop grid idea reused."""
    lat, lon = rec.get("lat"), rec.get("lon")
    return (round(lat, 3), round(lon, 3)) if lat is not None and lon is not None else None

# ============================================================
# Q4 -- SETS: decide "same person?" via set intersection/union
# ============================================================
def identity_signals(rec):
    """Sets of every phone-variant and email-variant seen for a record (Q4)."""
    phones, emails = set(), set()
    if norm_phone(rec.get("phone")): phones.add(norm_phone(rec["phone"]))
    for p in rec.get("alt_phones", []): phones.add(norm_phone(p))
    if norm_email(rec.get("email")): emails.add(norm_email(rec["email"]))
    for e in rec.get("alt_emails", []): emails.add(norm_email(e))
    return phones, emails

def same_person(a, b):
    pa, ea = identity_signals(a); pb, eb = identity_signals(b)
    shared_phone = bool(pa & pb)          # intersection (Q4)
    shared_email = bool(ea & eb)
    return shared_phone or shared_email

# ============================================================
# Q6 -- NESTED DATA: the merged-contact structure
# ============================================================
def new_bucket():
    return {
        "names":  set(),      # Q2/Q4 dedupe
        "emails": set(),
        "phones": set(),
        "calls":  [],         # Q1 call history (list => slicing/moving avg)
        "locs":   {},         # (lat,lon) tuple -> label  (Q2/Q6)
        "districts": set(),   # Q4/Q3 grouping
    }

def merge_contacts(records):
    """Q7 core: normalize -> group -> nested structure (Q6)."""
    merged = {}          # tuple key -> bucket
    for r in records:
        key = contact_key(r)
        bucket = merged.setdefault(key, new_bucket())
        if norm_name(r.get("name")):  bucket["names"].add(norm_name(r["name"]))
        if norm_email(r.get("email")): bucket["emails"].add(norm_email(r["email"]))
        if norm_phone(r.get("phone")): bucket["phones"].add(norm_phone(r["phone"]))
        bucket["calls"].extend(r.get("calls", []))
        loc = loc_tuple(r)
        if loc: bucket["locs"][loc] = r.get("label", "")
        if r.get("district"): bucket["districts"].add(r["district"])
    # Q4: merge buckets that are provably the same person (set intersection)
    return coalesce(merged)

def coalesce(merged):
    """Fold buckets whose phone/email sets intersect (Q4 union)."""
    items = list(merged.items())
    used = [False]*len(items)
    out = {}
    for i,(ki,bi) in enumerate(items):
        if used[i]: continue
        used[i]=True
        acc = copy.deepcopy(bi)                       # Q2 deep copy (nested mutables)
        for j in range(i+1,len(items)):
            if used[j]: continue
            kj,bj = items[j]
            if (acc["phones"] & bj["phones"]) or (acc["emails"] & bj["emails"]):  # Q4
                acc["names"]    |= bj["names"]
                acc["emails"]   |= bj["emails"]
                acc["phones"]   |= bj["phones"]
                acc["districts"]|= bj["districts"]
                acc["calls"].extend(bj["calls"])
                acc["locs"].update(bj["locs"])
                used[j]=True
        out[ki]=acc
    return out

# ============================================================
# Q3 -- DICTS: frequency of complaint words per contact
# ============================================================
STOP = {"not","high","no","the","a"}
def top_issues(calls, k=3):
    counts = Counter(w for c in calls for w in clean(c) if w not in STOP)
    # lambda tie-break: count desc, then alpha asc (Q3)
    return sorted(counts.items(), key=lambda p: (-p[1], p[0]))[:k]

def group_by_district(merged):
    """setdefault grouping (Q3) over the nested structure."""
    by = {}
    for bucket in merged.values():
        for d in bucket["districts"]:
            by.setdefault(d, []).append(bucket["names"])
    return {d: sorted(n for s in ns for n in s) for d,ns in by.items()}

# ============================================================
# Q1 -- LISTS/SLICING/MOVING AVG: call-activity time-series
# ============================================================
def call_lengths(bucket):
    return [len(c.split()) for c in bucket["calls"]]     # list (Q1)

def weekly_totals(xs):
    return [sum(xs[i:i+7]) for i in range(0,len(xs),7)]  # slicing (Q1)

def rolling_running(xs, w=7):
    if len(xs) < w: return []
    s = sum(xs[:w]); out=[s/w]
    for i in range(w,len(xs)):
        s += xs[i]-xs[i-w]; out.append(s/w)
    return out

def rolling_naive(xs, w=7):
    return [sum(xs[i:i+w])/w for i in range(len(xs)-w+1)] if len(xs)>=w else []

def extremes(xs):
    """max/min + position (Q1), returns (val,pos) tuples."""
    return (max(xs), xs.index(max(xs))+1), (min(xs), xs.index(min(xs))+1)

# ============================================================
# PIPELINE (Q7 = orchestration)
# ============================================================
def run(records):
    # Q5: three filter methods, prove equal
    a, b, c = list(valid_stream(records)), valid_list(records), valid_mapfilter(records)
    assert a == b == c, "Q5 methods disagree"

    merged = merge_contacts(a)                          # Q7 + Q6 + Q4 + Q2

    report = {}
    for key, bucket in merged.items():
        xs = call_lengths(bucket)                       # Q1
        report[key] = {
            "names":    sorted(bucket["names"]),
            "emails":   sorted(bucket["emails"]),
            "phones":   sorted(bucket["phones"]),
            "districts":sorted(bucket["districts"]),
            "locs":     {f"{la},{lo}": lab for (la,lo),lab in bucket["locs"].items()},
            "top_issues": top_issues(bucket["calls"]),  # Q3
            "weekly":   weekly_totals(xs),              # Q1 slicing
            "rolling":  [round(x,2) for x in rolling_running(xs)],
            "rolling_ok": rolling_running(xs) == rolling_naive(xs),
            "extreme":  extremes(xs) if xs else None,   # Q1
        }
    return {"contacts": report, "by_district": group_by_district(merged)}

# ============================================================
# DEMO + Q5 memory investigation
# ============================================================
if __name__ == "__main__":
    raw = [
        {"name":"Dr. Ravi","phone":"+91 98400 12345","email":"ravi@example.com",
         "district":"Salem","lat":11.664, "lon":78.146,"label":"home",
         "calls":["seeds not received seeds delayed","fertiliser price high"]},
        {"name":"ravi kumar","phone":"9840012345","email":"ravi.k@work.com",
         "district":"Salem","calls":["seeds price high subsidy not received"]},
        {"name":"Anjali","phone":"9000011111","email":"anjali@web.com",
         "district":"Erode","calls":["water not received"]},
        {"name":"Anjali","phone":"9000011111","email":"anjali@home.com",
         "district":"Erode","calls":["pest attack crop damaged"]},
        {"name":"NoPhone","phone":"","email":"np@x.com","district":"Salem",
         "calls":["loan delayed"]},
        {"name":"Bad","phone":"","email":"","calls":["junk"]},        # dropped (Q5)
    ]
    out = run(raw)

    print("=== Merged Contacts (Q7 capstone) ===")
    for k,v in out["contacts"].items():
        print(f"key={k}")
        print(f"  names={v['names']} phones={v['phones']} emails={v['emails']}")
        print(f"  districts={v['districts']} locs={v['locs']}")
        print(f"  top_issues={v['top_issues']}")
        print(f"  weekly={v['weekly']} rolling={v['rolling']} same_naive={v['rolling_ok']}")
        print(f"  extreme={v['extreme']}")
    print("\n=== Grouped by district (Q3) ===")
    print(out["by_district"])

    # Q5 memory: list vs generator
    print("\nQ5 memory:", "list=", sys.getsizeof(valid_list(raw)),
          "gen=", sys.getsizeof(valid_stream(raw)), "bytes")