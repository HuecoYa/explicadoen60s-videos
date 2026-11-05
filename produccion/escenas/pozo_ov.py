# Capa 2D de «¿Y si construyes un pozo?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("pozo")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"agua", "casa", "broca", "veinte", "metros", "arena", "subterránea", "tubo", "quince", "centímetros", "ranuras", "rejilla",
            "grava", "colador", "cemento", "bomba", "aspire", "diez", "aire", "atmósfera", "fondo", "sumergida", "empuja", "embudo",
            "vecino", "rápido", "mide"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def coma(v, d=1): return (f"%.{d}f" % v).replace(".", ",")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    label(C, ctx, t, 0.9, T("primero"), "TU CASA", A, "casa", dx=0, dy=110, size=60)
    label(C, ctx, t, 1.4, T("primero"), "AGUA", A, "acu", dx=60, dy=-110, size=64)
    # profundidad
    a0, a1 = T("una broca"), T("pero las paredes")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 1.0), (T("a veinte") + 0.2, 20.0), (T("el agua subterránea") + 1.0, 23.0)])
        C.badge(ctx, f"PROFUNDIDAD {int(v)} m", W / 2, H * 0.265, win(t, a0, a1), Y, size=80)
    label(C, ctx, t, T("encuentras") + 0.2, T("pero las paredes"), "ACUÍFERO", A, "acu", dx=40, dy=-100, size=60)
    badge(C, ctx, t, T("se desmoronan") - 0.2, T("así que metes"), "✗ DERRUMBE", R, size=86)
    # 15 cm
    a0, a1 = T("quince") - 0.6, T("pero el tubo")
    p = win(t, a0, a1)
    if p:
        (x0, y0), (x1, _) = A("tl"), A("tr")
        C.arrow_dim(ctx, x0, x1, y0, Y, p); C.callout(ctx, "15 cm", (x0 + x1) / 2, y0 - 110, p, size=72)
    badge(C, ctx, t, T("no puede entrar") - 0.3, T("así que", 2), "✗ 0 LITROS", R, size=86)
    label(C, ctx, t, T("la rejilla") - 0.3, T("y alrededor"), "REJILLA", A, "rej", dx=-170, dy=-150, size=58)
    label(C, ctx, t, T("deja pasar"), T("y alrededor"), "✓ AGUA", A, "rej", dx=-190, dy=60, size=56)
    label(C, ctx, t, T("pero no la arena") - 0.2, T("y alrededor"), "✗ ARENA", A, "rej2", dx=190, dy=60, size=56)
    label(C, ctx, t, T("rellenas con"), T("arriba"), "GRAVA", A, "grava", dx=200, dy=-80, size=60)
    label(C, ctx, t, T("sellas con"), T("ahora"), "CEMENTO", A, "cem", dx=230, dy=150, size=58)
    label(C, ctx, t, T("agua sucia") - 0.3, T("ahora"), "✗ AGUA SUCIA", A, "cem", dx=-120, dy=-200, size=52)
    label(C, ctx, t, T("una bomba") + 0.3, T("aspirando") + 0.3, "BOMBA", A, "bomba", dx=210, dy=90, size=58)
    # el agua aspirada solo sube 10 m
    a0, a1 = T("aspirando"), T("así que bajas")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0.0), (a0 + 1.8, 10.6), (a0 + 2.4, 10.0)])
        col = R if t > a0 + 1.9 else B
        C.badge(ctx, f"SUBE {coma(min(v, 10.0))} m", W / 2, H * 0.265, win(t, a0, a1), col, size=82)
    label(C, ctx, t, T("aspirando") + 2.0, T("en realidad"), "TOPE", A, "colw", dx=200, dy=-40, size=56)
    label(C, ctx, t, T("de la atmósfera") - 0.3, T("así que bajas"), "AIRE", A, "aire", dx=-230, dy=-60, size=60)
    label(C, ctx, t, T("sumergida") - 0.4, T("y en vez") + 1.0, "BOMBA", A, "sumer", dx=-220, dy=-40, size=58)
    a0, a1 = T("y en vez"), T("pero al bombear")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0.0), (a0 + 1.6, 22.0)])
        C.badge(ctx, f"{'✓ ' if v > 21.9 else ''}SUBE {int(v)} m", W / 2, H * 0.265, win(t, a0, a1), G, size=82)
    # nivel del agua y embudo
    a0, a1 = T("pero al bombear"), T("y puedes secar")
    if a0 <= t < a1:
        D = keyed(t, [(a0 + 0.3, 0.0), (T("y forma") + 1.0, 1.2), (T("si bombeas"), 1.3), (T("y puedes secar") + 0.3, 3.0)])
        C.badge(ctx, f"NIVEL −{coma(18 + D)} m", W / 2, H * 0.265, win(t, a0, a1), B, size=80)
    label(C, ctx, t, T("y forma") + 0.3, T("y puedes secar"), "NIVEL", A, "cono", dx=160, dy=-110, size=58)
    label(C, ctx, t, T("el embudo crece") - 0.3, T("por eso se mide"), "VECINO", A, "vecino", dx=-30, dy=-260, size=58)
    badge(C, ctx, t, T("del vecino") - 0.2, T("por eso se mide"), "✗ POZO SECO", R, size=84)
    a0, a1 = T("por eso se mide") + 1.3, DUR + 1
    if a0 <= t < a1:
        q = keyed(t, [(a0, 3.0), (a0 + 1.9, 1.2)])
        C.badge(ctx, f"CAUDAL {coma(q)} L/s", W / 2, clampy(A("dial")[1] + 230), win(t, a0, a1), Y, size=80)
    label(C, ctx, t, T("por eso se mide") + 1.3, DUR + 1, "CAUDALÍMETRO", A, "dial", dx=-260, dy=70, size=54)

def sfx_events(C):
    E = [(0.0, C.s_buzz(4.0), 0.3), (0.05, C.s_whoosh(), 0.4), (T("una broca"), C.s_buzz(5.5), 0.3), (T("a veinte"), C.s_pop(), 0.45),
         (T("el agua subterránea"), C.s_win(), 0.35), (T("se desmoronan"), C.s_thud(), 0.5), (T("así que metes"), C.s_whoosh(), 0.4),
         (T("quince") - 0.2, C.s_clank(), 0.4), (T("no puede entrar"), C.s_fail(), 0.4), (T("la rejilla"), C.s_pop(), 0.45),
         (T("deja pasar"), C.s_win(), 0.35), (T("rellenas con"), C.s_clank(), 0.35), (T("sellas con"), C.s_thud(), 0.45),
         (T("una bomba"), C.s_buzz(3.0), 0.3), (T("aspirando") + 1.9, C.s_fail(), 0.4), (T("así que bajas"), C.s_whoosh(), 0.4),
         (T("y en vez"), C.s_buzz(2.5), 0.3), (T("y en vez") + 1.6, C.s_win(), 0.4), (T("y forma"), C.s_whoosh(), 0.35),
         (T("del vecino"), C.s_fail(), 0.45), (T("por eso se mide"), C.s_pop(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
