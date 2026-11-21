def subsidy_separate(units, ration_card, elder):
    results = []
    if units <= 100:
        results.append("Full subsidy")
    if 101 <= units <= 200 and ration_card:
        results.append("Partial subsidy")
    if units > 200 and elder:
        results.append("Elderly subsidy")
    if units <= 200 and elder:          # overlapping rule -> double subsidy bug
        results.append("Elderly subsidy (extra)")
    return results if results else ["No subsidy"]

def subsidy_elif(units, ration_card, elder):
    if units <= 100:
        return "Full subsidy"
    elif 101 <= units <= 200 and ration_card:
        return "Partial subsidy"
    elif units > 200 and elder:
        return "Elderly subsidy"
    else:
        return "No subsidy"

def subsidy_match(units, ration_card, elder):
    match units:
        case u if u <= 100:
            return "Full subsidy"
        case u if 101 <= u <= 200 and ration_card:
            return "Partial subsidy"
        case u if u > 200 and elder:
            return "Elderly subsidy"
        case _:
            return "No subsidy"

SLABS = [(100, "Full subsidy"), (200, "Partial subsidy")]
def subsidy_table(units, ration_card, elder):
    for limit, decision in SLABS:
        if units <= limit:
            if decision == "Partial subsidy" and not ration_card:
                if units > 100:
                    return "No subsidy"
            return decision
    return "Elderly subsidy" if elder else "No subsidy"

households = [(50, False, False), (100, False, False), (101, True, False),
              (101, False, False), (200, True, False), (201, True, False),
              (201, False, True), (350, False, False), (150, True, True)]

for u, r, e in households:
    print(f"{u:4} ration={r!s:5} elder={e!s:5} | separate: {subsidy_separate(u, r, e)} | "
          f"elif: {subsidy_elif(u, r, e)} | match: {subsidy_match(u, r, e)} | table: {subsidy_table(u, r, e)}")