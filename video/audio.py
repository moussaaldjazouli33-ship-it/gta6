"""
Procedural soundtrack + SFX for the GTA 6 TikTok edit.

Builds a synthwave/trap bed (Vice-City mood) with drops synced to the
timeline, then lays every SFX cue from timeline.SEGMENTS on top.
Writes a 44.1 kHz stereo 16-bit WAV.

    python video/audio.py out/soundtrack.wav
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, lfilter

from timeline import SEGMENTS, DURATION

SR = 44100
RNG = np.random.default_rng(7)


# ----------------------------------------------------------------- helpers
def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_exp(dur, decay):
    return np.exp(-t_axis(dur) * decay)


def lp(x, hz, order=2):
    b, a = butter(order, min(hz / (SR / 2), 0.99), "low")
    return lfilter(b, a, x)


def hp(x, hz, order=2):
    b, a = butter(order, min(hz / (SR / 2), 0.99), "high")
    return lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], "band")
    return lfilter(b, a, x)


def noise(dur):
    return RNG.uniform(-1, 1, int(dur * SR))


def saw(freq, t):
    return 2.0 * ((t * freq) % 1.0) - 1.0


def place(buf, clip, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i < 0:
        clip = clip[-i:]
        i = 0
    n = min(len(clip), buf.shape[0] - i)
    if n <= 0:
        return
    l = np.sqrt(0.5 * (1 - pan))
    r = np.sqrt(0.5 * (1 + pan))
    buf[i:i + n, 0] += clip[:n] * gain * l * 1.414
    buf[i:i + n, 1] += clip[:n] * gain * r * 1.414


def sweep_bp_noise(dur, f0, f1, q=0.35):
    """Noise through a band-pass whose centre glides f0 -> f1 (block-wise)."""
    n = noise(dur)
    out = np.zeros_like(n)
    blocks = 32
    size = len(n) // blocks + 1
    for k in range(blocks):
        f = f0 * (f1 / f0) ** (k / (blocks - 1))
        seg = n[k * size:(k + 1) * size]
        if not len(seg):
            break
        out[k * size:k * size + len(seg)] = bp(seg, max(40, f * (1 - q)), f * (1 + q))
    return out


# ----------------------------------------------------------------- SFX bank
def sfx_whoosh(dur=0.45, up=False):
    f0, f1 = (300, 4000) if up else (3500, 250)
    x = sweep_bp_noise(dur, f0, f1)
    t = t_axis(dur)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return x * e * 2.2


def sfx_impact():
    dur = 1.2
    t = t_axis(dur)
    f = 90 * np.exp(-t * 6) + 38
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(dur, 3.2)
    crack = hp(noise(dur), 1500) * env_exp(dur, 30) * 0.6
    return np.tanh((body + crack) * 2.0) * 0.9


def sfx_boom():
    dur = 2.0
    t = t_axis(dur)
    f = 60 * np.exp(-t * 3) + 30
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(dur, 1.8)
    rumble = lp(noise(dur), 180) * env_exp(dur, 2.5) * 2.0
    return np.tanh((sub + rumble) * 2.5) * 0.85


def sfx_ding():
    dur = 1.0
    t = t_axis(dur)
    x = (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t)
         + 0.25 * np.sin(2 * np.pi * 3951 * t)) * env_exp(dur, 6)
    return x * 0.35


def sfx_glitch():
    dur = 0.35
    n = int(dur * SR)
    out = np.zeros(n)
    i = 0
    while i < n:
        L = RNG.integers(300, 2500)
        kind = RNG.integers(0, 3)
        tt = np.arange(L) / SR
        if kind == 0:
            seg = np.sign(np.sin(2 * np.pi * RNG.uniform(80, 1600) * tt))
        elif kind == 1:
            seg = RNG.uniform(-1, 1, L)
        else:
            seg = np.zeros(L)
        out[i:i + L] = seg[:max(0, min(L, n - i))]
        i += L
    return np.round(out * 4) / 4 * 0.35


def sfx_siren(dur=1.4):
    t = t_axis(dur)
    f = 850 + 250 * np.sign(np.sin(2 * np.pi * 2.2 * t))
    f = lp(f, 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x = np.tanh(x * 1.5)
    e = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.3)
    return lp(x, 3000) * e * 0.25


def sfx_alarm():
    dur = 1.2
    t = t_axis(dur)
    gate = (np.sin(2 * np.pi * 6 * t) > 0).astype(float)
    x = np.sign(np.sin(2 * np.pi * 950 * t)) * gate
    return lp(x, 4000) * 0.12


def sfx_beep():
    dur = 0.09
    t = t_axis(dur)
    return np.sin(2 * np.pi * 1760 * t) * np.minimum(1, (dur - t) / 0.02) * 0.25


def sfx_star_ticks():
    out = np.zeros(int(1.0 * SR))
    for k in range(6):
        c = sfx_beep() * (0.7 + 0.06 * k)
        i = int(k * 0.11 * SR)
        out[i:i + len(c)] += c
    return out


def sfx_heli(dur=2.6):
    t = t_axis(dur)
    chop = (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t)) ** 6
    x = lp(noise(dur), 400) * chop * 3
    e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.6)
    return x * e * 0.6


def sfx_click(f=3000):
    dur = 0.06
    return bp(noise(dur), f * 0.6, f * 1.4) * env_exp(dur, 80) * 1.4


def sfx_reload():
    out = np.zeros(int(0.4 * SR))
    for at, f in ((0.0, 2500), (0.14, 1600)):
        c = sfx_click(f)
        i = int(at * SR)
        out[i:i + len(c)] += c
    return out


def sfx_thud():
    dur = 0.5
    t = t_axis(dur)
    return np.sin(2 * np.pi * (70 * np.exp(-t * 8) + 45) * t) * env_exp(dur, 9) * 0.9


def sfx_cash():
    dur = 1.0
    t = t_axis(dur)
    drawer = hp(noise(dur), 2000) * env_exp(dur, 25) * 0.5
    bell = (np.sin(2 * np.pi * 2093 * t) + np.sin(2 * np.pi * 2637 * t)) * env_exp(dur, 5) * 0.25
    bell = np.roll(bell, int(0.08 * SR))
    return drawer + bell


def sfx_pop():
    dur = 0.18
    t = t_axis(dur)
    f = 900 * np.exp(-t * 25) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(dur, 20) * 0.45


def sfx_riser(dur=1.0):
    t = t_axis(dur)
    tone = saw(110 * 2 ** (t / dur * 2.5), t) * 0.25
    nz = sweep_bp_noise(dur, 300, 8000) * 1.5
    e = (t / dur) ** 2
    return lp(tone, 4000) * e + nz * e


def sfx_crowd():
    dur = 2.5
    t = t_axis(dur)
    x = bp(noise(dur), 400, 3000) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t + 3 * np.sin(5 * t)))
    e = np.minimum(1, t / 0.5) * np.minimum(1, (dur - t) / 1.0)
    return x * e * 0.6


SFX = {
    "whoosh": (lambda: sfx_whoosh(), 0.7),
    "swoosh_up": (lambda: sfx_whoosh(0.4, up=True), 0.6),
    "impact": (sfx_impact, 0.9),
    "boom": (sfx_boom, 0.8),
    "ding": (sfx_ding, 0.55),
    "glitch": (sfx_glitch, 0.6),
    "siren": (lambda: sfx_siren(1.6), 0.6),
    "siren_short": (lambda: sfx_siren(1.0), 0.5),
    "alarm": (sfx_alarm, 0.6),
    "beep": (sfx_beep, 0.6),
    "star_ticks": (sfx_star_ticks, 0.6),
    "heli": (sfx_heli, 0.6),
    "reload": (sfx_reload, 0.8),
    "thud": (sfx_thud, 0.8),
    "cash": (sfx_cash, 0.8),
    "pop": (sfx_pop, 0.6),
    "riser": (lambda: sfx_riser(1.0), 0.6),
    "riser_short": (lambda: sfx_riser(0.6), 0.45),
    "crowd": (sfx_crowd, 0.5),
}


# ----------------------------------------------------------------- music bed
BPM = 124
BEAT = 60 / BPM
# Am - F - C - G  (synthwave classic), one chord per bar
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
ROOTS = [45, 41, 36, 43]


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def kick():
    dur = 0.35
    t = t_axis(dur)
    f = 120 * np.exp(-t * 30) + 45
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(dur, 9) * 2.5)


def clap():
    dur = 0.25
    return bp(noise(dur), 900, 4500) * env_exp(dur, 18) * 1.2


def hat(open_=False):
    dur = 0.18 if open_ else 0.05
    return hp(noise(dur), 7000) * env_exp(dur, 18 if open_ else 70) * 0.5


def build_music(total):
    buf = np.zeros((int(total * SR), 2))
    K, C, Ho, Hc = kick(), clap(), hat(True), hat(False)

    # sections: (start, end, drums_on, filter_closed)
    counted = [s for s in SEGMENTS if s["counter"]]
    drums_from = next((s["start"] for s in SEGMENTS if s["counter"] is not None), SEGMENTS[1]["start"])
    if counted:
        f10 = max(counted, key=lambda s: (s["counter"], -s["start"]))
        break_start, break_end = f10["start"] - 1.0, f10["start"]     # silence-ish before the last item
    else:
        drop = next((s for s in SEGMENTS if s.get("drop")), None)
        break_start, break_end = (drop["start"] - 1.0, drop["start"]) if drop else (-9, -9)
    end_fade = total - 2.0

    n_beats = int(total / BEAT) + 2
    for b in range(n_beats):
        tb = drums_from + b * BEAT
        if tb >= total:
            break
        if break_start <= tb < break_end:
            continue
        place(buf, K, tb, 0.55)
        if b % 2 == 1:
            place(buf, C, tb, 0.35, pan=0.1)
        place(buf, Hc, tb + BEAT / 2, 0.25, pan=-0.3)
        if b % 4 == 3:
            place(buf, Ho, tb + BEAT / 2, 0.2, pan=0.3)
        # 16th hat rolls into each fact (every 8 bars-ish feel)
        if b % 16 == 15:
            for k in range(4):
                place(buf, Hc, tb + k * BEAT / 4, 0.2, pan=-0.3)

    # bass (8ths) + pad, chord per bar, starting from the very beginning
    bar = BEAT * 4
    t_all = t_axis(total)
    bass = np.zeros(len(t_all))
    pad = np.zeros(len(t_all))
    for i in range(int(total / bar) + 1):
        t0 = i * bar
        ci = i % 4
        # bass eighths
        for k in range(8):
            ts = t0 + k * BEAT / 2
            if ts >= total:
                break
            dur = BEAT / 2 * 0.9
            tt = t_axis(dur)
            note = midi(ROOTS[ci] - 12 + (12 if k % 4 == 3 else 0))
            s = saw(note, tt) * env_exp(dur, 6)
            j = int(ts * SR)
            bass[j:j + len(s)] += s[:max(0, len(bass) - j)]
        # pad
        tt = t_axis(bar)
        s = np.zeros(len(tt))
        for n in CHORDS[ci]:
            for det in (-0.12, 0.12):
                s += saw(midi(n + det), tt)
        s *= np.minimum(1, tt / 0.3) * np.minimum(1, (bar - tt) / 0.3)
        j = int(t0 * SR)
        pad[j:j + len(s)] += s[:max(0, len(pad) - j)]

    bass = lp(bass, 600) * 0.28
    pad = lp(pad, 1800) * 0.05
    # hook intro: filtered, tense
    pre = t_all < drums_from
    pad[pre] = lp(pad, 500)[pre]
    mute = (t_all >= break_start) & (t_all < break_end)
    bass[mute] *= 0.0
    pad[mute] *= 0.35
    bed = bass + pad
    buf[:, 0] += bed
    buf[:, 1] += bed
    # end fade
    fade = np.clip((total - t_all) / (total - end_fade), 0, 1)
    buf *= fade[:, None]
    return buf


def build(total=DURATION):
    buf = build_music(total)
    for seg in SEGMENTS:
        for at, name in seg.get("sfx", []):
            fn, gain = SFX[name]
            place(buf, fn(), seg["start"] + at, gain, pan=RNG.uniform(-0.2, 0.2))
    # master: soft clip + normalise
    buf = np.tanh(buf * 1.1)
    buf /= max(1e-6, np.abs(buf).max()) / 0.92
    return buf


def write_wav(path, buf):
    data = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out/soundtrack.wav"
    write_wav(out, build())
    print("wrote", out)
