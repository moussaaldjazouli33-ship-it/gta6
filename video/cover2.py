"""
TikTok cover for project p2 ("10 trucs à savoir avant de jouer").
Hero frame = the Jason + Lucia convertible shot used in the final video (shot s02,
t1.mp4 @ 26.5 s), super-resolved with the same ESRGAN-slim pipeline as the edit,
over the same blurred extension style. Graphics reuse the video identity.

    python video/cover2.py        # out/gta6_10_trucs_cover.png
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("GTA_PROJECT", "p2")
import reframe  # noqa: E402
from cover import big_ten, glow_line, name_tag, text_sprite  # noqa: E402
from overlay import F_MONT, ORANGE, PINK, W, H, font, glow_dot, gradient_img, icon_sprite, paste_center, ring_sprite  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAD = (np.array([255, 70, 150.]), np.array([255, 170, 40.]))


def main():
    src = reframe.decode(os.path.join(ROOT, "footage", "t1.mp4"), 26.5, 1)[0]
    # hero window: both characters (Lucia 0.12-0.47, Jason 0.50-0.72 of the width)
    cx, w = 0.475 * 1280, 0.56 * 1280
    win = Image.fromarray(src).crop((int(cx - w / 2), 0, int(cx + w / 2), 720))
    hero = reframe._sr(win)                                   # x2 AI super-resolution
    hh = int(round(W * hero.height / hero.width))
    hero = hero.resize((W, hh), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 45, 2))
    hero = ImageEnhance.Contrast(hero).enhance(1.06)
    hero = ImageEnhance.Color(hero).enhance(1.10)

    # background: same shot, blurred extension in its own colours, darker at the top for the title
    bg = reframe._bg(src, cx).convert("RGBA")
    a = np.zeros((H, 1), np.float32)
    a[:700, 0] = np.linspace(0.50, 0.05, 700)
    a[H - 220:, 0] = np.linspace(0.0, 0.45, 220)
    shade = Image.new("RGBA", (W, H), (10, 3, 16, 0))
    shade.putalpha(Image.fromarray((np.repeat(a, W, 1) * 255).astype(np.uint8)))
    bg.alpha_composite(shade)
    haze = Image.new("RGBA", (W, H), (255, 80, 120, 0))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - 420) / H) ** 2) * 2.4, 0, 1) ** 2
    haze.putalpha(Image.fromarray((g * 90).astype(np.uint8)))
    bg.alpha_composite(haze)

    y0 = 640
    canvas = bg
    m = np.ones((hh, 1), np.float32)
    m[:60, 0] = np.linspace(0, 1, 60) ** 1.5
    m[-60:, 0] = np.linspace(1, 0, 60) ** 1.5
    canvas.paste(hero.convert("RGBA"), (0, y0), Image.fromarray((np.repeat(m, W, 1) * 255).astype(np.uint8)))
    glow_line(canvas, (40, y0 + 8), (W - 40, y0 + 8), 5)
    glow_line(canvas, (40, y0 + hh - 8), (W - 40, y0 + hh - 8), 5)

    # title block
    pill = Image.new("RGBA", (190, 62), (0, 0, 0, 0))
    pm = Image.new("L", pill.size, 0)
    ImageDraw.Draw(pm).rounded_rectangle([0, 0, 189, 61], 30, fill=255)
    pill.paste(gradient_img(190, 62, PINK, ORANGE, horizontal=True), (0, 0), pm)
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([4, 4, 185, 57], 26, fill=(14, 6, 22, 235))
    pd.text((95, 32), "GTA 6", font=font(F_MONT, 30), anchor="mm", fill="white")
    paste_center(canvas, pill, W / 2, 190)
    paste_center(canvas, big_ten(), 250, 380)
    paste_center(canvas, text_sprite("TRUCS", 190), 660, 365)
    paste_center(canvas, text_sprite("À SAVOIR AVANT DE JOUER", 72, GRAD, 7), W / 2, 545)

    # name tags pointing at the characters
    paste_center(canvas, name_tag("LUCIA"), 190, y0 + 140)
    paste_center(canvas, name_tag("JASON"), 900, y0 + 140)

    # small topic icons near the edges (money, fuel, lockpick, sleep, police dog)
    for name, (x, y) in {"cash": (90, 1800), "fuel": (300, 1800), "lock": (W / 2, 1800),
                         "moon": (W - 300, 1800), "paw": (W - 90, 1800)}.items():
        paste_center(canvas, ring_sprite(40, 4).resize((78, 78), Image.LANCZOS), x, y, 0.5)
        paste_center(canvas, icon_sprite(name).resize((58, 58), Image.LANCZOS), x, y)
    rng = np.random.default_rng(5)
    for i in range(36):
        x = float(rng.choice([rng.uniform(10, 130), rng.uniform(W - 130, W - 10)]))
        y = rng.uniform(120, H - 260)
        col = [(255, 46, 136), (255, 154, 31), (255, 220, 180)][i % 3]
        paste_center(canvas, glow_dot(int(rng.choice([3, 4, 6])), col), x, y, rng.uniform(0.3, 0.75))

    out = os.path.join(ROOT, "out", "gta6_10_trucs_cover.png")
    canvas.convert("RGB").save(out, optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
