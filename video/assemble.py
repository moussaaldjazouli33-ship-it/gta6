"""
Cuts the final TikTok from REAL GTA 6 gameplay clips.

Footage sources (either or both):
  1. footage/<shot_id>.mp4 (or .mov/.mkv/.png/.jpg) - one clip per shot, used from its start
  2. footage/clips.csv - point shots into longer recordings:
         shot_id,file,start,focus
         f4_b,ps5_capture_03.mp4,12.5,0.62
     file is relative to footage/, start = in-point in seconds,
     focus = horizontal centre of the 9:16 crop (0..1, optional)

    python video/assemble.py --check            # what's present / missing
    python video/assemble.py --vo vo.wav        # out/gta6_crazy_details_FINAL.mp4
    python video/assemble.py --allow-missing    # test cut: black "CLIP NEEDED" cards for missing shots

Never fabricates footage: a missing shot is either an error or a black card.
Pipeline: 16:9 capture -> 9:16 crop at focus -> camera move (zoompan) ->
hard cuts inside a fact -> xfade transition between facts -> graphics
overlay (overlay.py) -> music/SFX ducked under the voice-over.
"""
import argparse
import csv
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from timeline import FPS, W, H, DURATION, SEGMENTS, all_shots  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FOOT = os.path.join(ROOT, "footage")
EXTS = (".mp4", ".mov", ".mkv", ".webm", ".png", ".jpg", ".jpeg")
IMG = (".png", ".jpg", ".jpeg")
XD = 0.25   # transition length between facts
XFADE = dict(whip="smoothleft", zoom_punch="zoomin", flash="fadewhite", glitch="pixelize",
             spin="radial", light_leak="fade")


def ff(*args):
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *args])


def sources():
    table = {}
    csv_path = os.path.join(FOOT, "clips.csv")
    if os.path.exists(csv_path):
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                p = os.path.join(FOOT, row["file"].strip())
                if os.path.exists(p):
                    table[row["shot_id"].strip()] = (p, float(row.get("start") or 0), row.get("focus") or None)
                else:
                    print(f"  ! clips.csv: {row['file']} not found")
    for s in all_shots():
        if s["id"] in table:
            continue
        for e in EXTS:
            p = os.path.join(FOOT, s["id"] + e)
            if os.path.exists(p):
                table[s["id"]] = (p, 0.0, None)
                break
    return table


def zoom_expr(cam, n, punch):
    p = f"(on/{n})"
    z = {"push_in": f"1.0+0.14*{p}", "pull_out": f"1.16-0.14*{p}", "crash_zoom": "1.0+0.28*min(1,on/9)",
         "handheld": "1.10", "hold": f"1.02+0.03*{p}", "pan_l": "1.18", "pan_r": "1.18", "tilt_up": "1.18"}[cam]
    if punch:
        z = f"({z})*(1+0.12*max(0,1-on/7.5))"
    x = "iw/2-(iw/zoom/2)"
    y = "ih/2-(ih/zoom/2)"
    if cam == "pan_l":
        x = f"(iw-iw/zoom)*(1-{p})"
    elif cam == "pan_r":
        x = f"(iw-iw/zoom)*{p}"
    elif cam == "tilt_up":
        y = f"(ih-ih/zoom)*(1-{p})"
    elif cam == "handheld":
        x = "iw/2-(iw/zoom/2)+14*sin(on/4)"
        y = "ih/2-(ih/zoom/2)+10*sin(on/3+1)"
    return z, x, y


def slate(shot, path):
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    fb = ImageFont.truetype(os.path.join(HERE, "assets", "fonts", "Anton.woff"), 90)
    fs = ImageFont.truetype(os.path.join(HERE, "assets", "fonts", "Montserrat-600.woff"), 40)
    d.text((W / 2, 1300), "CLIP NEEDED", font=fb, fill=(255, 60, 60), anchor="mm")
    d.text((W / 2, 1420), f"footage/{shot['id']}.mp4", font=fs, fill="white", anchor="mm")
    words, line, y = shot["need"].split(), "", 1500
    for w in words:
        if fs.getlength(line + " " + w) > 940:
            d.text((W / 2, y), line.strip(), font=fs, fill=(170, 170, 170), anchor="mm")
            line, y = "", y + 52
        line += " " + w
    d.text((W / 2, y), line.strip(), font=fs, fill=(170, 170, 170), anchor="mm")
    im.save(path)


def render_shot(shot, src, dur, punch, tmp):
    n = max(1, int(round(dur * FPS)))
    out = os.path.join(tmp, f"{shot['id']}.mp4")
    if src is None:
        png = os.path.join(tmp, f"{shot['id']}_slate.png")
        slate(shot, png)
        ff("-loop", "1", "-i", png, "-frames:v", str(n), "-r", str(FPS), "-pix_fmt", "yuv420p",
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "14", out)
        return out
    path, start, focus = src
    focus = float(focus) if focus not in (None, "") else shot["focus"]
    if path.lower().endswith(IMG):
        inp = ["-loop", "1", "-framerate", str(FPS), "-i", path]
    else:
        inp = ["-ss", f"{start}", "-stream_loop", "-1", "-i", path]
    z, x, y = zoom_expr(shot["cam"], n, punch)
    vf = (f"fps={FPS},scale=-2:{int(H * 1.25)}:flags=lanczos,"
          f"crop=w='min(iw,ih*9/16)':h=ih:x='(iw-min(iw,ih*9/16))*{focus}':y=0,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.06:saturation=1.12,unsharp=5:5:0.6,format=yuv420p")
    ff(*inp, "-vf", vf, "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", help="voice-over audio aligned to t=0 (see production/voiceover.srt)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--allow-missing", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "gta6_crazy_details_FINAL.mp4"))
    a = ap.parse_args()

    src = sources()
    shots = all_shots()
    missing = [s for s in shots if s["id"] not in src]
    print(f"{len(shots) - len(missing)}/{len(shots)} shots have real footage")
    for s in missing:
        print(f"  MISSING {s['id']:7s} {s['end'] - s['start']:4.1f}s  {s['need']}")
    if a.check:
        return
    if missing and not a.allow_missing:
        sys.exit("Add the missing clips (see production/CLIPS_NEEDED.md) or pass --allow-missing for a test cut.")

    overlay = os.path.join(ROOT, "out", "overlay_prores4444.mov")
    music = os.path.join(ROOT, "out", "soundtrack.wav")
    if not os.path.exists(music):
        subprocess.check_call([sys.executable, os.path.join(HERE, "audio.py"), music])
    if not os.path.exists(overlay):
        subprocess.check_call([sys.executable, os.path.join(HERE, "overlay.py")])

    tmp = tempfile.mkdtemp(prefix="gta6_")
    seg_clips = []
    for si, seg in enumerate(SEGMENTS):
        parts = []
        segshots = [s for s in shots if s["seg"] == seg["id"]]
        for k, s in enumerate(segshots):
            dur = s["end"] - s["start"]
            if k == len(segshots) - 1 and si < len(SEGMENTS) - 1:
                dur += XD            # tail overlap consumed by the xfade
            print(f"  cutting {s['id']}")
            parts.append(render_shot(s, src.get(s["id"]), dur, punch=k > 0, tmp=tmp))
        lst = os.path.join(tmp, f"{seg['id']}.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{p}'\n" for p in parts)
        sc = os.path.join(tmp, f"seg_{seg['id']}.mp4")
        ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", sc)
        seg_clips.append(sc)

    # chain xfades so each transition starts exactly on the fact boundary
    inputs, chain, last = [], [], "[0:v]"
    for i, p in enumerate(seg_clips):
        inputs += ["-i", p]
    for i in range(1, len(seg_clips)):
        tr = XFADE[SEGMENTS[i]["transition"]]
        lab = f"[x{i}]"
        chain.append(f"{last}[{i}:v]xfade=transition={tr}:duration={XD}:offset={SEGMENTS[i]['start']:.3f}{lab}")
        last = lab
    bg = os.path.join(tmp, "bg.mp4")
    ff(*inputs, "-filter_complex", ";".join(chain), "-map", last, "-c:v", "libx264", "-preset", "veryfast",
       "-crf", "14", "-pix_fmt", "yuv420p", bg)

    inputs = ["-i", bg, "-i", overlay, "-i", music]
    if a.vo:
        inputs += ["-i", a.vo]
        audio = ("[2:a]volume=0.5[m];[3:a]aresample=44100,highpass=f=80,acompressor=threshold=-18dB:ratio=3,"
                 "volume=1.6,asplit=2[vo][sc];[m][sc]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];"
                 "[duck][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    else:
        print("  note: no --vo given, the cut has music + SFX only")
        audio = "[2:a]anull[a]"
    fc = f"[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];{audio}"
    ff(*inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(DURATION),
       "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
