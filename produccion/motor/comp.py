#!/usr/bin/env python3
# Montaje: fotogramas 3D + subtítulo de UNA palabra + etiquetas/marcadores puntuales + voz + efectos.
# Uso: python3 comp.py <nombre> [t0 t1]  (con t0 t1 hace una prueba parcial)
import subprocess, os, sys, json, math, re, glob, importlib, wave
import numpy as np, cairo

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
ESTILO_ACTUAL = "palabra"
YL = (1.0, 0.82, 0.16); RED = (0.93, 0.2, 0.22); GREEN = (0.25, 0.85, 0.45)

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def text_path(ctx, s, size, italic=False):
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(s); return e

def outlined(ctx, s, cx, cy, size, fill=(1, 1, 1), stroke=10, italic=False, scale=1.0, rot=0.0, alpha=1.0, shadow=True):
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(scale, scale)
    e = text_path(ctx, s, size, italic)
    x = -e.x_advance / 2; y = size * 0.35
    if shadow:
        ctx.move_to(x + 4, y + 6); ctx.text_path(s); ctx.set_source_rgba(0, 0, 0, 0.35 * alpha); ctx.set_line_width(stroke); ctx.stroke_preserve(); ctx.fill()
    ctx.move_to(x, y); ctx.text_path(s)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_source_rgba(0, 0, 0, alpha); ctx.set_line_width(stroke); ctx.stroke_preserve()
    ctx.set_source_rgba(*fill, alpha); ctx.fill()
    ctx.restore()

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); ctx.close_path()

def badge(ctx, s, cx, cy, p, col=(1, 1, 1), size=70, sub=None):
    if p <= 0: return
    sc = back(p)
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc)
    # ✗ y ✓ no están en Poppins: se dibujan como trazos para no depender de fuentes de respaldo
    icon = None
    if s[:1] in "✗✓✕✔✘": icon = "ok" if s[0] in "✓✔" else "no"; s = s[1:].lstrip()
    iw = size * 0.78 if icon else 0
    e = text_path(ctx, s, size); w = e.x_advance + 56 + iw; h = size * 1.45
    rrect(ctx, -w / 2 + 4, -h / 2 + 7, w, h, 22); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, 22); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92); ctx.fill_preserve()
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.18); ctx.stroke()
    x0 = -(e.x_advance + iw) / 2
    if icon:
        r = size * 0.27; cx0 = x0 + r; ctx.set_source_rgb(*col); ctx.set_line_width(size * 0.13); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        if icon == "no":
            ctx.move_to(cx0 - r, -r); ctx.line_to(cx0 + r, r); ctx.move_to(cx0 + r, -r); ctx.line_to(cx0 - r, r)
        else:
            ctx.move_to(cx0 - r, 0.05 * r); ctx.line_to(cx0 - 0.25 * r, 0.8 * r); ctx.line_to(cx0 + r, -0.85 * r)
        ctx.stroke()
    ctx.move_to(x0 + iw, size * 0.36); ctx.text_path(s); ctx.set_source_rgb(*col); ctx.fill()
    ctx.restore()

def callout(ctx, s, cx, cy, p, size=64):
    if p <= 0: return
    lines = s.split("\n")
    for k, l in enumerate(lines):
        outlined(ctx, l, cx, cy + (k - (len(lines) - 1) / 2) * size * 0.95, size, fill=YL, stroke=12, italic=True,
                 scale=back(p), rot=-0.07)

def arrow_dim(ctx, x0, x1, y, col, p, lw=9):
    if p <= 0: return
    xm = (x0 + x1) / 2; hw = (x1 - x0) / 2 * ease(p)
    a, b = xm - hw, xm + hw
    for st, c in ((lw + 8, (0, 0, 0)), (lw, col)):
        ctx.set_line_width(st); ctx.set_source_rgb(*c); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(a, y); ctx.line_to(b, y); ctx.stroke()
        for xx, d in ((a, 1), (b, -1)):
            ctx.move_to(xx + d * 26, y - 20); ctx.line_to(xx, y); ctx.line_to(xx + d * 26, y + 20); ctx.stroke()
        for xx in (a, b):
            ctx.move_to(xx, y - 34); ctx.line_to(xx, y + 34); ctx.stroke()

def clean(w):
    w = re.sub(r"^[¿¡\"“(]+|[.,:;?!…\"”)]+$", "", w)
    return w[:1].upper() + w[1:] if w else w

# ---------------- audio: efectos sintéticos ----------------
SR = 44100
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def s_whoosh(dur=0.55):
    n = int(dur * SR); x = np.random.randn(n); t = np.arange(n) / n
    # ruido filtrado por un paso-bajo variable (sube y baja)
    out = np.zeros(n); y = 0
    for i in range(n):
        a = 0.02 + 0.25 * math.sin(math.pi * t[i]) ** 2; y += a * (x[i] - y); out[i] = y
    return out * np.sin(np.pi * t) ** 1.5 * 2.2
def s_pop():
    n = int(0.12 * SR); t = np.arange(n) / SR; f = 900 * np.exp(-t * 25) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.03) * 0.8
def s_coin():
    n = int(0.45 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2637 * t) * 0.6 + np.sin(2 * np.pi * 3951 * t) * 0.4) * env(n, 0.001, 0.09) * 0.5
def s_thud():
    n = int(0.3 * SR); t = np.arange(n) / SR; f = 140 * np.exp(-t * 12) + 50
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.08) * 1.0
def s_clank():
    n = int(0.6 * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((310, 0.5), (787, 0.35), (1290, 0.25), (2210, 0.15)))
    return x * env(n, 0.001, 0.12) * 0.8 + np.random.randn(n) * env(n, 0.001, 0.02) * 0.4
def s_win():
    out = np.zeros(int(0.9 * SR))
    for k, f in enumerate((784, 988, 1175, 1568)):
        n = int(0.35 * SR); t = np.arange(n) / SR; a = int(k * 0.1 * SR)
        tone = (np.sign(np.sin(2 * np.pi * f * t)) * 0.25 + np.sin(2 * np.pi * f * t) * 0.5) * env(n, 0.002, 0.12)
        out[a:a + n] += tone[:len(out) - a]
    return out * 0.45
def s_fail():
    n = int(0.5 * SR); t = np.arange(n) / SR; f = 420 - 250 * t / 0.5
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.005, 0.25) * 0.18
def s_bleep(f):
    n = int(0.09 * SR); t = np.arange(n) / SR; return np.sign(np.sin(2 * np.pi * f * t)) * env(n, 0.002, 0.04) * 0.12
def s_buzz(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 120 * t) * 0.5 + np.sign(np.sin(2 * np.pi * 240 * t)) * 0.15
    return x * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.1) * 0.12

def build_sfx(dur, events, path):
    out = np.zeros(int((dur + 2) * SR))
    for t, snd, g in events:
        a = int(t * SR); x = snd * g; b = min(len(out), a + len(x)); out[a:b] += x[:b - a]
    out = np.clip(out, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767 * 0.8).astype(np.int16).tobytes())

# ---------------- subtítulo en frases (estilo «karaoke») ----------------
# La frase se escribe palabra a palabra arriba; la palabra que suena va en blanco y las anteriores en gris.
# Las palabras clave llevan un recuadro azul. Fondo oscuro suave para que se lea sobre cualquier escena.
def frases(ws):
    # corta por signos de puntuación o pausas; las frases largas se parten por la mitad (nunca quedan palabras sueltas)
    bloques, cur = [], []
    for i, (ta, tb, w) in enumerate(ws):
        if cur and ta - cur[-1][1] > 0.6: bloques.append(cur); cur = []
        cur.append((ta, tb, w))
        if re.search(r"[.,;:?!…]$", w): bloques.append(cur); cur = []
    if cur: bloques.append(cur)
    out = []
    for b in bloques:
        while len(b) > 8:
            n = max(3, (len(b) + 1) // 2 if len(b) <= 16 else 8); out.append(b[:n]); b = b[n:]
        out.append(b)
    return out

def subtitulo_frase(ctx, t, FR, kws, y0):
    for k, fr in enumerate(FR):
        ini = fr[0][0] - 0.05
        fin = FR[k + 1][0][0] - 0.05 if k + 1 < len(FR) else fr[-1][1] + 0.6
        if not (ini <= t < fin): continue
        size = 70; ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
        esp = ctx.text_extents(" ").x_advance * 1.1
        toks = [(ta, tb, re.sub(r"^[\"“(]+|[\"”)]+$", "", w)) for ta, tb, w in fr]
        lineas, linea, ancho = [], [], 0
        for tok in toks:
            wd = ctx.text_extents(tok[2]).x_advance
            if linea and ancho + esp + wd > 880: lineas.append((linea, ancho)); linea, ancho = [], 0
            ancho += (esp if linea else 0) + wd; linea.append((tok, wd))
        if linea: lineas.append((linea, ancho))
        lh = size * 1.22; alto = lh * len(lineas)
        vis = [tok for tok in toks if tok[0] - 0.03 <= t]
        if not vis: return
        a = min(1, (t - ini) / 0.12)
        anch = max(an for _, an in lineas)
        rrect(ctx, W / 2 - anch / 2 - 30, y0 - 18, anch + 60, alto + 30, 26); ctx.set_source_rgba(0.04, 0.06, 0.14, 0.58 * a); ctx.fill()
        for j, (linea, an) in enumerate(lineas):
            x = W / 2 - an / 2; y = y0 + j * lh + size * 0.88
            for (ta, tb, w), wd in linea:
                if ta - 0.03 > t: x += wd + esp; continue
                actual = ta - 0.03 <= t < max(tb, ta + 0.18)
                limpio = re.sub(r"[.,;:?!…¿¡]", "", w).lower()
                if limpio in kws:
                    rrect(ctx, x - 9, y - size * 0.86, wd + 18, size * 1.12, 8)
                    ctx.set_source_rgba(0.2, 0.55, 1.0, 0.95); ctx.set_line_width(3.5); ctx.stroke()
                    for cx, cy in ((x - 9, y - size * 0.86), (x + wd + 9, y + size * 0.26)):
                        ctx.arc(cx, cy, 5, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()
                ctx.move_to(x, y); ctx.text_path(w)
                ctx.set_source_rgba(1, 1, 1, 1 if (actual or limpio in kws) else 0.62); ctx.fill()
                x += wd + esp
        return

# ---------------- montaje ----------------
def main(name, t0=None, t1=None):
    spec = importlib.import_module(f"{name}_ov")
    words = json.load(open(os.path.join(HERE, f"{name}_words.json")))
    dur = words["dur"]; ws = words["words"]
    frames_dir = os.path.join(HERE, "frames", name)
    anc = {}
    for f in glob.glob(os.path.join(HERE, "frames", f"anchors_{name}_*_1.json")):
        anc.update({int(k): v for k, v in json.load(open(f)).items()})
    n_total = int(math.ceil((dur + 0.4) * FPS))
    f0 = int(t0 * FPS) if t0 is not None else 0; f1 = int(t1 * FPS) if t1 is not None else n_total
    vout = os.path.join(HERE, f"{name}_video.mp4" if t0 is None else f"{name}_part.mp4")
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-start_number", str(f0), "-framerate", str(FPS), "-i", os.path.join(frames_dir, "%05d.png"),
                            "-frames:v", str(f1 - f0), "-vf", f"scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "bgra", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    last_anchor = None
    global ESTILO_ACTUAL
    estilo = getattr(spec, "SUB_ESTILO", "palabra"); FR = frases(ws); ESTILO_ACTUAL = estilo
    kws = {k.lower() for k in spec.KEYWORDS}
    for f in range(f0, f1):
        raw = dec.stdout.read(W * H * 4)
        if len(raw) < W * H * 4: break
        t = f / FPS
        buf = bytearray(raw)
        surf = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, W, H, W * 4); ctx = cairo.Context(surf)
        a = anc.get(f, last_anchor); last_anchor = a
        A = (lambda k: (a[k][0] * W, a[k][1] * H)) if a else (lambda k: (W / 2, H / 2))
        spec.overlay(ctx, t, A, sys.modules[__name__])
        if estilo == "frase":
            subtitulo_frase(ctx, t, FR, kws, H * getattr(spec, "SUB_Y_FRASE", 0.12))
            surf.flush(); enc.stdin.write(bytes(buf)); continue
        # subtítulo: una sola palabra
        cur = None
        for i, (ta, tb, w) in enumerate(ws):
            nxt = ws[i + 1][0] if i + 1 < len(ws) else tb + 0.5
            end = nxt if nxt - tb < 0.35 else tb + 0.25
            if ta - 0.03 <= t < end: cur = (ta, w); break
        if cur:
            ta, w = cur; s = clean(w); kw = s.lower() in spec.KEYWORDS
            p = min(1, (t - ta + 0.03) / 0.09)
            outlined(ctx, s, W / 2, H * spec.SUB_Y, 84, fill=(YL if kw else (1, 1, 1)), stroke=13, scale=0.82 + 0.18 * p)
        surf.flush(); enc.stdin.write(bytes(buf))
    enc.stdin.close(); enc.wait(); dec.wait()
    if t0 is not None: print("ok", vout); return
    sfx = os.path.join(HERE, f"{name}_sfx.wav")
    build_sfx(dur, spec.sfx_events(sys.modules[__name__]), sfx)
    final = os.path.join(HERE, f"{name}_final.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vout, "-i", os.path.join(HERE, f"{name}_voz.wav"), "-i", sfx, "-filter_complex",
                    "[1:a]apad[v];[v][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[m]", "-map", "0:v", "-map", "[m]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("ok", final)

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    if len(sys.argv) > 2: main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
    else: main(sys.argv[1])
