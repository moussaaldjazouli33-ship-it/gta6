"""
Project 2: "10 trucs à savoir avant de jouer" (GTA 6).

Voice-over: footage/voiceover2.mp3 (ElevenLabs "Maxime"), word timings in
production/vo2_words.json (Whisper). Footage: two 16:9 1280x720 videos
  t1.mp4 = launch trailer, t2.mp4 = "Jason meets Lucia" opening scene,
reframed to full-screen 9:16 by video/reframe.py (face tracking).

Shot tuple: (timeline_start, source, source_in, camera, opts)
  opts: "subsafe" -> crop the top 87 % of the frame (t2 has burned-in dialogue
  subtitles at the bottom), "x=0.4" -> framing hint when no face is found.
"""
import json
import os

FPS = 30
W, H = 1080, 1920
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VO_FILE = os.path.join(ROOT, "footage", "voiceover2.mp3")
NAME = "gta6_10_trucs"
PILL_TEXT = "GTA 6"
TITLE_LABEL = ""
XFADE_D = 0.25

with open(os.path.join(ROOT, "production", "vo2_words.json"), encoding="utf-8") as f:
    WORDS = [tuple(w) for w in json.load(f)]
DURATION = 57.39


def _num(n):
    return next(s for t, s, e in WORDS if t.rstrip(".") == str(n) and t.endswith("."))


_B = [0.0, 4.78] + [_num(n) for n in range(1, 10)] + [46.42, 50.82, DURATION]
_meta = [
    ("hook", None, "flash"), ("title", 0, "zoom_punch"),
    ("f1", 1, "whip"), ("f2", 2, "glitch"), ("f3", 3, "whip"), ("f4", 4, "zoom_punch"), ("f5", 5, "flash"),
    ("f6", 6, "spin"), ("f7", 7, "whip"), ("f8", 8, "glitch"), ("f9", 9, "light_leak"), ("f10", 10, "flash"),
    ("cta", 10, "whip"),
]
_sfx = {"hook": [(0.0, "impact")], "title": [(0.0, "whoosh"), (0.1, "ding")], "f10": [(-1.0, "riser"), (0.0, "impact"), (0.02, "ding")],
        "f6": [(0.0, "whoosh"), (0.02, "ding"), (5.0, "riser_short")], "cta": [(0.0, "whoosh")]}
SEGMENTS = []
for i, (sid, counter, tr) in enumerate(_meta):
    SEGMENTS.append(dict(id=sid, start=_B[i], end=_B[i + 1], counter=counter, transition=tr, icons=[],
                         sfx=_sfx.get(sid, [(0.0, "glitch" if tr == "glitch" else "whoosh"), (0.02, "ding")])))

# t1 clean shots (cuts from scene detection): 2.03-4.40 street/"The Keys" | 4.40-6.33 marina aerial |
# 6.33-9.33 Jason polishing a boat | 9.33-11.27 yacht | 11.27-13.57 Jason on the phone | 13.57-14.53 dock |
# 18.33-20.53 lowrider | 20.53-21.8 iguana | 25.73-27.20 Lucia+Jason convertible | 27.20-28.77 swamp crew |
# 28.77-29.7 Jason red light | 32.17-33.00 Jason driving | 33.00-34.43 garage | 34.43-35.83 Lucia vault door |
# 35.83-37.37 bedroom | 37.37-38.37 red room | 38.37-39.80 plane/bike | 39.80-41.70 Jason+Lucia by car |
# 41.70-42.80 neon reach | 46.37-48.27 police cars | 52.33-53.57 explosion | 53.87-54.53 laser |
# 54.53-56.43 beach | 56.43-57.87 gym | 57.87-59.27 couch | 59.27-60.23 club | 60.23-61.07 firefight |
# 61.07-62.53 crew | 62.53-63.40 Lucia sunset | 63.40-64.23 tail lights | 64.23-65.9 gun | 66.43-67.90 balcony couple |
# 67.90-69.30 skyscraper | 71.43-72.13 Jason gun | 72.17-73.17 Lucia shooting
SHOT_LIST = [
    (0.00, "t1", 11.30, "push_in", ""),          # Jason on the phone (broke)
    (2.20, "t1", 25.80, "push_in", ""),          # Lucia + Jason convertible
    (3.60, "t1", 52.36, "crash_zoom", ""),       # explosion
    (4.78, "t1", 4.45, "pull_out", "x=0.5"),     # marina aerial
    (6.52, "t1", 6.40, "push_in", "x=0.82"),           # Jason working on the boat
    (8.70, "t1", 61.10, "hold", ""),             # crew at night
    (10.10, "t1", 72.20, "crash_zoom", "x=0.36"),      # Lucia shooting (braque)
    (11.05, "t1", 71.45, "handheld", "x=0.68"),        # Jason with gun
    (11.70, "t1", 41.75, "push_in", ""),         # neon reach
    (12.08, "t1", 18.40, "push_in", "x=0.45"),   # lowrider (stolen car)
    (14.00, "t2", 23.00, "handheld", "subsafe x=0.55"),   # driving at night (breakdown)
    (15.50, "t1", 46.40, "crash_zoom", "x=0.45 fixed"),        # police chase
    (16.54, "t1", 69.35, "push_in", "x=0.5"),    # night city aerial (EV)
    (17.30, "t1", 32.18, "hold", "x=0.3"),            # Jason driving
    (18.10, "t1", 38.40, "pull_out", "x=0.5"),   # plane / bike
    (18.92, "t2", 12.40, "push_in", "subsafe x=0.5"),  # Lucia breaking into a car
    (20.70, "t2", 14.90, "push_in", "subsafe"),  # Lucia inside (lockpick)
    (22.20, "t1", 27.25, "hold", "x=0.5"),       # swamp crew at sunset
    (23.38, "t1", 35.90, "push_in", ""),         # bedroom (nuits blanches)
    (24.80, "t1", 57.90, "pull_out", "x=0.65"),        # wrecked on the couch
    (26.15, "t2", 190.00, "push_in", "subsafe"), # apartment, Lucia
    (27.60, "t2", 194.00, "hold", "subsafe"),    # couch
    (29.34, "t1", 56.45, "push_in", ""),         # gym (muscu)
    (30.74, "t1", 62.55, "push_in", ""),         # Lucia sunset (cardio)
    (31.60, "t2", 161.80, "pull_out", "x=0.55"), # beach walk
    (33.40, "t1", 67.95, "crash_zoom", "x=0.5"), # skyscraper
    (34.25, "t1", 37.40, "handheld", "x=0.36"),        # red room ("et attends")
    (35.28, "t1", 34.45, "push_in", "x=0.5"),         # Lucia at the vault door (focus)
    (36.65, "t1", 53.90, "crash_zoom", "x=0.5"), # laser
    (37.25, "t1", 28.80, "push_in", "x=0.6"),         # red light (red door)
    (38.10, "t1", 64.30, "hold", "x=0.55"),            # gun in the teal room
    (39.60, "t1", 60.25, "handheld", "x=0.42"),        # firefight (braquage)
    (40.46, "t1", 2.10, "push_in", "x=0.75"),     # street (dogs)
    (41.90, "t1", 54.60, "pull_out", "x=0.5"),   # beach crowd
    (43.38, "t2", 39.20, "push_in", "subsafe"),  # hands up, police
    (45.00, "t2", 41.60, "crash_zoom", "subsafe"),
    (46.42, "t1", 20.55, "push_in", "x=0.5"),    # iguana (gross)
    (47.50, "t1", 13.60, "hold", ""),            # dock
    (48.40, "t2", 170.10, "push_in", "subsafe"), # bar crowd (throw at people)
    (50.00, "t1", 59.30, "handheld", "x=0.45"),        # club
    (50.82, "t1", 39.85, "push_in", ""),         # Jason + Lucia by the car
    (52.60, "t1", 66.50, "pull_out", "x=0.6"),        # balcony couple
    (53.95, "t2", 124.00, "push_in", "subsafe"), # Jason close-up
    (55.50, "t2", 128.00, "push_in", "subsafe"), # Lucia close-up
]

# Logos, title cards, "ROCKSTAR GAMES PRESENTS", credits overlays, animal credit cards, end cards.
BANNED = {
    "t1": [(0.0, 2.0), (14.5, 18.35), (21.85, 25.75), (75.9, 99.0)],
    "t2": [(0.0, 3.3), (16.5, 22.8), (36.5, 38.97), (58.5, 60.0), (64.8, 70.6), (76.6, 78.9), (94.8, 96.9),
           (110.8, 117.0), (138.6, 142.6), (160.4, 161.75), (164.95, 170.0), (172.95, 181.6), (184.4, 186.0),
           (186.6, 189.2), (196.6, 999.0)],
}


def all_shots():
    out = []
    for i, (t0, src, sin, cam, opts) in enumerate(SHOT_LIST):
        t1 = SHOT_LIST[i + 1][0] if i + 1 < len(SHOT_LIST) else DURATION
        seg = next(s for s in SEGMENTS if s["start"] <= t0 < s["end"])
        last_in_seg = t1 >= seg["end"] - 1e-6 and seg is not SEGMENTS[-1]
        src_out = sin + (t1 - t0) + (XFADE_D if last_in_seg else 0)
        for b0, b1 in BANNED[src]:
            if sin < b1 and src_out > b0:
                raise ValueError(f"shot {i + 1} uses {src} {sin:.2f}-{src_out:.2f}s, overlapping banned {b0}-{b1}")
        hint = 0.5
        for o in opts.split():
            if o.startswith("x="):
                hint = float(o[2:])
        out.append(dict(id=f"s{i + 1:02d}", seg=seg["id"], start=t0, end=t1, src=src, src_in=sin, cam=cam,
                        flip=False, badge=False, reframe=True, subsafe="subsafe" in opts, hint=hint,
                        fixed="fixed" in opts))
    return out


# ------------------------------------------------------------------ decorative FX (edges only, no words)
def at(word, after=0.0):
    key = word.lower().strip(".,?!")
    for t, s, e in WORDS:
        tok = t.lower().strip(".,?!")
        if s >= after - 1e-6 and (tok == key or tok.split("'")[-1] == key):
            return s
    raise KeyError(word)


def _fx():
    S = {s["id"]: s["start"] for s in SEGMENTS}
    fx = []

    def icon(word, name, after=0.0, dur=1.8):
        fx.append(dict(t=at(word, after), kind="icon", dur=dur, name=name))

    def stars(word, n, after=0.0, dur=1.8, lose=False):
        fx.append(dict(t=at(word, after), kind="stars", dur=dur, n=n, lose=lose))

    icon("fauché,", "cash")
    icon("histoire,", "flame")
    icon("10", "controller")
    icon("argent", "cash", S["f1"])
    icon("braque,", "gun", S["f1"])
    icon("vol,", "car", S["f1"], 1.4)
    icon("voiture", "car", S["f2"])
    icon("essence", "fuel", S["f2"])
    stars("poursuite.", 3, S["f2"], 1.4)
    icon("électriques", "bolt", S["f3"])
    icon("vitre,", "gun", S["f4"], 1.3)
    icon("alarme", "alarm", S["f4"], 1.6)
    icon("crochetage,", "lock", S["f4"])
    icon("nuits", "moon", S["f5"])
    icon("détruit,", "skull", S["f5"], 1.6)
    icon("santé.", "heart", S["f5"])
    icon("muscu", "dumbbell", S["f6"])
    icon("cardio", "heart", S["f6"])
    icon("focus,", "eye", S["f7"])
    icon("porte", "door", S["f7"])
    icon("alarme", "alarm", S["f7"])
    icon("braquage.", "cash", S["f7"], 1.0)
    icon("chiens", "paw", S["f8"])
    icon("profil", "scan", S["f8"])
    stars("police", 3, S["f9"], 2.4)
    icon("chiens", "paw", S["f9"])
    icon("dégueu,", "flame", S["f10"])
    icon("chiens", "paw", S["f10"])
    icon("commentaire", "comment", S["cta"])
    icon("Envoie", "share", S["cta"])
    icon("abonne-toi", "controller", S["cta"])
    fx.sort(key=lambda e: e["t"])
    kept = []
    for e in fx:   # at most 2 icons at once, never the same twice
        if e["kind"] == "icon":
            live = [k for k in kept if k["kind"] == "icon" and k["t"] <= e["t"] < k["t"] + k["dur"]]
            if len(live) >= 2 or any(k["name"] == e["name"] for k in live):
                continue
        kept.append(e)
    return kept


FX = _fx()
