"""Build data/nma_hexbins.geojson for M3: objects made in Australia, counted in equal-area hexagons.

Usage: python build_nma_hexbins.py <nma_places.csv> <site folder> [hexagon radius in km]
The hexagons are drawn in the same projection the map uses (d3 conicEqualArea, parallels -18 and -36,
rotate -132), so every hexagon covers the same area on the ground and on the screen.
"""
import json
import math
import sys

import pandas as pd

from display_titles import readable_place_title

places_path, site_folder = sys.argv[1], sys.argv[2]
HEXAGON_RADIUS_KM = float(sys.argv[3]) if len(sys.argv) > 3 else 100.0
EARTH_RADIUS_KM = 6371.0

# Places that cover far more than one hexagon (the whole country, a whole state, or a region hundreds of
# kilometres wide). A single point for them would create a false hotspot, so they are left out.
TOO_LARGE_TO_PLACE = {
    "Australia", "Victoria, Australia", "New South Wales, Australia", "Tasmania, Australia",
    "South Australia, Australia", "Queensland, Australia", "Western Australia, Australia",
    "Northern Territory, Australia", "Canning Stock Route, Australia", "Central Australia, Australia",
    "Southern central, Australia", "North-west NSW, Australia", "Nullarbor Plain, Australia",
    "Northern Australia, Australia", "Western Desert, Australia", "Murray River, Australia",
    "Southern South Australia, Australia", "Central Australia, Northern Territory, Australia",
    "Kimberley, Western Australia, Australia", "North Western Australia, Western Australia, Australia",
    "Cape York Peninsula, Queensland, Australia", "South-west Western Australia, Western Australia, Australia",
}
MAINLAND_AND_TASMANIA = {"min_lat": -44.0, "max_lat": -9.0, "min_lon": 112.0, "max_lon": 154.0}

# --- d3.geoConicEqualArea with the page's parameters (unit sphere) ---
first_parallel, second_parallel, central_meridian = math.radians(-18), math.radians(-36), 132.0
sine_first = math.sin(first_parallel)
cone_constant = (sine_first + math.sin(second_parallel)) / 2
c_constant = 1 + sine_first * (2 * cone_constant - sine_first)
rho_zero = math.sqrt(c_constant) / cone_constant


def project(longitude, latitude):
    lam = math.radians(longitude - central_meridian)
    rho = math.sqrt(c_constant - 2 * cone_constant * math.sin(math.radians(latitude))) / cone_constant
    return (rho * math.sin(lam * cone_constant) * EARTH_RADIUS_KM,
            (rho_zero - rho * math.cos(lam * cone_constant)) * EARTH_RADIUS_KM)


def unproject(x_km, y_km):
    x, y = x_km / EARTH_RADIUS_KM, y_km / EARTH_RADIUS_KM
    rho_zero_minus_y = rho_zero - y
    lam = math.atan2(x, abs(rho_zero_minus_y)) * math.copysign(1, rho_zero_minus_y)
    phi = math.asin((c_constant - (x * x + rho_zero_minus_y ** 2) * cone_constant ** 2) / (2 * cone_constant))
    return math.degrees(lam / cone_constant) + central_meridian, math.degrees(phi)


# --- pointy-top hexagons in axial coordinates ---
def hexagon_of(x_km, y_km):
    q = (math.sqrt(3) / 3 * x_km - y_km / 3) / HEXAGON_RADIUS_KM
    r = (2 / 3 * y_km) / HEXAGON_RADIUS_KM
    cube_x, cube_z = q, r
    cube_y = -cube_x - cube_z
    rounded = [round(cube_x), round(cube_y), round(cube_z)]
    differences = [abs(rounded[0] - cube_x), abs(rounded[1] - cube_y), abs(rounded[2] - cube_z)]
    if differences[0] > differences[1] and differences[0] > differences[2]:
        rounded[0] = -rounded[1] - rounded[2]
    elif differences[1] > differences[2]:
        rounded[1] = -rounded[0] - rounded[2]
    else:
        rounded[2] = -rounded[0] - rounded[1]
    return rounded[0], rounded[2]


def hexagon_ring(q, r):
    centre_x = HEXAGON_RADIUS_KM * math.sqrt(3) * (q + r / 2)
    centre_y = HEXAGON_RADIUS_KM * 1.5 * r
    # clockwise when north is up: d3 treats a clockwise ring as the inside of the polygon
    corners = [unproject(centre_x + HEXAGON_RADIUS_KM * math.cos(math.radians(angle)),
                         centre_y + HEXAGON_RADIUS_KM * math.sin(math.radians(angle)))
               for angle in (90, 30, -30, -90, -150, 150)]
    return [[round(lon, 4), round(lat, 4)] for lon, lat in corners + corners[:1]]


places = pd.read_csv(places_path)
print(f"Places in the harvest: {len(places):,}; objects with a geocoded place: {places['objects'].sum():,}")
australian = places[places["in_australia"]].copy()
print(f"Made in Australia: {len(australian):,} places, {australian['objects'].sum():,} objects; "
      f"outside Australia: {places.loc[~places['in_australia'], 'objects'].sum():,} objects")

too_large = australian["place_title"].isin(TOO_LARGE_TO_PLACE)
print(f"Left out, place too large to show as one point: {too_large.sum()} places, "
      f"{australian.loc[too_large, 'objects'].sum():,} objects")
australian = australian[~too_large]
inside_box = (australian["lat"].between(MAINLAND_AND_TASMANIA["min_lat"], MAINLAND_AND_TASMANIA["max_lat"])
              & australian["lon"].between(MAINLAND_AND_TASMANIA["min_lon"], MAINLAND_AND_TASMANIA["max_lon"]))
for _, place in australian[~inside_box].iterrows():
    print(f"Left out, outside the mainland and Tasmania: {place['place_title']} ({place['lat']}, {place['lon']}), "
          f"{place['objects']} objects")
australian = australian[inside_box]
print(f"Mapped: {len(australian):,} places, {australian['objects'].sum():,} objects")

australian[["x_km", "y_km"]] = australian.apply(lambda p: pd.Series(project(p["lon"], p["lat"])), axis=1)
australian["hexagon"] = australian.apply(lambda p: hexagon_of(p["x_km"], p["y_km"]), axis=1)
hexagons = australian.sort_values("objects", ascending=False).groupby("hexagon").agg(
    objects=("objects", "sum"), places=("place_id", "size"), largest_place=("place_title", "first"),
    largest_place_objects=("objects", "first")).reset_index()

features = [{
    "type": "Feature",
    "properties": {"objects": int(row.objects), "places": int(row.places),
                   "largest_place": readable_place_title(row.largest_place.replace(", Australia", "")),
                   "largest_place_objects": int(row.largest_place_objects)},
    "geometry": {"type": "Polygon", "coordinates": [hexagon_ring(*row.hexagon)]},
} for row in hexagons.itertuples()]
with open(f"{site_folder}/data/nma_hexbins.geojson", "w") as output_file:
    json.dump({"type": "FeatureCollection", "features": features}, output_file, separators=(",", ":"))

area = 3 * math.sqrt(3) / 2 * HEXAGON_RADIUS_KM ** 2
print(f"Hexagon radius {HEXAGON_RADIUS_KM:.0f} km, area {area:,.0f} square km; {len(hexagons)} hexagons hold objects")
print("Objects per hexagon, quantiles:", hexagons["objects"].quantile([.25, .5, .75, .9, .95, 1]).round(0).tolist())
print(hexagons.sort_values("objects", ascending=False).head(8)[["objects", "places", "largest_place"]].to_string())
