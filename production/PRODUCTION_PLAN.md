# 10 THINGS YOU NEED TO KNOW BEFORE PLAYING GTA 6
**TikTok / Reels / Shorts · 9:16 · 1080×1920 · 30 fps · 69 s**

This folder holds the full production pack. `video/` holds the code that renders the motion graphics, sound design and final cut.

| File | What it is |
|---|---|
| `out/gta6_10_things.mp4` | Full edit: animated counter, subtitles, HUD, icons, transitions, music and SFX, over procedurally animated **placeholder** backgrounds |
| `out/overlay_prores4444.mov` | Graphics layer only, with transparency (ProRes 4444). Drop it on top of any footage in CapCut, Premiere or DaVinci |
| `out/bg_placeholder.mp4` | Placeholder plates only. Used as a fallback for shots you haven't filmed yet |
| `out/soundtrack.wav` | Music bed with every sound effect synced to the timeline |
| `production/SHOTLIST.md` / `shotlist.csv` | One video-generation prompt per shot (29 shots), with in/out times and camera move |
| `production/captions.srt` | Subtitle timings |
| `production/voiceover_script.txt` / `voiceover.srt` | Narration script, plus per-segment timing for TTS |

---

## 1. Workflow (fastest route to a post-ready video)

GTA 6 has been out since **19 November 2026**, so the best footage is your own gameplay capture. It looks real because it is real, and it's safe from copyright claims. Use AI generation only to fill gaps.

1. **Record a voice-over** from `voiceover_script.txt`. The `voiceover.srt` timings show where each line must land.
   - ElevenLabs settings: an energetic US narrator ("Adam"- or "Josh"-style voice), Stability 35, Similarity 80, Style 40, speed 1.08. You want about 175 words per minute, punchy, with no pauses between facts.
   - Generate one segment at a time and place each at its start time, so it stays synced with the subtitles.
2. **Get footage** for each shot id in `SHOTLIST.md`, then save it as `footage/<shot_id>.mp4` (or `.mov`, `.png`, `.jpg`).
   - Gameplay: capture on PS5 or Xbox (Share → video clip, 4K60 if possible). Use photo mode and the cinematic camera for hero shots, and the bumper or hood cam for chases. Film vertical-friendly compositions: the subject in the centre third, empty space at the top for the counter.
   - AI fallback: paste the prompt plus the style suffix into Kling 2.x, Veo 3, Runway Gen-4, Sora or Hailuo. Use 9:16, 5 s, "cinematic", and camera control matching the shot's camera move.
3. **Assemble** the video. Run these from the repo root:
   ```bash
   pip install numpy pillow scipy
   python video/audio.py out/soundtrack.wav
   python video/render.py --overlay      # graphics with alpha
   python video/render.py --bg-only      # fallback plates
   python video/assemble.py --vo vo.wav  # -> out/gta6_10_things_FINAL.mp4
   ```
   `assemble.py` scales each clip to fill 9:16 and trims it to the shot length. It applies the camera move (push-in, pan, crash zoom…), grades the clip, adds the overlay, and ducks the music under your voice.
   **Manual alternative (CapCut):** put the footage on track 1 cut to the shot list, `overlay_prores4444.mov` on track 2, `soundtrack.wav` at −6 dB with your VO on top, and you're done.

Want to change a fact, a caption, a timing or an icon? Edit `video/timeline.py` and run the renders again. Everything (graphics, SFX, SRTs, shot list) comes from that one file.

---

## 2. Narration script (196 words, about 69 s)

| Time | Segment | Voice-over | On-screen subtitles (yellow = highlight) |
|---|---|---|---|
| 0.0–3.2 | **HOOK** | If you play GTA 6 like GTA 5… you're getting busted. | IF YOU PLAY **GTA 6** / LIKE **GTA 5**... / YOU'RE GETTING **BUSTED** |
| 3.2–5.0 | Title | Ten things you need to know. | **10** THINGS YOU NEED / TO **KNOW** BEFORE PLAYING |
| 5.0–10.6 | **1/10** | Two heroes. Jason and Lucia work as a team, and splitting up can shake the cops. | **TWO** HEROES / **JASON** AND **LUCIA** / SPLIT UP TO / SHAKE THE **COPS** |
| 10.6–15.8 | **2/10** | No witness, no crime. Police only come if someone sees you or an alarm goes off. | NO **WITNESS** / NO **CRIME** / SOMEONE **SEES** YOU / OR AN **ALARM** GOES OFF |
| 15.8–21.4 | **3/10** | Cops remember you. Your face, your outfit, your car. Change all three to disappear. | COPS **REMEMBER** YOU / **FACE. OUTFIT. CAR.** / CHANGE ALL **THREE** |
| 21.4–26.6 | **4/10** | Crime scenes stay hot. Go back too soon and the stars come right back. | **CRIME** SCENES / STAY **HOT** / GO BACK TOO **SOON...** / **STARS** COME BACK |
| 26.6–31.8 | **5/10** | Six stars are back. And at max heat, Leonida stops playing fair. | **SIX** STARS / ARE BACK / AT **MAX** HEAT / NO **MERCY** |
| 31.8–37.6 | **6/10** | You can't carry an arsenal. Two handguns, two long guns. The rest stays in the trunk. | NO MORE **ARSENAL** / **2** HANDGUNS / **2** LONG GUNS / REST IN THE **TRUNK** |
| 37.6–43.2 | **7/10** | Cash on you is at risk. Die or get busted and you lose it. Bank it at an ATM. | **CASH** ON YOU / IS AT **RISK** / DIE = YOU **LOSE** IT / BANK IT AT AN **ATM** |
| 43.2–49.6 | **8/10** | Vice City is just the start. Leonida has the Keys, Grassrivers, Port Gellhorn, Ambrosia and Mount Kalaga. | **VICE** CITY / IS JUST THE **START** / LEONIDA **KEYS** / **GRASSRIVERS** / PORT **GELLHORN** / **AMBROSIA** + KALAGA |
| 49.6–55.2 | **9/10** | Online isn't here yet. GTA Online for 6 is expected in 2027, and PC is coming later. | **ONLINE** ISN'T / HERE YET / EXPECTED IN **2027** / **PC** COMES LATER |
| 55.2–63.4 | **10/10** 🔥 | And the craziest part? GTA 6 made three point seven nine billion dollars on day one. The biggest entertainment launch in history. | THE **CRAZIEST** PART? / DAY **ONE:** / **$3.79 BILLION** (counts up from $0.00) / **BIGGEST** LAUNCH / IN **HISTORY** |
| 63.4–69.0 | CTA | Jason or Lucia, who are you playing first? Send this to the friend who's still downloading. | **JASON** OR **LUCIA?** / **COMMENT** BELOW / SEND THIS TO / YOUR **SQUAD** |

**Retention logic**
- The hook is a direct threat to the viewer ("you're getting busted"), with six wanted stars slamming in and a police strobe. There's no intro and no logo.
- The counter ring and 10 progress dots stay on screen the whole time, so viewers always know how far they are. That pulls them through to 10/10.
- Facts 2–5 build one story (how the new police system works). Each fact sets up the next.
- The music drops out for one second at 54.2 s, a riser plays, then everything slams back in at 10/10. The biggest fact (the record $3.79B launch) gets a gold count-up.
- The CTA is a binary question (Jason or Lucia), which gets easy comments, plus a targeted share line ("the friend who's still downloading").

---

## 3. Editing timeline (beat by beat)

Every 1–3 s brings a new shot, a new subtitle, an icon pop or a camera move. Cuts inside a fact get an automatic 12% punch-in.

| Time | Shot | Camera | Transition in | Graphics | SFX |
|---|---|---|---|---|---|
| 0.00 | hook_a: night chase on a causeway | crash zoom | white flash | subtitle pop | impact + siren |
| 1.70 | hook_b: light bar close-up | handheld | punch-in | **6 stars fill one by one**, red/blue edge strobe, screen shake | sub boom + glitch, beat drops |
| 3.20 | title_a: aerial sunset beach | pull-out | zoom punch | **counter ring builds in** ("10 THINGS"), pill title, dots | whoosh + ding |
| 5.00 | f1_a: duo at a neon motel | push-in | whip pan | ring → 1/10 (elastic pop + arc sweep), duo icon | whoosh + ding |
| 7.40 | f1_b: cars splitting at a fork | pan → | punch-in | split-arrow icon | swoosh up |
| 10.60 | f2_a: alley, witness on a phone | orbit | RGB glitch | 2/10, eye icon + animated chevrons | glitch + ding |
| 13.50 | f2_b: store robbery alarm | handheld | punch-in | alarm icon | alarm |
| 15.80 | f3_a: CCTV view | handheld | whip | 3/10, **REC ● timestamp CAM 04**, green CCTV grade, scanlines | whoosh + ding |
| 17.10 | f3_b: police suspect profile | push-in | punch-in | scan icon | 3 beeps synced to FACE / OUTFIT / CAR |
| 19.00 | f3_c: outfit + car change | pan ← | punch-in | – | – |
| 21.40 | f4_a: jewelry store crime scene | push-in | zoom punch | 4/10, flame icon | boom + shake |
| 23.60 | f4_b: drive past, cop points | crash zoom | punch-in | 3 stars + strobe | short siren |
| 26.60 | f5_a: helicopter over the highway | tilt up | flash | 5/10, 6 stars | impact + star ticks |
| 28.70 | f5_b: armored vans ramming | handheld | punch-in | strobe | helicopter |
| 31.80 | f6_a: weapons on a motel bed | orbit | spin (28°) | 6/10, 2+2 weapon-slot icon | whoosh + 2× reload |
| 35.10 | f6_b: trunk stash | push-in | punch-in | – | trunk thud |
| 37.60 | f7_a: duffel bag of cash | push-in | whip | 7/10, cash icon | cha-ching |
| 39.60 | – | – | – | skull icon on "DIE" | boom |
| 41.00 | f7_b: ATM at night | pan → | punch-in | – | – |
| 43.20 | f8_a: aerial beach city | pull-out | light leak | 8/10 | short riser |
| 45.20 | f8_b: overseas bridge | pan → | punch-in | pin icon | pop |
| 46.00 | f8_c: airboat in the swamp | push-in | punch-in | – | pop ×2 |
| 47.40 | f8_d: glowing state map, pins light up | pull-out | punch-in | – | pop |
| 49.60 | f9_a: nightclub lasers | orbit | glitch | 9/10, wifi-off icon | glitch |
| 52.90 | f9_b: PC "coming soon" | push-in | punch-in | clock icon | pop |
| 54.20 | – | – | – | – | **music cut + riser** |
| 55.20 | f10_a: vault opening | crash zoom | flash | 10/10 (ring complete) | impact |
| 57.20 | f10_b: money rain | push-in | punch-in | **gold $0.00 → $3.79 BILLION count-up**, trophy | boom + cash |
| 59.80 | f10_c: fireworks over the skyline | tilt up | punch-in | – | crowd |
| 63.40 | cta_a: duo at a convertible | orbit | whip | comment icon | whoosh + pop |
| 66.20 | cta_b: skyline pull-back | pull-out | punch-in | share icon | swoosh, music fades out |

---

## 4. Animation specs (to rebuild in After Effects or CapCut if you want)

**Circular counter.** Top centre, centre at (540, 205).
- Ring: outer radius 100 px, 16 px stroke. The background track is white at 22%.
- Progress arc: conic gradient **#FF2E88 → #FF9A1F**, rotating 120°/s. It has a 12 px gaussian outer glow at 160% intensity, and a white-hot spark dot at the arc head.
- Inner disc: #0E0618 at 75%.
- Text: number in Anton 92 px white with a 4 px black stroke, then "/10" in Anton 40 px #FFB46E.
- On each new fact, the arc sweeps from the previous value to n/10 over 0.5 s with ease-out-cubic, and the ring does an elastic scale pop of 1.28 → 1.0 over 0.7 s.

**Title pill.** At y = 360: "THINGS TO KNOW BEFORE GTA 6", Montserrat ExtraBold 30 px. The border is a horizontal pink→orange gradient, the fill #0C0614 at 85%. Below it sit 10 progress dots at y = 418: filled dots use the gradient and the current one pulses, empty dots are white at 35%.

**Subtitles.** Centre at y = 1020.
- Font: Anton 134 px, uppercase, white, 13 px black stroke. Drop shadow: offset y +12, blur 10, 65% black.
- Highlight words: gradient fill #FFE14D → #FFAA28.
- Maximum width 940 px. Text wraps to 2 lines automatically.
- Pop in: scale 0.55 → 1.15 (90 ms) → 1.0 (110 ms), rotation −3° → 0°, y +30 → 0. While held, a ±1.2% scale breath at 0.6 Hz.
- Hard cut to the next subtitle (TikTok style).
- The money figure is Anton 150 px with a gold gradient, counting up over 1.6 s with ease-out.

**Icons.** 240 px badges: gradient ring, dark disc, white and colour glyph, soft pink glow.
- Entry: elastic-out scale over 0.6 s. While held: ±6° wobble and 4% pulse.
- "Side" icons sit at (870, 700) with three yellow chevrons sliding toward them. "Low" icons sit at (540, 1330).
- Wanted stars: six 110 px stars that fill one by one every 110 ms with a back-out pop. They turn red in sync with the strobe.

**HUD.**
- GTA-style radar minimap bottom-left at (155, 1555), r = 98, with a rotating pink sweep, a moving road grid, blinking red and blue blips, and a white player arrow.
- Health bar (green) and armor bar (blue) under the minimap.
- Animated corner brackets that breathe at 110–160 alpha.
- Police strobe: red left-edge and blue right-edge gradients alternating at 4 Hz.

**Transitions** (into each fact, rotating so no two in a row are the same):
- Whip pan: 9-tap horizontal motion blur over 0.12 s out and 0.18 s in.
- Zoom punch: 1.45× → 1× over 0.35 s, with blur.
- Flash: white 100% → 0 over 0.3 s.
- Glitch: RGB split of 18 px plus row tearing for 0.3 s.
- Spin: 28° and 1.5× → 0 over 0.4 s.
- Light leak: an orange flare sweeping left to right over 0.7 s.

**Grade.** Soft tonemap, purple-lifted blacks, vignette, and 6% animated film grain. Real footage gets contrast 1.08 and saturation 1.15.

**Safe zones.** Nothing important goes in the bottom 350 px or right 140 px (TikTok UI). The counter sits under TikTok's top tabs (y > 100).

---

## 5. Sound design

- **Music:** synthwave/trap at 124 BPM in A minor (Am–F–C–G), with saw bass eighths, a detuned pad, kick, clap and hats. The filtered intro opens up on "BUSTED", there's a one-second break before 10/10, and a fade-out at the end.
- **SFX on every beat that matters:** whoosh on each transition, a ding when the counter ticks, impact or boom on big reveals (with screen shake), sirens, an alarm, CCTV beeps, star ticks, a helicopter, a weapon reload, a trunk thud, cha-ching, pops on map pins, a riser and a crowd cheer.
- **With voice-over:** music at −5 dB, sidechain-ducked about 8:1 under the VO. The VO gets a high-pass at 80 Hz and 3:1 compression.
- **Trending audio swap:** to use a trending TikTok sound, mute the music bed. Keep only the SFX by rendering with the music lines commented out in `audio.py → build_music`, then add the sound in-app at about 10% volume.

---

## 6. Posting kit

- **On-screen title / cover frame:** use the frame at 1.8 s ("YOU'RE GETTING BUSTED" with the 6 stars), or the 10/10 gold frame.
- **Caption:** "Number 10 is insane 🤯 Which one did you not know? #gta6 #gtavi #rockstargames #gta #gaming #vicecity #fyp"
- **Pinned first comment:** "Jason or Lucia? 👇 Wrong answers only 😂"
- **Post time:** 6–9 pm in your audience's time zone. Reply to early comments with short video replies to keep the post's reach climbing.

---

## 7. Fact-check notes (read before posting)

The facts come from Rockstar's own material, launch coverage and pre-launch previews. Check #6 and #7 in-game before you post, since they come from previews and could have changed at launch.

| # | Claim | Source / status |
|---|---|---|
| 1 | Jason and Lucia as a duo; splitting up can lower the heat | Rockstar trailers; splitting up comes from previews (reportedly removes a star) |
| 2 | A crime needs a witness or an alarm | Rockstar's Rob Nelson, quoted in previews |
| 3 | Police track face, clothes and vehicle | Previews (GamesRadar and others) |
| 4 | Crime scenes stay "hot" | Previews |
| 5 | Six-star wanted system | Previews (GamesRadar) |
| 6 | 2 handguns + 2 long guns, the rest in the vehicle | Previews. **Verify in-game** |
| 7 | Cash carried is lost on death or arrest; ATM deposits | Previews. **Verify in-game** |
| 8 | Leonida regions: Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia, Mount Kalaga | Rockstar's official Leonida reveal |
| 9 | Online expected in 2027; PC later | Launch coverage (Yahoo Tech / CBS). No official date |
| 10 | $3.79B in pre-orders plus first-day sales, "biggest entertainment launch in history" | Take-Two, via Variety |

**Channel safety:**
- No story spoilers, and no leaked footage. Use your own gameplay or official trailer material.
- Don't put graphic violence in the first 7 s (monetisation).
- The AI prompts describe characters and places generically ("a rugged man and a Latina woman", "Miami-style neon city"), so the generators make original lookalike scenes instead of copying Rockstar assets.
