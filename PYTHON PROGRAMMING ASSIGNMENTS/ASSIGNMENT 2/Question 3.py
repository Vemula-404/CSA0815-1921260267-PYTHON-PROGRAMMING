def normalise(text):
    """'tn 09 ab 1234' -> 'TN09AB1234'"""
    return text.strip().replace(" ", "").replace("-", "").upper()

def is_valid(reg):
    """2 letters, 2 digits, 1 or 2 letters, 4 digits."""
    if len(reg) not in (9, 10):
        return False
    series = reg[4:-4]
    return (reg[:2].isalpha() and
            reg[2:4].isdigit() and
            series.isalpha() and len(series) in (1, 2) and
            reg[-4:].isdigit())

def format_reg(reg):
    """'TN09AB1234' -> 'TN 09 AB 1234'"""
    return " ".join([reg[:2], reg[2:4], reg[4:-4], reg[-4:]])

for raw in ["tn 09 ab 1234", "KA-01-M-0007", "TN9AB1234", "TN 22 1234 AB",
            "Tn09Ab1234", "TN-09-A-12"]:
    reg = normalise(raw)
    ok = is_valid(reg)
    print(f"{raw:15} -> {reg:11} {'valid' if ok else 'INVALID'}"
          + (f"  | receipt: {format_reg(reg)}" if ok else ""))

# Slicing demo
s9, s10 = "KA01M0007", "TN09AB1234"
print(s9[-4:], s9[4:-4])     # 0007 M
print(s10[-4:], s10[4:-4])   # 1234 AB

# Immutability demo
text = "tn09"
text.upper()
print(text)                  # still 'tn09'

# Regex alternative
import re
def is_valid_regex(reg):
    return re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}", reg) is not None
print(is_valid_regex("TN09AB1234"), is_valid_regex("TN9AB1234"))