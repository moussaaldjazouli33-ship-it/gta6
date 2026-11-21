"""
Final assembly with REAL footage.

Drop your clips (gameplay captures, official trailer cuts you are allowed to
use, or AI-generated shots from PRODUCTION_PLAN.md) into footage/ named after
the shot ids in timeline.py, e.g.

    footage/hook_a.mp4   footage/f3_b.mov   footage/f8_d.png ...

Any shot without a file falls back to the procedural placeholder plate.

    python video/render.py --overlay        # once: graphics layer with alpha
    python video/render.py --bg-only        # once: placeholder plates (fallback)
    python video/assemble.py [--vo voiceover.wav]

Each clip is scaled to cover 1080x1920, trimmed to the shot length and given
the shot's camera move (push-in, pan, crash zoom...). The overlay (counter,
subtitles, HUD, icons, flashes) is composited on top, and the soundtrack is
mixed with your voice-over, ducked under the voice automatically.
"""
import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from timeline import FPS, W, H, DURATION, all_shots  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXTS = (".mp4", ".mov", ".mkv", ".webm", ".png", ".jpg", ".jpeg")


def find_clip(sid):
    for e in EXTS:
        p = os.path.join(ROOT, "footage", sid + e)
        if os.path.exists(p):
            return p
    return None


def cam_filter(cam, dur):
    """Scale-to-cover + animated crop implementing the camera move."""
    n = max(1, int(round(dur * FPS)))
    p = f"(on/{n})"                                   # 0..1 progress
    zoom = {
        "push_in": f"1.04+0.16*{p}",
        "pull_out": f"1.22-0.16*{p}",
        "crash_zoom": f"1.02+0.30*min(1,on/10)",
        "handheld": "1.12",
        "orbit": f"1.14+0.04*{p}",
    }.get(cam, "1.2")
    x = "iw/2-(iw/zoom/2)"
    y = "ih/2-(ih/zoom/2)"
    if cam == "pan_l":
        x = f"(iw-iw/zoom)*(1-{p})"
    elif cam == "pan_r":
        x = f"(iw-iw/zoom)*{p}"
    elif cam == "tilt_up":
        y = f"(ih-ih/zoom)*(1-{p})"
    elif cam == "handheld":
        x = f"iw/2-(iw/zoom/2)+12*sin(on/4)"
        y = f"ih/2-(ih/zoom/2)+10*sin(on/3+1)"
    cover = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
             f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}")
    return cover


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", help="voice-over wav/mp3, aligned to t=0")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "gta6_10_things_FINAL.mp4"))
    a = ap.parse_args()

    overlay = os.path.join(ROOT, "out", "overlay_prores4444.mov")
    placeholder = os.path.join(ROOT, "out", "bg_placeholder.mp4")
    music = os.path.join(ROOT, "out", "soundtrack.wav")
    for p, how in ((overlay, "render.py --overlay"), (music, "audio.py out/soundtrack.wav")):
        if not os.path.exists(p):
            sys.exit(f"missing {p} - run: python video/{how}")

    tmp = tempfile.mkdtemp(prefix="gta6_")
    parts = []
    for s in all_shots():
        dur = s["end"] - s["start"]
        src = find_clip(s["id"])
        part = os.path.join(tmp, f"{s['id']}.mp4")
        if src:
            is_img = src.lower().endswith((".png", ".jpg", ".jpeg"))
            inp = ["-loop", "1", "-t", f"{dur}", "-i", src] if is_img else ["-stream_loop", "-1", "-t", f"{dur}", "-i", src]
            vf = cam_filter(s["cam"], dur) + ",eq=contrast=1.08:saturation=1.15,vignette=PI/5"
            print(f"[footage]     {s['id']:7s} {dur:5.2f}s  {os.path.basename(src)}")
        else:
            if not os.path.exists(placeholder):
                sys.exit(f"no clip for {s['id']} and no {placeholder} - run: python video/render.py --bg-only")
            inp = ["-ss", f"{s['start']}", "-t", f"{dur}", "-i", placeholder]
            vf = "null"
            print(f"[placeholder] {s['id']:7s} {dur:5.2f}s")
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *inp, "-vf", vf + f",fps={FPS},format=yuv420p",
                               "-frames:v", str(int(round(dur * FPS))), "-an", "-c:v", "libx264", "-crf", "16", part])
        parts.append(part)

    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    bg = os.path.join(tmp, "bg.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", bg])

    inputs = ["-i", bg, "-i", overlay, "-i", music]
    if a.vo:
        inputs += ["-i", a.vo]
        audio = ("[2:a]volume=0.55[m];[3:a]aresample=44100,highpass=f=80,acompressor=threshold=-18dB:ratio=3,"
                 "volume=1.6,asplit=2[vo][sc];[m][sc]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];"
                 "[duck][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    else:
        audio = "[2:a]anull[a]"
    fc = f"[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];{audio}"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                           "-t", str(DURATION), "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", a.out])
    print("wrote", a.out)


if __name__ == "__main__":
    main()
