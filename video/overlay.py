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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(HERE, "assets", "fonts")
F_ANTON = os.path.join(FONT_DIR, "Anton.woff")
F_MONT = os.path.join(FONT_DIR, "Montserrat-800.woff")

PINK = np.array([255, 46, 136], float)
ORANGE = np.array([255, 154, 31], float)
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
        s1, s2 = str(n), "/10"
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
    im = im.resize((150, 150), Image.LANCZOS)
    canvas.alpha_composite(im, (44, 1470))
    dd = ImageDraw.Draw(canvas)
    dd.rounded_rectangle([50, 1628, 190, 1636], 6, fill=(0, 0, 0, 150))
    dd.rounded_rectangle([50, 1628, 50 + 140 * (0.8 + 0.15 * math.sin(t * 0.7)), 1636], 6, fill=(90, 220, 110, 230))
    dd.rounded_rectangle([50, 1642, 190, 1650], 6, fill=(0, 0, 0, 150))
    dd.rounded_rectangle([50, 1642, 50 + 140 * 0.6, 1650], 6, fill=(80, 170, 255, 230))



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
AMBIENT = [dict(x=_RNG.uniform(0, W), y=_RNG.uniform(0, H), v=_RNG.uniform(25, 70), r=int(_RNG.choice([3, 4, 5, 7])),
                ph=_RNG.uniform(0, 6.28), col=[(255, 46, 136), (255, 154, 31), (255, 220, 180)][i % 3]) for i in range(34)]


def draw_ambient(canvas, t):
    for p in AMBIENT:
        y = (p["y"] - t * p["v"]) % (H + 100) - 50
        x = p["x"] + 22 * math.sin(t * 0.8 + p["ph"])
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
    size = 44
    x0 = W / 2 - 6 * size * 0.92 / 2 + size / 2
    flash = math.sin(age * 2 * math.pi * 4) > 0
    lose = e.get("lose")
    for i in range(6):
        on = i < n and age >= i * 0.09
        if lose and age > e["dur"] - 0.7:
            on = on and (i < n - int((age - (e["dur"] - 0.7)) / 0.12))
        sp = star_sprite(on, bool(on and flash))
        pop = back_out(clamp((age - i * 0.09) / 0.25)) if on else 1.0
        paste_center(canvas, scaled(sp, max(0.05, pop * 0.4)), x0 + i * size * 0.92, 300, a)



ICON_POS = [(830, 980), (250, 980)]


def draw_icon(canvas, e, age, slot):
    s = back_out(age / 0.45) * clamp((e["dur"] - age) / 0.2)
    if s <= 0.01:
        return
    bx, by = ICON_POS[slot % 2]
    cx = bx + 8 * math.sin(age * 1.7 + slot)
    cy = by - 26 * ease_out(age / e["dur"]) + 6 * math.sin(age * 2.6)     # slow float upwards
    ph = (age * 0.9) % 1
    paste_center(canvas, scaled(ring_sprite(40, 4), 0.9 + 0.7 * ph), cx, cy, 0.55 * (1 - ph) * min(1, s))
    paste_center(canvas, scaled(icon_sprite(e["name"]), 0.36 * s, 4 * math.sin(age * 3)), cx, cy, min(1, s))


def render_overlay(t):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    seg = seg_at(t)
    lt = t - seg["start"]
    idx = SEGMENTS.index(seg)
    canvas.alpha_composite(top_shade())
    draw_ambient(canvas, t)
    draw_minimap(canvas, t)

    # counter
    if seg["counter"] is not None:
        n = seg["counter"]
        prev = (SEGMENTS[idx - 1]["counter"] or 0) if idx else 0
        intro = seg["id"] == "title"
        appear = back_out(lt / 0.5) if intro else 1.0
        prog_from = 0 if intro else prev / 10
        prog = (prog_from + (n / 10 - prog_from) * ease_out(lt / 0.5)) if n else 0.0
        changed = n != prev and not intro
        pop = 1 + 0.3 * (1 - elastic_out(lt / 0.7)) if changed else 1.0
        CY = 150
        if changed and lt < 0.5:
            paste_center(canvas, scaled(ring_sprite(75, 5), 1 + lt * 1.6), W / 2, CY, 0.8 * (1 - lt / 0.5))
        paste_center(canvas, scaled(counter_sprite(n, prog, t, 1.0), max(0.02, 0.62 * pop * appear)), W / 2, CY)
        d = ImageDraw.Draw(canvas)
        for i in range(10):
            x = W / 2 + (i - 4.5) * 20
            on = i < n
            col = tuple((PINK + (ORANGE - PINK) * i / 9).astype(int)) + (230,) if on else (255, 255, 255, 80)
            r = 4.5 if on else 3.5
            if on and i == n - 1:
                r = 4.5 + 1.5 * abs(math.sin(t * 5))
            d.ellipse([x - r, 238 - r, x + r, 238 + r], fill=col)

    # timed decorative FX
    icon_slot = 0
    for e in FX:
        age = t - e["t"]
        if not 0 <= age < e["dur"]:
            continue
        k = e["kind"]
        if k == "pulse":
            paste_center(canvas, scaled(ring_sprite(60, 4), 0.6 + age * 1.4), W / 2, 960, 0.7 * max(0, 1 - age / 0.9))
            draw_burst(canvas, W / 2, 960, age, n=14, seed=int(e["t"] * 10), dist=170, dur=0.8, small=True)
        elif k == "ping":
            draw_ping(canvas, e["x"], e["y"], age, e["dur"])
        elif k == "stars":
            draw_stars(canvas, e, age)
        elif k == "icon":
            draw_icon(canvas, e, age, icon_slot)
            icon_slot += 1

    tr = seg["transition"]
    if tr == "flash" and lt < 0.3:
        canvas.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - lt / 0.3) ** 1.5))))
    if lt < 0.45 and idx > 0:   # glow sweep on every transition
        k = lt / 0.45
        yy, xx = np.mgrid[0:H // 8, 0:W // 8]
        cx = -20 + k * (W // 8 + 40)
        g = np.clip(1 - np.sqrt((xx - cx) ** 2 + (yy - H // 16) ** 2 * 0.25) / 80, 0, 1)
        a = Image.fromarray((g * 110 * math.sin(math.pi * k)).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        leak = Image.new("RGBA", (W, H), (255, 120, 80, 0))
        leak.putalpha(a)
        canvas.alpha_composite(leak)
    return canvas


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
    n = int(round(DURATION * FPS))
    with Pool(a.j) as pool:
        for k, data in enumerate(pool.imap(make_frame, range(n), chunksize=8)):
            proc.stdin.write(data)
            if k % 300 == 0:
                print(f"{k}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
