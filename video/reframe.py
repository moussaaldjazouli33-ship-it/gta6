"""
Intelligent 16:9 -> 9:16 reframing for one shot.

1. Decode the shot's source frames (1280x720).
2. Detect faces every 2nd frame (OpenCV Haar: frontal + left/right profile,
   on a histogram-equalised 640x360 copy). No external model download.
3. Pick the subject per sample: the face that best continues the previous
   target (size x proximity), or the midpoint of two faces when both fit in
   the vertical window. Samples with no face hold the last target, and a shot
   with no face at all uses its framing hint.
4. Smooth the path (median, then Gaussian, then a speed limit) so the virtual
   camera glides instead of jumping.
5. Render each frame with a sub-pixel affine crop (bicubic) to 1080x1920,
   plus the shot's camera move (push-in, pull-out, crash zoom, handheld),
   then a light unsharp mask. Never stretched, never letterboxed.

"subsafe" shots use only the top 87 % of the frame, so burned-in dialogue
subtitles at the bottom of the source stay out of the picture.
"""
import math
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageFilter

SW, SH = 1280, 720
W, H = 1080, 1920
FPS = 30
cv2.setNumThreads(1)
_FRONT = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_PROF = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")


def decode(path, start, n):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-ss", f"{start}", "-i", path, "-frames:v", str(n),
                                   "-vf", f"fps={FPS},scale={SW}:{SH}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    frames = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
    if len(frames) < n:
        raise RuntimeError(f"{path}: only {len(frames)} of {n} frames from {start}s")
    return frames


def _faces(rgb, max_y):
    g = cv2.equalizeHist(cv2.cvtColor(cv2.resize(rgb, (640, 360)), cv2.COLOR_RGB2GRAY))
    boxes = []
    for b in _FRONT.detectMultiScale(g, 1.1, 6, minSize=(30, 30)):
        boxes.append(tuple(int(v) for v in b))
    for b in _PROF.detectMultiScale(g, 1.1, 6, minSize=(30, 30)):
        boxes.append(tuple(int(v) for v in b))
    for x, y, w, h in _PROF.detectMultiScale(cv2.flip(g, 1), 1.1, 6, minSize=(30, 30)):
        boxes.append((int(640 - x - w), int(y), int(w), int(h)))
    out = []
    for x, y, w, h in sorted(boxes, key=lambda b: -b[2]):      # merge overlaps
        cx, cy = (x + w / 2) * 2, (y + h / 2) * 2
        if cy > max_y:
            continue
        if any(abs(cx - o[0]) < max(w, o[2] / 2) and abs(cy - o[1]) < max(h, o[2] / 2) for o in out):
            continue
        out.append((cx, cy, w * 2))
    return out


def track(frames, hint, win_w, max_y):
    n = len(frames)
    step = 2
    xs, have = [], []
    prev = None
    for i in range(0, n, step):
        faces = _faces(frames[i], max_y)
        if faces:
            if prev is None:
                pick = max(faces, key=lambda f: f[2] * math.exp(-((f[0] - hint * SW) / 500) ** 2))
            else:
                pick = max(faces, key=lambda f: f[2] * math.exp(-((f[0] - prev) / 220) ** 2))
            x = pick[0]
            others = [f for f in faces if f is not pick and abs(f[0] - pick[0]) < win_w * 0.75 and f[2] > pick[2] * 0.6]
            if others:                                       # two people fit: frame both
                x = (pick[0] + others[0][0]) / 2
            prev = x
            xs.append(x)
            have.append(True)
        else:
            xs.append(prev if prev is not None else np.nan)
            have.append(False)
    xs = np.array(xs, float)
    if np.all(np.isnan(xs)):
        return np.full(n, hint * SW), 0.0
    first = xs[~np.isnan(xs)][0]
    xs[np.isnan(xs)] = first
    k = 3                                                   # median filter (kills single false detections)
    xm = np.array([np.median(xs[max(0, i - k):i + k + 1]) for i in range(len(xs))])
    sig = 4.0                                               # gaussian (~0.27 s)
    r = np.arange(-12, 13)
    g = np.exp(-(r / sig) ** 2 / 2)
    g /= g.sum()
    pad = np.pad(xm, 12, mode="edge")
    xs_s = np.convolve(pad, g, mode="valid")
    vmax = 9.0 * step                                       # px per sample (~135 px/s at source scale)
    for i in range(1, len(xs_s)):
        xs_s[i] = xs_s[i - 1] + np.clip(xs_s[i] - xs_s[i - 1], -vmax, vmax)
    full = np.interp(np.arange(n), np.arange(0, n, step)[:len(xs_s)], xs_s)
    return full, float(np.mean(have))


def zoom_at(cam, i, n, punch):
    p = i / max(1, n - 1)
    z = {"push_in": 1.0 + 0.08 * p, "pull_out": 1.09 - 0.08 * p, "crash_zoom": 1.0 + 0.14 * min(1, i / 9),
         "handheld": 1.04, "hold": 1.01 + 0.02 * p}.get(cam, 1.03)
    if punch:
        z *= 1 + 0.07 * max(0, 1 - i / 7.5)
    dx = dy = 0.0
    if cam == "handheld":
        dx, dy = 5 * math.sin(i / 4), 4 * math.sin(i / 3 + 1)
    return z, dx, dy


def render(path, start, n, cam, punch, out_path, hint=0.5, subsafe=False, flip=False, fixed=False):
    """Writes the reframed 1080x1920 shot to out_path; returns the share of samples with a tracked face."""
    frames = decode(path, start, n)
    hf = 0.87 if subsafe else 1.0
    base_h = SH * hf
    base_w = base_h * W / H
    xs, cov = track(frames, hint, base_w, max_y=base_h * 0.85)
    if cov < 0.4 or fixed:          # too few faces to trust: use the editor's framing
        xs = np.full(n, hint * SW)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-vf", "eq=contrast=1.05:saturation=1.10,format=yuv420p",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", out_path], stdin=subprocess.PIPE)
    for i in range(n):
        z, dx, dy = zoom_at(cam, i, n, punch)
        ch, cw = base_h / z, base_w / z
        cx = float(np.clip(xs[i] + dx, cw / 2, SW - cw / 2))
        top = 0.0 if subsafe else (SH - ch) * 0.35       # keep faces in the upper third when zooming
        top = float(np.clip(top + dy, 0, SH * hf - ch))
        sx = cw / W
        im = Image.fromarray(frames[i])
        if flip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = im.transform((W, H), Image.AFFINE, (sx, 0, cx - cw / 2, 0, sx, top), resample=Image.BICUBIC)
        im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=75, threshold=2))
        enc.stdin.write(im.tobytes())
    enc.stdin.close()
    enc.wait()
    return cov
