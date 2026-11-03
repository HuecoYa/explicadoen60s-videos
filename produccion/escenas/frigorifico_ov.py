# Capa 2D de «Así funciona la nevera»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("frigorifico")
SUB_Y = 0.72
KEYWORDS = {"frío", "calor", "refrigerante", "evapora", "sudor", "gas", "compresor", "aprieta", "caliente", "rejilla",
            "líquido", "tibia", "estrechamiento", "presión", "termostato", "puerta", "calientas"}

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    badge(C, ctx, t, T("hierve a una"), T("dentro de la nevera"), "≈ -26 °C", B, size=100)
    label(C, ctx, t, T("se evapora"), T("ahora es un gas"), "EVAPORADOR", A, "evap", dx=-60, dy=-200, size=58)
    label(C, ctx, t, T("compresor"), T("ese gas caliente"), "COMPRESOR", A, "comp", dx=-80, dy=-230, size=58)
    label(C, ctx, t, T("rejilla negra"), T("después"), "CONDENSADOR", A, "cond", dx=-40, dy=-260, size=56)
    label(C, ctx, t, T("tubo finísimo"), T("vuelve a entrar"), "CAPILAR", A, "cap", dx=-80, dy=-160, size=58)
    label(C, ctx, t, T("termostato"), T("y un dato") - 0.1, "TERMOSTATO", A, "termo", dx=-60, dy=-170, size=56)
    badge(C, ctx, t, T("la calientas"), T("sígueme") - 0.1, "✗ COCINA + CALIENTE", R, size=66)

def sfx_events(C):
    E = [(0.15, C.s_whoosh(), 0.4), (T("mira dentro"), C.s_whoosh(1.4), 0.6)]
    for w in ("refrigerante", "se evapora", "compresor", "rejilla negra", "tubo finísimo", "termostato"): E.append((T(w), C.s_pop(), 0.45))
    E.append((T("lo aprieta"), C.s_thud(), 0.6)); E.append((T("la presión cae"), C.s_whoosh(), 0.5))
    E.append((T("si dejas la puerta") + 0.3, C.s_clank(), 0.5)); E.append((T("la calientas"), C.s_fail(), 0.6))
    E.append((T("sígueme"), C.s_whoosh(), 0.4))
    return E
