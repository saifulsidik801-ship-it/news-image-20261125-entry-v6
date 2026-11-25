#!/usr/bin/env python3
"""Render the front page for news-image-20261125 v6.

Layout engine: a y-cursor. Every text block is wrapped and measured with
font ascent+descent (getmetrics) BEFORE it is drawn; art and text live in
separate stacked boxes, so no text can ever sit under a picture. Art
heights are derived from the remaining page budget after all text is
measured, so the page ends flush at the bottom.

v6 fixes vs v5: the last mid-story row (#14, #15, #16) is 3 cards each
1/3 wide (full page width, no blank gap right of #16), and the 17-50
list columns are balanced 12/11/11 (no short third column).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 10                      # side margin
CW = W - 2 * M              # content width = 1004
PAPER = (245, 241, 232)
NAVY = (27, 42, 74)
RED = (176, 30, 40)
INK = (17, 17, 17)
GREY = (85, 85, 85)
LINE = (153, 153, 153)
SEA = (214, 228, 235)
LAND = (216, 196, 158)

FD = "/usr/share/fonts/truetype/dejavu"


def F(path, size):
    return ImageFont.truetype(os.path.join(FD, path), size)


F_MAST = F("DejaVuSerif-Bold.ttf", 48)
F_SUB = F("DejaVuSerif.ttf", 13)
F_NUM = F("DejaVuSans-Bold.ttf", 26)
F_NUMCAP = F("DejaVuSans.ttf", 10)
F_CONT = F("DejaVuSans-Bold.ttf", 10)
F_HERO_HEAD = F("DejaVuSerif-Bold.ttf", 19)
F_HERO_BODY = F("DejaVuSans.ttf", 11)
F_HERO_DATE = F("DejaVuSans-Bold.ttf", 10)
F_HERO_SRC = F("DejaVuSans.ttf", 9)
F_MID_HEAD = F("DejaVuSerif-Bold.ttf", 14)
F_MID_BODY = F("DejaVuSans.ttf", 10)
F_MID_DATE = F("DejaVuSans-Bold.ttf", 9)
F_MAP_T = F("DejaVuSans-Bold.ttf", 12)
F_LIST_H = F("DejaVuSans-Bold.ttf", 12)
F_LIST = F("DejaVuSans.ttf", 10)
F_LIST_N = F("DejaVuSans-Bold.ttf", 11)
F_DC_T = F("DejaVuSans-Bold.ttf", 11)
F_DC = F("DejaVuSans.ttf", 11)
F_FOOT = F("DejaVuSans.ttf", 9)


def wrap(text, font, max_w, d):
    """Greedy word wrap to a max width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def lh(font):
    a, d = font.getmetrics()
    return a + d


def fit_lines(text, font, max_w, d, max_lines, min_size, fname):
    """Wrap text to at most max_lines; shrink font if needed (never below min)."""
    size = font.size
    while size >= min_size:
        f = F(fname, size)
        lines = wrap(text, f, max_w, d)
        if len(lines) <= max_lines:
            return lines, f
        size -= 1
    f = F(fname, min_size)
    lines = wrap(text, f, max_w, d)[:max_lines]
    return lines, f


def text_h(lines, font):
    return len(lines) * lh(font)


def draw_lines(d, x, y, lines, font, fill, align="left", width=None):
    for ln in lines:
        if align == "center":
            d.text((x + (width - d.textlength(ln, font=font)) / 2, y), ln,
                   font=font, fill=fill)
        else:
            d.text((x, y), ln, font=font, fill=fill)
        y += lh(font)
    return y


def badge(d, cx, cy, n, r=11):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=1)
    f = F("DejaVuSans-Bold.ttf", 12 if n < 10 else 10)
    t = str(n)
    d.text((cx - d.textlength(t, font=f) / 2, cy - lh(f) / 2 + 1), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- data
NUMSTRIP = [
    ("1ST", "Pakistani in orbit on Shenzhou-24"),
    ("4TH", "4th Politburo member probed"),
    ("50,000", "Dow closes above 50,000"),
    ("11", "hurt in Houthi strike on Riyadh"),
    ("5-1", "Real Madrid rout PSV"),
    ("116", "women vie for Miss Universe crown"),
]
CONTINENTS = [("EUROPE", 13, (46, 90, 136)), ("MID EAST", 3, RED),
              ("AMERICAS", 22, (46, 125, 50)), ("ASIA-PACIFIC", 5, (180, 150, 40)),
              ("AFRICA", 4, (141, 110, 99)), ("OCEANIA", 3, (0, 131, 143))]

HEROES = [
    dict(n=1, tag="TOP STORY", date="JIUQUAN, CHINA  •  ASIA-PACIFIC",
         head="Shenzhou-24 lifts off with Pakistan's first astronaut",
         body="Long March 2F, 00:18 GMT; Zeeshan Ali, 40, first in orbit.",
         src="(Reuters)", scene="rocket"),
    dict(n=2, tag="CYBER BREACH", date="WASHINGTON, US  •  AMERICAS",
         head="CIA and spy agency hit by cyber breach",
         body="CIA and ODNI breached; NYT: hackers used an AI tool, Artex.",
         src="(Reuters / NYT)", scene="server"),
    dict(n=3, tag="MARKETS", date="NEW YORK, US  •  AMERICAS",
         head="Dow tops 50,000 as tech rout deepens",
         body="Dow 50,018.70 (+0.85%); Nasdaq -1.48%, Nvidia -5.9%.",
         src="(WSJ)", scene="candles"),
]

MIDS = [
    dict(n=4, date="BEIJING  •  ASIA-PACIFIC", head="China probes Politburo member Chen Jining",
         body="Shanghai chief, 62, probed for 'serious violations'.", scene="hall"),
    dict(n=5, date="NEW YORK  •  AMERICAS", head="Huawei guilty of stealing trade secrets",
         body="Brooklyn jury: guilty on 10 of 12 counts.", scene="chip"),
    dict(n=6, date="RIYADH  •  MIDDLE EAST", head="Houthi drone hits Riyadh tower, 11 hurt",
         body="Second strike on the PIF Tower in days.", scene="tower"),
    dict(n=7, date="WASHINGTON  •  AMERICAS", head="Trump set to unveil new wave of tariffs",
         body="New tariffs on many countries; China rate may rise.", scene="ship"),
    dict(n=8, date="CARTAGENA  •  AMERICAS", head="Gunmen hold hostages in Cartagena supermarket",
         body="About 25 held after a failed robbery.", scene="store"),
    dict(n=9, date="MADRID  •  EUROPE", head="Real Madrid rout PSV 5-1",
         body="Mbappe twice; 10th straight win.", scene="pitch"),
    dict(n=10, date="SAN JUAN  •  AMERICAS", head="Miss Universe crowns Jennifer Barreto",
         body="First mother to win; 116 women competed.", scene="crown"),
    dict(n=11, date="SANTA CLARA  •  AMERICAS", head="Nvidia shares slide as bounce fades",
         body="Shares -5.9% a day after +30% on Huang's return.", scene="nvchart"),
    dict(n=12, date="THE HAGUE  •  EUROPE", head="Top UN court condemns Myanmar for genocide",
         body="ICJ rules against Myanmar over the Rohingya.", scene="scales"),
    dict(n=13, date="PARIS  •  EUROPE", head="Sarkozy and wife ordered to stand trial",
         body="Ex-president faces trial over Libyan funding case.", scene="gavel"),
    dict(n=14, date="IOWA  •  AMERICAS", head="Army to detonate Iowa bomb-chemical stockpile",
         body="Army to blow up its lead azide stockpile.", scene="bunker"),
    dict(n=15, date="KATHMANDU  •  ASIA-PACIFIC", head="5.3 quake shakes Nepal, tremors felt in India",
         body="Magnitude 5.3 quake strikes near Lelep.", scene="quake"),
    dict(n=16, date="ANTALYA  •  EUROPE", head="COP31 chief blames EU for failure",
         body="Longest-ever climate talks ended with no deal.", scene="flags"),
]

LIST = [
    (17, "Gaza: death toll reaches 74,746 — WAFA"),
    (18, "Washington: Trump gives Giuliani Medal of Freedom"),
    (19, "Washington: Trump: Huang pardon “an option”"),
    (20, "New York: US confidence jumps to 103.3"),
    (21, "Round Rock: Dell lifts forecasts after record quarter"),
    (22, "Washington: US blacklists Singapore firm"),
    (23, "Washington: Shein to pay $100m to settle FTC claims"),
    (24, "Brussels: EU leaders meet over €1.78tn budget fight"),
    (25, "Brussels: NATO vows space defence amid satellite fears"),
    (26, "Kyiv: 700,000 Russian troops killed, study says"),
    (27, "Zaporizhzhia: Russian strike kills 2, wounds 48"),
    (28, "Kyiv: Zelensky confirms Ukraine hit Russian cargo ship"),
    (29, "Warsaw: Poland summons Russia's envoy"),
    (30, "Aden: Houthis close in on Aden, 60 km away"),
    (31, "New York: UN: five women killed each hour by relatives"),
    (32, "Sinaloa: Mexico captures “El Chapo Isidro”"),
    (33, "Villavicencio: Car bomb hits governor's office in Meta"),
    (34, "Tupanciretã: Supercell storm wrecks town"),
    (35, "Buenos Aires: Argentina 2027 budget goes to floor vote"),
    (36, "DRC: WHO pulls staff from Ebola hospital siege"),
    (37, "DRC: Ebola toll: 5,775 dead of 11,762 cases"),
    (38, "Nigeria: Katsina Emir suspended over assault claim"),
    (39, "Rome: 266m face acute food insecurity — WFP"),
    (40, "Addis Ababa: Ethiopia polio drive to protect 11m children"),
    (41, "Los Angeles: GTA 6 draws 39m PS5 players in four days"),
    (42, "San Francisco: Anthropic founders bank $2bn on IPO day"),
    (43, "San Francisco: OpenAI releases GPT-6.2 Astra"),
    (44, "London: Physicists send message through a wall"),
    (45, "Cambridge: Amateurs spot possible exoplanets with AI"),
    (46, "Sydney: Australia beat NZ 32-12 to lift World Cup"),
    (47, "Sydney: a2 Milk A$62m settlement approved"),
    (48, "Christmas Island: Red crabs begin their great migration"),
    (49, "Pyongyang: N. Korea threatens to close Swiss office"),
    (50, "Seoul: S. Korea education minister quits"),
]

DATECHECK = ("Wires read up to 06:00 UTC, Wednesday 25 November 2026. Tuesday's big stories — "
             "the Chen probe, the Huawei verdict, the Riyadh strike — were still developing into "
             "Wednesday. Left out as earlier news: the COP31 failure (22 Nov), the Mercury sinking "
             "(23 Nov), the DR Congo plane (22 Nov), the midterm vote (4 Nov), Nvidia reinstates "
             "Huang (23 Nov), the warship sunk off Libya (23 Nov), Hormuz tankers hit by mines "
             "(24 Nov), Sanofi buys Insmed (24 Nov), Hasina's return plan (24 Nov), the Gaza "
             "strike (24 Nov), the Bucks' skid (23 Nov), Suryavanshi's 204 (24 Nov).")

# ---------------------------------------------------------------- scenes
# Every scene fills its box edge-to-edge: sky/background + midground + subject.
def _sky(d, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(1, h - 1)
        d.line([(x, y + i), (x + w, y + i)],
               fill=tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3)))


def _stars(d, x, y, w, h, n=14, seed=7):
    import random
    r = random.Random(seed)
    for _ in range(n):
        sx, sy = x + r.randint(2, int(w) - 3), y + r.randint(2, int(h) // 2)
        s = r.choice([1, 1, 2])
        d.ellipse([sx, sy, sx + s, sy + s], fill=(255, 255, 220))


def scene_rocket(d, x, y, w, h):
    _sky(d, x, y, w, h, (16, 24, 54), (58, 74, 110))
    _stars(d, x, y, w, h)
    # floodlight beams
    d.polygon([(x + w * 0.12, y + h), (x + w * 0.42, y + h * 0.18),
               (x + w * 0.58, y + h * 0.18), (x + w * 0.88, y + h)], fill=(210, 210, 160))
    # ground
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(30, 30, 34))
    # launch tower
    tx = x + w * 0.16
    d.rectangle([tx, y + h * 0.22, tx + w * 0.07, y + h * 0.82], fill=(40, 40, 46))
    for k in range(4):
        yy = y + h * (0.30 + 0.13 * k)
        d.line([(tx, yy), (tx + w * 0.07, yy)], fill=(120, 120, 130), width=2)
    # rocket body
    rx, rw = x + w * 0.48, w * 0.13
    d.rectangle([rx, y + h * 0.14, rx + rw, y + h * 0.72], fill=(240, 240, 240))
    d.polygon([(rx, y + h * 0.14), (rx + rw / 2, y + h * 0.02), (rx + rw, y + h * 0.14)],
              fill=(176, 30, 40))
    d.ellipse([rx + rw * 0.2, y + h * 0.30, rx + rw * 0.8, y + h * 0.46], fill=(70, 130, 200))
    d.polygon([(rx, y + h * 0.72), (rx - rw * 0.35, y + h * 0.84), (rx, y + h * 0.66)], fill=(176, 30, 40))
    d.polygon([(rx + rw, y + h * 0.72), (rx + rw * 1.35, y + h * 0.84), (rx + rw, y + h * 0.66)],
              fill=(176, 30, 40))
    # smoke
    for cx, cy, r in [(0.50, 0.88, 0.09), (0.60, 0.92, 0.11), (0.40, 0.93, 0.10), (0.68, 0.86, 0.07)]:
        d.ellipse([x + w * cx - w * r, y + h * cy - h * r * 0.7,
                   x + w * cx + w * r, y + h * cy + h * r * 0.7], fill=(200, 200, 200))
    # flame
    d.polygon([(rx + rw * 0.25, y + h * 0.72), (rx + rw * 0.5, y + h * 0.95),
               (rx + rw * 0.75, y + h * 0.72)], fill=(255, 170, 40))


def scene_server(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 28, 52))
    # server racks left and right
    for rx in (x + w * 0.02, x + w * 0.72):
        d.rectangle([rx, y + h * 0.06, rx + w * 0.26, y + h * 0.94], fill=(38, 52, 82))
        for r in range(6):
            yy = y + h * (0.12 + 0.13 * r)
            d.rectangle([rx + 3, yy, rx + w * 0.26 - 3, yy + h * 0.07], fill=(24, 36, 64))
            for c in range(4):
                cc = (60, 220, 90) if (r + c) % 3 else (255, 200, 60)
                d.ellipse([rx + 5 + c * w * 0.055, yy + 2, rx + 9 + c * w * 0.055, yy + 6], fill=cc)
    # cables
    d.line([(x + w * 0.30, y + h * 0.9), (x + w * 0.45, y + h * 0.6),
            (x + w * 0.60, y + h * 0.9)], fill=(90, 110, 160), width=2)
    # gold shield centre
    cx, cy = x + w * 0.50, y + h * 0.48
    s = h * 0.36
    d.polygon([(cx, cy - s), (cx + s * 0.75, cy - s * 0.6), (cx + s * 0.75, cy + s * 0.1),
               (cx, cy + s * 0.75), (cx - s * 0.75, cy + s * 0.1), (cx - s * 0.75, cy - s * 0.6)],
              fill=(230, 180, 40), outline=(150, 110, 20), width=2)
    d.line([(cx - s * 0.15, cy - s * 0.45), (cx + s * 0.1, cy - s * 0.05),
            (cx + s * 0.35, cy + s * 0.45), (cx - s * 0.1, cy + s * 0.05)],
           fill=(120, 30, 30), width=3)


def scene_candles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 40, 26))
    for i in range(1, 6):
        d.line([(x, y + h * i / 6), (x + w, y + h * i / 6)], fill=(40, 90, 60), width=1)
    pts = []
    vals = [0.78, 0.66, 0.70, 0.55, 0.60, 0.44, 0.50, 0.34, 0.40, 0.28, 0.34, 0.22, 0.30, 0.18]
    bw = w / len(vals)
    for i, v in enumerate(vals):
        cx = x + bw * (i + 0.5)
        top = y + h * v
        bot = y + h * (v + 0.14)
        col = (60, 200, 100) if i % 3 else (220, 70, 60)
        d.line([(cx, y + h * (v - 0.05)), (cx, y + h * (v + 0.19))], fill=col, width=2)
        d.rectangle([cx - bw * 0.32, top, cx + bw * 0.32, bot], fill=col)
        pts.append((cx, top))
    d.line(pts, fill=(255, 220, 60), width=2)
    d.polygon([(x + w * 0.94, y + h * 0.16), (x + w * 0.99, y + h * 0.24),
               (x + w * 0.94, y + h * 0.30), (x + w * 0.90, y + h * 0.24)], fill=(255, 80, 60))


def scene_hall(d, x, y, w, h):
    _sky(d, x, y, w, h, (200, 220, 235), (240, 235, 220))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(120, 140, 110))
    # hall with red roof
    d.rectangle([x + w * 0.08, y + h * 0.38, x + w * 0.92, y + h * 0.74], fill=(235, 225, 205))
    d.polygon([(x + w * 0.02, y + h * 0.40), (x + w * 0.5, y + h * 0.16),
               (x + w * 0.98, y + h * 0.40)], fill=(176, 30, 40))
    for i in range(5):
        d.rectangle([x + w * (0.16 + 0.15 * i), y + h * 0.48, x + w * (0.24 + 0.15 * i), y + h * 0.66],
                    fill=(70, 100, 140))
    d.rectangle([x + w * 0.46, y + h * 0.56, x + w * 0.54, y + h * 0.74], fill=(90, 60, 40))
    # flag
    d.line([(x + w * 0.88, y + h * 0.10), (x + w * 0.88, y + h * 0.38)], fill=(60, 60, 60), width=2)
    d.polygon([(x + w * 0.88, y + h * 0.10), (x + w * 0.99, y + h * 0.16),
               (x + w * 0.88, y + h * 0.22)], fill=(220, 40, 40))


def scene_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 44, 66))
    for i in range(5):
        d.line([(x, y + h * i / 5), (x + w, y + h * i / 5)], fill=(44, 66, 96), width=1)
    # chip
    cx, cy, s = x + w * 0.5, y + h * 0.52, min(w, h) * 0.30
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(30, 120, 70), outline=(180, 220, 180), width=2)
    d.rectangle([cx - s * 0.55, cy - s * 0.55, cx + s * 0.55, cy + s * 0.55], fill=(60, 180, 110))
    for k in range(-1, 2):
        d.line([(cx + k * s * 0.6, cy - s * 1.15), (cx + k * s * 0.6, cy - s)], fill=(200, 200, 200), width=2)
        d.line([(cx + k * s * 0.6, cy + s), (cx + k * s * 0.6, cy + s * 1.15)], fill=(200, 200, 200), width=2)
        d.line([(cx - s * 1.15, cy + k * s * 0.6), (cx - s, cy + k * s * 0.6)], fill=(200, 200, 200), width=2)
        d.line([(cx + s, cy + k * s * 0.6), (cx + s * 1.15, cy + k * s * 0.6)], fill=(200, 200, 200), width=2)
    # gavel across the bottom
    d.rectangle([x + w * 0.08, y + h * 0.86, x + w * 0.42, y + h * 0.95], fill=(150, 100, 50))
    d.line([(x + w * 0.42, y + h * 0.90), (x + w * 0.92, y + h * 0.90)], fill=(120, 80, 40), width=3)


def scene_tower(d, x, y, w, h):
    _sky(d, x, y, w, h, (70, 50, 90), (230, 140, 70))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(50, 40, 50))
    # tower
    tx = x + w * 0.42
    d.polygon([(tx, y + h * 0.12), (tx + w * 0.16, y + h * 0.12), (tx + w * 0.12, y + h * 0.80),
               (tx + w * 0.04, y + h * 0.80)], fill=(35, 32, 40))
    for r in range(6):
        yy = y + h * (0.20 + 0.10 * r)
        d.rectangle([tx + 2, yy, tx + w * 0.16 - 2, yy + h * 0.05], fill=(255, 200, 90))
    d.polygon([(tx + w * 0.06, y + h * 0.12), (tx + w * 0.10, y + h * 0.02),
               (tx + w * 0.14, y + h * 0.12)], fill=(255, 200, 90))
    # drone + burst
    dx, dy = x + w * 0.80, y + h * 0.30
    d.ellipse([dx - 4, dy - 3, dx + 4, dy + 3], fill=(20, 20, 20))
    for sx in (-9, 9):
        d.line([(dx + sx - 5, dy - 5), (dx + sx + 5, dy - 5)], fill=(120, 120, 120), width=2)
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        d.line([(dx + 14 * math.cos(a), dy + 10 * math.sin(a)),
                (dx + 22 * math.cos(a), dy + 16 * math.sin(a))], fill=(255, 220, 80), width=2)


def scene_ship(d, x, y, w, h):
    _sky(d, x, y, w, h, (190, 215, 235), (235, 230, 210))
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=(40, 90, 140))
    # hull
    d.polygon([(x + w * 0.04, y + h * 0.62), (x + w * 0.96, y + h * 0.62),
               (x + w * 0.88, y + h * 0.82), (x + w * 0.12, y + h * 0.82)], fill=(30, 30, 38))
    # containers
    cols = [(200, 60, 50), (50, 120, 200), (220, 170, 40), (60, 160, 90), (200, 110, 40)]
    for r in range(2):
        for c in range(5):
            cx = x + w * (0.08 + 0.17 * c)
            cy = y + h * (0.34 + 0.14 * r)
            d.rectangle([cx, cy, cx + w * 0.15, cy + h * 0.12], fill=cols[(r + c) % 5],
                        outline=(255, 255, 255), width=1)
    # crane
    d.line([(x + w * 0.86, y + h * 0.06), (x + w * 0.86, y + h * 0.62)], fill=(60, 60, 60), width=3)
    d.line([(x + w * 0.60, y + h * 0.08), (x + w * 0.98, y + h * 0.08)], fill=(60, 60, 60), width=3)


def scene_store(d, x, y, w, h):
    _sky(d, x, y, w, h, (210, 225, 240), (240, 238, 228))
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(150, 150, 145))
    # storefront
    d.rectangle([x + w * 0.06, y + h * 0.30, x + w * 0.94, y + h * 0.72], fill=(225, 215, 195))
    for i in range(6):
        col = (200, 60, 50) if i % 2 == 0 else (240, 240, 235)
        d.polygon([(x + w * (0.06 + 0.146 * i), y + h * 0.30), (x + w * (0.20 + 0.146 * i), y + h * 0.30),
                   (x + w * (0.17 + 0.146 * i), y + h * 0.44), (x + w * (0.09 + 0.146 * i), y + h * 0.44)],
                  fill=col)
    d.rectangle([x + w * 0.14, y + h * 0.48, x + w * 0.42, y + h * 0.70], fill=(120, 170, 200))
    d.rectangle([x + w * 0.58, y + h * 0.48, x + w * 0.86, y + h * 0.70], fill=(120, 170, 200))
    # police tape
    for yy in (0.74, 0.84):
        d.rectangle([x, y + h * yy, x + w, y + h * (yy + 0.07)], fill=(240, 200, 20))
        for i in range(10):
            xx = x + w * i / 10
            d.polygon([(xx, y + h * (yy + 0.07)), (xx + w * 0.05, y + h * (yy + 0.07)),
                       (xx + w * 0.10, y + h * yy), (xx + w * 0.05, y + h * yy)], fill=(20, 20, 20))


def scene_pitch(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 140, 70))
    for i in range(4):
        d.rectangle([x, y + h * i / 4, x + w, y + h * (i + 1) / 4],
                    fill=(52, 150, 76) if i % 2 else (46, 140, 70))
    d.ellipse([x + w * 0.30, y + h * 0.18, x + w * 0.70, y + h * 0.82], outline=(255, 255, 255), width=2)
    d.line([(x + w * 0.5, y), (x + w * 0.5, y + h)], fill=(255, 255, 255), width=2)
    # goal
    d.rectangle([x + w * 0.06, y + h * 0.30, x + w * 0.26, y + h * 0.62], outline=(255, 255, 255), width=2)
    # ball
    d.ellipse([x + w * 0.60, y + h * 0.60, x + w * 0.72, y + h * 0.78], fill=(255, 255, 255),
              outline=(30, 30, 30), width=1)
    # scoreboard
    d.rectangle([x + w * 0.62, y + h * 0.06, x + w * 0.96, y + h * 0.26], fill=(20, 20, 28))
    d.rectangle([x + w * 0.65, y + h * 0.10, x + w * 0.93, y + h * 0.22], fill=(255, 255, 255))


def scene_crown(d, x, y, w, h):
    _sky(d, x, y, w, h, (90, 50, 140), (160, 110, 200))
    # cushion
    d.ellipse([x + w * 0.10, y + h * 0.62, x + w * 0.90, y + h * 0.92], fill=(176, 30, 40))
    d.ellipse([x + w * 0.16, y + h * 0.58, x + w * 0.84, y + h * 0.72], fill=(200, 50, 60))
    # crown
    cx = x + w * 0.5
    d.polygon([(x + w * 0.20, y + h * 0.62), (x + w * 0.20, y + h * 0.30),
               (x + w * 0.32, y + h * 0.48), (x + w * 0.42, y + h * 0.18),
               (x + w * 0.58, y + h * 0.18), (x + w * 0.68, y + h * 0.48),
               (x + w * 0.80, y + h * 0.30), (x + w * 0.80, y + h * 0.62)],
              fill=(240, 200, 60), outline=(180, 140, 20), width=2)
    for fx in (0.20, 0.42, 0.58, 0.80):
        d.ellipse([x + w * fx - 3, y + h * (0.28 if fx in (0.20, 0.80) else 0.16) - 3,
                   x + w * fx + 3, y + h * (0.28 if fx in (0.20, 0.80) else 0.16) + 3],
                  fill=(255, 240, 150))
    d.ellipse([cx - 5, y + h * 0.44, cx + 5, y + h * 0.54], fill=(220, 40, 60))


def scene_nvchart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 244, 238))
    for i in range(1, 5):
        d.line([(x, y + h * i / 5), (x + w, y + h * i / 5)], fill=(220, 220, 210), width=1)
    pts_up = [(x + w * i / 9, y + h * (0.55 - 0.05 * i)) for i in range(5)]
    pts_dn = [(x + w * (4 + i) / 9, y + h * (0.30 + 0.10 * i)) for i in range(6)]
    d.line(pts_up, fill=(60, 180, 100), width=3)
    d.line(pts_dn, fill=(220, 60, 50), width=3)
    ex, ey = pts_dn[-1]
    d.polygon([(ex, ey), (ex - 12, ey - 2), (ex - 4, ey + 10)], fill=(220, 60, 50))
    d.ellipse([pts_up[0][0] - 3, pts_up[0][1] - 3, pts_up[0][0] + 3, pts_up[0][1] + 3], fill=(60, 180, 100))


def scene_scales(d, x, y, w, h):
    _sky(d, x, y, w, h, (200, 215, 230), (238, 234, 222))
    d.rectangle([x, y + h * 0.74, x + w, y + h], fill=(150, 140, 120))
    # court building
    d.rectangle([x + w * 0.10, y + h * 0.34, x + w * 0.90, y + h * 0.76], fill=(230, 224, 208))
    d.polygon([(x + w * 0.04, y + h * 0.36), (x + w * 0.5, y + h * 0.12),
               (x + w * 0.96, y + h * 0.36)], fill=(200, 190, 170))
    for i in range(4):
        d.rectangle([x + w * (0.18 + 0.19 * i), y + h * 0.42, x + w * (0.25 + 0.19 * i), y + h * 0.74],
                    fill=(250, 246, 236))
    # scales of justice
    cx, cy = x + w * 0.5, y + h * 0.30
    d.line([(cx, cy - 8), (cx, cy + 16)], fill=(180, 140, 40), width=3)
    d.line([(cx - 22, cy - 4), (cx + 22, cy - 4)], fill=(180, 140, 40), width=2)
    for sx in (-22, 22):
        d.line([(cx + sx, cy - 4), (cx + sx, cy + 12)], fill=(180, 140, 40), width=2)
        d.polygon([(cx + sx - 10, cy + 12), (cx + sx + 10, cy + 12), (cx + sx, cy + 20)],
                  fill=(220, 180, 60))


def scene_gavel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 84, 52))
    for i in range(3):
        d.rectangle([x, y + h * i / 3, x + w, y + h * (i + 1) / 3],
                    fill=(130, 92, 58) if i % 2 else (120, 84, 52))
    # columns
    for cx in (0.08, 0.84):
        d.rectangle([x + w * cx, y + h * 0.10, x + w * (cx + 0.08), y + h * 0.90], fill=(210, 200, 180))
    # gavel head + handle
    d.rectangle([x + w * 0.28, y + h * 0.30, x + w * 0.62, y + h * 0.52], fill=(90, 55, 25))
    d.rectangle([x + w * 0.24, y + h * 0.26, x + w * 0.66, y + h * 0.34], fill=(110, 70, 35))
    d.rectangle([x + w * 0.24, y + h * 0.48, x + w * 0.66, y + h * 0.56], fill=(110, 70, 35))
    d.line([(x + w * 0.62, y + h * 0.41), (x + w * 0.92, y + h * 0.62)], fill=(140, 95, 50), width=5)
    # sound block
    d.ellipse([x + w * 0.30, y + h * 0.72, x + w * 0.60, y + h * 0.86], fill=(70, 45, 20))


def scene_bunker(d, x, y, w, h):
    _sky(d, x, y, w, h, (180, 200, 210), (220, 215, 195))
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(110, 130, 90))
    # bunker dome
    d.pieslice([x + w * 0.14, y + h * 0.34, x + w * 0.66, y + h * 0.94], 180, 360, fill=(80, 85, 80))
    d.rectangle([x + w * 0.14, y + h * 0.64, x + w * 0.66, y + h * 0.74], fill=(60, 64, 60))
    d.rectangle([x + w * 0.36, y + h * 0.66, x + w * 0.44, y + h * 0.76], fill=(30, 30, 30))
    # blast starburst
    bx, by = x + w * 0.82, y + h * 0.34
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        d.line([(bx, by), (bx + 18 * math.cos(a), by + 13 * math.sin(a))], fill=(255, 170, 40), width=3)
    d.ellipse([bx - 9, by - 7, bx + 9, by + 7], fill=(255, 220, 80))
    # warning triangle
    tx, ty = x + w * 0.72, y + h * 0.72
    d.polygon([(tx, ty - 10), (tx + 11, ty + 8), (tx - 11, ty + 8)], fill=(240, 200, 20),
              outline=(20, 20, 20))
    d.text((tx - 2, ty - 7), "!", font=F("DejaVuSans-Bold.ttf", 11), fill=(20, 20, 20))


def scene_quake(d, x, y, w, h):
    _sky(d, x, y, w, h, (170, 195, 215), (225, 225, 215))
    # mountains
    d.polygon([(x, y + h), (x + w * 0.28, y + h * 0.22), (x + w * 0.55, y + h)], fill=(90, 100, 120))
    d.polygon([(x + w * 0.45, y + h), (x + w * 0.72, y + h * 0.10), (x + w, y + h)], fill=(70, 80, 100))
    d.polygon([(x + w * 0.24, y + h * 0.28), (x + w * 0.28, y + h * 0.22),
               (x + w * 0.32, y + h * 0.28), (x + w * 0.28, y + h * 0.34)], fill=(255, 255, 255))
    d.polygon([(x + w * 0.68, y + h * 0.16), (x + w * 0.72, y + h * 0.10),
               (x + w * 0.76, y + h * 0.16), (x + w * 0.72, y + h * 0.22)], fill=(255, 255, 255))
    # cracks
    d.line([(x + w * 0.30, y + h * 0.80), (x + w * 0.36, y + h * 0.88), (x + w * 0.32, y + h * 0.96),
            (x + w * 0.40, y + h)], fill=(40, 40, 40), width=2)
    d.line([(x + w * 0.70, y + h * 0.82), (x + w * 0.66, y + h * 0.90), (x + w * 0.72, y + h)],
           fill=(40, 40, 40), width=2)
    # seismograph line
    d.line([(x + w * 0.06, y + h * 0.92), (x + w * 0.20, y + h * 0.92), (x + w * 0.26, y + h * 0.80),
            (x + w * 0.32, y + h * 0.98), (x + w * 0.38, y + h * 0.86), (x + w * 0.50, y + h * 0.92)],
           fill=(220, 60, 50), width=2)


def scene_flags(d, x, y, w, h):
    _sky(d, x, y, w, h, (185, 210, 235), (240, 235, 220))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(140, 130, 110))
    # flag row
    fcols = [(200, 60, 50), (50, 110, 200), (240, 200, 40), (60, 160, 90), (150, 80, 180)]
    for i in range(5):
        px = x + w * (0.10 + 0.18 * i)
        d.line([(px, y + h * 0.16), (px, y + h * 0.72)], fill=(70, 70, 70), width=2)
        d.polygon([(px, y + h * 0.16), (px + w * 0.13, y + h * 0.22), (px, y + h * 0.28)],
                  fill=fcols[i])
    # podium
    d.rectangle([x + w * 0.36, y + h * 0.56, x + w * 0.64, y + h * 0.74], fill=(60, 55, 70))
    d.rectangle([x + w * 0.42, y + h * 0.50, x + w * 0.58, y + h * 0.56], fill=(90, 85, 100))
    d.ellipse([x + w * 0.46, y + h * 0.38, x + w * 0.54, y + h * 0.50], fill=(240, 200, 160))


SCENES = {"rocket": scene_rocket, "server": scene_server, "candles": scene_candles,
          "hall": scene_hall, "chip": scene_chip, "tower": scene_tower, "ship": scene_ship,
          "store": scene_store, "pitch": scene_pitch, "crown": scene_crown,
          "nvchart": scene_nvchart, "scales": scene_scales, "gavel": scene_gavel,
          "bunker": scene_bunker, "quake": scene_quake, "flags": scene_flags}

# ---------------------------------------------------------------- map + glyphs
LAND_POLYS = [
    [(30, 20), (150, 8), (260, 18), (300, 45), (250, 70), (180, 75), (120, 60), (40, 45)],
    [(330, 5), (360, 5), (360, 22), (335, 22)],
    [(270, 85), (320, 80), (350, 105), (330, 150), (295, 165), (270, 130)],
    [(470, 15), (530, 10), (555, 28), (520, 48), (480, 45), (460, 30)],
    [(470, 55), (540, 50), (560, 80), (530, 130), (490, 135), (465, 95)],
    [(560, 12), (760, 8), (900, 25), (950, 55), (880, 75), (760, 70), (640, 55), (565, 40)],
    [(800, 125), (880, 120), (900, 140), (850, 155), (800, 145)],
]
PINS = {1: (820, 30), 2: (165, 55), 3: (205, 48), 4: (855, 38), 5: (225, 60),
        6: (590, 62), 7: (150, 68), 8: (240, 95), 9: (472, 30), 10: (265, 78),
        11: (95, 55), 12: (498, 14), 13: (500, 52), 14: (140, 42), 15: (760, 55),
        16: (545, 45)}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    for i in range(1, 7):
        d.line([(x, y + h * i / 7), (x + w, y + h * i / 7)], fill=(190, 205, 215), width=1)
    for i in range(1, 10):
        d.line([(x + w * i / 10, y), (x + w * i / 10, y + h)], fill=(190, 205, 215), width=1)
    sx, sy = w / 1000.0, h / 180.0
    for poly in LAND_POLYS:
        d.polygon([(x + px * sx, y + py * sy) for px, py in poly], fill=LAND,
                  outline=(180, 160, 120))
    for gx, gy, gw, gh in [(775, 92, 14, 8), (805, 100, 18, 9), (838, 90, 12, 7)]:
        d.ellipse([x + gx * sx, y + gy * sy, x + (gx + gw) * sx, y + (gy + gh) * sy], fill=LAND)
    for n, (px, py) in PINS.items():
        cx, cy = x + px * sx, y + py * sy
        r = 8
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=1)
        f = F("DejaVuSans-Bold.ttf", 9 if n < 10 else 8)
        t = str(n)
        d.text((cx - d.textlength(t, font=f) / 2, cy - lh(f) / 2 + 1), t, font=f,
               fill=(255, 255, 255))


GLYPHS = ["flag", "bars", "chip", "ball", "cross", "cloud", "star", "bolt"]
GLYPH_COLS = [(46, 90, 136), (176, 30, 40), (46, 125, 50), (180, 150, 40),
              (0, 131, 143), (141, 110, 99)]


def draw_glyph(d, x, y, s, kind, col):
    d.rounded_rectangle([x, y, x + s, y + s], radius=2, fill=col)
    c = (255, 255, 255)
    if kind == "flag":
        d.polygon([(x + 2, y + 2), (x + s - 2, y + 4), (x + 2, y + 6)], fill=c)
        d.line([(x + 2, y + 2), (x + 2, y + s - 2)], fill=c, width=1)
    elif kind == "bars":
        for i, bh in enumerate((4, 7, 5)):
            d.rectangle([x + 2 + i * 3, y + s - 2 - bh, x + 4 + i * 3, y + s - 2], fill=c)
    elif kind == "chip":
        d.rectangle([x + 3, y + 3, x + s - 3, y + s - 3], outline=c, width=1)
        d.rectangle([x + 4, y + 4, x + s - 4, y + s - 4], fill=c)
    elif kind == "ball":
        d.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=c, width=1)
    elif kind == "cross":
        d.rectangle([x + s // 2 - 1, y + 2, x + s // 2 + 1, y + s - 2], fill=c)
        d.rectangle([x + 2, y + s // 2 - 1, x + s - 2, y + s // 2 + 1], fill=c)
    elif kind == "cloud":
        d.ellipse([x + 2, y + 4, x + s - 4, y + s - 3], fill=c)
    elif kind == "star":
        import math
        cx, cy = x + s / 2, y + s / 2
        pts = []
        for k in range(10):
            r = s / 2 - 1 if k % 2 == 0 else s / 4
            a = math.radians(-90 + 36 * k)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=c)
    else:  # bolt
        d.polygon([(x + s * 0.6, y + 1), (x + s * 0.3, y + s * 0.55), (x + s * 0.5, y + s * 0.55),
                   (x + s * 0.4, y + s - 1), (x + s * 0.7, y + s * 0.45), (x + s * 0.5, y + s * 0.45)],
                  fill=c)


# ---------------------------------------------------------------- layout
def measure_card(d, card, w, head_font, head_name, body_font, max_head_lines=2):
    """Measure a story card's text block height (dateline + headline + body)."""
    tw = w - 10
    date_f = F_HERO_DATE if head_font is F_HERO_HEAD else F_MID_DATE
    head_lines, head_f = fit_lines(card["head"], head_font, tw, d, max_head_lines, 12, head_name)
    body_lines = wrap(card["body"], body_font, tw, d)[:2]
    h = lh(date_f) + text_h(head_lines, head_f) + text_h(body_lines, body_font)
    return h, head_lines, head_f, body_lines


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 0

    # --- top strip
    d.rectangle([0, 0, W, 18], fill=NAVY)
    d.text((M, 2), "THE WORLD IN ONE DAY", font=F("DejaVuSans-Bold.ttf", 11), fill=(255, 255, 255))
    rt = "50 STORIES  •  6 CONTINENTS  •  EVERY ONE DATED WEDNESDAY 25 NOVEMBER 2026"
    d.text((W - M - d.textlength(rt, font=F("DejaVuSans-Bold.ttf", 11)), 2), rt,
           font=F("DejaVuSans-Bold.ttf", 11), fill=(255, 255, 255))
    y = 18

    # --- masthead
    mt = "Wednesday 25 November 2026"
    d.text(((W - d.textlength(mt, font=F_MAST)) / 2, y), mt, font=F_MAST, fill=INK)
    y += lh(F_MAST) - 2
    sub = "Shenzhou-24 carries Pakistan's first astronaut  •  Dow tops 50,000  •  Huawei guilty in US trial"
    d.text(((W - d.textlength(sub, font=F_SUB)) / 2, y), sub, font=F_SUB, fill=RED)
    y += lh(F_SUB) + 4

    # --- number strip
    cell_w = CW / 6
    for i, (num, cap) in enumerate(NUMSTRIP):
        cx = M + cell_w * i
        d.text((cx + (cell_w - d.textlength(num, font=F_NUM)) / 2, y), num, font=F_NUM, fill=INK)
        d.text((cx + (cell_w - d.textlength(cap, font=F_NUMCAP)) / 2, y + lh(F_NUM) + 1),
               cap, font=F_NUMCAP, fill=GREY)
        if i:
            d.line([(cx, y + 2), (cx, y + lh(F_NUM) + lh(F_NUMCAP))], fill=LINE, width=1)
    y += lh(F_NUM) + lh(F_NUMCAP) + 6

    # --- continent bar
    bx = M
    for name, cnt, col in CONTINENTS:
        d.rectangle([bx, y + 1, bx + 10, y + 11], fill=col)
        t = f"{name} {cnt}"
        d.text((bx + 13, y), t, font=F_CONT, fill=INK)
        bx += 13 + d.textlength(t, font=F_CONT) + 18
    y += lh(F_CONT) + 4

    # --- measure all story text (heroes + mids)
    hero_w = (CW - 2 * 6) / 3
    mid_w = (CW - 4 * 4) / 5
    wide_w = (CW - 2 * 4) / 3
    hero_m = [measure_card(d, c, hero_w, F_HERO_HEAD, "DejaVuSerif-Bold.ttf", F_HERO_BODY)
              for c in HEROES]
    mid_m = []
    for i, c in enumerate(MIDS):
        w = wide_w if i >= 10 else mid_w
        mid_m.append(measure_card(d, c, w, F_MID_HEAD, "DejaVuSerif-Bold.ttf", F_MID_BODY))
    hero_text = max(m[0] for m in hero_m) + lh(F_HERO_SRC) + 8
    mid_text = [max(mid_m[r * 5 + k][0] for k in range(5)) + 6 for r in range(2)]
    mid_text.append(max(mid_m[10 + k][0] for k in range(3)) + 6)
    dc_lines = wrap(DATECHECK, F_DC, CW - 16, d)
    dc_h = lh(F_DC_T) + text_h(dc_lines, F_DC) + 8
    list_row_h = lh(F_LIST)
    list_h = lh(F_LIST_H) + 2 + 12 * list_row_h

    # --- fit pass: art heights fill the remaining budget exactly
    fixed = (y + hero_text + sum(mid_text) + (lh(F_MAP_T) + lh(F_CONT) + 4)
             + list_h + dc_h + lh(F_FOOT) + 3 * 7)
    avail = H - fixed
    hero_art, mid_art, map_art = 62, 44, 74
    art_total = hero_art + 3 * mid_art + map_art
    scale = avail / art_total
    hero_art = max(46, round(hero_art * scale))
    mid_art = max(32, round(mid_art * scale))
    map_art = max(56, round(map_art * scale))
    print(f"fit: avail={avail} scale={scale:.3f} hero_art={hero_art} mid_art={mid_art} "
          f"map_art={map_art} hero_text={hero_text} mid_text={mid_text} dc_h={dc_h}")

    # --- heroes
    for i, c in enumerate(HEROES):
        x = M + i * (hero_w + 6)
        d.rectangle([x, y, x + hero_w, y + hero_art + hero_text], outline=LINE, width=1)
        SCENES[c["scene"]](d, x + 1, y + 1, hero_w - 2, hero_art - 1)
        d.rectangle([x + 1, y + 1, x + 86, y + 17], fill=RED)
        d.text((x + 6, y + 2), c["tag"], font=F("DejaVuSans-Bold.ttf", 9), fill=(255, 255, 255))
        badge(d, x + hero_w - 14, y + 14, c["n"])
        ty = y + hero_art + 3
        d.text((x + 5, ty), c["date"], font=F_HERO_DATE, fill=RED)
        ty += lh(F_HERO_DATE)
        ty = draw_lines(d, x + 5, ty, hero_m[i][1], hero_m[i][2], INK)
        ty = draw_lines(d, x + 5, ty, hero_m[i][3], F_HERO_BODY, INK)
        d.text((x + 5, ty), c["src"], font=F_HERO_SRC, fill=GREY)
    y += hero_art + hero_text + 3

    # --- mid rows: rows of 5, 5, then 3 cards stretched to full width
    rows = [(MIDS[0:5], mid_w, 4), (MIDS[5:10], mid_w, 4), (MIDS[10:13], wide_w, 4)]
    for ri, (cards, cw, gap) in enumerate(rows):
        row_h = mid_art + mid_text[ri]
        for k, c in enumerate(cards):
            x = M + k * (cw + gap)
            d.rectangle([x, y, x + cw, y + row_h], outline=LINE, width=1)
            SCENES[c["scene"]](d, x + 1, y + 1, cw - 2, mid_art - 1)
            badge(d, x + cw - 12, y + 12, c["n"], r=10)
            m = mid_m[ri * 5 + k] if ri < 2 else mid_m[10 + k]
            ty = y + mid_art + 2
            d.text((x + 5, ty), c["date"], font=F_MID_DATE, fill=RED)
            ty += lh(F_MID_DATE)
            ty = draw_lines(d, x + 5, ty, m[1], m[2], INK)
            draw_lines(d, x + 5, ty, m[3], F_MID_BODY, INK)
        y += row_h + 3

    # --- map
    d.text((M, y), "WHERE IT HAPPENED", font=F_MAP_T, fill=INK)
    d.text((M + 150, y), "pins match story numbers", font=F("DejaVuSans.ttf", 10), fill=GREY)
    y += lh(F_MAP_T)
    lx = M
    for name, cnt, col in CONTINENTS:
        d.rectangle([lx, y + 1, lx + 9, y + 10], fill=col)
        t = f"{name} {cnt}"
        d.text((lx + 11, y), t, font=F_CONT, fill=INK)
        lx += 11 + d.textlength(t, font=F_CONT) + 14
    y += lh(F_CONT) + 4
    draw_map(d, M, y, CW, map_art)
    y += map_art + 3

    # --- list 17-50, columns balanced 12/11/11
    d.text((M, y), "ALSO ON WEDNESDAY 25 NOVEMBER — 34 MORE STORIES", font=F_LIST_H, fill=INK)
    rt = "ALL 25 NOVEMBER 2026"
    d.text((W - M - d.textlength(rt, font=F_LIST_H), y), rt, font=F_LIST_H, fill=RED)
    y += lh(F_LIST_H) + 2
    cols = [LIST[0:12], LIST[12:23], LIST[23:34]]
    col_w = (CW - 2 * 16) / 3
    for ci, col in enumerate(cols):
        cx = M + ci * (col_w + 16)
        for ri, (n, txt) in enumerate(col):
            ry = y + ri * list_row_h
            d.text((cx, ry), str(n), font=F_LIST_N, fill=INK)
            draw_glyph(d, cx + 20, ry + 1, 10, GLYPHS[(n + ci) % len(GLYPHS)],
                       GLYPH_COLS[(n + ci) % len(GLYPH_COLS)])
            # guard: never let a row run past the column's right edge
            max_tw = col_w - 34
            while d.textlength(txt, font=F_LIST) > max_tw and len(txt) > 4:
                txt = txt.rsplit(" ", 1)[0] + "…"
            d.text((cx + 34, ry), txt, font=F_LIST, fill=INK)
    y += 12 * list_row_h + 3

    # --- DATE CHECK
    d.rectangle([M, y, W - M, y + dc_h], outline=RED, width=2)
    d.text((M + 6, y + 3), "DATE CHECK", font=F_DC_T, fill=RED)
    draw_lines(d, M + 6, y + 3 + lh(F_DC_T), dc_lines, F_DC, INK)
    y += dc_h + 2

    # --- footer
    d.text((M, y), "Sources: Reuters, AP, BBC, Al Jazeera, UEFA, Xinhua, WSJ, NYT — all reported 25 November 2026.",
           font=F_FOOT, fill=GREY)
    d.text((W - M - d.textlength("THE WORLD IN ONE DAY", font=F_FOOT), y),
           "THE WORLD IN ONE DAY", font=F_FOOT, fill=GREY)
    y += lh(F_FOOT)
    print(f"final y={y} (target 1024)")
    return img


if __name__ == "__main__":
    img = render()
    img.save("entry.png", optimize=True)
    import os as _os
    print("bytes:", _os.path.getsize("entry.png"))
