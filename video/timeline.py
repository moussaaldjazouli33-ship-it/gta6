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
PILL_TEXT = "GTA 6 • CRAZY DETAILS"
TITLE_LABEL = "DETAILS"


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
    # 4 hand-to-hand: Lucia, then Jason
    (23.02, "c4", 12.6, "push_in", ""),
    (25.40, "c2", 7.2, "push_in", ""),
    (27.95, "c1", 9.45, "crash_zoom", ""),
    (28.60, "c1", 8.4, "push_in", ""),
    # 5 cap / glasses
    (29.52, "c1", 16.95, "push_in", ""),
    (30.42, "c4", 6.9, "pan_l", ""),
    (32.70, "c2", 34.0, "push_in", ""),
    # 6 store robbery
    (34.98, "c3", 0.3, "push_in", "badge"),
    (36.60, "c1", 13.48, "push_in", ""),
    (37.75, "c3", 6.5, "crash_zoom", ""),
    (40.50, "c1", 4.53, "pan_r", ""),
    # 7 clothes in the trunk / lose the cops
    (41.76, "c2", 18.0, "pan_l", ""),
    (43.90, "c3", 14.0, "handheld", ""),
    # 8 arrested / weapons
    (45.96, "c3", 2.0, "push_in", "badge"),
    (48.20, "c3", 11.3, "handheld", ""),
    (49.10, "c1", 19.0, "push_in", ""),
    (50.65, "c2", 4.0, "pull_out", ""),
    # 9 car delivered, valet leaves on a scooter
    (52.72, "c4", 3.9, "pan_r", "badge"),
    (55.40, "c4", 0.0, "push_in", "badge"),
    # 10 NPC robberies
    (56.62, "c1", 13.48, "crash_zoom", "flip"),
    (57.77, "c3", 9.0, "handheld", "flip"),
    (60.20, "c3", 6.8, "push_in", "flip"),
    # outro: Jason, Lucia, skydive
    (62.22, "c2", 6.0, "push_in", ""),
    (63.00, "c2", 1.7, "push_in", "badge flip"),
    (64.90, "c5", 3.4, "pull_out", "badge"),
    (67.20, "c5", 6.0, "push_in", "badge"),
]

# Source ranges that contain logos, title cards, "PRE-LOAD NOW", PS5 splash or end cards.
# A shot (including its transition overlap) may never touch these.
BANNED = {
    "c1": [(0.0, 2.0), (6.05, 8.37), (14.65, 16.9), (20.55, 99)],
    "c2": [(40.95, 99)],
    "c3": [(16.55, 99)],
    "c4": [(15.85, 99)],
    "c5": [(9.35, 99)],
}
XFADE_D = 0.25


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


# ------------------------------------------------------------------ decorative FX (NO narration text)
def at(word, after=0.0):
    """Start time of the first spoken word matching `word` (case/punctuation-insensitive) after `after`."""
    key = word.lower().strip(".,?!")
    for t, s, e in WORDS:
        if s >= after - 1e-6 and t.lower().strip(".,?!").replace("’", "'") == key:
            return s
    raise KeyError(word)


def _seg(sid):
    return next(s for s in SEGMENTS if s["id"] == sid)


def _fx():
    S = {s["id"]: s["start"] for s in SEGMENTS}
    fx = []
    add = lambda t, kind, dur, **k: fx.append(dict(t=t, kind=kind, dur=dur, **k))  # noqa: E731
    # big animated numbers on every spoken number
    for s in SEGMENTS:
        if s["id"].startswith("f"):
            add(s["start"], "bignum", 1.15, n=s["counter"])
    # hook
    add(0.05, "label", 2.6, text="DID YOU KNOW?", icon="eye")
    add(at("Lucia"), "tag", 2.4, text="LUCIA", x=640, y=470, side="l")
    add(at("couple"), "icon", 1.2, name="heart")
    # title
    add(at("10"), "label", 2.6, text="10 CRAZY DETAILS", icon="controller", big=True)
    # 1 relationship
    f = S["f1"]
    add(at("appel,", f), "notif", 3.6, title="LUCIA", msg="Missed call", slot=0)
    add(at("SMS,", f), "notif", 2.9, title="LUCIA", msg="New message", slot=1)
    add(at("chuter", f), "meter", 3.2, label="RELATIONSHIP", v0=0.85, v1=0.18)
    add(at("chuter", f) + 0.1, "icon", 3.0, name="heart")
    # 2 drive-by
    f = S["f2"]
    add(at("conduit,", f), "label", 2.4, text="DRIVE-BY MODE", icon="car")
    add(at("tirer", f), "icon", 2.0, name="gun")
    add(at("fuite,", f), "stars", 1.7, n=3)
    # 3 gun in the street
    f = S["f3"]
    add(at("arme", f), "label", 2.6, text="HANDS OFF!", icon="gun")
    add(at("passants", f), "icon", 2.0, name="eye")
    add(at("arme", f), "stars", 3.2, n=2)
    # 4 fighting styles
    f = S["f4"]
    add(at("main", f), "label", 2.4, text="FIGHT STYLES", icon="duo")
    add(at("Lucia", f), "tag", 2.2, text="LUCIA", x=400, y=560, side="l")
    add(at("Jason", f), "tag", 1.9, text="JASON", x=250, y=600, side="r")
    # 5 cap / glasses
    f = S["f5"]
    add(f + 0.15, "ping", 1.0, x=540, y=760)
    add(at("bagarre,", f), "label", 2.4, text="LOOT THEIR STYLE", icon="scan")
    add(at("casquette", f), "ping", 1.6, x=150, y=980)
    add(at("lunettes", f), "icon", 1.8, name="scan")
    # 6 store robbery
    f = S["f6"]
    add(at("supérette,", f), "icon", 2.0, name="alarm")
    add(at("coffre", f), "label", 2.5, text="SECRET SAFE", icon="cash")
    add(at("coffre", f) + 0.1, "money", 1.8, text="+$25,000")
    add(at("attends,", f), "ping", 1.1, x=540, y=900)
    # 7 change your look
    f = S["f7"]
    add(at("vêtements", f), "label", 2.6, text="CHANGE YOUR LOOK", icon="scan")
    add(at("voiture", f), "icon", 1.4, name="car")
    add(at("semer", f) - 0.9, "stars", 1.6, n=4, lose=True)
    # 8 weapon rules
    f = S["f8"]
    add(at("arrêter,", f), "stars", 1.8, n=5)
    add(at("armes", f), "label", 2.6, text="WEAPON RULES", icon="slots")
    add(at("perso", f), "icon", 2.0, name="slots")
    # 9 car delivery
    f = S["f9"]
    add(at("appelles", f), "icon", 1.6, name="pin")
    add(at("voiture,", f), "label", 2.4, text="CAR DELIVERY", icon="car")
    add(at("trottinette.", f), "ping", 1.2, x=560, y=1050)
    # 10 rob the robbers
    f = S["f10"]
    add(at("fou,", f), "icon", 1.6, name="flame")
    add(at("braquent", f), "stars", 1.9, n=3)
    add(at("magasins", f), "label", 2.4, text="ROB THE ROBBERS", icon="gun")
    add(at("braqueurs.", f), "money", 1.6, text="+$$$")
    # outro
    f = S["cta"]
    add(at("Jason", f), "tag", 0.9, text="JASON", x=330, y=650, side="r")
    add(at("Lucia", f), "tag", 1.6, text="LUCIA", x=600, y=640, side="l")
    add(at("Lucia", f) + 0.3, "label", 2.0, text="WHO'S YOUR MAIN?", icon="duo")
    add(at("commentaire.", f), "icon", 1.8, name="comment")
    add(at("Envoie", f), "icon", 1.9, name="share")
    add(at("abonne-toi", f), "label", 2.3, text="FOLLOW FOR MORE", icon="controller")
    return _minimal(sorted(fx, key=lambda e: e["t"]))


def _minimal(fx):
    """Text-free version: every element becomes a small icon, ping, pulse or star row. No words on screen."""
    out = []
    for e in fx:
        k = e["kind"]
        if k == "bignum":
            out.append(dict(t=e["t"], kind="pulse", dur=0.9))
        elif k == "label":
            out.append(dict(t=e["t"], kind="icon", dur=min(e["dur"], 2.0), name=e.get("icon") or "eye"))
        elif k == "tag":
            out.append(dict(t=e["t"], kind="ping", dur=min(e["dur"], 1.6), x=e["x"], y=e["y"]))
        elif k == "notif":
            out.append(dict(t=e["t"], kind="icon", dur=min(e["dur"], 2.0), name="comment"))
        elif k == "meter":
            out.append(dict(t=e["t"], kind="icon", dur=2.0, name="heart"))
        elif k == "money":
            out.append(dict(t=e["t"], kind="icon", dur=1.6, name="cash"))
        else:
            out.append(dict(e))
    out.sort(key=lambda e: e["t"])
    # at most 2 icons at once, never the same icon twice at the same time
    kept = []
    for e in out:
        if e["kind"] == "icon":
            live = [k for k in kept if k["kind"] == "icon" and k["t"] <= e["t"] < k["t"] + k["dur"]]
            if len(live) >= 2 or any(k["name"] == e["name"] for k in live):
                continue
        kept.append(e)
    return kept


FX = _fx()
