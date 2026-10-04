"""Build data/trove_states.csv for the two state maps (M1 proportional symbols, M2 choropleth).

Inputs (download first, see README):
  - wragge/trove-newspaper-totals (git clone)            -> Feb 2025 articles by state
  - wragge/trove-newspaper-totals-historical (git clone) -> Apr 2011 articles by state
  - ABS 310104.xlsx (Mar 2026 estimated resident population)
  - raw/state_points.csv (inner point of each state, made with mapshaper -points inner)
"""
import sys
import pandas as pd

trove_weekly_repo = sys.argv[1] if len(sys.argv) > 1 else "trove-newspaper-totals"
trove_historical_repo = sys.argv[2] if len(sys.argv) > 2 else "trove-newspaper-totals-historical"
abs_population_file = sys.argv[3] if len(sys.argv) > 3 else "raw/310104.xlsx"
state_points_file = sys.argv[4] if len(sys.argv) > 4 else "raw/state_points.csv"
output_file = sys.argv[5] if len(sys.argv) > 5 else "site/data/trove_states.csv"

# Trove uses "ACT"; ABS and the boundary file use the full name
trove_to_abs_state_name = {"ACT": "Australian Capital Territory"}

articles_2025 = pd.read_csv(f"{trove_weekly_repo}/data/total_articles_by_year_and_state.csv")
articles_2011 = pd.read_csv(f"{trove_historical_repo}/data/total_articles_by_state_and_year_20110412.csv")

articles_2025_by_state = articles_2025.groupby("state")["total"].sum()
articles_2011_by_state = articles_2011.groupby("state")["total"].sum()
print("Feb 2025 total (all rows):", articles_2025_by_state.sum())

# "International" and "National" are not places on the map -> excluded, and logged
not_a_place = ["International", "National"]
excluded_articles = articles_2025_by_state.reindex(not_a_place).fillna(0).sum()
print("Excluded International + National articles (Feb 2025):", int(excluded_articles))
articles_2025_by_state = articles_2025_by_state.drop(not_a_place, errors="ignore")
articles_2011_by_state = articles_2011_by_state.drop(not_a_place, errors="ignore")

state_table = pd.DataFrame({
    "articles_2011": articles_2011_by_state,
    "articles_2025": articles_2025_by_state,
}).rename(index=trove_to_abs_state_name)
state_table.index.name = "state"

# ABS 310104.xlsx: sheet Data1, row 0 = series names, data rows start after the 9 metadata rows
abs_sheet = pd.read_excel(abs_population_file, sheet_name="Data1", header=None)
series_names = abs_sheet.iloc[0]
abs_rows = abs_sheet.iloc[10:].copy()
abs_rows[0] = pd.to_datetime(abs_rows[0])
latest_quarter = abs_rows.iloc[-1]
print("ABS population quarter used:", latest_quarter[0].date())
population_by_state = {}
for column_index, series_name in series_names.items():
    if isinstance(series_name, str) and series_name.startswith("Estimated Resident Population ;  Persons ;"):
        state_name = series_name.split(";")[2].strip()
        if state_name != "Australia":
            population_by_state[state_name] = int(latest_quarter[column_index])
state_table["population_mar2026"] = pd.Series(population_by_state)

state_points = pd.read_csv(state_points_file).set_index("state")[["lon", "lat"]]
state_table = state_table.join(state_points)

missing_values = state_table.isna().sum().sum()
assert missing_values == 0, f"join problem: {missing_values} missing values"   # never fill, stop instead

state_table["articles_per_resident"] = (state_table["articles_2025"] / state_table["population_mar2026"]).round(1)
state_table["growth_times"] = (state_table["articles_2025"] / state_table["articles_2011"]).round(1)
state_table = state_table.reset_index().sort_values("articles_per_resident", ascending=False)
state_table.to_csv(output_file, index=False)
print(state_table.to_string(index=False))
