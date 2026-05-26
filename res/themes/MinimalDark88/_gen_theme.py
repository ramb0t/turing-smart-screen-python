"""Generate theme.yaml for MinimalDark88 (writes the file in this directory).

Re-run after tweaking palette/layout constants below.
"""
from pathlib import Path
from textwrap import dedent

# --- palette / fonts -------------------------------------------------------
ACCENT     = "95, 179, 214"
ACCENT_DIM = "70, 130, 160"
TXT        = "224, 226, 230"
TXT_DIM    = "140, 144, 153"
BAR_BG     = "32, 35, 42"
GRAPH_LINE = "95, 179, 214"

FONT_BOLD  = "jetbrains-mono/JetBrainsMono-Bold.ttf"
FONT_EBOLD = "jetbrains-mono/JetBrainsMono-ExtraBold.ttf"
FONT_REG   = "jetbrains-mono/JetBrainsMono-Regular.ttf"

BG = "background.png"

# --- section Y-anchors (must match make_background.py) ---------------------
#  HEADER  2..78
#  CPU    82..640
#  GPU   644..1000
#  MEM  1004..1174
#  NET  1178..1520
#  DISK 1524..1918

# --- per-core CCD grid -----------------------------------------------------
# 9950X3D: 2 CCDs, 8 cores each, 2 HT threads → 4 rows of 8
# CCD0: logical cores 0-7  (T0) + 16-23 (T1)
# CCD1: logical cores 8-15 (T0) + 24-31 (T1)
PC_X0 = 20
PC_W  = 48
PC_H  = 26
PC_DX = 56   # 20 + 7*56 + 48 = 460  (20px each side margin)

# Y rows for the 4 core rows
PC_Y = {
    "ccd0_t0": 300,   # cores 0-7
    "ccd0_t1": 336,   # cores 16-23
    "ccd1_t0": 392,   # cores 8-15
    "ccd1_t1": 428,   # cores 24-31
}


def percore_block() -> str:
    lines = ["  CUSTOM:", "    INTERVAL: 1"]
    # CCD0 T0: logical 0-7 → col 0-7
    for col, core in enumerate(range(0, 8)):
        _core_bar(lines, core, PC_X0 + col * PC_DX, PC_Y["ccd0_t0"])
    # CCD0 T1: logical 16-23 → col 0-7
    for col, core in enumerate(range(16, 24)):
        _core_bar(lines, core, PC_X0 + col * PC_DX, PC_Y["ccd0_t1"])
    # CCD1 T0: logical 8-15 → col 0-7
    for col, core in enumerate(range(8, 16)):
        _core_bar(lines, core, PC_X0 + col * PC_DX, PC_Y["ccd1_t0"])
    # CCD1 T1: logical 24-31 → col 0-7
    for col, core in enumerate(range(24, 32)):
        _core_bar(lines, core, PC_X0 + col * PC_DX, PC_Y["ccd1_t1"])
    return "\n".join(lines)


def _core_bar(lines, core, x, y):
    lines += [
        f"    CpuCore{core:02d}:",
        f"      GRAPH:",
        f"        SHOW: True",
        f"        X: {x}",
        f"        Y: {y}",
        f"        WIDTH: {PC_W}",
        f"        HEIGHT: {PC_H}",
        f"        MIN_VALUE: 0",
        f"        MAX_VALUE: 100",
        f"        BAR_COLOR: {ACCENT}",
        f"        BAR_OUTLINE: False",
        f"        BACKGROUND_COLOR: {BAR_BG}",
    ]


# --- custom sensor stanzas (MemUsedGB, MemTotalGB, DiskReadMBs, etc.) ------
# --- helpers for built-in sensors ------------------------------------------
def text(*, x, y, font, size, color, anchor="lt", show_unit=True, indent=8):
    pad = " " * indent
    return dedent(f"""\
        SHOW: True
        SHOW_UNIT: {show_unit}
        X: {x}
        Y: {y}
        FONT: {font}
        FONT_SIZE: {size}
        FONT_COLOR: {color}
        BACKGROUND_IMAGE: {BG}
        ANCHOR: {anchor}""").replace("\n", "\n" + pad)


def bar(*, x, y, w, h, color=ACCENT, indent=8):
    pad = " " * indent
    return dedent(f"""\
        SHOW: True
        X: {x}
        Y: {y}
        WIDTH: {w}
        HEIGHT: {h}
        MIN_VALUE: 0
        MAX_VALUE: 100
        BAR_COLOR: {color}
        BAR_OUTLINE: False
        BACKGROUND_COLOR: {BAR_BG}""").replace("\n", "\n" + pad)


def linegraph(*, x, y, w, h, min_v=0, max_v=100, autoscale=False,
              color=GRAPH_LINE, history=120, indent=8):
    pad = " " * indent
    return dedent(f"""\
        SHOW: True
        X: {x}
        Y: {y}
        WIDTH: {w}
        HEIGHT: {h}
        MIN_VALUE: {min_v}
        MAX_VALUE: {max_v}
        HISTORY_SIZE: {history}
        AUTOSCALE: {autoscale}
        LINE_COLOR: {color}
        LINE_WIDTH: 2
        AXIS: False
        BACKGROUND_IMAGE: {BG}""").replace("\n", "\n" + pad)


# ===========================================================================
# CUSTOM sensors block — each sensor name appears exactly once
# ===========================================================================

def _ctext(x, y, font, size, color, anchor="lt"):
    return dedent(f"""\
        SHOW: True
        SHOW_UNIT: False
        X: {x}
        Y: {y}
        FONT: {font}
        FONT_SIZE: {size}
        FONT_COLOR: {color}
        BACKGROUND_IMAGE: {BG}
        ANCHOR: {anchor}""").replace("\n", "\n        ")


def _cgraph(x, y, w, h, max_v, color=ACCENT):
    return dedent(f"""\
        SHOW: True
        X: {x}
        Y: {y}
        WIDTH: {w}
        HEIGHT: {h}
        MIN_VALUE: 0
        MAX_VALUE: {max_v}
        BAR_COLOR: {color}
        BAR_OUTLINE: False
        BACKGROUND_COLOR: {BAR_BG}""").replace("\n", "\n        ")


def _cline(x, y, w, h, autoscale=True, color=GRAPH_LINE):
    return dedent(f"""\
        SHOW: True
        X: {x}
        Y: {y}
        WIDTH: {w}
        HEIGHT: {h}
        MIN_VALUE: 0
        MAX_VALUE: 100
        HISTORY_SIZE: 120
        AUTOSCALE: {autoscale}
        LINE_COLOR: {color}
        LINE_WIDTH: 2
        AXIS: False
        BACKGROUND_IMAGE: {BG}""").replace("\n", "\n        ")


CUSTOM_BLOCK = f"""  CUSTOM:
    INTERVAL: 1

    # Power — text only, positioned in each card's header band
    CpuPowerW:
      TEXT:
        {_ctext(460, 90, FONT_BOLD, 24, ACCENT_DIM, anchor="rt")}
    GpuPowerW:
      TEXT:
        {_ctext(460, 652, FONT_BOLD, 24, ACCENT_DIM, anchor="rt")}

    # GPU memory in GB (replaces built-in MB readout)
    GpuMemUsedGB:
      TEXT:
        {_ctext(20, 758, FONT_REG, 22, TXT_DIM)}
    GpuMemTotalGB:
      TEXT:
        {_ctext(460, 758, FONT_REG, 22, TXT_DIM, anchor="rt")}

    # Memory GB (framework hardcodes MB; these show GB at 1 d.p.)
    MemUsedGB:
      TEXT:
        {_ctext(20, 1050, FONT_BOLD, 32, ACCENT)}
    MemTotalGB:
      TEXT:
        {_ctext(20, 1086, FONT_REG, 18, TXT_DIM)}

    # Disk I/O speeds with history line graphs (DISK card 1524..1918)
    DiskReadMBs:
      TEXT:
        {_ctext(460, 1686, FONT_BOLD, 22, ACCENT, anchor="rt")}
      LINE_GRAPH:
        {_cline(20, 1702, 440, 80)}
    DiskWriteMBs:
      TEXT:
        {_ctext(460, 1794, FONT_BOLD, 22, ACCENT_DIM, anchor="rt")}
      LINE_GRAPH:
        {_cline(20, 1810, 440, 80, color=ACCENT_DIM)}"""


def percore_lines() -> str:
    """Generate CCD-grouped per-core bar entries at correct 4-space indent."""
    lines = []
    for col, core in enumerate(range(0, 8)):
        _core_bar(lines, core, PC_X0 + col * PC_DX, PC_Y["ccd0_t0"])
    for col, core in enumerate(range(16, 24)):
        _core_bar(lines, core, PC_X0 + col * PC_DX, PC_Y["ccd0_t1"])
    for col, core in enumerate(range(8, 16)):
        _core_bar(lines, core, PC_X0 + col * PC_DX, PC_Y["ccd1_t0"])
    for col, core in enumerate(range(24, 32)):
        _core_bar(lines, core, PC_X0 + col * PC_DX, PC_Y["ccd1_t1"])
    # _core_bar puts lines like "    CpuCoreXX:" (4-space indent) — correct
    return "\n".join(lines)


# ===========================================================================
THEME = f"""---
# MinimalDark88 — clean dark portrait theme for 8.8" Turing displays (480×1920).
# Generated by _gen_theme.py. Edit constants there, not here.
author: "Ramb0t (with Claude)"

display:
  DISPLAY_ORIENTATION: portrait
  DISPLAY_SIZE: 8.8"
  DISPLAY_RGB_LED: 0, 0, 0

static_images:
  BACKGROUND:
    PATH: {BG}
    X: 0
    Y: 0
    WIDTH: 480
    HEIGHT: 1920

STATS:
  # ── HEADER ───────────────────────────────────────────────────────────────
  DATE:
    INTERVAL: 1
    HOUR:
      TEXT:
        {text(x=20, y=8, font=FONT_EBOLD, size=60, color=TXT)}
    DAY:
      TEXT:
        {text(x=460, y=10, font=FONT_REG, size=22, color=TXT_DIM, anchor="rt")}
    DATE:
      TEXT:
        {text(x=460, y=42, font=FONT_REG, size=18, color=TXT_DIM, anchor="rt")}

  # ── CPU  (card 82..640, HDR_H=36, divider at 118) ────────────────────────
  CPU:
    PERCENTAGE:
      INTERVAL: 1
      TEXT:
        {text(x=20, y=126, font=FONT_EBOLD, size=58, color=TXT)}
      GRAPH:
        {bar(x=20, y=248, w=440, h=22)}
      LINE_GRAPH:
        {linegraph(x=20, y=462, w=440, h=160, autoscale=False)}
    TEMPERATURE:
      INTERVAL: 1
      TEXT:
        {text(x=460, y=130, font=FONT_BOLD, size=44, color=TXT, anchor="rt")}
    FREQUENCY:
      INTERVAL: 1
      TEXT:
        {text(x=20, y=202, font=FONT_BOLD, size=28, color=ACCENT)}
    FAN_SPEED:
      INTERVAL: 3
      TEXT:
        {text(x=460, y=207, font=FONT_REG, size=20, color=TXT_DIM, anchor="rt")}

  # ── GPU  (card 644..1000, HDR_H=36, divider at 680) ──────────────────────
  # GpuPowerW in header, GpuMemUsedGB/TotalGB via CUSTOM (built-ins hidden)
  GPU:
    INTERVAL: 1
    PERCENTAGE:
      TEXT:
        {text(x=20, y=688, font=FONT_EBOLD, size=58, color=TXT)}
      GRAPH:
        {bar(x=20, y=800, w=440, h=22)}
      LINE_GRAPH:
        {linegraph(x=20, y=866, w=440, h=100, autoscale=False)}
    TEMPERATURE:
      TEXT:
        {text(x=460, y=693, font=FONT_BOLD, size=44, color=TXT, anchor="rt")}
    MEMORY_PERCENT:
      GRAPH:
        {bar(x=20, y=830, w=440, h=14, color=ACCENT_DIM)}
    MEMORY_USED:
      SHOW: False
    MEMORY_TOTAL:
      SHOW: False

  # ── MEMORY  (card 1004..1174, HDR_H=36, divider at 1040) ─────────────────
  # MemUsedGB / MemTotalGB shown via CUSTOM sensors; built-in USED/TOTAL hidden.
  MEMORY:
    INTERVAL: 2
    VIRTUAL:
      PERCENT_TEXT:
        {text(x=460, y=1048, font=FONT_BOLD, size=44, color=TXT, anchor="rt")}
      GRAPH:
        {bar(x=20, y=1110, w=440, h=20)}
      LINE_GRAPH:
        {linegraph(x=20, y=1134, w=440, h=36, autoscale=False)}
      USED:
        SHOW: False
      FREE:
        SHOW: False
      TOTAL:
        SHOW: False

  # ── NET  (card 1178..1520, HDR_H=36, divider at 1214) ────────────────────
  NET:
    INTERVAL: 2
    ETH:
      DOWNLOAD:
        TEXT:
          {text(x=460, y=1222, font=FONT_BOLD, size=22, color=ACCENT, anchor="rt", indent=10)}
        LINE_GRAPH:
          SHOW: True
          X: 20
          Y: 1238
          WIDTH: 440
          HEIGHT: 120
          MIN_VALUE: 0
          MAX_VALUE: 1000000
          HISTORY_SIZE: 120
          AUTOSCALE: True
          LINE_COLOR: {GRAPH_LINE}
          LINE_WIDTH: 2
          AXIS: False
          BACKGROUND_IMAGE: {BG}
      UPLOAD:
        TEXT:
          {text(x=460, y=1366, font=FONT_BOLD, size=22, color=ACCENT, anchor="rt", indent=10)}
        LINE_GRAPH:
          SHOW: True
          X: 20
          Y: 1382
          WIDTH: 440
          HEIGHT: 120
          MIN_VALUE: 0
          MAX_VALUE: 1000000
          HISTORY_SIZE: 120
          AUTOSCALE: True
          LINE_COLOR: {ACCENT_DIM}
          LINE_WIDTH: 2
          AXIS: False
          BACKGROUND_IMAGE: {BG}

  # ── DISK  (card 1524..1918, HDR_H=36, divider at 1560) ───────────────────
  # DiskReadMBs / DiskWriteMBs shown via CUSTOM sensors below.
  DISK:
    INTERVAL: 3
    USED:
      PERCENT_TEXT:
        {text(x=460, y=1568, font=FONT_BOLD, size=44, color=TXT, anchor="rt")}
      GRAPH:
        {bar(x=20, y=1625, w=440, h=22)}
      TEXT:
        {text(x=20, y=1660, font=FONT_REG, size=20, color=TXT_DIM)}
    TOTAL:
      TEXT:
        {text(x=460, y=1660, font=FONT_REG, size=20, color=TXT_DIM, anchor="rt")}

{CUSTOM_BLOCK}
{percore_lines()}
"""


def main():
    out = Path(__file__).with_name("theme.yaml")
    out.write_text(THEME)
    print(f"wrote {out}  ({len(THEME.splitlines())} lines)")


if __name__ == "__main__":
    main()
