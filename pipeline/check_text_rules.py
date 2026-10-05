"""Check the text rules on the live page: short forms, and body-text lines over 60 characters or 10 words.

Usage: python check_text_rules.py <site folder> <page url>   (the page must already be served)
"""
import asyncio
import json
import re
import sys
import glob

from playwright.async_api import async_playwright

site_folder, page_url = sys.argv[1], sys.argv[2]
SHORT_FORMS = re.compile(r"\b(vs|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|NSW|QLD|VIC|TAS|NT|ACT|WA|SA|avg|approx|etc|incl|no\.)\b")
MAXIMUM_CHARACTERS, MAXIMUM_WORDS = 60, 10


def strings_in(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("text", "subtitle", "title", "name") or isinstance(value, (dict, list)):
                yield from strings_in(value)
            elif isinstance(value, str) and key in ("labelExpr", "format"):
                continue
    elif isinstance(node, list):
        for item in node:
            yield from strings_in(item)
    elif isinstance(node, str):
        yield node


print("1) Short forms in chart specs (titles, subtitles, labels, tooltips)")
found = 0
for spec_path in sorted(glob.glob(f"{site_folder}/specs/*.v[lg].json")):
    for text in strings_in(json.load(open(spec_path))):
        if SHORT_FORMS.search(text) and not text.startswith("data/"):
            print(f"   {spec_path.split('/')[-1]}: {text!r}")
            found += 1
print(f"   {found} found")

print("1b) Capital-letter short forms in tooltip text that comes from data files")
import pandas as pd
CAPITALS = re.compile(r"\b(?!(?:II|III|IV|VI|VII|VIII|IX|XI|XII)\b)[A-Z]{2,}s?\b")
tooltip_fields = [("data/naa_treemap.csv", "name"), ("data/naa_weekly.csv", "top_series_title"),
                  ("data/decade_shares.csv", "panel_title"), ("data/decade_shares.csv", "year_measured"),
                  ("data/oral_history_icons.csv", "status")]
found_in_data = 0
for data_file, column in tooltip_fields:
    for text in pd.read_csv(f"{site_folder}/{data_file}")[column].dropna().unique():
        if CAPITALS.search(str(text)) or SHORT_FORMS.search(str(text)):
            print(f"   {data_file} {column}: {text!r}")
            found_in_data += 1
hexagons = json.load(open(f"{site_folder}/data/nma_hexbins.geojson"))["features"]
for feature in hexagons:
    place = feature["properties"]["largest_place"]
    if CAPITALS.search(place) or SHORT_FORMS.search(place):
        print(f"   data/nma_hexbins.geojson largest_place: {place!r}")
        found_in_data += 1
print(f"   {found_in_data} found")


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(page_url)
        await page.wait_for_timeout(4000)
        lines = await page.evaluate("""() => {
          const result = [];
          const elements = document.querySelectorAll('.body-text, .note, .callout-label, .stat-label, .force-list li, .subtitle, .takeaway-text, .source-list li');
          for (const element of elements) {
            const range = document.createRange(); const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
            const byTop = new Map();
            while (walker.nextNode()) {
              const node = walker.currentNode; const text = node.textContent;
              for (let i = 0; i < text.length; i++) {
                range.setStart(node, i); range.setEnd(node, i + 1);
                const rect = range.getBoundingClientRect(); if (!rect.height) continue;
                const key = Math.round(rect.top / 4);
                byTop.set(key, (byTop.get(key) || '') + text[i]);
              }
            }
            for (const line of byTop.values()) result.push({where: element.className || element.tagName, text: line.replace(/\\s+/g, ' ').trim()});
          }
          return result;
        }""")
        print("2) Page text lines over", MAXIMUM_CHARACTERS, "characters or", MAXIMUM_WORDS, "words (as drawn at 1280 px)")
        too_long = [line for line in lines if len(line["text"]) > MAXIMUM_CHARACTERS or len(line["text"].split()) > MAXIMUM_WORDS]
        for line in too_long:
            print(f"   [{line['where']}] {len(line['text'])} characters, {len(line['text'].split())} words: {line['text']}")
        print(f"   {len(too_long)} long lines out of {len(lines)}")
        await browser.close()

asyncio.run(main())
