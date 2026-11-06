# Capa 2D de «¿Y si construyes el depósito de agua de tu pueblo?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("deposito")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"grifo", "fuerza", "empujando", "depósito", "pozo", "bomba", "tubos", "seca", "mañana", "ducha", "abasto", "suelo",
            "pisos", "alto", "gravedad", "diez", "metros", "bar", "treinta", "tres", "bares", "pesa", "hormigón", "copa", "ancho",
            "estrecho", "llenando", "baja", "quieta", "estropea", "renueva", "luz", "horas"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

def nivel(t):
    return keyed(t, [(0, 0.0), (T("así que construyes") + 0.3, 0.0), (T("pero si lo pones"), 0.85), (T("y aquí viene"), 0.85),
                     (T("el agua del"), 0.6), (T("la bomba lo va"), 0.6), (T("y cuando todos") - 0.2, 0.95), (T("el depósito baja", fin=True) + 0.6, 0.55),
                     (T("así que cada"), 0.55), (T("así que cada") + 1.2, 0.2),
                     (T("y el agua siempre") - 0.2, 0.92), (T("y el agua siempre") + 0.9, 0.3), (T("por eso", 1), 0.9), (T("sigue saliendo", fin=True), 0.45), (DUR + 2, 0.4)])

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # el grifo empuja con fuerza
    a0, a1 = T("y el agua sale") , T("vamos a construir")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0.0), (T("con fuerza", fin=True), 3.0)])
        C.badge(ctx, ("%.1f BAR" % v).replace(".", ","), W / 2, BY, win(t, a0, a1), Y, size=92)
    label(C, ctx, t, T("pero nadie"), T("vamos a construir"), "?", A, "grifo", dx=-150, dy=-260, size=110)
    label(C, ctx, t, T("de un pozo") - 0.2, T("pero si la bomba"), "POZO", A, "pozo", dx=0, dy=-20, size=58)
    label(C, ctx, t, T("con una bomba") - 0.1, T("pero si la bomba"), "BOMBA", A, "bomba", dx=20, dy=-110, size=58)
    a0, a1 = T("pero si la bomba"), T("y por la mañana")
    if a0 <= t < a1:
        C.badge(ctx, "✗ BOMBA", W / 2, BY, win(t, a0, a1), R, size=86)
        if t > T("el grifo se") - 0.2:
            v = keyed(t, [(T("el grifo se") - 0.2, 12), (T("se seca", fin=True), 0)])
            C.badge(ctx, f"{int(v)} L/min", W / 2, BY + 145, win(t, T("el grifo se") - 0.2, a1), B, size=74)
    a0, a1 = T("y por la mañana"), T("así que construyes")
    if a0 <= t < a1:
        hh = keyed(t, [(a0, 7.0), (a1, 8.5)]); C.badge(ctx, "%02d:%02d" % (int(hh), int((hh % 1) * 60)), W / 2, BY, win(t, a0, a1), Y, size=90)
        n = int(min(5, 1 + (t - a0) * 2.5)); C.badge(ctx, f"{n} GRIFOS", W / 2, BY + 145, win(t, a0 + 0.2, a1), B, size=72)
    a0, a1 = T("así que construyes") + 0.3, T("pero si lo pones")
    if a0 <= t < a1:
        C.badge(ctx, f"{int(100 * nivel(t) / 0.85)} %", W / 2, BY, win(t, a0, a1), B, size=90)
    a0, a1 = T("el agua no sube") - 0.2, T("así que lo subes") + 0.3
    for k in (1, 2, 3):
        label(C, ctx, t, a0 + 0.15 * k, a1, "✗", A, f"f{k}", dx=110, dy=-20, size=72)
    label(C, ctx, t, a0, a1, "OK", A, "f0", dx=120, dy=-20, size=58)
    a0, a1 = T("así que lo subes"), T("cada diez") - 0.2
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("muy alto", fin=True) + 0.3, 30)])
        C.badge(ctx, f"{int(v)} m", W / 2, BY, win(t, a0, a1), Y, size=92)
    # regla: 10 m = 1 bar … 30 m = 3 bar
    a0, a1 = T("cada diez") - 0.2, T("pero tanta")
    if a0 <= t < a1:
        h = keyed(t, [(T("cada diez"), 0.0), (T("de altura"), 10), (T("un depósito de"), 10), (T("treinta") + 0.4, 30)])
        C.badge(ctx, ("%.1f BAR" % (h / 10)).replace(".", ","), W / 2, BY, win(t, a0, a1), Y, size=92)
        for k, key in ((1, "r10"), (2, "r20"), (3, "r30")):
            if h >= 10 * k - 0.3:
                x, y = A(key); C.callout(ctx, f"{10 * k} m", clampx(x - 150, 150), y, win(t, T("de altura") if k == 1 else T("un depósito de") + 0.3 * k, a1), size=54)
    label(C, ctx, t, T("de hormigón") - 0.3, T("y le das forma"), "HORMIGÓN", A, "col", dx=200, dy=0, size=58)
    a0, a1 = T("ancho arriba") - 0.2, T("y aquí viene") + 0.2
    p = win(t, a0, a1)
    if p:
        (x0, y0), (x1, _) = A("cupL"), A("cupR"); C.arrow_dim(ctx, x0, x1, y0 - 40, Y, p)
    p = win(t, T("estrecho") - 0.2, T("y aquí viene") + 0.2)
    if p:
        (x0, y0), (x1, _) = A("botL"), A("botR"); C.arrow_dim(ctx, x0, x1, y0 + 30, B, p)
    # nivel del depósito (de noche se llena, de día baja)
    a0, a1 = T("el agua del"), T("pero si el agua")
    if a0 <= t < a1:
        C.badge(ctx, f"{int(round(100 * nivel(t)))} %", W / 2, BY, win(t, a0, a1), B, size=90)
        if T("la bomba lo va") - 0.3 <= t < T("y cuando todos") - 0.2:
            C.badge(ctx, "03:00", W / 2, BY + 145, win(t, T("la bomba lo va") - 0.3, T("y cuando todos") - 0.2), (1, 1, 1), size=74)
        if T("y cuando todos") - 0.2 <= t:
            C.badge(ctx, "08:00", W / 2, BY + 145, win(t, T("y cuando todos") - 0.2, a1), Y, size=74)
    a0, a1 = T("pero si el agua"), T("así que cada")
    if a0 <= t < a1:
        d = int(min(7, 1 + (t - a0) * 2.6)); C.badge(ctx, f"{d} DÍAS", W / 2, BY, win(t, a0, a1), (0.6, 0.85, 0.4), size=88)
    a0, a1 = T("así que cada"), T("por eso", 1)
    if a0 <= t < a1:
        d = 1 + int((t - a0) / 2.4); C.badge(ctx, f"DÍA {d}", W / 2, BY, win(t, a0, a1), G, size=88)
        C.badge(ctx, f"{int(round(100 * nivel(t)))} %", W / 2, BY + 145, win(t, a0, a1), B, size=74)
    a0, a1 = T("por eso", 1), DUR - 0.5
    if a0 <= t < a1:
        C.badge(ctx, "✗ LUZ", W / 2, BY, win(t, a0, a1), R, size=86)
        if t > T("durante unas") - 0.2:
            hh = keyed(t, [(T("durante unas") - 0.2, 0), (T("sigue saliendo", fin=True), 3)])
            C.badge(ctx, f"+{max(1, int(hh))} h", W / 2, BY + 145, win(t, T("durante unas") - 0.2, a1), Y, size=74)

def sfx_events(C):
    E = [(0.0, C.s_clank(), 0.4), (0.1, C.s_buzz(3.0), 0.25), (T("y el agua sale"), C.s_pop(), 0.35), (T("vamos a construir"), C.s_whoosh(), 0.45),
         (T("con una bomba"), C.s_buzz(2.5), 0.3), (T("pero si la bomba"), C.s_fail(), 0.4), (T("y por la mañana"), C.s_pop(), 0.4),
         (T("así que construyes"), C.s_thud(), 0.5), (T("el agua no sube"), C.s_fail(), 0.35), (T("así que lo subes"), C.s_whoosh(1.2), 0.45),
         (T("de altura"), C.s_pop(), 0.4), (T("treinta"), C.s_pop(), 0.45), (T("tres bares"), C.s_win(), 0.4), (T("pero tanta"), C.s_thud(), 0.5),
         (T("de hormigón"), C.s_clank(), 0.45), (T("y le das forma"), C.s_whoosh(), 0.4), (T("la bomba lo va"), C.s_buzz(2.0), 0.25),
         (T("el depósito baja"), C.s_whoosh(), 0.35), (T("se estropea"), C.s_fail(), 0.35), (T("y el agua siempre"), C.s_win(), 0.35),
         (T("por eso", 1), C.s_thud(), 0.45), (T("sigue saliendo"), C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
