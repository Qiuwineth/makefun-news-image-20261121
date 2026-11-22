#!/usr/bin/env python3
"""The World on Saturday - 21 November 2026 in one picture.

A deterministic poster drawn entirely with Pillow primitives: no network,
no external assets, no clock, no randomness. Running it twice writes the
same bytes. The image is written to $MAKEFUN_OUTPUT_DIR/entry.png, or to
/output/entry.png when the variable is unset (the grader's container).
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 28

PAPER = (247, 242, 231)
CARD = (255, 253, 246)
INK = (24, 24, 28)
FAINT = (108, 102, 92)
RED = (179, 32, 44)
SKY = (207, 228, 239)
LAND = (94, 148, 92)
SEA_LINE = (70, 110, 140)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def text_w(draw, s, f):
    box = draw.textbbox((0, 0), s, font=f)
    return box[2] - box[0]


def draw_centered(draw, cx, y, s, f, fill):
    draw.text((cx - text_w(draw, s, f) / 2, y), s, font=f, fill=fill)


def draw_spaced(draw, x, y, s, f, fill, tracking=3):
    """Draw text with extra letter tracking; returns the end x."""
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += text_w(draw, ch, f) + tracking
    return x - tracking


def draw_spaced_centered(draw, cx, y, s, f, fill, tracking=3):
    total = sum(text_w(draw, ch, f) for ch in s) + tracking * (len(s) - 1)
    return draw_spaced(draw, cx - total / 2, y, s, f, fill, tracking)


def wrap(draw, s, f, max_w):
    return wrap_multi(draw, s, f, [max_w])


def wrap_multi(draw, s, f, widths):
    """Greedy wrap where line i may use widths[min(i, len(widths)-1)]."""
    words = s.split()
    lines, cur, li = [], "", 0
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= widths[min(li, len(widths) - 1)]:
            cur = trial
        else:
            lines.append(cur)
            li += 1
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons

def icon_tanker(d, x, y, s, c):
    """Cargo ship with a flame over its deck."""
    d.polygon([(x, y + 0.62 * s), (x + s, y + 0.62 * s),
               (x + 0.86 * s, y + 0.86 * s), (x + 0.14 * s, y + 0.86 * s)], fill=c)
    d.rectangle([x + 0.18 * s, y + 0.44 * s, x + 0.52 * s, y + 0.62 * s], fill=c)
    d.rectangle([x + 0.58 * s, y + 0.50 * s, x + 0.82 * s, y + 0.62 * s], fill=c)
    fx, fy = x + 0.68 * s, y + 0.30 * s
    d.polygon([(fx, fy - 0.20 * s), (fx + 0.10 * s, fy + 0.02 * s),
               (fx + 0.03 * s, fy + 0.16 * s), (fx - 0.06 * s, fy + 0.16 * s),
               (fx - 0.11 * s, fy + 0.02 * s)], fill=RED)
    d.line([x + 0.04 * s, y + 0.97 * s, x + 0.96 * s, y + 0.97 * s], fill=c, width=4)


def icon_missile(d, x, y, s, c):
    """A rocket streaking up-right, flame at its tail, burst beside it."""
    import math
    # body: one thick diagonal stroke with a triangular nose
    x0, y0 = x + 0.30 * s, y + 0.70 * s
    x1, y1 = x + 0.66 * s, y + 0.34 * s
    d.line([x0, y0, x1, y1], fill=c, width=int(0.17 * s))
    d.polygon([(x1 - 0.10 * s, y1 + 0.13 * s), (x1 + 0.13 * s, y1 - 0.10 * s),
               (x1 + 0.24 * s, y1 + 0.13 * s)], fill=c)
    # fins
    d.polygon([(x0, y0), (x0 - 0.16 * s, y0 + 0.10 * s), (x0 + 0.02 * s, y0 + 0.16 * s)],
              fill=c)
    d.polygon([(x0, y0), (x0 + 0.10 * s, y0 - 0.16 * s), (x0 + 0.16 * s, y0 + 0.02 * s)],
              fill=c)
    # flame
    d.polygon([(x0 - 0.02 * s, y0 + 0.02 * s), (x0 - 0.20 * s, y0 + 0.24 * s),
               (x0 + 0.10 * s, y0 + 0.12 * s)], fill=RED)
    # burst star, lower right
    cx, cy, r = x + 0.80 * s, y + 0.82 * s, 0.13 * s
    pts = []
    for i in range(8):
        ang = i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=c)


def icon_chart(d, x, y, s, c):
    """Axes with a plunging line."""
    d.line([x + 0.10 * s, y + 0.08 * s, x + 0.10 * s, y + 0.88 * s], fill=c, width=5)
    d.line([x + 0.10 * s, y + 0.88 * s, x + 0.95 * s, y + 0.88 * s], fill=c, width=5)
    pts = [(x + 0.16 * s, y + 0.22 * s), (x + 0.38 * s, y + 0.34 * s),
           (x + 0.52 * s, y + 0.30 * s), (x + 0.86 * s, y + 0.74 * s)]
    d.line(pts, fill=RED, width=6, joint="curve")
    d.polygon([(x + 0.86 * s, y + 0.74 * s), (x + 0.70 * s, y + 0.72 * s),
               (x + 0.82 * s, y + 0.58 * s)], fill=RED)


def icon_cuffs(d, x, y, s, c):
    """Two handcuff rings set diagonally, joined by chain links."""
    r = 0.20 * s
    for cx, cy in [(x + 0.30 * s, y + 0.68 * s), (x + 0.72 * s, y + 0.36 * s)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=6)
        d.ellipse([cx - 0.045 * s, cy - r - 0.07 * s, cx + 0.045 * s, cy - r + 0.02 * s],
                  fill=c)
    d.line([x + 0.40 * s, y + 0.52 * s, x + 0.62 * s, y + 0.30 * s], fill=c, width=5)


def icon_quake(d, x, y, s, c):
    """Mountain ridge split by a seismic zigzag."""
    d.polygon([(x + 0.04 * s, y + 0.78 * s), (x + 0.34 * s, y + 0.30 * s),
               (x + 0.50 * s, y + 0.52 * s), (x + 0.66 * s, y + 0.24 * s),
               (x + 0.96 * s, y + 0.78 * s)], outline=c, width=6)
    pts = [(x + 0.10 * s, y + 0.94 * s), (x + 0.28 * s, y + 0.86 * s),
           (x + 0.42 * s, y + 0.95 * s), (x + 0.58 * s, y + 0.85 * s),
           (x + 0.72 * s, y + 0.95 * s), (x + 0.90 * s, y + 0.87 * s)]
    d.line(pts, fill=RED, width=5, joint="curve")


def icon_robot(d, x, y, s, c):
    """Robot head with antenna and eyes."""
    d.line([x + 0.50 * s, y + 0.06 * s, x + 0.50 * s, y + 0.22 * s], fill=c, width=5)
    d.ellipse([x + 0.43 * s, y + 0.00 * s, x + 0.57 * s, y + 0.12 * s], fill=RED)
    d.rounded_rectangle([x + 0.14 * s, y + 0.22 * s, x + 0.86 * s, y + 0.86 * s],
                        radius=10, outline=c, width=6)
    for cx in (x + 0.36 * s, x + 0.64 * s):
        d.ellipse([cx - 0.06 * s, y + 0.44 * s, cx + 0.06 * s, y + 0.56 * s], fill=c)
    d.line([x + 0.34 * s, y + 0.72 * s, x + 0.66 * s, y + 0.72 * s], fill=c, width=5)
    d.rectangle([x + 0.02 * s, y + 0.44 * s, x + 0.12 * s, y + 0.64 * s], fill=c)
    d.rectangle([x + 0.88 * s, y + 0.44 * s, x + 0.98 * s, y + 0.64 * s], fill=c)


# ---------------------------------------------------------------- lead art

def draw_lead_visual(img, d):
    """A globe under a rising thermometer, with smoke over a factory."""
    gx, gy, gr = 252, 352, 116
    # pale sun behind the globe
    d.ellipse([gx - gr - 34, gy - gr - 40, gx - gr + 44, gy - gr + 38],
              fill=(243, 205, 92))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=SKY + (255,))
    # simple continent blobs
    blobs = [
        [(gx - 78, gy - 62), (gx - 30, gy - 84), (gx - 8, gy - 48),
         (gx - 34, gy - 18), (gx - 70, gy - 26)],
        [(gx - 44, gy + 2), (gx - 12, gy + 6), (gx - 22, gy + 52),
         (gx - 44, gy + 76), (gx - 56, gy + 34)],
        [(gx + 22, gy - 70), (gx + 74, gy - 58), (gx + 84, gy - 20),
         (gx + 44, gy - 6), (gx + 20, gy - 34)],
        [(gx + 30, gy + 26), (gx + 66, gy + 34), (gx + 54, gy + 66),
         (gx + 28, gy + 52)],
    ]
    for blob in blobs:
        ld.polygon(blob, fill=LAND + (255,))
    # graticule: two meridian ellipses plus parallel lines
    for wf in (0.36, 0.72):
        ld.ellipse([gx - gr * wf, gy - gr, gx + gr * wf, gy + gr],
                   outline=SEA_LINE + (160,), width=2)
    for frac in (-0.62, -0.3, 0.0, 0.3, 0.62):
        wdt = gr * (1 - frac * frac) ** 0.5
        ld.line([gx - wdt, gy + frac * gr, gx + wdt, gy + frac * gr],
                fill=SEA_LINE + (160,), width=2)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=255)
    img.paste(layer, (0, 0), Image.composite(layer, Image.new("RGBA", (W, H)), mask))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=INK, width=5)
    # factory silhouette with smoke, bottom-left of the visual zone
    fx, fy = 66, 448
    d.rectangle([fx, fy - 34, fx + 108, fy], fill=INK)
    d.polygon([(fx + 8, fy - 34), (fx + 34, fy - 58), (fx + 60, fy - 34)], fill=INK)
    d.rectangle([fx + 76, fy - 74, fx + 92, fy - 30], fill=INK)
    for i, (sx, sy, sr) in enumerate([(fx + 84, fy - 92, 13), (fx + 98, fy - 112, 18),
                                      (fx + 118, fy - 128, 24)]):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(168, 160, 148))
    # thermometer, right of the globe
    tx, ttop, tbot = 428, 238, 452
    d.rounded_rectangle([tx - 13, ttop, tx + 13, tbot - 16], radius=13,
                        outline=INK, width=5, fill=(255, 255, 255))
    d.ellipse([tx - 27, tbot - 42, tx + 27, tbot + 12], outline=INK, width=5,
              fill=(255, 255, 255))
    d.rectangle([tx - 6, ttop + 52, tx + 6, tbot - 22], fill=RED)
    d.ellipse([tx - 17, tbot - 32, tx + 17, tbot + 2], fill=RED)
    for i in range(5):
        yy = ttop + 26 + i * 40
        d.line([tx + 18, yy, tx + 32, yy], fill=INK, width=4)
    draw_centered(d, tx, ttop - 34, "1.5C", font(SANS_B, 19), RED)


# ---------------------------------------------------------------- panels

PANELS = [
    {
        "kicker": "GULF · BAHRAIN & HORMUZ", "accent": (199, 81, 9),
        "icon": icon_tanker,
        "headline": "Iran strike sets Bahrain plant ablaze",
        "summary": "Two tankers attacked in the Strait of Hormuz.",
        "stat": "BRENT $92",
    },
    {
        "kicker": "UKRAINE · KRYVYI RIH", "accent": (29, 78, 158),
        "icon": icon_missile,
        "headline": "Russian missiles hit Zelensky's hometown",
        "summary": "Kyiv's drones hit a Russia-bound ship near Finland.",
        "stat": "2 DEAD · 58 HURT",
    },
    {
        "kicker": "MARKETS · NEW YORK", "accent": (179, 32, 44),
        "icon": icon_chart,
        "headline": "AI sell-off tips Wall St into correction",
        "summary": "Chip shares plunge as investors dump tech.",
        "stat": "DOW -900 PTS",
    },
    {
        "kicker": "MEXICO · SINALOA", "accent": (94, 43, 151),
        "icon": icon_cuffs,
        "headline": "FBI most-wanted cartel boss captured",
        "summary": "'El Chapo Isidro' seized in a Guasave shoot-out.",
        "stat": "11 KILLED",
    },
    {
        "kicker": "PERU · JUNIN", "accent": (122, 92, 0),
        "icon": icon_quake,
        "headline": "6.7 quake shakes the Andes, felt in Lima",
        "summary": "Deep tremor near Junin leaves 1 dead, 16 hurt.",
        "stat": "152 HOMES LOST",
    },
    {
        "kicker": "GENEVA · UNITED NATIONS", "accent": (0, 112, 124),
        "icon": icon_robot,
        "headline": "Nations to negotiate 'killer robot' rules",
        "summary": "128 UN states open talks on autonomous weapons.",
        "stat": "DEAL BY 2028",
    },
]


def draw_panel(d, x, y, w, h, p):
    accent = p["accent"]
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=INK, width=2)
    d.rectangle([x, y, x + w, y + 7], fill=accent)
    pad = 14
    f_kick = font(SANS_B, 15)
    draw_spaced(d, x + pad, y + 16, p["kicker"], f_kick, accent, tracking=1)
    # icon, top-right
    p["icon"](d, x + w - 74, y + 34, 58, accent)
    f_head = font(SANS_B, 23)
    lines = wrap_multi(d, p["headline"], f_head,
                       [w - 2 * pad - 66, w - 2 * pad - 66, w - 2 * pad])
    ly = y + 42
    for line in lines[:3]:
        d.text((x + pad, ly), line, font=f_head, fill=INK)
        ly += 28
    f_sum = font(SANS, 16)
    sy = y + 138
    for line in wrap(d, p["summary"], f_sum, w - 2 * pad)[:2]:
        d.text((x + pad, sy), line, font=f_sum, fill=(52, 50, 46))
        sy += 21
    f_stat = font(SANS_B, 26)
    d.text((x + pad, y + h - 40), p["stat"], font=f_stat, fill=accent)


# ---------------------------------------------------------------- build

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    d.line([MARGIN, 30, W - MARGIN, 30], fill=INK, width=2)
    draw_centered(d, W // 2, 40, "THE WORLD ON SATURDAY", font(SERIF_B, 56), INK)
    d.rectangle([MARGIN, 112, W - MARGIN, 118], fill=INK)
    d.text((MARGIN, 126), "ONE DAY · ONE PICTURE", font=font(SANS_B, 16), fill=INK)
    draw_spaced_centered(d, W // 2, 122, "21 NOVEMBER 2026", font(SANS_B, 29), RED,
                         tracking=4)
    right = "WORLD NEWS IN BRIEF"
    d.text((W - MARGIN - text_w(d, right, font(SANS_B, 16)), 126), right,
           font=font(SANS_B, 16), fill=INK)
    d.line([MARGIN, 156, W - MARGIN, 156], fill=INK, width=2)

    # lead panel
    lx, ly, lw, lh = MARGIN, 170, W - 2 * MARGIN, 336
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=CARD, outline=INK, width=2)
    d.rectangle([lx, ly, lx + lw, ly + 9], fill=RED)
    draw_lead_visual(img, d)
    tx = 500
    draw_spaced(d, tx, ly + 26, "CLIMATE · ANTALYA, TURKIYE", font(SANS_B, 19),
                RED, tracking=2)
    f_lead = font(SERIF_B, 40)
    for i, line in enumerate(["COP31 DEADLOCKED", "IN OVERTIME"]):
        d.text((tx, ly + 64 + i * 47), line, font=f_lead, fill=INK)
    f_sum = font(SANS, 20)
    body = ("UN climate talks blew past their Friday deadline with no deal, "
            "after a draft dropped any mention of fossil fuels - the very "
            "cause of the warming they met to stop.")
    sy = ly + 182
    for line in wrap(d, body, f_sum, lx + lw - tx - 22):
        d.text((tx, sy), line, font=f_sum, fill=(52, 50, 46))
        sy += 27
    d.line([tx, ly + 292, lx + lw - 22, ly + 292], fill=FAINT, width=2)
    d.text((tx, ly + 302), "~200 NATIONS  ·  $120BN FINANCE TARGET DROPPED",
           font=font(SANS_B, 16), fill=INK)

    # grid of six panels
    gap = 16
    pw = (W - 2 * MARGIN - 2 * gap) // 3
    ph = 216
    for i, p in enumerate(PANELS):
        px = MARGIN + (i % 3) * (pw + gap)
        py = 522 + (i // 3) * (ph + gap)
        draw_panel(d, px, py, pw, ph, p)

    # footer
    fy = 522 + 2 * ph + gap + 12
    d.line([MARGIN, fy, W - MARGIN, fy], fill=INK, width=2)
    draw_centered(
        d, W // 2, fy + 8,
        "Sources: Reuters · AP · AFP · BBC · RTM · INDECI · UKMTO - as reported on the day",
        font(SANS, 14), FAINT)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "entry.png")
    img.save(out, format="PNG", optimize=False)
    return out


if __name__ == "__main__":
    print(build())
