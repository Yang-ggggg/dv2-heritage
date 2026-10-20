"""Add the October 2026 Trove API refresh to the site data.

Run AFTER build_trove_time_data.py and build_state_data.py.
Input: data/trove_refresh_2026-10-20/ (written by colab_trove_refresh.ipynb, Trove API version 3,
       harvested 20 October 2026 09:26 UTC, 26 calls, same parameters as Tim Sherratt's harvester).
Output:
  data/trove_states.csv   articles_2026 replaces articles_2025; per resident and growth recomputed
  data/trove_by_year.csv  articles_2026 replaces articles_2025 (C3, C6 newspaper panel)
  data/trove_growth.csv   one new row, harvest_type "api_refresh" (C1)
Every number used on the page is printed at the end.
Usage: python build_trove_refresh.py <site folder>
"""
import sys
import pandas as pd

site_folder = sys.argv[1] if len(sys.argv) > 1 else "."
refresh_folder = f"{site_folder}/data/trove_refresh_2026-10-20"
HARVEST_DATE = "2026-10-20"

states_refresh = pd.read_csv(f"{refresh_folder}/trove_states_refresh.csv")
totals_refresh = pd.read_csv(f"{refresh_folder}/trove_totals_refresh.csv").set_index("harvest_type")["total"]
years_refresh = pd.read_csv(f"{refresh_folder}/trove_by_year_refresh.csv").set_index("year")["total"]
all_articles = int(totals_refresh["all"])
corrected_articles = int(totals_refresh["has:corrections"])
assert states_refresh["total"].sum() == all_articles, "state rows do not add up to the total"
assert years_refresh.sum() == all_articles, "year rows do not add up to the total"

# ---------------------------------------------------------------- states (M1, M2, C10)
states_refresh["state"] = states_refresh["state"].replace({"ACT": "Australian Capital Territory"})
not_a_place = ["International", "National"]
excluded = states_refresh[states_refresh["state"].isin(not_a_place)]
print(f"States: dropped {', '.join(excluded['state'])} = {int(excluded['total'].sum()):,} articles "
      f"({excluded['total'].sum() / all_articles:.2%} of all); they are not places on the map")
states_refresh = states_refresh[~states_refresh["state"].isin(not_a_place)].set_index("state")["total"]

states = pd.read_csv(f"{site_folder}/data/trove_states.csv").set_index("state")
assert set(states.index) == set(states_refresh.index), "state names do not match"
old_2025 = states.pop("articles_2025") if "articles_2025" in states else None
states["articles_2026"] = states_refresh
states["articles_per_resident"] = (states["articles_2026"] / states["population_mar2026"]).round(1)
states["growth_times"] = (states["articles_2026"] / states["articles_2011"]).round(1)
assert not states.isna().any().any(), "missing values in the state table"
states = states[["articles_2011", "articles_2026", "population_mar2026", "lon", "lat",
                 "articles_per_resident", "growth_times"]].sort_values("articles_per_resident", ascending=False)
states.reset_index().to_csv(f"{site_folder}/data/trove_states.csv", index=False)
print(states[["articles_2011", "articles_2026", "articles_per_resident", "growth_times"]].to_string())
if old_2025 is not None:
    print("Change since February 2025 (articles):")
    print((states["articles_2026"] - old_2025).sort_values(ascending=False).to_string())

# ---------------------------------------------------------------- years (C3, C6)
by_year = pd.read_csv(f"{site_folder}/data/trove_by_year.csv").set_index("year")
by_year = by_year.drop(columns=["articles_2025"], errors="ignore")
by_year = by_year.join(years_refresh.rename("articles_2026"), how="outer")[["articles_2026", "articles_2011"]]
by_year.index.name = "year"
print(f"Years: {len(by_year)} rows, {by_year.index.min()} to {by_year.index.max()}; "
      f"empty 2026 values: {int(by_year.articles_2026.isna().sum())}, empty 2011 values: {int(by_year.articles_2011.isna().sum())} "
      "(left empty, never 0)")
by_year.reset_index().to_csv(f"{site_folder}/data/trove_by_year.csv", index=False, float_format="%.0f")

# ---------------------------------------------------------------- growth (C1)
growth = pd.read_csv(f"{site_folder}/data/trove_growth.csv")
growth = growth[growth["harvest_type"] != "api_refresh"]          # safe to run twice
last_weekly = growth.iloc[-1]
growth = pd.concat([growth, pd.DataFrame([{"harvest_date": HARVEST_DATE, "total_articles": all_articles,
                                           "harvest_type": "api_refresh"}])], ignore_index=True)
growth.to_csv(f"{site_folder}/data/trove_growth.csv", index=False)
print(f"Growth: {len(growth)} rows; gap from {last_weekly.harvest_date} to {HARVEST_DATE} has no harvests (shown dashed)")

# ---------------------------------------------------------------- numbers used in the text
first = growth.iloc[0]
print("\nNUMBERS FOR THE PAGE")
print(f"All articles, October 2026: {all_articles:,} = {all_articles / 1e6:.1f} million")
print(f"Growth since {first.harvest_date}: {all_articles / first.total_articles:.2f} times")
print(f"Added since {last_weekly.harvest_date}: {(all_articles - last_weekly.total_articles) / 1e6:.1f} million")
for start, end in [("2016-12-14", "2025-02-16")]:
    a = growth.set_index("harvest_date").loc[[start, end], "total_articles"]
    years = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25
    print(f"Average added per year, {start} to {end}: {(a[end] - a[start]) / years / 1e6:.1f} million")
print(f"Articles with corrections: {corrected_articles:,} = {corrected_articles / 1e6:.1f} million "
      f"({corrected_articles / all_articles:.1%} of all)")
y1954, y1955 = years_refresh[1954], years_refresh[1955]
print(f"1954: {y1954:,}; 1955: {y1955:,} = {y1955 / 1e6:.2f} million; drop {1 - y1955 / y1954:.1%}")
peak_year = years_refresh.idxmax()
print(f"Peak year: {peak_year} with {years_refresh.max():,}")
print(f"Share of articles from 1955 or later: {years_refresh[years_refresh.index >= 1955].sum() / all_articles:.2%}")
