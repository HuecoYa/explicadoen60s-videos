# Capa 2D de «Si tuvieras que inventar la lata»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("lata")
SUB_Y = 0.72
KEYWORDS = {"lata", "gas", "aluminio", "papel", "fondo", "cúpula", "arco", "barniz", "ácido", "tapa", "cuello", "anilla",
            "lengüeta", "palanca", "persona", "aplastas", "fuerte"}

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    badge(C, ctx, t, T("rueda"), T("y quieres"), "≈ 2,5 BAR", Y, size=90)
    badge(C, ctx, t, T("tan finas"), T("pero el gas"), "0,1 mm", Y, size=96)
    badge(C, ctx, t, T("se volcaría"), T("así que haces"), "✗ SE VUELCA", R, size=80)
    label(C, ctx, t, T("cúpula"), T("barniz") - 0.2, "CÚPULA", A, "fondo", dy=-260, size=66)
    label(C, ctx, t, T("barniz"), T("la tapa necesita") - 0.2, "BARNIZ", A, "pared", dx=40, dy=-200, size=62)
    label(C, ctx, t, T("estrechas"), T("problema") - 0.1, "CUELLO", A, "tapa", dy=-200, size=66)
    badge(C, ctx, t, T("acababan tiradas"), T("así que inventas"), "✗ BASURA", R, size=80)
    label(C, ctx, t, T("hace de palanca"), T("y aquí lo"), "PALANCA", A, "tab", dy=-220, size=62)
    badge(C, ctx, t, T("cerrada aguanta"), T("pero vacía"), "✓ AGUANTA", G, size=90)
    badge(C, ctx, t, T("el propio gas") - 0.2, T("sígueme"), "EL GAS LA SUJETA", Y, size=66)

def sfx_events(C):
    E = [(0.1, C.s_pop(), 0.5)]
    for w in ("aluminio", "tan finas", "cúpula", "barniz", "estrechas", "lengüeta"): E.append((T(w), C.s_whoosh(), 0.4))
    E.append((T("se volcaría"), C.s_fail(), 0.5)); E.append((T("aguanta la presión"), C.s_win(), 0.45))
    E.append((T("anilla") + 0.4, C.s_clank(), 0.4))
    E.append((T("hace de palanca") + 0.3, C.s_pop(), 0.6))
    E.append((T("cerrada aguanta") + 0.8, C.s_thud(), 0.8)); E.append((T("pero vacía") + 1.2, C.s_clank(), 0.7))
    E.append((T("sígueme"), C.s_whoosh(), 0.4))
    return E
