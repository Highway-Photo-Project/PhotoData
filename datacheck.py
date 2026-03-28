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

# File types to include
VALID_EXTENSIONS = (".json", ".csv", ".txt")

# -----------------------------
# NORMALIZATION
# -----------------------------
def normalize(name):
    """Normalize route names for comparison."""
    return name.lower().replace(" ", "").replace("-", "").replace("_", "")

# -----------------------------
# ROUTE COLLECTION
# -----------------------------
def get_routes(folder):
    """Return ordered list and set of normalized route names."""
    routes_list = []
    routes_set = set()

    for root, _, files in os.walk(folder):
        for file in sorted(files):
            if file.endswith(VALID_EXTENSIONS):
                route_name = os.path.splitext(file)[0]
                norm = normalize(route_name)

                routes_list.append((route_name, norm))
                routes_set.add(norm)

    return routes_list, routes_set

# -----------------------------
# LOAD DATA
# -----------------------------
counties_list, counties_set = get_routes(COUNTIES_DIR)
systems_list, systems_set   = get_routes(SYSTEMS_DIR)
regions_list, regions_set   = get_routes(REGIONS_DIR)

# -----------------------------
# BUILD RESULTS (preserve counties order)
# -----------------------------
results = []

for original_name, norm in counties_list:
    results.append({
        "route": original_name,
        "in_counties": True,
        "in_systems": norm in systems_set,
        "in_regions": norm in regions_set
    })

# Add routes missing from counties but present elsewhere
extra_routes = (systems_set | regions_set) - counties_set

for norm in sorted(extra_routes):
    results.append({
        "route": norm,
        "in_counties": False,
        "in_systems": norm in systems_set,
        "in_regions": norm in regions_set
    })

# -----------------------------
# FILTER FLAGGED ONLY
# -----------------------------
flagged = [
    r for r in results
    if not (r["in_counties"] and r["in_systems"] and r["in_regions"])
]

# -----------------------------
# HTML GENERATION
# -----------------------------
def generate_html(data):
    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Route Data Check</title>
<style>
    body {
        font-family: Arial, sans-serif;
    }
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid black;
        padding: 8px;
        text-align: left;
        word-wrap: break-word;
        max-width: 300px;
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

<h2>Route Data Check - Missing Entries</h2>

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
        row_class = "missing"

        html += f"""
<tr class="{row_class}">
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

print(f"Datacheck complete. Output saved to: {OUTPUT_FILE}")
