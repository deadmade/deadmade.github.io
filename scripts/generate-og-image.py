#!/usr/bin/env python3
"""Draw the share image (og:image, 1200x630) into static/images/og.png: python3 scripts/generate-og-image.py

Run from the repository root. Colours come from assets/css/tokens.css and the type from static/fonts/,
so a new palette only needs a rerun. The text comes from hugo.toml (title, params.role).
"""
import re
import tomllib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630

tokens = dict(re.findall(r"--(\w+):\s*(#[0-9A-Fa-f]{6})", (ROOT / "assets/css/tokens.css").read_text(encoding="utf-8")))
site = tomllib.loads((ROOT / "hugo.toml").read_text(encoding="utf-8"))


def font(weight, size):
    return ImageFont.truetype(str(ROOT / f"static/fonts/ibm-plex-mono-latin-{weight}-normal.woff2"), size)


img = Image.new("RGB", (W, H), tokens["bg"])
d = ImageDraw.Draw(img)

# the sheet: a hairline frame whose lines overshoot at the corners, as on the site
x0, y0, x1, y1, over = 72, 64, W - 72, H - 64, 14
for y in (y0, y1):
    d.line([(x0 - over, y), (x1 + over, y)], fill=tokens["line"], width=2)
for x in (x0, x1):
    d.line([(x, y0 - over), (x, y1 + over)], fill=tokens["line"], width=2)
d.line([(W // 2, y0 - 9), (W // 2, y0 + 9)], fill=tokens["quiet"], width=2)  # centring tick
d.polygon([(W // 2, y1 - 16), (W // 2 + 10, y1), (W // 2 - 10, y1)], fill=tokens["quiet"])  # orientation mark

# the name, one word per line, then the role with the hood's triangle
left = x0 + 64
first, last = site["title"].split(" ", 1)
d.text((left, 108), first, font=font(700, 124), fill=tokens["fg"])
d.text((left, 232), last, font=font(700, 124), fill=tokens["fg"])
role = font(600, 40)
d.polygon([(left, 452), (left + 24, 438), (left, 424)], fill=tokens["accent"])
d.text((left + 44, 414), site["params"]["role"], font=role, fill=tokens["muted"])
d.text((left, 484), "C# · .NET · APIs · ERP integrations", font=font(400, 28), fill=tokens["quiet"])

out = ROOT / "static/images/og.png"
img.save(out, "PNG", optimize=True)
print(f"[OK] Created {out.relative_to(ROOT)}")
