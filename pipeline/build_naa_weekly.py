"""Build data/naa_weekly.csv (C2 calendar heat map) from the NAA recently-digitised weekly CSVs."""
import glob, re, sys
import pandas as pd

from display_titles import readable_series_title

naa_repo = sys.argv[1] if len(sys.argv) > 1 else "naa-recently-digitised"
output_file = sys.argv[2] if len(sys.argv) > 2 else "data/naa_weekly.csv"

weekly_frames = []
for path in sorted(glob.glob(f"{naa_repo}/data/digitised-week-ending-*.csv")):
    week_frame = pd.read_csv(path, dtype=str)
    week_frame["week_ending"] = pd.to_datetime(re.search(r"(\d{8})\.csv$", path).group(1))
    weekly_frames.append(week_frame)
all_rows = pd.concat(weekly_frames, ignore_index=True)
unique_files = all_rows.drop_duplicates("item_id")          # a file listed in two weeks counts once (first week)
print("rows", len(all_rows), "-> unique files", len(unique_files))

series_titles = (pd.concat([pd.read_parquet(p) for p in glob.glob(f"{naa_repo}/years/*.parquet")])
                 .dropna(subset=["series_title"]).drop_duplicates("series").set_index("series")["series_title"])

weekly = unique_files.groupby("week_ending").agg(files=("item_id", "size")).reset_index()
top_series = (unique_files.groupby(["week_ending", "series"]).size().reset_index(name="series_files")
              .sort_values("series_files", ascending=False).drop_duplicates("week_ending"))
top_series["top_series_title"] = top_series["series"].map(series_titles).fillna(top_series["series"]).map(readable_series_title)
weekly = weekly.merge(top_series[["week_ending", "series", "top_series_title", "series_files"]], on="week_ending")

# every Sunday between the first and last harvest; weeks with no file are marked "not recorded" (never filled with 0)
all_sundays = pd.DataFrame({"week_ending": pd.date_range(weekly.week_ending.min(), weekly.week_ending.max(), freq="W-SUN")})
calendar = all_sundays.merge(weekly, on="week_ending", how="left")
calendar["status"] = calendar["files"].apply(lambda value: "recorded" if pd.notna(value) else "not recorded")
iso = calendar["week_ending"].dt.isocalendar()
calendar["iso_year"], calendar["iso_week"] = iso["year"], iso["week"]
calendar["week_ending"] = calendar["week_ending"].dt.date
calendar.to_csv(output_file, index=False)
print("weeks", len(calendar), "recorded", (calendar.status == "recorded").sum(), "not recorded", (calendar.status == "not recorded").sum())
print(calendar.sort_values("files", ascending=False).head(3)[["week_ending", "files", "top_series_title", "series_files"]].to_string(index=False))
