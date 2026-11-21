"""
Master timeline for "10 CRAZY DETAILS YOU MISSED IN GTA 6".

Single source of truth for overlay.py (counter, subtitles, icons, flashes),
audio.py (music + SFX), assemble.py (real-gameplay cut) and export_docs.py
(SRTs + clip request list).

FOOTAGE POLICY: every shot is REAL GTA 6 gameplay captured by you on
PS5 / Xbox Series. Nothing is drawn or AI-generated. If a clip is missing,
the assembler renders a black "CLIP NEEDED" card instead of inventing one.

Times are in seconds. 30 fps, 1080x1920.
Shot tuple: (shot_id, start_in_segment, camera_move, what_to_capture, focus_x)
  focus_x = horizontal centre of the 9:16 crop inside your 16:9 capture (0 = left edge, 1 = right edge)
Camera moves: push_in, pull_out, pan_l, pan_r, tilt_up, handheld, crash_zoom, hold
Transitions between segments: whip, zoom_punch, flash, glitch, spin, light_leak
"""

FPS = 30
W, H = 1080, 1920
DURATION = 68.0

SEGMENTS = [
    dict(
        id="hook", start=0.0, end=3.2, counter=None, transition="flash",
        vo="Rockstar hid things in GTA 6... that almost nobody has found.",
        captions=[(0.00, "ROCKSTAR HID THINGS", ["HID"]),
                  (1.00, "IN GTA 6...", ["GTA", "6..."]),
                  (1.90, "ALMOST NOBODY FOUND THEM", ["NOBODY"])],
        shots=[("hook_a", 0.00, "crash_zoom", "Night drive through Vice City's neon strip, low chase cam, lots of light reflections", 0.5),
               ("hook_b", 1.90, "push_in", "Jason or Lucia slowly turning to face the camera (photo mode / cinematic cam), night", 0.5)],
        icons=[(1.90, "eye", "side")],
        sfx=[(0.0, "impact"), (1.90, "boom"), (1.90, "glitch")],
    ),
    dict(
        id="title", start=3.2, end=5.0, counter=0, transition="zoom_punch",
        vo="Ten crazy details you missed.",
        captions=[(0.00, "10 CRAZY DETAILS", ["10", "CRAZY"]),
                  (0.85, "YOU MISSED", ["MISSED"])],
        shots=[("title_a", 0.00, "pull_out", "Wide aerial of Vice City beach at sunset (helicopter or plane), skyline + ocean", 0.5)],
        icons=[],
        sfx=[(0.0, "whoosh"), (0.05, "ding")],
    ),
    dict(
        id="f1", start=5.0, end=10.4, counter=1, transition="whip",
        vo="Check your phone's ringtones. Wind Chimes is the exact tone Michael used in GTA 5.",
        captions=[(0.00, "CHECK YOUR RINGTONES", ["RINGTONES"]),
                  (1.50, "\"WIND CHIMES\"", ["\"WIND", "CHIMES\""]),
                  (2.60, "MICHAEL'S RINGTONE", ["MICHAEL'S"]),
                  (3.70, "FROM GTA 5", ["GTA", "5"])],
        shots=[("f1_a", 0.00, "push_in", "Jason/Lucia pulling out the in-game phone (third-person, close)", 0.5),
               ("f1_b", 1.50, "hold", "Phone settings > ringtone list with 'Wind Chimes' highlighted (screen capture of the menu)", 0.5),
               ("f1_c", 3.70, "pan_r", "Character answering a call on the street while the ringtone plays", 0.5)],
        icons=[], sfx=[(0.0, "whoosh"), (0.02, "ding"), (1.50, "pop")],
    ),
    dict(
        id="f2", start=10.4, end=15.6, counter=2, transition="glitch",
        vo="There's an apartment that looks straight out of Dexter... but Rockstar won't let you inside.",
        captions=[(0.00, "A DEXTER APARTMENT", ["DEXTER"]),
                  (1.40, "STRAIGHT OUT OF THE SHOW", ["SHOW"]),
                  (2.90, "BUT YOU CAN'T", []),
                  (3.70, "GO INSIDE", ["INSIDE"])],
        shots=[("f2_a", 0.00, "tilt_up", "Exterior of the Dexter-style apartment building, slow tilt up from street level", 0.5),
               ("f2_b", 2.90, "push_in", "Character walking up to the locked entrance / door that can't be opened", 0.5)],
        icons=[], sfx=[(0.0, "glitch"), (0.02, "ding"), (2.90, "thud")],
    ),
    dict(
        id="f3", start=15.6, end=21.0, counter=3, transition="whip",
        vo="A parrot named Tony keeps yelling generator. Follow the clue and you'll find a hidden cash stash.",
        captions=[(0.00, "TONY THE PARROT", ["TONY"]),
                  (1.20, "KEEPS YELLING", []),
                  (1.90, "\"GENERATOR\"", ["\"GENERATOR\""]),
                  (3.30, "= HIDDEN CASH", ["CASH"])],
        shots=[("f3_a", 0.00, "push_in", "Close-up of Tony the parrot talking", 0.5),
               ("f3_b", 1.90, "handheld", "Walking toward / searching the generator", 0.5),
               ("f3_c", 3.30, "crash_zoom", "Picking up the hidden cash stash (money pickup animation)", 0.5)],
        icons=[(3.30, "cash", "side")],
        sfx=[(0.0, "whoosh"), (0.02, "ding"), (3.30, "cash")],
    ),
    dict(
        id="f4", start=21.0, end=26.4, counter=4, transition="zoom_punch",
        vo="Swim too far out, and a dog in goggles rides in on a jet ski to save you.",
        captions=[(0.00, "SWIM TOO FAR OUT", ["FAR"]),
                  (1.30, "A DOG IN GOGGLES", ["DOG"]),
                  (2.60, "ON A JET SKI", ["JET", "SKI"]),
                  (3.70, "COMES TO SAVE YOU", ["SAVE"])],
        shots=[("f4_a", 0.00, "pull_out", "Character swimming far offshore, open ocean, shore tiny in the distance", 0.5),
               ("f4_b", 1.30, "push_in", "The goggle-wearing dog arriving on the jet ski", 0.5),
               ("f4_c", 3.70, "handheld", "Character climbing onto the jet ski behind the dog", 0.5)],
        icons=[], sfx=[(0.0, "boom"), (0.02, "ding"), (1.30, "swoosh_up")],
    ),
    dict(
        id="f5", start=26.4, end=31.6, counter=5, transition="flash",
        vo="Stay on board long enough... and it takes you to an island full of dogs.",
        captions=[(0.00, "STAY ON BOARD...", ["BOARD..."]),
                  (1.40, "IT TAKES YOU TO", []),
                  (2.30, "AN ISLAND", ["ISLAND"]),
                  (3.10, "FULL OF DOGS", ["DOGS"])],
        shots=[("f5_a", 0.00, "pan_r", "Riding the jet ski with the dog across the water, side tracking shot", 0.5),
               ("f5_b", 2.30, "pull_out", "Arriving at the small island packed with dogs (wide)", 0.5)],
        icons=[(2.30, "pin", "side")],
        sfx=[(0.0, "impact"), (0.02, "ding"), (2.30, "pop")],
    ),
    dict(
        id="f6", start=31.6, end=37.2, counter=6, transition="spin",
        vo="Climb a radio tower for seven minutes, throw an egg from the top, and a secret cutscene unlocks.",
        captions=[(0.00, "CLIMB A RADIO TOWER", ["TOWER"]),
                  (1.20, "FOR 7 MINUTES", ["7"]),
                  (2.30, "THROW AN EGG", ["EGG"]),
                  (3.50, "SECRET CUTSCENE", ["SECRET"])],
        shots=[("f6_a", 0.00, "tilt_up", "Looking up the communications tower, character climbing the ladder", 0.5),
               ("f6_b", 2.30, "push_in", "The nest of eggs at the top, picking one up and throwing it", 0.5),
               ("f6_c", 3.50, "hold", "First seconds of the secret cutscene (no story spoilers)", 0.5)],
        icons=[(1.20, "clock", "side")],
        sfx=[(0.0, "whoosh"), (0.02, "ding"), (3.50, "riser_short")],
    ),
    dict(
        id="f7", start=37.2, end=42.6, counter=7, transition="whip",
        vo="At a research facility, a giant mutant crab can ambush you. Yes, really.",
        captions=[(0.00, "RESEARCH FACILITY", ["RESEARCH"]),
                  (1.40, "GIANT MUTANT CRAB", ["GIANT", "CRAB"]),
                  (3.40, "YES. REALLY.", ["REALLY."])],
        shots=[("f7_a", 0.00, "push_in", "Approaching the research facility exterior (night or dusk works best)", 0.5),
               ("f7_b", 1.40, "crash_zoom", "The giant mutant crab bursting out / ambushing the player", 0.5),
               ("f7_c", 3.40, "handheld", "Player running away from the crab", 0.5)],
        icons=[], sfx=[(0.0, "whoosh"), (0.02, "ding"), (1.40, "boom")],
    ),
    dict(
        id="f8", start=42.6, end=48.4, counter=8, transition="light_leak",
        vo="In some bars, people whisper about a secret bunker full of jetpacks, hidden under a mountain.",
        captions=[(0.00, "LISTEN IN BARS", ["BARS"]),
                  (1.40, "A SECRET BUNKER", ["BUNKER"]),
                  (2.60, "FULL OF JETPACKS", ["JETPACKS"]),
                  (3.80, "UNDER A MOUNTAIN", ["MOUNTAIN"])],
        shots=[("f8_a", 0.00, "push_in", "Inside a bar, NPCs talking at the counter (subtitles visible if possible)", 0.5),
               ("f8_b", 2.60, "pan_l", "Close-up of the NPC conversation / player listening", 0.5),
               ("f8_c", 3.80, "pull_out", "Wide shot of a mountain in Leonida at dusk (Mount Kalaga area)", 0.5)],
        icons=[], sfx=[(0.0, "riser_short"), (0.02, "ding"), (1.40, "pop")],
    ),
    dict(
        id="f9", start=48.4, end=54.2, counter=9, transition="glitch",
        vo="And there's a strange monument near Manifest Canyon. Players are calling it the new Mount Chiliad mystery.",
        captions=[(0.00, "A STRANGE MONUMENT", ["STRANGE"]),
                  (1.40, "NEAR MANIFEST CANYON", ["MANIFEST"]),
                  (3.00, "THE NEW", []),
                  (3.60, "CHILIAD MYSTERY", ["CHILIAD"])],
        shots=[("f9_a", 0.00, "push_in", "The monument near Manifest Canyon, slow approach", 0.5),
               ("f9_b", 3.00, "tilt_up", "Low-angle shot looking up at the monument, sky behind", 0.5)],
        icons=[(3.00, "eye", "side")],
        sfx=[(0.0, "glitch"), (0.02, "ding"), (3.00, "pop")],
    ),
    dict(
        id="f10", start=54.2, end=62.6, counter=10, transition="flash",
        vo="But the craziest one? A building in GTA 6 was hidden in the San Andreas remaster years ago. Rockstar was teasing us the whole time.",
        captions=[(0.00, "THE CRAZIEST ONE?", ["CRAZIEST"]),
                  (1.40, "HIDDEN IN SAN ANDREAS", ["SAN", "ANDREAS"]),
                  (3.40, "YEARS AGO", ["YEARS"]),
                  (5.40, "ROCKSTAR WAS TEASING US", ["TEASING"]),
                  (6.90, "THE WHOLE TIME", ["WHOLE"])],
        shots=[("f10_a", 0.00, "crash_zoom", "Dramatic reveal: flying toward the matching building on the GTA 6 map", 0.5),
               ("f10_b", 1.40, "hold", "The image from GTA San Andreas Definitive Edition (your own capture of the remaster)", 0.5),
               ("f10_c", 3.40, "push_in", "The same structure in GTA 6, matching angle (side-by-side moment)", 0.5),
               ("f10_d", 5.40, "pull_out", "Epic wide shot of Vice City skyline at night", 0.5)],
        icons=[(1.40, "scan", "side")],
        sfx=[(-1.0, "riser"), (0.0, "impact"), (0.02, "ding"), (1.40, "boom"), (5.40, "boom")],
    ),
    dict(
        id="cta", start=62.6, end=68.0, counter=10, transition="whip",
        vo="Which one did you miss? Comment below, and send this to your squad.",
        captions=[(0.00, "WHICH ONE DID YOU MISS?", ["MISS?"]),
                  (1.60, "COMMENT BELOW", ["COMMENT"]),
                  (2.80, "SEND THIS TO", []),
                  (3.60, "YOUR SQUAD", ["SQUAD"])],
        shots=[("cta_a", 0.00, "pan_r", "Jason and Lucia together in a car or on the beach, sunset", 0.5),
               ("cta_b", 2.80, "pull_out", "Vice City skyline pull-back / plane flying away", 0.5)],
        icons=[(1.60, "comment", "side"), (2.80, "share", "side")],
        sfx=[(0.0, "whoosh"), (1.60, "pop"), (2.80, "swoosh_up")],
    ),
]


def all_shots():
    out = []
    for seg in SEGMENTS:
        shots = seg["shots"]
        for i, (sid, t, cam, need, focus) in enumerate(shots):
            t0 = seg["start"] + t
            t1 = seg["start"] + shots[i + 1][1] if i + 1 < len(shots) else seg["end"]
            out.append(dict(id=sid, seg=seg["id"], start=round(t0, 3), end=round(t1, 3),
                            cam=cam, need=need, focus=focus))
    return out


def all_captions():
    out = []
    for seg in SEGMENTS:
        caps = seg["captions"]
        for i, (t, text, hl) in enumerate(caps):
            t0 = seg["start"] + t
            t1 = seg["start"] + caps[i + 1][0] if i + 1 < len(caps) else seg["end"]
            out.append(dict(start=t0, end=t1, text=text, hl=hl, seg=seg["id"]))
    return out
