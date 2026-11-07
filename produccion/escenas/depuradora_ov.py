# Capa 2D de «¿Y si construyes una depuradora?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("depuradora")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"cadena", "segundos", "depuradora", "ciento", "veintiocho", "litros", "cien", "mil", "trece", "millones", "alcantarilla",
            "rejas", "arena", "bombas", "lento", "fondo", "grasa", "aire", "pesado", "disuelto", "bacterias", "respirar", "grumos",
            "transparente", "río", "lodo", "cerrados", "gas", "electricidad"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def miles(v): return f"{int(round(v)):,}".replace(",", ".")
def dec(v, n=1): return (f"%.{n}f" % v).replace(".", ",")

def eaten(t):
    a, b = T("se comen"), T("pero necesitan") + 0.3
    c, d = T("así que unas máquinas") + 0.6, T("esas bacterias")
    return 0.45 * sg(t, a, b) + 0.45 * sg(t, c, d)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # segundos que tarda en irse el agua
    a0, a1 = T("y en unos"), T("y si tuvieras")
    if a0 <= t < a1:
        C.badge(ctx, dec(min(3.0, 3.0 * sg(t, a0, T("desaparecido", fin=True)))) + " s", W / 2, BY, win(t, a0, a1), B, size=88)
    # 128 L por persona
    a0, a1 = T("cada persona"), T("en una ciudad")
    if a0 <= t < a1:
        v = 128 * sg(t, a0 + 0.6, T("al día", fin=True))
        C.badge(ctx, f"{int(round(v))} L", W / 2, BY, win(t, a0, a1), B, size=96)
        C.badge(ctx, "1 PERSONA", W / 2, BY + 150, win(t, a0 + 0.3, a1), (1, 1, 1), size=58)
    # ciudad: personas y litros
    a0, a1 = T("en una ciudad"), T("todos acaban") + 0.4
    if a0 <= t < a1:
        p = 100000 * sg(t, a0 + 0.3, T("de cien mil", fin=True) + 0.2)
        C.badge(ctx, miles(p) + " PERSONAS", W / 2, BY, win(t, a0, a1), (1, 1, 1), size=64)
        b0 = T("son casi")
        if t > b0 - 0.1:
            v = 12800000 * sg(t, b0, T("diarios", fin=True))
            C.badge(ctx, miles(v) + " L", W / 2, BY + 150, win(t, b0 - 0.1, a1), B, size=78)
    label(C, ctx, t, T("son casi") + 1.0, T("todos acaban") + 0.2, "23 m", A, "cbig", dx=0, dy=0, size=64)
    # reja, arena, bomba
    label(C, ctx, t, T("primero llegan") + 0.3, T("pero la arena"), "REJA", A, "reja", dx=-60, dy=-120, size=60)
    a0, a1 = T("pero la arena"), T("así que el agua cruza")
    label(C, ctx, t, a0 + 0.2, a1, "ARENA", A, "sand", dx=-80, dy=-140, size=56)
    label(C, ctx, t, T("y destrozaría"), a1, "BOMBA", A, "pump", dx=40, dy=-120, size=56)
    if T("y destrozaría") + 0.4 <= t < a1:
        C.badge(ctx, "✗ BOMBA", W / 2, BY, win(t, T("y destrozaría") + 0.4, a1), R, size=80)
    # canal lento: velocidad
    a0, a1 = T("así que el agua cruza"), T("pero aún flota")
    if a0 <= t < a1:
        v = 1.0 - 0.7 * sg(t, a0 + 0.3, T("un canal lento", fin=True) + 0.3)
        C.badge(ctx, dec(v) + " m/s", W / 2, BY, win(t, a0, a1), Y, size=90)
    # grasa y aire
    a0, a1 = T("pero aún flota"), T("ahora el agua")
    label(C, ctx, t, a0 + 0.3, a1, "GRASA", A, "grasa", dx=40, dy=-150, size=56)
    label(C, ctx, t, T("así que soplas") + 0.3, T("y la retiras"), "AIRE", A, "aire", dx=-40, dy=140, size=56)
    # decantador: horas y lo disuelto
    a0, a1 = T("lo más pesado"), T("así que contratas")
    if a0 <= t < a1:
        hh = 2 * sg(t, a0, T("poco a poco", fin=True))
        C.badge(ctx, dec(hh) + " h", W / 2, BY, win(t, a0, a1), Y, size=90)
    label(C, ctx, t, T("lo más pesado") + 1.2, T("pero lo peor"), "LODO", A, "prim", dx=0, dy=-110, size=56)
    label(C, ctx, t, T("pero lo peor") + 0.4, T("así que contratas"), "DISUELTO", A, "diss", dx=0, dy=-160, size=56)
    # reactor: suciedad y oxígeno
    a0, a1 = T("bacterias"), T("y aquí viene")
    if a0 <= t < a1:
        s = 100 * (1 - eaten(t))
        C.badge(ctx, f"SUCIEDAD {int(round(s))} %", W / 2, BY, win(t, a0, a1), (0.75, 0.6, 0.35), size=66)
        b0 = T("pero necesitan")
        if t > b0:
            o2 = 2.0 * (1 - sg(t, b0, b0 + 0.8)) + 2.0 * sg(t, T("así que unas máquinas") + 0.4, T("por el fondo", fin=True))
            col = R if o2 < 0.8 else G
            C.badge(ctx, "OXÍGENO " + dec(o2) + " mg/L", W / 2, BY + 150, win(t, b0, a1), col, size=60)
    label(C, ctx, t, T("así que unas máquinas") + 0.6, T("y aquí viene"), "AIRE", A, "difu", dx=0, dy=120, size=56)
    # decantador final
    a0, a1 = T("en otro depósito"), T("esa agua vuelve")
    if a0 <= t < a1:
        s = 10 - 5 * sg(t, T("y arriba queda"), T("transparente", fin=True))
        C.badge(ctx, f"SUCIEDAD {int(round(s))} %", W / 2, BY, win(t, a0, a1), G, size=66)
    label(C, ctx, t, T("esa agua vuelve"), T("y el lodo"), "RÍO", A, "rio", dx=0, dy=-90, size=60)
    # lodo y digestor
    label(C, ctx, t, T("y el lodo"), T("lo metes") + 0.5, "LODO", A, "sec_bot", dx=-60, dy=-120, size=58)
    a0, a1 = T("lo metes"), T("ese gas")
    if a0 <= t < a1:
        tc = 15 + 20 * sg(t, a0 + 0.2, T("sin aire", fin=True) + 0.4)
        C.badge(ctx, f"{int(round(tc))} °C", W / 2, BY, win(t, a0, a1), Y, size=90)
    label(C, ctx, t, T("y sueltan gas"), T("y da electricidad"), "BIOGÁS", A, "egg_top", dx=0, dy=-60, size=58)
    a0, a1 = T("ese gas"), DUR
    label(C, ctx, t, a0 + 0.2, T("y da electricidad"), "MOTOR", A, "motor", dx=0, dy=-110, size=58)
    if T("y da electricidad") <= t < a1:
        k = 1800 * sg(t, T("y da electricidad"), DUR - 0.5)
        C.badge(ctx, f"+{miles(k)} kWh", W / 2, BY, win(t, T("y da electricidad"), a1), Y, size=84)

def sfx_events(C):
    E = [(0.0, C.s_clank(), 0.45), (0.05, C.s_whoosh(1.4), 0.55), (0.9, C.s_whoosh(1.2), 0.4), (T("el agua ha"), C.s_pop(), 0.35),
         (T("vamos a construir"), C.s_whoosh(), 0.45), (T("cada persona") + 0.6, C.s_pop(), 0.4), (T("en una ciudad"), C.s_whoosh(), 0.4),
         (T("son casi"), C.s_buzz(2.0), 0.25), (T("diarios"), C.s_thud(), 0.5), (T("todos acaban"), C.s_whoosh(1.0), 0.45),
         (T("toallitas") - 0.2, C.s_thud(), 0.4), (T("plásticos"), C.s_thud(), 0.35), (T("palos"), C.s_clank(), 0.4),
         (T("y destrozaría"), C.s_fail(), 0.45), (T("así que el agua cruza"), C.s_whoosh(), 0.4), (T("y la arena cae"), C.s_pop(), 0.35),
         (T("así que soplas"), C.s_buzz(1.6), 0.25), (T("y la retiras"), C.s_whoosh(), 0.4), (T("ahora el agua"), C.s_whoosh(), 0.4),
         (T("lo más pesado") + 1.0, C.s_thud(), 0.4), (T("y eso no"), C.s_fail(), 0.35), (T("bacterias"), C.s_pop(), 0.45),
         (T("se comen"), C.s_pop(), 0.3), (T("pero necesitan"), C.s_fail(), 0.4), (T("así que unas máquinas"), C.s_buzz(2.4), 0.3),
         (T("esas bacterias") + 0.5, C.s_pop(), 0.4), (T("los grumos se"), C.s_thud(), 0.45), (T("transparente"), C.s_win(), 0.45),
         (T("esa agua vuelve"), C.s_whoosh(), 0.4), (T("lo metes"), C.s_clank(), 0.45), (T("sueltan gas"), C.s_pop(), 0.35),
         (T("ese gas"), C.s_whoosh(), 0.4), (T("y da electricidad"), C.s_win(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
