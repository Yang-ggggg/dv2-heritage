# Part B Domain Description

## Describe your domain chosen for DV II

My domain is Australia's digitised heritage collections. Libraries and archives digitise newspapers, files and recordings. Museums also publish catalogue records describing their objects. These online records show only part of the past.

My page, **Who Decides What Goes Online?**, follows copyright, funding and public demand through collections held by the National Library of Australia, National Archives of Australia and National Museum of Australia. It ends with lessons for Malaysian libraries, archives and museums.

## Describe the Why and Who aspects of your DV II

**Who:** The page is for general readers in Malaysia. It uses full state names, explains terms such as “per resident” and archive “series”, and explains how to read the logarithmic scale. Readers can follow the main findings without interacting with the charts.

**Why:** I want readers to understand how online collections grow and where their gaps remain. The tasks are to compare growth, find the newspaper copyright boundary, compare states by total and rate, identify the archive themes that dominate recorded digitisation, and examine access to recordings and the mapped museum records.

The narrative connects patterns with documented institutional context. For example, the Trove Data Guide describes New South Wales' investment in digitisation. The charts show different growth between states, but do not isolate the effect of spending or measure whether access is fair.

## Describe the “What” aspect of your DV II

The datasets combine time series, categorical collection information, hierarchies and geographic geometry. Counts, digitised shares, growth ratios and articles per resident are quantitative attributes. States, archive themes and availability groups are categorical. Dates and decades provide ordered temporal information.

**Sources and relevance:**

- **National Library of Australia, Trove application programming interface, version 3:** newspaper counts by state and publication year, plus articles with user-corrected text. I harvested these on 20 October 2026 using my own key. [Trove](https://trove.nla.gov.au/).
- **Tim Sherratt:** [weekly newspaper totals](https://github.com/wragge/trove-newspaper-totals) through 16 February 2025 and [historical newspaper snapshots](https://github.com/wragge/trove-newspaper-totals-historical) for the earlier observations. His [dashboard](https://wragge.github.io/trove-newspaper-totals/) explains the cancellation of his access keys. These sources support the time and state comparisons.
- **Tim Sherratt:** [National Archives recently digitised files](https://github.com/wragge/naa-recently-digitised), through 13 September 2026. The weekly lists support the activity, date and archive-theme charts.
- **Tim Sherratt, GLAM Workbench:** [manuscript finding aids](https://github.com/GLAM-Workbench/nla-finding-aids-data), March 2023; [oral histories](https://github.com/GLAM-Workbench/trove-oral-histories-data), December 2023; and [periodicals](https://github.com/GLAM-Workbench/trove-periodicals-data), March 2024. These published snapshots support comparisons of listed items, recording availability and dates. Finding aids list the items within a collection.
- **National Museum of Australia:** 97,214 object records harvested on 4 October 2026 through its [Collection API](https://www.nma.gov.au/about/our-collection/museum-api). Recorded production places provide the museum map's geographic information.
- **Australian Bureau of Statistics:** [March 2026 population](https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/latest-release) supplies the rate denominator; [2026 state and territory boundaries](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-4-july-2026-june-2031/access-and-downloads/digital-boundary-files) supply the maps.

The contextual sources are the [Trove Data Guide](https://tdg.glam-workbench.net/newspapers-and-gazettes/newspaper-corpus.html), Trove's [Welcome to the Public Domain](https://trove.nla.gov.au/announcement/2025/12/15/welcome-public-domain) notice, and the National Archives' [Second World War digitisation announcement](https://www.naa.gov.au/about-us/media-and-publications/media-releases/large-scale-effort-sees-1-million-second-world-war-records-digitised). Authors, dataset dates and access dates are also listed on the webpage.

**Preparation and derived attributes:** Python cleaned, joined and aggregated the data, removed duplicate archive file identifiers and built the museum hexagons. Vega-Lite draws the charts and maps; Vega draws the treemap. The scripts log exclusions. Missing weeks remain missing, rather than becoming zero.

- Articles per resident = October 2026 articles ÷ March 2026 residents.
- Growth multiple = October 2026 articles ÷ April 2011 articles.
- Digitised share = digitised items ÷ all listed items.
- Monthly files per recorded week = monthly files ÷ recorded weeks.

The 1.49 million archive files are those in the recorded lists. The museum map shows 14,348 records, or 14.8% of the 97,214 harvested catalogue records. Of 18,962 records with a coordinated production place, 3,168 were overseas, 1,435 named only a broad region and 11 fell outside the map. Each mapped record contributes its first production place with coordinates. These are catalogue records, not a count of the museum's entire physical collection. A downloadable transcript is distinct from an online audio link or summary.

## Describe the “How” aspect of your DV II

The page moves from growth to copyright, regional differences, archive themes and remaining gaps. Finding titles and selected annotations guide the reader. A consistent grid, larger gaps between sections, archival serif headings and left-aligned sans serif prose support the reading order.

Source accents are blue for the National Library, amber for the National Archives and green for the National Museum. Local legends explain each chart's data encoding. C7 and C8 consistently use rose for service records, purple for migration records and grey for the remaining themes. Ordered lightness shows quantities in C2, M2 and M3. Filled and hollow symbols also distinguish states of availability or observation dates. Colour-vision simulations informed the final palette; they do not guarantee readability for every reader.

### C1 Line chart

**Why:** Show changes in Trove's article total over time. Ordered dates and quantitative counts suit a line with aligned positions.

**How:** Line and point marks use horizontal position for date and vertical position for articles. Points identify observations. A dashed segment joins the last February 2025 observation to October 2026 without implying an observed path through that interval. End labels compare 48.5 and 266.3 million. The adjacent callout shows Queensland supplied 69% of the net increase over that interval.

### C2 Calendar heatmap

**Why:** Compare busy and quiet recorded weeks while showing gaps in coverage.

**How:** Rectangular cells use rows for years, columns for weeks and five ordered colour classes for file counts. Grey identifies missing weeks. An outlined cell with a white halo marks the record week. The title describes averages over recorded weeks: 2025 and 2026 contain only 19 and 18 recorded weeks, respectively.

### C3 Annual bar chart

**Why:** Locate the sharp change in newspaper coverage at 1955 and compare it with the earlier collection.

**How:** Bars use publication year on the horizontal axis and length for article count. Notes identify the peak and the 79% drop from 1954 to 1955. A checkbox adds the April 2011 outline. The text explains the library's digitisation rule and publisher permissions, rather than claiming one legal expiry date for every work.

### C4 Waffle chart

**Why:** Explain the overall digitised share of listed manuscript items with a simple part-to-whole view.

**How:** One hundred equal square units represent the whole. Thirty blue units show the rounded 29.5% digitised share; light units show the remainder. The printed 128,619 of 435,537 items gives the exact totals, and the rounding note explains the difference.

### C5 Lollipop chart

**Why:** Compare digitised shares by the decade a collection begins, while showing how many listed items those shares concern.

**How:** Line stems and point heads use horizontal position for starting decade and vertical position for share. Dot area encodes item count and has a size legend. Two annotations compare earlier and later collections. Decades with fewer than 20 collections are excluded and this filter is stated.

### C6 Small multiples

**Why:** Compare the date distributions of five kinds of collection without letting their different totals dominate the comparison.

**How:** Five bar panels share the same decade axis and percentage scale. Bar length shows that panel's share in each decade. Each panel is normalised to its own dated records within 1800–2029. Subtitles give totals and explain whether dates mean publication, recording or the start of a date range. One note per panel identifies a finding. The small multiples count as one chart.

### C10 Connected dot plot

**Why:** Compare states' initial and final article totals and their proportional growth.

**How:** Point marks show April 2011 and October 2026, linked by line marks. Hollow and filled dots distinguish the dates. Rows follow the growth ranking. The horizontal axis is logarithmic: 1–2 occupies the same distance as 10–20. Line length therefore reflects the logarithm of the final-to-initial ratio. Only New South Wales and the Northern Territory receive numerical finding labels; all eight row names remain necessary identifiers.

### M1 Proportional symbol map

**Why:** Compare state article totals in their geographic context.

**How:** Point circles are scaled by area, with zero articles corresponding to zero area. Larger symbols are drawn before smaller ones; white edges and transparency preserve visibility. State names and a leader identify locations. The size legend shows 1, 10 and 25 million articles. M1 and M2 share the same map scale.

### M2 Choropleth map

**Why:** Compare article totals relative to current population, complementing M1's counts.

**How:** State polygons use sequential blue lightness for articles per resident. Manual breaks at 5, 10 and 20 give four clearly labelled classes. Highest and lowest rates are annotated; hovering outlines a state. The denominator date is explicit. This rate does not measure historical completeness, individual access or funding need.

### C7 Treemap

**Why:** Show both the archive themes' shares and the hierarchy of themes containing record series.

**How:** Vega's stratify and treemap transforms produce nested area rectangles. Parent area represents theme totals; inner boxes are series, or groups of related files. Rose and purple highlight the two main themes. Header bands keep theme names above internal boundaries. A quoted institutional statement supplies demand context; tooltips identify series and exact values.

### C8 Streamgraph

**Why:** Show changes in the size and mix of recorded archive digitisation over time.

**How:** Area-band thickness encodes monthly average files per recorded week; horizontal position encodes month. Colours match C7. Centred bands emphasise the changing theme mix. A thickness key explains magnitude; tooltips support exact comparisons. A leader identifies June 2022's 72% migration share; a bracket marks the later low-service period. Legend clicks highlight themes.

### C9 Pictogram chart

**Why:** Make recording availability and the “9 in 100” downloadable-transcript finding concrete.

**How:** One hundred microphone symbols represent rounded shares. Three labelled groups contain audio with a transcript, audio without a transcript, and no online audio link. Filled blue, blue outlines and grey reinforce the groups. Exact counts accompany the rounded icons. The 2,710 summary downloads belong within the audio-without-transcript group, not a fourth category.

### M3 Hexagon bin map

**Why:** Show concentrations in the available production-place metadata while avoiding thousands of overlapping point symbols.

**How:** Python aggregates records into equal-area geographic hexagons with a 100-kilometre centre-to-corner radius, approximately 26,000 square kilometres each. Area polygons use five ordered green classes for counts. The subtitle discloses 14.8% coverage. Notes identify Sydney's 2,048 records and Yirrkala's 1,056, about half as many. A 150-kilometre sensitivity check retains the same four leading areas.

### Map projection and adapted examples

All three maps use an Albers conic equal-area projection, with standard parallels at 18°S and 36°S and central meridian 132°E. A conic projection suits Australia's east–west extent at these latitudes. It preserves relative geographic areas, which supports state-area interpretation and equal-area hexagon aggregation. Shapes and distances can still be distorted. M1 and M2 use identical scale and translation to align their outlines.

The webpage credits adaptations from the FIT3179 [multiple-chart example](https://fit3179.github.io/Vega-Lite/5_multiple_charts_html/), [symbol-map example](https://github.com/FIT3179/Vega-Lite/tree/main/2_symbol_map) and [choropleth example](https://github.com/FIT3179/Vega-Lite/tree/main/3_choropleth_map), plus the [Vega treemap example](https://vega.github.io/vega/examples/treemap/) and [Vega-Lite streamgraph example](https://vega.github.io/vega-lite/examples/stacked_area_stream.html). The custom microphone symbol, prepared hexagon geometry and selected annotations support this page's specific tasks. Interactions reveal detail without swapping major sections.
