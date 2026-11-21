# GTA 6: 10 TRUCS À SAVOIR AVANT DE JOUER (project p2)
**TikTok · 9:16 · 1080×1920 · 30 fps · 57.4 s · French voice-over (ElevenLabs "Maxime")**

Output: `out/gta6_10_trucs_FINAL.mp4`
Sources:
- `footage/t1.mp4`: launch trailer, 16:9 1280×720.
- `footage/t2.mp4`: "Jason meets Lucia" scene, 16:9 1280×720.
- `footage/voiceover2.mp3`: the voice-over.

## Vertical conversion (`video/reframe.py`)
- **Full screen.** Every shot is a full-screen 9:16 crop of the 16:9 frame. It's never stretched, and there are no black bars or blurred fill.
- **Face tracking.**
  - OpenCV detects faces (frontal and both profiles) every 2nd frame.
  - The tracker follows the main character, and frames two people together when both fit.
  - The path is smoothed (median, Gaussian, speed limit) so the virtual camera glides.
  - Dark or action shots with too few faces (under 40% of samples) use an editor-set framing instead.
- **Quality.** Sub-pixel bicubic crop, light sharpening, same grade as the previous video.
- **Dialogue subtitles.** In t2 shots only the top 87% of the frame is used, so the burned-in subtitles stay out.
- **Clean frames.** Banned source ranges are listed in `video/projects/p2.py`: logos, "ROCKSTAR GAMES PRESENTS", title cards, credits overlays, animal credit cards and end cards. Shots touching them, transitions included, are refused.

## Graphics (same identity as the previous video)
No subtitles or text, and nothing in the centre. Small counter at the top, small "#n" in the upper-left corner, tiny icons at the edges synced to the voice-over: cash, gun, car, fuel pump, lightning bolt, alarm, padlock, moon, skull, heart, dumbbell, eye, door, paw, comment, share. Small wanted stars, edge particles, xfade transitions and camera moves.

## Rebuild
```bash
GTA_PROJECT=p2 python video/assemble.py --bg-only      # reframe + cut the footage
GTA_PROJECT=p2 python video/overlay.py --out out/gta6_10_trucs_overlay.mov
GTA_PROJECT=p2 python video/assemble.py --reuse-bg     # composite + mix
```
The previous video is project `p1` (`GTA_PROJECT=p1`).
