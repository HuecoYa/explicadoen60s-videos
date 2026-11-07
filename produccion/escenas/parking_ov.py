# Capa 2D de «¿Y si construyes un parking subterráneo?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("parking")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"rampa", "edificio", "excavar", "tres", "plantas", "diez", "metros", "derrumba", "paredes", "zanjas", "acero", "hormigón",
            "pantalla", "empuja", "suelo", "puntal", "agua", "empapado", "juntas", "pozo", "bombas", "peligro", "monóxido", "carbono",
            "huele", "acumula", "detectores", "cincuenta", "millón", "ventiladores", "chimeneas", "limpio", "apagar", "cerrado"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def miles(v): return f"{int(round(v)):,}".replace(",", ".")
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

def ppm(t):
    a = T("los tubos de escape")
    v = keyed(t, [(a, 0.0), (T("no huele"), 12.0), (T("se acumula", fin=True), 34.0), (T("cuando llegan") + 0.3, 42.0), (T("por millón", fin=True), 50.0),
                  (T("se encienden") + 0.6, 52.0), (T("cuando el aire"), 18.0), (T("se vuelven"), 8.0), (T("por eso nunca"), 8.0), (DUR, 180.0)])
    return v if t > a else 0.0

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # bajando la rampa: profundidad
    a0, a1 = 0.0, T("y si tuvieras")
    if t < a1:
        z = keyed(t, [(0.0, 0.8), (2.3, 3.3)])
        C.badge(ctx, "-%s m" % ("%.1f" % z).replace(".", ","), W / 2, BY, win(t, -0.5, a1), Y, size=90)
    # tres plantas, diez metros
    a0, a1 = T("quieres tres"), T("pero si cavas")
    if a0 <= t < a1:
        n = min(3, int(1 + (t - a0 - 0.4) / 0.35)) if t > a0 + 0.4 else 0
        C.badge(ctx, f"{n} PLANTAS", W / 2, BY, win(t, a0, a1), (1, 1, 1), size=74)
        if t > T("unos diez") - 0.1:
            h = 10 * sg(t, T("unos diez"), T("de hondo", fin=True))
            C.badge(ctx, f"{int(round(h))} m", W / 2, BY + 150, win(t, T("unos diez") - 0.1, a1), Y, size=90)
    a0, a1 = T("la tierra de los lados") + 0.3, T("así que antes")
    if a0 <= t < a1: C.badge(ctx, "✗ DERRUMBE", W / 2, BY, win(t, a0, a1), R, size=80)
    # zanjas
    a0, a1 = T("haces zanjas"), T("y las rellenas")
    if a0 <= t < a1:
        d = 14 * sg(t, a0 - 0.2, T("y profundas", fin=True))
        C.badge(ctx, f"{int(round(d))} m", W / 2, BY, win(t, a0, a1), Y, size=90)
        C.badge(ctx, "60 cm DE ANCHO", W / 2, BY + 150, win(t, a0 + 0.4, a1), (1, 1, 1), size=56)
    label(C, ctx, t, T("acero") - 0.2, T("y hormigón") + 0.2, "ACERO", A, "cage", dx=-170, dy=-40, size=56)
    label(C, ctx, t, T("y hormigón"), T("ahora sí"), "HORMIGÓN", A, "trench", dx=-200, dy=0, size=56)
    # empuje y puntales
    label(C, ctx, t, T("pero la tierra de fuera") + 0.6, T("así que haces"), "EMPUJE", A, "push", dx=-30, dy=-150, size=56)
    a0, a1 = T("vacías la"), T("pero al bajar")
    if a0 <= t < a1:
        d = keyed(t, [(a0, 0.0), (T("de dentro", fin=True), 3.6), (T("así que haces el suelo"), 3.6), (T("de cada planta", fin=True), 7.0), (T("como un puntal", fin=True), 10.4)])
        C.badge(ctx, "-%d m" % int(round(d)), W / 2, BY, win(t, a0, a1), Y, size=88)
    label(C, ctx, t, T("así que haces el suelo") + 0.4, T("pero al bajar"), "FORJADO", A, "slab", dx=0, dy=-90, size=54)
    # agua
    label(C, ctx, t, T("en muchas"), T("así que en el fondo"), "NIVEL FREÁTICO", A, "wt", dx=40, dy=-60, size=50)
    a0, a1 = T("en muchas"), T("esa agua empuja")
    if a0 <= t < a1:
        C.badge(ctx, "AGUA A -4 m", W / 2, BY, win(t, a0, a1), B, size=74)
    a0, a1 = T("así que en el fondo") + 0.6, T("y aquí viene") + 0.3
    if a0 <= t < a1:
        v = 2400 * sg(t, a0, a1) ** 1.2
        C.badge(ctx, "+" + miles(v) + " L", W / 2, BY, win(t, a0, a1), B, size=84)
    label(C, ctx, t, T("así que en el fondo") + 0.3, T("que la sacan", fin=True), "BOMBA", A, "pump", dx=150, dy=-80, size=56)
    # CO
    label(C, ctx, t, T("los tubos de escape") + 1.0, T("no huele"), "CO", A, "exhaust", dx=60, dy=-120, size=72)
    a0, a1 = T("no huele"), T("por eso nunca")
    if a0 <= t < a1:
        p = ppm(t); col = R if p >= 49.5 else (Y if p > 20 else G)
        C.badge(ctx, f"{int(round(p))} ppm CO", W / 2, BY, win(t, a0, a1), col, size=80)
    label(C, ctx, t, T("así que en cada planta") + 0.3, T("cuando llegan"), "DETECTOR", A, "det", dx=60, dy=-120, size=52)
    label(C, ctx, t, T("sacan el aire"), T("y entra aire"), "CHIMENEA", A, "chim", dx=170, dy=60, size=52)
    a0, a1 = T("y entra aire"), T("cuando el aire")
    if a0 <= t < a1:
        x, y = A("fresh"); C.callout(ctx, "AIRE LIMPIO", clampx(x - 60), clampy(y - 120), win(t, a0, a1), size=52)
    a0, a1 = T("cuando el aire"), T("por eso nunca")
    if a0 <= t < a1: C.badge(ctx, "✓ VENTILADORES OFF", W / 2, BY + 150, win(t, T("se vuelven"), a1), G, size=54)
    a0, a1 = T("por eso nunca"), DUR
    if a0 <= t < a1:
        p = ppm(t)
        C.badge(ctx, f"✗ {int(round(p))} ppm CO", W / 2, BY, win(t, a0, a1), R, size=80)

def sfx_events(C):
    E = [(0.0, C.s_buzz(2.4), 0.25), (0.1, C.s_whoosh(1.2), 0.4), (2.3, C.s_thud(), 0.35), (T("y si tuvieras"), C.s_whoosh(), 0.5),
         (T("vamos a excavar"), C.s_clank(), 0.45), (T("quieres tres") + 0.4, C.s_pop(), 0.35), (T("quieres tres") + 0.75, C.s_pop(), 0.35),
         (T("quieres tres") + 1.1, C.s_pop(), 0.35), (T("unos diez"), C.s_whoosh(), 0.35), (T("la tierra de los lados"), C.s_thud(), 0.55),
         (T("se derrumba"), C.s_fail(), 0.4), (T("construyes las paredes"), C.s_whoosh(), 0.4), (T("haces zanjas"), C.s_clank(), 0.45),
         (T("acero"), C.s_clank(), 0.45), (T("y hormigón"), C.s_whoosh(1.0), 0.4), (T("se llaman"), C.s_win(), 0.35), (T("vacías la"), C.s_clank(), 0.4),
         (T("empuja los muros"), C.s_fail(), 0.4), (T("así que haces el suelo") + 0.3, C.s_thud(), 0.45), (T("de cada planta"), C.s_thud(), 0.4),
         (T("que los sujeta"), C.s_thud(), 0.4), (T("aparece el agua"), C.s_pop(), 0.35), (T("y se cuela"), C.s_fail(), 0.35),
         (T("así que en el fondo"), C.s_buzz(3.0), 0.3), (T("y aquí viene"), C.s_whoosh(), 0.45), (T("los tubos de escape"), C.s_buzz(2.0), 0.2),
         (T("cuando llegan") + 1.2, C.s_fail(), 0.45), (T("se encienden"), C.s_buzz(4.0), 0.3), (T("sacan el aire"), C.s_whoosh(1.2), 0.4),
         (T("se vuelven"), C.s_win(), 0.4), (T("por eso nunca"), C.s_fail(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
