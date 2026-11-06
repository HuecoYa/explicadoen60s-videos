# Capa 2D de «¿Cómo sabe el ordenador qué tecla pulsas?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("teclado")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"teclado", "cien", "teclas", "cables", "lámina", "capas", "pistas", "agujeros", "circuito", "cuadrícula", "filas",
            "columnas", "cruce", "ocho", "dieciocho", "cuarenta", "veintiséis", "chip", "corriente", "primera", "segunda",
            "tercera", "tres", "cinco", "mil", "cuarta", "diodo", "válvula", "sentido"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    BY = H * 0.265
    # teclas frente a cables
    a0, a1 = 0.6, T("cómo sabe")
    if a0 <= t < a1:
        n = keyed(t, [(a0, 0), (2.6, 105)])
        C.badge(ctx, f"{int(n)} TECLAS", W / 2, BY, win(t, a0, a1), Y, size=82)
        C.badge(ctx, "✗ 105 CABLES", W / 2, BY + 140, win(t, T("y no tiene") + 0.3, a1), R, size=70)
    # capas
    a1 = T("al pulsar")
    label(C, ctx, t, T("dos capas") - 0.2, a1, "PISTAS", A, "top", dx=-30, dy=-110, size=56)
    label(C, ctx, t, T("una capa con"), a1, "AGUJEROS", A, "spc", dx=40, dy=10, size=56)
    label(C, ctx, t, T("dos capas") + 0.5, a1, "PISTAS", A, "bot", dx=60, dy=120, size=56)
    a0, a1 = T("y cierra"), T("pero no hay") + 0.4
    if a0 <= t < a1:
        C.badge(ctx, "✓ CIRCUITO", W / 2, BY, win(t, a0, a1), G, size=80)
    a0, a1 = T("pero no hay"), T("las pistas forman")
    if a0 + 0.3 <= t < a1:
        C.badge(ctx, "✗ 1 CABLE POR TECLA", W / 2, BY, win(t, a0 + 0.3, a1), R, size=64)
    # filas y columnas
    a1 = T("con ocho")
    label(C, ctx, t, T("filas y") - 0.05, a1, "FILAS", A, "rowh", dx=-40, dy=90, size=60)
    label(C, ctx, t, T("columnas") - 0.05, a1, "COLUMNAS", A, "colh", dx=0, dy=110, size=60)
    a0, a1 = T("con ocho"), T("ahora un")
    if a0 <= t < a1:
        f = 8 if t > T("con ocho") + 0.3 else 0
        cc = 18 if t > T("dieciocho") else 0
        cr = int(keyed(t, [(T("ciento cuarenta") - 0.2, 0), (T("ciento cuarenta") + 1.3, 144)]))
        s = f"{f} × {cc}" if t < T("ciento cuarenta") - 0.2 else f"{cr} CRUCES"
        C.badge(ctx, s, W / 2, BY, win(t, a0, a1), Y, size=86)
        if t > T("con solo"):
            n = int(keyed(t, [(T("con solo"), 0), (T("con solo") + 1.0, 26)]))
            C.badge(ctx, f"{n} CABLES", W / 2, BY + 145, win(t, T("con solo"), a1), G, size=78)
    # chip y barrido
    label(C, ctx, t, T("un pequeño chip") + 0.3, T("mete corriente") + 1.0, "CHIP", A, "chip", dx=60, dy=-130, size=64)
    for k, (a0, a1) in enumerate(((T("mete corriente"), T("luego en la segunda")), (T("luego en la segunda"), T("luego en la tercera")),
                                  (T("luego en la tercera"), T("si la corriente")))):
        if a0 <= t < a1:
            C.badge(ctx, f"COLUMNA {k + 1}", W / 2, BY, win(t, a0, a1, 0.08), Y, size=78)
            C.badge(ctx, "FILAS: —", W / 2, BY + 135, win(t, T("y mira") if k == 0 else a0 + 0.4, a1, 0.08), (0.8, 0.8, 0.85), size=64)
    a0, a1 = T("si la corriente"), T("y aquí viene") + 0.2
    if a0 <= t < a1:
        cn = 4 if t < a0 + 0.7 else 5
        C.badge(ctx, f"COLUMNA {cn}", W / 2, BY, win(t, a0, a1), Y, size=78)
        if t > a0 + 0.9: C.badge(ctx, "FILA 3", W / 2, BY + 135, win(t, a0 + 0.9, a1), G, size=72)
    label(C, ctx, t, T("has pulsado", 2), T("y aquí viene") + 0.2, "PULSADA", A, "pr", dx=0, dy=160, size=64)
    # mil veces por segundo
    a0, a1 = T("y en un teclado"), T("pero si pulsas")
    if a0 <= t < a1:
        v = keyed(t, [(T("se lo cuenta"), 0), (T("mil veces") + 1.2, 1000)])
        C.badge(ctx, f"{miles(v)} / s", W / 2, BY, win(t, a0, a1), Y, size=92)
    # tecla fantasma
    a0, a1 = T("pero si pulsas") + 0.6, T("por eso los")
    if a0 <= t < a1:
        C.badge(ctx, "3 TECLAS", W / 2, BY, win(t, a0, a1), Y, size=78)
    label(C, ctx, t, T("y aparece") + 0.1, T("por eso los") + 0.6, "FANTASMA", A, "ghost", dx=0, dy=110, size=64)
    label(C, ctx, t, T("por eso los") + 1.6, T("sígueme") - 0.3, "DIODO", A, "diodo", dx=40, dy=-150, size=66)
    a0, a1 = T("una válvula") + 0.7, T("sígueme")
    if a0 <= t < a1:
        C.badge(ctx, "✗ VUELTA", W / 2, BY, win(t, a0, a1), R, size=78)

def sfx_events(C):
    E = []
    for k in range(14): E.append((0.05 + 0.3 * k, C.s_pop() if k % 2 else C.s_thud(), 0.18))
    E += [(T("y no tiene") + 0.3, C.s_fail(), 0.35), (T("vamos a abrirlo"), C.s_whoosh(), 0.45), (T("dos capas"), C.s_pop(), 0.35),
          (T("una capa con"), C.s_pop(), 0.35), (T("toca la de"), C.s_thud(), 0.45), (T("y cierra"), C.s_win(), 0.35),
          (T("pero no hay") + 0.3, C.s_fail(), 0.3), (T("las pistas forman"), C.s_whoosh(), 0.4), (T("ciento cuarenta"), C.s_coin(), 0.4),
          (T("con solo"), C.s_coin(), 0.4), (T("un pequeño chip") + 0.3, C.s_pop(), 0.4), (T("mete corriente"), C.s_buzz(1.2), 0.25),
          (T("luego en la segunda"), C.s_buzz(1.0), 0.25), (T("luego en la tercera"), C.s_buzz(1.0), 0.25),
          (T("si la corriente") + 0.9, C.s_win(), 0.4), (T("el chip repasa"), C.s_buzz(3.0), 0.2), (T("mil veces"), C.s_coin(), 0.4),
          (T("pero si pulsas") + 0.8, C.s_thud(), 0.4), (T("y aparece"), C.s_fail(), 0.45), (T("por eso los") + 1.4, C.s_clank(), 0.4),
          (T("una válvula") + 0.7, C.s_fail(), 0.3), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
