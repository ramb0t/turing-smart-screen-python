"""Render background.png for the MinimalDark88 theme (480×1920).

Run from this directory:  python make_background.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 480, 1920
BG      = (14, 15, 18)
DIVIDER = (38, 41, 48)
LABEL   = (140, 144, 153)
SUBTLE  = (90, 94, 102)
ACCENT  = (95, 179, 214)

FONTS    = Path(__file__).resolve().parents[2] / "fonts"
F_LABEL  = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-Bold.ttf"), 16)
F_SECTION = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-ExtraBold.ttf"), 20)
F_SUB    = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-Regular.ttf"), 14)

img = Image.new("RGB", (W, H), BG)
d   = ImageDraw.Draw(img)

# Section dividers (lines between sections)
dividers = [80, 580, 1020, 1270, 1520]
for y in dividers:
    d.line([(12, y), (W - 12, y)], fill=DIVIDER, width=1)

# Section labels baked into background
sections = [
    (86,   "CPU"),
    (586,  "GPU"),
    (1026, "MEM"),
    (1276, "DISK"),
    (1526, "NET"),
]
for y, txt in sections:
    d.text((20, y), txt, font=F_SECTION, fill=ACCENT)

# Processor / GPU sub-labels
d.text((20, 110), "Ryzen 9 9950X3D", font=F_SUB, fill=SUBTLE)
d.text((20, 610), "NVIDIA RTX 3060", font=F_SUB, fill=SUBTLE)
d.text((20, 1030), "RAM", font=F_SUB, fill=SUBTLE)
d.text((20, 1280), "/", font=F_SUB, fill=SUBTLE)  # disk mount point placeholder

# NET sub-labels
d.text((20, 1560), "ETH  ↓", font=F_SUB, fill=SUBTLE)
d.text((20, 1748), "ETH  ↑", font=F_SUB, fill=SUBTLE)

# Left accent strip (matches MinimalDark35 style)
d.rectangle([(0, 0), (4, 78)], fill=ACCENT)

out = Path(__file__).with_name("background.png")
img.save(out)
print(f"wrote {out}  ({W}×{H})")
