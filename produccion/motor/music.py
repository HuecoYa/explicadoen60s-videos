#!/usr/bin/env python3
# Base musical original (sin copyright) para la versión TikTok + mezcla con ducking bajo la voz.
# Uso: python3 music.py <video_in.mp4> <video_out.mp4> [estilo 0-3]
import sys, subprocess, numpy as np, wave

SR = 44100
STYLES = [  # bpm, progresión (semitonos desde La), carácter
    dict(bpm=124, prog=[0, -4, 3, -2], minor=True),     # Am F C G
    dict(bpm=118, prog=[0, 3, -2, -4], minor=True),
    dict(bpm=128, prog=[0, 5, -3, 7], minor=False),
    dict(bpm=110, prog=[0, -5, -2, 3], minor=True),
]

def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)

def note(f, n, kind="saw"):
    t = np.arange(n) / SR
    if kind == "saw":
        return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 8)) * 0.6
    if kind == "sq":
        return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9, 2)) * 0.7
    return np.sin(2 * np.pi * f * t)

def make(dur, style=0, seed=1):
    st = STYLES[style % len(STYLES)]; rng = np.random.default_rng(seed)
    beat = 60 / st["bpm"]; N = int((dur + 1) * SR); out = np.zeros(N)
    def add(sig, t0, g=1.0):
        i = int(t0 * SR); j = min(N, i + len(sig))
        if i < N: out[i:j] += sig[:j - i] * g
    base = 220.0; third = 3 if st["minor"] else 4
    nb = int(dur / beat) + 2
    for b in range(nb):
        t0 = b * beat; bar = b // 4; root = st["prog"][bar % 4]
        fr = base * 2 ** (root / 12)
        # bombo
        n = int(0.35 * SR); tt = np.arange(n) / SR
        add(np.sin(2 * np.pi * (50 + 110 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9), t0, 0.9)
        # clap en 2 y 4
        if b % 2 == 1:
            n = int(0.18 * SR); add(rng.standard_normal(n) * env(n, 0.002, 0.05), t0, 0.35)
        # hi-hats en corcheas
        for h in (0, 0.5):
            n = int(0.05 * SR); hh = rng.standard_normal(n); hh = np.diff(np.concatenate([[0], hh]))
            add(hh * env(n, 0.001, 0.012), t0 + h * beat, 0.18 if h else 0.1)
        # bajo en contratiempo
        n = int(beat * 0.45 * SR)
        add(note(fr / 4, n, "saw") * env(n, 0.005, 0.12), t0 + beat * 0.5, 0.35)
        # arpegio
        for k in range(4):
            iv = [0, third, 7, 12][(b * 4 + k) % 4]
            n = int(beat * 0.24 * SR)
            add(note(fr * 2 * 2 ** (iv / 12), n, "sq") * env(n, 0.003, 0.07), t0 + k * beat / 4, 0.10)
        # pad al inicio de cada compás
        if b % 4 == 0:
            n = int(beat * 4 * SR)
            pad = sum(note(fr * 2 ** (iv / 12), n, "saw") for iv in (0, third, 7)) / 3
            e = np.minimum(1, np.arange(n) / (0.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.4 * SR))
            add(pad * e, t0, 0.08)
    out = out[:int(dur * SR)]
    fade = int(1.2 * SR); out[-fade:] *= np.linspace(1, 0, fade)
    out = np.tanh(out * 1.2); out /= np.abs(out).max()
    return out

def main(vin, vout, style=0):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vin],
                               capture_output=True, text=True).stdout)
    m = make(dur, style, seed=style + 7)
    wav = vout + ".music.wav"
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767 * 0.9).astype(np.int16).tobytes())
    # música a ~ -19 dB respecto a la voz y comprimida (ducking) cuando hay voz
    fc = ("[0:a]asplit=2[v][key];[1:a]volume=0.196[mus];"
          "[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck];"
          "[v][duck]amix=inputs=2:duration=first:normalize=0[m]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vin, "-i", wav, "-filter_complex", fc, "-map", "0:v", "-map", "[m]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", vout], check=True)
    print("ok", vout)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0)
