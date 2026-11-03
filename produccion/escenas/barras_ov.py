# Elementos gráficos puntuales: "Inventa el código de barras"
import math
SUB_Y = 0.70
KEYWORDS = {"código", "barras", "errores", "número", "números", "máquina", "claro", "oscuro", "láser", "negro", "blanco", "marco",
            "revés", "patrón", "mancha", "arañazo", "comprobación", "cuadra", "pita", "cobra", "españa", "chicles", "1974", "lento"}
W, H = 1080, 1920
MODS = None

def clampx(x, m=260): return max(m, min(W - m, x))
def clampy(y, lo=330, hi=1150): return max(lo, min(hi, y))
def win(t, a, b, fade=0.15):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / 0.22) * min(1.0, (b - t) / fade)

def label(C, ctx, t, a, b, text, A, key, dx=0, dy=-220, size=68):
    p = win(t, a, b)
    if p:
        x, y = A(key); C.callout(ctx, text, clampx(x + dx), clampy(y + dy), p, size=size)

def signal(ctx, t, a, b, C):
    """onda claro/oscuro que 've' el láser"""
    p = win(t, a, b)
    if not p: return
    import barras_scene as BS
    mods = [on for (_, on, _) in BS.modules()]
    x0, y0, w, h = 90, 290, 900, 120
    ctx.save(); C.rrect(ctx, x0 - 20, y0 - 30, w + 40, h + 60, 20); ctx.set_source_rgba(0.12, 0.14, 0.18, 0.9 * p); ctx.fill()
    n = len(mods); prog = min(1.0, ((t - a) * 0.9) % 1.0 * 1.0)
    upto = int(n * prog)
    ctx.set_line_width(6); ctx.set_source_rgba(0.3, 1.0, 0.5, p); ctx.set_line_join(1)
    for i in range(upto):
        x = x0 + w * i / n; y = y0 + (h if mods[i] else 0)
        if i == 0: ctx.move_to(x, y)
        else: ctx.line_to(x, y)
        ctx.line_to(x0 + w * (i + 1) / n, y)
    ctx.stroke(); ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    p = win(t, 6.2, 8.2)
    if p: C.badge(ctx, "TECLEA: 19,90 €", W / 2, H * 0.165, p, R)
    p = win(t, 11.0, 13.8)
    if p:
        n = min(13, int((t - 11.0) / 0.2) + 1); C.badge(ctx, "8412345678905"[:n], W / 2, H * 0.165, p, (1, 1, 1))
    p = win(t, 18.9, 20.2)
    if p:
        on = t < 19.45
        C.badge(ctx, "CLARO" if on else "OSCURO", W / 2, H * 0.165, p, (1, 1, 1) if on else (0.55, 0.58, 0.65), size=80)
    signal(ctx, t, 25.9, 30.5, C)
    label(C, ctx, t, 33.3, 38.3, "MARCO", A, "label", dy=-330, size=80)
    label(C, ctx, t, 42.4, 49.5, "IZQUIERDA", A, "left", dy=-300, size=56)
    label(C, ctx, t, 43.4, 49.5, "DERECHA", A, "right", dy=-200, size=56)
    label(C, ctx, t, 51.4, 55.0, "MANCHA", A, "stain", dy=-240)
    p = win(t, 53.0, 55.0)
    if p: C.badge(ctx, "LEE: 8412345671905", W / 2, H * 0.165, p, R)
    label(C, ctx, t, 55.3, 59.8, "COMPROBACIÓN", A, "last", dx=-120, dy=-260, size=60)
    p = win(t, 60.0, 63.4)
    if p: C.badge(ctx, "8·1 + 4·3 + 1·1 + 2·3 …", W / 2, H * 0.165, p, G, size=60)
    p = win(t, 64.3, 67.8)
    if p: C.badge(ctx, "NO CUADRA", W / 2, H * 0.165, p, R, size=76)
    p = win(t, 70.4, 75.3)
    if p: C.badge(ctx, "84 = ESPAÑA", W / 2, H * 0.165, p, Y, size=80)
    p = win(t, 80.3, 82.0)
    if p: C.badge(ctx, "1974", W / 2, H * 0.165, p, Y, size=90)

def sfx_events(C):
    E = []
    for t in (0.2, 2.6, 8.5, 14.1, 20.4, 25.9, 30.9, 38.9, 41.6, 50.1, 55.1, 63.7, 68.1, 75.8, 82.2):
        E.append((t, C.s_whoosh(), 0.4))
    for k in range(25): E.append((2.6 + k * 0.2, C.s_bleep(700 + 30 * (k % 5)), 1.0))
    E.append((6.3, C.s_fail(), 0.6))
    for k in range(13): E.append((11.0 + k * 0.2, C.s_bleep(800), 1.0))
    for t in (28.6, 47.0, 81.0): E.append((t, C.s_bleep(1568), 3.0))
    for t in (33.3, 42.4, 51.4, 55.3, 70.4): E.append((t, C.s_pop(), 0.5))
    E.append((65.6, C.s_fail(), 0.8))
    return E
