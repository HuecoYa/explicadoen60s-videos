# Capa 2D de «Si tuvieras que inventar el bolígrafo»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("boligrafo")
SUB_Y = 0.72
KEYWORDS = {"bolígrafo", "tintero", "depósito", "tinta", "gotea", "espesa", "pasta", "bolita", "arena", "gira", "desodorante",
            "rodar", "tapa", "casquillo", "vacío", "aire", "agujerito", "capuchón", "respirar", "bíró", "húngaro"}

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    label(C, ctx, t, T("depósito"), T("pero la tinta"), "DEPÓSITO", A, "tinta", dx=150, dy=-80, size=60)
    badge(C, ctx, t, T("gotea"), T("así que usas"), "✗ GOTEA", R, size=88)
    badge(C, ctx, t, T("no sale por"), T("así que en la punta"), "✗ NO SALE", R, size=88)
    badge(C, ctx, t, T("grano de arena"), T("la bola gira"), "≈ 0,7 mm", Y, size=100)
    badge(C, ctx, t, T("demasiado justa"), T("y si está"), "✗ NO GIRA", R, size=84)
    badge(C, ctx, t, T("se sale"), T("así que la sujetas"), "✗ SE SALE", R, size=84)
    label(C, ctx, t, T("casquillo"), T("último problema") - 0.2, "CASQUILLO", A, "casq", dx=160, dy=-120, size=58)
    badge(C, ctx, t, T("se forma un vacío"), T("así que haces"), "✗ VACÍO", R, size=88)
    label(C, ctx, t, T("agujerito"), T("y el agujero") - 0.1, "AIRE", A, "aire", dx=-140, dy=-100, size=66)
    badge(C, ctx, t, T("patentó"), T("sígueme") - 0.1, "LÁSZLÓ BÍRÓ · 1938", Y, size=66)

def sfx_events(C):
    E = [(0.1, C.s_whoosh(), 0.4), (T("depósito"), C.s_pop(), 0.5)]
    for w in ("gotea", "no sale por", "demasiado justa", "se sale", "se forma un vacío"): E.append((T(w) + 0.2, C.s_fail(), 0.45))
    for w in ("bolita", "casquillo", "agujerito", "capuchón"): E.append((T(w), C.s_pop(), 0.45))
    E.append((T("la bola gira"), C.s_whoosh(), 0.4)); E.append((T("patentó"), C.s_win(), 0.4)); E.append((T("sígueme"), C.s_whoosh(), 0.4))
    return E
