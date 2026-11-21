# GTA 6 TikTok: "10 CRAZY DETAILS YOU MISSED IN GTA 6"

A 68-second vertical (1080×1920) edit built **only from real GTA 6 gameplay you capture**. It has:
- an animated pink/orange circular counter
- big outlined subtitles
- camera moves and transitions
- music and SFX

1. Capture the clips in [`production/CLIPS_NEEDED.md`](production/CLIPS_NEEDED.md) and save them in `footage/`.
2. Optionally, record the voice-over: [`production/voiceover_script.txt`](production/voiceover_script.txt).
3. Run the editor:

```bash
pip install numpy pillow scipy           # ffmpeg required
python video/assemble.py --check         # what's missing
python video/assemble.py --vo vo.wav     # -> out/gta6_crazy_details_FINAL.mp4
```

Script, specs and posting kit: [`production/PRODUCTION_PLAN.md`](production/PRODUCTION_PLAN.md). Everything is driven by [`video/timeline.py`](video/timeline.py). After editing it, run `python video/overlay.py` and `python video/export_docs.py`.
