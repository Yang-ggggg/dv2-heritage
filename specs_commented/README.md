# specs_commented: the chart code with short comments

The real chart files are in `specs/`. JSON files cannot hold comments,
so this folder has a copy of each one with short notes added (`.jsonc` = JSON with comments).
The code is exactly the same as in `specs/`. The page does not load these files.

How to read any chart file, from top to bottom:

1. **data**: which file the rows come from
2. **transform**: change the rows first (filter, calculate, fold, lookup, aggregate)
3. **mark**: the shape to draw (point, line, rule, bar, rect, area, text, geoshape)
4. **encoding**: which column goes to which channel (x, y, colour, size, tooltip)
5. **layer / vconcat / hconcat**: more than one view in one chart

| Chart | File | Idiom |
|---|---|---|
| C1 | `c1_trove_growth.vl.jsonc` | Line chart |
| C2 | `c2_naa_calendar.vl.jsonc` | Calendar heat map |
| C3 | `c3_publication_years.vl.jsonc` | Histogram |
| C4 | `c4_manuscripts_waffle.vl.jsonc` | Waffle chart |
| C5 | `c5_manuscripts_lollipop.vl.jsonc` | Lollipop chart |
| C6 | `c6_small_multiples.vl.jsonc` | Small multiples (vconcat + hconcat) |
| C7 | `c7_naa_treemap.vg.jsonc` | Treemap (Vega, not Vega-Lite) |
| C8 | `c8_naa_streamgraph.vl.jsonc` | Streamgraph |
| C9 | `c9_oral_history_isotype.vl.jsonc` | ISOTYPE |
| C10 | `c10_state_growth_dumbbell.vl.jsonc` | Dumbbell chart (log scale) |
| M1 | `m1_proportional_symbols.vl.jsonc` | Proportional symbol map |
| M2 | `m2_choropleth.vl.jsonc` | Choropleth map |
| M3 | `m3_hexbin_map.vl.jsonc` | Hexagon bin map |
| — | `theme.jsonc` | Shared fonts, sizes and greys |
