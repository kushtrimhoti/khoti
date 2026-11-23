"""Build the soundtrack: Albanian voices, a vocal-only nasheed, ambience. Writes WAV + SRT files.

python3 audio.py OUTDIR
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np

SR = 44100
TOTAL = 720.0
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- dialogue cues
# (start_s, voice, albanian, english)
CUES = [
    (8.5, "nar", "Në një mëngjes si çdo mëngjes në Medine…", "On a morning like every morning in Medina…"),
    (41, "nar", "Qyteti flinte ende. Por zemrat e disave ishin zgjuar para diellit.",
     "The city was still asleep. But some hearts were awake before the sun."),
    (62, "sub", "", "(The adhan, the call to prayer)"),
    (98, "nar", "Thirrja e ezanit zgjoi Medinën. Dhe të gjithë u nisën drejt xhamisë.",
     "The call of the adhan woke Medina. And everyone set out for the masjid."),
    (147, "nar", "Rreshtat qëndronin si një trup i vetëm. Para tyre, drita e të Dërguarit të Allahut, paqja qoftë mbi të.",
     "The rows stood as one body. Before them, the light of the Messenger of Allah ﷺ."),
    (205, "nar", "Secili shkoi në punën e vet. Por disa bëjnë mirë kur askush nuk i sheh.",
     "Everyone went to their own work. But some do good when no one sees them."),
    (228, "nar", "Kur u kthyen në xhami, u ulën rreth të Dërguarit të Allahut, paqja qoftë mbi të, si çdo ditë.",
     "When they returned to the masjid, they sat around the Messenger of Allah ﷺ, as every day."),
    (255, "nar", "Atë ditë, ai u bëri disa pyetje.", "That day, he asked them a few questions."),
    (273, "soft", "Dhe i Dërguari i Allahut, paqja qoftë mbi të, pyeti: Kush prej jush agjëroi sot?",
     "And the Messenger of Allah ﷺ asked: “Who among you fasted today?”"),
    (294.5, "abu", "Unë.", "I did."),
    (303, "soft", "Pastaj pyeti: Kush prej jush përcolli sot një xhenaze?",
     "Then he asked: “Who among you followed a funeral today?”"),
    (324.5, "abu", "Unë.", "I did."),
    (333, "soft", "Pastaj pyeti: Kush prej jush ushqeu sot një të varfër?",
     "Then he asked: “Who among you fed a poor person today?”"),
    (354.5, "abu", "Unë.", "I did."),
    (363, "soft", "Pastaj pyeti: Kush prej jush vizitoi sot një të sëmurë?",
     "Then he asked: “Who among you visited a sick person today?”"),
    (384.5, "abu", "Unë.", "I did."),
    (397, "soft", "Dhe i Dërguari i Allahut, paqja qoftë mbi të, tha: Këto cilësi nuk bashkohen te një njeri, "
                  "përveçse ai hyn në Xhennet.",
     "And the Messenger of Allah ﷺ said: “These deeds never come together in one person except that he enters "
     "Paradise.”"),
    (447, "nar", "Umeri mendoi: Çfarë bën ai fshehurazi, që unë nuk e bëj?",
     "Umar wondered: “What does he do in secret that I do not?”"),
    (478, "nar", "Dhe vendosi: nesër, para agimit, do ta ndiqte.",
     "And he decided: tomorrow, before dawn, he would follow him."),
    (588, "woman", "Allahu të shpërbleftë, o i panjohur. Allahu të shpërbleftë.",
     "May Allah reward you, stranger. May Allah reward you."),
    (594.5, "nar", "Çdo mëngjes. Pa asnjë fjalë. Pa asnjë dëshmitar.", "Every morning. Without a word. Without a witness."),
    (613, "umar_w", "Nuk do të garoj kurrë me ty në mirësi.", "I will never be able to outdo you in goodness."),
    (652, "nar", "Kaluan vite. Dhe një ditë, Ebu Bekri u kthye te Zoti i tij.",
     "Years passed. And one day, Abu Bakr returned to his Lord."),
    (678, "woman", "Këto hurma nuk janë si ato të tjerat… Kush je ti?", "These dates are not like the others… Who are you?"),
    (685.5, "umar", "Ai që vinte para meje… ka shkuar te Allahu.", "The one who came before me… has gone to Allah."),
    (691.5, "woman", "Ai ishte Ebu Bekri… apo jo?", "It was Abu Bakr… wasn't it?"),
    (696, "umar", "Po, nënë. Ai ishte.", "Yes, mother. It was him."),
    (714, "sub", "", "Do good in secret."),
]

VOICES = {  # espeak-ng: voice, speed, pitch, amplitude, gain, reverb-wet
    "nar": ("sq+m3", 128, 30, 120, 1.0, 0.18),
    "soft": ("sq+m3", 112, 26, 100, 0.8, 0.30),
    "abu": ("sq+m7", 110, 42, 110, 0.9, 0.18),
    "umar": ("sq+m1", 118, 22, 120, 1.0, 0.18),
    "umar_w": ("sq+whisper", 105, 22, 160, 1.1, 0.22),
    "woman": ("sq+grandma", 105, 50, 110, 0.95, 0.18),
}


def read_wav(path):
    with wave.open(path) as w:
        n = w.getnframes()
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(1)
        return x


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def fft_conv(x, ir):
    n = len(x) + len(ir) - 1
    size = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:n]
    return y[:len(x)]


def make_ir(seconds, seed, damp=0.5):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * 6.9 / seconds)
    # gentle low-pass for a warm room
    k = int(SR * 0.00025 * (1 + damp * 4))
    ir = np.convolve(ir, np.ones(k) / k, mode="same")
    ir[0] = 1.0
    return ir / np.sqrt(np.sum(ir ** 2))


def lowpass(x, hz):
    a = math.exp(-2 * math.pi * hz / SR)
    # simple one-pole via cumulative trick in chunks (vectorized scan is not in numpy): use FFT filter
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / hz) ** 4)
    del a
    return np.fft.irfft(X, len(x))


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / np.sqrt(1 + (f / hi) ** 4)) * (1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4))
    return np.fft.irfft(X, len(x))


# ---------------------------------------------------------------- voices
def make_voice(text, key, tmp):
    v, sp, pi, amp, gain, wet = VOICES[key]
    raw = os.path.join(tmp, "raw.wav")
    res = os.path.join(tmp, "res.wav")
    subprocess.run(["espeak-ng", "-v", v, "-s", str(sp), "-p", str(pi), "-a", str(amp), "-g", "4",
                    "-w", raw, text], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-ar", str(SR), "-ac", "1", res], check=True)
    x = read_wav(res)
    x = lowpass(x, 3800 if key != "umar_w" else 5000)
    x = x + wet * fft_conv(x, make_ir(0.9, 3))
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.8 * gain
    return x


# ---------------------------------------------------------------- nasheed synthesis
FORMANTS = {
    "a": [(730, 90, 1.0), (1090, 110, 0.5), (2440, 170, 0.18)],
    "o": [(570, 80, 1.0), (840, 100, 0.45), (2410, 170, 0.1)],
    "u": [(320, 70, 1.0), (870, 100, 0.25), (2240, 170, 0.06)],
    "m": [(250, 70, 1.0), (1100, 200, 0.05)],
}
SCALES = {
    "hijaz": [0, 1, 4, 5, 7, 8, 10, 12],
    "bayati": [0, 1.5, 3, 5, 7, 8, 10, 12],
    "nahawand": [0, 2, 3, 5, 7, 8, 11, 12],
}
TONIC = 146.83  # D3


def sing(f0, dur, vowel, amp, voices=3, vib=0.006):
    n = int((dur + 0.6) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    form = FORMANTS[vowel]
    for v in range(voices):
        det = 2 ** ((rng.uniform(-8, 8)) / 1200)
        ph = rng.uniform(0, 6.28)
        vibr = 1 + vib * np.sin(2 * np.pi * rng.uniform(4.8, 5.8) * t + ph) * np.clip(t / 0.5, 0, 1)
        inst = f0 * det * vibr
        phase = 2 * np.pi * np.cumsum(inst) / SR
        hmax = int(3500 / f0)
        for h in range(1, hmax + 1):
            fh = h * f0
            g = 0.06
            for fc, bw, ga in form:
                g += ga * math.exp(-0.5 * ((fh - fc) / bw) ** 2)
            g *= h ** -0.7
            if g < 0.004:
                continue
            out += g * np.sin(h * phase + rng.uniform(0, 6.28))
    env = np.clip(t / 0.35, 0, 1) * np.clip((dur + 0.6 - t) / 0.6, 0, 1)
    breath = bandpass(rng.standard_normal(n), 800, 3000) * 0.01 * env
    return (out / voices * env + breath) * amp


def place(buf, x, start):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i]


# segments: (start, end, level, scale, layers, tempo, vowel)
SEGMENTS = [
    (0.5, 58, 0.55, "bayati", 2, 1.0, "u"),
    (110, 160, 0.30, "bayati", 1, 1.3, "m"),
    (160, 220, 0.55, "hijaz", 2, 0.8, "a"),
    (220, 270, 0.62, "hijaz", 3, 1.0, "o"),
    (270, 300, 0.45, "hijaz", 1, 1.1, "o"),
    (300, 330, 0.55, "hijaz", 2, 1.1, "o"),
    (330, 360, 0.65, "hijaz", 3, 1.0, "a"),
    (360, 390, 0.75, "hijaz", 4, 1.0, "a"),
    (390, 440, 0.95, "hijaz", 4, 0.9, "a"),
    (440, 490, 0.38, "bayati", 1, 1.4, "m"),
    (490, 540, 0.40, "hijaz", 1, 1.6, "m"),
    (540, 600, 0.55, "nahawand", 2, 1.2, "o"),
    (600, 630, 0.45, "nahawand", 2, 1.2, "u"),
    (636, 660, 0.35, "bayati", 1, 1.5, "m"),
    (660, 677, 0.35, "nahawand", 1, 1.3, "u"),
]


def nasheed():
    buf = np.zeros(int(TOTAL * SR) + SR * 4)
    for (s, e, lvl, scale, layers, tempo, vowel) in SEGMENTS:
        sc = SCALES[scale]
        # drone: tonic + fifth below, hummed
        t = s
        while t < e - 1:
            d = min(8.0, e - t)
            place(buf, sing(TONIC / 2, d, "m", 0.35 * lvl, voices=2, vib=0.002), t)
            place(buf, sing(TONIC * 2 ** (-5 / 12), d, "m", 0.18 * lvl, voices=2, vib=0.002), t)
            t += d - 0.5
        if layers < 2 and vowel == "m":
            # hummed slow melody
            pass
        deg = 0
        t = s + 1.0
        while t < e - 2:
            phrase = rng.integers(3, 7)
            for k in range(phrase):
                if t > e - 2:
                    break
                deg = int(np.clip(deg + rng.choice([-2, -1, -1, 0, 1, 1, 2]), 0, 7))
                if k == phrase - 1:
                    deg = rng.choice([0, 4, 7])
                dur = float(rng.choice([1.0, 1.5, 1.5, 2.0, 3.0])) * tempo
                f = TONIC * 2 ** (sc[deg] / 12)
                v = vowel if vowel != "m" else "u"
                place(buf, sing(f, dur, v, 0.55 * lvl), t)
                if layers >= 2:
                    hd = max(0, deg - 2)
                    place(buf, sing(TONIC * 2 ** (sc[hd] / 12) / 1.0, dur, v, 0.3 * lvl), t + 0.05)
                if layers >= 3:
                    place(buf, sing(f / 2, dur, "o", 0.28 * lvl), t + 0.08)
                if layers >= 4:
                    place(buf, sing(f * 2 ** (7 / 12) / 2, dur, "a", 0.2 * lvl), t + 0.1)
                t += dur
            t += float(rng.uniform(1.0, 2.5)) * tempo
    # final long note (700-718)
    for f, v, a in [(TONIC, "o", 0.5), (TONIC * 2 ** (7 / 12), "o", 0.25), (TONIC / 2, "m", 0.35)]:
        place(buf, sing(f, 15.0, v, a, vib=0.004), 701)
    buf = buf[:int(TOTAL * SR)]
    L = buf + 0.45 * fft_conv(buf, make_ir(2.6, 11))
    R = buf + 0.45 * fft_conv(buf, make_ir(2.6, 12))
    return np.stack([L, R], 1)


# ---------------------------------------------------------------- ambience
def env_curve(points):
    t = np.arange(int(TOTAL * SR)) / SR
    xs, ys = zip(*points)
    return np.interp(t, xs, ys)


def ambience():
    n = int(TOTAL * SR)
    out = np.zeros(n)
    # wind
    w = np.cumsum(rng.standard_normal(n))
    w -= np.convolve(w, np.ones(4410) / 4410, mode="same")
    w = w / np.max(np.abs(w))
    w = bandpass(w, 80, 900)
    w /= np.max(np.abs(w)) + 1e-9
    slow = 0.6 + 0.4 * np.sin(2 * np.pi * np.arange(n) / SR / 9.0)
    wind_lvl = env_curve([(0, .25), (38, .25), (39, .08), (60, .3), (110, .25), (111, .05), (160, .25), (220, .2),
                          (221, .05), (490, .05), (491, .3), (540, .3), (541, .06), (610, .3), (630, .3),
                          (645, .4), (660, .2), (668, .05), (720, .05)])
    out += w * slow * wind_lvl * 0.12

    def at(t0, x, g=1.0):
        place(out, x * g, t0)

    t = np.arange(int(0.12 * SR)) / SR
    # birds at dawn / day
    for (s, e, dens) in [(60, 110, 0.9), (160, 220, 1.2), (600, 630, 0.5), (660, 668, 0.8), (700, 713, 0.8)]:
        k = s
        while k < e:
            k += float(rng.exponential(1.4 / dens))
            for j in range(int(rng.integers(2, 5))):
                f0, f1 = rng.uniform(2500, 4200), rng.uniform(3000, 5200)
                d = rng.uniform(0.05, 0.12)
                tt = np.arange(int(d * SR)) / SR
                ch = np.sin(2 * np.pi * (f0 * tt + (f1 - f0) * tt ** 2 / (2 * d))) * np.sin(np.pi * tt / d) ** 2
                at(k + j * rng.uniform(0.08, 0.16), ch, 0.03)
    # crickets at night
    for (s, e) in [(0, 60), (440, 540), (645, 652)]:
        k = s
        while k < e:
            k += float(rng.uniform(0.6, 1.4))
            d = 0.25
            tt = np.arange(int(d * SR)) / SR
            ch = np.sin(2 * np.pi * 4600 * tt) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * tt))) * np.sin(
                np.pi * tt / d)
            at(k, ch, 0.012)
    # footsteps
    for (s, e, rate) in [(84, 110, 1.6), (202, 216, 1.4), (490, 505, 1.3), (520, 532, 1.3), (620, 630, 1.1),
                         (660, 666, 1.3)]:
        k = s
        while k < e:
            d = 0.09
            tt = np.arange(int(d * SR)) / SR
            st = lowpass(rng.standard_normal(len(tt)), 600) * np.exp(-tt * 40)
            at(k, st, 0.25)
            k += 1 / rate
    # heartbeat daf while Umar follows
    k = 490
    while k < 540:
        for off in (0, 0.22):
            d = 0.35
            tt = np.arange(int(d * SR)) / SR
            thump = np.sin(2 * np.pi * 58 * tt) * np.exp(-tt * 14) + 0.2 * lowpass(rng.standard_normal(len(tt)),
                                                                                    300) * np.exp(-tt * 30)
            at(k + off, thump, 0.35 if off == 0 else 0.22)
        k += 1.0
    # broom
    for (s, e, sp) in [(550, 560, 3.2), (668, 674, 3.0)]:
        d = e - s
        tt = np.arange(int(d * SR)) / SR
        sw = bandpass(rng.standard_normal(len(tt)), 1500, 6000) * np.abs(np.sin(tt * sp)) ** 3
        at(s, sw, 0.05)
    # water pour
    tt = np.arange(int(4.5 * SR)) / SR
    at(562.5, bandpass(rng.standard_normal(len(tt)), 400, 2500) * np.sin(np.pi * tt / 4.5) * 0.06)
    # rain
    tt = np.arange(int(4.5 * SR)) / SR
    at(636, bandpass(rng.standard_normal(len(tt)), 1000, 8000) * np.sin(np.pi * tt / 4.5) * 0.06)
    # lamp crackle indoors
    for (s, e) in [(38, 60), (458, 490), (540, 600), (668, 712)]:
        k = s
        while k < e:
            k += float(rng.exponential(0.7))
            at(k, rng.standard_normal(60) * np.exp(-np.arange(60) / 12), 0.03)
    return np.stack([out, out * 0.95], 1)


# ---------------------------------------------------------------- main
def srt_time(x):
    h, rem = divmod(x, 3600)
    m, s = divmod(rem, 60)
    ms = int(round((s - int(s)) * 1000))
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{ms:03d}"


def main(outdir):
    tmp = os.path.join(outdir, "tmp")
    os.makedirs(tmp, exist_ok=True)
    n = int(TOTAL * SR)
    vtrack = np.zeros(n)
    duck = np.zeros(n)
    subs = []
    for start, key, sq, en in CUES:
        if key == "sub":
            subs.append((start, start + 6, "", en))
            continue
        x = make_voice(sq, key, tmp)
        place(vtrack, x, start)
        dur = len(x) / SR
        end = start + dur
        subs.append((start, max(end + 0.4, start + 2.2), sq, en))
        a, b = int((start - 0.4) * SR), int((end + 0.6) * SR)
        duck[max(0, a):min(n, b)] = 1
        print(f"{start:7.1f} {key:7s} {dur:5.1f}s  {sq[:60]}")
    # check overlaps
    for (s1, e1, *_), (s2, *_r) in zip(subs, subs[1:]):
        if e1 > s2:
            print("WARNING overlap", s1, s2)
    # smooth ducking
    k = int(0.3 * SR)
    duck = np.convolve(duck, np.ones(k) / k, mode="same")
    music = nasheed()
    amb = ambience()
    mg = (1 - 0.6 * duck)[:, None]
    mix = 0.33 * music * mg + amb + 0.9 * np.stack([vtrack, vtrack], 1)
    # silence at the woman's question (music stops) handled by segments; master fade in/out
    t = np.arange(n) / SR
    fade = np.clip(t / 2.0, 0, 1) * np.clip((TOTAL - t) / 3.0, 0, 1)
    mix *= fade[:, None]
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.9
    write_wav(os.path.join(outdir, "soundtrack.wav"), mix)
    write_wav(os.path.join(outdir, "voices_only.wav"), np.stack([vtrack, vtrack], 1) * 0.9)
    write_wav(os.path.join(outdir, "music_and_ambience.wav"),
              (0.33 * music + amb) / (np.max(np.abs(0.33 * music + amb)) + 1e-9) * 0.9)
    for lang, idx in (("en", 3), ("sq", 2)):
        with open(os.path.join(outdir, f"subtitles-{lang}.srt"), "w", encoding="utf-8") as f:
            k = 0
            for s in subs:
                if not s[idx]:
                    continue
                k += 1
                f.write(f"{k}\n{srt_time(s[0])} --> {srt_time(s[1])}\n{s[idx]}\n\n")


if __name__ == "__main__":
    main(sys.argv[1])
