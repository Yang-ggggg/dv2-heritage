"""Build data/oral_history_icons.csv for C9 (ISOTYPE): 100 microphones, one per about 1% of recordings.

Usage: python build_oral_history_icons.py <trove-oral-histories.csv> <site folder>
Status (ordinal): not online < listen online, no transcript < online with a transcript.
"""
import math
import sys

import pandas as pd

source_path, site_folder = sys.argv[1], sys.argv[2]
recordings = pd.read_csv(source_path, usecols=["fulltext_url", "transcript"])
online = recordings["fulltext_url"].notna()
has_transcript = recordings["transcript"] == 1
print(f"Recordings: {len(recordings):,}; online: {online.sum():,}; with transcript: {has_transcript.sum():,}; "
      f"transcript but not online: {(has_transcript & ~online).sum()}")

counts = {
    "Online with a transcript": int((online & has_transcript).sum()),
    "Listen online, no transcript": int((online & ~has_transcript).sum()),
    "Not online": int((~online).sum()),
}
assert sum(counts.values()) == len(recordings)

# largest-remainder rounding so the icons add up to exactly 100
exact = {status: count / len(recordings) * 100 for status, count in counts.items()}
icons = {status: math.floor(value) for status, value in exact.items()}
for status in sorted(exact, key=lambda s: exact[s] - icons[s], reverse=True)[:100 - sum(icons.values())]:
    icons[status] += 1
for status in counts:
    print(f"   {status}: {counts[status]:,} recordings = {exact[status]:.1f}% -> {icons[status]} icons")
print(f"One icon = {len(recordings) / 100:.1f} recordings")

rows, position = [], 0
for status in counts:                               # transcript first, so the rare group is read first
    for _ in range(icons[status]):
        row, column = divmod(position, 10)
        rows.append({"position": position, "row": row, "column": column, "status": status,
                     "recordings_in_group": counts[status], "share_percent": round(exact[status], 1)})
        position += 1
pd.DataFrame(rows).to_csv(f"{site_folder}/data/oral_history_icons.csv", index=False)
