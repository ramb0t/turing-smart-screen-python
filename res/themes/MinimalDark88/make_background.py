"""Render background.png for the MinimalDark88 theme (480×1920).

Run from this directory:  python make_background.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 480, 1920
BG      = (14, 15, 18)
BORDER  = (95, 110, 138)     # card outline
DIVIDER = (50, 56, 70)       # header-bar underline inside each card
ACCENT  = (95, 179, 214)
SUBTLE  = (90, 94, 102)
LABEL_C = (140, 144, 153)

FONTS     = Path(__file__).resolve().parents[2] / "fonts"
F_SECTION = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-ExtraBold.ttf"), 20)
F_SUB     = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-Regular.ttf"), 14)

img = Image.new("RGB", (W, H), BG)
d   = ImageDraw.Draw(img)

RADIUS  = 16
MARGIN  = 8      # gap between screen edge and card
PAD_X   = 20     # content left margin (matches theme.yaml X=20)
HDR_H   = 36     # height of the label band inside each card

# (y_top, y_bottom, label, sub_label)
cards = [
    (2,    78,   None,   None),             # HEADER — no label, no sub-line
    (82,   578,  "CPU",  "Ryzen 9 9950X3D"),
    (582,  1018, "GPU",  "NVIDIA RTX 3060"),
    (1022, 1268, "MEM",  None),
    (1272, 1518, "DISK", None),
    (1522, 1918, "NET",  None),
]

for (yt, yb, label, sub) in cards:
    # Outer card border
    d.rounded_rectangle(
        [MARGIN, yt, W - MARGIN, yb],
        radius=RADIUS,
        outline=BORDER,
        width=2,
    )
    if label:
        # Thin line under the label row
        line_y = yt + HDR_H
        d.line([(MARGIN + 1, line_y), (W - MARGIN - 1, line_y)], fill=DIVIDER, width=1)
        # Section label
        d.text((PAD_X, yt + 8), label, font=F_SECTION, fill=ACCENT)
        # Sub-label (hardware name)
        if sub:
            d.text((PAD_X + 56, yt + 11), sub, font=F_SUB, fill=SUBTLE)

# NET sub-labels for graph lanes (must clear HDR_H divider at yt+36=1558)
d.text((PAD_X, 1562), "ETH  ↓", font=F_SUB, fill=SUBTLE)
d.text((PAD_X, 1750), "ETH  ↑", font=F_SUB, fill=SUBTLE)

# Left accent strip on header card
d.rectangle([(MARGIN, 2), (MARGIN + 4, 78)], fill=ACCENT)
# Widen border to 2px on all cards


out = Path(__file__).with_name("background.png")
img.save(out)
print(f"wrote {out}  ({W}×{H})")
