# Capa 2D de «Así ve la cámara de tu móvil»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("camara")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"foto", "millones", "puntos", "luz", "lentes", "chip", "uña", "sensor", "píxeles", "cincuenta", "milésima", "milímetro",
            "electricidad", "electrones", "cien", "quinientos", "mil", "color", "filtro", "rojo", "verde", "azul", "verdes", "ojos",
            "vecinos", "colores", "enfoque", "muelles", "bobina", "imanes", "corriente", "cerca", "lejano", "estabilizador", "temblor"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    label(C, ctx, t, T("detrás de las") + 0.4, T("el sensor"), "LENTES", A, "lente2", dx=-250, dy=40, size=60)
    label(C, ctx, t, T("el sensor") - 0.2, T("está lleno") + 0.4, "SENSOR", A, "sensor", dx=0, dy=150, size=62)
    label(C, ctx, t, T("que una uña") - 0.2, T("el sensor") + 0.8, "UÑA", A, "una", dx=-60, dy=-130, size=58)
    a0, a1 = T("muchos móviles"), T("y cada uno mide")
    if a0 <= t < a1:
        v = 50e6 * min(1, (t - a0) / 1.6); C.badge(ctx, miles(v), W / 2, H * 0.265, win(t, a0, a1), Y, size=96)
    a0, a1 = T("una milésima"), T("cuando entra")
    if a0 - 0.3 <= t < a1:
        C.badge(ctx, "0,001 mm", W / 2, H * 0.265, win(t, a0 - 0.3, a1), Y, size=96)
        label(C, ctx, t, a0, a1, "1 PÍXEL", A, "pix", dx=0, dy=-130, size=56)
    a0, a1 = T("más luz"), T("pero un píxel")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("cien"), 100), (T("quinientos"), 500), (T("mil"), 1000)])
        C.badge(ctx, f"{miles(v)} ELECTRONES", W / 2, H * 0.265, win(t, a0, a1), B, size=78)
    badge(C, ctx, t, T("no sabe"), T("así que encima"), "✗ SIN COLOR", R, size=86)
    a0, a1 = T("la mitad"), T("luego")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        for k, (txt, col) in enumerate((("VERDE 50 %", G), ("ROJO 25 %", R), ("AZUL 25 %", B))):
            q = min(p, max(0, (t - a0 - 0.25 * k) / 0.3))
            C.badge(ctx, txt, W / 2, H * 0.265 + 125 * k, q, col, size=70)
    label(C, ctx, t, T("mira a los"), T("así salen"), "VECINOS", A, "pix", dx=0, dy=-170, size=58)
    label(C, ctx, t, T("de unos muelles") - 0.2, T("rodeada"), "MUELLES", A, "muelle", dx=-80, dy=110, size=56)
    label(C, ctx, t, T("una bobina"), T("cuando pasa"), "BOBINA", A, "bobina", dx=-120, dy=60, size=56)
    label(C, ctx, t, T("y unos imanes"), T("cuando pasa"), "IMÁN", A, "iman2", dx=60, dy=-140, size=56)
    a0, a1 = T("cuando pasa"), T("y el estabilizador")
    if a0 <= t < a1:
        enf = keyed(t, [(a0, 0.0), (a0 + 1.2, 0.6), (T("si se aleja"), 0.6), (T("si se aleja") + 0.6, 0.9), (T("si se acerca"), 0.9),
                        (T("si se acerca") + 0.5, 0.05), (T("todo"), 0.05), (T("todo") + 0.4, 0.5), (T("todo") + 0.8, 0.2)])
        s = ("%.2f" % (enf / 3)).replace(".", ",")
        C.badge(ctx, f"LENTE +{s} mm", W / 2, H * 0.265, win(t, a0, a1), Y, size=80)
    label(C, ctx, t, T("enfoca lo que"), T("si se acerca"), "CERCA", A, "lente2", dx=-250, dy=-80, size=62)
    label(C, ctx, t, T("enfoca lo lejano"), T("todo"), "LEJOS", A, "lente2", dx=250, dy=-80, size=62)
    badge(C, ctx, t, T("y el estabilizador") + 0.4, T("mueve la lente"), "✗ TEMBLOR", R, size=84)
    badge(C, ctx, t, T("para compensar"), DUR + 1, "✓ COMPENSADO", G, size=80)

def sfx_events(C):
    E = [(0.05, C.s_whoosh(), 0.4)]
    for k in range(6): E.append((0.02 + 1.2 * k, C.s_pop(), 0.35))
    E += [(T("detrás de las"), C.s_whoosh(), 0.45), (T("el sensor"), C.s_pop(), 0.45), (T("muchos móviles"), C.s_pop(), 0.45),
          (T("cuando entra"), C.s_whoosh(), 0.4), (T("cien"), C.s_coin(), 0.4), (T("quinientos"), C.s_coin(), 0.4), (T("mil"), C.s_coin(), 0.45),
          (T("no sabe"), C.s_fail(), 0.45), (T("así que encima"), C.s_whoosh(), 0.4), (T("la mitad"), C.s_pop(), 0.45),
          (T("calcula"), C.s_win(), 0.4), (T("y el enfoque"), C.s_whoosh(), 0.4), (T("cuando pasa"), C.s_buzz(1.5), 0.35),
          (T("si se aleja"), C.s_pop(), 0.4), (T("si se acerca"), C.s_pop(), 0.4), (T("y el estabilizador"), C.s_buzz(2.0), 0.3),
          (T("para compensar"), C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
