"""
TikTok cover for project p3 ("20 000 $ dès le début : 3 spots").
Hero frame = Jason at the open safe from the user's own clip (m3 @ 12.35 s), cleaned of
the MP logo / captions with clean_text.py. Graphics reuse the video identity: gold
$20,000 badge (coin + bills), pink/orange numbered badges.

    python video/cover3.py        # out/gta6_3_spots_cover.png
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("GTA_PROJECT", "p3")
import clean_text  # noqa: E402
from cover import text_sprite  # noqa: E402
from overlay import (F_MONT, ORANGE, PINK, W, H, coin_and_bills_sprite, font, glow_dot, gold_glow,  # noqa: E402
                     gradient_img, money_text_sprite, num_badge_sprite, paste_center)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-ss", "12.35", "-i", os.path.join(ROOT, "footage", "m3.mov"),
                                   "-frames:v", "1", "-vf", "hqdn3d=1.2:1.0:3:2.5", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    src = clean_text.clean(np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy())
    im = Image.fromarray(src)
    # slight push-in toward the safe, keeps the corner where the logo was out of frame
    z = 1.06
    cw, ch = W / z, H / z
    im = im.crop((int((W - cw) * 0.55), int((H - ch) * 0.6), int((W - cw) * 0.55 + cw), int((H - ch) * 0.6 + ch))).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(1.12).filter(ImageFilter.UnsharpMask(1.4, 40, 2))
    canvas = im.convert("RGBA")

    # darken the title zone + warm gold light from the safe
    a = np.zeros((H, 1), np.float32)
    a[:820, 0] = np.linspace(0.78, 0.0, 820) ** 1.2
    a[H - 330:, 0] = np.linspace(0.0, 0.6, 330)
    shade = Image.new("RGBA", (W, H), (12, 4, 18, 0))
    shade.putalpha(Image.fromarray((np.repeat(a, W, 1) * 255).astype(np.uint8)))
    canvas.alpha_composite(shade)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - np.sqrt(((xx - 700) / W) ** 2 + ((yy - 1050) / H) ** 2) * 3.0, 0, 1) ** 2
    warm = Image.new("RGBA", (W, H), (255, 190, 80, 0))
    warm.putalpha(Image.fromarray((g * 70).astype(np.uint8)))
    canvas.alpha_composite(warm)

    # "GTA 6" pill
    pill = Image.new("RGBA", (190, 62), (0, 0, 0, 0))
    pm = Image.new("L", pill.size, 0)
    ImageDraw.Draw(pm).rounded_rectangle([0, 0, 189, 61], 30, fill=255)
    pill.paste(gradient_img(190, 62, PINK, ORANGE, horizontal=True), (0, 0), pm)
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([4, 4, 185, 57], 26, fill=(14, 6, 22, 235))
    pd.text((95, 32), "GTA 6", font=font(F_MONT, 30), anchor="mm", fill="white")
    paste_center(canvas, pill, W / 2, 150)

    # big gold $20,000 with coin + bills (same design as the video animation)
    coin = coin_and_bills_sprite().resize((250, 250), Image.LANCZOS)
    txt = money_text_sprite("$20,000")
    txt = txt.resize((int(txt.width * 1.45), int(txt.height * 1.45)), Image.LANCZOS)
    gw = coin.width - 40 + txt.width
    group = Image.new("RGBA", (gw, max(coin.height, txt.height)), (0, 0, 0, 0))
    group.alpha_composite(coin, (0, (group.height - coin.height) // 2))
    group.alpha_composite(txt, (coin.width - 40, (group.height - txt.height) // 2 + 8))
    if group.width > 1000:
        group = group.resize((1000, int(group.height * 1000 / group.width)), Image.LANCZOS)
    paste_center(canvas, gold_glow(group.width + 260, group.height + 220), W / 2, 330, 0.9)
    paste_center(canvas, group, W / 2, 330)
    paste_center(canvas, text_sprite("DÈS LE DÉBUT DU JEU", 84), W / 2, 495)

    # numbered badges = the 3 spots (bottom, above TikTok's caption area)
    for i, x in enumerate((W / 2 - 190, W / 2, W / 2 + 190)):
        paste_center(canvas, num_badge_sprite(i + 1).resize((132, 132), Image.LANCZOS), x, 1432)
    rng = np.random.default_rng(9)
    for i in range(30):
        x = float(rng.choice([rng.uniform(10, 130), rng.uniform(W - 130, W - 10)]))
        y = rng.uniform(120, H - 260)
        col = [(255, 210, 90), (255, 154, 31), (255, 240, 200)][i % 3]
        paste_center(canvas, glow_dot(int(rng.choice([3, 4, 6])), col), x, y, rng.uniform(0.3, 0.8))

    out = os.path.join(ROOT, "out", "gta6_3_spots_cover.png")
    canvas.convert("RGB").save(out, optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
