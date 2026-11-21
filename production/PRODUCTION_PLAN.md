# 10 CRAZY DETAILS YOU MISSED IN GTA 6
**TikTok · 9:16 · 1080×1920 · 30 fps · 68 s · American English · real GTA 6 gameplay only**

## Footage policy
The video uses **only real GTA 6 gameplay you capture on PS5 / Xbox Series**: no drawings, no 3D renders, no AI-generated scenes. The editor (`video/assemble.py`) refuses to build the final video while any clip is missing. For a timing test, `--allow-missing` puts a black "CLIP NEEDED" card where a clip is missing. It never invents footage.

## What you provide → what you get
| You provide | Where | |
|---|---|---|
| 33 gameplay clips (about 5 s each) | `footage/<shot_id>.mp4`, or long captures mapped in `footage/clips.csv` | see **`CLIPS_NEEDED.md`** |
| A voice-over (optional but recommended) | any `.wav` / `.mp3` | read `voiceover_script.txt`, timed to `voiceover.srt` |

```bash
python video/assemble.py --check          # lists present / missing clips
python video/assemble.py --vo vo.wav      # -> out/gta6_crazy_details_FINAL.mp4
```
`out/overlay_prores4444.mov` (the graphics with transparency) and `out/soundtrack.wav` are already rendered. For the manual route, put them over your clips in CapCut, Premiere or DaVinci.

---

## Script and subtitles (198 words)
| Time | # | Voice-over | Subtitles (bold = yellow highlight) |
|---|---|---|---|
| 0.0–3.2 | HOOK | Rockstar hid things in GTA 6... that almost nobody has found. | ROCKSTAR **HID** THINGS / IN **GTA 6...** / ALMOST **NOBODY** FOUND THEM |
| 3.2–5.0 | title | Ten crazy details you missed. | **10 CRAZY** DETAILS / YOU **MISSED** |
| 5.0–10.4 | 1 | Check your phone's ringtones. Wind Chimes is the exact tone Michael used in GTA 5. | CHECK YOUR **RINGTONES** / **"WIND CHIMES"** / **MICHAEL'S** RINGTONE / FROM **GTA 5** |
| 10.4–15.6 | 2 | There's an apartment that looks straight out of Dexter... but Rockstar won't let you inside. | A **DEXTER** APARTMENT / STRAIGHT OUT OF THE **SHOW** / BUT YOU CAN'T / GO **INSIDE** |
| 15.6–21.0 | 3 | A parrot named Tony keeps yelling generator. Follow the clue and you'll find a hidden cash stash. | **TONY** THE PARROT / KEEPS YELLING / **"GENERATOR"** / = HIDDEN **CASH** |
| 21.0–26.4 | 4 | Swim too far out, and a dog in goggles rides in on a jet ski to save you. | SWIM TOO **FAR** OUT / A **DOG** IN GOGGLES / ON A **JET SKI** / COMES TO **SAVE** YOU |
| 26.4–31.6 | 5 | Stay on board long enough... and it takes you to an island full of dogs. | STAY ON **BOARD...** / IT TAKES YOU TO / AN **ISLAND** / FULL OF **DOGS** |
| 31.6–37.2 | 6 | Climb a radio tower for seven minutes, throw an egg from the top, and a secret cutscene unlocks. | CLIMB A RADIO **TOWER** / FOR **7** MINUTES / THROW AN **EGG** / **SECRET** CUTSCENE |
| 37.2–42.6 | 7 | At a research facility, a giant mutant crab can ambush you. Yes, really. | **RESEARCH** FACILITY / **GIANT** MUTANT **CRAB** / YES. **REALLY.** |
| 42.6–48.4 | 8 | In some bars, people whisper about a secret bunker full of jetpacks, hidden under a mountain. | LISTEN IN **BARS** / A SECRET **BUNKER** / FULL OF **JETPACKS** / UNDER A **MOUNTAIN** |
| 48.4–54.2 | 9 | And there's a strange monument near Manifest Canyon. Players are calling it the new Mount Chiliad mystery. | A **STRANGE** MONUMENT / NEAR **MANIFEST** CANYON / THE NEW / **CHILIAD** MYSTERY |
| 54.2–62.6 | 10 | But the craziest one? A building in GTA 6 was hidden in the San Andreas remaster years ago. Rockstar was teasing us the whole time. | THE **CRAZIEST** ONE? / HIDDEN IN **SAN ANDREAS** / **YEARS** AGO / ROCKSTAR WAS **TEASING** US / THE **WHOLE** TIME |
| 62.6–68.0 | outro | Which one did you miss? Comment below, and send this to your squad. | WHICH ONE DID YOU **MISS?** / **COMMENT** BELOW / SEND THIS TO / YOUR **SQUAD** |

**Retention:**
- The hook promises a secret and opens a loop. The counter ring and 10 dots show progress all the way through.
- Details 4→5 are a two-part payoff (the dog, then the dog island). Details 8→9 build the mystery.
- The music cuts out for one second before #10, a riser plays, and the beat drops on the biggest reveal.
- The outro asks a question that's easy to answer in the comments.

## Voice-over and subtitle sync
I can't generate a voice here, so the subtitles are timed to the script (about 175 wpm, energetic US narrator).
- Record or generate each segment so it starts at the time in `voiceover.srt`. In ElevenLabs, use a US male narrator: Stability 35, Style 40, speed about 1.08.
- If your take runs longer or shorter, send me the audio file. I'll retime `video/timeline.py` (caption start times) to match it, and the overlay re-renders in about 2 minutes.

## Edit specs (built into the overlay and assembler)
- **Counter.** Top centre at y = 205.
  - Ring: radius 100 px, 16 px stroke, with a rotating conic gradient **#FF2E88 → #FF9A1F** and an outer glow.
  - Inside: the number in Anton, plus "/10" in orange.
  - On each new detail, the arc sweeps to the new value (0.5 s) and the ring does an elastic pop.
  - Underneath: the pill "CRAZY DETAILS YOU MISSED IN GTA 6" and 10 progress dots.
- **Subtitles.** Anton 134 px, white with a 13 px black outline and a soft drop shadow. Key words get a yellow→orange gradient. They pop in (0.55 → 1.15 → 1.0 in 0.2 s), centred at y = 1020.
- **Footage.**
  - Always full-screen. The 16:9 capture is cropped to 9:16 around `focus`.
  - Each shot gets a camera move: push-in, pull-back, pan, tilt, crash zoom or handheld.
  - A new shot every 1.2–3 s, with a 12% punch-in on each cut inside a detail.
  - Light grade: contrast 1.06, saturation 1.12, plus sharpening.
- **Transitions between details** (0.25 s): smooth whip, zoom-in, white flash, pixel glitch, radial spin, and a light leak.
- **Audio.**
  - Synthwave/trap bed at 124 BPM, music at −6 dB, automatically ducked under the voice.
  - Subtle SFX: whoosh on transitions, a ding on each counter tick, booms on reveals, a cash sound, pops, and a riser.
  - To use a trending TikTok sound instead, add it in-app at about 10% volume.
- **TikTok safe zones.** Nothing important in the bottom 350 px or right 140 px.

## Posting kit
- **Caption:** "#10 changes everything 👀 Which one did you miss? #gta6 #gtavi #rockstargames #gta #eastereggs #vicecity"
- **Pinned comment:** "Drop the craziest detail YOU found 👇"
- **Cover:** the hook frame with "ALMOST NOBODY FOUND THEM".

## Fact-check (early post-launch community finds, so confirm each one in your own capture)
These are early community finds. Filming each one yourself both verifies it and gives you the footage.
- Jet-ski dog and dog island; tower egg cutscene (about 7-minute climb, a callback to Vice City's Easter egg; parachuting onto the tower reportedly skips the climb); Dexter-style apartment (exterior only); Manifest Canyon monument; jetpack bunker talk in bars; Tony the parrot "generator" stash; "Wind Chimes" ringtone; giant mutant crab; San Andreas DE image matching a GTA 6 structure. Sources: ComicBook.com, GamingBible, BuzzFeed and others (launch week, Nov 2026).
- No story spoilers. Use your own captures, not leaked material.
