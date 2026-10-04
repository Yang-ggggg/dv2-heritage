"""Render a Vega-Lite spec to PNG for a quick check (inlines local data, applies specs/theme.json like the page)."""
import json, sys, vl_convert

def inline_local_data(node, site_folder):
    if isinstance(node, dict):
        if "url" in node and not node["url"].startswith("http"):
            local_path = f"{site_folder}/{node['url']}"
            if local_path.endswith(".csv"):
                node["values"] = open(local_path).read()   # csv text, parsed by Vega with the spec's format
                node.setdefault("format", {"type": "csv"})
            else:
                node["values"] = json.load(open(local_path))
            del node["url"]
        for value in node.values():
            inline_local_data(value, site_folder)
    elif isinstance(node, list):
        for value in node:
            inline_local_data(value, site_folder)

def merge_config(theme, spec_config):
    merged = dict(theme)
    for key, value in (spec_config or {}).items():
        merged[key] = {**merged.get(key, {}), **value} if isinstance(value, dict) and isinstance(merged.get(key), dict) else value
    return merged

spec_path, output_png = sys.argv[1], sys.argv[2]
site_folder = sys.argv[3] if len(sys.argv) > 3 else "."
spec = json.load(open(spec_path))
spec["config"] = merge_config(json.load(open(f"{site_folder}/specs/theme.json")), spec.get("config"))
inline_local_data(spec, site_folder)
open(output_png, "wb").write(vl_convert.vegalite_to_png(spec, scale=1.4))
print("wrote", output_png)
