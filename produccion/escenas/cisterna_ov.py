# Elementos gráficos puntuales: "La cisterna del váter"
SUB_Y = 0.74
KEYWORDS = {"cisterna", "plástico", "agua", "tapón", "boya", "flota", "grifo", "electricidad", "sensores", "rebosadero", "desborde",
            "problema", "escapa", "litros", "colorante", "fuga", "botón", "ahorrar", "pagas"}
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
    label(C, ctx, t, 7.1, 10.7, "TAPÓN", A, "plug", dy=220)
    label(C, ctx, t, 12.1, 16.6, "BOYA", A, "float", dy=-220, size=80)
    label(C, ctx, t, 14.8, 20.0, "GRIFO", A, "fill", dy=-260)
    p = win(t, 25.6, 29.3)
    if p: C.badge(ctx, "0 CABLES · 0 SENSORES", W / 2, H * 0.165, p, G, size=62)
    label(C, ctx, t, 31.7, 37.2, "REBOSADERO", A, "overflow", dy=-250, size=62)
    p = win(t, 47.9, 50.5)
    if p: C.badge(ctx, "CIENTOS DE LITROS / DÍA", W / 2, H * 0.165, p, R, size=60)
    label(C, ctx, t, 51.4, 55.4, "COLORANTE", A, "tank", dy=-330, size=66)
    p = win(t, 57.6, 59.0)
    if p: C.badge(ctx, "¡FUGA!", W / 2, H * 0.165, p, R, size=90)
    label(C, ctx, t, 59.3, 61.6, "MEDIA", A, "small", dx=-80, dy=-200)
    label(C, ctx, t, 61.9, 64.2, "COMPLETA", A, "big", dx=60, dy=-200)
def sfx_events(C):
    E = []
    for t in (0.2, 4.7, 11.0, 14.8, 20.2, 25.6, 29.5, 37.5, 50.7, 55.7, 59.2, 64.5): E.append((t, C.s_whoosh(), 0.4))
    E.append((5.7, C.s_clank(), 0.5)); E.append((6.4, C.s_whoosh(4.0), 0.9)); E.append((17.2, C.s_buzz(7.2), 0.15)); E.append((40.0, C.s_buzz(10.4), 0.08))
    E.append((59.5, C.s_whoosh(1.0), 0.8)); E.append((62.3, C.s_whoosh(1.5), 0.9))
    for t in (7.1, 12.1, 14.8, 31.7, 51.4, 59.3, 61.9): E.append((t, C.s_pop(), 0.5))
    E.append((57.6, C.s_fail(), 0.6))
    return E
