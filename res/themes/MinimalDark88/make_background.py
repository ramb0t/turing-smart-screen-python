"""Render background.png for the MinimalDark88 theme (480×1920).

Run from this directory:  python make_background.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H    = 480, 1920
BG      = (14, 15, 18)
BORDER  = (95, 110, 138)
DIVIDER = (50, 56, 70)
ACCENT  = (95, 179, 214)
ACCENT_DIM = (70, 130, 160)
SUBTLE  = (90, 94, 102)

FONTS     = Path(__file__).resolve().parents[2] / "fonts"
F_SECTION = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-ExtraBold.ttf"), 20)
F_LABEL   = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-Bold.ttf"), 14)
F_SUB     = ImageFont.truetype(str(FONTS / "jetbrains-mono" / "JetBrainsMono-Regular.ttf"), 13)

img = Image.new("RGB", (W, H), BG)
d   = ImageDraw.Draw(img)

RADIUS = 16
MARGIN = 8
PAD_X  = 20
HDR_H  = 36

# (y_top, y_bottom, section_label, sub_label)
cards = [
    (2,    78,   None,    None),
    (82,   640,  "CPU",   "Ryzen 9 9950X3D"),
    (644,  1000, "GPU",   "NVIDIA RTX 3060"),
    (1004, 1230, "MEM",   None),
    (1234, 1520, "DISK",  None),
    (1524, 1666, "POWER", None),
    (1670, 1918, "NET",   None),
]

for (yt, yb, label, sub) in cards:
    d.rounded_rectangle([MARGIN, yt, W - MARGIN, yb], radius=RADIUS,
                        outline=BORDER, width=2)
    if label:
        line_y = yt + HDR_H
        d.line([(MARGIN + 1, line_y), (W - MARGIN - 1, line_y)], fill=DIVIDER, width=1)
        d.text((PAD_X, yt + 8), label, font=F_SECTION, fill=ACCENT)
        if sub:
            d.text((PAD_X + 60, yt + 11), sub, font=F_SUB, fill=SUBTLE)

# Accent strip on HEADER card
d.rectangle([(MARGIN, 2), (MARGIN + 4, 78)], fill=ACCENT)

# ── CPU section labels ──────────────────────────────────────────────────────
d.text((PAD_X, 280), "CCD0", font=F_LABEL, fill=ACCENT)
d.text((PAD_X, 370), "CCD1", font=F_LABEL, fill=ACCENT_DIM)

# ── GPU graph labels ────────────────────────────────────────────────────────
# Side-by-side line graphs: left = GPU UTIL %, right = VRAM %
d.text((PAD_X, 852), "GPU UTIL %", font=F_SUB, fill=SUBTLE)
d.text((252,   852), "VRAM %",     font=F_SUB, fill=SUBTLE)

# ── MEM section sub-label ───────────────────────────────────────────────────
d.text((PAD_X, 1044), "used", font=F_SUB, fill=SUBTLE)

# ── DISK R/W labels ─────────────────────────────────────────────────────────
d.text((PAD_X, 1394), "READ  MB/s",  font=F_SUB, fill=SUBTLE)
d.text((PAD_X, 1462), "WRITE MB/s", font=F_SUB, fill=SUBTLE)

# ── POWER section labels ────────────────────────────────────────────────────
d.text((PAD_X, 1562), "GPU  W", font=F_LABEL, fill=ACCENT)
d.text((PAD_X, 1628), "CPU  W", font=F_LABEL, fill=ACCENT)

# ── NET labels ──────────────────────────────────────────────────────────────
d.text((PAD_X, 1708), "ETH  ↓", font=F_SUB, fill=SUBTLE)
d.text((PAD_X, 1818), "ETH  ↑", font=F_SUB, fill=SUBTLE)

out = Path(__file__).with_name("background.png")
img.save(out)
print(f"wrote {out}  ({W}×{H})")
