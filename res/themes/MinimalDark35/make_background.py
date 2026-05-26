"""Render background.png for the MinimalDark35 theme.

Run from this directory:  python make_background.py
Produces a 320x480 portrait background with section dividers and labels baked in.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 320, 480
BG = (14, 15, 18)
DIVIDER = (38, 41, 48)
LABEL = (140, 144, 153)
SUBTLE = (90, 94, 102)
ACCENT = (95, 179, 214)

FONTS = Path(__file__).resolve().parents[2] / "fonts"
F_LABEL = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-Bold.ttf"), 11)
F_SECTION = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-ExtraBold.ttf"), 14)
F_SUB = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-Regular.ttf"), 10)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# y-anchors for the 6 horizontal dividers (below: header, cpu, gpu, mem, disk, [net is last])
dividers = [30, 170, 258, 322, 386]
for y in dividers:
    d.line([(10, y), (W - 10, y)], fill=DIVIDER, width=1)

# section labels (drawn on top-left of each block; values painted by theme yaml on top)
sections = [
    (34, "CPU"),
    (174, "GPU"),
    (262, "MEM"),
    (326, "DISK"),
    (390, "NET"),
]
for y, txt in sections:
    d.text((12, y), txt, font=F_SECTION, fill=ACCENT)

# Static labels under each section title
d.text((12, 54), "Ryzen 9 9950X3D", font=F_SUB, fill=SUBTLE)
d.text((12, 194), "NVIDIA RTX 3060", font=F_SUB, fill=SUBTLE)
d.text((12, 410), "enp8s0", font=F_SUB, fill=SUBTLE)

# ↓ / ↑ arrows for the NET line graphs
d.text((90, 394), "DL", font=F_SUB, fill=SUBTLE)
d.text((250, 394), "UL", font=F_SUB, fill=SUBTLE)

# Thin top accent strip beside header for a touch of color
d.rectangle([(0, 0), (3, 28)], fill=ACCENT)

out = Path(__file__).with_name("background.png")
img.save(out)
print(f"wrote {out}")
