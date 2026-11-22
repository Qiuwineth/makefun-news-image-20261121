# THE WORLD ON SATURDAY - 21 November 2026 in one picture.
# Pure-stdlib front-page renderer: own rasterizer, own bitmap font, own PNG encoder.
# Runs in the bare grader image (no Pillow, no system fonts, no network).
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
PANEL = (233, 226, 203)
PANEL2 = (238, 232, 214)
INK = (18, 22, 28)
FAINT = (104, 108, 114)
RED = (172, 30, 38)
BLUE = (26, 72, 128)
GOLD = (176, 132, 32)
WHITE = (252, 250, 244)

canvas = bytearray(PAPER * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i] = c[0]
        canvas[i + 1] = c[1]
        canvas[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        base = (yy * W + x) * 3
        for xx in range(w):
            i = base + xx * 3
            canvas[i] = c[0]
            canvas[i + 1] = c[1]
            canvas[i + 2] = c[2]


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for ox in range(t):
            for oy in range(t):
                px(x0 + ox, y0 + oy, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, fill=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if fill:
                if d2 <= r * r:
                    px(xx, yy, c)
            else:
                if r * r - 2 * r < d2 <= r * r:
                    px(xx, yy, c)


def save_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += canvas[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph: 7 strings of 5 chars, '#' = ink.
# Lowercase letters reuse the uppercase shapes (small-caps poster style).
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "....#", "....#", "....#", "....#", "#...#", ".###."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": (".##..", "...#.", "....#", "....#", "....#", "...#.", ".##.."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "<": ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c, bold=False):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch)
        if g is None:
            cx += 6 * scale
            continue
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "#":
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
                    if bold:
                        rect(cx + col * scale + 1, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx - scale


def wrap(s, scale, max_w):
    words = s.split()
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, scale, c, max_w, leading=None, bold=False):
    if leading is None:
        leading = 9 * scale
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, c, bold)
        y += leading
    return y


# ---------------------------------------------------------------------------
# Coarse dot world map (64 x 30). '#' = land. Decorative panel graphic.
# ---------------------------------------------------------------------------
MAP = (
    "................................................................",
    "....######.......................##########.....................",
    "..##########......##..........##################....##..........",
    ".############....####........##########################.........",
    "##############..............###########################..#......",
    ".################..........##########################...........",
    "..##############............########################............",
    "...############..............######################.............",
    "....##########................####################..............",
    ".....########..................#################....##..........",
    "......######....................###############....####.........",
    ".......#####.....................#############......##..........",
    ".......#####......................###########...................",
    "........####.......................#########......##............",
    "........####........................#######......####...........",
    ".........###.........................#####......######..........",
    ".........####.........................###........####...........",
    "..........####........................##........................",
    "..........#####.................................................",
    "...........####.....................................###.........",
    "...........#####..................................#####.........",
    "............####.................................#######........",
    "............###...................................#####.........",
    ".............##....................................###..........",
    ".............##.................................................",
    "..............#.................................................",
    "..............#.................................................",
    "................................................................",
    "................................................................",
    "................................................................",
)


def draw_map(x, y, pitch, c_land, c_dot):
    for r, row in enumerate(MAP):
        row = (row + "." * 64)[:64]
        for i, ch in enumerate(row):
            cx = x + i * pitch
            cy = y + r * pitch
            if ch == "#":
                circle(cx, cy, 2, c_land)
            else:
                px(cx, cy, c_dot)


def panel(x, y, w, h, fill, edge=INK):
    rect(x, y, w, h, fill)
    hline(x, y, w, edge, 2)
    hline(x, y + h - 2, w, edge, 2)
    vline(x, y, h, edge, 2)
    vline(x + w - 2, y, h, edge, 2)


def kicker(x, y, s, c=RED):
    draw_text(x, y, s, 2, c, bold=True)
    return y + 20


def headline(x, y, s, scale, max_w, c=INK, leading=None):
    if leading is None:
        leading = 9 * scale
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, c, bold=True)
        y += leading
    return y


def byline(x, y, s):
    draw_text(x, y, s, 1, FAINT)
    return y + 12


# ---------------------------------------------------------------------------
# Poster copy - condensed from the verified facts file (every story >= 2 sources).
# ---------------------------------------------------------------------------
LEAD_KICKER = "CLIMATE SUMMIT - ANTALYA, TURKIYE"
LEAD_HEAD = "COP31 TALKS DEADLOCKED IN OVERTIME AS FOSSIL-FUEL WORDS VANISH FROM THE DRAFT"
LEAD_BODY = (
    "The UN climate summit in Antalya, scheduled to end on Friday, stretched deep into "
    "overtime on Saturday with nearly 200 countries still locked in negotiation and no "
    "deal in sight. A draft agreement circulated at the talks had removed every mention "
    "of fossil fuels and dropped a proposed 120 billion dollar target for finance to help "
    "developing countries adapt to a warming planet. Failure here would be the first "
    "time a UN climate summit has closed without an overarching agreement in more "
    "than a decade."
)
LEAD_QUOTE = '"IT IS EITHER GOING TO BE A GOOD DEAL OR IT IS GOING TO BE NO DEAL."'
LEAD_QUOTE_BY = "- WOPKE HOEKSTRA, EU CLIMATE COMMISSIONER"

GLANCE = (
    ("$120 BN", "ADAPTATION FINANCE TARGET DROPPED FROM COP31 DRAFT"),
    ("$92", "BRENT CRUDE AFTER TWO TANKERS HIT NEAR HORMUZ"),
    ("-900 PTS", "DOW JONES DROP AS AI SELL-OFF TIPS WALL ST INTO CORRECTION"),
    ("58", "WOUNDED IN RUSSIAN MISSILE STRIKE ON KRYVYI RIH, 6 OF THEM CHILDREN"),
    ("M 6.7", "EARTHQUAKE IN PERU'S ANDES: 1 DEAD, 16 HURT, 152 HOMES LOST"),
    ("128", "UN STATES AGREE TO NEGOTIATE 'KILLER ROBOT' RULES BY 2028"),
    ("11", "KILLED AS MEXICO CAPTURES FBI MOST-WANTED CARTEL BOSS"),
    ("2", "TANKERS ATTACKED IN THE STRAIT OF HORMUZ, UKMTO SAYS"),
)

S_HORMUZ_HEAD = "IRAN STRIKE SETS BAHRAIN PLANT ABLAZE; TANKERS HIT NEAR HORMUZ"
S_HORMUZ_BODY = (
    "Bahrain said an Iranian strike caused a fire at an industrial facility, and Iran's "
    "Guards claimed missile and drone strikes on US positions in Bahrain on Saturday "
    "night. Two tankers were attacked in the Strait of Hormuz, UKMTO reported, sending "
    "Brent crude to 92 dollars a barrel."
)
S_UKRAINE_HEAD = "RUSSIAN MISSILE KILLS TWO IN ZELENSKY'S HOMETOWN; SHIP HIT NEAR FINLAND"
S_UKRAINE_BODY = (
    "A Russian ballistic missile struck Kryvyi Rih, President Zelensky's hometown, "
    "killing two people and wounding 58, six of them children. In the Gulf of Finland, "
    "drones struck a Russia-bound cargo ship; Finnish forces said Ukraine was likely "
    "responsible."
)
S_WALLST_HEAD = "AI SELL-OFF TIPS WALL STREET INTO CORRECTION TERRITORY"
S_WALLST_BODY = (
    "US stocks fell sharply on Friday as a sell-off in AI and chip shares pushed the "
    "Dow and the S&P 500 into correction territory. The Dow dropped more than 900 "
    "points as investors questioned the valuations of the AI boom's biggest winners."
)
S_MEXICO_HEAD = "MEXICO CAPTURES FBI MOST-WANTED CARTEL BOSS 'EL CHAPO ISIDRO'"
S_MEXICO_BODY = (
    "Mexican special forces captured Fausto Isidro Meza Flores, 'El Chapo Isidro', a "
    "cartel leader on the FBI's Ten Most Wanted list, in Guasave, Sinaloa, after a "
    "shoot-out. Eleven people were killed in the violence."
)
S_PERU_HEAD = "MAGNITUDE 6.7 EARTHQUAKE SHAKES PERU'S ANDES"
S_PERU_BODY = (
    "A magnitude 6.7 earthquake struck about 30 km northwest of Junin at 129 km depth "
    "at 00:09 UTC and was felt in Lima. Civil defence (INDECI) recorded 1 dead, 16 "
    "injured and 152 homes left uninhabitable."
)
S_ROBOTS_HEAD = "UN STATES AGREE TO NEGOTIATE 'KILLER ROBOT' RULES"
S_ROBOTS_BODY = (
    "UN talks in Geneva on lethal autonomous weapons ended with the 128 member states "
    "of the CCW agreeing to negotiate new rules for such weapons within two years, by "
    "2028 - a first mandate of its kind."
)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def masthead():
    draw_text(28, 16, "SATURDAY EDITION", 2, INK, bold=True)
    draw_text(W - 28 - text_w("NO. 21-11 - PRICE: ONE IMAGE", 2), 16,
              "NO. 21-11 - PRICE: ONE IMAGE", 2, FAINT)
    title = "THE WORLD ON SATURDAY"
    draw_text((W - text_w(title, 6)) // 2, 38, title, 6, INK, bold=True)
    sub = "ALL THE DAY'S NEWS THAT FITS ON ONE PAGE - EVERY STORY CHECKED AGAINST TWO OR MORE SOURCES"
    draw_text((W - text_w(sub, 1)) // 2, 88, sub, 1, FAINT)
    hline(28, 104, W - 56, INK, 3)
    hline(28, 110, W - 56, INK, 1)


def glance_strip(y):
    draw_text(28, y, "THE DAY IN NUMBERS", 2, RED, bold=True)
    col_w = (W - 56) // 4
    yy = y + 22
    for i, (num, label) in enumerate(GLANCE):
        cx = 28 + (i % 4) * col_w
        cy = yy + (i // 4) * 56
        draw_text(cx, cy, num, 3, BLUE, bold=True)
        para(cx, cy + 28, label, 1, INK, col_w - 14, leading=10)
        if i % 4 != 3:
            vline(cx + col_w - 8, cy, 46, FAINT, 1)
    hline(28, yy + 116, W - 56, INK, 1)
    return yy + 124


def lead_block(x, y, w):
    y = kicker(x, y, LEAD_KICKER)
    y = headline(x, y, LEAD_HEAD, 3, w, leading=29)
    y += 4
    y = byline(x, y, "FROM THE SUMMIT HALLS - ANTALYA")
    y = para(x, y, LEAD_BODY, 2, INK, w, leading=19)
    y += 8
    panel(x, y, w, 64, PANEL2)
    para(x + 14, y + 9, LEAD_QUOTE, 2, RED, w - 28, leading=19)
    draw_text(x + 14, y + 46, LEAD_QUOTE_BY, 1, FAINT)
    return y + 64


def side_rail(x, y, w):
    panel(x, y, w, 206, PANEL)
    draw_text(x + 12, y + 9, "WHERE IT HAPPENED", 2, INK, bold=True)
    draw_map(x + 16, y + 36, 5, BLUE, (198, 190, 164))
    draw_text(x + 12, y + 182, "ANTALYA - HORMUZ - KRYVYI RIH - JUNIN - GENEVA", 1, FAINT)
    y2 = y + 220
    draw_text(x, y2, "WHY THE DRAFT FAILED", 2, RED, bold=True)
    bullets = (
        "FOSSIL FUELS: EVERY MENTION REMOVED FROM THE TEXT",
        "FINANCE: $120 BN ADAPTATION TARGET DROPPED",
        "LOSS AND DAMAGE: NO AGREED FUNDING SOURCE",
        "EU POSITION: A GOOD DEAL OR NO DEAL AT ALL",
    )
    yy = y2 + 22
    for b in bullets:
        draw_text(x, yy, "*", 2, RED, bold=True)
        yy = para(x + 16, yy + 2, b, 1, INK, w - 16, leading=10) + 5
    return yy


def story_col(x, y, w, kick, head, body, head_scale=2):
    y = kicker(x, y, kick)
    y = headline(x, y, head, head_scale, w, leading=17)
    y += 4
    y = para(x, y, body, 1, INK, w, leading=10)
    return y


def build():
    masthead()
    y = glance_strip(124)
    lead_block(28, y + 4, 600)
    side_rail(652, y + 4, 344)
    panel(652, 632, 344, 60, PANEL2)
    draw_text(666, 642, "NEARLY 200 COUNTRIES", 2, BLUE, bold=True)
    draw_text(666, 664, "AT THE TABLE IN ANTALYA - ONE DRAFT TEXT, STILL NO DEAL", 1, INK)
    row_y = 705
    hline(28, row_y - 10, W - 56, INK, 2)
    col_w = (W - 56 - 32) // 3
    story_col(28, row_y, col_w, "GULF", S_HORMUZ_HEAD, S_HORMUZ_BODY)
    story_col(28 + col_w + 16, row_y, col_w, "UKRAINE WAR",
              S_UKRAINE_HEAD, S_UKRAINE_BODY)
    story_col(28 + 2 * (col_w + 16), row_y, col_w, "MARKETS",
              S_WALLST_HEAD, S_WALLST_BODY)
    row2_y = 862
    hline(28, row2_y - 10, W - 56, INK, 1)
    story_col(28, row2_y, col_w, "MEXICO", S_MEXICO_HEAD, S_MEXICO_BODY)
    story_col(28 + col_w + 16, row2_y, col_w, "PERU", S_PERU_HEAD, S_PERU_BODY)
    story_col(28 + 2 * (col_w + 16), row2_y, col_w, "GENEVA",
              S_ROBOTS_HEAD, S_ROBOTS_BODY)
    hline(28, H - 44, W - 56, INK, 2)
    foot = ("SOURCES: REUTERS - ASSOCIATED PRESS - AFP - BBC - UKMTO - INDECI - IGP/USGS - "
            "INVESTORTRUST - RTM - ANTARA - ONE TURN NEWS - STANDARD TOPIC")
    draw_text(28, H - 34, foot, 1, FAINT)
    draw_text(28, H - 20, "DRAWN BY CODE, WITHOUT PHOTOGRAPHS - THE WORLD ON SATURDAY, 21 NOVEMBER 2026", 1, FAINT)


def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(os.path.abspath(__file__))
    save_png(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
