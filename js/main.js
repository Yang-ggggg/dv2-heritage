// main.js: puts all 13 charts onto the page. It draws nothing itself.
// How: index.html has an empty <div id="..."> for each chart.
// This file says which spec file goes into which div, then calls vegaEmbed.
// The C7 treemap is a Vega spec (.vg.json); the other 12 are Vega-Lite (.vl.json).

// Lookup table: div id (in index.html) -> spec file (in specs/)
const chartSpecs = {
  c1_trove_growth: "specs/c1_trove_growth.vl.json",
  c2_naa_calendar: "specs/c2_naa_calendar.vl.json",
  c3_publication_years: "specs/c3_publication_years.vl.json",
  c4_manuscripts_waffle: "specs/c4_manuscripts_waffle.vl.json",
  c5_manuscripts_lollipop: "specs/c5_manuscripts_lollipop.vl.json",
  c6_small_multiples: "specs/c6_small_multiples.vl.json",
  c7_naa_treemap: "specs/c7_naa_treemap.vg.json",
  c8_naa_streamgraph: "specs/c8_naa_streamgraph.vl.json",
  c9_oral_history_isotype: "specs/c9_oral_history_isotype.vl.json",
  c10_state_growth_dumbbell: "specs/c10_state_growth_dumbbell.vl.json",
  m1_proportional_symbols: "specs/m1_proportional_symbols.vl.json",
  m2_choropleth: "specs/m2_choropleth.vl.json",
  m3_hexbin_map: "specs/m3_hexbin_map.vl.json"
};

// Step 1: load theme.json once (shared fonts, sizes and greys for every chart)
fetch("specs/theme.json")
  .then((response) => response.json())
  .then((pageTheme) => {
    // Step 2: go through the table, one chart at a time
    for (const [elementId, specPath] of Object.entries(chartSpecs)) {
      if (!document.getElementById(elementId)) continue; // no div with this id: skip it
      // Step 3: vegaEmbed reads the spec, builds the chart and draws it inside the div
      //   actions: false   -> hide the "..." export menu
      //   renderer: "svg"  -> vector drawing, so text stays sharp
      //   config: theme    -> apply the shared look from theme.json
      vegaEmbed(`#${elementId}`, specPath, { actions: false, renderer: "svg", config: pageTheme })
        .catch((error) => console.error(`Chart ${elementId} failed to load`, error)); // one chart fails, the rest still draw
    }
  })
  .catch((error) => console.error("specs/theme.json failed to load, so no chart was drawn", error));
