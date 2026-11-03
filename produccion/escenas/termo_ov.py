# Elementos gráficos puntuales: "Inventa un termo"
SUB_Y = 0.72
KEYWORDS = {"termo", "caliente", "calor", "caminos", "contacto", "aire", "frío", "radiación", "infrarroja", "paredes", "vacío", "plateadas",
            "espejo", "arriba", "tapón", "dewar", "1892", "revés"}
W, H = 1080, 1920
def clampx(x, m=260): return max(m, min(W - m, x))
def clampy(y, lo=330, hi=1150): return max(lo, min(hi, y))
def win(t, a, b, fade=0.15):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / 0.22) * min(1.0, (b - t) / fade)
def label(C, ctx, t, a, b, text, A, key, dx=0, dy=-220, size=68):
    p = win(t, a, b)
    if p:
        x, y = A(key); C.callout(ctx, text, clampx(x + dx), clampy(y + dy), p, size=size)
def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    if 1.8 <= t < 4.4:
        v = int(80 - 30 * C.ease((t - 1.8) / 2.5)); C.badge(ctx, f"{v} °C", W / 2, H * 0.165, win(t, 1.8, 4.4), R, size=84)
    for a, b, txt in ((8.2, 13.7, "1 · CONTACTO"), (14.0, 19.3, "2 · AIRE"), (19.5, 25.8, "3 · RADIACIÓN")):
        p = win(t, a, b)
        if p: C.badge(ctx, txt, W / 2, H * 0.165, p, Y, size=68)
    label(C, ctx, t, 27.3, 31.8, "DOBLE PARED", A, "gap", dy=-260, size=62)
    p = win(t, 37.3, 42.6)
    if p: C.badge(ctx, "VACÍO", W / 2, H * 0.165, p, G, size=90)
    label(C, ctx, t, 44.5, 50.8, "PLATA", A, "wall", dy=-260, size=80)
    label(C, ctx, t, 56.4, 58.9, "TAPÓN", A, "cap", dy=-200, size=80)
    p = win(t, 60.0, 65.2)
    if p: C.badge(ctx, "JAMES DEWAR · 1892", W / 2, H * 0.165, p, Y, size=66)
    p = win(t, 66.0, 69.6)
    if p: C.badge(ctx, "4 °C", W / 2, H * 0.165, p, (0.55, 0.8, 1.0), size=90)
def sfx_events(C):
    E = []
    for t in (0.2, 4.7, 8.2, 14.0, 19.5, 25.9, 32.0, 35.7, 42.9, 51.0, 56.3, 59.0, 65.5, 69.9): E.append((t, C.s_whoosh(), 0.4))
    for t in (27.3, 37.3, 44.5, 56.4, 60.0): E.append((t, C.s_pop(), 0.5))
    E.append((57.1, C.s_thud(), 0.8)); E.append((35.7, C.s_whoosh(1.6), 0.8))
    return E
