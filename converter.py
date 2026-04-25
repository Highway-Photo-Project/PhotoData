import csv
import re
from pathlib import Path

# Full state names
STATE_NAMES = {
    "AR": "Arkansas",
    "TX": "Texas",
    "OK": "Oklahoma",
    "LA": "Louisiana",
    # Add all states/provinces here
}

def format_route(route, state_code):
    state = STATE_NAMES.get(state_code, state_code)

    # US Routes
    m = re.match(r"US(\d+)$", route)
    if m:
        num = m.group(1)
        return f"[[U.S. Route {num} in {state}|US {num}]]"

    # Interstate
    m = re.match(r"I(\d+)$", route)
    if m:
        num = m.group(1)
        return f"[[Interstate {num} in {state}|I-{num}]]"

    # State highways
    m = re.match(rf"{state_code}(\d+)$", route)
    if m:
        num = m.group(1)

        if state_code == "AR":
            return f"[[Arkansas Highway {num}|AR {num}]]"
        elif state_code == "TX":
            return f"[[Texas State Highway {num}|SH {num}]]"
        else:
            return f"[[{state} Highway {num}|{state_code} {num}]]"

    return route


def convert_file(filename):
    entries = []

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')

        for row in reader:
            if len(row) != 3:
                continue

            state_code, route, county = row
            entries.append((state_code, route, county))

    if not entries:
        return

    county_name = entries[0][2]

    print(f"== {county_name} County ==")

    for state_code, route, county in entries:
        formatted = format_route(route, state_code)
        print(f"* {formatted}")


# Example usage
convert_file("arkansas_county.csv")
