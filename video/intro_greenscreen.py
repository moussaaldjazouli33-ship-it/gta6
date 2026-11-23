"""
Exports the animated "GTA 6" intro on a solid chroma-key green (#00FF00), plus an alpha version.
The green-safe title has hard edges (no soft glow/shadow) so a chroma key removes the green cleanly.

    GTA_PROJECT=p4 python video/intro_greenscreen.py
      -> out/gta6_intro_greenscreen.mp4   (1080x1920, 2.3 s, green background)
      -> out/gta6_intro_alpha.mov          (ProRes 4444 with transparency)
"""
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("GTA_PROJECT", "p4")
import overlay  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUR, FPS, W, H = 2.3, 30, 1080, 1920


def frames(green):
    for i in range(int(DUR * FPS)):
        c = Image.new("RGBA", (W, H), (0, 255, 0, 255) if green else (0, 0, 0, 0))
        overlay.draw_title(c, i / FPS, DUR, green_safe=True, cy=H / 2)
        yield c


def main():
    g = os.path.join(ROOT, "out", "gta6_intro_greenscreen.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", g],
                         stdin=subprocess.PIPE)
    for f in frames(True):
        p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    al = os.path.join(ROOT, "out", "gta6_intro_alpha.mov")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", al],
                         stdin=subprocess.PIPE)
    for f in frames(False):
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    print("wrote", g, al)


if __name__ == "__main__":
    main()
