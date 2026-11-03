# Capa 2D de «Así funciona la cerradura»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("cerradura")
SUB_Y = 0.72
KEYWORDS = {"llave", "dientes", "altura", "cilindro", "carcasa", "pernos", "muelle", "cerrojo", "línea", "corte", "gira", "leva",
            "pestillo", "combinaciones", "egipcios", "madera", "yale", "muelles"}

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    label(C, ctx, t, T("cilindro"), T("carcasa"), "CILINDRO", A, "plug", dy=200, size=60)
    label(C, ctx, t, T("carcasa"), T("atravesando") + 0.3, "CARCASA", A, "casa", dy=-170, size=60)
    label(C, ctx, t, T("dos pernos"), T("muelle") + 1.2, "PERNOS", A, "pernos", dy=-330, size=60)
    label(C, ctx, t, T("muelle"), T("sin llave"), "MUELLE", A, "muelle", dy=-180, size=56)
    badge(C, ctx, t, T("hacen de cerrojo"), T("ahora metes"), "BLOQUEADO", R, size=80)
    label(C, ctx, t, T("línea de corte") - 0.1, T("ya nada") + 0.9, "LÍNEA DE CORTE", A, "shear", dy=-260, size=56)
    badge(C, ctx, t, T("cilindro gira"), T("cilindro gira") + 1.8, "✓ GIRA", G, size=90)
    label(C, ctx, t, T("pestillo"), T("si un solo") - 0.3, "PESTILLO", A, "pest", dy=-220, size=60)
    badge(C, ctx, t, T("si un solo") + 1.6, T("con seis") - 0.2, "✗ NO GIRA", R, size=90)
    badge(C, ctx, t, T("combinaciones") - 0.2, T("sorprendente") - 0.1, "6 PERNOS", Y, size=80)
    badge(C, ctx, t, T("egipcios"), T("linus") - 0.15, "≈ 4000 AÑOS", Y, size=84)
    badge(C, ctx, t, T("linus"), T("sígueme") - 0.1, "LINUS YALE · SIGLO XIX", Y, size=60)

def sfx_events(C):
    E = [(0.15, C.s_whoosh(), 0.4), (T("mira"), C.s_whoosh(1.4), 0.6)]
    for w in ("cilindro", "carcasa", "dos pernos", "muelle", "línea de corte", "pestillo"): E.append((T(w), C.s_pop(), 0.45))
    E.append((T("hacen de cerrojo"), C.s_thud(), 0.7))
    k = T("metes la llave")
    for i in range(5): E.append((k + 0.5 + i * 0.38, C.s_clank(), 0.25))
    E.append((T("cilindro gira"), C.s_win(), 0.55))
    E.append((T("si un solo") + 1.6, C.s_fail(), 0.6))
    E.append((T("egipcios"), C.s_whoosh(), 0.45)); E.append((T("sígueme"), C.s_whoosh(), 0.4))
    return E
