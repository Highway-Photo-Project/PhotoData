import os
import csv
import re

BASE = "_counties"
OUTPUT = "highest_lowest_routes_by_county.csv"

route_re = re.compile(r"(\d+)")

def extract_route_number(route_code):
    match = route_re.search(route_code)
    return int(match.group(1)) if match else None

def analyze_counties(base_folder):
    results = {}

    for filename in os.listdir(base_folder):
        if not filename.lower().endswith(".csv"):
            continue

        csv_path = os.path.join(base_folder, filename)

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                if len(row) < 3:
                    continue

                state = row[0].strip()
                route_code = row[1].strip()
                county = row[2].strip()

                route_num = extract_route_number(route_code)
                if route_num is None:
                    continue

                key = (state, county)

                if key not in results:
                    results[key] = [route_num, route_num]
                else:
                    results[key][0] = min(results[key][0], route_num)
                    results[key][1] = max(results[key][1], route_num)

    return results

def write_output(results, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "State",
            "County",
            "Lowest Route Number",
            "Highest Route Number"
        ])

        for (state, county), (low, high) in sorted(results.items()):
            writer.writerow([state, county, low, high])

if __name__ == "__main__":
    results = analyze_counties(BASE)
    write_output(results, OUTPUT)
