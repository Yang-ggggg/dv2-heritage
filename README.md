# Who Decides What Goes Online?

FIT3179 Data Visualisation 2 (Semester 2, 2026) by **Tan Jing Yang**.

A one-page, scrolling data story about Australia's digitised heritage collections, built with Vega-Lite and Vega.

- `index.html`, `css/`, `js/`: the web page
- `specs/`: one pretty-printed Vega-Lite JSON spec per chart (`theme.json` = shared fonts and greys)
- `specs_commented/`: earlier annotated references; the current page loads only `specs/`
- `data/`: small aggregated data files used by the charts
- `pipeline/`: Python scripts that make the files in `data/` from the original sources
- `sketch/`: PDF of the hand-drawn A4 sketch

Data sources, access dates and the AI acknowledgement are listed at the bottom of the web page.

Trove counts were refreshed on 20 October 2026 with the Trove API (`pipeline/colab_trove_refresh.ipynb`, key entered at run time, never saved).
The raw counts are in `data/trove_refresh_2026-10-20/`. Rebuild order: `build_trove_time_data.py` → `build_state_data.py` → `build_trove_refresh.py` → `build_c4_c5_c6_data.py` → `build_c6_spec.py`.

## Final submission package

The final poster design is v0.23. The `submission/` folder contains the Part B description, AI acknowledgement, screenshot-caption instructions and local verification record. Start with [submission/README.md](submission/README.md).

The description explains Why and How for all 13 charts, the Australian Albers projection and the credited course examples. The final live screenshot must be captured after publication; old screenshot dimensions are not used as a substitute.
