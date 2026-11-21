# GTA 6: 10 DÉTAILS QUE PERSONNE NE CONNAÎT
**TikTok · 9:16 · 1080×1920 · 30 fps · 69.6 s · French voice-over (ElevenLabs "Nicolas")**

The final video is `out/gta6_10_details_FINAL.mp4`, built only from the real GTA 6 clips you supplied (`footage/c1–c5.mp4`) and your voice-over (`footage/voiceover.mp3`).

## How it was edited
- **Sync.** I transcribed the voice-over with Whisper, which gives a timestamp for every word. Spelling was fixed by hand ("répondeur", "GTA 6", "PNJ", "trottinette"). The result is in `vo_words.json`.
  - Each detail starts exactly on its spoken number ("1.", "2." …). The counter pops at that moment, along with a transition, a whoosh and a ding.
- **Footage.** 40 shots, with a new shot every 0.6–2.5 s. Each one was picked to match its sentence:

| Detail | What the voice says | Shots used |
|---|---|---|
| Hook | Lucia on voicemail / your relationship hits rock bottom | Lucia in the elevator, the couple walking, underwater shot |
| Title | 10 details | skydive over Vice City, neon street, DJ |
| 1 | ignored calls and texts | Lucia in the club, Jason in the elevator, rooftop bar |
| 2 | Lucia drives, Jason shoots | police truck charging, street shootout, getaway truck |
| 3 | pull a gun in the street | shootout, passers-by on the rooftop |
| 4 | hand-to-hand: Lucia vs Jason | Lucia at the gym, Jason, close-ups |
| 5 | cap and sunglasses | guy in sunglasses, guy in a cap, group wearing shades |
| 6 | robbing a convenience store | helicopter shootout, night crew, police truck |
| 7 | clothes in the trunk / losing the cops | rooftop outfits, police |
| 8 | arrest / confiscated weapons | police shootout, Jason |
| 9 | car delivered, valet leaves on a scooter | airboat, the **scooter** shot |
| 10 | NPCs rob stores | night crew, shootout (mirrored reuse) |
| Outro | Jason or Lucia? / follow | Jason, Lucia, skydive and parachute |

  - Logos, Rockstar end cards, "PRE-LOAD NOW" text and the PS5 splash screens were left out.
  - In the first seconds of some clips, a small ESRB rating badge sits in a corner. Those shots are zoomed and reframed so it's out of frame.
- **Camera.** Every shot moves (push-in, pull-out, pan, crash zoom, handheld), and each cut inside a detail gets a 10% punch-in.
  - Transitions between details: smooth whip, zoom, white flash, pixel glitch, radial spin, light leak.
- **Graphics** (`video/overlay.py`): **no text on screen at all**, apart from the small counter.
  - Small circular pink/orange counter at the top centre (0/10 → 10/10) with progress dots and a soft ring pulse on each spoken number.
  - Small floating gaming icons (about 86 px, two at most at a time, either side of the centre) appear on the matching words. Icons: phone, car, gun, eye, heart, cash, police, location, flame, share.
  - Thin glowing rings on characters (Lucia / Jason), small wanted stars on police moments, a compact radar, faint particles, and a soft light sweep on transitions.
- **Clean footage only.** Banned source ranges (logos, PRE-LOAD NOW, PS5 splash, end cards) are listed in `timeline.py`. Any shot touching them, transitions included, is refused.
- **Audio.** Your voice-over is level-controlled. The synthwave bed sits low at 30% and is ducked further whenever you speak. Subtle SFX: whoosh, ding, impact, cash, riser.

## Files
- `edit_list.csv`: every shot, with timeline in/out, source clip, in-point and camera move.
- `vo_words.json`: word timings.

## Rebuild after a change
Edit `video/timeline.py`, for example a shot's source or in-point, then run:
```bash
python video/overlay.py && python video/assemble.py
```
