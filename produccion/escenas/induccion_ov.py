# Capa 2D de «Si tuvieras que inventar la placa de inducción…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("induccion")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"inducción", "frío", "fuego", "cuarenta", "dentro", "bobina", "cobre", "veinte", "cien", "magnético", "remolinos",
            "calienta", "imanes", "hierro", "imán", "cristal", "noventa", "metal", "corta", "parpadea"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def miles(v): return f"{int(round(v)):,}".replace(",", ".")
BY = H * 0.265

def meter(C, ctx, x, y, frac, p, col, label):
    """barra de rendimiento: label + barra que se llena"""
    if p <= 0: return
    w, h = 620, 54
    ctx.save(); ctx.translate(x, y); s = C.back(p)
    if s < 1e-3: ctx.restore(); return
    ctx.scale(s, s)
    C.rrect(ctx, -w / 2 - 8, -h / 2 - 8, w + 16, h + 16, 20); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92); ctx.fill()
    if frac > 0.01:
        C.rrect(ctx, -w / 2, -h / 2, w * frac, h, 14); ctx.set_source_rgb(*col); ctx.fill()
    ctx.restore()
    C.outlined(ctx, label, x, y + 4, 50, fill=(1, 1, 1), stroke=9, alpha=p)

def thermo(C, ctx, x, y, temp, p, col, name):
    if p <= 0: return
    C.badge(ctx, "%s %d °C" % (name, round(temp)), clampx(x, 300), clampy(y), p, col, size=56)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    O = (1.0, 0.55, 0.25)
    # el agua hierve, el cristal de al lado está frío
    a0, a1 = 0.0, T("vamos a inventarla")
    if t < a1:
        x, y = A("pot"); thermo(C, ctx, x, y - 120, 100, win(t, 0.05, a1), O, "AGUA")
        x, y = A("glassF"); thermo(C, ctx, x + 60, y + 170, 24, win(t, T("pero el cristal"), a1), B, "CRISTAL")
    # gas: 40 %
    a0, a1 = T("con fuego"), T("así que pones")
    if a0 <= t < a1:
        label(C, ctx, t, a0 + 0.8, T("con gas"), "SE ESCAPA", A, "pot", dx=0, dy=-160, size=60)
        meter(C, ctx, W / 2, BY, 0.4 * sg(t, T("con gas"), T("cuarenta", fin=True)), win(t, T("con gas"), a1), O,
              "GAS: %d %%" % round(40 * sg(t, T("con gas"), T("cuarenta", fin=True))))
    # bobina
    label(C, ctx, t, T("bobina") + 0.3, T("le metes"), "COBRE", A, "coil", dx=-60, dy=170, size=62)
    a0, a1 = T("le metes"), T("eso crea")
    if a0 <= t < a1 + 0.3:
        b0 = T("veinte mil"); b1 = T("cien mil", fin=True)
        v = 20000 + 80000 * sg(t, T("y cien"), b1) if t > b0 else 0
        if t > b0:
            C.badge(ctx, miles(v) + " VECES/S", W / 2, BY, win(t, b0, a1 + 0.3), Y, size=76)
        C.badge(ctx, "+  −  +  −" if int(t * 6) % 2 else "−  +  −  +", W / 2, BY + 140, win(t, a0 + 0.3, a1 + 0.3), B, size=60)
    # campo magnético
    label(C, ctx, t, T("eso crea") + 0.3, T("ahí dentro"), "CAMPO", A, "coil", dx=-140, dy=-330, size=62)
    # remolinos y temperatura del fondo
    a0, a1 = T("ahí dentro"), T("pero no vale")
    if a0 <= t < a1:
        x, y = A("bottom")
        temp = 20 + 200 * sg(t, a0 + 0.4, T("se calienta", fin=True) + 0.3)
        thermo(C, ctx, W / 2, BY, temp, win(t, a0, a1), O, "FONDO")
        label(C, ctx, t, a0 + 0.5, T("y el metal"), "REMOLINOS", A, "bottom", dx=0, dy=200, size=58)
    # imán: hierro sí, aluminio no
    a0, a1 = T("tiene que ser"), T("si tu sartén")
    if a0 <= t < a1:
        C.badge(ctx, "✓ HIERRO", W / 2, BY, win(t, T("como el hierro") - 0.6, a1), G, size=70)
    a0, a1 = T("si tu sartén"), T("y aquí viene")
    if a0 <= t < a1:
        C.badge(ctx, "✗ ALUMINIO", W / 2, BY, win(t, a0 + 1.0, a1), R, size=70)
        x, y = A("pan"); thermo(C, ctx, x, y - 200, 22, win(t, T("la placa ni"), a1), B, "SARTÉN")
    # el cristal: solo se calienta por la olla
    a0, a1 = T("la bobina no"), T("y así aprovechas")
    if a0 <= t < a1:
        b0 = T("el cristal solo"); b1 = T("por eso se enfría")
        if t < b0: g = 22
        elif t < b1 + 0.3: g = 22 + 38 * sg(t, b0 + 0.3, b1)
        else: g = 60 - 32 * sg(t, b1 + 0.3, a1 - 0.2)
        C.badge(ctx, "CRISTAL %d °C" % round(g), W / 2, BY, win(t, a0, a1), B if g < 40 else O, size=70)
        if t < b1 + 0.3:
            C.badge(ctx, "OLLA 100 °C", W / 2, BY + 130, win(t, b0, b1 + 0.3), O, size=60)
    # 90 % frente a 40 %
    a0, a1 = T("y así aprovechas"), T("pero ahora hay")
    if a0 <= t < a1 + 0.2:
        pp = win(t, a0, a1 + 0.2)
        meter(C, ctx, W / 2, BY, 0.4, pp, O, "GAS: 40 %")
        f = 0.9 * sg(t, a0 + 0.3, T("noventa", fin=True))
        meter(C, ctx, W / 2, BY + 110, f, pp, G, "INDUCCIÓN: %d %%" % round(100 * f))
    # detección de metal
    a0, a1 = T("así que la placa"), T("por eso parpadea")
    if a0 <= t < a1:
        ok = t < T("si no detecta") + 0.3
        C.badge(ctx, ("¿METAL?" if ok else "✗ 0 METAL"), W / 2, BY, win(t, a0 + 0.2, a1), Y if ok else R, size=70)
        if t > T("corta la"):
            C.badge(ctx, "0 A", W / 2, BY + 130, win(t, T("corta la"), a1), R, size=80)
    label(C, ctx, t, T("por eso parpadea") + 0.2, T("sígueme"), "PILOTO", A, "led", dx=-40, dy=-150, size=58)

def sfx_events(C):
    E = [(0.0, C.s_buzz(2.5), 0.15), (T("pero el cristal") + 0.2, C.s_pop(), 0.45), (T("vamos a inventarla"), C.s_whoosh(), 0.4),
         (T("con fuego"), C.s_whoosh(0.9), 0.45), (T("cuarenta"), C.s_fail(), 0.35), (T("así que pones"), C.s_whoosh(), 0.4),
         (T("bobina"), C.s_clank(), 0.4), (T("le metes"), C.s_buzz(3.8), 0.18), (T("eso crea"), C.s_whoosh(0.9), 0.4),
         (T("atraviesa"), C.s_whoosh(), 0.35), (T("ahí dentro"), C.s_pop(), 0.4), (T("se calienta"), C.s_coin(), 0.4),
         (T("tiene que ser") + 1.1, C.s_clank(), 0.5), (T("como el hierro"), C.s_win(), 0.35), (T("si tu sartén") + 1.0, C.s_fail(), 0.4),
         (T("y aquí viene"), C.s_whoosh(), 0.4), (T("por eso se enfría"), C.s_whoosh(), 0.4), (T("noventa"), C.s_win(), 0.4),
         (T("si quitas"), C.s_whoosh(), 0.4), (T("si no detecta"), C.s_fail(), 0.35), (T("corta la"), C.s_thud(), 0.45),
         (T("sígueme"), C.s_pop(), 0.4)]
    t0 = T("por eso parpadea")
    for i in range(7): E.append((t0 + i / 1.5, C.s_bleep(1500), 0.12))
    return E
