# Elementos gráficos puntuales: "Inventa la cremallera"
SUB_Y = 0.70
KEYWORDS = {"cremallera", "chaqueta", "ganchos", "eternidad", "sueltan", "dientes", "saliente", "hueco", "desfasadas", "encaja", "aguantan",
            "imposible", "cursor", "canales", "solas", "cuña", "separa", "sale", "topes", "1913", "sundback", "cien"}
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
    label(C, ctx, t, 5.6, 8.9, "GANCHOS", A, "zip", dy=-420)
    label(C, ctx, t, 16.0, 17.6, "SALIENTE", A, "tooth", dy=-240, size=64)
    label(C, ctx, t, 17.6, 19.0, "HUECO", A, "tooth", dy=-240, size=64)
    if 26.4 <= t < 28.8:
        n = min(80, int((t - 26.4) / 0.22) + 1)
        C.badge(ctx, f"{n} / 80", W / 2, H * 0.165, win(t, 26.4, 28.8), R)
    label(C, ctx, t, 31.3, 33.5, "CURSOR", A, "slider", dy=-260, size=76)
    p = win(t, 32.5, 37.6)
    if p: C.outlined(ctx, "Y", W / 2, H * 0.30, 200, fill=Y, stroke=18, italic=True, scale=C.back(p))
    label(C, ctx, t, 45.8, 47.5, "CUÑA", A, "slider", dy=-260, size=76)
    label(C, ctx, t, 53.9, 55.6, "TOPES", A, "stops", dy=-230, size=76)
    label(C, ctx, t, 55.8, 57.7, "TOPE", A, "bstop", dy=-230, size=76)
    p = win(t, 58.9, 63.1)
    if p: C.badge(ctx, "GIDEON SUNDBACK · 1913", W / 2, H * 0.165, p, Y, size=62)
    p = win(t, 63.2, 66.0)
    if p: C.badge(ctx, "+100 AÑOS", W / 2, H * 0.165, p, G, size=80)

def sfx_events(C):
    E = []
    for t in (0.2, 5.2, 13.0, 15.6, 21.2, 29.0, 31.2, 37.9, 47.7, 51.0, 53.7, 58.0, 66.2):
        E.append((t, C.s_whoosh(), 0.4))
    for k in range(10): E.append((5.35 + k * 0.32, C.s_bleep(600 + 40 * k), 0.8))
    for k in range(6): E.append((10.8 + k * 0.35, C.s_pop(), 0.4))
    for k in range(11): E.append((26.4 + k * 0.22, C.s_bleep(900), 0.8))
    E.append((38.0, C.s_buzz(5.5), 0.25)); E.append((45.0, C.s_buzz(2.4), 0.25)); E.append((59.0, C.s_buzz(5.5), 0.25))
    E.append((49.8, C.s_clank(), 0.7))
    for t in (16.0, 31.3, 45.8, 53.9, 55.8): E.append((t, C.s_pop(), 0.5))
    return E
