"""Check the page palette: contrast on white, lightness steps, and colour-vision-deficiency (CVD) separation."""
import numpy as np

palette = {
    # ColorBrewer sequential ramps (light -> dark); base = the single colour used for bars/lines
    "nla_blue":   {"ramp": ["#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"], "base": "#3182bd", "text": "#08519c"},
    "naa_amber":  {"ramp": ["#fee6ce", "#fdae6b", "#fd8d3c", "#e6550d", "#a63603"], "base": "#e6550d", "text": "#a63603"},
    "nma_green":  {"ramp": ["#ccece6", "#99d8c9", "#66c2a4", "#2ca25f", "#006d2c"], "base": "#2ca25f", "text": "#006d2c"},
    # M3 hex bin map: BuGn 7 without its two lightest steps, so the lightest class stays visible on the basemap #F0F0EB
    "nma_hexbin": {"ramp": ["#F0F0EB", "#99d8c9", "#66c2a4", "#2ca25f", "#006d2c", "#00441b"], "base": "#2ca25f", "text": "#006d2c"},
    "migration_purple": {"ramp": [], "base": "#6a51a3", "text": "#54278f"},
    "context_grey": {"ramp": [], "base": "#bdbdbd", "text": "#55554d"},
}

def hex_to_rgb(hex_colour):
    hex_colour = hex_colour.lstrip("#")
    return np.array([int(hex_colour[i:i + 2], 16) / 255 for i in (0, 2, 4)])

def to_linear(rgb):
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)

def to_srgb(linear):
    linear = np.clip(linear, 0, 1)
    return np.where(linear <= 0.0031308, linear * 12.92, 1.055 * linear ** (1 / 2.4) - 0.055)

def relative_luminance(hex_colour):
    return float(np.dot(to_linear(hex_to_rgb(hex_colour)), [0.2126, 0.7152, 0.0722]))

def contrast_ratio(colour_a, colour_b):
    lighter, darker = sorted([relative_luminance(colour_a), relative_luminance(colour_b)], reverse=True)
    return (lighter + 0.05) / (darker + 0.05)

def lab_from_linear(linear):
    xyz = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ linear
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])

# Machado et al. (2009) full-severity simulation matrices (linear RGB)
cvd_matrices = {
    "normal": np.eye(3),
    "protanopia": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    "deuteranopia": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "tritanopia": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}

def delta_e(colour_a, colour_b, vision):
    matrix = cvd_matrices[vision]
    lab_a = lab_from_linear(np.clip(matrix @ to_linear(hex_to_rgb(colour_a)), 0, 1))
    lab_b = lab_from_linear(np.clip(matrix @ to_linear(hex_to_rgb(colour_b)), 0, 1))
    return float(np.linalg.norm(lab_a - lab_b))

print("1) Text colours on white (need >= 4.5:1) and page ink")
for name, colour_set in palette.items():
    print(f"   {name:17s} text {colour_set['text']}  {contrast_ratio(colour_set['text'], '#ffffff'):.2f}:1")
print(f"   ink #1E1E1A {contrast_ratio('#1E1E1A', '#ffffff'):.2f}:1 | secondary #55554D {contrast_ratio('#55554D', '#ffffff'):.2f}:1")

print("2) Ramps: CIE L* must fall steadily light -> dark (light = low, dark = high)")
for name, colour_set in palette.items():
    if colour_set["ramp"]:
        lightness = [round(float(lab_from_linear(to_linear(hex_to_rgb(c)))[0]), 1) for c in colour_set["ramp"]]
        steps = np.diff(lightness)
        print(f"   {name:17s} L* {lightness}  min step {abs(steps).min():.1f}  monotonic {all(steps < 0)}")

print("3) Pairs that appear together: delta E under each vision type (> ~20 = clearly different)")
pairs = [("naa_amber", "migration_purple"), ("naa_amber", "context_grey"), ("migration_purple", "context_grey"),
         ("nla_blue", "naa_amber"), ("nla_blue", "nma_green"), ("naa_amber", "nma_green"), ("nla_blue", "migration_purple")]
for first, second in pairs:
    values = {vision: delta_e(palette[first]["base"], palette[second]["base"], vision) for vision in cvd_matrices}
    print(f"   {first:16s} vs {second:16s} " + "  ".join(f"{v[:5]} {d:5.1f}" for v, d in values.items()))
