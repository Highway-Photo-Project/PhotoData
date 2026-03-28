import os
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = Path("PhotoData")  # adjust if needed
COUNTIES_DIR = BASE_DIR / "_counties"
SYSTEMS_DIR  = BASE_DIR / "_systems"
REGIONS_DIR  = BASE_DIR / "_regions"

OUTPUT_FILE = "datacheck.html"

VALID_EXTENSIONS = (".csv", ".txt", ".list")  # adjust if needed

# -----------------------------
# NORMALIZATION
# -----------------------------
def normalize(line):
    return line.strip().upper()

# -----------------------------
# READ ROUTES FROM FILE CONTENTS
# -----------------------------
def get_routes(folder):
    routes_list = []   # preserves order (important)
    routes_set = set()

    for root, _, files in os.walk(folder):
        for file in sorted(files):
            if file.endswith(VALID_EXTENSIONS):
                filepath = Path(root) / file

                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()

                        # skip empty or comments
                        if not line or line.startswith("#"):
                            continue

                        norm = normalize(line)

                        routes_list.append(norm)
                        routes_set.add(norm)

    return routes_list, routes_set

# -----------------------------
# LOAD DATA
# -----------------------------
counties_list, counties_set = get_routes(COUNTIES_DIR)
systems_list, systems_set   = get_routes(SYSTEMS_DIR)
regions_list, regions_set   = get_routes(REGIONS_DIR)

# -----------------------------
# BUILD RESULTS (preserve order)
# -----------------------------
results = []

for route in counties_list:
    results.append({
        "route": route,
        "in_counties": True,
        "in_systems": route in systems_set,
        "in_regions": route in regions_set
    })

# add extras not in counties
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

print(f"Datacheck complete. {len(flagged)} issues found.")
print(f"Output: {OUTPUT_FILE}")
