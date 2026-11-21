# Building the nested structure
timetable = {
    101: {
        "name": "Express A",
        "stops": [
            ("Chennai", 10, 12),
            ("Salem", 15, 17),
            ("Erode", 20, 22)
        ],
        "days": {"Mon", "Wed", "Fri"}
    },
    102: {
        "name": "Superfast B",
        "stops": [
            ("Chennai", 8, 10),
            ("Coimbatore", 18, 20),
            ("Madurai", 25, 27)
        ],
        "days": {"Tue", "Thu", "Sat"}
    },
    # ... add more to reach 5 trains as per instructions
}

def query_station(sched, station_name, day):
    results = []
    for train_no, info in sched.items():
        if day in info["days"]:
            for stop in info["stops"]:
                if stop[0] == station_name:
                    results.append((train_no, info["name"], stop[1], stop[2]))
    return results

# Sorting by departure time using lambda
def sort_trains_by_departure(query_results):
    # query_results format: (train_no, name, arrival, departure)
    return sorted(query_results, key=lambda x: x[3])

# Test Query
station = "Salem"
day = "Mon"
matches = query_station(timetable, station, day)
sorted_matches = sort_trains_by_departure(matches)

print(f"Trains at {station} on {day}:")
for m in sorted_matches:
    print(f"Train {m[0]} ({m[1]}) - Departs at {m[3]}:00")