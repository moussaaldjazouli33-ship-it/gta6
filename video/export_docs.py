"""
Exports editor files from timeline.py into production/:
  edit_list.csv       - every shot: timeline in/out, source clip, source in-point, camera move
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from timeline import all_shots  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "production")


def ts(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)):03d}"


def main():
    with open(os.path.join(OUT, "edit_list.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["shot", "segment", "timeline_in", "timeline_out", "source", "source_in", "camera", "mirrored", "badge_crop"])
        for s in all_shots():
            w.writerow([s["id"], s["seg"], s["start"], round(s["end"], 2), s["src"] + ".mp4", s["src_in"], s["cam"], s["flip"], s["badge"]])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
