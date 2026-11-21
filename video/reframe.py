"""
Quality-first 16:9 -> 9:16 reframing for one shot.

Framing (per shot, set by the editor after reviewing every shot, see projects/p2.py):
  cx  horizontal centre of the subject (0..1 of the source width)
  w   width of the source that must stay visible (0..1). Faces, bodies, both
      characters of a two-shot, or the main action.
      w <= 0.33 -> FULL CROP: a 9:16 window of the full source height.
      w  > 0.33 -> EXTENDED: that wider window is shown sharp in the middle of
                   the frame over a cinematic blurred extension of the same shot,
                   so nothing important is cut and nothing is over-zoomed.
  track       -> body + face tracking (OpenCV HOG people detector + Haar faces)
                 may refine cx by up to +/-6 % when it finds the subject reliably.

Image chain: ffmpeg decode with light temporal denoise (hqdn3d) -> sub-pixel
bicubic crop -> ESRGAN-slim x2 super-resolution (ONNX, CPU) -> gentle unsharp.
Camera moves are kept small (max ~4 % zoom) to avoid soft, pixelated faces.
"subsafe" (t2) drops the bottom 13 % (burned-in dialogue subtitles) and, for
wide windows, the top 5 % (channel watermark).
"""
import math
import os
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageFilter

SW, SH = 1280, 720
W, H = 1080, 1920
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
SR_MODEL = os.path.join(HERE, "models", "esrgan_slim_x2.onnx")
cv2.setNumThreads(1)
_FRONT = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_PROF = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
_HOG = cv2.HOGDescriptor()
_HOG.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
_SESS = None


def _sr(img):
    """ESRGAN-slim x2 on an RGB uint8 PIL image."""
    global _SESS
    if _SESS is None:
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        _SESS = ort.InferenceSession(SR_MODEL, so, providers=["CPUExecutionProvider"])
    a = np.asarray(img, np.float32)
    h, w = a.shape[:2]
    T, P = 320, 12                                   # tiles with overlap keep memory low
    out = np.zeros((h * 2, w * 2, 3), np.float32)
    for y0 in range(0, h, T):
        for x0 in range(0, w, T):
            ya, xa = max(0, y0 - P), max(0, x0 - P)
            yb, xb = min(h, y0 + T + P), min(w, x0 + T + P)
            x = a[ya:yb, xa:xb].transpose(2, 0, 1)[None]
            y = _SESS.run(None, {"input": np.ascontiguousarray(x)})[0][0].transpose(1, 2, 0)
            cy, cx = (y0 - ya) * 2, (x0 - xa) * 2
            th, tw = (min(h, y0 + T) - y0) * 2, (min(w, x0 + T) - x0) * 2
            out[y0 * 2:y0 * 2 + th, x0 * 2:x0 * 2 + tw] = y[cy:cy + th, cx:cx + tw]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))


def decode(path, start, n):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-ss", f"{start}", "-i", path, "-frames:v", str(n),
                                   "-vf", f"fps={FPS},scale={SW}:{SH},hqdn3d=1.5:1.2:4:3", "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-"])
    frames = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
    if len(frames) < n:
        raise RuntimeError(f"{path}: only {len(frames)} of {n} frames from {start}s")
    return frames


def _subjects(rgb, max_y):
    """Centres (x, weight) of faces and full bodies, at source scale."""
    small = cv2.resize(rgb, (640, 360))
    g = cv2.equalizeHist(cv2.cvtColor(small, cv2.COLOR_RGB2GRAY))
    out = []
    for det, flip in ((_FRONT, False), (_PROF, False), (_PROF, True)):
        gg = cv2.flip(g, 1) if flip else g
        for x, y, w, h in det.detectMultiScale(gg, 1.1, 6, minSize=(30, 30)):
            if flip:
                x = 640 - x - w
            if (y + h / 2) * 2 < max_y:
                out.append(((x + w / 2) * 2, w * 2 * 1.5))
    bodies, _ = _HOG.detectMultiScale(cv2.cvtColor(small, cv2.COLOR_RGB2GRAY), winStride=(8, 8), padding=(8, 8), scale=1.06)
    for x, y, w, h in bodies:
        out.append(((x + w / 2) * 2, w * 2))
    return out


def refine(frames, cx_px, max_y):
    """Track faces + bodies near the editor's centre; return a smooth path (or None if unreliable)."""
    n, step = len(frames), 3
    lim = 0.06 * SW
    xs, hits = [], 0
    for i in range(0, n, step):
        cand = [(x, wt) for x, wt in _subjects(frames[i], max_y) if abs(x - cx_px) < 2.2 * lim]
        if cand:
            tot = sum(wt for _, wt in cand)
            xs.append(sum(x * wt for x, wt in cand) / tot)
            hits += 1
        else:
            xs.append(np.nan)
    if hits < 0.5 * len(xs):
        return None
    xs = np.array(xs)
    good = ~np.isnan(xs)
    xs = np.interp(np.arange(len(xs)), np.flatnonzero(good), xs[good])
    xs = np.array([np.median(xs[max(0, i - 2):i + 3]) for i in range(len(xs))])
    r = np.arange(-8, 9)
    g = np.exp(-(r / 3.0) ** 2 / 2)
    xs = np.convolve(np.pad(xs, 8, mode="edge"), g / g.sum(), mode="valid")
    xs = np.clip(xs, cx_px - lim, cx_px + lim)
    return np.interp(np.arange(n), np.arange(0, n, step)[:len(xs)], xs)


def zoom_at(cam, i, n, punch):
    p = i / max(1, n - 1)
    z = {"push_in": 1.0 + 0.035 * p, "pull_out": 1.035 - 0.035 * p, "crash_zoom": 1.0 + 0.05 * min(1, i / 9),
         "handheld": 1.015, "hold": 1.0 + 0.012 * p}.get(cam, 1.01)
    if punch:
        z *= 1 + 0.025 * max(0, 1 - i / 7.5)
    dx = dy = 0.0
    if cam == "handheld":
        dx, dy = 3 * math.sin(i / 5), 2.5 * math.sin(i / 4 + 1)
    return z, dx, dy


def _bg(frame, cx):
    """Cinematic extension: the same shot, cover-scaled, heavily blurred, darkened, warm-tinted."""
    s = H / SH
    cw = W / s
    x0 = float(np.clip(cx - cw / 2, 0, SW - cw))
    small = Image.fromarray(frame).crop((int(x0), 0, int(x0 + cw), SH)).resize((90, 160), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(4))
    a = np.asarray(small.resize((W, H), Image.BICUBIC), np.float32)
    lum = a.mean(-1, keepdims=True)
    a = lum + (a - lum) * 1.35                     # keep the colours of the shot alive
    a = a * 0.78 + np.array([10, 2, 12])
    yy = np.linspace(-1, 1, H)[:, None]
    a *= (1 - 0.18 * yy ** 4)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


_FEATHER = {}


def _feather(h):
    if h not in _FEATHER:
        m = np.ones((h, 1), np.float32)
        f = min(70, h // 6)
        m[:f, 0] = np.linspace(0, 1, f) ** 1.5
        m[-f:, 0] = np.linspace(1, 0, f) ** 1.5
        _FEATHER[h] = Image.fromarray((np.repeat(m, W, 1) * 255).astype(np.uint8))
    return _FEATHER[h]


def render(path, start, n, cam, punch, out_path, cx=0.5, w=0.32, subsafe=False, track=False, flip=False):
    frames = decode(path, start, n)
    if flip:
        frames = np.ascontiguousarray(frames[:, :, ::-1])
    extended = w > 0.33
    top0 = 0.05 * SH if (subsafe and extended) else 0.0
    bot = 0.87 * SH if subsafe else SH
    avail_h = bot - top0
    if extended:
        base_w, base_h = min(w * SW, SW), avail_h
    else:
        base_h = avail_h
        base_w = base_h * W / H
    cx_px = cx * SW
    path_x = refine(frames, cx_px, bot * 0.9) if track else None
    xs = path_x if path_x is not None else np.full(n, cx_px)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-vf", "eq=contrast=1.05:saturation=1.10,format=yuv420p",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "15", out_path], stdin=subprocess.PIPE)
    for i in range(n):
        z, dx, dy = zoom_at(cam, i, n, punch)
        cw, ch = base_w / z, base_h / z
        x = float(np.clip(xs[i] + dx, cw / 2, SW - cw / 2))
        top = float(np.clip(top0 + (base_h - ch) * 0.4 + dy, top0, bot - ch))
        im = Image.fromarray(frames[i])
        if not extended:
            win = im.transform((540, 960), Image.AFFINE, (cw / 540, 0, x - cw / 2, 0, ch / 960, top), resample=Image.BICUBIC)
            out = _sr(win)
        else:
            fgh = int(round(W * ch / cw)) // 2 * 2
            if cw >= 540:      # enough native pixels: super-resolve the native window, then downscale (max detail)
                nw, nh = int(round(cw)), int(round(ch))
                win = im.transform((nw, nh), Image.AFFINE, (cw / nw, 0, x - cw / 2, 0, ch / nh, top), resample=Image.BICUBIC)
                fg = _sr(win).resize((W, fgh), Image.LANCZOS)
            else:
                fh = fgh // 2
                win = im.transform((540, fh), Image.AFFINE, (cw / 540, 0, x - cw / 2, 0, ch / fh, top), resample=Image.BICUBIC)
                fg = _sr(win)
            out = _bg(frames[i], x)
            y0 = int((H - fg.height) * 0.46)
            out.paste(fg, (0, y0), _feather(fg.height))
        out = out.filter(ImageFilter.UnsharpMask(radius=1.4, percent=45, threshold=2))
        enc.stdin.write(out.tobytes())
    enc.stdin.close()
    enc.wait()
    return 1.0 if path_x is not None else 0.0
