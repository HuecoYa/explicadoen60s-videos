# Capa 2D de «¿Y si construyes una presa?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("presa")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"presa", "río", "túnel", "seco", "barro", "piedras", "roca", "muro", "hormigón", "capa", "empuja", "diez", "atmósfera",
            "cien", "toneladas", "triángulo", "gordísimo", "calienta", "agrieta", "fría", "embalse", "grietas", "arriba", "cemento",
            "cortina", "drenaje", "presión", "llueve", "aliviaderos", "compuertas", "tuberías", "turbinas", "generadores", "luz"}

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    label(C, ctx, t, T("por un túnel"), T("pero el fondo"), "TÚNEL", A, "tunel", dx=0, dy=-140, size=60)
    label(C, ctx, t, T("es barro"), T("así que excavas"), "BARRO", A, "barro", dx=0, dy=-150, size=62)
    label(C, ctx, t, T("roca dura") - 0.3, T("ahí apoyas"), "ROCA", A, "roca", dx=0, dy=120, size=62)
    a0, a1 = T("subes hormigón"), T("pero el agua empuja")
    if a0 <= t < a1:
        n = 1 + int(min(11, 12 * (t - T("ahí apoyas")) / max(0.5, T("capa a capa", fin=True) + 0.5 - T("ahí apoyas"))))
        C.badge(ctx, f"CAPA {max(1, n)}", W / 2, H * 0.265, win(t, a0, a1), Y, size=86)
    a0, a1 = T("cada diez"), T("así que haces")
    if a0 <= t < a1:
        u = min(1, max(0, (t - a0) / (T("a cien") + 0.6 - a0)))
        prof = 10 * max(1, int(1 + 9 * u)); atm = prof // 10
        C.badge(ctx, f"{prof} m · +{atm} atm", W / 2, H * 0.265, win(t, a0, a1), B, size=80)
        if t > T("aguanta"):
            q = win(t, T("aguanta"), a1); C.badge(ctx, "100 t / m²", W / 2, H * 0.265 + 150, q, R, size=90)
    label(C, ctx, t, T("estrecho arriba"), T("pero el hormigón"), "ANCHO ABAJO", A, "presa", dx=60, dy=200, size=56)
    badge(C, ctx, t, T("se calienta"), T("y al enfriarse"), "CALOR AL FRAGUAR", (1.0, 0.6, 0.3), size=74)
    badge(C, ctx, t, T("se agrieta"), T("así que lo enfrías"), "✗ GRIETAS", R, size=88)
    label(C, ctx, t, T("con tubos"), T("ahora cierras"), "TUBOS FRÍOS", A, "frio", dx=0, dy=160, size=58)
    a0, a1 = T("ahora cierras"), T("pero el agua se cuela")
    if a0 + 0.5 <= t < a1:
        lv = min(86, max(0, 86 * (t - a0) / max(0.5, T("se llena", fin=True) + 0.5 - a0)))
        C.badge(ctx, f"NIVEL {int(lv)} m", W / 2, H * 0.265, win(t, a0 + 0.5, a1), B, size=88)
    badge(C, ctx, t, T("y empuja la presa"), T("así que inyectas"), "✗ SUBPRESIÓN", R, size=86)
    label(C, ctx, t, T("inyectas cemento") + 0.3, T("y abres pozos"), "INYECCIONES", A, "cortina", dx=180, dy=0, size=54)
    label(C, ctx, t, T("de drenaje"), T("pero si llueve"), "DRENES", A, "dren", dx=170, dy=60, size=58)
    badge(C, ctx, t, T("que alivian"), T("pero si llueve"), "✓ MENOS EMPUJE", G, size=78)
    badge(C, ctx, t, T("pasar por encima"), T("así que pones"), "✗ SE DESBORDA", R, size=84)
    label(C, ctx, t, T("compuertas"), T("y por último"), "ALIVIADERO", A, "compuerta", dx=230, dy=140, size=58)
    label(C, ctx, t, T("hasta las turbinas"), T("llega con"), "TURBINA", A, "turbina", dx=-150, dy=150, size=60)
    label(C, ctx, t, T("mueve los"), T("y la luz"), "GENERADOR", A, "gen", dx=230, dy=-40, size=58)
    label(C, ctx, t, T("encendida"), DUR + 1, "TU CASA", A, "casa", dx=-60, dy=-140, size=60)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(1.5), 0.5), (T("desvías"), C.s_whoosh(), 0.45), (T("es barro"), C.s_thud(), 0.5), (T("así que excavas"), C.s_thud(), 0.5),
         (T("ahí apoyas"), C.s_clank(), 0.5), (T("cada diez"), C.s_pop(), 0.4), (T("a cien"), C.s_pop(), 0.5), (T("aguanta"), C.s_fail(), 0.4),
         (T("así que haces"), C.s_whoosh(), 0.45), (T("se agrieta"), C.s_fail(), 0.5), (T("con tubos"), C.s_pop(), 0.4),
         (T("ahora cierras"), C.s_clank(), 0.5), (T("y empuja la presa"), C.s_fail(), 0.45), (T("inyectas cemento"), C.s_buzz(1.5), 0.35),
         (T("de drenaje"), C.s_pop(), 0.4), (T("pero si llueve"), C.s_whoosh(1.5), 0.45), (T("compuertas"), C.s_clank(), 0.55),
         (T("hasta las turbinas"), C.s_buzz(2.5), 0.35), (T("mueve los"), C.s_win(), 0.4), (T("encendida"), C.s_pop(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
