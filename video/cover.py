"""
TikTok cover (1080x1920) built ONLY from real frames of the supplied GTA 6 clips:
  - background: Vice City neon street at night (c1 @ 18.4 s)
  - Jason: profile in sunglasses (c2 @ 6.0 s)
  - Lucia: facing camera (c4 @ 14.6 s)
Graphics reuse the video's identity: pink→orange glowing ring counter, Anton type,
small gaming icons, glow particles.

    python video/cover.py              # out/cover.png + out/cover_clean.png (no title)
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from overlay import (F_ANTON, F_MONT, ORANGE, PINK, W, H, font, glow_dot,  # noqa: E402
                     gradient_img, icon_sprite, paste_center, ring_sprite, star_sprite)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def frame(src, t):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", os.path.join(ROOT, "footage", src),
                                   "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return Image.frombytes("RGB", (W, H), raw)


def grade(im, warm=1.0):
    a = np.asarray(im, np.float32) / 255
    a = a / (1 + a * 0.15) * 1.12                      # soft tonemap
    lum = a.mean(-1, keepdims=True)
    tint = np.array([1.06, 0.97, 1.02]) * warm
    a = a * tint + (1 - lum) * np.array([0.04, 0.0, 0.06])   # purple-lifted shadows
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def panel_mask(poly):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return m


def glow_line(canvas, p0, p1, width=8):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).line([p0, p1], fill=255, width=width)
    glow = Image.new("RGBA", (W, H), (255, 90, 110, 0))
    glow.putalpha(m.filter(ImageFilter.GaussianBlur(18)))
    canvas.alpha_composite(glow)
    canvas.alpha_composite(glow)
    g = gradient_img(W, H, PINK, ORANGE)
    line = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    line.paste(g, (0, 0), m)
    canvas.alpha_composite(line)


def text_sprite(txt, size, fill_grad=None, stroke=10, glow=0.7):
    f = font(F_ANTON, size)
    w = int(f.getlength(txt)) + stroke * 2 + 60
    h = int(size * 1.45) + 40
    st = Image.new("L", (w, h), 0)
    ImageDraw.Draw(st).text((w / 2, h / 2), txt, font=f, anchor="mm", fill=255, stroke_width=stroke, stroke_fill=255)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((w / 2, h / 2), txt, font=f, anchor="mm", fill=255)
    im = Image.new("RGBA", (w, h), (255, 80, 110, 0))
    im.putalpha(st.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * glow)))
    blk = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    blk.paste((10, 4, 16, 255), (0, 0), st)
    im = Image.alpha_composite(im, blk)
    if fill_grad:
        im.paste(gradient_img(w, h, *fill_grad), (0, 0), m)
    else:
        im.paste((255, 255, 255), (0, 0), m)
    return im


def name_tag(txt):
    f = font(F_ANTON, 50)
    w = int(f.getlength(txt)) + 56
    h = 72
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    g = Image.new("L", im.size, 0)
    ImageDraw.Draw(g).rounded_rectangle([20, 20, 20 + w, 20 + h], 16, fill=255)
    glow = Image.new("RGBA", im.size, (255, 80, 110, 0))
    glow.putalpha(g.filter(ImageFilter.GaussianBlur(12)))
    im = Image.alpha_composite(im, glow)
    im.paste(gradient_img(im.width, im.height, PINK, ORANGE, horizontal=True), (0, 0), g)
    ImageDraw.Draw(im).text((20 + w / 2, 20 + h / 2 + 2), txt, font=f, anchor="mm", fill="white",
                            stroke_width=3, stroke_fill=(60, 0, 30))
    return im


def big_ten():
    S = 420
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = S / 2
    ring = Image.new("L", (S, S), 0)
    ImageDraw.Draw(ring).ellipse([c - 160, c - 160, c + 160, c + 160], outline=255, width=24)
    glow = Image.new("RGBA", (S, S), (255, 80, 110, 0))
    glow.putalpha(ring.filter(ImageFilter.GaussianBlur(22)))
    im = Image.alpha_composite(im, glow)
    im = Image.alpha_composite(im, glow)
    d = ImageDraw.Draw(im)
    d.ellipse([c - 148, c - 148, c + 148, c + 148], fill=(14, 6, 24, 215))
    im.paste(gradient_img(S, S, PINK, ORANGE, horizontal=True), (0, 0), ring)
    d = ImageDraw.Draw(im)
    d.ellipse([c + 108, c - 128, c + 132, c - 104], fill=(255, 255, 230))     # spark on the ring
    d.text((c, c + 6), "10", font=font(F_ANTON, 190), anchor="mm", fill="white", stroke_width=6, stroke_fill="black")
    return im.resize((300, 300), Image.LANCZOS)


def build(with_title=True):
    # --- background: neon Vice City street, darkened + blurred so characters pop
    bg = frame("c1.mp4", 18.4)
    bg = grade(bg).filter(ImageFilter.GaussianBlur(3))
    bg = ImageEnhance.Brightness(bg).enhance(0.8)
    canvas = bg.convert("RGBA")
    # pink/orange atmosphere
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    haze = np.clip(1 - np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.33) / H) ** 2) * 2.2, 0, 1) ** 2
    hz = Image.new("RGBA", (W, H), (255, 70, 120, 0))
    hz.putalpha(Image.fromarray((haze * 110).astype(np.uint8)))
    canvas.alpha_composite(hz)

    # --- character panels split by a glowing diagonal
    top, bot = 640, H
    xa, xb = 690, 390                      # diagonal from (xa, top) to (xb, bot)
    jason = grade(frame("c2.mp4", 6.0), 1.02).crop((0, 60, 760, 1410)).resize((800, 1421), Image.LANCZOS)
    jason = jason.filter(ImageFilter.UnsharpMask(2, 80, 2))
    lucia = grade(frame("c4.mp4", 14.6), 1.02).crop((120, 170, 980, 1560)).resize((900, 1455), Image.LANCZOS)
    lucia = lucia.filter(ImageFilter.UnsharpMask(2, 80, 2))
    jl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    jl.paste(jason, (-10, top - 50))
    ll = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ll.paste(lucia, (290, top - 30))
    canvas.paste(jl, (0, 0), panel_mask([(0, top + 40), (xa, top), (xb, bot), (0, bot)]))
    canvas.paste(ll, (0, 0), panel_mask([(xa, top), (W, top - 40), (W, bot), (xb, bot)]))
    # panel top edges + diagonal
    glow_line(canvas, (0, top + 40), (xa, top), 6)
    glow_line(canvas, (xa, top), (W, top - 40), 6)
    glow_line(canvas, (xa, top), (xb, bot), 9)
    # bottom fade so the TikTok UI band stays readable
    a = np.zeros((H, 1), np.float32)
    a[H - 380:, 0] = np.linspace(0, 0.75, 380) ** 1.4
    a[:300, 0] = np.linspace(0.55, 0, 300) ** 1.4
    shade = Image.new("RGBA", (W, H), (8, 2, 14, 0))
    shade.putalpha(Image.fromarray((np.repeat(a, W, 1) * 255).astype(np.uint8)))
    canvas.alpha_composite(shade)

    # names
    paste_center(canvas, name_tag("JASON"), 170, 1440)
    paste_center(canvas, name_tag("LUCIA"), 900, 1440)

    if with_title:
        # big counter-style ring with "10"
        paste_center(canvas, big_ten(), 230, 420)
        paste_center(canvas, text_sprite("DÉTAILS", 165), 680, 360)
        paste_center(canvas, text_sprite("QUE PERSONNE", 74, (np.array([255, 70, 150.]), np.array([255, 170, 40.])), 7), 680, 492)
        paste_center(canvas, text_sprite("NE CONNAÎT", 74, (np.array([255, 70, 150.]), np.array([255, 170, 40.])), 7), 680, 572)
        # small "GTA 6" pill
        f = font(F_MONT, 30)
        pill = Image.new("RGBA", (190, 62), (0, 0, 0, 0))
        g = Image.new("L", pill.size, 0)
        ImageDraw.Draw(g).rounded_rectangle([0, 0, 189, 61], 30, fill=255)
        pill.paste(gradient_img(190, 62, PINK, ORANGE, horizontal=True), (0, 0), g)
        dd = ImageDraw.Draw(pill)
        dd.rounded_rectangle([4, 4, 185, 57], 26, fill=(14, 6, 22, 235))
        dd.text((95, 32), "GTA 6", font=f, anchor="mm", fill="white")
        paste_center(canvas, pill, W / 2, 205)

    # small icons near the edges + wanted stars
    for name, (x, y) in {"comment": (1010, 760), "car": (1012, 900), "cash": (1010, 1040),
                         "gun": (70, 820), "pin": (68, 960)}.items():
        paste_center(canvas, ring_sprite(40, 4).resize((70, 70), Image.LANCZOS), x, y, 0.5)
        paste_center(canvas, icon_sprite(name).resize((50, 50), Image.LANCZOS), x, y)
    for i in range(5):
        paste_center(canvas, star_sprite(True, i < 2).resize((40, 40), Image.LANCZOS), W / 2 - 80 + i * 40, 1600)
    # glow particles along the edges
    rng = np.random.default_rng(3)
    for i in range(40):
        x = float(rng.choice([rng.uniform(10, 150), rng.uniform(W - 150, W - 10)]))
        y = rng.uniform(150, H - 200)
        col = [(255, 46, 136), (255, 154, 31), (255, 220, 180)][i % 3]
        paste_center(canvas, glow_dot(int(rng.choice([3, 4, 6])), col), x, y, rng.uniform(0.3, 0.8))
    return canvas.convert("RGB")


def main():
    out = os.path.join(ROOT, "out")
    os.makedirs(out, exist_ok=True)
    build(True).save(os.path.join(out, "cover.png"))
    build(False).save(os.path.join(out, "cover_clean.png"))
    print("wrote out/cover.png, out/cover_clean.png")


if __name__ == "__main__":
    main()
