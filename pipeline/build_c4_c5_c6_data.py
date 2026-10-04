"""Build the data files for C4 (waffle), C5 (lollipop) and C6 (small multiples).

Usage: python build_c4_c5_c6_data.py <folder holding the cloned source repos> <site folder>
Every filter that changes a row count is printed, so it can be copied into DV2_Log.md.
"""
import json
import re
import sys

import pandas as pd

source_folder, site_folder = sys.argv[1], sys.argv[2]

FIRST_YEAR_PATTERN = re.compile(r"(?<!\d)(1[5-9]\d\d|20[0-2]\d)(?!\d)")
SMALL_MULTIPLES_FIRST_YEAR = 1800
SMALL_MULTIPLES_LAST_YEAR = 2029
MINIMUM_COLLECTIONS_PER_DECADE = 20   # lollipop only shows decades with enough collections


def first_year_in_text(text):
    """First four-digit year (1500-2029) found in a text such as '1920-1970' or '1 March 1902'."""
    if pd.isna(text):
        return None
    match = FIRST_YEAR_PATTERN.search(str(text))
    return int(match.group(1)) if match else None


def decade_of(year):
    return year // 10 * 10


# ---------------------------------------------------------------- manuscripts (S7)
finding_aids = pd.read_csv(f"{source_folder}/nla-finding-aids-data/finding-aids-totals.csv")
print(f"S7 collections: {len(finding_aids):,}")
total_items = int(finding_aids["total_items"].sum())
total_digitised_items = int(finding_aids["total_digitised_items"].sum())
digitised_share = total_digitised_items / total_items
print(f"C4: {total_digitised_items:,} of {total_items:,} items digitised = {digitised_share:.4%}")

squares_digitised = round(digitised_share * 100)
print(f"C4: {squares_digitised} of 100 squares are digitised (rounded to whole per cents)")
waffle_rows = []
for cell_number in range(100):                       # fill from the bottom row, left to right
    row_from_bottom, column = divmod(cell_number, 10)
    waffle_rows.append({
        "row": 9 - row_from_bottom,
        "column": column,
        "status": "Digitised" if cell_number < squares_digitised else "Not digitised",
    })
pd.DataFrame(waffle_rows).to_csv(f"{site_folder}/data/manuscripts_waffle.csv", index=False)

# ---------------------------------------------------------------- C5 lollipop
finding_aids["start_year"] = finding_aids["date_range"].map(first_year_in_text)
no_start_year = int(finding_aids["start_year"].isna().sum())
print(f"C5: {no_start_year} collections have no parsable start year (for example 'undated'); excluded")
dated = finding_aids.dropna(subset=["start_year"]).copy()
dated["decade"] = dated["start_year"].astype(int).map(decade_of)
by_decade = dated.groupby("decade").agg(
    collections=("url", "size"),
    items=("total_items", "sum"),
    digitised_items=("total_digitised_items", "sum"),
).reset_index()
by_decade["share_digitised"] = by_decade["digitised_items"] / by_decade["items"] * 100
by_decade.to_csv(f"{site_folder}/data/manuscripts_by_decade.csv", index=False)
shown = by_decade[by_decade["collections"] >= MINIMUM_COLLECTIONS_PER_DECADE]
print(f"C5: {len(by_decade)} decades in the file; {len(shown)} decades have at least "
      f"{MINIMUM_COLLECTIONS_PER_DECADE} collections ({int(shown['decade'].min())}s to {int(shown['decade'].max())}s); "
      f"{len(by_decade) - len(shown)} decades are not shown")
for label, first_decade, last_decade in [("1760s-1820s", 1760, 1820), ("1930s-1980s", 1930, 1980)]:
    window = shown[shown["decade"].between(first_decade, last_decade)]
    print(f"C5: {label} share digitised from {window['share_digitised'].min():.1f}% to {window['share_digitised'].max():.1f}%")

# ---------------------------------------------------------------- C6 small multiples
shares = []


def add_panel(collection_type, panel_title, year_measured, data_date, counts_by_year):
    counts_by_year = counts_by_year[counts_by_year.index.to_series().between(
        SMALL_MULTIPLES_FIRST_YEAR, SMALL_MULTIPLES_LAST_YEAR)]
    counts_by_decade = counts_by_year.groupby(counts_by_year.index // 10 * 10).sum()
    total = counts_by_decade.sum()
    for decade in range(SMALL_MULTIPLES_FIRST_YEAR, SMALL_MULTIPLES_LAST_YEAR, 10):
        count = int(counts_by_decade.get(decade, 0))
        shares.append({
            "collection_type": collection_type, "panel_title": panel_title,
            "year_measured": year_measured, "data_date": data_date,
            "decade": decade, "items": count, "share_percent": count / total * 100,
        })
    print(f"C6 {collection_type}: {int(total):,} items kept")
    return counts_by_decade, total


newspapers_by_year = pd.read_csv(f"{site_folder}/data/trove_by_year.csv").set_index("year")["articles_2025"]
newspaper_deciles, _ = add_panel("newspapers", "Newspaper articles", "Year of publication", "February 2025", newspapers_by_year)

periodical_issues = pd.read_csv(f"{source_folder}/trove-periodicals-data/periodical-issues.csv", usecols=["date"])
periodical_issues["year"] = periodical_issues["date"].map(first_year_in_text)
print(f"C6 periodicals: {len(periodical_issues):,} issues; {int(periodical_issues['year'].isna().sum())} "
      f"have no usable year (431 empty, 2 implausible years 0196 and 0858); excluded")
periodical_deciles, periodical_total = add_panel(
    "periodicals", "Periodical issues", "Date of the issue", "March 2024",
    periodical_issues.dropna(subset=["year"]).astype({"year": int}).groupby("year").size())
issues_from_1955 = int((periodical_issues["year"] >= 1955).sum())
print(f"C6 periodicals: {issues_from_1955:,} issues from 1955 or later = {issues_from_1955 / periodical_total:.1%}")

archive_files = pd.read_parquet(f"{source_folder}/work/naa_all_weekly.parquet", columns=["item_id", "date_range"])
archive_files = archive_files.drop_duplicates("item_id")
archive_files["year"] = archive_files["date_range"].map(first_year_in_text)
print(f"C6 archive files: {len(archive_files):,} unique files; {int(archive_files['year'].isna().sum())} without a start year")
archive_deciles, archive_total = add_panel(
    "archive_files", "Archive files", "Start of the file's date range", "September 2026",
    archive_files.dropna(subset=["year"]).astype({"year": int}).groupby("year").size())
print(f"C6 archive files: 1930s share {archive_deciles.get(1930, 0) / archive_total:.1%}")

manuscripts = dated[dated["start_year"].between(SMALL_MULTIPLES_FIRST_YEAR, SMALL_MULTIPLES_LAST_YEAR)]
print(f"C6 manuscripts: {len(dated) - len(manuscripts)} collections start before {SMALL_MULTIPLES_FIRST_YEAR}; "
      f"not shown in this chart (shown in C5)")
manuscript_deciles, manuscript_total = add_panel(
    "manuscripts", "Manuscript collections", "Start of the collection", "March 2023",
    manuscripts.astype({"start_year": int}).groupby("start_year").size())
print(f"C6 manuscripts: largest decade share {manuscript_deciles.max() / manuscript_total:.1%}")

oral_histories = pd.read_csv(f"{source_folder}/trove-oral-histories-data/trove-oral-histories.csv", usecols=["date"])
oral_histories["year"] = oral_histories["date"].map(first_year_in_text)
print(f"C6 oral histories: {len(oral_histories):,} recordings; {int(oral_histories['year'].isna().sum())} have no usable date; excluded")
oral_deciles, oral_total = add_panel(
    "oral_histories", "Oral history recordings", "Year of the recording", "December 2023",
    oral_histories.dropna(subset=["year"]).astype({"year": int}).groupby("year").size())
recorded_1970_to_2019 = oral_deciles.loc[1970:2010].sum() / oral_total
print(f"C6 oral histories: 1970s to 2010s share {recorded_1970_to_2019:.1%}")

shares_table = pd.DataFrame(shares)
shares_table.to_csv(f"{site_folder}/data/decade_shares.csv", index=False)
print(f"C6: wrote {len(shares_table)} rows; the largest share anywhere is {shares_table['share_percent'].max():.1f}%")
newspaper_share = shares_table[shares_table["collection_type"] == "newspapers"].set_index("decade")["share_percent"]
print(f"C6 newspapers: 1950s {newspaper_share[1950]:.1f}% then 1960s {newspaper_share[1960]:.1f}%")
