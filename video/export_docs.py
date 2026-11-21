"""
Exports editor-friendly files from timeline.py into production/:
  captions.srt        - on-screen subtitle timings (import in CapCut / Premiere)
  voiceover.srt       - one cue per narration line (for TTS alignment)
  voiceover_script.txt
  shotlist.csv        - shot id, in/out, camera move, video-generation prompt
  SHOTLIST.md         - same, readable
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from timeline import SEGMENTS, all_captions, all_shots  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "production")

STYLE = ("Style: ultra-realistic next-gen open-world crime game look, Vice City / Miami-inspired, humid neon "
         "atmosphere, ray-traced reflections, wet asphalt, volumetric light, cinematic color grade "
         "(teal shadows, pink-orange highlights), anamorphic lens flare, motion blur, 24fps film feel, "
         "vertical 9:16, 1080x1920, no text, no logos, no watermark.")
NEGATIVE = ("Negative: text, captions, UI, logos, watermarks, distorted faces, extra fingers, warped cars, "
            "cartoon, low-poly, blurry, static camera, slideshow.")


def ts(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "captions.srt"), "w") as f:
        for i, c in enumerate(all_captions(), 1):
            f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n")
    with open(os.path.join(OUT, "voiceover.srt"), "w") as f:
        for i, s in enumerate(SEGMENTS, 1):
            f.write(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['vo']}\n\n")
    with open(os.path.join(OUT, "voiceover_script.txt"), "w") as f:
        f.write(" ".join(s["vo"] for s in SEGMENTS) + "\n")
    shots = all_shots()
    with open(os.path.join(OUT, "shotlist.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["shot_id", "segment", "in", "out", "duration", "camera", "placeholder_scene", "prompt"])
        for s in shots:
            w.writerow([s["id"], s["seg"], s["start"], s["end"], round(s["end"] - s["start"], 2), s["cam"], s["scene"],
                        s["prompt"] + " " + STYLE])
    cam_txt = dict(push_in="slow push-in", pull_out="drone pull-back", pan_l="lateral pan right-to-left",
                   pan_r="lateral pan left-to-right", tilt_up="tilt up / crane up", orbit="slow 20-degree orbit",
                   handheld="handheld shake", crash_zoom="fast crash zoom in the first 0.3 s")
    with open(os.path.join(OUT, "SHOTLIST.md"), "w") as f:
        f.write("# Shot list + video-generation prompts\n\n")
        f.write(f"Generate each shot at **9:16, 1080x1920, 5 s** (trimmed automatically) and save it as "
                f"`footage/<shot_id>.mp4`.\nAppend this to every prompt:\n\n> {STYLE}\n>\n> {NEGATIVE}\n\n")
        seg = None
        for s in shots:
            if s["seg"] != seg:
                seg = s["seg"]
                sg = next(x for x in SEGMENTS if x["id"] == seg)
                label = {"hook": "HOOK", "title": "TITLE", "cta": "CALL TO ACTION"}.get(seg, f"FACT {sg['counter']}/10")
                f.write(f"\n## {label}  ({sg['start']:.1f}s - {sg['end']:.1f}s)\n\n*VO:* \"{sg['vo']}\"\n\n")
            f.write(f"**`{s['id']}`**  {s['start']:.2f}s → {s['end']:.2f}s ({s['end'] - s['start']:.1f}s) · camera: "
                    f"{cam_txt[s['cam']]}\n\n> {s['prompt']}\n\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
