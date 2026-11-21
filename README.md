# GTA 6 TikTok edit: "10 DÉTAILS QUE PERSONNE NE CONNAÎT"

A 69.6 s vertical (1080×1920) TikTok, edited from **real GTA 6 footage** and a French voice-over.

What the code does:
- Syncs the subtitles word by word to the voice (Whisper word timestamps).
- Puts a glowing pink/orange circular counter at the top that pops on each spoken number.
- Moves the camera in every shot, with transitions between details.
- Adds icons, music and SFX.

```bash
pip install numpy pillow scipy        # ffmpeg required
# footage/c1..c5.mp4 + footage/voiceover.mp3 (not committed)
python video/audio.py out/soundtrack.wav
python video/overlay.py               # graphics layer with alpha
python video/assemble.py              # -> out/gta6_10_details_FINAL.mp4
```

See [`production/PRODUCTION_PLAN.md`](production/PRODUCTION_PLAN.md). The edit is defined in [`video/timeline.py`](video/timeline.py).
