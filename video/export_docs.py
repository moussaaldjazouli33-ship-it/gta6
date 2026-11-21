"""
Exports editor files from timeline.py into production/:
  CLIPS_NEEDED.md      - the exact gameplay clips to capture, one per shot
  clips_needed.csv     - same as a spreadsheet / template for footage/clips.csv
  captions.srt         - on-screen subtitle timings
  voiceover.srt        - one cue per narration segment (record/generate VO to these)
  voiceover_script.txt - plain narration text
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from timeline import SEGMENTS, all_captions, all_shots  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "production")
CAM = dict(push_in="slow push-in", pull_out="slow pull-back", pan_l="pan right→left", pan_r="pan left→right",
           tilt_up="tilt up", handheld="handheld shake", crash_zoom="crash zoom", hold="slight drift")


def ts(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)):03d}"


def main():
    os.makedirs(OUT, exist_ok=True)
    for old in ("SHOTLIST.md", "shotlist.csv"):
        p = os.path.join(OUT, old)
        if os.path.exists(p):
            os.remove(p)
    with open(os.path.join(OUT, "captions.srt"), "w") as f:
        for i, c in enumerate(all_captions(), 1):
            f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n")
    with open(os.path.join(OUT, "voiceover.srt"), "w") as f:
        for i, s in enumerate(SEGMENTS, 1):
            f.write(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['vo']}\n\n")
    with open(os.path.join(OUT, "voiceover_script.txt"), "w") as f:
        f.write("\n".join(s["vo"] for s in SEGMENTS) + "\n")
    shots = all_shots()
    with open(os.path.join(OUT, "clips_needed.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["shot_id", "file", "start", "focus", "seconds_used", "capture_this"])
        for s in shots:
            w.writerow([s["id"], f"{s['id']}.mp4", 0, s["focus"], round(s["end"] - s["start"], 2), s["need"]])
    with open(os.path.join(OUT, "CLIPS_NEEDED.md"), "w") as f:
        f.write("# Gameplay clips needed (real GTA 6 captures only)\n\n"
                f"**{len(shots)} shots.** Record each one for **at least 5 seconds** (more is fine; the editor uses the "
                "first seconds, or the in-point you set in `footage/clips.csv`).\n\n"
                "Save as `footage/<shot_id>.mp4`, or record a few long sessions and map timecodes in "
                "`footage/clips.csv` (template: `production/clips_needed.csv`).\n\n"
                "**Capture settings:** PS5 Create button → video clip, 1080p or 4K, 60 fps, landscape 16:9 is fine "
                "(the editor crops 9:16 around `focus`). Turn the HUD/minimap OFF in Display settings, and turn in-game "
                "subtitles off unless noted. Keep the subject in the middle third. Use photo mode or the cinematic "
                "camera for hero shots. No story cutscene spoilers.\n\n"
                "Wait for a clean moment: no pause menus, notifications or party-chat pop-ups.\n")
        cur = None
        for s in shots:
            if s["seg"] != cur:
                cur = s["seg"]
                sg = next(x for x in SEGMENTS if x["id"] == cur)
                label = {"hook": "HOOK", "title": "TITLE", "cta": "OUTRO"}.get(cur, f"DETAIL {sg['counter']}/10")
                f.write(f"\n## {label} ({sg['start']:.1f}s – {sg['end']:.1f}s)\n*Voice-over:* \"{sg['vo']}\"\n\n"
                        "| File | Used | Capture this | Edit move |\n|---|---|---|---|\n")
            f.write(f"| `{s['id']}.mp4` | {s['end'] - s['start']:.1f}s | {s['need']} | {CAM[s['cam']]} |\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
