"""
Graphics layer for the GTA 6 TikTok edit, rendered with transparency so it
sits on top of REAL gameplay footage (assemble.py does the compositing).

    python video/overlay.py                 # out/overlay_prores4444.mov (alpha)
    python video/overlay.py --still 12.0    # PNG of one frame (over a neutral grey, for checking)

Contains: circular pink/orange counter, title pill + progress dots, big
outlined subtitles, small animated indicator icons, flash / light-leak
accents. There is NO background imagery in this file by design.
"""
import argparse
import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from timeline import SEGMENTS, FPS, W, H, DURATION, FX, PILL_TEXT, TITLE_LABEL  # noqa: E402
import timeline as _TL  # noqa: E402
STYLE = getattr(_TL, "STYLE", "p2")
TOTAL = getattr(_TL, "COUNTER_TOTAL", 10)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(HERE, "assets", "fonts")
F_ANTON = os.path.join(FONT_DIR, "Anton.woff")
F_MONT = os.path.join(FONT_DIR, "Montserrat-800.woff")

PINK = np.array([255, 46, 136], float)
ORANGE = np.array([255, 154, 31], float)
GTA_GREEN = np.array([114, 214, 104], float)
GTA_PURPLE = np.array([150, 70, 255], float)
if STYLE == "gta":                       # GTA-inspired palette: purple -> green
    PINK, ORANGE = GTA_PURPLE, GTA_GREEN
YELLOW = (255, 225, 77)


# =================================================================== easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def back_out(x, s=1.9):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def elastic_out(x):
    x = clamp(x)
    if x in (0, 1):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1


@lru_cache(None)
def font(path, size):
    return ImageFont.truetype(path, size)


def seg_at(t):
    for s in SEGMENTS:
        if s["start"] <= t < s["end"]:
            return s
    return SEGMENTS[-1]



# =================================================================== overlay sprites
def gradient_img(w, h, c1=PINK, c2=ORANGE, horizontal=False):
    if horizontal:
        k = np.linspace(0, 1, w)[None, :, None]
    else:
        k = np.linspace(0, 1, h)[:, None, None]
    arr = c1 * (1 - k) + c2 * k
    arr = np.broadcast_to(arr, (h, w, 3))
    return Image.fromarray(arr.astype(np.uint8), "RGB")



def star_points(cx, cy, r1, r2, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


@lru_cache(None)
def icon_sprite(name):
    S = 240
    im = Image.new("RGBA", (S * 2, S * 2), (0, 0, 0, 0))
    c = S
    d = ImageDraw.Draw(im)
    if name.startswith("stars"):
        return None
    # badge: glow + gradient ring + dark disc
    glow = Image.new("L", im.size, 0)
    ImageDraw.Draw(glow).ellipse([c - 200, c - 200, c + 200, c + 200], fill=200)
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    gl = Image.new("RGBA", im.size, (255, 80, 110, 0))
    gl.putalpha(glow.point(lambda v: int(v * 0.55)))
    im = Image.alpha_composite(im, gl)
    ring = Image.new("L", im.size, 0)
    ImageDraw.Draw(ring).ellipse([c - 190, c - 190, c + 190, c + 190], fill=255)
    im.paste(gradient_img(S * 2, S * 2), (0, 0), ring)
    d = ImageDraw.Draw(im)
    d.ellipse([c - 172, c - 172, c + 172, c + 172], fill=(18, 8, 28, 255))
    W_, P, O, Y, R, G = (255, 255, 255), (255, 46, 136), (255, 154, 31), YELLOW, (255, 50, 60), (90, 220, 110)
    if name == "controller":
        d.rounded_rectangle([c - 120, c - 60, c + 120, c + 60], 50, fill=W_)
        d.ellipse([c - 150, c - 20, c - 50, c + 100], fill=W_)
        d.ellipse([c + 50, c - 20, c + 150, c + 100], fill=W_)
        d.rectangle([c - 95, c - 8, c - 45, c + 8], fill=(18, 8, 28))
        d.rectangle([c - 78, c - 25, c - 62, c + 25], fill=(18, 8, 28))
        for dx, dy, col in ((60, -18, P), (90, 8, O), (60, 34, Y), (30, 8, (80, 200, 255))):
            d.ellipse([c + dx - 12, c + dy - 12, c + dx + 12, c + dy + 12], fill=col)
    elif name == "duo":
        for dx, col in ((-55, P), (55, O)):
            d.ellipse([c + dx - 38, c - 100, c + dx + 38, c - 24], fill=col)
            d.rounded_rectangle([c + dx - 60, c - 14, c + dx + 60, c + 110], 40, fill=col)
    elif name == "arrow_split":
        d.line([c, c + 110, c, c + 10], fill=W_, width=26)
        d.line([c, c + 20, c - 80, c - 70], fill=P, width=26)
        d.line([c, c + 20, c + 80, c - 70], fill=O, width=26)
        d.polygon([(c - 120, c - 110), (c - 40, c - 100), (c - 110, c - 30)], fill=P)
        d.polygon([(c + 120, c - 110), (c + 40, c - 100), (c + 110, c - 30)], fill=O)
    elif name == "eye":
        d.ellipse([c - 130, c - 70, c + 130, c + 70], fill=W_)
        d.ellipse([c - 55, c - 55, c + 55, c + 55], fill=P)
        d.ellipse([c - 24, c - 24, c + 24, c + 24], fill=(10, 5, 15))
        d.ellipse([c + 4, c - 30, c + 22, c - 12], fill=W_)
    elif name == "alarm":
        d.pieslice([c - 80, c - 90, c + 80, c + 70], 180, 360, fill=R)
        d.rectangle([c - 80, c - 10, c + 80, c + 40], fill=R)
        d.rounded_rectangle([c - 110, c + 40, c + 110, c + 80], 10, fill=W_)
        for a in (-150, -120, -90, -60, -30):
            r = math.radians(a)
            d.line([c + math.cos(r) * 110, c - 10 + math.sin(r) * 110, c + math.cos(r) * 150, c - 10 + math.sin(r) * 150], fill=Y, width=14)
    elif name == "scan":
        L = 50
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x0, y0 = c + sx * 110, c + sy * 110
            d.line([x0, y0, x0 - sx * L, y0], fill=W_, width=14)
            d.line([x0, y0, x0, y0 - sy * L], fill=W_, width=14)
        d.ellipse([c - 45, c - 75, c + 45, c + 15], fill=P)
        d.pieslice([c - 80, c + 10, c + 80, c + 150], 180, 360, fill=P)
        d.rectangle([c - 120, c - 6, c + 120, c + 6], fill=O)
    elif name == "flame":
        d.polygon([(c, c - 140), (c + 90, c - 10), (c + 80, c + 80), (c, c + 120), (c - 80, c + 80), (c - 90, c - 10)], fill=O)
        d.ellipse([c - 92, c - 30, c + 92, c + 122], fill=O)
        d.polygon([(c, c - 60), (c + 50, c + 30), (c, c + 110), (c - 50, c + 30)], fill=Y)
        d.ellipse([c - 50, c + 10, c + 50, c + 110], fill=Y)
    elif name == "slots":
        for i, (dx, dy) in enumerate(((-65, -65), (65, -65), (-65, 65), (65, 65))):
            col = P if i < 2 else O
            d.rounded_rectangle([c + dx - 55, c + dy - 55, c + dx + 55, c + dy + 55], 16, fill=col)
            if i < 2:   # pistol
                d.rectangle([c + dx - 35, c + dy - 25, c + dx + 35, c + dy - 5], fill=W_)
                d.polygon([(c + dx - 30, c + dy - 5), (c + dx - 5, c + dy - 5), (c + dx - 12, c + dy + 32), (c + dx - 36, c + dy + 32)], fill=W_)
            else:       # rifle
                d.rectangle([c + dx - 45, c + dy - 12, c + dx + 45, c + dy + 2], fill=W_)
                d.polygon([(c + dx - 45, c + dy - 12), (c + dx - 25, c + dy - 12), (c + dx - 30, c + dy + 22), (c + dx - 48, c + dy + 22)], fill=W_)
                d.rectangle([c + dx + 2, c + dy + 2, c + dx + 12, c + dy + 26], fill=W_)
    elif name == "cash":
        for k in range(3):
            y = c + 40 - k * 40
            d.rounded_rectangle([c - 130, y - 40, c + 130, y + 40], 10, fill=(60, 170, 80), outline=(20, 90, 40), width=5)
        d.ellipse([c - 40, c - 120, c + 40, c - 40], fill=(30, 110, 50))
        d.text((c, c - 80), "$", font=font(F_ANTON, 70), fill=W_, anchor="mm")
    elif name == "skull":
        d.ellipse([c - 100, c - 120, c + 100, c + 60], fill=W_)
        d.rounded_rectangle([c - 60, c + 20, c + 60, c + 110], 14, fill=W_)
        d.ellipse([c - 70, c - 50, c - 15, c + 10], fill=(18, 8, 28))
        d.ellipse([c + 15, c - 50, c + 70, c + 10], fill=(18, 8, 28))
        d.polygon([(c, c + 20), (c - 15, c + 50), (c + 15, c + 50)], fill=(18, 8, 28))
        for dx in (-30, 0, 30):
            d.line([c + dx, c + 70, c + dx, c + 110], fill=(18, 8, 28), width=8)
    elif name == "pin":
        d.ellipse([c - 85, c - 140, c + 85, c + 30], fill=P)
        d.polygon([(c - 75, c - 30), (c + 75, c - 30), (c, c + 130)], fill=P)
        d.ellipse([c - 35, c - 90, c + 35, c - 20], fill=W_)
    elif name == "wifi_off":
        for r in (130, 90, 50):
            d.arc([c - r, c - r + 40, c + r, c + r + 40], 220, 320, fill=W_, width=22)
        d.ellipse([c - 18, c + 22, c + 18, c + 58], fill=W_)
        d.line([c - 120, c - 110, c + 120, c + 120], fill=R, width=26)
    elif name == "clock":
        d.ellipse([c - 130, c - 130, c + 130, c + 130], outline=W_, width=20)
        d.line([c, c, c, c - 85], fill=W_, width=18)
        d.line([c, c, c + 60, c + 30], fill=O, width=18)
        d.ellipse([c - 16, c - 16, c + 16, c + 16], fill=P)
    elif name == "trophy":
        d.pieslice([c - 100, c - 180, c + 100, c + 40], 0, 180, fill=Y)
        d.rectangle([c - 100, c - 120, c + 100, c - 70], fill=Y)
        d.arc([c - 150, c - 110, c - 50, c - 10], 90, 270, fill=Y, width=18)
        d.arc([c + 50, c - 110, c + 150, c - 10], 270, 90, fill=Y, width=18)
        d.rectangle([c - 18, c + 30, c + 18, c + 90], fill=O)
        d.rounded_rectangle([c - 80, c + 90, c + 80, c + 125], 8, fill=O)
        d.polygon(star_points(c, c - 70, 38, 16), fill=W_)
    elif name == "comment":
        d.rounded_rectangle([c - 140, c - 100, c + 140, c + 70], 50, fill=W_)
        d.polygon([(c - 70, c + 60), (c - 100, c + 130), (c - 10, c + 65)], fill=W_)
        for dx, col in ((-70, P), (0, O), (70, Y)):
            d.ellipse([c + dx - 20, c - 35, c + dx + 20, c + 5], fill=col)
    elif name == "share":
        d.polygon([(c + 140, c - 10), (c + 10, c - 120), (c + 10, c - 60), (c - 130, c - 30), (c - 140, c + 110),
                   (c - 60, c + 30), (c + 10, c + 40), (c + 10, c + 100)], fill=W_)
    elif name == "car":
        d.rounded_rectangle([c - 150, c - 10, c + 150, c + 60], 24, fill=W_)
        d.polygon([(c - 95, c - 10), (c - 55, c - 75), (c + 55, c - 75), (c + 100, c - 10)], fill=W_)
        d.polygon([(c - 70, c - 18), (c - 42, c - 62), (c - 5, c - 62), (c - 5, c - 18)], fill=(18, 8, 28))
        d.polygon([(c + 8, c - 18), (c + 8, c - 62), (c + 45, c - 62), (c + 75, c - 18)], fill=(18, 8, 28))
        for dx in (-85, 85):
            d.ellipse([c + dx - 34, c + 30, c + dx + 34, c + 98], fill=(18, 8, 28))
            d.ellipse([c + dx - 20, c + 44, c + dx + 20, c + 84], fill=O)
        d.rectangle([c + 128, c + 5, c + 150, c + 22], fill=Y)
        d.rectangle([c - 150, c + 5, c - 132, c + 22], fill=R)
    elif name == "heart":
        d.ellipse([c - 120, c - 100, c + 5, c + 25], fill=P)
        d.ellipse([c - 5, c - 100, c + 120, c + 25], fill=P)
        d.polygon([(c - 116, c - 20), (c + 116, c - 20), (c, c + 125)], fill=P)
        d.line([(c + 5, c - 75), (c - 22, c - 25), (c + 18, c + 10), (c - 10, c + 60)], fill=(18, 8, 28), width=14)
    elif name == "gun":
        d.rectangle([c - 130, c - 60, c + 120, c - 15], fill=W_)
        d.rectangle([c + 95, c - 75, c + 112, c - 60], fill=W_)
        d.polygon([(c - 120, c - 15), (c - 40, c - 15), (c - 62, c + 110), (c - 135, c + 110)], fill=W_)
        d.arc([c - 50, c - 30, c + 10, c + 40], 0, 180, fill=W_, width=12)
        d.rectangle([c - 100, c - 52, c + 100, c - 44], fill=O)
    elif name == "fuel":
        d.rounded_rectangle([c - 90, c - 120, c + 40, c + 125], 18, fill=W_)
        d.rectangle([c - 65, c - 95, c + 15, c - 30], fill=(18, 8, 28))
        d.line([(c + 40, c - 60), (c + 90, c - 30), (c + 90, c + 70), (c + 70, c + 90)], fill=W_, width=16)
        d.rectangle([c - 110, c + 110, c + 60, c + 130], fill=O)
    elif name == "bolt":
        d.polygon([(c + 30, c - 140), (c - 80, c + 15), (c - 5, c + 15), (c - 35, c + 140), (c + 85, c - 25), (c + 10, c - 25)], fill=Y)
    elif name == "lock":
        d.arc([c - 70, c - 140, c + 70, c + 10], 180, 360, fill=W_, width=26)
        d.rectangle([c - 70, c - 70, c - 44, c - 10], fill=W_)
        d.rectangle([c + 44, c - 70, c + 70, c - 10], fill=W_)
        d.rounded_rectangle([c - 105, c - 20, c + 105, c + 125], 22, fill=W_)
        d.ellipse([c - 20, c + 25, c + 20, c + 65], fill=(18, 8, 28))
        d.rectangle([c - 8, c + 50, c + 8, c + 95], fill=(18, 8, 28))
    elif name == "moon":
        d.ellipse([c - 120, c - 120, c + 120, c + 120], fill=Y)
        d.ellipse([c - 60, c - 150, c + 160, c + 70], fill=(18, 8, 28))
        for sx, sy in ((70, 60), (110, -10)):
            d.polygon(star_points(c + sx, c + sy, 22, 9), fill=W_)
    elif name == "dumbbell":
        d.rectangle([c - 80, c - 14, c + 80, c + 14], fill=W_)
        for sx in (-1, 1):
            d.rounded_rectangle([c + sx * 80 - 18, c - 80, c + sx * 80 + 18, c + 80], 8, fill=W_)
            d.rounded_rectangle([c + sx * 118 - 16, c - 55, c + sx * 118 + 16, c + 55], 8, fill=O)
    elif name == "door":
        d.rectangle([c - 85, c - 140, c + 85, c + 135], fill=W_)
        d.rectangle([c - 65, c - 120, c + 65, c + 135], fill=(18, 8, 28))
        d.polygon([(c - 65, c - 120), (c + 40, c - 95), (c + 40, c + 150), (c - 65, c + 135)], fill=P)
        d.ellipse([c + 12, c + 5, c + 30, c + 23], fill=W_)
    elif name == "paw":
        d.ellipse([c - 75, c - 5, c + 75, c + 120], fill=W_)
        for sx, sy, r in ((-105, -40, 34), (-45, -110, 36), (45, -110, 36), (105, -40, 34)):
            d.ellipse([c + sx - r, c + sy - r, c + sx + r, c + sy + r], fill=W_)
    elif name == "bag":
        d.rounded_rectangle([c - 130, c - 50, c + 130, c + 90], 50, fill=O)
        d.rectangle([c - 130, c - 5, c + 130, c + 10], fill=(150, 70, 10))
        d.arc([c - 60, c - 120, c + 60, c - 10], 180, 360, fill=W_, width=16)
        d.rectangle([c - 30, c + 25, c + 30, c + 55], fill=Y)
    elif name == "coke":
        d.polygon([(c - 100, c - 70), (c + 100, c - 70), (c + 115, c + 110), (c - 115, c + 110)], fill=(235, 235, 240))
        d.rectangle([c - 100, c - 100, c + 100, c - 70], fill=(180, 180, 195))
        for dx, dy in ((-40, 20), (25, 40), (-5, 75), (55, 85), (-65, 80)):
            d.ellipse([c + dx - 12, c + dy - 12, c + dx + 12, c + dy + 12], fill=W_)
        d.line([(c - 100, c - 70), (c + 100, c - 70)], fill=P, width=8)
    return im.resize((S, S), Image.LANCZOS)


@lru_cache(None)
def star_sprite(filled=True, red=False):
    S = 220
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = star_points(S / 2, S / 2 + 6, 92, 40)
    g = Image.new("L", (S, S), 0)
    ImageDraw.Draw(g).polygon(pts, fill=255)
    g = g.filter(ImageFilter.GaussianBlur(10))
    glow = Image.new("RGBA", (S, S), (255, 60, 60, 0) if red else (255, 200, 80, 0))
    glow.putalpha(g.point(lambda v: int(v * 0.8)))
    im = Image.alpha_composite(im, glow)
    d = ImageDraw.Draw(im)
    if filled:
        d.polygon(pts, fill=(255, 70, 70) if red else (255, 255, 255), outline=(0, 0, 0), width=8)
    else:
        d.polygon(pts, fill=(0, 0, 0, 120), outline=(255, 255, 255), width=8)
    return im.resize((110, 110), Image.LANCZOS)


# ring geometry
RC = 260                      # ring patch size
RYY, RXX = np.mgrid[0:RC, 0:RC].astype(np.float32) - RC / 2
RR = np.sqrt(RXX ** 2 + RYY ** 2)
RANG = (np.degrees(np.arctan2(RXX, -RYY)) + 360) % 360   # 0 at top, clockwise


def counter_sprite(n, progress, t, pop):
    """Circular counter: glowing pink->orange conic ring, n/10 inside."""
    r_out, r_in = 100, 84
    ring = ((RR < r_out) & (RR > r_in)).astype(np.float32)
    aa = np.clip(r_out - RR, 0, 1) * np.clip(RR - r_in, 0, 1)
    ring = np.maximum(ring * 0, aa)
    arc = ring * (RANG <= progress * 360)
    base = ring * 0.22
    k = ((RANG + t * 120) % 360) / 360
    k = 0.5 - 0.5 * np.cos(k * 2 * np.pi)
    col = PINK * (1 - k[..., None]) + ORANGE * k[..., None]
    rgba = np.zeros((RC, RC, 4), np.float32)
    rgba[..., :3] = col * arc[..., None] + 255 * base[..., None] * (1 - arc[..., None])
    rgba[..., 3] = np.clip(arc + base, 0, 1) * 255
    # glow of the arc
    a_img = Image.fromarray((arc * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12))
    glow = np.asarray(a_img, np.float32) / 255
    gl = np.zeros_like(rgba)
    gl[..., :3] = col
    gl[..., 3] = np.clip(glow * 1.6, 0, 1) * 255
    disc = (RR < r_in - 2).astype(np.float32)
    dk = np.zeros_like(rgba)
    dk[..., :3] = np.array([14, 6, 24])
    dk[..., 3] = disc * 190
    im = Image.alpha_composite(Image.fromarray(gl.astype(np.uint8), "RGBA"), Image.fromarray(dk.astype(np.uint8), "RGBA"))
    im = Image.alpha_composite(im, Image.fromarray(rgba.astype(np.uint8), "RGBA"))
    d = ImageDraw.Draw(im)
    # spark at arc head
    if 0 < progress < 1.0001:
        a = math.radians(progress * 360 - 90)
        hx, hy = RC / 2 + math.cos(a) * 92, RC / 2 + math.sin(a) * 92
        d.ellipse([hx - 9, hy - 9, hx + 9, hy + 9], fill=(255, 255, 230))
    cx = RC / 2
    if False:   # title shows 0/10 (no words on screen)
        d.text((cx, cx - 14), "10", font=font(F_ANTON, 84), fill="white", anchor="mm", stroke_width=4, stroke_fill="black")
        d.text((cx, cx + 46), TITLE_LABEL, font=font(F_MONT, 20), fill=(255, 190, 120), anchor="mm")
    else:
        big = font(F_ANTON, 92 if n < 10 else 80)
        small = font(F_ANTON, 40)
        s1, s2 = str(n), f"/{TOTAL}"
        w1, w2 = big.getlength(s1), small.getlength(s2)
        x0 = cx - (w1 + w2) / 2
        d.text((x0, cx + 30), s1, font=big, fill="white", anchor="ls", stroke_width=4, stroke_fill="black")
        d.text((x0 + w1 + 2, cx + 30), s2, font=small, fill=(255, 180, 110), anchor="ls", stroke_width=3, stroke_fill="black")
    if pop != 1.0:
        sz = max(2, int(RC * pop))
        im = im.resize((sz, sz), Image.BILINEAR)
    return im


@lru_cache(None)
def pill_sprite():
    text = PILL_TEXT
    f = font(F_MONT, 30)
    w = int(f.getlength(text)) + 70
    h = 62
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w + 7, h + 7], 34, fill=255)
    im.paste(gradient_img(w + 8, h + 8, horizontal=True), (0, 0), m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, w + 3, h + 3], 30, fill=(12, 6, 20, 215))
    d.text(((w + 8) / 2, (h + 8) / 2 + 1), text, font=f, fill="white", anchor="mm")
    return im


@lru_cache(None)
def edge_glow(side):
    g = np.zeros((H, 260), np.float32)
    g[:] = np.linspace(1, 0, 260)[None, :] ** 2
    if side == "r":
        g = g[:, ::-1]
    col = (255, 30, 50) if side == "l" else (40, 80, 255)
    im = Image.new("RGBA", (260, H), col + (0,))
    im.putalpha(Image.fromarray((g * 200).astype(np.uint8)))
    return im


def paste_center(canvas, sprite, cx, cy, alpha=1.0):
    if sprite is None:
        return
    if alpha < 1:
        sprite = sprite.copy()
        a = sprite.getchannel("A").point(lambda v: int(v * alpha))
        sprite.putalpha(a)
    canvas.alpha_composite(sprite, (int(cx - sprite.width / 2), int(cy - sprite.height / 2))) if (
        0 <= int(cx - sprite.width / 2) and 0 <= int(cy - sprite.height / 2)
        and int(cx + sprite.width / 2) <= canvas.width and int(cy + sprite.height / 2) <= canvas.height
    ) else canvas.paste(sprite, (int(cx - sprite.width / 2), int(cy - sprite.height / 2)), sprite)


def scaled(sprite, s, rot=0.0):
    if sprite is None:
        return None
    if abs(s - 1) < 1e-3 and abs(rot) < 0.05:
        return sprite
    w, h = max(2, int(sprite.width * s)), max(2, int(sprite.height * s))
    out = sprite.resize((w, h), Image.BILINEAR)
    if abs(rot) >= 0.05:
        out = out.rotate(rot, Image.BILINEAR, expand=True)
    return out



def draw_minimap(canvas, t):
    S = 230
    r = 98
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) - S / 2
    rr = np.sqrt(xx ** 2 + yy ** 2)
    ang = (np.degrees(np.arctan2(xx, -yy)) - t * 140) % 360
    disc = (rr < r)
    rgba = np.zeros((S, S, 4), np.float32)
    rgba[..., :3] = np.array([10, 14, 30])
    rgba[..., 3] = disc * 170
    sweep = disc * np.clip(1 - ang / 70, 0, 1) * 0.5
    rgba[..., :3] += sweep[..., None] * np.array([255, 120, 160])
    rgba[..., 3] = np.maximum(rgba[..., 3], sweep * 255)
    im = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    c = S / 2
    off = (t * 18) % 60
    for k in range(-3, 4):   # moving road grid
        y = c + k * 60 + off
        d.line([c - r, y, c + r, y], fill=(90, 90, 120, 160), width=4)
    d.line([c - 30, c - r, c + 10, c + r], fill=(110, 110, 140, 180), width=7)
    rng = np.random.default_rng(3)
    for i in range(5):
        a = rng.uniform(0, 6.28) + t * 0.2
        rr_ = rng.uniform(30, 85)
        bx, by = c + math.cos(a) * rr_, c + math.sin(a) * rr_
        col = (255, 60, 60, 255) if i % 2 else (60, 140, 255, 255)
        if (t * 3 + i) % 2 < 1.4:
            d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=col)
    d.polygon([(c, c - 16), (c + 12, c + 12), (c, c + 5), (c - 12, c + 12)], fill="white")
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([c - r, c - r, c + r, c + r], fill=255)
    im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(mask))))
    d = ImageDraw.Draw(im)
    d.ellipse([c - r, c - r, c + r, c + r], outline=(255, 255, 255, 200), width=4)
    im = im.resize((120, 120), Image.LANCZOS)
    canvas.alpha_composite(im, (36, 1500))
    dd = ImageDraw.Draw(canvas)
    dd.rounded_rectangle([40, 1630, 156, 1636], 6, fill=(0, 0, 0, 150))
    dd.rounded_rectangle([40, 1630, 40 + 116 * (0.8 + 0.15 * math.sin(t * 0.7)), 1636], 6, fill=(90, 220, 110, 230))
    dd.rounded_rectangle([40, 1642, 156, 1648], 6, fill=(0, 0, 0, 150))
    dd.rounded_rectangle([40, 1642, 40 + 116 * 0.6, 1648], 6, fill=(80, 170, 255, 230))



# =================================================================== decorative FX layer
WHITE = (255, 255, 255)


def fx_alpha(age, dur, fin=0.12, fout=0.2):
    return clamp(age / fin) * clamp((dur - age) / fout)


@lru_cache(None)
def glow_dot(r, col):
    S = r * 6
    im = Image.new("RGBA", (S, S), col + (0,))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(r * 0.9))
    core = Image.new("L", (S, S), 0)
    ImageDraw.Draw(core).ellipse([S / 2 - r * 0.35, S / 2 - r * 0.35, S / 2 + r * 0.35, S / 2 + r * 0.35], fill=255)
    m = Image.fromarray(np.maximum(np.asarray(m), np.asarray(core.filter(ImageFilter.GaussianBlur(1)))))
    im.putalpha(m)
    return im


_RNG = np.random.default_rng(11)
AMBIENT = [dict(x=float(_RNG.choice([_RNG.uniform(10, 120), _RNG.uniform(W - 120, W - 10)])), y=_RNG.uniform(0, H), v=_RNG.uniform(25, 70), r=int(_RNG.choice([3, 4, 5, 7])),
                ph=_RNG.uniform(0, 6.28), col=[(255, 46, 136), (255, 154, 31), (255, 220, 180)][i % 3]) for i in range(34)]


def draw_ambient(canvas, t):
    for p in AMBIENT:
        y = (p["y"] - t * p["v"]) % (H + 100) - 50
        x = p["x"] + 10 * math.sin(t * 0.8 + p["ph"])
        a = 0.2 + 0.2 * math.sin(t * 2.2 + p["ph"])
        paste_center(canvas, glow_dot(p["r"], p["col"]), x, y, max(0.05, a))


def draw_burst(canvas, cx, cy, age, n=26, seed=0, dist=330, dur=0.9, small=False):
    if not 0 <= age < dur:
        return
    rng = np.random.default_rng(seed)
    k = ease_out(age / dur)
    for i in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        dd = dist * rng.uniform(0.4, 1.0) * k
        col = [(255, 46, 136), (255, 154, 31), (255, 230, 120)][i % 3]
        paste_center(canvas, glow_dot(int(rng.choice([2, 3, 4] if small else [4, 6, 8])), col), cx + math.cos(ang) * dd, cy + math.sin(ang) * dd,
                     max(0.02, 1 - age / dur))


@lru_cache(None)
def ring_sprite(r, width=10):
    S = r * 2 + 80
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([40, 40, S - 40, S - 40], outline=255, width=width)
    g = m.filter(ImageFilter.GaussianBlur(14))
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    grad = gradient_img(S, S, PINK, ORANGE, horizontal=True)
    glow = Image.new("RGBA", (S, S), (255, 90, 110, 0))
    glow.putalpha(g)
    im = Image.alpha_composite(im, glow)
    im.paste(grad, (0, 0), m)
    return im


def draw_ping(canvas, x, y, age, dur, base=34):
    a = fx_alpha(age, dur) * 0.8
    for k in range(3):
        ph = (age * 1.2 + k / 3) % 1
        paste_center(canvas, scaled(ring_sprite(base, 4), 0.4 + ph * 1.1), x, y, a * (1 - ph))
    paste_center(canvas, scaled(ring_sprite(base // 2, 4), 1 + 0.06 * math.sin(age * 9)), x, y, a)


def draw_stars(canvas, e, age):
    a = fx_alpha(age, e["dur"])
    n = e["n"]
    size = 30
    x0 = W - 40 - 6 * size * 0.92 + size / 2
    flash = math.sin(age * 2 * math.pi * 4) > 0
    lose = e.get("lose")
    for i in range(6):
        on = i < n and age >= i * 0.09
        if lose and age > e["dur"] - 0.7:
            on = on and (i < n - int((age - (e["dur"] - 0.7)) / 0.12))
        sp = star_sprite(on, bool(on and flash))
        pop = back_out(clamp((age - i * 0.09) / 0.25)) if on else 1.0
        paste_center(canvas, scaled(sp, max(0.05, pop * 0.27)), x0 + i * size * 0.92, 112, a)



ICON_POS = [(1018, 860), (62, 860)]


def draw_icon(canvas, e, age, slot):
    if STYLE in ("p3", "gta"):
        s = back_out(age / 0.5) * clamp((e["dur"] - age) / 0.22)
        if s <= 0.01:
            return
        cx = 950 + 4 * math.sin(age * 1.7)
        cy = 715 + 6 * math.sin(age * 2.4)
        ph = (age * 0.9) % 1
        paste_center(canvas, scaled(ring_sprite(70, 5), 0.9 + 0.5 * ph), cx, cy, 0.55 * (1 - ph) * min(1, s))
        if age < 0.5:
            draw_burst(canvas, cx, cy, age, n=12, seed=int(e["t"] * 10), dist=130, dur=0.5, small=True)
        isz = 0.68 if STYLE == "gta" else 0.52
        paste_center(canvas, scaled(icon_sprite(e["name"]), isz * s, 4 * math.sin(age * 3)), cx, cy, min(1, s))
        return
    s = back_out(age / 0.45) * clamp((e["dur"] - age) / 0.2)
    if s <= 0.01:
        return
    bx, by = ICON_POS[slot % 2]
    cx = bx + 8 * math.sin(age * 1.7 + slot)
    cx = bx + 3 * math.sin(age * 1.7 + slot)
    cy = by - 18 * ease_out(age / e["dur"]) + 4 * math.sin(age * 2.6)     # slow float upwards
    ph = (age * 0.9) % 1
    paste_center(canvas, scaled(ring_sprite(40, 4), 0.38 + 0.3 * ph), cx, cy, 0.5 * (1 - ph) * min(1, s))
    paste_center(canvas, scaled(icon_sprite(e["name"]), 0.16 * s, 4 * math.sin(age * 3)), cx, cy, min(1, s))


def render_overlay(t):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    seg = seg_at(t)
    lt = t - seg["start"]
    idx = SEGMENTS.index(seg)
    canvas.alpha_composite(top_shade())
    draw_ambient(canvas, t)
    if STYLE not in ("p3", "gta"):
        draw_minimap(canvas, t)
    if STYLE == "gta":
        draw_user_logo(canvas, t)

    # counter
    if seg["counter"] is not None:
        n = seg["counter"]
        prev = (SEGMENTS[idx - 1]["counter"] or 0) if idx else 0
        intro = seg["id"] == "title"
        appear = back_out(lt / 0.5) if intro else 1.0
        prog_from = 0 if intro else prev / TOTAL
        prog = (prog_from + (n / TOTAL - prog_from) * ease_out(lt / 0.5)) if n else 0.0
        changed = n != prev and not intro
        pop = 1 + 0.3 * (1 - elastic_out(lt / 0.7)) if changed else 1.0
        CY, CS, DY, DS = (118, 0.44, 190, 15) if STYLE not in ("p3", "gta") else (205, 0.58, 300, 26)
        if changed and lt < 0.5:
            paste_center(canvas, scaled(ring_sprite(52, 4), (1 + lt * 1.2) * CS / 0.44), W / 2, CY, 0.7 * (1 - lt / 0.5))
        paste_center(canvas, scaled(counter_sprite(n, prog, t, 1.0), max(0.02, CS * pop * appear)), W / 2, CY)
        d = ImageDraw.Draw(canvas)
        for i in range(TOTAL):
            x = W / 2 + (i - (TOTAL - 1) / 2) * DS
            on = i < n
            col = tuple((PINK + (ORANGE - PINK) * i / max(1, TOTAL - 1)).astype(int)) + (230,) if on else (255, 255, 255, 80)
            r = (3.5 if on else 2.5) * (1.6 if STYLE in ("p3", "gta") else 1)
            if on and i == n - 1:
                r += 1.5 * abs(math.sin(t * 5))
            d.ellipse([x - r, DY - r, x + r, DY + r], fill=col)

    # "#n" badge: corner (p1/p2) or numbered badge in the upper-middle band (p3)
    if seg["id"].startswith("f"):
        if STYLE in ("p3", "gta"):
            sp = num_badge_sprite(seg["counter"])
            pop = elastic_out(lt / 0.7)
            bx, by = 130, 715 + 6 * math.sin(t * 2.2)
            if lt < 0.6:
                paste_center(canvas, scaled(ring_sprite(70, 5), 0.8 + lt * 1.6), bx, by, 0.8 * (1 - lt / 0.6))
                draw_burst(canvas, bx, by, lt, n=16, seed=seg["counter"], dist=150, dur=0.6, small=True)
            paste_center(canvas, scaled(sp, max(0.05, pop), -8 * (1 - ease_out(lt / 0.5))), bx, by)
        else:
            sp = corner_num_sprite(seg["counter"])
            pop = elastic_out(lt / 0.6)
            paste_center(canvas, scaled(sp, max(0.05, pop)), 40 + sp.width / 2 - 20, 118)

    # timed decorative FX
    icon_slot = 0
    for e in FX:
        age = t - e["t"]
        if not 0 <= age < e["dur"]:
            continue
        k = e["kind"]
        if k in ("pulse", "ping"):
            continue   # centre stays empty
        elif k == "stars":
            draw_stars(canvas, e, age)
        elif k == "money_big":
            (draw_money_gta if STYLE == "gta" else draw_money_big)(canvas, e, age)
        elif k == "weapons":
            draw_weapons(canvas, e, t)
        elif k == "title":
            draw_title(canvas, age, e["dur"])
        elif k == "icon":
            draw_icon(canvas, e, age, icon_slot)
            icon_slot += 1

    tr = seg["transition"]
    if tr == "flash" and lt < 0.25:     # soft flash (the footage transition already dips to white)
        canvas.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(90 * (1 - lt / 0.25) ** 1.5))))
    return canvas


@lru_cache(None)
def corner_num_sprite(n):
    f = font(F_ANTON, 50)
    txt = f"#{n}"
    w = int(f.getlength(txt)) + 40
    h = 90
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((20, h / 2), txt, font=f, anchor="lm", fill=255)
    st = Image.new("L", (w, h), 0)
    ImageDraw.Draw(st).text((20, h / 2), txt, font=f, anchor="lm", fill=255, stroke_width=4, stroke_fill=255)
    im = Image.new("RGBA", (w, h), (255, 80, 110, 0))
    im.putalpha(st.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.7)))
    blk = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    blk.paste((15, 5, 20, 255), (0, 0), st)
    im = Image.alpha_composite(im, blk)
    im.paste(gradient_img(w, h, np.array([255, 70, 150.]), np.array([255, 170, 40.])), (0, 0), m)
    return im


GOLD_HI, GOLD_LO = np.array([255, 236, 150.]), np.array([214, 140, 20.])


@lru_cache(None)
def coin_and_bills_sprite():
    """Golden $ coin in front of a small stack of green dollar bills (drawn at 2x, downsampled)."""
    S = 360
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # bill stack (behind, tilted)
    bills = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bills)
    for k in range(4):
        y = 150 - k * 16
        x = 120 + k * 6
        bd.rounded_rectangle([x, y, x + 220, y + 110], 10, fill=(46, 140, 70, 255), outline=(170, 230, 170, 255), width=4)
        bd.rounded_rectangle([x + 14, y + 12, x + 206, y + 98], 8, outline=(120, 200, 130, 255), width=3)
        bd.ellipse([x + 80, y + 25, x + 140, y + 85], outline=(190, 240, 190, 255), width=4)
    bd.text((120 + 18 + 6 * 3 + 92, 150 - 48 + 55), "$", font=font(F_ANTON, 56), fill=(210, 250, 210, 255), anchor="mm")
    bills = bills.rotate(-12, Image.BICUBIC, center=(230, 160))
    im.alpha_composite(bills)
    # coin
    c, r = 130, 98
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    dist = np.sqrt((xx - c) ** 2 + (yy - (c + 70)) ** 2)
    k = np.clip(((xx - c) * -0.6 + (yy - (c + 70)) * -0.8) / r * 0.5 + 0.5, 0, 1)[..., None]
    col = GOLD_LO * (1 - k) + GOLD_HI * k
    coin = np.zeros((S, S, 4), np.float32)
    coin[..., :3] = col
    coin[..., 3] = np.clip(r - dist, 0, 1) * 255
    rim = (np.abs(dist - (r - 9)) < 4.5)
    coin[rim, :3] = coin[rim, :3] * 0.72
    cim = Image.fromarray(coin.astype(np.uint8), "RGBA")
    cd = ImageDraw.Draw(cim)
    cd.text((c + 4, c + 74), "$", font=font(F_ANTON, 150), fill=(150, 90, 10, 255), anchor="mm")
    cd.text((c, c + 70), "$", font=font(F_ANTON, 150), fill=(255, 246, 200, 255), anchor="mm")
    im.alpha_composite(cim)
    return im.resize((205, 205), Image.LANCZOS)


@lru_cache(256)
def money_text_sprite(txt):
    f = font(F_ANTON, 96)
    w = int(f.getlength(txt)) + 50
    h = 150
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((25, h / 2), txt, font=f, anchor="lm", fill=255)
    st = Image.new("L", (w, h), 0)
    ImageDraw.Draw(st).text((25, h / 2), txt, font=f, anchor="lm", fill=255, stroke_width=7, stroke_fill=255)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    blk = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    blk.paste((40, 22, 0, 255), (0, 0), st)
    im = Image.alpha_composite(im, blk)
    im.paste(gradient_img(w, h, GOLD_HI, GOLD_LO), (0, 0), m)
    return im


@lru_cache(None)
def gold_glow(w, h):
    g = Image.new("L", (w, h), 0)
    ImageDraw.Draw(g).ellipse([110, 100, w - 110, h - 100], fill=255)
    g = g.filter(ImageFilter.GaussianBlur(45))
    im = Image.new("RGBA", (w, h), (255, 200, 60, 0))
    im.putalpha(g.point(lambda v: int(v * 0.55)))
    return im


def draw_money_big(canvas, e, age):
    """Animated $20,000 badge: pop-up, count-up, golden glow, sparkles. Upper-middle (~37 % height)."""
    a = clamp(age / 0.12) * clamp((e["dur"] - age) / 0.3)
    s = back_out(age / 0.55)
    if e["dur"] - age < 0.3:
        s *= 0.85 + 0.15 * (e["dur"] - age) / 0.3
    amount = int(round(e["amount"] * ease_out(clamp((age - 0.1) / 0.7)) / 100.0) * 100)
    txt = f"${amount:,}"
    coin = coin_and_bills_sprite()
    tx = money_text_sprite(f"${e['amount']:,}")          # fixed width, for a stable layout
    tv = money_text_sprite(txt)
    total_w = coin.width - 30 + tx.width
    cx, cy = W / 2, 470 + 5 * math.sin(age * 2.3)
    glow = gold_glow(int(total_w + 260), 420)
    pulse = 0.75 + 0.25 * math.sin(age * 4)
    paste_center(canvas, scaled(glow, max(0.05, s)), cx, cy, a * pulse)
    group = Image.new("RGBA", (int(total_w), max(coin.height, tx.height)), (0, 0, 0, 0))
    group.alpha_composite(coin, (0, (group.height - coin.height) // 2))
    group.alpha_composite(tv, (coin.width - 30, (group.height - tv.height) // 2 + 6))
    paste_center(canvas, scaled(group, max(0.05, s), -5 * (1 - ease_out(age / 0.5))), cx, cy, a)
    if age < 0.7:
        draw_burst(canvas, cx, cy, age, n=22, seed=20, dist=260, dur=0.7, small=True)
    rng = np.random.default_rng(7)
    for i in range(7):                                    # twinkling gold sparkles around the badge
        sx = cx + rng.uniform(-total_w / 2, total_w / 2)
        sy = cy + rng.uniform(-95, 95)
        tw = max(0.0, math.sin(age * 5 + i * 1.7)) ** 3
        if tw > 0.05:
            paste_center(canvas, glow_dot(int(rng.choice([3, 4, 5])), (255, 225, 120)), sx, sy, a * tw)


# =================================================================== GTA-style graphics (STYLE "gta")
def _outline_text(txt, size, fill, stroke=12, shadow=True, grad=None):
    f = font(F_ANTON, size)
    w = int(f.getlength(txt)) + stroke * 2 + 60
    h = int(size * 1.45) + 40
    st = Image.new("L", (w, h), 0)
    ImageDraw.Draw(st).text((w / 2, h / 2), txt, font=f, anchor="mm", fill=255, stroke_width=stroke, stroke_fill=255)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((w / 2, h / 2), txt, font=f, anchor="mm", fill=255)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh.putalpha(st.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.7)))
        im.alpha_composite(sh, (6, 9))
    blk = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    blk.paste((0, 0, 0, 255), (0, 0), st)
    im = Image.alpha_composite(im, blk)
    if grad is not None:
        im.paste(gradient_img(w, h, *grad), (0, 0), m)
    else:
        im.paste(tuple(int(c) for c in fill), (0, 0), m)
    return im


@lru_cache(None)
def bill_stack_sprite():
    """Detailed stack of green US bills with a purple paper band (2x, downsampled)."""
    S = 520
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    for k in range(6):
        b = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(b)
        x0, y0 = 70, 150 - k * 12
        d.rounded_rectangle([x0, y0, x0 + 380, y0 + 175], 12, fill=(64, 150, 74, 255), outline=(22, 70, 30, 255), width=5)
        d.rounded_rectangle([x0 + 16, y0 + 14, x0 + 364, y0 + 161], 8, outline=(170, 230, 160, 255), width=3)
        d.ellipse([x0 + 140, y0 + 35, x0 + 240, y0 + 140], fill=(120, 190, 120, 255), outline=(30, 90, 40, 255), width=4)
        d.ellipse([x0 + 168, y0 + 55, x0 + 212, y0 + 99], fill=(60, 120, 64, 255))
        d.pieslice([x0 + 155, y0 + 80, x0 + 225, y0 + 150], 180, 360, fill=(60, 120, 64, 255))
        for cx_, cy_ in ((x0 + 45, y0 + 45), (x0 + 335, y0 + 130)):
            d.ellipse([cx_ - 22, cy_ - 22, cx_ + 22, cy_ + 22], outline=(190, 240, 180, 255), width=3)
            d.text((cx_, cy_), "$", font=font(F_ANTON, 30), anchor="mm", fill=(200, 245, 190, 255))
        b = b.rotate(-8 + k * 2.2, Image.BICUBIC, center=(S / 2, S / 2 + 20))
        im.alpha_composite(b)
    d = ImageDraw.Draw(im)
    d.rectangle([228, 60, 300, 360], fill=(140, 60, 230, 255), outline=(60, 10, 110, 255), width=5)
    d.text((264, 210), "$", font=font(F_ANTON, 64), anchor="mm", fill=(240, 220, 255, 255))
    return im.resize((260, 260), Image.LANCZOS)


@lru_cache(64)
def gta_money_text(txt):
    return _outline_text(txt, 150, GTA_GREEN, stroke=12)


@lru_cache(None)
def purple_glow(w, h):
    g = Image.new("L", (w, h), 0)
    ImageDraw.Draw(g).ellipse([120, 90, w - 120, h - 90], fill=255)
    g = g.filter(ImageFilter.GaussianBlur(55))
    im = Image.new("RGBA", (w, h), (140, 60, 255, 0))
    im.putalpha(g.point(lambda v: int(v * 0.55)))
    return im


def draw_money_gta(canvas, e, age):
    """GTA-style cash readout: bill stack + big green '$6,000' with black outline, purple glow, count-up."""
    a = clamp(age / 0.1) * clamp((e["dur"] - age) / 0.3)
    s = back_out(age / 0.5)
    amount = int(round(e["amount"] * ease_out(clamp((age - 0.05) / 0.6)) / 100.0) * 100)
    stack = bill_stack_sprite()
    tv = gta_money_text(f"${amount:,}")
    tfull = gta_money_text(f"${e['amount']:,}")
    gw = stack.width - 50 + tfull.width
    group = Image.new("RGBA", (gw, max(stack.height, tfull.height)), (0, 0, 0, 0))
    group.alpha_composite(stack, (0, (group.height - stack.height) // 2))
    group.alpha_composite(tv, (stack.width - 50, (group.height - tv.height) // 2))
    if group.width > 600:
        group = group.resize((600, int(group.height * 600 / group.width)), Image.LANCZOS)
    cx, cy = 40 + group.width / 2, 640 + 5 * math.sin(age * 2.3)     # left side, medium
    paste_center(canvas, scaled(purple_glow(group.width + 200, group.height + 160), max(0.05, s)), cx, cy,
                 a * (0.8 + 0.2 * math.sin(age * 4)))
    paste_center(canvas, scaled(group, max(0.05, s)), cx, cy, a)
    if age < 0.7:
        draw_burst(canvas, cx, cy, age, n=24, seed=60, dist=300, dur=0.7, small=True)


def _weapon(name):
    """Detailed weapon silhouette (mask + detail mask) on a 900x340 canvas, facing right."""
    Wd, Hd = 900, 340
    m = Image.new("L", (Wd, Hd), 0)
    det = Image.new("L", (Wd, Hd), 0)
    d, dd = ImageDraw.Draw(m), ImageDraw.Draw(det)
    if name == "rifle":                                   # carbine / assault rifle
        d.polygon([(30, 118), (165, 108), (170, 122), (205, 122), (205, 160), (172, 160), (150, 200), (40, 214), (24, 200)], fill=255)
        d.rectangle([200, 104, 470, 140], fill=255)                          # upper receiver
        d.polygon([(205, 138), (470, 138), (470, 163), (425, 175), (262, 175), (215, 160)], fill=255)
        d.rectangle([272, 66, 402, 94], fill=255)                            # optic
        d.ellipse([392, 64, 418, 96], fill=255)
        d.rectangle([292, 92, 318, 106], fill=255)
        d.rectangle([356, 92, 382, 106], fill=255)
        d.rectangle([465, 98, 705, 152], fill=255)                           # handguard
        d.polygon([(640, 98), (655, 66), (672, 66), (676, 98)], fill=255)    # front sight
        d.rectangle([700, 116, 830, 132], fill=255)                          # barrel
        d.rectangle([822, 108, 872, 140], fill=255)                          # flash hider
        d.polygon([(388, 170), (446, 170), (482, 300), (424, 314)], fill=255)    # curved magazine
        d.polygon([(268, 170), (320, 170), (302, 266), (250, 258)], fill=255)    # pistol grip
        d.line([(320, 172), (322, 204), (384, 204), (384, 172)], fill=255, width=9)  # trigger guard
        dd.rectangle([330, 112, 392, 130], fill=255)                         # ejection port
        for x in range(484, 690, 24):
            dd.rounded_rectangle([x, 110, x + 12, 140], 4, fill=255)         # rail slots
        for y in (200, 230, 260):
            dd.line([(395 + (y - 170) * 0.25, y), (452 + (y - 170) * 0.28, y)], fill=255, width=5)
        dd.line([(45, 150), (150, 140)], fill=255, width=5)
        for x in range(830, 868, 12):
            dd.line([(x, 112), (x, 136)], fill=255, width=3)
    elif name == "smg":                                   # submachine gun / machine gun
        d.rounded_rectangle([230, 104, 622, 156], 18, fill=255)              # receiver tube
        d.polygon([(500, 150), (640, 150), (640, 176), (522, 184)], fill=255)    # handguard
        d.rectangle([618, 118, 720, 140], fill=255)                          # barrel
        d.rectangle([705, 110, 745, 148], fill=255)                          # muzzle
        d.rectangle([596, 72, 632, 106], fill=255)                           # front sight hood
        d.rectangle([248, 78, 292, 106], fill=255)                           # rear sight drum
        d.polygon([(430, 152), (478, 152), (516, 302), (466, 314)], fill=255)    # curved magazine
        d.polygon([(298, 152), (352, 152), (336, 262), (284, 255)], fill=255)    # grip
        d.line([(352, 156), (354, 190), (420, 190), (420, 156)], fill=255, width=9)
        d.rectangle([78, 108, 236, 124], fill=255)                           # retractable stock
        d.rectangle([78, 140, 236, 154], fill=255)
        d.rounded_rectangle([62, 96, 98, 172], 8, fill=255)
        dd.rectangle([520, 92, 590, 102], fill=255)                          # cocking tube
        for x in range(380, 500, 22):
            dd.rectangle([x, 114, x + 10, 146], fill=255)
        for y in (205, 235, 265):
            dd.line([(442 + (y - 152) * 0.25, y), (488 + (y - 152) * 0.25, y)], fill=255, width=5)
    else:                                                 # semi-automatic pistol
        d.rounded_rectangle([226, 92, 664, 166], 14, fill=255)               # slide
        d.polygon([(236, 160), (646, 160), (646, 186), (430, 192), (404, 204), (236, 200)], fill=255)
        d.polygon([(248, 170), (382, 170), (352, 334), (214, 320)], fill=255)    # grip
        d.rounded_rectangle([380, 176, 486, 248], 26, outline=255, width=12)     # trigger guard
        d.line([(412, 190), (420, 230)], fill=255, width=10)                 # trigger
        d.rectangle([632, 80, 650, 94], fill=255)                            # front sight
        d.rectangle([246, 80, 276, 94], fill=255)                            # rear sight
        for x in range(270, 400, 18):
            dd.rectangle([x, 104, x + 8, 156], fill=255)                     # slide serrations
        dd.rectangle([470, 110, 560, 132], fill=255)                         # ejection port
        for y in range(200, 310, 22):
            for x in range(236 - (y - 170) // 5, 360 - (y - 170) // 5, 22):
                dd.ellipse([x, y, x + 8, y + 8], fill=255)                   # grip texture
    return m, det


@lru_cache(None)
def weapon_card(name):
    """Weapon-wheel style card: dark translucent rounded panel, purple/green rim, white detailed weapon."""
    m, det = _weapon(name)
    box = m.getbbox()
    pad = 34
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(m.width, box[2] + pad), min(m.height, box[3] + pad))
    m, det = m.crop(box), det.crop(box)
    wm = m.filter(ImageFilter.GaussianBlur(1))
    Wd, Hd = m.size
    card = Image.new("RGBA", (Wd + 80, Hd + 80), (0, 0, 0, 0))
    rim = Image.new("L", card.size, 0)
    ImageDraw.Draw(rim).rounded_rectangle([4, 4, card.width - 5, card.height - 5], 60, outline=255, width=10)
    glow = Image.new("RGBA", card.size, (150, 70, 255, 0))
    glow.putalpha(rim.filter(ImageFilter.GaussianBlur(14)))
    card = Image.alpha_composite(card, glow)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([10, 10, card.width - 11, card.height - 11], 54, fill=(12, 8, 20, 190))
    card.paste(gradient_img(card.width, card.height, GTA_PURPLE, GTA_GREEN, horizontal=True), (0, 0), rim)
    # weapon: black outline, white body, grey detail, soft top-light gradient
    out = m.filter(ImageFilter.MaxFilter(15))
    blk = Image.new("RGBA", m.size, (0, 0, 0, 0))
    blk.paste((0, 0, 0, 255), (0, 0), out)
    body = Image.new("RGBA", m.size, (0, 0, 0, 0))
    body.paste(gradient_img(Wd, Hd, np.array([255, 255, 255.]), np.array([170, 175, 190.])), (0, 0), wm)
    grey = Image.new("RGBA", m.size, (0, 0, 0, 0))
    grey.paste((90, 92, 105, 255), (0, 0), Image.fromarray(np.minimum(np.asarray(det), np.asarray(m))))
    wpn = Image.alpha_composite(Image.alpha_composite(blk, body), grey)
    card.alpha_composite(wpn, (40, 40))
    return card.resize((card.width // 2, card.height // 2), Image.LANCZOS)


def draw_weapons(canvas, e, t):
    """Weapon cards stacked on the right side, each popping in as it is named."""
    age = t - e["t"]
    a = clamp(age / 0.12) * clamp((e["dur"] - age) / 0.3)
    items = e["items"]
    cards = [weapon_card(nm) for nm, _ in items]
    th = 128                                               # equal card height on screen (medium)
    gap = 18
    tws = [min(390, c.width * th / c.height) for c in cards]
    hs = [c.height * w_ / c.width for c, w_ in zip(cards, tws)]
    total = sum(hs) + gap * (len(cards) - 1)
    y = 700 - total / 2
    for i, ((nm, ti), c, hh, tw) in enumerate(zip(items, cards, hs, tws)):
        cy = y + hh / 2
        y += hh + gap
        ai = t - ti
        if ai < 0:
            continue
        s = back_out(ai / 0.45) * tw / c.width
        cx = W - 30 - tw / 2 + 4 * math.sin(t * 2.0 + i)
        paste_center(canvas, scaled(c, max(0.05, s)), cx, cy, a)
        if ai < 0.5:
            draw_burst(canvas, cx, cy, ai, n=12, seed=i + 3, dist=150, dur=0.5, small=True)


@lru_cache(None)
def user_logo(width=150):          # ~14 % of the 1080 px width
    p = os.path.join(ROOT, "footage", "gta6_logo_alpha.png")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGBA")
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


LOGO_FROM = 0.0           # corner logo shown for the whole video


def draw_user_logo(canvas, t):
    """The user's own GTA VI logo, top centre, medium size; pops in after the intro, then stays."""
    lg = user_logo()
    if lg is None or t < LOGO_FROM:
        return
    u = t - LOGO_FROM
    s = back_out(u / 0.6) if u < 0.6 else 1.0
    a = clamp(u / 0.15)
    m = 34                                                 # margin from the top / right edges
    paste_center(canvas, scaled(lg, max(0.05, s)), W - m - lg.width / 2, m + 22 + lg.height / 2, a)


# --------------------------------------------------------------- intro title "GTA 6"
@lru_cache(None)
def title_sprite(green_safe=False):
    """'GTA 6' in a bold GTA-inspired treatment: white GTA, purple->green 6, heavy black outline.
    green_safe=True drops the soft shadow/glow so a chroma key cuts it cleanly."""
    g = _outline_text("GTA", 330, (255, 255, 255), stroke=18, shadow=not green_safe)
    six = _outline_text("6", 400, None, stroke=20, shadow=not green_safe, grad=(GTA_PURPLE, np.array([255, 80, 200.])))
    w = g.width + six.width - 70
    h = max(g.height, six.height)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if not green_safe:
        gl = Image.new("L", (w, h), 0)
        ImageDraw.Draw(gl).ellipse([60, 60, w - 60, h - 60], fill=255)
        glow = Image.new("RGBA", (w, h), (150, 70, 255, 0))
        glow.putalpha(gl.filter(ImageFilter.GaussianBlur(70)).point(lambda v: int(v * 0.55)))
        im.alpha_composite(glow)
    im.alpha_composite(g, (0, (h - g.height) // 2 + 20))
    im.alpha_composite(six, (g.width - 70, (h - six.height) // 2))
    return im


def _shine(sprite, k):
    w, h = sprite.size
    band = Image.new("L", (w, h), 0)
    x = -w * 0.3 + k * w * 1.6
    ImageDraw.Draw(band).polygon([(x, 0), (x + 90, 0), (x - 60, h), (x - 150, h)], fill=200)
    band = band.filter(ImageFilter.GaussianBlur(10))
    band = Image.fromarray(np.minimum(np.asarray(band), np.asarray(sprite.getchannel("A"))))
    white = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    white.putalpha(band)
    return Image.alpha_composite(sprite, white)


@lru_cache(None)
def intro_logo(width=760):
    p = os.path.join(ROOT, "footage", "gta6_intro_logo.png")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGBA")
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


def draw_title(canvas, age, dur, green_safe=False, cy=560):
    sp = intro_logo() or title_sprite(green_safe)
    if age < 0.3:
        s = 1.9 - 0.9 * ease_out(age / 0.3)
    else:
        s = 1.0 + 0.04 * ease_out(clamp((age - 0.3) / (dur - 0.3)))
    out = clamp((age - (dur - 0.3)) / 0.3)
    a = clamp(age / 0.12) * (1 - out)
    if 0.35 < age < 1.15 and not green_safe:
        sp = _shine(sp, (age - 0.35) / 0.8)
    shake = 10 * math.sin(age * 70) * max(0, 1 - (age - 0.3) / 0.25) if age > 0.3 else 0
    paste_center(canvas, scaled(sp, max(0.05, s * (1 - 0.25 * out))), W / 2 + shake, cy, a)
    if not green_safe and 0.28 < age < 0.95:
        draw_burst(canvas, W / 2, cy, age - 0.28, n=30, seed=66, dist=460, dur=0.67)

@lru_cache(None)
def num_badge_sprite(n):
    """Numbered badge '#n' for STYLE p3: dark disc, glowing pink->orange ring, white/gradient number."""
    S = 300
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = S / 2
    ring = Image.new("L", (S, S), 0)
    ImageDraw.Draw(ring).ellipse([c - 110, c - 110, c + 110, c + 110], outline=255, width=16)
    glow = Image.new("RGBA", (S, S), (255, 80, 110, 0))
    glow.putalpha(ring.filter(ImageFilter.GaussianBlur(16)))
    im = Image.alpha_composite(im, glow)
    d = ImageDraw.Draw(im)
    d.ellipse([c - 102, c - 102, c + 102, c + 102], fill=(14, 6, 24, 225))
    im.paste(gradient_img(S, S, PINK, ORANGE, horizontal=True), (0, 0), ring)
    f = font(F_ANTON, 120)
    txt = f"#{n}"
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).text((c, c + 4), txt, font=f, anchor="mm", fill=255)
    st = Image.new("L", (S, S), 0)
    ImageDraw.Draw(st).text((c, c + 4), txt, font=f, anchor="mm", fill=255, stroke_width=6, stroke_fill=255)
    blk = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    blk.paste((10, 4, 16, 255), (0, 0), st)
    im = Image.alpha_composite(im, blk)
    im.paste(gradient_img(S, S, np.array([255, 255, 255.]), np.array([255, 190, 120.])), (0, 0), m)
    return im.resize((150, 150), Image.LANCZOS)


@lru_cache(None)
def top_shade():
    a = np.zeros((H, 1), np.float32)
    a[:520, 0] = np.linspace(0.5, 0, 520) ** 1.5
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.putalpha(Image.fromarray((np.repeat(a, W, 1) * 255).astype(np.uint8)))
    return im


def make_frame(i):
    return render_overlay(i / FPS).tobytes()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float)
    ap.add_argument("--bg", help="video to composite under --still (e.g. out/bg_cut.mp4)")
    ap.add_argument("--out")
    ap.add_argument("-j", type=int, default=os.cpu_count())
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    a = ap.parse_args()
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    if a.still is not None:
        if a.bg:
            raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-ss", str(a.still), "-i", a.bg, "-frames:v", "1",
                                           "-f", "rawvideo", "-pix_fmt", "rgba", "-"])
            bg = Image.frombytes("RGBA", (W, H), raw)
        else:
            bg = Image.new("RGBA", (W, H), (70, 70, 78, 255))
        bg.alpha_composite(render_overlay(a.still))
        p = a.out or os.path.join(ROOT, "out", f"still_{a.still:05.2f}.png")
        bg.convert("RGB").save(p)
        print(p)
        return
    out = a.out or os.path.join(ROOT, "out", "overlay_prores4444.mov")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
           "-vendor", "apl0", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    f0 = int(round(a.start * FPS))
    n = int(round((a.end if a.end is not None else DURATION) * FPS))
    with Pool(a.j) as pool:
        for k, data in enumerate(pool.imap(make_frame, range(f0, n), chunksize=8)):
            proc.stdin.write(data)
            if k % 300 == 0:
                print(f"{k}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
