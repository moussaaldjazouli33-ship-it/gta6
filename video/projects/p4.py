"""
Project 4: "Secret warehouse" (GTA 6), English voice-over.

Voice-over: footage/voiceover4.mp3 (ElevenLabs "Adam"), kept at its full length (68.86 s),
word timings in production/vo4_words.json. Footage: the user's own clean vertical
captures footage/n1..n4.mov (no captions / logo; in-game prompts kept as gameplay).
"""
import json
import os

FPS = 30
W, H = 1080, 1920
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VO_FILE = os.path.join(ROOT, "footage", "voiceover4.mp3")
NAME = "gta6_secret_warehouse"
PILL_TEXT = "GTA 6"
TITLE_LABEL = ""
STYLE = "gta"
COUNTER_TOTAL = 3
XFADE_D = 0.25
DURATION = 68.86

with open(os.path.join(ROOT, "production", "vo4_words.json"), encoding="utf-8") as f:
    WORDS = [tuple(w) for w in json.load(f)]

# segments follow the narration's beats (no numbered list in this script -> no counter)
_meta = [
    ("hook", 0.0, "flash"), ("where", 7.25, "zoom_punch"), ("inside", 15.25, "whip"),
    ("people", 23.05, "glitch"), ("sub", 29.55, "light_leak"), ("weapons", 33.95, "whip"),
    ("coke", 40.45, "zoom_punch"), ("safe", 51.15, "glitch"), ("bags", 58.15, "whip"), ("brian", 62.15, "flash"),
]
_sfx = {"hook": [(0.0, "impact"), (1.0, "cash")], "inside": [(0.0, "whoosh"), (1.3, "thud")],
        "people": [(0.0, "glitch")], "weapons": [(0.0, "whoosh"), (2.65, "reload"), (3.55, "reload")],
        "coke": [(0.0, "boom")], "brian": [(-1.0, "riser"), (0.0, "impact"), (3.6, "cash")]}
SEGMENTS = []
for i, (sid, t0, tr) in enumerate(_meta):
    t1 = _meta[i + 1][1] if i + 1 < len(_meta) else DURATION
    SEGMENTS.append(dict(id=sid, start=t0, end=t1, counter=None, transition=tr, icons=[],
                         sfx=_sfx.get(sid, [(0.0, "whoosh")]), drop=(sid == "brian")))

SHOT_LIST = [
    (0.00, "n1", 0.30, "push_in", ""),       # safe swinging open (money)
    (1.80, "n2", 19.00, "push_in", ""),      # Jason in the office
    (3.00, "n2", 7.40, "crash_zoom", ""),    # machine gun on the floor (powerful weapons)
    (4.80, "n2", 10.50, "pull_out", ""),     # sunlit warehouse interior (secret warehouse)
    (7.25, "n1", 6.00, "hold", ""),          # the map
    (9.20, "n1", 8.50, "push_in", ""),       # route from Jason's house
    (11.80, "n1", 11.00, "push_in", ""),     # the three lakes
    (13.30, "n1", 14.20, "push_in", ""),     # the red warehouse
    (15.25, "n1", 15.60, "push_in", ""),     # walking to the door, forcing it
    (17.80, "n1", 18.00, "handheld", ""),    # dark interior
    (18.80, "n1", 18.85, "push_in", ""),     # loot bag on the table
    (20.90, "n2", 0.00, "push_in", ""),      # grabbing the loot ($6,000)
    (23.05, "n2", 2.40, "hold", ""),         # "just the beginning"
    (24.70, "n2", 5.00, "push_in", ""),      # unconscious people
    (27.00, "n2", 17.00, "handheld", ""),    # searching them
    (29.55, "n4", 4.20, "pull_out", ""),     # walking the alley (subscribe)
    (31.70, "n2", 11.00, "push_in", ""),     # sunlit office
    (33.95, "n2", 8.20, "push_in", ""),      # machine gun pickup
    (35.80, "n2", 14.80, "push_in", ""),     # pistol pickup
    (37.80, "n3", 6.00, "hold", ""),         # rifle on his back
    (40.45, "n3", 0.30, "push_in", ""),      # the teddy-bear table
    (42.70, "n3", 2.00, "handheld", ""),     # cocaine in the office
    (44.30, "n3", 4.20, "push_in", ""),      # inside the trucks
    (46.60, "n4", 0.50, "push_in", ""),      # forcing a van
    (48.60, "n3", 17.20, "pull_out", ""),    # carrying the bags
    (51.15, "n3", 8.80, "push_in", ""),      # the office safe
    (53.60, "n3", 11.30, "crash_zoom", ""),  # cocaine + cash inside
    (55.40, "n3", 14.30, "push_in", ""),     # the collectible card (after the game's black fade)
    (57.60, "n4", 13.00, "hold", ""),        # selling (pawn shop)
    (58.15, "n3", 19.00, "handheld", ""),    # bags by the van
    (59.90, "n4", 2.50, "push_in", ""),      # filling bags
    (62.15, "n4", 5.00, "push_in", ""),      # to Brian's warehouse
    (64.00, "n4", 8.00, "push_in", ""),      # the door
    (65.60, "n4", 11.00, "hold", ""),        # selling the bags
    (67.40, "n1", 3.40, "pull_out", ""),     # loaded up
]
LEN = {"n1": 21.03, "n2": 21.03, "n3": 21.03, "n4": 16.86}


def all_shots():
    out = []
    for i, (t0, src, sin, cam, opts) in enumerate(SHOT_LIST):
        t1 = SHOT_LIST[i + 1][0] if i + 1 < len(SHOT_LIST) else DURATION
        seg = next(s for s in SEGMENTS if s["start"] <= t0 < s["end"])
        last_in_seg = t1 >= seg["end"] - 1e-6 and seg is not SEGMENTS[-1]
        src_out = sin + (t1 - t0) + (XFADE_D if last_in_seg else 0)
        if src_out > LEN[src] - 0.05:
            raise ValueError(f"shot {i + 1}: {src} {sin}-{src_out:.2f} past clip end")
        out.append(dict(id=f"s{i + 1:02d}", seg=seg["id"], start=t0, end=t1, src=src, src_in=sin, cam=cam,
                        flip="flip" in opts, badge=False, vertical_clean=True, ext="mov", croptop=0.0, notext=True))
    return out


def at(word, after=0.0):
    key = word.lower()
    for t, s, e in WORDS:
        if s >= after - 1e-6 and key in t.lower():
            return s
    raise KeyError(word)


def _fx():
    fx = []

    def icon(word, name, after=0.0, dur=2.0):
        fx.append(dict(t=at(word, after), kind="icon", dur=dur, name=name))

    fx.append(dict(t=at("weapons", 3) - 0.05, kind="weapons", dur=1.25,
                   items=[("rifle", at("weapons", 3) - 0.05)]))
    icon("warehouse", "pin", 6, 1.6)
    icon("location", "pin", 11)
    icon("lakes", "eye", 12, 1.6)
    icon("force", "door", 16, 1.8)
    icon("loot", "bag", 20, 1.6)
    fx.append(dict(t=at("$6", 21), kind="money_big", dur=2.3, amount=6000))
    icon("unconscious", "eye", 25, 2.0)
    icon("loot", "bag", 28, 1.6)
    icon("subscribe", "share", 30, 2.6)
    tw = at("weapons", 35)
    fx.append(dict(t=tw, kind="weapons", dur=40.4 - tw,
                   items=[("smg", at("machine", 36)), ("rifle", at("assault", 37)), ("pistol", at("pistols", 38))]))
    icon("cocaine", "coke", 42, 2.2)
    icon("trucks", "car", 46, 1.8)
    icon("storage", "bag", 50, 1.6)
    icon("safe", "lock", 52, 2.0)
    icon("cocaine", "coke", 53, 1.0)
    icon("cash", "cash", 54, 1.2)
    icon("card", "scan", 56, 1.4)
    icon("bags", "bag", 59, 2.0)
    icon("Brian", "pin", 63, 1.6)
    fx.append(dict(t=at("$15", 65), kind="money_big", dur=2.4, amount=15000))
    icon("card", "scan", 68, 0.8)
    fx.sort(key=lambda e: e["t"])
    kept = []
    for e in fx:                       # one icon at a time; icons pause while a money badge shows
        if e["kind"] != "icon":
            kept.append(e)
            continue
        live = [k for k in kept if k["t"] <= e["t"] < k["t"] + k["dur"] and k["kind"] == "icon"]
        for k in live:
            k["dur"] = max(0.4, e["t"] - k["t"])
        kept.append(e)
    return kept


FX = _fx()
