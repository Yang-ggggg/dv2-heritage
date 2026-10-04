# ============================================================
# FIT3179 DV2 - National Museum of Australia (NMA) object places
# Run in Google Colab (any Google account). Takes about 30-60 minutes.
# Output: nma_places.csv (one row per place where objects were made)
#         nma_harvest_log.txt (row counts for the DV2 log)
# Licence of the data: CC BY-NC. Required credit on the page:
# "This visualisation was developed using the National Museum of Australia's Collection API."
# ============================================================
import time, json, requests
import pandas as pd

api_base = "https://data.nma.gov.au/object"
page_size = 100
seconds_between_requests = 1.1          # no API key = 1 request per second

def get_page(offset, attempts=4):
    for attempt in range(attempts):
        try:
            response = requests.get(api_base, params={"text": "*", "limit": page_size, "offset": offset}, timeout=60)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"failed at offset {offset}")

first_page = get_page(0)
total_objects = first_page["meta"]["results"]
print("objects in the API:", total_objects)

object_rows = []
for offset in range(0, total_objects, page_size):
    page = first_page if offset == 0 else get_page(offset)
    for item in page.get("data", []):
        production_places = [place for place in item.get("spatial", []) if place.get("interactionType") == "Production" and place.get("geo")]
        first_place = production_places[0] if production_places else None
        object_rows.append({
            "object_id": item.get("id"),
            "object_types": "|".join(item.get("additionalType", []) or []),
            "has_image": bool(item.get("hasVersion")),
            "place_id": first_place.get("id") if first_place else None,
            "place_title": first_place.get("title") if first_place else None,
            "place_geo": first_place.get("geo") if first_place else None,
        })
    if offset % 5000 == 0:
        print(f"{offset:>6} / {total_objects}  rows so far: {len(object_rows)}")
    time.sleep(seconds_between_requests)

objects = pd.DataFrame(object_rows).drop_duplicates("object_id")
objects.to_csv("nma_objects_raw.csv", index=False)       # keep a copy for checking

with_place = objects.dropna(subset=["place_geo"]).copy()
with_place[["lat", "lon"]] = with_place["place_geo"].str.split(",", expand=True).astype(float)
places = (with_place.groupby(["place_id", "place_title", "lat", "lon"])
          .agg(objects=("object_id", "size"), objects_with_image=("has_image", "sum"))
          .reset_index().sort_values("objects", ascending=False))
places["in_australia"] = places["place_title"].str.contains("Australia", na=False)
places.to_csv("nma_places.csv", index=False)

log_lines = [
    f"Harvest date: {pd.Timestamp.now().date()}",
    f"Objects reported by API: {total_objects}",
    f"Objects harvested (unique ids): {len(objects)}",
    f"Objects with a geocoded place of production: {len(with_place)}",
    f"Distinct production places: {len(places)}",
    f"Objects made at places in Australia: {int(places.loc[places.in_australia, 'objects'].sum())}",
    f"Objects made at places outside Australia: {int(places.loc[~places.in_australia, 'objects'].sum())}",
]
open("nma_harvest_log.txt", "w").write("\n".join(log_lines))
print("\n".join(log_lines))
print(places.head(15).to_string(index=False))

from google.colab import files
files.download("nma_places.csv")
files.download("nma_harvest_log.txt")
