"""
Cuts the final TikTok from the REAL GTA 6 clips in footage/ (c1..c5.mp4) and
the voice-over (footage/voiceover.mp3), following the shot list in timeline.py.

    python video/assemble.py --check
    python video/assemble.py            # -> out/gta6_10_details_FINAL.mp4

Pipeline per shot: source in-point -> optional mirror -> 2x upscale ->
zoompan camera move (push-in, pull-out, pan, crash zoom, handheld; badge
shots are cropped so the ESRB corner badge is out of frame) -> light grade.
Hard cuts inside a detail, xfade transitions between details, the
graphics overlay from overlay.py on top, music + SFX ducked under the voice.
"""
import argparse
import os
import subprocess
import sys
import tempfile


sys.path.insert(0, os.path.dirname(__file__))
from timeline import FPS, W, H, DURATION, SEGMENTS, VO_FILE, all_shots  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FOOT = os.path.join(ROOT, "footage")
XD = 0.25   # transition length between facts
XFADE = dict(whip="smoothleft", zoom_punch="zoomin", flash="fadewhite", glitch="pixelize",
             spin="radial", light_leak="fade")


def ff(*args):
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *args])


def zoom_expr(cam, n, punch, badge):
    p = f"(on/{n})"
    z = {"push_in": f"1.06+0.12*{p}", "pull_out": f"1.20-0.12*{p}", "crash_zoom": "1.06+0.24*min(1,on/9)",
         "handheld": "1.12", "hold": f"1.06+0.03*{p}", "pan_l": "1.18", "pan_r": "1.18", "tilt_up": "1.18"}[cam]
    if punch:
        z = f"({z})*(1+0.10*max(0,1-on/7.5))"
    x = "iw/2-(iw/zoom/2)"
    y = "ih/2-(ih/zoom/2)"
    if cam == "pan_l":
        x = f"(iw-iw/zoom)*(1-{p})"
    elif cam == "pan_r":
        x = f"(iw-iw/zoom)*{p}"
    elif cam == "handheld":
        x = "iw/2-(iw/zoom/2)+16*sin(on/4)"
        y = "ih/2-(ih/zoom/2)+12*sin(on/3+1)"
    if badge:   # crop the ESRB corner badge (bottom-left): zoom >= 1.24, anchor top-right
        z = f"max(1.24,{z})"
        x = "iw-iw/zoom"
        y = "(ih-ih/zoom)*0.15"
    return z, x, y


def render_shot(shot, dur, punch, tmp):
    n = max(1, int(round(dur * FPS)))
    out = os.path.join(tmp, f"{shot['id']}.mp4")
    path = os.path.join(FOOT, shot["src"] + ".mp4")
    z, x, y = zoom_expr(shot["cam"], n, punch, shot["badge"])
    vf = (f"fps={FPS},{'hflip,' if shot['flip'] else ''}scale={W * 2}:{H * 2}:flags=lanczos,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.05:saturation=1.10,unsharp=5:5:0.5,format=yuv420p")
    ff("-ss", f"{shot['src_in']}", "-i", path, "-vf", vf, "-frames:v", str(n), "-an",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", out)
    got = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
    if got < dur - 0.05:
        sys.exit(f"{shot['id']}: source {shot['src']} too short from {shot['src_in']}s ({got:.2f}s < {dur:.2f}s)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", help="voice-over audio aligned to t=0 (see production/voiceover.srt)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "gta6_10_details_FINAL.mp4"))
    a = ap.parse_args()

    shots = all_shots()
    for s in shots:
        if not os.path.exists(os.path.join(FOOT, s["src"] + ".mp4")):
            sys.exit(f"missing footage/{s['src']}.mp4")
    if a.check:
        print(f"{len(shots)} shots OK")
        return
    vo = a.vo or (VO_FILE if os.path.exists(VO_FILE) else None)

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
            parts.append(render_shot(s, dur, punch=k > 0, tmp=tmp))
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
    if vo:
        inputs += ["-i", vo]
        audio = ("[2:a]volume=0.30[m];[3:a]aresample=44100,highpass=f=80,acompressor=threshold=-18dB:ratio=3,"
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
