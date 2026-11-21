"""
Assignment 2 CAPSTONE (Q7): Ration-Shop Billing & Verification System
Composes Q1-Q6. Each stage is tagged with its source question.

  Q1 decision engine  -> subsidy eligibility (match/elif, overlap-safe)
  Q2 retry control    -> OTP + lockout (while/for-else/recursion)
  Q3 string handling  -> vehicle/ration-card normalization + validation
  Q4 string building  -> receipt assembly (+= vs join vs StringIO) + timing
  Q5 scoping          -> per-customer cart via closure (mutable-default fix)
  Q6 optimization     -> count distinct bills via memo vs loop, recursion limit
"""
import re, time, io, sys
from functools import lru_cache

# ============================================================
# Q1 -- DECISION LOGIC: subsidy eligibility (overlap-safe)
# ============================================================
def subsidy_elif(units, ration_card, elder):
    """Q1: elif chain avoids the 'double subsidy' bug of separate ifs."""
    if units <= 100:
        return "Full subsidy"
    elif 101 <= units <= 200 and ration_card:
        return "Partial subsidy"
    elif units > 200 and elder:
        return "Elderly subsidy"
    else:
        return "No subsidy"

def subsidy_match(units, ration_card, elder):
    """Q1: match-case mirror of the same logic (verifies equivalence)."""
    match units:
        case u if u <= 100:                         return "Full subsidy"
        case u if 101 <= u <= 200 and ration_card:  return "Partial subsidy"
        case u if u > 200 and elder:                return "Elderly subsidy"
        case _:                                     return "No subsidy"

def subsidy_buggy(units, ration_card, elder):
    """Q1: the ORIGINAL separate-if version -- kept to prove it double-counts."""
    out = []
    if units <= 100: out.append("Full subsidy")
    if 101 <= units <= 200 and ration_card: out.append("Partial subsidy")
    if units > 200 and elder: out.append("Elderly subsidy")
    if units <= 200 and elder: out.append("Elderly subsidy (extra)")
    return out or ["No subsidy"]

# ============================================================
# Q2 -- RETRY CONTROL: OTP with lockout (while / for-else / recursion)
# ============================================================
CORRECT_OTP = "4321"

def otp_while(inputs, max_attempts=3):
    """Q2: while loop; blank entries don't consume an attempt."""
    attempts, it = 0, iter(inputs)
    while attempts < max_attempts:
        entry = next(it, "").strip()
        if not entry: continue
        attempts += 1
        if entry == CORRECT_OTP:
            return "Access granted"
    return "Account locked for 30 minutes"

def otp_for(inputs):
    """Q2: for-else -- else runs only if loop exhausts without break/return."""
    it = iter(inputs)
    for _ in range(3):
        entry = next(it, "").strip()
        while entry == "":
            entry = next(it, None)
            if entry is None: break
            entry = entry.strip()
        if entry == CORRECT_OTP:
            return "Access granted"
    else:
        return "Account locked for 30 minutes"

def otp_recursive(inputs, attempt=0):
    """Q2: recursive variant; blank does not increment attempt."""
    if attempt == 3 or not inputs:
        return "Account locked for 30 minutes"
    entry = inputs[0].strip()
    if entry == "":      return otp_recursive(inputs[1:], attempt)
    if entry == CORRECT_OTP: return "Access granted"
    return otp_recursive(inputs[1:], attempt + 1)

# ============================================================
# Q3 -- STRING HANDLING: normalize + validate ration/vehicle IDs
# ============================================================
def normalise(text):
    """Q3: 'tn 09 ab 1234' -> 'TN09AB1234' (strip, remove spaces/dashes, upper)."""
    return text.strip().replace(" ", "").replace("-", "").upper()

def is_valid_manual(reg):
    """Q3: manual slicing check (2 letters, 2 digits, 1-2 letters, 4 digits)."""
    if len(reg) not in (9, 10): return False
    series = reg[4:-4]
    return (reg[:2].isalpha() and reg[2:4].isdigit()
            and series.isalpha() and len(series) in (1, 2)
            and reg[-4:].isdigit())

def is_valid_regex(reg):
    """Q3: regex equivalent -- must agree with is_valid_manual."""
    return re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}", reg) is not None

def format_reg(reg):
    """Q3: 'TN09AB1234' -> 'TN 09 AB 1234'."""
    return " ".join([reg[:2], reg[2:4], reg[4:-4], reg[-4:]])

# ============================================================
# Q4 -- STRING BUILDING: receipt assembly, plus benchmark
# ============================================================
def receipt_plus(lines):
    """Q4: quadratic += build (slow)."""
    s = ""
    for l in lines: s += l + "\n"
    return s

def receipt_join(lines):
    """Q4: linear join build (recommended)."""
    return "\n".join(lines) + ("\n" if lines else "")

def receipt_stringio(lines):
    """Q4: StringIO buffer (linear, good for streaming)."""
    buf = io.StringIO()
    for l in lines: buf.write(l + "\n")
    return buf.getvalue()

def timed(fn, arg):
    t = time.perf_counter(); r = fn(arg); return r, time.perf_counter() - t

# ============================================================
# Q5 -- SCOPING: per-customer cart via closure (mutable-default fix)
# ============================================================
def add_item_buggy(item, order=[]):     # Q5: shared default -> classic bug
    order.append(item); return order

def add_item(item, order=None):         # Q5: correct sentinel fix
    if order is None: order = []
    order.append(item); return order

def make_cart():
    """Q5: closure factory -- each cart is isolated via nonlocal-free closure."""
    order = []
    def add(item, qty=1):
        order.append((item, qty))
        return list(order)
    return add

# ============================================================
# Q6 -- OPTIMIZATION: distinct bill-sequences via memo vs loop
# ============================================================
def ways_naive(n, counter):
    counter[0] += 1
    if n <= 1: return 1
    return ways_naive(n-1, counter) + ways_naive(n-2, counter)

@lru_cache(maxsize=None)
def ways_memo(n):
    if n <= 1: return 1
    return ways_memo(n-1) + ways_memo(n-2)

def ways_loop(n):
    a, b = 1, 1
    for _ in range(n-1):
        a, b = b, a + b
    return b

# ============================================================
# THE PIPELINE (Q7 = orchestration)
# ============================================================
def process_customer(name, raw_reg, units, ration_card, elder, otp_inputs, items):
    """One end-to-end customer record, exercising every question."""
    # Q3: normalize + validate registration
    reg = normalise(raw_reg)
    reg_ok = is_valid_manual(reg) and is_valid_regex(reg)   # cross-check

    # Q1: subsidy (elif vs match must agree; buggy version differs)
    sub = subsidy_elif(units, ration_card, elder)
    sub_match = subsidy_match(units, ration_card, elder)
    assert sub == sub_match, "Q1 elif/match disagree"
    bug = subsidy_buggy(units, ration_card, elder)

    # Q2: OTP gate (three implementations must agree)
    g1, g2, g3 = otp_while(otp_inputs), otp_for(otp_inputs), otp_recursive(otp_inputs)
    gate = g1  # trust while-version; assert agreement where semantics match
    gate_agree = (g1 == g3)   # for-else uses slightly different blank handling

    # Q5: per-customer cart (isolated)
    cart = make_cart()
    for it in items: cart(it[0], it[1])

    # Q4: build receipt lines, verify three builders agree
    lines = [f"Customer: {name}", f"Reg: {format_reg(reg) if reg_ok else 'INVALID'}",
             f"Subsidy: {sub}", f"Gate: {gate}"]
    lines += [f"  {it} x{qty}" for it, qty in cart.__closure__[0].cell_contents]
    r_plus, _ = timed(receipt_plus, lines)
    r_join, _ = timed(receipt_join, lines)
    r_io,   _ = timed(receipt_stringio, lines)
    assert r_plus == r_join == r_io, "Q4 builders disagree"

    return {
        "name": name, "reg": reg, "reg_valid": reg_ok,
        "subsidy": sub, "buggy_subsidy": bug,
        "gate": gate, "gate_agree": gate_agree,
        "receipt": r_join,
        "cart_items": list(cart.__closure__[0].cell_contents),
    }

# ============================================================
# DEMO + benchmarks (Q4 + Q6)
# ============================================================
if __name__ == "__main__":
    customers = [
        ("Ravi",  "tn 09 ab 1234",  50, False, False, ["", "1111", "4321"], [("Rice",5),("Dal",2)]),
        ("Anjali","KA-01-M-0007",  150, True,  False, ["1111","2222","3333"], [("Oil",1)]),
        ("Kumar", "TN 22 1234 AB", 350, False, True,  ["9","8","4321"], [("Sugar",3)]),
    ]
    for c in customers:
        rec = process_customer(*c)
        print("="*50)
        print(rec["receipt"])
        print(f"  buggy_subsidy={rec['buggy_subsidy']} (Q1 overlap demo)")
        print(f"  gate_agree(while==rec)={rec['gate_agree']}")

    # ---- Q4 benchmark: += vs join vs StringIO ----
    print("\nQ4 string-building benchmark:")
    for n in (1_000, 10_000, 200_000):
        lines = [f"Item{i}:Rs{i%50}" for i in range(n)]
        _, tp = timed(receipt_plus, lines)
        _, tj = timed(receipt_join, lines)
        _, ti = timed(receipt_stringio, lines)
        print(f"  n={n:7}  += {tp:.4f}s | join {tj:.4f}s | StringIO {ti:.4f}s")

    # ---- Q6 recursion vs memo vs loop ----
    print("\nQ6 optimization (distinct bill sequences):")
    for n in (10, 20, 25, 30):
        c = [0]; ways_naive(n, c); naive_calls = c[0]
        ways_memo.cache_clear()
        t = time.perf_counter(); ways_memo(n); tm = time.perf_counter()-t
        t = time.perf_counter(); ways_loop(n); tl = time.perf_counter()-t
        print(f"  n={n:2} naive_calls={naive_calls:8} memo={tm:.8f}s loop={tl:.8f}s")

    # recursion-limit deployment decision
    print("\nQ6 deployment at n=1000:")
    print("  recursionlimit:", sys.getrecursionlimit())
    ways_memo.cache_clear()
    try:
        ways_memo(1000); print("  memo ok")
    except RecursionError:
        print("  memo -> RecursionError (use loop)")
    print("  loop:", ways_loop(1000) % 10**9)