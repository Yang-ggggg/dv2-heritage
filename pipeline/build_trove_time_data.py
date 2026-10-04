"""Build data/trove_growth.csv (C1) and data/trove_by_year.csv (C3) from Tim Sherratt's Trove harvests."""
import glob, io, re, subprocess, sys
import pandas as pd

weekly_repo = sys.argv[1] if len(sys.argv) > 1 else "trove-newspaper-totals"
historical_repo = sys.argv[2] if len(sys.argv) > 2 else "trove-newspaper-totals-historical"
output_folder = sys.argv[3] if len(sys.argv) > 3 else "data"

# C1: total articles at each harvest. 9 historical snapshots + every weekly version in the git history
growth_rows = []
for path in sorted(glob.glob(f"{historical_repo}/data/total_articles_by_year_*.csv")):
    harvest_date = pd.to_datetime(re.search(r"_(\d{8})\.csv$", path).group(1))
    growth_rows.append({"harvest_date": str(harvest_date.date()), "total_articles": int(pd.read_csv(path)["total"].sum()), "harvest_type": "snapshot"})
git_log = subprocess.run(["git", "-C", weekly_repo, "log", "--format=%H %ad", "--date=short", "--", "data/total_articles_by_year.csv"],
                         capture_output=True, text=True, check=True).stdout.split("\n")
for line in filter(None, git_log):
    commit_hash, commit_date = line.split()
    file_text = subprocess.run(["git", "-C", weekly_repo, "show", f"{commit_hash}:data/total_articles_by_year.csv"],
                               capture_output=True, text=True, check=True).stdout
    growth_rows.append({"harvest_date": commit_date, "total_articles": int(pd.read_csv(io.StringIO(file_text))["total"].sum()), "harvest_type": "weekly"})
growth = pd.DataFrame(growth_rows).sort_values("harvest_date")
growth.to_csv(f"{output_folder}/trove_growth.csv", index=False)
print("C1 rows:", len(growth), growth.groupby("harvest_type").size().to_dict())
print(growth.head(3).to_string(index=False)); print(growth.tail(2).to_string(index=False))

# C3: articles by publication year, Feb 2025 and Apr 2011
articles_2025 = pd.read_csv(f"{weekly_repo}/data/total_articles_by_year.csv").set_index("year")["total"]
articles_2011 = pd.read_csv(f"{historical_repo}/data/total_articles_by_year_20110412.csv").set_index("year")["total"]
by_year = pd.DataFrame({"articles_2025": articles_2025, "articles_2011": articles_2011})
by_year.index.name = "year"
by_year = by_year.reset_index()      # years missing in one harvest stay empty (never filled with 0)
by_year.to_csv(f"{output_folder}/trove_by_year.csv", index=False)
print("C3 rows:", len(by_year), "years", by_year.year.min(), "-", by_year.year.max(),
      "| empty 2011 values:", by_year.articles_2011.isna().sum(), "| empty 2025 values:", by_year.articles_2025.isna().sum())
