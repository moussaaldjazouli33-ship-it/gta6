# GTA 6 TikTok: "10 THINGS YOU NEED TO KNOW BEFORE PLAYING GTA 6"

A complete, code-driven production kit for a 69-second vertical (1080×1920) viral GTA 6 edit:
- an animated pink→orange circular counter
- big pop-in subtitles
- GTA-style HUD (radar, wanted stars, CCTV)
- animated icons
- whip, glitch, flash, spin and light-leak transitions
- a synced synthwave soundtrack with SFX

- **Read first:** [`production/PRODUCTION_PLAN.md`](production/PRODUCTION_PLAN.md). It has the script, timeline, animation specs, sound design, posting kit and fact-check notes.
- **Prompts per shot:** [`production/SHOTLIST.md`](production/SHOTLIST.md)

```bash
pip install numpy pillow scipy          # ffmpeg must be installed
python video/audio.py out/soundtrack.wav
python video/render.py                  # out/gta6_10_things.mp4 (placeholder backgrounds)
python video/render.py --overlay        # out/overlay_prores4444.mov (graphics with alpha)
python video/render.py --bg-only        # out/bg_placeholder.mp4
# put real clips in footage/<shot_id>.mp4, then:
python video/assemble.py --vo vo.wav    # out/gta6_10_things_FINAL.mp4
python video/export_docs.py             # regenerate SRTs / shot list after editing the timeline
```

Everything is driven by [`video/timeline.py`](video/timeline.py).
