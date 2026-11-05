# Capa 2D de «Si tuvieras que inventar el cargador de tu móvil…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("cargador")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"cargador", "enchufe", "voltios", "cincuenta", "batería", "cinco", "diodos", "puertas", "dirección", "condensador",
            "trescientos", "transformador", "bobinas", "cobre", "núcleo", "enorme", "interruptor", "miles", "pequeño", "palma",
            "magnetismo", "tocan", "chip", "nueve", "veinte", "cero", "doscientos", "treinta"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # 230 V que cambian de sentido
    a0, a1 = T("en el enchufe"), T("tu batería")
    if a0 <= t < a1:
        C.badge(ctx, "230 V", W / 2, BY, win(t, a0, a1), R, size=92)
        b0 = T("y cambian")
        if t > b0:
            n = int(50 * min(1, (t - b0) / 2.2))
            C.badge(ctx, f"{n} CAMBIOS / s", W / 2, BY + 140, win(t, b0, a1), Y, size=70)
    a0, a1 = T("tu batería"), T("lo primero")
    if a0 <= t < a1:
        C.badge(ctx, "5 V", W / 2, BY, win(t, a0, a1), G, size=92)
        label(C, ctx, t, a0, a1, "BATERÍA", A, "bat", dx=0, dy=-120, size=60)
    label(C, ctx, t, T("unos diodos") + 0.3, T("un condensador"), "DIODOS", A, "diodo", dx=0, dy=-150, size=62)
    badge(C, ctx, t, T("la corriente ya"), T("un condensador"), "✗ VOLVER ATRÁS", R, size=78)
    label(C, ctx, t, T("un condensador") + 0.3, T("pero ahora") + 0.3, "CONDENSADOR", A, "cap", dx=-40, dy=-170, size=58)
    a0, a1 = T("pero ahora"), T("necesitas")
    if a0 - 0.1 <= t < a1:
        v = keyed(t, [(a0, 230), (a0 + 1.4, 325)])
        C.badge(ctx, f"{int(v)} V", W / 2, BY, win(t, a0 - 0.1, a1), R, size=96)
    label(C, ctx, t, T("dos bobinas") , T("pero con"), "COBRE", A, "prim", dx=-170, dy=-60, size=58)
    label(C, ctx, t, T("un núcleo") - 0.1, T("pero con"), "NÚCLEO", A, "nucleo", dx=150, dy=-120, size=58)
    a0, a1 = T("pero con"), T("así que añades")
    if a0 <= t < a1:
        C.badge(ctx, "50 / s", W / 2, BY, win(t, a0, a1), R, size=92)
    label(C, ctx, t, T("un interruptor") + 0.4, T("cuanto más"), "INTERRUPTOR", A, "sw", dx=40, dy=-150, size=56)
    a0, a1 = T("que corta"), T("por eso los")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 50), (a0 + 2.5, 100000)])
        C.badge(ctx, f"{miles(v)} / s", W / 2, BY, win(t, a0, a1), Y, size=92)
    label(C, ctx, t, T("por eso los") + 0.3, T("y los de ahora"), "ANTES", A, "vieja", dx=-10, dy=0, size=64)
    label(C, ctx, t, T("y los de ahora") + 0.5, T("y aquí viene"), "AHORA", A, "nueva", dx=30, dy=0, size=64)
    label(C, ctx, t, T("no se tocan") - 0.2, T("así los"), "HUECO", A, "hueco", dx=200, dy=40, size=58)
    a0, a1 = T("así los"), T("pero aún")
    if a0 <= t < a1:
        label(C, ctx, t, a0, a1, "230 V", A, "prim", dx=-200, dy=-30, size=66)
        label(C, ctx, t, a0 + 0.5, a1, "5 V", A, "secu", dx=200, dy=40, size=66)
    label(C, ctx, t, T("un chip") + 0.3, T("el móvil le"), "CHIP", A, "chip", dx=170, dy=-40, size=60)
    a0, a1 = T("el móvil le"), T("cuando la batería")
    if a0 <= t < a1:
        v = 5 if t < T("nueve") else (9 if t < T("veinte") else 20)
        C.badge(ctx, f"{v} V", W / 2, BY, win(t, a0, a1), G if v == 5 else (Y if v == 9 else R), size=96)
    a0, a1 = T("cuando la batería"), DUR - 1.0
    if a0 <= t < a1:
        p = keyed(t, [(a0, 80), (T("casi cero", fin=True), 97)])
        amp = keyed(t, [(a0, 3.0), (T("la corriente baja"), 2.4), (T("casi cero", fin=True), 0.1)])
        C.badge(ctx, f"{int(p)} %", W / 2, BY, win(t, a0, a1), G, size=92)
        C.badge(ctx, ("%.1f A" % amp).replace(".", ","), W / 2, BY + 140, win(t, a0 + 0.3, a1), B, size=78)

def sfx_events(C):
    E = [(0.05, C.s_whoosh(), 0.4), (0.5, C.s_clank(), 0.5), (0.55, C.s_buzz(0.4), 0.3),
         (T("cómo lo harías"), C.s_whoosh(), 0.45), (T("en el enchufe"), C.s_buzz(1.5), 0.3), (T("tu batería"), C.s_pop(), 0.4)]
    for k in range(4): E.append((T("unos diodos") + 0.12 * k + 0.45, C.s_thud(), 0.4))
    E += [(T("la corriente ya"), C.s_fail(), 0.35), (T("un condensador") + 0.45, C.s_thud(), 0.45), (T("pero ahora"), C.s_coin(), 0.4),
          (T("necesitas") + 0.9, C.s_clank(), 0.5), (T("tendría"), C.s_whoosh(), 0.45), (T("un interruptor") + 0.45, C.s_thud(), 0.4),
          (T("que corta"), C.s_buzz(2.5), 0.3), (T("más pequeño"), C.s_whoosh(), 0.4), (T("y los de ahora"), C.s_pop(), 0.45),
          (T("la energía"), C.s_buzz(2.0), 0.3), (T("así los"), C.s_win(), 0.4), (T("un chip") + 0.45, C.s_thud(), 0.4),
          (T("cinco", 2), C.s_pop(), 0.4), (T("nueve"), C.s_pop(), 0.4), (T("veinte"), C.s_pop(), 0.45),
          (T("casi cero"), C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
