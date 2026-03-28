import os
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = Path("PhotoData")  # adjust path if needed
COUNTIES_DIR = BASE_DIR / "_counties"
SYSTEMS_DIR  = BASE_DIR / "_systems"
REGIONS_DIR  = BASE_DIR / "_regions"

OUTPUT_FILE = "datacheck.html"

# -----------------------------
# PARSING FUNCTION
# -----------------------------
def parse_file(filepath, folder_type):
    """
    Extract (region;route) from a file depending on folder type.
    """
    routes = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # skip header
    for line in lines[1:]:
        parts = line.strip().split(";")

        if len(parts) < 2:
            continue

        if folder_type == "counties":
            # region;route;county
            region, route = parts[0], parts[1]

        elif folder_type in ("systems", "regions"):
            # systemName;region;route
            region, route = parts[1], parts[2]

        else:
            continue

        key = f"{region.strip().upper()};{route.strip().upper()}"
        routes.append(key)

    return routes

# -----------------------------
# LOAD ROUTES FROM FOLDER
# -----------------------------
def get_routes(folder, folder_type):
    routes_list = []
    routes_set = set()

    for root, _, files in os.walk(folder):
        for file in sorted(files):
            if file.endswith(".csv"):
                filepath = Path(root) / file

                entries = parse_file(filepath, folder_type)

                for e in entries:
                    routes_list.append(e)
                    routes_set.add(e)

    return routes_list, routes_set

# -----------------------------
# LOAD DATA
# -----------------------------
counties_list, counties_set = get_routes(COUNTIES_DIR, "counties")
systems_list, systems_set   = get_routes(SYSTEMS_DIR, "systems")
regions_list, regions_set   = get_routes(REGIONS_DIR, "regions")

# -----------------------------
# BUILD RESULTS (COUNTY ORDER)
# -----------------------------
results = []

for route in counties_list:
    results.append({
        "route": route,
        "in_counties": True,
        "in_systems": route in systems_set,
        "in_regions": route in regions_set
    })

# Add routes missing from counties
extra_routes = (systems_set | regions_set) - counties_set

for route in sorted(extra_routes):
    results.append({
        "route": route,
        "in_counties": False,
        "in_systems": route in systems_set,
        "in_regions": route in regions_set
    })

# -----------------------------
# FILTER ONLY MISSING
# -----------------------------
flagged = [
    r for r in results
    if not (r["in_counties"] and r["in_systems"] and r["in_regions"])
]

# -----------------------------
# HTML OUTPUT
# -----------------------------
def generate_html(data):
    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Route Data Check</title>
<style>
body { font-family: Arial; }
table {
    border-collapse: collapse;
    width: 100%;
}
th, td {
    border: 1px solid black;
    padding: 6px;
    text-align: left;
    word-wrap: break-word;
}
th {
    background-color: #f2f2f2;
}
.missing {
    background-color: #ffcccc;
}
</style>
</head>
<body>

<h2>Missing Route Entries</h2>

<table>
<tr>
    <th>Route</th>
    <th>Counties</th>
    <th>Systems</th>
    <th>Regions</th>
</tr>
"""

    def mark(val):
        return "✔" if val else "✖"

    for r in data:
        html += f"""
<tr class="missing">
    <td>{r['route']}</td>
    <td>{mark(r['in_counties'])}</td>
    <td>{mark(r['in_systems'])}</td>
    <td>{mark(r['in_regions'])}</td>
</tr>
"""

    html += """
</table>

</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

# -----------------------------
# RUN
# -----------------------------
generate_html(flagged)

print(f"Datacheck complete.")
print(f"{len(flagged)} missing/flagged routes found.")
print(f"Output file: {OUTPUT_FILE}")
