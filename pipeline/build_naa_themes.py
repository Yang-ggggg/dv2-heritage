"""Build the data for C7 (treemap) and C8 (streamgraph): National Archives files by theme.

Usage: python build_naa_themes.py <naa-recently-digitised repo folder> <site folder>
Themes are read from each file's own title (for example "Service Number - QX19641" or
"Nationality - GERMAN : Travelled per - SKAUBRYN"), so no theme is guessed from a series number.
"""
import glob
import re
import sys

import pandas as pd

from display_titles import readable_series_title

naa_repo, site_folder = sys.argv[1], sys.argv[2]
FIRST_MONTH, LAST_MONTH = "2021-04", "2025-04"      # the long run of weekly harvests before the one-year gap
SMALL_SERIES_SHARE = 0.01                           # series under 1% of a theme are grouped in the treemap

weekly_frames = []
for path in sorted(glob.glob(f"{naa_repo}/data/digitised-week-ending-*.csv")):
    week_frame = pd.read_csv(path, dtype=str)
    week_frame["week_ending"] = pd.to_datetime(re.search(r"(\d{8})\.csv$", path).group(1))
    weekly_frames.append(week_frame)
all_rows = pd.concat(weekly_frames, ignore_index=True)
files = all_rows.drop_duplicates("item_id").copy()
print(f"{len(weekly_frames)} weekly files, {len(all_rows):,} rows, {len(files):,} unique files")

series_titles = (pd.concat([pd.read_parquet(p) for p in glob.glob(f"{naa_repo}/years/*.parquet")])
                 .dropna(subset=["series_title"]).drop_duplicates("series").set_index("series")["series_title"])

title = files["title"].fillna("")
years = files["date_range"].fillna("").str.findall(r"\d{4}")
start_year = years.map(lambda found: int(found[0]) if found else None)
end_year = years.map(lambda found: int(found[-1]) if found else None)
covers_second_world_war = (start_year <= 1945) & (end_year >= 1939)

theme_rules = [   # first rule that matches wins
    ("Second World War service records",
     title.str.contains(r"Service Number", case=False) & covers_second_world_war),
    ("Migration and citizenship records",
     title.str.contains(r"Nationality\s*-|Travelled per|passenger list|naturalisation", case=False)),
    ("Photographs", title.str.contains(r"CATEGORY:\s*photograph", case=False)),
    ("Patents", title.str.contains(r"patent", case=False)),
]
files["theme"] = "Other files"
for theme_name, matches in reversed(theme_rules):
    files.loc[matches, "theme"] = theme_name
theme_counts = files["theme"].value_counts()
print("Files by theme:")
for theme_name, count in theme_counts.items():
    print(f"   {theme_name}: {count:,} ({count / len(files):.1%})")

# ---------------------------------------------------------------- C7 treemap: theme -> series
series_by_theme = files.groupby(["theme", "series"]).size().reset_index(name="files")
series_by_theme["theme_files"] = series_by_theme["theme"].map(theme_counts)
large = series_by_theme["files"] >= SMALL_SERIES_SHARE * series_by_theme["theme_files"]
rows = [{"id": "all", "parent": None, "name": "All digitised files", "files": None, "theme": None, "series": None}]
for theme_name, count in theme_counts.items():
    rows.append({"id": theme_name, "parent": "all", "name": theme_name, "files": None, "theme": theme_name, "series": None})
for record in series_by_theme[large].itertuples():
    rows.append({"id": f"{record.theme}|{record.series}", "parent": record.theme,
                 "name": readable_series_title(series_titles.get(record.series, record.series)), "files": record.files,
                 "theme": record.theme, "series": record.series})
grouped = series_by_theme[~large].groupby("theme").agg(files=("files", "sum"), series_count=("series", "size"))
for theme_name, record in grouped.iterrows():
    rows.append({"id": f"{theme_name}|grouped", "parent": theme_name,
                 "name": f"{record.series_count:,} smaller series", "files": int(record.files),
                 "theme": theme_name, "series": "grouped"})
treemap = pd.DataFrame(rows)
treemap["share_percent"] = treemap["files"] / len(files) * 100
treemap["theme_share_percent"] = treemap["theme"].map(theme_counts) / len(files) * 100
treemap.to_csv(f"{site_folder}/data/naa_treemap.csv", index=False)
print(f"C7: {len(treemap)} rows ({int(large.sum())} series shown alone, the rest grouped per theme)")
print(treemap[treemap.files.notna()].sort_values("files", ascending=False).head(8)[["theme", "series", "files", "share_percent"]].to_string(index=False))

# ---------------------------------------------------------------- C8 streamgraph: theme by month
files["date_digitised"] = pd.to_datetime(files["date_digitised"])
files["month"] = files["week_ending"].dt.to_period("M").astype(str)
in_period = files[(files["month"] >= FIRST_MONTH) & (files["month"] <= LAST_MONTH)]
print(f"C8: {len(in_period):,} files in {FIRST_MONTH} to {LAST_MONTH} "
      f"({len(files) - len(in_period):,} files outside this period are not shown)")
recorded_weeks = (files.drop_duplicates("week_ending").groupby("month").size().rename("recorded_weeks"))
all_sundays = pd.Series(pd.date_range(f"{FIRST_MONTH}-01", pd.Period(LAST_MONTH).end_time, freq="W-SUN"))
weeks_in_month = all_sundays.dt.to_period("M").astype(str).value_counts().rename("weeks_in_month")
monthly = in_period.groupby(["month", "theme"]).size().unstack(fill_value=0).stack().rename("files").reset_index()
monthly = monthly.merge(recorded_weeks, on="month").merge(weeks_in_month, left_on="month", right_index=True)
monthly["files_per_week"] = monthly["files"] / monthly["recorded_weeks"]
monthly.to_csv(f"{site_folder}/data/naa_theme_months.csv", index=False)
gaps = monthly.drop_duplicates("month").query("recorded_weeks < weeks_in_month")
print("C8: months with missing weekly harvests (values are averages over recorded weeks):",
      ", ".join(f"{r.month} ({r.recorded_weeks} of {r.weeks_in_month})" for r in gaps.itertuples()))
pivot = monthly.pivot(index="month", columns="theme", values="files_per_week")
pivot["total"] = pivot.sum(axis=1)
share = pivot.div(pivot["total"], axis=0) * 100
print(share.round(0).to_string())
print(pivot["total"].round(0).to_string())
