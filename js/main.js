// Embed every chart: element id -> pretty-printed Vega-Lite spec in specs/
const chartSpecs = {
  m1_proportional_symbols: "specs/m1_proportional_symbols.vl.json",
  m2_choropleth: "specs/m2_choropleth.vl.json"
};

const embedOptions = { actions: false, renderer: "svg" };

for (const [elementId, specPath] of Object.entries(chartSpecs)) {
  vegaEmbed(`#${elementId}`, specPath, embedOptions).catch((error) => {
    console.error(`Chart ${elementId} failed to load`, error);
  });
}
