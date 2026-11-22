"""
Removes burned-in text from the user's own vertical clips (footage/m*.mov):
  - the "MP" channel logo (fixed position, top-right),
  - the word-by-word caption line (~73 % of the height),
  - small in-game dialogue subtitles near the bottom.
Only text-shaped white components are masked (glyph-sized connected components
fully inside the text band), then filled from the surrounding image with
OpenCV inpainting (Telea). No black boxes; shirts and shoes are not touched.
"""
import cv2
import numpy as np

LOGO_BOX = (830, 95, 1015, 205)            # x0, y0, x1, y1
BANDS = [  # (y0, y1, max glyph height, white threshold, dilation)
    (1385, 1490, 80, 205, 15),             # creator caption line
    (1712, 1782, 34, 190, 7),              # in-game dialogue subtitles
]


def text_mask(rgb):
    h, w = rgb.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    mn = rgb.min(axis=2)
    # logo
    x0, y0, x1, y1 = LOGO_BOX
    m = (mn[y0:y1, x0:x1] > 200).astype(np.uint8) * 255
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19)))
    mask[y0:y1, x0:x1] = np.maximum(m, np.roll(np.roll(m, 6, 0), 5, 1))     # include the drop shadow
    for b0, b1, gh, thr, dil in BANDS:
        e0, e1 = max(0, b0 - 70), min(h, b1 + 70)
        white = (mn[e0:e1] > thr).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(white, 8)
        keep = np.zeros_like(white)
        for i in range(1, n):
            x, y, ww, hh, area = st[i]
            top, bot = y + e0, y + hh + e0
            if top >= b0 and bot <= b1 and 4 <= hh <= gh and ww <= 2.2 * gh and area >= 12:
                keep[lab == i] = 1
        if keep.any():
            # keep only components that line up like a text line (>= 2 glyphs in the band)
            k = cv2.dilate(keep * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dil * 2 + 1, dil * 2 + 1)))
            k = np.maximum(k, np.roll(np.roll(k, dil // 2 + 2, 0), dil // 3 + 1, 1))   # soft drop shadow
            mask[e0:e1] = np.maximum(mask[e0:e1], k)
    return mask


def clean(rgb):
    mask = text_mask(rgb)
    if not mask.any():
        return rgb
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    out = cv2.inpaint(bgr, mask, 9, cv2.INPAINT_TELEA)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
