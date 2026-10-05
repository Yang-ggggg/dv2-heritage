// Embed every chart: element id -> pretty-printed Vega-Lite spec in specs/
// specs/theme.json holds the shared fonts and greys so every chart matches the page.
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
  m1_proportional_symbols: "specs/m1_proportional_symbols.vl.json",
  m2_choropleth: "specs/m2_choropleth.vl.json",
  m3_hexbin_map: "specs/m3_hexbin_map.vl.json"
};

fetch("specs/theme.json")
  .then((response) => response.json())
  .then((pageTheme) => {
    for (const [elementId, specPath] of Object.entries(chartSpecs)) {
      if (!document.getElementById(elementId)) continue;
      vegaEmbed(`#${elementId}`, specPath, { actions: false, renderer: "svg", config: pageTheme })
        .catch((error) => console.error(`Chart ${elementId} failed to load`, error));
    }
  });
