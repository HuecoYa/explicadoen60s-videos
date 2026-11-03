#!/usr/bin/env python3
# Alinea el guion (palabra a palabra) con el audio usando las pausas, recorta silencios largos.
# Uso: python3 align.py <audio.mp3> <guion.txt> <salida_base>
import subprocess, json, sys, re, wave, numpy as np

SR = 44100; MAXGAP = 0.30; PAD = 0.03

def intervals(f, noise="-35dB", d=0.11):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
    iv = []; s = 0.0
    for line in out.splitlines():
        if "silence_start" in line:
            e = float(line.split("silence_start: ")[1].split()[0])
            if e - s > 0.05: iv.append((s, e))
        if "silence_end" in line: s = float(line.split("silence_end: ")[1].split()[0])
    if dur - s > 0.1: iv.append((s, dur))
    return iv

def wlen(w):
    core = re.sub(r"[^\wáéíóúüñÁÉÍÓÚÜÑ]", "", w)
    return len(core) + 1.5

def main(audio, script, base):
    text = open(script, encoding="utf-8").read().strip()
    words = text.split()
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", audio, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    iv = intervals(audio)
    # recorte de pausas
    pieces = []; new_iv = []; cur = 0.0
    for k, (a, b) in enumerate(iv):
        a2, b2 = max(0, a - PAD), min(len(x) / SR, b + PAD)
        if k > 0:
            gap = min(MAXGAP, max(0.0, a - iv[k - 1][1] - 2 * PAD))
            pieces.append(np.zeros(int(gap * SR), dtype=np.float32)); cur += int(gap * SR) / SR
        new_iv.append((cur + (a - a2), cur + (a - a2) + (b - a)))
        seg = x[int(a2 * SR):int(b2 * SR)]; pieces.append(seg); cur += len(seg) / SR
    y = np.concatenate(pieces)
    with wave.open(base + "_voz.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.astype(np.int16).tobytes())
    iv = new_iv
    L = [wlen(w) for w in words]; P = [bool(re.search(r"[.,:;?!…]$", w)) for w in words]
    cum = np.concatenate([[0], np.cumsum(L)])
    tot_speech = sum(b - a for a, b in iv); r = tot_speech / cum[-1]
    nW, nI = len(words), len(iv)
    INF = 1e18
    # dp[j][i]: coste mínimo asignando las primeras i palabras a los primeros j intervalos
    dp = np.full((nI + 1, nW + 1), INF); bk = np.zeros((nI + 1, nW + 1), dtype=int)
    dp[0][0] = 0
    for j in range(1, nI + 1):
        d = iv[j - 1][1] - iv[j - 1][0]
        for i in range(1, nW + 1):
            best = INF; bi = 0
            lo = max(0, i - 40)
            for s in range(lo, i):
                if dp[j - 1][s] >= INF: continue
                exp = r * (cum[i] - cum[s])
                c = dp[j - 1][s] + (d - exp) ** 2 / max(d, 0.25)
                if i < nW and not P[i - 1]: c += 0.35
                if c < best: best, bi = c, s
            dp[j][i] = best; bk[j][i] = bi
    # permite descartar intervalos (respiraciones/ruido): no; exigimos todos
    i = nW; asg = []
    for j in range(nI, 0, -1):
        s = bk[j][i]; asg.append((j - 1, s, i)); i = s
    asg.reverse()
    out = []
    for j, s, e in asg:
        a, b = iv[j]; tot = cum[e] - cum[s]; t = a
        for k in range(s, e):
            d = (b - a) * L[k] / tot
            out.append([round(t, 3), round(t + d, 3), words[k]]); t += d
    json.dump({"dur": len(y) / SR, "words": out, "iv": iv}, open(base + "_words.json", "w"), ensure_ascii=False, indent=0)
    print("intervals", nI, "words", nW, "dur", round(len(y) / SR, 2), "cost", round(dp[nI][nW], 2))
    for j, s, e in asg:
        print(f"{iv[j][0]:6.2f}-{iv[j][1]:6.2f}  {' '.join(words[s:e])}")

if __name__ == "__main__":
    main(*sys.argv[1:4])
