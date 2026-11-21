CORRECT_OTP = "4321"

# Version 1: while loop
def otp_while(inputs):
    attempts = 0
    it = iter(inputs)
    while attempts < 3:
        entry = next(it, "").strip()
        if entry == "":
            continue                 # blank entry does not count
        attempts += 1                # counter updated only for real attempts
        if entry == CORRECT_OTP:
            return "Access granted"
        pass                         # wrong OTP: nothing extra, loop goes on
    return "Account locked for 30 minutes"

# Version 2: for loop with range(3) and loop-else
def otp_for(inputs):
    it = iter(inputs)
    for attempt in range(3):
        entry = next(it, "").strip()
        while entry == "":           # blank entries don't consume an attempt
            entry = next(it, None)
            if entry is None:
                break
            entry = entry.strip()
        if entry == CORRECT_OTP:
            return "Access granted"
    else:
        return "Account locked for 30 minutes"   # runs only if no break

# Changed condition: 2 extra attempts if security question is correct
def otp_extended(inputs, security_ok):
    max_attempts = 5 if security_ok else 3
    attempts = 0
    it = iter(inputs)
    while attempts < max_attempts:
        entry = next(it, "").strip()
        if not entry:
            continue
        attempts += 1
        if entry == CORRECT_OTP:
            return "Access granted"
    return "Account locked for 30 minutes"

# Recursive version
def otp_recursive(inputs, attempt=0):
    if attempt == 3 or not inputs:
        return "Account locked for 30 minutes"
    entry = inputs[0].strip()
    if entry == "":
        return otp_recursive(inputs[1:], attempt)       # blank: no attempt used
    if entry == CORRECT_OTP:
        return "Access granted"
    return otp_recursive(inputs[1:], attempt + 1)

print(otp_while(["", "1111", "2222", "4321"]))
print(otp_while(["1111", "2222", "3333", "4321"]))
print(otp_for(["9", "8", "4321"]))
print(otp_for(["9", "8", "7"]))
print(otp_extended(["1", "2", "3", "4", "4321"], security_ok=True))
print(otp_extended(["1", "2", "3", "4", "4321"], security_ok=False))
print(otp_recursive(["", "1", "4321"]))