# Capa 2D de «Si tuvieras que inventar el mando de la tele…»
import math, cairo
from _ovbase import *
from comp import rrect
from marcas import cargar
T, DUR = cargar("mando")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"mando", "cámara", "lucecita", "luz", "led", "destellos", "infrarrojo", "novecientos", "nanómetros", "ojos", "sol",
            "bombillas", "estufa", "parpadear", "treinta", "mil", "receptor", "ritmo", "código", "unos", "ceros", "uno", "cero",
            "dos", "aparato", "tecla", "dieciséis", "revés", "ignora", "paredes", "sofá"}

ADDR = [1, 0, 1, 1, 0, 0, 1, 0]; CMD = [0, 1, 1, 0, 1, 0, 0, 0]
BITS = ADDR + CMD + [1 - b for b in ADDR] + [1 - b for b in CMD]
IRC = (0.78, 0.45, 1.0); BLUE = (0.35, 0.65, 1.0)

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def visor(ctx, p, t):
    """marco de cámara del móvil"""
    if p <= 0: return
    x0, y0, x1, y1, L = 90, 470, 920, 1460, 90
    ctx.set_line_width(9); ctx.set_source_rgba(1, 1, 1, 0.9 * p); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for cx, cy, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        ctx.move_to(cx + dx * L, cy); ctx.line_to(cx, cy); ctx.line_to(cx, cy + dy * L); ctx.stroke()
    if int(t * 2) % 2 == 0:
        ctx.arc(x0 + 40, y0 + 52, 14, 0, 7); ctx.set_source_rgba(1, 0.2, 0.2, p); ctx.fill()
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(40)
    ctx.move_to(x0 + 66, y0 + 66); ctx.set_source_rgba(1, 1, 1, p); ctx.show_text("REC")

def espectro(ctx, t, a0, a1):
    p = win(t, a0, a1)
    if p <= 0: return
    x0, x1, y, hh = 110, 900, 600, 56
    ctx.save(); ctx.translate(W / 2, y); ctx.scale(0.6 + 0.4 * p, 0.6 + 0.4 * p); ctx.translate(-W / 2, -y)
    # 380..1000 nm
    nm = lambda v: x0 + (x1 - x0) * (v - 380) / 620
    rrect(ctx, x0 - 20, y - 80, x1 - x0 + 40, hh + 170, 22); ctx.set_source_rgba(0.08, 0.09, 0.12, 0.9 * p); ctx.fill()
    g = cairo.LinearGradient(nm(400), 0, nm(700), 0)
    for s, c in ((0, (0.55, 0.2, 0.9)), (0.2, (0.2, 0.35, 1)), (0.4, (0.2, 0.85, 0.4)), (0.6, (1, 0.9, 0.2)), (0.8, (1, 0.5, 0.15)), (1, (0.9, 0.12, 0.12))):
        g.add_color_stop_rgba(s, *c, p)
    rrect(ctx, nm(400), y, nm(700) - nm(400), hh, 10); ctx.set_source(g); ctx.fill()
    rrect(ctx, nm(700), y, nm(1000) - nm(700), hh, 10); ctx.set_source_rgba(0.2, 0.2, 0.24, p); ctx.fill()
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(34)
    ctx.set_source_rgba(1, 1, 1, 0.8 * p); ctx.move_to(nm(470), y - 22); ctx.show_text("LO QUE VES")
    ctx.move_to(nm(800), y - 22); ctx.show_text("IR")
    v = keyed(t, [(a0, 550), (a0 + 1.6, 940)])
    x = nm(v)
    ctx.set_line_width(8); ctx.set_source_rgba(*IRC, p); ctx.move_to(x, y - 6); ctx.line_to(x, y + hh + 6); ctx.stroke()
    ctx.set_font_size(48); txt = f"{int(v)} nm"; e = ctx.text_extents(txt)
    ctx.move_to(min(x1 - e.width, max(x0, x - e.width / 2)), y + hh + 62); ctx.set_source_rgba(*IRC, p); ctx.show_text(txt)
    ctx.restore()

def onda(ctx, t, a0, a1, hl1, hl0):
    """tren de ráfagas: larga = 1, corta = 0"""
    p = win(t, a0, a1)
    if p <= 0: return
    x0, x1, y = 90, 990, 560
    rrect(ctx, x0, y - 70, x1 - x0, 210, 22); ctx.set_source_rgba(0.08, 0.09, 0.12, 0.9 * p); ctx.fill()
    seq = [1, 0, 1, 1, 0, 0, 1, 0]
    x = x0 + 40; base = y + 80
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    shown = int((t - a0) / 0.28) + 1
    for i, b in enumerate(seq[:shown]):
        w = 70 if b else 26
        hl = (b == 1 and t > hl1 and t < hl0) or (b == 0 and t > hl0)
        first_of = (b == 1 and i == 0) or (b == 0 and i == 1)
        col = IRC if not (hl and first_of) else (1, 0.9, 0.3)
        # dibujar ráfaga como barras finas (parpadeo de 38 kHz)
        for k in range(int(w / 9)):
            ctx.rectangle(x + k * 9, base - 90, 5, 90); ctx.set_source_rgba(*col, p); ctx.fill()
        ctx.set_font_size(46 if not (hl and first_of) else 62); s = str(b); e = ctx.text_extents(s)
        ctx.move_to(x + w / 2 - e.width / 2, base - 104); ctx.set_source_rgba(*(col if hl and first_of else (1, 1, 1)), p); ctx.show_text(s)
        x += w + 34
    ctx.set_source_rgba(1, 1, 1, 0.35 * p); ctx.set_line_width(3); ctx.move_to(x0 + 30, base + 2); ctx.line_to(x1 - 30, base + 2); ctx.stroke()

def bits32(ctx, t):
    a0, a1 = T("cada pulsación"), T("por eso tienes") - 0.1
    p = win(t, a0, a1)
    if p <= 0: return
    x0, y0, cw, chh, gap = 84, 500, 52, 70, 4
    n = min(32, int(32 * (t - a0) / 2.2) + 1)
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    t_ap, t_te, t_rev, t_ok = T("ocho dicen"), T("ocho dicen", 2), T("y las otras"), T("para comprobar")
    t_mal = T("si algo")
    for i in range(n):
        row, col = divmod(i, 16)
        x = x0 + col * (cw + gap) + (12 if col >= 8 else 0); y = y0 + row * (chh + 64)
        grp = 0 if i < 8 else (1 if i < 16 else (2 if i < 24 else 3))
        c = (0.22, 0.24, 0.3)
        if grp == 0 and t > t_ap: c = (0.2, 0.45, 0.9)
        if grp == 1 and t > t_te: c = (0.85, 0.65, 0.1)
        if grp >= 2 and t > t_rev: c = (0.2, 0.45, 0.9) if grp == 2 else (0.85, 0.65, 0.1)
        bad = t > t_mal and i == 19
        if bad: c = (0.85, 0.2, 0.2)
        rrect(ctx, x, y, cw, chh, 8); ctx.set_source_rgba(*c, 0.95 * p); ctx.fill()
        b = BITS[i] if not bad else 1 - BITS[i]
        ctx.set_font_size(44); s = str(b); e = ctx.text_extents(s)
        ctx.move_to(x + cw / 2 - e.width / 2 - e.x_bearing, y + chh / 2 + e.height / 2); ctx.set_source_rgba(1, 1, 1, p); ctx.show_text(s)
    ctx.set_font_size(34)
    def tag(s, cx, y, pp, col):
        if pp <= 0: return
        e = ctx.text_extents(s); ctx.move_to(cx - e.width / 2, y); ctx.set_source_rgba(*col, pp * p); ctx.show_text(s)
    tag("APARATO", x0 + 4 * (cw + gap), y0 - 14, ss((t - t_ap) / 0.3), (0.5, 0.75, 1))
    tag("TECLA", x0 + 12 * (cw + gap) + 12, y0 - 14, ss((t - t_te) / 0.3), (1, 0.8, 0.3))
    tag("AL REVÉS", W / 2, y0 + 2 * chh + 64 + 46, ss((t - t_rev) / 0.3), (0.8, 0.8, 0.85))
    # contador de señales
    rrect(ctx, W / 2 - 150, y0 + 2 * chh + 120, 300, 90, 20); ctx.set_source_rgba(0.08, 0.09, 0.12, 0.85 * p); ctx.fill()
    ctx.set_font_size(58); s = f"{n} / 32"; e = ctx.text_extents(s)
    ctx.move_to(W / 2 - e.width / 2, y0 + 2 * chh + 186); ctx.set_source_rgba(*IRC, p); ctx.show_text(s)

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    BY = H * 0.265
    # visor de la cámara del móvil
    vp = max(win(t, 0.0, T("a simple") - 0.15, 0.25) if t > 0.05 else 1.0,
             win(t, T("pero muchas") - 0.05, T("pero hay un problema") - 0.1), win(t, T("sígueme") + 0.4, DUR + 5))
    visor(ctx, vp, t)
    a0, a1 = T("a simple"), T("vamos a inventar")
    if a0 <= t < a1:
        C.badge(ctx, "✓ CÁMARA", W / 2, BY, win(t, a0 - 0.1, a1), G, size=72)
        C.badge(ctx, "✗ OJO", W / 2, BY + 130, win(t, a0 + 0.5, a1), R, size=72)
    label(C, ctx, t, T("una bombillita") + 0.6, T("pero si fuera"), "LED", A, "led", dx=0, dy=-170, size=70)
    # luz normal: destellos visibles
    a0, a1 = T("pero si fuera"), T("así que usas infrarrojo")
    if a0 + 0.5 <= t < a1:
        C.badge(ctx, "✗ SE VE", W / 2, BY, win(t, a0 + 0.5, a1), R, size=76)
    espectro(ctx, t, T("a unos novecientos"), T("pero muchas") - 0.1)
    # otras fuentes de infrarrojo
    a1 = T("cómo distingue") + 0.4
    label(C, ctx, t, T("el sol") - 0.05, a1, "SOL", A, "sol", dy=-90, size=56)
    label(C, ctx, t, T("las bombillas") - 0.05, a1, "BOMBILLA", A, "bomb", dy=-80, size=56)
    label(C, ctx, t, T("y la estufa") - 0.05, a1, "ESTUFA", A, "estu", dy=-90, size=56)
    a0, a1 = T("cómo distingue") + 1.2, T("así que haces") + 0.2
    label(C, ctx, t, a0, a1, "RECEPTOR", A, "rx", dx=-60, dy=-150, size=60)
    if a0 <= t < a1:
        C.badge(ctx, "¿ CUÁL ES ?", W / 2, BY, win(t, a0, a1), Y, size=74)
    # parpadeo: contador
    a0, a1 = T("treinta y ocho"), T("pero ahora tienes")
    if a0 - 0.2 <= t < a1:
        v = keyed(t, [(a0 - 0.2, 0), (a0 + 1.6, 38000)])
        C.badge(ctx, f"{miles(v)} / s", W / 2, BY, win(t, a0 - 0.2, a1), (0.85, 0.6, 1.0), size=92)
    label(C, ctx, t, T("el receptor") + 0.6, T("e ignora"), "RECEPTOR", A, "rx", dx=-80, dy=-150, size=60)
    a0, a1 = T("e ignora"), T("pero ahora tienes")
    if a0 <= t < a1:
        C.badge(ctx, "✗ LO DEMÁS", W / 2, BY + 140, win(t, a0, a1), R, size=66)
    # unos y ceros
    onda(ctx, t, T("así que mandas") + 0.6, T("y aquí viene") + 0.2, T("ráfaga larga"), T("ráfaga corta"))
    # 32 señales
    bits32(ctx, t)
    a0, a1 = T("para comprobar") + 0.9, T("si algo")
    if a0 <= t < a1:
        C.badge(ctx, "✓", W / 2, H * 0.6, win(t, a0, a1), G, size=110)
    a0, a1 = T("si algo") + 0.2, T("por eso tienes") - 0.1
    if a0 <= t < a1:
        C.badge(ctx, "✗ CANAL", W / 2, H * 0.6, win(t, a0, a1), R, size=80)
    # rebote y sofá
    label(C, ctx, t, T("la luz rebota") + 0.4, T("pero no atraviesa"), "REBOTE", A, "wb", dx=-120, dy=-90, size=60)
    a0, a1 = T("pero no atraviesa") + 0.5, T("sígueme") + 0.2
    if a0 <= t < a1:
        x, y = A("sofa"); C.badge(ctx, "✗", clampx(x), clampy(y - 120), win(t, a0, a1), R, size=100)

def sfx_events(C):
    E = [(0.15, C.s_bleep(1200), 0.25), (1.35, C.s_bleep(1200), 0.25), (2.5, C.s_bleep(1200), 0.25), (3.45, C.s_bleep(1200), 0.25),
         (T("a simple"), C.s_fail(), 0.3), (T("vamos a inventar"), C.s_whoosh(), 0.45), (T("quieres cambiar"), C.s_whoosh(), 0.35),
         (T("una bombillita") + 0.85, C.s_thud(), 0.45), (T("pero si fuera") + 0.5, C.s_pop(), 0.4), (T("pero si fuera") + 1.9, C.s_pop(), 0.4),
         (T("pero si fuera") + 3.2, C.s_pop(), 0.4), (T("a unos novecientos"), C.s_whoosh(), 0.35), (T("pero muchas"), C.s_win(), 0.35),
         (T("pero hay un problema"), C.s_whoosh(), 0.4), (T("el sol"), C.s_pop(), 0.35), (T("las bombillas"), C.s_pop(), 0.35),
         (T("y la estufa"), C.s_pop(), 0.35), (T("cómo distingue") + 1.2, C.s_fail(), 0.3), (T("así que haces") + 0.3, C.s_buzz(2.0), 0.25),
         (T("treinta y ocho"), C.s_coin(), 0.4), (T("e ignora"), C.s_fail(), 0.3), (T("así que mandas"), C.s_whoosh(), 0.4),
         (T("ráfaga larga"), C.s_bleep(900), 0.35), (T("ráfaga corta"), C.s_bleep(1400), 0.35), (T("cada pulsación"), C.s_whoosh(), 0.4),
         (T("ocho dicen"), C.s_pop(), 0.4), (T("ocho dicen", 2), C.s_pop(), 0.4), (T("y las otras"), C.s_pop(), 0.4),
         (T("para comprobar") + 0.9, C.s_win(), 0.4), (T("si algo") + 0.2, C.s_fail(), 0.4), (T("la luz rebota") + 0.4, C.s_pop(), 0.4),
         (T("pero no atraviesa") + 0.5, C.s_thud(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
