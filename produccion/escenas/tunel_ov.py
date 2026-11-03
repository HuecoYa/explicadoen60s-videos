# Capa 2D de «¿Y si construyes un túnel bajo un río?»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("tunel")
SUB_Y = 0.72
KEYWORDS = {"túnel", "río", "empapada", "derrumba", "agua", "escudo", "acero", "tuneladora", "cuchillas", "presión", "paredes",
            "anillos", "hormigón", "puzle", "dovelas", "gatos", "goma", "mortero", "bombas", "broma", "barcos", "brunel", "támesis"}

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    badge(C, ctx, t, T("se derrumba"), T("así que usas"), "✗ SE INUNDA", R, size=86)
    label(C, ctx, t, T("tuneladora"), T("pero el río"), "TUNELADORA", A, "tbm", dx=-40, dy=-200, size=58)
    label(C, ctx, t, T("cámara llena"), T("y avanza"), "TIERRA A PRESIÓN", A, "camara", dx=-120, dy=-220, size=52)
    badge(C, ctx, t, T("y avanza"), T("pero al avanzar"), "✓ EQUILIBRIO", G, size=80)
    label(C, ctx, t, T("dovelas"), T("unos gatos"), "DOVELAS", A, "anillo", dx=-40, dy=-200, size=60)
    label(C, ctx, t, T("gatos hidráulicos"), T("pero entre"), "GATOS", A, "gatos", dx=-60, dy=-200, size=62)
    badge(C, ctx, t, T("se puede colar"), T("así que llevan"), "✗ FUGAS", R, size=86)
    label(C, ctx, t, T("bombas"), T("sabes de dónde") - 0.1, "BOMBA", A, "bomba", dx=-60, dy=-180, size=60)
    badge(C, ctx, t, T("marc brunel"), T("sígueme") - 0.1, "TÁMESIS · 1843", Y, size=78)

def sfx_events(C):
    E = [(0.1, C.s_whoosh(), 0.4), (T("empiezas cavando"), C.s_thud(), 0.5), (T("se derrumba"), C.s_fail(), 0.6)]
    for w in ("usas un escudo", "tuneladora", "cámara llena", "dovelas", "gatos hidráulicos", "juntas de goma", "mortero", "bombas"):
        E.append((T(w), C.s_pop(), 0.45))
    E.append((T("y avanza"), C.s_whoosh(), 0.4)); E.append((T("se puede colar"), C.s_fail(), 0.45))
    E.append((T("marc brunel"), C.s_win(), 0.4)); E.append((T("sígueme"), C.s_whoosh(), 0.4))
    return E
