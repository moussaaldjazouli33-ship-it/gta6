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
from timeline import FPS, W, H, DURATION, SEGMENTS, VO_FILE, NAME, all_shots  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FOOT = os.path.join(ROOT, "footage")
from timeline import XFADE_D as XD  # noqa: E402
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


def zoom_for(shot, n, punch):
    z, x, y = zoom_expr(shot["cam"], n, punch, shot["badge"])
    if shot["badge"] and shot["flip"]:
        x = "0"        # mirrored: the badge is now bottom-right, anchor left instead
    return z, x, y


def _key(shot, dur, punch):
    import hashlib
    return hashlib.md5(repr((sorted((k, v) for k, v in shot.items() if k not in ("start", "end", "seg")), round(dur, 3), punch)).encode()).hexdigest()[:10]


def render_shot(shot, dur, punch, tmp):
    n = max(1, int(round(dur * FPS)))
    cache = os.path.join(ROOT, "out", "shot_cache", NAME)
    os.makedirs(cache, exist_ok=True)
    cached = os.path.join(cache, f"{shot['id']}_{_key(shot, dur, punch)}.mp4")
    if os.path.exists(cached):
        return cached
    out = cached
    path = os.path.join(FOOT, shot["src"] + "." + shot.get("ext", "mp4"))
    if shot.get("vertical_clean"):              # user's own vertical clips: text removal + camera move
        import reframe
        reframe.render_vertical(path, shot["src_in"], n, shot["cam"], punch, out, flip=shot.get("flip", False))
        print(f"  {shot['id']}: {shot['src']}@{shot['src_in']:.2f}s  cleaned", flush=True)
        return out
    if shot.get("reframe"):                     # 16:9 source -> tracked 9:16 crop
        import reframe
        tr = reframe.render(path, shot["src_in"], n, shot["cam"], punch, out, cx=shot["cx"], w=shot["w"],
                            subsafe=shot.get("subsafe", False), track=shot.get("track", False), flip=shot.get("flip", False),
                            bottom=shot.get("bottom", 0.87))
        mode = "extended" if shot["w"] > 0.33 else "full crop"
        print(f"  {shot['id']}: {shot['src']}@{shot['src_in']:.2f}s  {mode}{'  tracked' if tr else ''}", flush=True)
        return out
    z, x, y = zoom_for(shot, n, punch)
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
    ap.add_argument("--bg-only", action="store_true", help="only cut the footage track to out/bg_cut.mp4")
    ap.add_argument("--reuse-bg", action="store_true", help="skip cutting, reuse out/bg_cut.mp4")
    ap.add_argument("--preview", type=float, default=None, help="render only the first N seconds (quick check)")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", f"{NAME}_FINAL.mp4"))
    a = ap.parse_args()

    shots = all_shots()
    segments = SEGMENTS
    if a.preview:
        segments = [s for s in SEGMENTS if s["start"] < a.preview]
        shots = [s for s in shots if s["seg"] in {g["id"] for g in segments}]
    for s in shots:
        if not os.path.exists(os.path.join(FOOT, s["src"] + "." + s.get("ext", "mp4"))):
            sys.exit(f"missing footage/{s['src']}.mp4")
    if a.check:
        print(f"{len(shots)} shots OK")
        return
    vo = a.vo or (VO_FILE if os.path.exists(VO_FILE) else None)

    overlay = os.path.join(ROOT, "out", f"{NAME}_overlay.mov")
    music = os.path.join(ROOT, "out", f"{NAME}_soundtrack.wav")
    if not os.path.exists(music):
        subprocess.check_call([sys.executable, os.path.join(HERE, "audio.py"), music])
    if not os.path.exists(overlay) and not a.bg_only:
        subprocess.check_call([sys.executable, os.path.join(HERE, "overlay.py"), "--out", overlay])

    bg = os.path.join(ROOT, "out", f"{NAME}_bg{'_preview' if a.preview else ''}.mp4")
    if a.preview:
        overlay = os.path.join(ROOT, "out", f"{NAME}_overlay_preview.mov")
        if not os.path.exists(overlay) or True:
            subprocess.check_call([sys.executable, os.path.join(HERE, "overlay.py"), "--out", overlay, "--end", str(a.preview)])
        if a.out.endswith("_FINAL.mp4"):
            a.out = a.out.replace("_FINAL.mp4", "_PREVIEW.mp4")
    if not a.reuse_bg:
        tmp = tempfile.mkdtemp(prefix="gta6_")
        jobs = []
        for si, seg in enumerate(segments):
            segshots = [s for s in shots if s["seg"] == seg["id"]]
            for k, s in enumerate(segshots):
                dur = s["end"] - s["start"]
                if k == len(segshots) - 1 and si < len(segments) - 1:
                    dur += XD            # tail overlap consumed by the xfade
                jobs.append((s, dur, k > 0, tmp))
        from multiprocessing import Pool
        with Pool(os.cpu_count()) as pool:
            rendered = dict(zip([j[0]["id"] for j in jobs], pool.starmap(render_shot, jobs)))
        seg_clips = []
        for si, seg in enumerate(segments):
            parts = [rendered[s["id"]] for s in shots if s["seg"] == seg["id"]]
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
            tr = XFADE[segments[i]["transition"]]
            lab = f"[x{i}]"
            chain.append(f"{last}[{i}:v]xfade=transition={tr}:duration={XD}:offset={segments[i]['start']:.3f}{lab}")
            last = lab
        ff(*inputs, "-filter_complex", ";".join(chain), "-map", last, "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "14", "-pix_fmt", "yuv420p", bg)


    if a.bg_only:
        print("wrote", bg)
        return
    inputs = ["-i", bg, "-i", overlay, "-i", music]
    if vo:
        inputs += ["-i", vo]
        audio = ("[2:a]volume=0.30[m];[3:a]aresample=44100,highpass=f=80,acompressor=threshold=-18dB:ratio=3,"
                 "volume=1.6,asplit=2[vo][sc];[m][sc]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];"
                 "[duck][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000[a]")
    else:
        print("  note: no --vo given, the cut has music + SFX only")
        audio = "[2:a]anull[a]"
    fc = f"[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];{audio}"
    ff(*inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(a.preview or DURATION),
       "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
