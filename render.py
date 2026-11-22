#!/usr/bin/env python3
"""THE WORLD ON SATURDAY - 21 November 2026 in one picture.

Pure standard-library poster renderer: its own raster canvas, its own
stroke font drawn from code, and its own PNG encoder (zlib + struct).
No Pillow, no system fonts, no network - it runs in a bare python image
and always produces the identical entry.png.
"""
import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (246, 241, 230)
INK = (20, 20, 20)
BODY = (52, 50, 46)
GRAY = (96, 92, 84)
RED = (178, 34, 34)
ORANGE = (196, 100, 0)
BLUE = (26, 86, 168)
PURPLE = (106, 27, 154)
OLIVE = (133, 106, 0)
TEAL = (0, 112, 122)
SKY = (198, 219, 236)
GREEN = (94, 158, 88)
SUN = (242, 197, 64)
SMOKE = (148, 143, 134)
LAT = (130, 158, 178)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg) * (w * h)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def stamp(self, cx, cy, r, color):
        r2 = r * r
        x0 = int(cx - r - 1)
        x1 = int(cx + r + 1)
        y0 = int(cy - r - 1)
        y1 = int(cy + r + 1)
        for y in range(y0, y1 + 1):
            dy = y - cy
            for x in range(x0, x1 + 1):
                dx = x - cx
                if dx * dx + dy * dy <= r2:
                    self.px(x, y, color)

    def line(self, x1, y1, x2, y2, color, thick):
        r = thick / 2.0
        dist = max(abs(x2 - x1), abs(y2 - y1))
        steps = max(2, int(dist * 2))
        for i in range(steps + 1):
            t = i / steps
            self.stamp(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, r, color)

    def fill_rect(self, x, y, w, h, color):
        for yy in range(int(y), int(y + h)):
            base = (yy * self.w + int(x)) * 3
            for xx in range(int(w)):
                i = base + xx * 3
                if 0 <= i < len(self.buf) - 2:
                    self.buf[i] = color[0]
                    self.buf[i + 1] = color[1]
                    self.buf[i + 2] = color[2]

    def rect_outline(self, x, y, w, h, color, thick):
        self.line(x, y, x + w, y, color, thick)
        self.line(x + w, y, x + w, y + h, color, thick)
        self.line(x + w, y + h, x, y + h, color, thick)
        self.line(x, y + h, x, y, color, thick)

    def fill_circle(self, cx, cy, r, color):
        self.stamp(cx, cy, r, color)

    def circle_outline(self, cx, cy, r, color, thick):
        pts = []
        n = 72
        for i in range(n + 1):
            import math
            a = 2 * math.pi * i / n
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        for i in range(n):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color, thick)

    def fill_polygon(self, pts, color, clip=None):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0 = max(0, int(min(xs)))
        x1 = min(self.w - 1, int(max(xs)) + 1)
        y0 = max(0, int(min(ys)))
        y1 = min(self.h - 1, int(max(ys)) + 1)
        n = len(pts)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if clip is not None:
                    cx, cy, cr = clip
                    if (x - cx) ** 2 + (y - cy) ** 2 > cr * cr:
                        continue
                inside = False
                j = n - 1
                for i in range(n):
                    xi, yi = pts[i]
                    xj, yj = pts[j]
                    if ((yi > y) != (yj > y)) and (
                            x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                        inside = not inside
                    j = i
                if inside:
                    self.px(x, y, color)


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h,
                                      8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# Stroke font. Each glyph is a list of polylines; points live in a box
# 4 units wide, cap height y=0..6, baseline y=6, x-height y=2..6,
# descenders reach y=8.4. Advance per character is 5 units.
GLYPHS = {
    'A': [[(0, 6), (2, 0), (4, 6)], [(0.9, 4), (3.1, 4)]],
    'B': [[(0, 0), (0, 6)],
          [(0, 0), (2.8, 0), (4, 1), (4, 2.2), (2.8, 3), (0, 3)],
          [(0, 3), (2.8, 3), (4, 4), (4, 5.2), (2.8, 6), (0, 6)]],
    'C': [[(4, 1.2), (2.8, 0), (1.2, 0), (0, 1.2), (0, 4.8), (1.2, 6),
           (2.8, 6), (4, 4.8)]],
    'D': [[(0, 0), (0, 6)],
          [(0, 0), (2.6, 0), (4, 1.2), (4, 4.8), (2.6, 6), (0, 6)]],
    'E': [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]],
    'F': [[(4, 0), (0, 0), (0, 6)], [(0, 3), (3, 3)]],
    'G': [[(4, 1.2), (2.8, 0), (1.2, 0), (0, 1.2), (0, 4.8), (1.2, 6),
           (2.8, 6), (4, 5), (4, 3.2), (2.6, 3.2)]],
    'H': [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    'I': [[(2, 0), (2, 6)], [(0.6, 0), (3.4, 0)], [(0.6, 6), (3.4, 6)]],
    'J': [[(4, 0), (4, 4.8), (3, 6), (1.2, 6), (0, 4.8)]],
    'K': [[(0, 0), (0, 6)], [(4, 0), (0, 3.4)], [(1.4, 3.9), (4, 6)]],
    'L': [[(0, 0), (0, 6), (4, 6)]],
    'M': [[(0, 6), (0, 0), (2, 2.8), (4, 0), (4, 6)]],
    'N': [[(0, 6), (0, 0), (4, 6), (4, 0)]],
    'O': [[(1.2, 0), (2.8, 0), (4, 1.2), (4, 4.8), (2.8, 6), (1.2, 6),
           (0, 4.8), (0, 1.2), (1.2, 0)]],
    'P': [[(0, 6), (0, 0), (2.8, 0), (4, 1), (4, 2.2), (2.8, 3.2),
           (0, 3.2)]],
    'Q': [[(1.2, 0), (2.8, 0), (4, 1.2), (4, 4.8), (2.8, 6), (1.2, 6),
           (0, 4.8), (0, 1.2), (1.2, 0)], [(2.4, 4.4), (4.2, 6.2)]],
    'R': [[(0, 6), (0, 0), (2.8, 0), (4, 1), (4, 2.2), (2.8, 3.2),
           (0, 3.2)], [(2, 3.2), (4, 6)]],
    'S': [[(4, 1.2), (2.8, 0), (1, 0), (0, 1.2), (0, 2.4), (1, 3),
           (3, 3.2), (4, 4.2), (4, 5.2), (2.8, 6), (1, 6), (0, 5)]],
    'T': [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    'U': [[(0, 0), (0, 4.8), (1.2, 6), (2.8, 6), (4, 4.8), (4, 0)]],
    'V': [[(0, 0), (2, 6), (4, 0)]],
    'W': [[(0, 0), (0.9, 6), (2, 2.4), (3.1, 6), (4, 0)]],
    'X': [[(0, 0), (4, 6)], [(4, 0), (0, 6)]],
    'Y': [[(0, 0), (2, 2.8), (4, 0)], [(2, 2.8), (2, 6)]],
    'Z': [[(0, 0), (4, 0), (0, 6), (4, 6)]],
    '0': [[(1.3, 0), (2.7, 0), (3.8, 1.2), (3.8, 4.8), (2.7, 6),
           (1.3, 6), (0.2, 4.8), (0.2, 1.2), (1.3, 0)]],
    '1': [[(1, 1.2), (2.6, 0), (2.6, 6)], [(0.6, 6), (3.8, 6)]],
    '2': [[(0.2, 1.2), (1.2, 0), (2.8, 0), (3.8, 1.2), (3.8, 2.4),
           (0.2, 6), (3.8, 6)]],
    '3': [[(0.2, 1), (1.2, 0), (2.8, 0), (3.8, 1), (3, 3), (1.4, 3)],
          [(3, 3), (3.8, 4), (3.8, 5.2), (2.8, 6), (1.2, 6), (0.2, 5)]],
    '4': [[(3.2, 6), (3.2, 0), (0, 4.2), (4, 4.2)]],
    '5': [[(3.8, 0), (0.2, 0), (0.2, 2.6), (2.8, 2.6), (3.8, 3.6),
           (3.8, 5), (2.8, 6), (1, 6), (0.2, 5.2)]],
    '6': [[(3.8, 1.2), (2.6, 0), (1.2, 0.4), (0.2, 2), (0.2, 5),
           (1.2, 6), (2.8, 6), (3.8, 5), (3.8, 3.6), (2.8, 2.8),
           (0.2, 3.2)]],
    '7': [[(0.2, 0), (3.8, 0), (1.6, 6)]],
    '8': [[(1.2, 0), (2.8, 0), (3.8, 0.9), (3.8, 2.1), (2.8, 3),
           (1.2, 3), (0.2, 2.1), (0.2, 0.9), (1.2, 0)],
          [(1.2, 3), (2.8, 3), (3.8, 3.9), (3.8, 5.1), (2.8, 6),
           (1.2, 6), (0.2, 5.1), (0.2, 3.9), (1.2, 3)]],
    '9': [[(0.2, 4.8), (1.4, 6), (2.8, 5.6), (3.8, 4), (3.8, 1),
           (2.8, 0), (1.2, 0), (0.2, 1), (0.2, 2.4), (1.2, 3.2),
           (3.8, 2.8)]],
    'a': [[(3.8, 2), (3.8, 6)],
          [(3.8, 3), (2.8, 2), (1, 2), (0.2, 3.2), (0.2, 5), (1, 6),
           (2.8, 6), (3.8, 5)]],
    'b': [[(0.2, 0), (0.2, 6)],
          [(0.2, 3.2), (1, 2.2), (2.8, 2.2), (3.8, 3.2), (3.8, 5),
           (2.8, 6), (1, 6), (0.2, 5.2)]],
    'c': [[(3.8, 3), (2.8, 2), (1, 2), (0.2, 3.2), (0.2, 5), (1, 6),
           (2.8, 6), (3.8, 5)]],
    'd': [[(3.8, 0), (3.8, 6)],
          [(3.8, 3), (2.8, 2), (1, 2), (0.2, 3.2), (0.2, 5), (1, 6),
           (2.8, 6), (3.8, 5)]],
    'e': [[(0.2, 4), (3.8, 4), (3.8, 3), (2.8, 2), (1, 2), (0.2, 3.2),
           (0.2, 5), (1, 6), (2.8, 6), (3.8, 5)]],
    'f': [[(3.4, 0.6), (2.4, 0), (1.6, 0.8), (1.6, 6)],
          [(0.4, 2.4), (3, 2.4)]],
    'g': [[(3.8, 2), (3.8, 7.6), (2.8, 8.4), (1, 8.4), (0.2, 7.6)],
          [(3.8, 3), (2.8, 2), (1, 2), (0.2, 3.2), (0.2, 5), (1, 6),
           (2.8, 6), (3.8, 5)]],
    'h': [[(0.2, 0), (0.2, 6)],
          [(0.2, 3.4), (1, 2.2), (2.8, 2.2), (3.8, 3.4), (3.8, 6)]],
    'i': [[(2, 2.2), (2, 6)], [(2, 0.4), (2, 1)]],
    'j': [[(2.4, 2.2), (2.4, 7.4), (1.6, 8.3), (0.4, 8.3)],
          [(2.4, 0.4), (2.4, 1)]],
    'k': [[(0.2, 0), (0.2, 6)], [(3.8, 2), (0.4, 4.4)],
          [(1.4, 3.8), (3.8, 6)]],
    'l': [[(2, 0), (2, 6)]],
    'm': [[(0.2, 2), (0.2, 6)],
          [(0.2, 3.2), (1, 2.2), (1.9, 2.4), (2, 3.4), (2, 6)],
          [(2, 3.2), (2.9, 2.2), (3.8, 2.4), (3.8, 6)]],
    'n': [[(0.2, 2), (0.2, 6)],
          [(0.2, 3.2), (1, 2.2), (2.8, 2.2), (3.8, 3.4), (3.8, 6)]],
    'o': [[(1, 2), (2.8, 2), (3.8, 3), (3.8, 5), (2.8, 6), (1, 6),
           (0.2, 5), (0.2, 3), (1, 2)]],
    'p': [[(0.2, 2), (0.2, 8.2)],
          [(0.2, 3.2), (1, 2.2), (2.8, 2.2), (3.8, 3.2), (3.8, 5),
           (2.8, 6), (1, 6), (0.2, 5.2)]],
    'q': [[(3.8, 2), (3.8, 8.2)],
          [(3.8, 3), (2.8, 2), (1, 2), (0.2, 3.2), (0.2, 5), (1, 6),
           (2.8, 6), (3.8, 5)]],
    'r': [[(0.2, 2), (0.2, 6)], [(0.2, 3.2), (1.2, 2.2), (3, 2.2)]],
    's': [[(3.8, 2.8), (2.8, 2), (1, 2), (0.2, 2.8), (0.2, 3.6),
           (1, 4), (2.8, 4.2), (3.8, 4.8), (3.8, 5.4), (2.8, 6),
           (1, 6), (0.2, 5.4)]],
    't': [[(2, 0.6), (2, 5.4), (2.8, 6), (3.8, 6)],
          [(0.4, 2.4), (3.6, 2.4)]],
    'u': [[(0.2, 2), (0.2, 5), (1, 6), (2.8, 6), (3.8, 5), (3.8, 2)],
          [(3.8, 5), (3.8, 6)]],
    'v': [[(0.2, 2), (2, 6), (3.8, 2)]],
    'w': [[(0.2, 2), (0.9, 6), (2, 3), (3.1, 6), (3.8, 2)]],
    'x': [[(0.2, 2), (3.8, 6)], [(3.8, 2), (0.2, 6)]],
    'y': [[(0.2, 2), (2, 5.4), (3.8, 2)],
          [(2, 5.4), (1.6, 7.6), (0.6, 8.3)]],
    'z': [[(0.2, 2), (3.8, 2), (0.2, 6), (3.8, 6)]],
    '.': [[(2, 5.6), (2, 6)]],
    ',': [[(2.2, 5.4), (1.7, 6.9)]],
    '·': [[(2, 3.1), (2, 3.5)]],
    '-': [[(0.6, 3.6), (3.4, 3.6)]],
    "'": [[(2.3, 0.2), (1.9, 1.6)]],
    '’': [[(2.3, 0.2), (1.9, 1.6)]],
    ':': [[(2, 2.5), (2, 2.9)], [(2, 5.3), (2, 5.7)]],
    '~': [[(0.2, 3.8), (1.1, 2.8), (2, 3.8), (2.9, 2.8), (3.8, 3.8)]],
    '&': [[(3.8, 6), (1.2, 2.6), (0.8, 1.4), (1.6, 0.2), (2.8, 0.2),
           (3.2, 1.2), (2.6, 2.4), (0.4, 4.6), (0.8, 5.6), (2.2, 5.8),
           (3.2, 5.2)]],
    '(': [[(3.2, 0), (1.8, 1.6), (1.8, 4.4), (3.2, 6)]],
    ')': [[(0.8, 0), (2.2, 1.6), (2.2, 4.4), (0.8, 6)]],
    '/': [[(3.8, 0), (0.2, 6)]],
    ' ': [],
}
GLYPHS['$'] = GLYPHS['S'] + [[(2, 0), (2, 6)]]


def text_w(s, unit):
    return len(s) * 5 * unit


def draw_text(cv, x, y, s, unit, color, bold=False, align='l'):
    w = text_w(s, unit)
    if align == 'c':
        x -= w / 2
    elif align == 'r':
        x -= w
    thick = unit * (0.98 if bold else 0.66)
    for i, ch in enumerate(s):
        glyph = GLYPHS.get(ch)
        if not glyph:
            continue
        ox = x + i * 5 * unit
        for poly in glyph:
            for a, b in zip(poly, poly[1:]):
                cv.line(ox + a[0] * unit, y + a[1] * unit,
                        ox + b[0] * unit, y + b[1] * unit, color, thick)


def fit_unit(s, maxw, unit):
    while text_w(s, unit) > maxw and unit > 1.0:
        unit -= 0.1
    return unit


def wrap(s, unit, maxw):
    lines = []
    cur = ''
    for word in s.split(' '):
        test = word if not cur else cur + ' ' + word
        if text_w(test, unit) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, s, unit, color, maxw, line_units, bold=False):
    for ln in wrap(s, unit, maxw):
        draw_text(cv, x, y, ln, unit, color, bold=bold)
        y += line_units * unit
    return y


def draw_globe(cv, cx, cy, r):
    import math
    cv.fill_circle(cx, cy, r, SKY)
    clip = (cx, cy, r - 3)
    land = [
        [(150, 302), (196, 288), (214, 306), (198, 332), (164, 334),
         (148, 320)],
        [(204, 372), (228, 368), (226, 404), (210, 424), (198, 398)],
        [(252, 318), (288, 312), (296, 340), (272, 368), (254, 344)],
        [(282, 292), (318, 298), (314, 328), (288, 324)],
        [(292, 392), (318, 390), (316, 410), (296, 408)],
    ]
    for poly in land:
        cv.fill_polygon(poly, GREEN, clip=clip)
    for k in (-0.6, -0.3, 0.0, 0.3, 0.6):
        yy = cy + k * r
        half = r * math.sqrt(max(0.0, 1 - k * k))
        cv.line(cx - half, yy, cx + half, yy, LAT, 1.5)
    for k in (0.35, 0.7):
        pts = []
        for i in range(41):
            t = 2 * math.pi * i / 40
            pts.append((cx + k * r * math.cos(t), cy + r * math.sin(t)))
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], LAT, 1.5)
    cv.line(cx, cy - r, cx, cy + r, LAT, 1.5)
    cv.circle_outline(cx, cy, r, INK, 3)


def draw_lead(cv):
    cv.rect_outline(28, 176, 968, 344, INK, 2.5)
    cv.fill_rect(28, 176, 968, 10, RED)
    draw_globe(cv, 218, 368, 100)
    cv.fill_circle(128, 262, 32, SUN)
    cv.fill_circle(140, 336, 20, SMOKE)
    cv.fill_circle(118, 352, 15, SMOKE)
    cv.fill_circle(110, 368, 11, SMOKE)
    cv.fill_rect(58, 432, 110, 46, INK)
    cv.fill_rect(84, 388, 18, 90, INK)
    cv.fill_rect(80, 384, 26, 8, INK)
    cv.line(383, 266, 383, 430, INK, 2.5)
    cv.line(401, 266, 401, 430, INK, 2.5)
    cv.line(383, 266, 401, 266, INK, 2.5)
    cv.circle_outline(392, 446, 17, INK, 2.5)
    cv.fill_rect(387, 326, 10, 112, RED)
    cv.fill_circle(392, 446, 12, RED)
    for ty in (282, 312, 342, 372, 402):
        cv.line(403, ty, 415, ty, INK, 2)
    draw_text(cv, 360, 220, '1.5C', 3.2, RED, bold=True)
    draw_text(cv, 448, 196, 'CLIMATE · ANTALYA, TURKIYE', 2.9, RED,
              bold=True)
    draw_text(cv, 448, 240, 'COP31 DEADLOCKED', 6.5, INK, bold=True)
    draw_text(cv, 448, 290, 'IN OVERTIME', 6.5, INK, bold=True)
    draw_block(cv, 448, 348,
               'UN climate talks blew past their Friday deadline with '
               'no deal, after a draft dropped any mention of fossil '
               'fuels - the very cause of the warming they met to stop.',
               2.6, BODY, 532, 8.4)
    cv.line(448, 464, 980, 464, INK, 1.5)
    stat = '~200 NATIONS · $120BN FINANCE TARGET DROPPED'
    draw_text(cv, 448, 476, stat, fit_unit(stat, 532, 2.6), INK, bold=True)


PANELS = [
    (ORANGE, 'GULF · BAHRAIN & HORMUZ',
     'Iran strike sets Bahrain plant ablaze',
     'Two tankers attacked in the Strait of Hormuz.', 'BRENT $92'),
    (BLUE, 'UKRAINE · KRYVYI RIH',
     "Russian missiles hit Zelensky's hometown",
     "Kyiv's drones hit a Russia-bound ship near Finland.",
     '2 DEAD · 58 HURT'),
    (RED, 'MARKETS · NEW YORK',
     'AI sell-off tips Wall St into correction',
     'Chip shares plunge as investors dump tech.', 'DOW -900 PTS'),
    (PURPLE, 'MEXICO · SINALOA',
     'FBI most-wanted cartel boss captured',
     "'El Chapo Isidro' seized in a Guasave shoot-out.", '11 KILLED'),
    (OLIVE, 'PERU · JUNIN',
     '6.7 quake shakes the Andes, felt in Lima',
     'Deep tremor near Junin leaves 1 dead, 16 hurt.', '152 HOMES LOST'),
    (TEAL, 'GENEVA · UNITED NATIONS',
     "Nations to negotiate 'killer robot' rules",
     '128 UN states open talks on autonomous weapons.', 'DEAL BY 2028'),
]


def draw_panel(cv, x, y, w, h, data):
    color, kicker, head, body, stat = data
    cv.rect_outline(x, y, w, h, INK, 2.5)
    cv.fill_rect(x, y, w, 8, color)
    draw_text(cv, x + 14, y + 16, kicker, 2.25, color, bold=True)
    endy = draw_block(cv, x + 14, y + 40, head, 3.3, INK, w - 28, 7.2,
                      bold=True)
    draw_block(cv, x + 14, endy + 8, body, 2.15, BODY, w - 28, 8.4)
    su = fit_unit(stat, w - 28, 3.6)
    draw_text(cv, x + 14, y + h - 40, stat, su, color, bold=True)


def main():
    cv = Canvas(W, H, CREAM)
    cv.rect_outline(10, 10, 1004, 1004, INK, 2)
    cv.line(28, 30, 996, 30, INK, 3)
    title = 'THE WORLD ON SATURDAY'
    draw_text(cv, 512, 40, title, fit_unit(title, 950, 9.2), INK,
              bold=True, align='c')
    cv.line(28, 110, 996, 110, INK, 5)
    draw_text(cv, 28, 124, 'ONE DAY · ONE PICTURE', 2.5, INK, bold=True)
    draw_text(cv, 512, 120, '21 NOVEMBER 2026', 3.6, RED, bold=True,
              align='c')
    draw_text(cv, 996, 124, 'WORLD NEWS IN BRIEF', 2.5, INK, bold=True,
              align='r')
    cv.line(28, 158, 996, 158, INK, 3)
    draw_lead(cv)
    cols = (28, 357, 686)
    for i, data in enumerate(PANELS):
        x = cols[i % 3]
        y = 538 if i < 3 else 770
        h = 218 if i < 3 else 208
        draw_panel(cv, x, y, 310, h, data)
    cv.line(28, 988, 996, 988, INK, 2)
    draw_text(cv, 512, 996,
              'Sources: Reuters · AP · AFP · BBC · RTM · INDECI · '
              'UKMTO - as reported on the day',
              2.0, GRAY, align='c')
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or os.path.dirname(
        os.path.abspath(__file__))
    write_png(cv, os.path.join(out_dir, 'entry.png'))


if __name__ == '__main__':
    main()
