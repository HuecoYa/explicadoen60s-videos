# Elementos gráficos puntuales: "La máquina expendedora"
from _ovbase import *
SUB_Y = 0.74
KEYWORDS = {"moneda", "falsa", "segundo", "examen", "tamaño", "diámetro", "grosor", "peso", "rampa", "velocidad", "metal", "bobinas",
            "magnético", "aleación", "cobre", "níquel", "latón", "euro", "metales", "anillo", "centro", "huella", "trampilla", "depósito", "devolución", "arandela", "chocolate"}
def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    badge(C, ctx, t, 3.2, 4.8, "0,5 s", Y, 90)
    badge(C, ctx, t, 8.8, 16.2, "PRUEBA 1 · TAMAÑO", Y, 64); label(C, ctx, t, 11.0, 16.0, "TAMAÑO", A, "gauge", dy=-230)
    badge(C, ctx, t, 16.3, 23.6, "PRUEBA 2 · PESO", Y, 64); label(C, ctx, t, 18.6, 23.5, "RAMPA", A, "ramp", dy=-230)
    badge(C, ctx, t, 23.8, 36.6, "PRUEBA 3 · METAL", Y, 64); label(C, ctx, t, 27.3, 31.0, "BOBINAS", A, "coil", dy=-300)
    for a, b, txt, col in ((34.1, 34.85, "COBRE", (0.95, 0.55, 0.3)), (34.85, 35.7, "NÍQUEL", (0.85, 0.87, 0.9)), (35.7, 36.6, "LATÓN", (0.98, 0.8, 0.35))):
        label(C, ctx, t, a, b, txt, A, "coil", dy=300, size=74)
    label(C, ctx, t, 41.9, 43.6, "ANILLO", A, "ring", dx=-140, dy=-200); label(C, ctx, t, 42.4, 43.6, "CENTRO", A, "center", dx=160, dy=200)
    badge(C, ctx, t, 47.8, 52.0, "✓ COINCIDE".replace("✓ ", ""), G, 76); label(C, ctx, t, 49.2, 52.0, "DEPÓSITO", A, "cash", dy=-230)
    badge(C, ctx, t, 52.3, 58.9, "NO COINCIDE", R, 76); label(C, ctx, t, 55.5, 59.0, "DEVOLUCIÓN", A, "tray", dy=-230, size=62)
def sfx_events(C):
    E = []
    for t in (0.2, 5.1, 8.8, 16.3, 23.8, 36.8, 43.9, 47.8, 52.3, 59.3, 64.9): E.append((t, C.s_whoosh(), 0.4))
    for t in (2.1, 3.2, 6.2, 52.6, 59.6, 61.2): E.append((t, C.s_coin(), 0.5))
    E.append((27.3, C.s_buzz(20.0), 0.12)); E.append((51.6, C.s_coin(), 0.7)); E.append((51.7, C.s_bleep(1568), 2.5))
    for t in (11.0, 18.6, 27.3, 41.9, 49.2, 55.5): E.append((t, C.s_pop(), 0.5))
    E.append((57.5, C.s_fail(), 0.6))
    return E
