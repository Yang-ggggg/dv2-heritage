"""Write specs/c6_small_multiples.vl.json: five panels on one shared scale, plus a how-to-read cell.

The panels are generated from one template so that every panel has exactly the same size, scale and axes.
"""
import json
import sys

site_folder = sys.argv[1]
SHARED_SCALE_MAXIMUM = 55          # per cent; the largest value anywhere is 51.7 (archive files, 1930s)
PANEL_WIDTH, PANEL_HEIGHT = 290, 170
SANS = "'Source Sans 3', 'Helvetica Neue', Arial, sans-serif"

panels = [
    ("newspapers", "Newspaper articles", "By year of publication, February 2025", "#3182bd",
     [("Falls from 7.5% in the 1950s", 1805, 44), ("to 0.7% in the 1960s", 1805, 39)]),
    ("periodicals", "Periodical issues", "By date of the issue, March 2024", "#3182bd",
     [("28% of issues are from", 1805, 44), ("1955 or later", 1805, 39)]),
    ("archive_files", "Archive files", "By start of date range, September 2026", "#e6550d",
     [("52% of files begin", 1805, 44), ("in the 1930s", 1805, 39)]),
    ("manuscripts", "Manuscript collections", "By start of collection, March 2023", "#3182bd",
     [("No decade has more than", 1805, 44), ("8.3% of collections", 1805, 39)]),
    ("oral_histories", "Oral history recordings", "By year recorded, December 2023", "#3182bd",
     [("89% were recorded in", 1805, 44), ("the 1970s to 2010s", 1805, 39)]),
]


def panel_spec(collection_type, panel_title, panel_subtitle, bar_colour, notes):
    return {
        "title": {"text": panel_title, "subtitle": panel_subtitle, "font": SANS, "fontSize": 15,
                  "subtitleFontSize": 12, "anchor": "start", "offset": 8},
        "width": PANEL_WIDTH, "height": PANEL_HEIGHT,
        "transform": [{"filter": f"datum.collection_type == '{collection_type}'"},
                      {"calculate": "datum.decade + 10", "as": "decade_end"}],
        "encoding": {
            "x": {"field": "decade", "type": "quantitative",
                  "scale": {"domain": [1800, 2030], "nice": False},
                  "axis": {"title": None, "values": [1800, 1850, 1900, 1950, 2000], "format": "d", "grid": False}},
        },
        "layer": [
            {"mark": {"type": "bar", "color": bar_colour, "binSpacing": 0},
             "encoding": {
                 "x2": {"field": "decade_end"},
                 "y": {"field": "share_percent", "type": "quantitative",
                       "scale": {"domain": [0, SHARED_SCALE_MAXIMUM]},
                       "axis": {"title": None, "values": [0, 25, 50], "labelExpr": "datum.value + '%'"}},
                 "y2": {"datum": 0},
                 "tooltip": [
                     {"field": "panel_title", "title": "Collection"},
                     {"field": "year_measured", "title": "Year measured"},
                     {"field": "decade", "title": "Decade begins", "format": "d"},
                     {"field": "items", "title": "Items", "format": ","},
                     {"field": "share_percent", "title": "Share of its items (per cent)", "format": ".1f"}]}},
            {"data": {"values": [{"decade": x, "share": y, "text": text} for text, x, y in notes]},
             "mark": {"type": "text", "align": "left", "baseline": "middle", "fontSize": 13, "fontWeight": 700},
             "encoding": {"x": {"field": "decade", "type": "quantitative"},
                          "y": {"field": "share", "type": "quantitative"},
                          "text": {"field": "text"}}},
        ],
    }


key_lines = ["Each panel is one kind of collection.", "Each bar is one decade.",
             "Bar height is the share of its items.", "Every panel uses the same scale."]
key_cell = {
    "width": PANEL_WIDTH, "height": PANEL_HEIGHT,
    "data": {"values": [{"line": 0, "text": "How to read"}] +
                       [{"line": index + 1, "text": text} for index, text in enumerate(key_lines)]},
    "encoding": {
        "x": {"datum": 0, "type": "quantitative", "scale": {"domain": [0, 1]}, "axis": None},
        "y": {"field": "line", "type": "quantitative", "scale": {"domain": [6.5, -0.5]}, "axis": None},
        "text": {"field": "text"},
    },
    "layer": [
        {"transform": [{"filter": "datum.line == 0"}],
         "mark": {"type": "text", "align": "left", "baseline": "middle", "fontSize": 15, "fontWeight": 700}},
        {"transform": [{"filter": "datum.line > 0"}],
         "mark": {"type": "text", "align": "left", "baseline": "middle", "fontSize": 13}},
    ],
}

specification = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": {
        "text": ["Newspapers stop at the copyright wall.", "Other collections reach later."],
        "subtitle": ["Share of each collection's items, by decade of content",
                     "(1800 to 2029). All panels use the same scale."],
    },
    "data": {"url": "data/decade_shares.csv",
             "format": {"type": "csv", "parse": {"decade": "number", "items": "number", "share_percent": "number"}}},
    "spacing": 36,
    "vconcat": [
        {"hconcat": [panel_spec(*panels[0]), panel_spec(*panels[1]), panel_spec(*panels[2])], "spacing": 36},
        {"hconcat": [panel_spec(*panels[3]), panel_spec(*panels[4]), key_cell], "spacing": 36},
    ],
}
with open(f"{site_folder}/specs/c6_small_multiples.vl.json", "w") as output_file:
    json.dump(specification, output_file, indent=2)
    output_file.write("\n")
print("wrote c6_small_multiples.vl.json")
