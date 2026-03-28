import os
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = Path(".")
COUNTIES_DIR = BASE_DIR / "_counties"
SYSTEMS_DIR  = BASE_DIR / "_systems"
REGIONS_DIR  = BASE_DIR / "_regions"

OUTPUT_FILE = "datacheck.html"

# -----------------------------
# PARSE FILE
# -----------------------------
def parse_file(filepath, folder_type):
    routes = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return routes

    for line in lines[1:]:  # skip header
        line = line.strip()

        if not line:
            continue

        parts = line.split(";")

        try:
            if folder_type == "counties":
                region = parts[0].strip()
                route  = parts[1].strip()

            elif folder_type in ("systems", "regions"):
                region = parts[1].strip()
                route  = parts[2].strip()

            else:
                continue

            key = f"{region.upper()};{route.upper()}"
            routes.append(key)

        except IndexError:
            print(f"⚠️ Skipping bad line in {filepath}: {line}")

    return routes

# -----------------------------
# LOAD ROUTES
# -----------------------------
def get_routes(folder, folder_type):
    routes_list = []
    routes_set = set()

    print(f"\nScanning: {folder}")

    for root, _, files in os.walk(folder):
        for file in files:
            filepath = Path(root) / file

            try:
                entries = parse_file(filepath, folder_type)

                for e in entries:
                    routes_list.append(e)
                    routes_set.add(e)

            except Exception as e:
                print(f"❌ Error reading {filepath}: {e}")

    print(f"✔ Found {len(routes_set)} unique routes in {folder_type}")

    # Show sample
    print("Sample:", list(routes_set)[:5])

    return routes_list, routes_set

# -----------------------------
# LOAD DATA
# -----------------------------
counties_list, counties_set = get_routes(COUNTIES_DIR, "counties")
systems_list, systems_set   = get_routes(SYSTEMS_DIR, "systems")
regions_list, regions_set   = get_routes(REGIONS_DIR, "regions")

# -----------------------------
# DEBUG COUNTS
# -----------------------------
print("\n--- SUMMARY ---")
print("Counties:", len(counties_set))
print("Systems :", len(systems_set))
print("Regions :", len(regions_set))

# -----------------------------
# BUILD RESULTS
# -----------------------------
all_routes = counties_set | systems_set | regions_set

results = []

for route in sorted(all_routes):
    results.append({
        "route": route,
        "in_counties": route in counties_set,
        "in_systems": route in systems_set,
        "in_regions": route in regions_set
    })

# -----------------------------
# FLAGGED
# -----------------------------
flagged = [
    r for r in results
    if not (r["in_counties"] and r["in_systems"] and r["in_regions"])
]

print(f"\n🚨 Flagged routes: {len(flagged)}")

# Show a few
for r in flagged[:10]:
    print(r)

# -----------------------------
# HTML
# -----------------------------
def generate_html(data):
    html = """
<html>
<head>
<style>
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid black; padding: 6px; }
.missing { background-color: #ffcccc; }
</style>
</head>
<body>

<h2>Missing Routes</h2>

<table>
<tr>
<th>Route</th>
<th>Counties</th>
<th>Systems</th>
<th>Regions</th>
</tr>
"""

    def mark(x):
        return "✔" if x else "✖"

    for r in data:
        html += f"""
<tr class="missing">
<td>{r['route']}</td>
<td>{mark(r['in_counties'])}</td>
<td>{mark(r['in_systems'])}</td>
<td>{mark(r['in_regions'])}</td>
</tr>
"""

    html += "</table></body></html>"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

generate_html(flagged)

print(f"\n✅ HTML written to {OUTPUT_FILE}")
