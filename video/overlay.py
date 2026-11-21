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
from timeline import SEGMENTS, FPS, W, H, DURATION, all_shots, all_captions  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(HERE, "assets", "fonts")
F_ANTON = os.path.join(FONT_DIR, "Anton.woff")
F_MONT = os.path.join(FONT_DIR, "Montserrat-800.woff")

PINK = np.array([255, 46, 136], float)
ORANGE = np.array([255, 154, 31], float)
YELLOW = (255, 225, 77)

SHOTS = all_shots()
CAPS = all_captions()

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


def shot_at(t):
    for s in SHOTS:
        if s["start"] <= t < s["end"]:
            return s
    return SHOTS[-1]


# =================================================================== overlay sprites
def gradient_img(w, h, c1=PINK, c2=ORANGE, horizontal=False):
    if horizontal:
        k = np.linspace(0, 1, w)[None, :, None]
    else:
        k = np.linspace(0, 1, h)[:, None, None]
    arr = c1 * (1 - k) + c2 * k
    arr = np.broadcast_to(arr, (h, w, 3))
    return Image.fromarray(arr.astype(np.uint8), "RGB")


@lru_cache(64)
def caption_sprite(text, hl, size=134, color_hl=YELLOW, gold=False):
    hl = set(hl)
    f = font(F_ANTON, size)
    stroke = max(8, size // 10)
    words = text.split(" ")
    space = f.getlength(" ")
    maxw = 940

    def width(ws):
        return sum(f.getlength(w) for w in ws) + space * (len(ws) - 1)

    lines = [words]
    if width(words) > maxw and len(words) > 1:
        best = None
        for i in range(1, len(words)):
            m = max(width(words[:i]), width(words[i:]))
            if best is None or m < best[0]:
                best = (m, i)
        lines = [words[:best[1]], words[best[1]:]]
    while max(width(l) for l in lines) > maxw:
        size -= 6
        f = font(F_ANTON, size)
        space = f.getlength(" ")
        stroke = max(8, size // 10)
    asc, desc = f.getmetrics()
    lh = asc + desc
    pad = stroke + 30
    Wd = int(max(width(l) for l in lines) + pad * 2)
    Ht = int(lh * len(lines) * 0.98 + pad * 2)
    sprite = Image.new("RGBA", (Wd, Ht), (0, 0, 0, 0))
    shadow = Image.new("L", (Wd, Ht), 0)
    fill_hl = Image.new("L", (Wd, Ht), 0)
    d = ImageDraw.Draw(sprite)
    ds = ImageDraw.Draw(shadow)
    dh = ImageDraw.Draw(fill_hl)
    y = pad
    for line in lines:
        x = (Wd - width(line)) / 2
        for w in line:
            ds.text((x, y + 12), w, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
            d.text((x, y), w, font=f, fill=(255, 255, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            if w in hl:
                dh.text((x, y), w, font=f, fill=255)
            x += f.getlength(w) + space
        y += lh * 0.98
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    sh = Image.new("RGBA", (Wd, Ht), (0, 0, 0, 0))
    sh.putalpha(shadow.point(lambda v: int(v * 0.65)))
    if gold:
        g = gradient_img(Wd, Ht, np.array([255, 240, 140.]), np.array([255, 150, 20.]))
    else:
        g = gradient_img(Wd, Ht, np.array(color_hl, float), np.array([255, 170, 40.]))
    sprite.paste(g, (0, 0), fill_hl)
    return Image.alpha_composite(sh, sprite)


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
    if n == 0:
        d.text((cx, cx - 14), "10", font=font(F_ANTON, 84), fill="white", anchor="mm", stroke_width=4, stroke_fill="black")
        d.text((cx, cx + 46), "DETAILS", font=font(F_MONT, 20), fill=(255, 190, 120), anchor="mm")
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
    text = "CRAZY DETAILS YOU MISSED IN GTA 6"
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



# =================================================================== overlay frame
def icon_layout(slot, t):
    return 900 + 10 * math.sin(t * 2.4), 700 + 8 * math.sin(t * 3.1)


def draw_icons(canvas, seg, t):
    lt = t - seg["start"]
    cur = None
    for at, name, slot in seg.get("icons", []):
        if lt >= at:
            cur = (at, name, slot)
    if not cur:
        return
    at, name, slot = cur
    age = lt - at
    s = elastic_out(age / 0.6) * clamp((seg["end"] - t) / 0.12) * 0.72
    if s <= 0.01:
        return
    cx, cy = icon_layout(slot, t)
    sp = scaled(icon_sprite(name), s * (1 + 0.04 * math.sin(t * 6)), 6 * math.sin(t * 4))
    paste_center(canvas, sp, cx, cy)
    d = ImageDraw.Draw(canvas)
    for j in range(3):   # chevrons pointing at the icon
        ph = (t * 2.5 - j * 0.25) % 1
        a = int(255 * (1 - ph) * min(1, s / 0.72))
        x = cx - 115 - j * 30 + ph * 18
        d.line([x - 12, cy - 19, x + 5, cy, x - 12, cy + 19], fill=(255, 225, 77, a), width=9, joint="curve")


def render_overlay(t):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    seg = seg_at(t)
    lt = t - seg["start"]
    idx = SEGMENTS.index(seg)

    # soft top/bottom gradient so white text + ring always read on bright gameplay
    canvas.alpha_composite(top_shade())

    if seg["counter"] is not None:
        n = seg["counter"]
        prev = (SEGMENTS[idx - 1]["counter"] or 0) if idx else 0
        intro = seg["id"] == "title"
        appear = back_out(lt / 0.5) if intro else 1.0
        prog_from = 0 if intro else prev / 10
        prog = (prog_from + (n / 10 - prog_from) * ease_out(lt / 0.5)) if n else 0.0
        changed = n != prev and not intro
        pop = 1 + 0.28 * (1 - elastic_out(lt / 0.7)) if changed else 1.0
        paste_center(canvas, counter_sprite(n, prog, t, max(0.02, pop * appear)), W / 2, 205)
        pa = clamp((lt - 0.15) / 0.3) if intro else 1.0
        paste_center(canvas, scaled(pill_sprite(), 0.6 + 0.4 * ease_out(pa)), W / 2, 360, pa)
        d = ImageDraw.Draw(canvas)
        for i in range(10):
            x = W / 2 + (i - 4.5) * 34
            on = i < n
            col = tuple((PINK + (ORANGE - PINK) * i / 9).astype(int)) + (255,) if on else (255, 255, 255, 90)
            r = 8 if on else 6
            if on and i == n - 1:
                r = 8 + 3 * abs(math.sin(t * 5))
            d.ellipse([x - r, 418 - r, x + r, 418 + r], fill=col)

    cap = next((c for c in CAPS if c["start"] <= t < c["end"]), None)
    if cap:
        age = t - cap["start"]
        hl = tuple(w for w in cap["text"].split(" ") if w in cap["hl"])
        sp = caption_sprite(cap["text"], hl, 134)
        if age < 0.09:
            s = 0.55 + 0.6 * ease_out(age / 0.09)
        elif age < 0.2:
            s = 1.15 - 0.15 * ease_in_out((age - 0.09) / 0.11)
        else:
            s = 1.0 + 0.012 * math.sin(age * 4)
        rot = -3 * (1 - ease_out(age / 0.2))
        y = 1020 - 30 * (1 - ease_out(age / 0.2))
        paste_center(canvas, scaled(sp, s, rot), W / 2, y)

    draw_icons(canvas, seg, t)

    tr = seg["transition"]
    if tr == "flash" and lt < 0.3:
        canvas.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - lt / 0.3) ** 1.5))))
    if tr == "light_leak" and lt < 0.7:
        k = lt / 0.7
        yy, xx = np.mgrid[0:H // 8, 0:W // 8]
        cx = -20 + k * (W // 8 + 40)
        g = np.clip(1 - np.sqrt((xx - cx) ** 2 + (yy - H // 16) ** 2 * 0.3) / 90, 0, 1)
        a = Image.fromarray((g * 200 * math.sin(math.pi * k)).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        leak = Image.new("RGBA", (W, H), (255, 140, 60, 0))
        leak.putalpha(a)
        canvas.alpha_composite(leak)
    return canvas


@lru_cache(None)
def top_shade():
    a = np.zeros((H, 1), np.float32)
    a[:520, 0] = np.linspace(0.55, 0, 520) ** 1.5
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.putalpha(Image.fromarray((np.repeat(a, W, 1) * 255).astype(np.uint8)))
    return im


def make_frame(i):
    return render_overlay(i / FPS).tobytes()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float)
    ap.add_argument("--out")
    ap.add_argument("-j", type=int, default=os.cpu_count())
    a = ap.parse_args()
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    if a.still is not None:
        bg = Image.new("RGBA", (W, H), (70, 70, 78, 255))
        bg.alpha_composite(render_overlay(a.still))
        p = a.out or os.path.join(ROOT, "out", f"overlay_{a.still:05.2f}.png")
        bg.convert("RGB").save(p)
        print(p)
        return
    out = a.out or os.path.join(ROOT, "out", "overlay_prores4444.mov")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
           "-vendor", "apl0", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DURATION * FPS)
    with Pool(a.j) as pool:
        for k, data in enumerate(pool.imap(make_frame, range(n), chunksize=8)):
            proc.stdin.write(data)
            if k % 150 == 0:
                print(f"{k}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
