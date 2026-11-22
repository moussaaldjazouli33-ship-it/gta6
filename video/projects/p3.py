"""
Project 3: "3 spots pour 20 000 $ dès le début" (GTA 6).

Voice-over: footage/voiceover3.mp3 (ElevenLabs "Maxime - Young and Casual"),
word timings in production/vo3_words.json.
Footage: the user's own vertical clips footage/m1..m4.mov (cleaned of their
MP logo, burned-in captions and in-game dialogue subtitles by clean_text.py)
plus 16:9 GTA 6 footage t1/t2 reframed to 9:16 (reframe.py).

Shot tuple: (timeline_start, source, source_in, camera, opts)
  m* sources: vertical, cleaned. opts "flip" mirrors a reused clip.
  t* sources: reframed; opts x=/w=/subsafe/track as in project p2.
"""
import json
import os

FPS = 30
W, H = 1080, 1920
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VO_SRC = os.path.join(ROOT, "footage", "voiceover3.mp3")
VO_FILE = os.path.join(ROOT, "footage", "voiceover3_60s.wav")
# Exact 60.00 s: trim only silences (middle of the longest pauses + the tail), never a word.
VO_LEN = 60.734694
CUTS = [(37.87, 38.02), (42.35, 42.45), (43.90, 44.03), (45.53, 45.65), (60.50, VO_LEN)]


def tmap(t):
    """original voice-over time -> edited (60 s) time"""
    d = 0.0
    for a, b in CUTS:
        if t >= b:
            d += b - a
        elif t > a:
            d += t - a
    return t - d


def _build_vo():
    if os.path.exists(VO_FILE) and os.path.getmtime(VO_FILE) > os.path.getmtime(__file__):
        return
    import subprocess
    keep, t = [], 0.0
    for a, b in CUTS:
        keep.append((t, a))
        t = b
    if t < VO_LEN:
        keep.append((t, VO_LEN))
    parts = [f"[0:a]atrim={a}:{b},asetpts=N/SR/TB,afade=t=in:d=0.006,afade=t=out:st={b - a - 0.006:.4f}:d=0.006[p{i}]"
             for i, (a, b) in enumerate(keep)]
    fc = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,atrim=0:60[a]"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", VO_SRC, "-filter_complex", fc, "-map", "[a]",
                           "-ar", "44100", "-ac", "2", VO_FILE])


_build_vo()
NAME = "gta6_3_spots"
PILL_TEXT = "GTA 6"
TITLE_LABEL = ""
STYLE = "p3"            # icons at ~36 % height, bigger counter, numbered badge, no radar
COUNTER_TOTAL = 3
XFADE_D = 0.25
DURATION = 60.0

with open(os.path.join(ROOT, "production", "vo3_words_orig.json"), encoding="utf-8") as f:
    WORDS = [(w[0], tmap(w[1]), tmap(w[2])) for w in json.load(f)]


def _num(n):
    return next(s for t, s, e in WORDS if t == f"{n}.")


_B = [0.0, tmap(4.54), _num(1), _num(2), _num(3), tmap(56.68), DURATION]
_meta = [("hook", None, "flash"), ("title", 0, "zoom_punch"), ("f1", 1, "whip"), ("f2", 2, "glitch"),
         ("f3", 3, "light_leak"), ("cta", 3, "whip")]
_sfx = {"hook": [(0.0, "impact"), (0.9, "cash")], "title": [(0.0, "whoosh"), (0.1, "ding")],
        "f2": [(0.0, "glitch"), (0.02, "ding"), (19.4, "riser_short")], "cta": [(0.0, "whoosh")]}
SEGMENTS = []
for i, (sid, counter, tr) in enumerate(_meta):
    SEGMENTS.append(dict(id=sid, start=_B[i], end=_B[i + 1], counter=counter, transition=tr, icons=[],
                         sfx=_sfx.get(sid, [(0.0, "whoosh"), (0.02, "ding")])))

SHOT_LIST = [
    # hook: money
    (0.00, "m4", 0.20, "push_in", "croptop=0.315"),                 # riding (old cash box reframed out)
    (2.00, "m3", 13.00, "push_in", ""),                # counting the cash
    (3.30, "t1", 52.36, "crash_zoom", "x=0.55"),       # gunman + explosion
    # title
    (4.54, "m1", 11.20, "hold", ""),                   # the map
    # spot 1: the parrot
    (5.66, "m2", 3.00, "push_in", ""),                 # parrot in its cage
    (6.66, "m1", 6.60, "push_in", ""),                 # Shirley on the porch
    (8.70, "m1", 12.00, "hold", ""),                   # map: Three Sheets Liquor
    (9.60, "m1", 14.20, "push_in", ""),                # walking to the back entrance
    (10.52, "m2", 0.00, "handheld", ""),               # taking out the guards
    (11.60, "m2", 9.30, "push_in", ""),                # talking to the parrot
    (12.60, "m3", 0.00, "push_in", ""),                # the yellow generator
    (13.90, "m3", 3.30, "push_in", ""),                # the hidden stash behind it
    (14.80, "m3", 10.20, "push_in", ""),               # the safe in the back room
    # spot 2: the warehouse
    (16.44, "m4", 4.20, "push_in", ""),                # riding to the spot
    (18.20, "m1", 1.20, "pull_out", ""),               # arriving near Hamlet
    (20.00, "t1", 2.10, "push_in", "x=0.40"),          # vehicle parked on the road
    (21.50, "m1", 15.60, "push_in", ""),               # walking to the warehouse gate
    (23.10, "m1", 17.30, "crash_zoom", ""),            # breaking in
    (23.82, "t1", 33.05, "hold", "x=0.38"),            # dark interior
    (25.22, "m3", 13.30, "push_in", "flip"),           # the bag of cash
    (26.60, "t1", 72.20, "crash_zoom", "x=0.32 w=0.50"),  # weapons
    (27.55, "m3", 9.50, "push_in", ""),                # the office safe
    (28.62, "m3", 7.20, "push_in", ""),                # office (collectible card)
    (30.30, "t1", 11.30, "push_in", "x=0.62"),         # Jason on the phone (pawn shop deal)
    (32.00, "t2", 124.00, "push_in", "subsafe x=0.52 track"),  # Jason close-up
    (32.98, "m4", 1.90, "hold", "croptop=0.315"),                   # riding (old cash box reframed out)
    (34.90, "t1", 61.10, "hold", "x=0.45 w=0.70"),     # the crew
    (36.30, "t1", 41.75, "push_in", "x=0.45"),         # neon reach
    (37.20, "t1", 28.80, "push_in", "x=0.58"),         # Jason in red light ("et attends")
    # spot 3: the crab research outpost
    (38.08, "t1", 27.25, "hold", "x=0.50"),            # crew in the swamp at sunset
    (39.50, "t1", 34.45, "push_in", "x=0.45"),         # Lucia at the vault door
    (40.76, "m3", 13.40, "push_in", "flip"),           # the desk / computer
    (42.20, "m3", 11.20, "crash_zoom", "flip"),        # the safe (code)
    (43.66, "t1", 13.60, "hold", "x=0.42"),            # the dock
    (44.50, "t1", 9.40, "push_in", "x=0.50"),          # yacht at the quay
    (45.72, "t1", 64.30, "hold", "x=0.50 w=0.55"),     # gun in the teal room
    (47.20, "m2", 13.20, "push_in", "flip"),           # back with the cash
    (48.70, "t1", 4.45, "pull_out", "x=0.50"),         # BRIAN'S MARINA
    (50.40, "t1", 6.40, "push_in", "x=0.58 w=0.82"),   # Jason working at the marina
    (52.36, "t2", 39.20, "push_in", "subsafe x=0.42 w=0.50"),   # busted: hands up
    (54.00, "t2", 41.60, "crash_zoom", "subsafe x=0.40 w=0.65"),
    (55.26, "t2", 194.00, "hold", "subsafe x=0.58 w=0.45"),    # family savings: the couple at home
    # outro
    (56.68, "m1", 7.60, "push_in", ""),                # Jason with Shirley
    (58.40, "m4", 4.20, "pull_out", "flip"),           # riding away
]

BANNED = {
    "t1": [(0.0, 2.0), (14.5, 18.35), (21.85, 25.75), (75.9, 99.0)],
    "t2": [(0.0, 3.3), (16.5, 22.8), (36.5, 38.97), (58.5, 60.0), (64.8, 70.6), (76.6, 78.9), (94.8, 96.9),
           (110.8, 117.0), (138.6, 142.6), (160.4, 161.75), (164.95, 170.0), (172.95, 181.6), (184.4, 186.0),
           (186.6, 189.2), (196.6, 999.0)],
    "m1": [(19.0, 99.0)], "m2": [(17.0, 99.0)], "m3": [(15.0, 99.0)],
    "m4": [(6.85, 99.0)],                                   # subscribe animation at the end
}


def all_shots():
    out = []
    for i, (t0, src, sin, cam, opts) in enumerate(SHOT_LIST):
        t0 = round(tmap(t0), 4)
        t1 = round(tmap(SHOT_LIST[i + 1][0]), 4) if i + 1 < len(SHOT_LIST) else DURATION
        seg = next(s for s in SEGMENTS if s["start"] <= t0 < s["end"])
        last_in_seg = t1 >= seg["end"] - 1e-6 and seg is not SEGMENTS[-1]
        src_out = sin + (t1 - t0) + (XFADE_D if last_in_seg else 0)
        for b0, b1 in BANNED[src]:
            if sin < b1 and src_out > b0:
                raise ValueError(f"shot {i + 1} uses {src} {sin:.2f}-{src_out:.2f}s, overlapping banned {b0}-{b1}")
        cx, w, bottom = 0.5, 0.32, 0.87
        for o in opts.split():
            if o.startswith("x="):
                cx = float(o[2:])
            if o.startswith("w="):
                w = float(o[2:])
            if o.startswith("bot="):
                bottom = float(o[4:])
        d = dict(id=f"s{i + 1:02d}", seg=seg["id"], start=t0, end=t1, src=src, src_in=sin, cam=cam,
                 flip="flip" in opts, badge=False)
        if src.startswith("m"):
            ct = next((float(o[8:]) for o in opts.split() if o.startswith("croptop=")), 0.0)
            d.update(vertical_clean=True, ext="mov", croptop=ct)
        else:
            d.update(reframe=True, subsafe="subsafe" in opts, cx=cx, w=w, bottom=bottom, track="track" in opts)
        out.append(d)
    return out


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

    def icon(word, name, after=0.0, dur=2.2):
        fx.append(dict(t=at(word, after), kind="icon", dur=dur, name=name))

    fx.append(dict(t=at("20"), kind="money_big", dur=2.45, amount=20000))   # the "$20,000" moment
    icon("spots.", "pin")
    icon("perroquet.", "eye", S["f1"], 2.0)
    icon("Shirley,", "comment", S["f1"], 1.9)
    icon("gardes,", "gun", S["f1"], 1.6)
    icon("générateur", "bolt", S["f1"], 1.6)
    icon("coffre", "lock", S["f1"], 1.6)
    icon("carte,", "pin", S["f2"], 2.0)
    icon("van", "car", S["f2"], 2.0)
    icon("porte.", "door", S["f2"], 1.6)
    icon("billets,", "cash", S["f2"], 1.8)
    icon("armes", "gun", S["f2"], 1.6)
    icon("coffre", "lock", S["f2"], 1.4)
    icon("carte", "scan", 28.6, 1.8)
    icon("6000", "cash", S["f2"], 2.0)
    icon("crabes", "pin", S["f3"], 2.2)
    icon("ordi,", "eye", S["f3"], 1.6)
    icon("coffre", "lock", S["f3"], 1.4)
    icon("porte", "door", S["f3"], 1.4)
    icon("billets", "cash", S["f3"], 2.0)
    icon("garage", "car", S["f3"], 1.8)
    icon("chapitre", "alarm", S["f3"], 2.0)
    icon("épargne", "heart", S["f3"], 1.6)
    icon("commentaire", "comment", S["cta"], 2.0)
    icon("abonne-toi", "share", S["cta"], 2.2)
    fx.sort(key=lambda e: e["t"])
    kept = []
    for e in fx:   # one topic icon at a time, never overlapping
        live = [k for k in kept if k["t"] <= e["t"] < k["t"] + k["dur"] and k["kind"] == "icon"]
        for k in live:
            k["dur"] = max(0.4, e["t"] - k["t"])
        kept.append(e)
    return kept


FX = _fx()
