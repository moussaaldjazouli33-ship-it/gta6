# GTA 6: 10 TRUCS À SAVOIR AVANT DE JOUER (project p2)
**TikTok · 9:16 · 1080×1920 · 30 fps · 57.4 s · French voice-over (ElevenLabs "Maxime")**

Output: `out/gta6_10_trucs_FINAL.mp4`
Sources:
- `footage/t1.mp4`: launch trailer, 16:9 1280×720.
- `footage/t2.mp4`: "Jason meets Lucia" scene, 16:9 1280×720.
- `footage/voiceover2.mp3`: the voice-over.

## Vertical conversion (`video/reframe.py`)
- **Per-shot framing.** All 44 shots were reviewed frame by frame. Each has a subject centre and the width that must stay visible: faces, upper bodies, both characters, or the main action.
- **Full crop (30 shots).** A full-height 9:16 window, with gentle body and face tracking where the subject is reliably detected.
- **Extended background (14 shots).** Used only where a 9:16 crop would cut characters or action: two-character shots, Jason polishing the boat, the crew, the sniper, the arm with the gun. The wider window stays sharp in the middle over a natural blurred extension of the same shot, in its own colours. No split screens, no side-by-side layouts.
- **Image quality.**
  - Light temporal noise reduction, then ESRGAN-slim x2 AI super-resolution.
  - The model is converted to ONNX (`video/build_sr_onnx.py`) and run on the CPU in tiles.
  - Wide windows are super-resolved at native resolution.
  - Gentle sharpening, and small camera moves only (at most about 4% zoom).
- **Clean frames.** Burned-in dialogue subtitles are cropped out (bottom 13%, 20% for the driving shot), and so is the channel watermark. Logos, title cards, credits and end cards are banned source ranges.
- **Shot cache.** Rendered shots are cached in `out/shot_cache/`, so a fix re-renders only the shot that changed.

## Graphics (same identity as the previous video)
No subtitles or text, and nothing in the centre. Small counter at the top, small "#n" in the upper-left corner, tiny icons at the edges synced to the voice-over: cash, gun, car, fuel pump, lightning bolt, alarm, padlock, moon, skull, heart, dumbbell, eye, door, paw, comment, share. Small wanted stars, edge particles, xfade transitions and camera moves.

## Rebuild
```bash
GTA_PROJECT=p2 python video/assemble.py --bg-only      # reframe + cut the footage
GTA_PROJECT=p2 python video/overlay.py --out out/gta6_10_trucs_overlay.mov
GTA_PROJECT=p2 python video/assemble.py --reuse-bg     # composite + mix
```
The previous video is project `p1` (`GTA_PROJECT=p1`).
