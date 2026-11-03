# Elementos gráficos puntuales: "Inventa un mechero"
SUB_Y = 0.72
KEYWORDS = {"mechero", "fuego", "chispa", "chispas", "rueda", "piedra", "aleación", "combustible", "butano", "gas", "presión", "líquido",
            "válvula", "botón", "llama", "ruedecita", "viento", "chimenea", "muelle", "cristal", "eléctrica"}
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
    label(C, ctx, t, 5.3, 8.2, "RUEDA", A, "wheel", dx=60, dy=-200)
    label(C, ctx, t, 6.6, 10.9, "PIEDRA", A, "flint", dx=120, dy=160)
    p = win(t, 15.3, 17.4)
    if p: C.badge(ctx, "CHISPA SOLA = NADA", W / 2, H * 0.165, p, R, size=62)
    label(C, ctx, t, 19.4, 22.0, "BUTANO", A, "tank", dy=-120, size=80)
    p = win(t, 25.2, 29.9)
    if p: C.badge(ctx, "GAS → LÍQUIDO".replace("→", "»"), W / 2, H * 0.165, p, G, size=70)
    label(C, ctx, t, 34.0, 37.4, "VÁLVULA", A, "valve", dy=-230)
    label(C, ctx, t, 48.6, 52.2, "REGULADOR", A, "reg", dx=-40, dy=-260, size=62)
    label(C, ctx, t, 54.3, 57.9, "CHIMENEA", A, "chim", dy=-250)
    label(C, ctx, t, 59.4, 62.7, "MUELLE", A, "spring", dx=-120, dy=230)
    label(C, ctx, t, 63.4, 66.8, "CRISTAL", A, "piezo", dy=-260)
    p = win(t, 44.4, 45.4, fade=0.3)
    if p: C.outlined(ctx, "¡FUEGO!", W / 2, H * 0.3, 140, fill=Y, stroke=18, italic=True, scale=C.back(p), rot=-0.08)

def sfx_events(C):
    E = []
    for t in (0.2, 3.5, 17.6, 20.3, 23.8, 30.3, 33.8, 48.3, 54.1, 58.2, 63.1, 70.2):
        E.append((t, C.s_whoosh(), 0.4))
    for a in (5.3, 8.4, 40.9, 54.6):
        for k in range(6): E.append((a + k * 0.12, C.s_bleep(2400 + 200 * k), 0.35))
    E.append((30.3, C.s_buzz(3.6), 0.2)); E.append((37.8, C.s_buzz(6.5), 0.15))
    E.append((44.4, C.s_whoosh(0.6), 1.0)); E.append((45.3, C.s_whoosh(1.5), 0.8))
    E.append((52.5, C.s_whoosh(1.5), 0.8)); E.append((55.3, C.s_whoosh(0.6), 0.7))
    E.append((65.8, C.s_clank(), 0.6)); E.append((67.55, C.s_clank(), 0.6))
    for t in (5.3, 19.4, 34.0, 48.6, 54.3, 59.4, 63.4): E.append((t, C.s_pop(), 0.5))
    return E
