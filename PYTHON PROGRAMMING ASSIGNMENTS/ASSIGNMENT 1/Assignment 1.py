
from decimal import Decimal, ROUND_HALF_UP
import math
import sys
import time

# ====================================================================
# T3 : NAMED CONSTANTS (UPPER_CASE), T12 : SEASONAL RATE CARDS
# ====================================================================
RATE_CARDS = {
    "normal":  {"base": Decimal("30.00"),
                "fat_step": Decimal("0.40"),
                "snf_step": Decimal("0.30")},
    "apr-jun": {"base": Decimal("32.00"),
                "fat_step": Decimal("0.45"),
                "snf_step": Decimal("0.30")},
}
STD_FAT       = Decimal("3.5")
STD_SNF       = Decimal("8.5")
STEP          = Decimal("0.1")
BONUS_THRESH  = Decimal("500")     # litres in ten days
BONUS_RATE    = Decimal("0.50")    # Rs per litre
TWO_DP        = Decimal("0.01")

# T1: validation limits (rules every payment must satisfy)
FAT_MIN, FAT_MAX = Decimal("2.0"), Decimal("7.0")
SNF_MIN, SNF_MAX = Decimal("7.0"), Decimal("10.0")

# ====================================================================
# T2 : TYPE EXPLORATION (evidence, run in interpreter; here as a demo)
# ====================================================================
def types_demo():
    print("\n[T2] type() and division exploration")
    for v in (10, 10.0, "10", True, [10, 8.5]):
        print(f"  {v!r:12} -> {type(v).__name__}")
    print(f"  7/2  = {7/2}    (true division -> float)")
    print(f"  7//2 = {7//2}   (floor division -> int)")
    print(f"  7%2  = {7%2}    (remainder)")
    print(f"  -7//2= {-7//2}  (floor, rounds toward -inf)")
    print(f"  0.1+0.2 == 0.3 ? {0.1+0.2 == 0.3}   (binary float cannot store 0.1)")
    print(f"  Decimal('0.1')+Decimal('0.2') == Decimal('0.3') ? "
          f"{Decimal('0.1')+Decimal('0.2') == Decimal('0.3')}")

# ====================================================================
# T4 : STEP EXPRESSION (operator precedence; 2-dp safe)
# ====================================================================
def steps(value, standard):
    """
    [T4] Number of 0.1% steps from the standard.
    [T12] Decimal + ROUND_HALF_UP fixes the 2-dp boundary bug where
          round((4.25-3.5)/0.1) gave 7 instead of 8.
    """
    return int(((value - standard) / STEP).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP))

def round_traps_demo():
    """[T4] Show round()/int()/floor differences, incl. negatives."""
    print("\n[T4] round() vs int() vs math.floor()")
    for x in (2.5, 3.5, -2.5, -3.5, 4.25):
        print(f"  x={x:>6}: round={round(x):>3}  int={int(x):>3}  "
              f"floor={math.floor(x):>3}")
    print("  (4.2-3.5)/0.1 =", (4.2-3.5)/0.1, "-> round gives", round((4.2-3.5)/0.1))
    print("  (4.25-3.5)/0.1 =", (4.25-3.5)/0.1,
          "-> float round gives", round((4.25-3.5)/0.1),
          "but Decimal gives", steps(Decimal("4.25"), STD_FAT))

# ====================================================================
# T5 : INPUT PARSING & VALIDATION (input() returns str)
# ====================================================================
def parse_entry(raw):
    """
    [T5] 'litres,fat,snf[,shift]' -> (Decimal, Decimal, Decimal, str).
    Demonstrates converting str -> Decimal with clear errors, like
    float(text) in try/except but precision-safe.
    """
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) not in (3, 4):
        raise ValueError(f"expected 3 or 4 fields, got {len(parts)}")
    try:
        litres, fat, snf = Decimal(parts[0]), Decimal(parts[1]), Decimal(parts[2])
    except Exception as exc:
        raise ValueError(f"non-numeric entry: {raw!r}") from exc
    shift = parts[3] if len(parts) == 4 else "M"
    return litres, fat, snf, shift

def validate(litres, fat, snf):
    """[T1] Return None if valid, else an error message string."""
    if litres <= 0:                     return "litres must be > 0"
    if not (FAT_MIN <= fat <= FAT_MAX): return f"fat {fat} outside 2.0-7.0"
    if not (SNF_MIN <= snf <= SNF_MAX): return f"snf {snf} outside 7.0-10.0"
    return None

# ====================================================================
# T6 : FUNCTIONS (params, returns, docstrings, scope)
# ====================================================================
def rate_per_litre(fat, snf, season="normal"):
    """[T6][T12] Rs per litre for the season (Decimal, 2 dp)."""
    card = RATE_CARDS[season]
    rate = (card["base"]
            + steps(fat, STD_FAT) * card["fat_step"]
            + steps(snf, STD_SNF) * card["snf_step"])
    return rate.quantize(TWO_DP, rounding=ROUND_HALF_UP)

def payout(litres, fat, snf, season="normal"):
    """[T6][T12] Amount for one entry (Decimal, 2 dp)."""
    return (litres * rate_per_litre(fat, snf, season)).quantize(
        TWO_DP, rounding=ROUND_HALF_UP)

# ====================================================================
# T10 : RATE-TABLE CACHE (lookup vs recompute)
# ====================================================================
_RATE_CACHE = {}
def rate_cached(fat, snf, season="normal"):
    """[T10] Memoise rate by (fat, snf, season)."""
    key = (fat, snf, season)
    if key not in _RATE_CACHE:
        _RATE_CACHE[key] = rate_per_litre(fat, snf, season)
    return _RATE_CACHE[key]

# ====================================================================
# T8 : TEN-DAY TOTAL (running total, hand-traceable) + T12 BONUS
# ====================================================================
def ten_day_total(entries, season="normal"):
    """
    [T8] Running total over entries.
    [T12] Bonus if total litres > 500.
    entries: list of (litres, fat, snf) Decimals.
    Returns (amount, litres, bonus_applied).
    """
    amount = Decimal("0")
    litres = Decimal("0")
    for l, f, s in entries:
        amount += payout(l, f, s, season)
        litres += l
    bonus = litres > BONUS_THRESH
    if bonus:
        amount += (litres * BONUS_RATE).quantize(TWO_DP, rounding=ROUND_HALF_UP)
    return amount.quantize(TWO_DP, rounding=ROUND_HALF_UP), litres, bonus

# ====================================================================
# T2 + T10 : FLOAT vs DECIMAL MEASUREMENT
# ====================================================================
def total_float(amounts):
    s = 0.0
    for a in amounts:
        s += float(a)
    return s

def total_decimal(amounts):
    return sum((a for a in amounts), Decimal("0"))

def bench():
    print("\n[T2][T10] float vs Decimal totals")
    print(f"{'n':>7} | {'float':>18} | {'Decimal':>14} | "
          f"{'diff':>10} | {'float s':>9} | {'dec s':>9}")
    for n in (300, 6_000, 150_000):
        amounts = [Decimal("33.40")] * n + [Decimal("0.10")] * (n // 300)
        t = time.perf_counter(); f = total_float(amounts); tf = time.perf_counter()-t
        t = time.perf_counter(); d = total_decimal(amounts); td = time.perf_counter()-t
        diff = Decimal(str(f)) - d
        print(f"{n:>7} | {f:>18.4f} | {str(d):>14} | {diff:>10.4f} | "
              f"{tf:>9.5f} | {td:>9.5f}")

# ====================================================================
# T9 : TEST SUITE (asserts, boundary, invalid)
# ====================================================================
def run_tests():
    """[T9] Re-runnable assert table."""
    # normal
    assert rate_per_litre(Decimal("3.5"), Decimal("8.5")) == Decimal("30.00")
    assert rate_per_litre(Decimal("4.2"), Decimal("8.7")) == Decimal("33.40")
    assert rate_per_litre(Decimal("3.1"), Decimal("8.3")) == Decimal("27.80")
    # boundary
    assert rate_per_litre(Decimal("2.0"), Decimal("8.5")) == Decimal("24.00")
    assert rate_per_litre(Decimal("7.0"), Decimal("8.5")) == Decimal("44.00")
    # 2-dp boundary (old float code failed)
    assert rate_per_litre(Decimal("4.25"), Decimal("8.5")) == Decimal("33.00")
    assert rate_per_litre(Decimal("4.25"), Decimal("8.5"), "apr-jun") == Decimal("35.60")
    # payout
    assert payout(Decimal("10"), Decimal("3.5"), Decimal("8.5")) == Decimal("300.00")
    # bonus boundary
    below = [(Decimal("50.00"), Decimal("3.5"), Decimal("8.5"))] * 10
    above = [(Decimal("50.01"), Decimal("3.5"), Decimal("8.5"))] * 10
    assert ten_day_total(below)[0] == Decimal("15000.00")
    assert ten_day_total(above)[2] is True
    # validation
    assert validate(Decimal("10"), Decimal("3.5"), Decimal("8.5")) is None
    assert validate(Decimal("-1"), Decimal("3.5"), Decimal("8.5")) is not None
    assert validate(Decimal("10"), Decimal("8.0"), Decimal("8.5")) is not None
    print("\n[T9] all assertions passed.")

# ====================================================================
# T3 : DYNAMIC TYPING & MULTIPLE ASSIGNMENT DEMO
# ====================================================================
def dynamic_demo():
    print("\n[T3] dynamic typing & swap")
    x = 10            # int
    print(f"  x={x!r} -> {type(x).__name__}")
    x = "ten"         # same name, str now
    print(f"  x={x!r} -> {type(x).__name__}")
    a, b = 1, 2
    a, b = b, a
    print(f"  swapped: a={a} b={b}")

# ====================================================================
# T11 + T12.D : RECOMMENDATION & EVIDENCE
# ====================================================================
def report(normal, june):
    print("\n[T11] FINAL RECOMMENDATION")
    print("  Money type : Decimal (float lost pennies at 6,000+ in [T10])")
    print("  Rounding   : ROUND_HALF_UP, 2 dp on entry and on total")
    print("  Rate change: edit RATE_CARDS only - no caller changes")
    print("  Limitations: single 0.1% step sensitivity; bonus on one")
    print("               ten-day window only")
    print("  Scale      : O(n) time, O(1) extra memory - fine at")
    print("               district-union scale")
    print(f"\n[T12] EVIDENCE")
    print(f"  normal  block = {normal}")
    print(f"  apr-jun block = {june}")

# ====================================================================
# T7 : MODULE MAIN GUARD (runs only when executed directly)
# ====================================================================
if __name__ == "__main__":
    print("=" * 68)
    print("ASSIGNMENT 1 - FINAL QUESTION (Task 12) CAPSTONE")
    print("=" * 68)

    types_demo()          # T2
    round_traps_demo()    # T4
    dynamic_demo()        # T3

    # ---- T5/T1: parse a raw ten-line block, reject bad lines ----
    raw_block = [
        "45.00,3.50,8.50,M",
        "52.10,4.23,8.57,E",
        "48.75,3.90,8.40,M",
        "50.00,3.10,8.30,M",
        "47.50,4.25,8.60,M",   # 2-dp boundary case
        "49.80,3.55,8.55,E",
        "51.20,4.10,8.45,M",
        "46.90,3.70,8.35,M",
        "50.40,4.00,8.50,E",
        "48.35,3.60,8.40,M",
        "BAD,4.0,8.5,M",       # invalid -> rejected
        "60.00,8.50,8.50,M",   # fat out of range -> rejected
    ]
    parsed = []
    for raw in raw_block:
        try:
            l, f, s, sh = parse_entry(raw)
        except ValueError as exc:
            print(f"  SKIP {raw!r}: {exc}")
            continue
        err = validate(l, f, s)
        if err:
            print(f"  REJECT {raw!r}: {err}")
            continue
        parsed.append((l, f, s))

    # ---- T6/T12: one entry, both seasons ----
    print("\n[T6][T12] one entry, both seasons")
    for season in ("normal", "apr-jun"):
        r = rate_per_litre(Decimal("4.23"), Decimal("8.57"), season)
        p = payout(Decimal("8.50"), Decimal("4.23"), Decimal("8.57"), season)
        print(f"  {season:8} rate={r}  pay={p}")

    # ---- T8/T12: ten-day totals ----
    normal_total, normal_litres, normal_bonus = ten_day_total(parsed, "normal")
    june_block = [(Decimal("55.00"), Decimal("4.23"), Decimal("8.57")),
                  (Decimal("60.00"), Decimal("4.10"), Decimal("8.40")),
                  (Decimal("58.00"), Decimal("3.90"), Decimal("8.60")),
                  (Decimal("62.00"), Decimal("4.25"), Decimal("8.55")),
                  (Decimal("57.00"), Decimal("3.70"), Decimal("8.45")),
                  (Decimal("59.00"), Decimal("4.00"), Decimal("8.50")),
                  (Decimal("61.00"), Decimal("4.20"), Decimal("8.65")),
                  (Decimal("56.00"), Decimal("3.80"), Decimal("8.35")),
                  (Decimal("63.00"), Decimal("4.15"), Decimal("8.55")),
                  (Decimal("52.00"), Decimal("3.60"), Decimal("8.30"))]
    june_total, june_litres, june_bonus = ten_day_total(june_block, "apr-jun")

    print("\n[T8][T12] ten-day totals")
    print(f"  normal : litres={normal_litres}  bonus={normal_bonus}  total={normal_total}")
    print(f"  apr-jun: litres={june_litres}   bonus={june_bonus}   total={june_total}")

    bench()               # T2/T10
    run_tests()           # T9

    # ---- T10: cache speed-up ----
    print("\n[T10] rate cache")
    t = time.perf_counter()
    for _ in range(100_000):
        rate_per_litre(Decimal("4.23"), Decimal("8.57"), "normal")
    t_re = time.perf_counter() - t
    _RATE_CACHE.clear()
    t = time.perf_counter()
    for _ in range(100_000):
        rate_cached(Decimal("4.23"), Decimal("8.57"), "normal")
    t_c = time.perf_counter() - t
    print(f"  recompute 100k: {t_re:.4f}s")
    print(f"  cached    100k: {t_c:.4f}s   speedup ~{t_re/t_c:.1f}x")

    report((normal_total, normal_litres, normal_bonus),
           (june_total, june_litres, june_bonus))     # T11/T12.D

    print("\n" + "=" * 68)
    print("Done.")