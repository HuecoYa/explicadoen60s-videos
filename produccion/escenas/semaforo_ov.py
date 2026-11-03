# Elementos gráficos puntuales: "El semáforo que te ve"
from _ovbase import *
SUB_Y = 0.74
KEYWORDS = {"semáforos", "semáforo", "verde", "casualidad", "detectando", "asfalto", "rectángulo", "alquitrán", "cable", "espira", "corriente",
            "magnético", "coche", "chapa", "motor", "campo", "caja", "atrás", "motos", "bicis", "cámaras", "barata", "debajo"}
def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    label(C, ctx, t, 8.6, 11.4, "RECTÁNGULO", A, "rect", dy=-260, size=62)
    label(C, ctx, t, 15.1, 21.0, "ESPIRA", A, "loop", dy=-330, size=84)
    label(C, ctx, t, 18.5, 21.4, "CAMPO MAGNÉTICO", A, "field", dy=-220, size=56)
    badge(C, ctx, t, 23.6, 26.5, "CAMPO ALTERADO", (1.0, 0.6, 0.2), 66)
    label(C, ctx, t, 27.0, 31.3, "CAJA", A, "box", dy=-260, size=80)
    if 34.4 <= t < 37.1:
        n = 1 + (1 if t >= 35.6 else 0) + (1 if t >= 36.4 else 0); C.badge(ctx, f"COCHES: {n}", W / 2, H * 0.165, win(t, 34.4, 37.1), G, size=74)
    badge(C, ctx, t, 39.6, 42.0, "NO TE VE", R, 80); badge(C, ctx, t, 45.7, 48.0, "POCO METAL", R, 76)
    label(C, ctx, t, 48.6, 50.6, "CÁMARA", A, "camicon", dy=-230)
    badge(C, ctx, t, 51.6, 55.5, "DÉCADAS FUNCIONANDO", G, 62)
def sfx_events(C):
    E = []
    for t in (0.2, 5.9, 11.7, 21.8, 26.7, 31.6, 37.3, 42.3, 48.2, 55.8): E.append((t, C.s_whoosh(), 0.4))
    E.append((2.1, C.s_bleep(1568), 2.5)); E.append((31.6, C.s_bleep(1568), 2.5)); E.append((16.7, C.s_buzz(4.7), 0.15)); E.append((23.6, C.s_buzz(3.0), 0.3))
    for t in (8.6, 15.1, 27.0, 48.6): E.append((t, C.s_pop(), 0.5))
    for t in (35.0, 35.8, 36.6): E.append((t, C.s_whoosh(0.4), 0.6))
    E.append((40.0, C.s_fail(), 0.5)); E.append((46.0, C.s_fail(), 0.5))
    return E
