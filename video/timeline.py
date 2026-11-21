"""
Edit decision list for the French voice-over version:
"10 DÉTAILS QUE PERSONNE NE CONNAÎT" (GTA 6).

Driven by the real voice-over (footage/voiceover.mp3). Word timings come from
production/vo_words.json (Whisper transcription with word timestamps, spelling
corrected by hand). Every segment boundary sits on the spoken number word.

Footage = the real GTA 6 clips supplied by the user (footage/c1..c5.mp4,
already 1080x1920). No generated imagery anywhere.

Shot tuple: (timeline_start, source, source_in, camera, opts)
  opts: "flip" (mirror a reused clip), "badge" (crop away the ESRB corner badge,
  anchors the zoom to the top-right)
"""
import json
import os

FPS = 30
W, H = 1080, 1920
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO_FILE = os.path.join(ROOT, "footage", "voiceover.mp3")

with open(os.path.join(ROOT, "production", "vo_words.json"), encoding="utf-8") as f:
    WORDS = [tuple(w) for w in json.load(f)]   # (text, start, end)
WORDS = [("fuite," if w[0] == "fuite" else w[0], w[1], w[2]) for w in WORDS]

DURATION = 69.56
PILL_TEXT = "DÉTAILS QUE PERSONNE NE CONNAÎT"
TITLE_LABEL = "DÉTAILS"


def _num_time(n):
    return next(s for t, s, e in WORDS if t == f"{n}.")


# segment boundaries = spoken numbers
_B = [0.0, 3.95] + [_num_time(n) for n in range(1, 11)] + [62.22, DURATION]

SEGMENTS = []
_meta = [
    ("hook", None, "flash", [], [(0.0, "impact")]),
    ("title", 0, "zoom_punch", [], [(0.0, "whoosh"), (0.1, "ding")]),
    ("f1", 1, "whip", [(0.6, "comment")], [(0.0, "whoosh"), (0.02, "ding")]),
    ("f2", 2, "glitch", [(0.6, "slots")], [(0.0, "glitch"), (0.02, "ding")]),
    ("f3", 3, "whip", [(0.6, "eye")], [(0.0, "whoosh"), (0.02, "ding")]),
    ("f4", 4, "zoom_punch", [(0.9, "duo")], [(0.0, "boom"), (0.02, "ding")]),
    ("f5", 5, "flash", [(2.4, "scan")], [(0.0, "impact"), (0.02, "ding")]),
    ("f6", 6, "spin", [(3.1, "cash")], [(0.0, "whoosh"), (0.02, "ding"), (3.15, "cash"), (5.55, "riser_short")]),
    ("f7", 7, "whip", [(1.0, "alarm")], [(0.0, "whoosh"), (0.02, "ding")]),
    ("f8", 8, "glitch", [(2.3, "slots")], [(0.0, "glitch"), (0.02, "ding")]),
    ("f9", 9, "light_leak", [(1.3, "pin")], [(0.0, "riser_short"), (0.02, "ding")]),
    ("f10", 10, "flash", [(1.6, "flame")], [(-1.0, "riser"), (0.0, "impact"), (0.02, "ding"), (2.2, "boom")]),
    ("cta", 10, "whip", [(2.1, "comment"), (3.0, "share")], [(0.0, "whoosh"), (2.1, "pop"), (3.0, "swoosh_up")]),
]
for i, (sid, counter, tr, icons, sfx) in enumerate(_meta):
    SEGMENTS.append(dict(id=sid, start=_B[i], end=_B[i + 1], counter=counter, transition=tr,
                         icons=[(t, n, "side") for t, n in icons], sfx=sfx))

# ------------------------------------------------------------------ shots
# Clean source ranges (no logo / end card): c1 is a fast-cut trailer:
#  2.0-4.5 neon club | 4.6-5.9 racer at pier | 8.4-9.4 man in bucket hat | 9.5-10.5 tank top
#  10.6-11.9 truck on boat | 12.0-13.4 DJ | 13.5-14.9 night crew at fence | 16.95-17.85 shades guy
#  17.95-18.9 neon street drive | 19.0-20.8 club dancer
# c2 0-3.6 Lucia in elevator* | 4-9 Jason elevator | 9.5-16 couple walking | 16-41 rooftop bar
# c3 0-16.5 street shootout vs police* | c4 0-3.6 scooter street* | 3.7-6.7 airboat* | 6.8-9.8 cap guy
#  9.9-12.4 underwater | 12.5-15.9 Lucia gym | c5 0-9.3 Lucia skydive / parachute*
# (* ESRB corner badge in the first seconds -> "badge" crop)
SHOT_LIST = [
    # hook: Lucia / couple / "au fond du trou"
    (0.00, "c2", 0.2, "push_in", "badge"),
    (1.70, "c2", 12.5, "pan_r", ""),
    (2.85, "c4", 10.2, "push_in", ""),
    # title
    (3.95, "c5", 1.6, "pull_out", "badge"),
    (5.45, "c1", 17.95, "push_in", ""),
    (6.40, "c1", 12.1, "crash_zoom", ""),
    # 1 relationship
    (6.98, "c1", 2.1, "push_in", ""),
    (9.30, "c2", 5.0, "pan_l", ""),
    (11.50, "c2", 26.0, "pull_out", ""),
    # 2 Lucia drives, Jason shoots
    (13.96, "c3", 4.5, "crash_zoom", ""),
    (15.90, "c3", 9.6, "handheld", ""),
    (17.60, "c1", 10.6, "push_in", ""),
    # 3 gun in the street
    (19.00, "c3", 12.2, "handheld", ""),
    (21.00, "c2", 21.5, "pan_r", ""),
    # 4 hand-to-hand
    (23.02, "c4", 12.6, "push_in", ""),
    (25.40, "c2", 7.2, "push_in", ""),
    (27.50, "c1", 9.45, "crash_zoom", ""),
    (28.50, "c1", 8.4, "push_in", ""),
    # 5 cap / glasses
    (29.52, "c1", 16.95, "push_in", ""),
    (30.42, "c4", 6.9, "pan_l", ""),
    (32.70, "c2", 34.0, "push_in", ""),
    # 6 store robbery
    (34.98, "c3", 0.3, "push_in", "badge"),
    (36.60, "c1", 13.5, "push_in", ""),
    (38.00, "c3", 6.5, "crash_zoom", ""),
    (40.50, "c1", 4.6, "pan_r", ""),
    # 7 clothes in the trunk / lose the cops
    (41.76, "c2", 18.0, "pan_l", ""),
    (43.90, "c3", 14.3, "handheld", ""),
    # 8 arrested / weapons
    (45.96, "c3", 2.0, "push_in", "badge"),
    (48.20, "c3", 11.3, "handheld", ""),
    (49.10, "c1", 19.0, "push_in", ""),
    (50.90, "c2", 4.0, "pull_out", ""),
    # 9 car delivered, valet leaves on a scooter
    (52.72, "c4", 4.0, "pan_r", "badge"),
    (54.30, "c4", 0.3, "push_in", "badge"),
    # 10 NPC robberies
    (56.62, "c1", 13.5, "crash_zoom", "flip"),
    (58.10, "c3", 9.0, "handheld", "flip"),
    (60.20, "c3", 6.8, "push_in", "flip"),
    # outro
    (62.22, "c2", 6.0, "push_in", ""),
    (63.30, "c2", 2.0, "push_in", "badge"),
    (64.90, "c5", 3.4, "pull_out", "badge"),
    (67.20, "c5", 6.0, "push_in", "badge"),
]


def all_shots():
    out = []
    for i, (t0, src, sin, cam, opts) in enumerate(SHOT_LIST):
        t1 = SHOT_LIST[i + 1][0] if i + 1 < len(SHOT_LIST) else DURATION
        seg = next(s for s in SEGMENTS if s["start"] <= t0 < s["end"])
        out.append(dict(id=f"s{i + 1:02d}", seg=seg["id"], start=t0, end=t1, src=src, src_in=sin,
                        cam=cam, flip="flip" in opts, badge="badge" in opts))
    return out


def all_captions():
    """Word-by-word chunks (<=3 words, break on punctuation). Spoken numbers become '#n'."""
    chunks, cur = [], []

    def flush():
        if cur:
            chunks.append(list(cur))
            cur.clear()

    for w in WORDS:
        txt = w[0]
        if txt.rstrip(".").isdigit() and txt.endswith("."):
            flush()
            chunks.append([("#" + txt[:-1], w[1], w[2])])
            continue
        cur.append(w)
        if txt[-1] in ".,?!" or len(cur) == 3 or sum(len(x[0]) for x in cur) > 15:
            flush()
    flush()
    out = []
    for i, ch in enumerate(chunks):
        start = ch[0][1]
        nxt = chunks[i + 1][0][1] if i + 1 < len(chunks) else DURATION
        end = min(nxt, ch[-1][2] + 0.7)
        out.append(dict(start=start, end=end, words=[(t.upper(), s, e) for t, s, e in ch],
                        text=" ".join(t.upper() for t, _, _ in ch)))
    return out
