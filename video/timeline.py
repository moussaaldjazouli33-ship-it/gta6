"""
Master timeline for "10 THINGS YOU NEED TO KNOW BEFORE PLAYING GTA 6".

Single source of truth: render.py (motion graphics + SFX), assemble.py (real
footage cut) and export_docs.py (SRT / shot list) all read from here.

Times are in seconds. 30 fps, 1080x1920.
"""

FPS = 30
W, H = 1080, 1920
DURATION = 69.0

# ---------------------------------------------------------------------------
# Scene types used by the placeholder background generator in render.py.
# When real clips exist in footage/<shot_id>.mp4, assemble.py uses them.
#   beach  city  chase  club  swamp  money  map  bridge  cctv  motel
# Camera moves: push_in, pull_out, pan_l, pan_r, tilt_up, orbit, handheld, crash_zoom
# Transitions (into a segment): whip, zoom_punch, flash, glitch, spin, light_leak
# ---------------------------------------------------------------------------

SEGMENTS = [
    # ------------------------------------------------------------------ HOOK
    dict(
        id="hook", start=0.0, end=3.2, counter=None, transition="flash",
        vo="If you play GTA 6 like GTA 5... you're getting busted.",
        captions=[
            (0.00, "IF YOU PLAY GTA 6", ["GTA 6"]),
            (0.85, "LIKE GTA 5...", ["GTA 5"]),
            (1.70, "YOU'RE GETTING BUSTED", ["BUSTED"]),
        ],
        shots=[
            ("hook_a", 0.00, "chase", "crash_zoom",
             "Night police chase on a neon-lit Miami-style causeway, red and blue strobes "
             "reflecting on a wet black sports car, low angle bumper cam, motion blur, "
             "photoreal open-world game graphics, 9:16"),
            ("hook_b", 1.70, "chase", "handheld",
             "Close-up of a police cruiser light bar flashing red and blue, rain drops, "
             "shallow depth of field, camera shake, cinematic game render, 9:16"),
        ],
        icons=[(1.70, "stars6", "top")],
        sfx=[(0.0, "impact"), (0.05, "siren"), (1.70, "boom"), (1.70, "glitch")],
        strobe=(1.70, 3.2),
    ),
    # ----------------------------------------------------------------- TITLE
    dict(
        id="title", start=3.2, end=5.0, counter=0, transition="zoom_punch",
        vo="Ten things you need to know.",
        captions=[
            (0.00, "10 THINGS YOU NEED", ["10"]),
            (0.75, "TO KNOW BEFORE PLAYING", ["KNOW"]),
        ],
        shots=[
            ("title_a", 0.00, "beach", "pull_out",
             "Aerial drone shot pulling back over a sunset beach lined with palm trees and "
             "Art-Deco hotels, pink and orange sky, ocean reflections, ultra-detailed "
             "open-world game graphics, 9:16"),
        ],
        icons=[(0.2, "controller", "low")],
        sfx=[(0.0, "whoosh"), (0.05, "ding")],
    ),
    # ---------------------------------------------------------------- FACT 1
    dict(
        id="f1", start=5.0, end=10.6, counter=1, transition="whip",
        vo="Two heroes. Jason and Lucia work as a team, and splitting up can shake the cops.",
        captions=[
            (0.00, "TWO HEROES", ["TWO"]),
            (0.80, "JASON AND LUCIA", ["JASON", "LUCIA"]),
            (2.40, "SPLIT UP TO", []),
            (3.30, "SHAKE THE COPS", ["COPS"]),
        ],
        shots=[
            ("f1_a", 0.00, "motel", "push_in",
             "A rugged man in his 30s and a confident Latina woman with braided hair "
             "standing back to back in a neon-lit motel parking lot at dusk, pistols lowered, "
             "cinematic game character render, 9:16"),
            ("f1_b", 2.40, "chase", "pan_r",
             "Two getaway cars splitting at a highway fork at night, police cars following, "
             "helicopter spotlight, motion blur, photoreal game footage, 9:16"),
        ],
        icons=[(0.80, "duo", "low"), (2.40, "arrow_split", "low")],
        sfx=[(0.0, "whoosh"), (0.02, "ding"), (2.40, "swoosh_up")],
    ),
    # ---------------------------------------------------------------- FACT 2
    dict(
        id="f2", start=10.6, end=15.8, counter=2, transition="glitch",
        vo="No witness, no crime. Police only come if someone sees you or an alarm goes off.",
        captions=[
            (0.00, "NO WITNESS", ["WITNESS"]),
            (0.75, "NO CRIME", ["CRIME"]),
            (1.60, "SOMEONE SEES YOU", ["SEES"]),
            (2.90, "OR AN ALARM GOES OFF", ["ALARM"]),
        ],
        shots=[
            ("f2_a", 0.00, "city", "orbit",
             "Quiet back alley in a humid neon city at night, a pedestrian on a phone "
             "turning to look at the camera, steam from vents, photoreal game footage, 9:16"),
            ("f2_b", 2.90, "money", "handheld",
             "Convenience-store robbery interior, red alarm light spinning, cash register open, "
             "shaky handheld camera, cinematic game graphics, 9:16"),
        ],
        icons=[(0.0, "eye", "side"), (2.90, "alarm", "side")],
        sfx=[(0.0, "glitch"), (0.02, "ding"), (2.90, "alarm")],
    ),
    # ---------------------------------------------------------------- FACT 3
    dict(
        id="f3", start=15.8, end=21.4, counter=3, transition="whip",
        vo="Cops remember you. Your face, your outfit, your car. Change all three to disappear.",
        captions=[
            (0.00, "COPS REMEMBER YOU", ["REMEMBER"]),
            (1.30, "FACE. OUTFIT. CAR.", ["FACE.", "OUTFIT.", "CAR."]),
            (3.20, "CHANGE ALL THREE", ["THREE"]),
        ],
        shots=[
            ("f3_a", 0.00, "cctv", "handheld",
             "Grainy security-camera view of a man in a hoodie walking past a gas station "
             "at night, timestamp overlay, fisheye lens, 9:16"),
            ("f3_b", 1.30, "cctv", "push_in",
             "Police computer screen showing a suspect profile with face, clothing and "
             "vehicle thumbnails, blue UI glow, 9:16"),
            ("f3_c", 3.20, "motel", "pan_l",
             "Character changing into a new outfit in a clothing store mirror, then driving "
             "off in a different car, neon signage, photoreal game render, 9:16"),
        ],
        icons=[(1.30, "scan", "side")],
        sfx=[(0.0, "whoosh"), (0.02, "ding"), (1.30, "beep"), (1.75, "beep"), (2.20, "beep")],
    ),
    # ---------------------------------------------------------------- FACT 4
    dict(
        id="f4", start=21.4, end=26.6, counter=4, transition="zoom_punch",
        vo="Crime scenes stay hot. Go back too soon and the stars come right back.",
        captions=[
            (0.00, "CRIME SCENES", ["CRIME"]),
            (0.80, "STAY HOT", ["HOT"]),
            (2.20, "GO BACK TOO SOON...", ["SOON..."]),
            (3.40, "STARS COME BACK", ["STARS"]),
        ],
        shots=[
            ("f4_a", 0.00, "city", "push_in",
             "Police tape and patrol cars outside a jewelry store at night, officers with "
             "flashlights, red and blue light wash, photoreal game footage, 9:16"),
            ("f4_b", 2.20, "chase", "crash_zoom",
             "Car slowly driving back past the crime scene, a cop turns and points, "
             "dramatic zoom, cinematic game graphics, 9:16"),
        ],
        icons=[(0.80, "flame", "side"), (3.40, "stars3", "top")],
        sfx=[(0.0, "boom"), (0.02, "ding"), (3.40, "siren_short")],
        strobe=(3.40, 5.2),
    ),
    # ---------------------------------------------------------------- FACT 5
    dict(
        id="f5", start=26.6, end=31.8, counter=5, transition="flash",
        vo="Six stars are back. And at max heat, Leonida stops playing fair.",
        captions=[
            (0.00, "SIX STARS", ["SIX"]),
            (0.80, "ARE BACK", []),
            (2.10, "AT MAX HEAT", ["MAX"]),
            (3.10, "NO MERCY", ["MERCY"]),
        ],
        shots=[
            ("f5_a", 0.00, "chase", "tilt_up",
             "Helicopter with searchlight over a burning highway interchange, SWAT trucks "
             "blocking the road, smoke, epic wide shot, photoreal game footage, 9:16"),
            ("f5_b", 2.10, "chase", "handheld",
             "Armored police vans ramming a muscle car in slow motion, sparks, debris, "
             "cinematic game render, 9:16"),
        ],
        icons=[(0.0, "stars6", "top")],
        sfx=[(0.0, "impact"), (0.02, "ding"), (0.15, "star_ticks"), (2.10, "heli")],
        strobe=(2.10, 5.2),
    ),
    # ---------------------------------------------------------------- FACT 6
    dict(
        id="f6", start=31.8, end=37.6, counter=6, transition="spin",
        vo="You can't carry an arsenal. Two handguns, two long guns. The rest stays in the trunk.",
        captions=[
            (0.00, "NO MORE ARSENAL", ["ARSENAL"]),
            (1.30, "2 HANDGUNS", ["2"]),
            (2.10, "2 LONG GUNS", ["2"]),
            (3.30, "REST IN THE TRUNK", ["TRUNK"]),
        ],
        shots=[
            ("f6_a", 0.00, "motel", "orbit",
             "Weapons laid out on a motel bed under a neon window, pistols and rifles, "
             "moody teal and pink light, product-shot style, game render, 9:16"),
            ("f6_b", 3.30, "city", "push_in",
             "Character opening a car trunk revealing a hidden weapon stash, parking garage "
             "at night, cinematic game footage, 9:16"),
        ],
        icons=[(1.30, "slots", "low")],
        sfx=[(0.0, "whoosh"), (0.02, "ding"), (1.30, "reload"), (2.10, "reload"), (3.30, "thud")],
    ),
    # ---------------------------------------------------------------- FACT 7
    dict(
        id="f7", start=37.6, end=43.2, counter=7, transition="whip",
        vo="Cash on you is at risk. Die or get busted and you lose it. Bank it at an ATM.",
        captions=[
            (0.00, "CASH ON YOU", ["CASH"]),
            (0.80, "IS AT RISK", ["RISK"]),
            (2.00, "DIE = YOU LOSE IT", ["LOSE"]),
            (3.40, "BANK IT AT AN ATM", ["ATM"]),
        ],
        shots=[
            ("f7_a", 0.00, "money", "push_in",
             "Duffel bag overflowing with dollar bills on a car passenger seat, neon "
             "reflections, slow push-in, photoreal game render, 9:16"),
            ("f7_b", 3.40, "city", "pan_r",
             "Character using a street ATM at night under a palm tree, pink neon glow, "
             "cinematic game footage, 9:16"),
        ],
        icons=[(0.0, "cash", "side"), (2.00, "skull", "side")],
        sfx=[(0.0, "whoosh"), (0.02, "ding"), (0.10, "cash"), (2.00, "boom")],
    ),
    # ---------------------------------------------------------------- FACT 8
    dict(
        id="f8", start=43.2, end=49.6, counter=8, transition="light_leak",
        vo="Vice City is just the start. Leonida has the Keys, Grassrivers, Port Gellhorn, Ambrosia and Mount Kalaga.",
        captions=[
            (0.00, "VICE CITY", ["VICE"]),
            (0.80, "IS JUST THE START", ["START"]),
            (2.00, "LEONIDA KEYS", ["KEYS"]),
            (2.80, "GRASSRIVERS", ["GRASSRIVERS"]),
            (3.50, "PORT GELLHORN", ["GELLHORN"]),
            (4.20, "AMBROSIA + KALAGA", ["AMBROSIA"]),
        ],
        shots=[
            ("f8_a", 0.00, "beach", "pull_out",
             "Epic aerial of a neon Art-Deco beach city at golden hour, skyscrapers and "
             "palm-lined ocean drive, drone pull-out, photoreal game graphics, 9:16"),
            ("f8_b", 2.00, "bridge", "pan_r",
             "Long overseas highway bridge over turquoise water connecting tropical keys, "
             "convertible driving, sun flare, 9:16"),
            ("f8_c", 2.80, "swamp", "push_in",
             "Airboat speeding through misty everglades with alligators and cypress trees, "
             "dawn light, photoreal game footage, 9:16"),
            ("f8_d", 4.20, "map", "pull_out",
             "Stylized glowing 3D map of a Florida-like state with six region pins lighting up, "
             "dark background, game menu UI, 9:16"),
        ],
        icons=[(2.0, "pin", "map")],
        sfx=[(0.0, "riser_short"), (0.02, "ding"), (2.0, "pop"), (2.8, "pop"), (3.5, "pop"), (4.2, "pop")],
    ),
    # ---------------------------------------------------------------- FACT 9
    dict(
        id="f9", start=49.6, end=55.2, counter=9, transition="glitch",
        vo="Online isn't here yet. GTA Online for 6 is expected in 2027, and PC is coming later.",
        captions=[
            (0.00, "ONLINE ISN'T", ["ONLINE"]),
            (0.75, "HERE YET", []),
            (1.80, "EXPECTED IN 2027", ["2027"]),
            (3.30, "PC COMES LATER", ["PC"]),
        ],
        shots=[
            ("f9_a", 0.00, "club", "orbit",
             "Crowded neon nightclub with lasers and a DJ booth, slow orbit, purple and "
             "cyan beams, photoreal game footage, 9:16"),
            ("f9_b", 3.30, "city", "push_in",
             "Gaming desk with a glowing PC tower showing a 'coming soon' loading screen, "
             "RGB light, cinematic close-up, 9:16"),
        ],
        icons=[(0.0, "wifi_off", "side"), (1.80, "clock", "side")],
        sfx=[(0.0, "glitch"), (0.02, "ding"), (1.80, "pop")],
    ),
    # --------------------------------------------------------------- FACT 10
    dict(
        id="f10", start=55.2, end=63.4, counter=10, transition="flash",
        vo="And the craziest part? GTA 6 made three point seven nine billion dollars on day one. The biggest entertainment launch in history.",
        captions=[
            (0.00, "THE CRAZIEST PART?", ["CRAZIEST"]),
            (1.30, "DAY ONE:", ["ONE:"]),
            (2.00, "$3.79 BILLION", ["$3.79"]),
            (4.60, "BIGGEST LAUNCH", ["BIGGEST"]),
            (5.60, "IN HISTORY", ["HISTORY"]),
        ],
        shots=[
            ("f10_a", 0.00, "money", "crash_zoom",
             "Vault door swinging open revealing towering stacks of cash and gold bars, "
             "light rays, dust, slow motion, photoreal game render, 9:16"),
            ("f10_b", 2.00, "money", "push_in",
             "Money raining down over a neon city rooftop at night, bills fluttering in "
             "slow motion, celebratory, cinematic, 9:16"),
            ("f10_c", 4.60, "beach", "tilt_up",
             "Fireworks over a neon Art-Deco skyline and beach at night, crowds cheering, "
             "epic wide shot, photoreal game graphics, 9:16"),
        ],
        icons=[(2.0, "trophy", "low")],
        count_up=(2.0, 3.6, 3.79),   # animated number: start, end, value (billions)
        sfx=[(-1.0, "riser"), (0.0, "impact"), (0.02, "ding"), (2.0, "boom"), (2.05, "cash"), (4.6, "crowd")],
    ),
    # ------------------------------------------------------------------- CTA
    dict(
        id="cta", start=63.4, end=69.0, counter=10, transition="whip",
        vo="Jason or Lucia, who are you playing first? Send this to the friend who's still downloading.",
        captions=[
            (0.00, "JASON OR LUCIA?", ["JASON", "LUCIA?"]),
            (1.40, "COMMENT BELOW", ["COMMENT"]),
            (2.80, "SEND THIS TO", []),
            (3.60, "YOUR SQUAD", ["SQUAD"]),
        ],
        shots=[
            ("cta_a", 0.00, "beach", "orbit",
             "The duo leaning on a pink convertible on a beach road at sunset, slow orbit, "
             "lens flare, cinematic game character render, 9:16"),
            ("cta_b", 2.80, "club", "pull_out",
             "Neon Vice City-style skyline at night, camera pulling back into the sky, "
             "magenta and orange glow, 9:16"),
        ],
        icons=[(1.40, "comment", "low"), (2.8, "share", "low")],
        sfx=[(0.0, "whoosh"), (1.40, "pop"), (2.80, "swoosh_up")],
    ),
]


def all_shots():
    """Flatten shots to absolute times with durations."""
    out = []
    for seg in SEGMENTS:
        shots = seg["shots"]
        for i, (sid, t, scene, cam, prompt) in enumerate(shots):
            t0 = seg["start"] + t
            t1 = seg["start"] + shots[i + 1][1] if i + 1 < len(shots) else seg["end"]
            out.append(dict(id=sid, seg=seg["id"], start=round(t0, 3), end=round(t1, 3),
                            scene=scene, cam=cam, prompt=prompt))
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
