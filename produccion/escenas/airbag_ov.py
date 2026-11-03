# Elementos gráficos puntuales: "El airbag"
SUB_Y = 0.70
KEYWORDS = {"airbag", "milésimas", "parpadeo", "bombona", "sensores", "frenada", "choque", "centralita", "corriente", "origami", "bolsa",
            "pastilla", "química", "gas", "llena", "balón", "rebotarías", "agujeros", "desinfla", "vacía", "humo", "fuego", "polvo", "cinturón"}
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
    p = win(t, 1.7, 3.4)
    if p: C.badge(ctx, "0,03 s", W / 2, H * 0.165, p, Y, size=90)
    p = win(t, 3.7, 6.0)
    if p: C.badge(ctx, "PARPADEO: 0,3 s", W / 2, H * 0.165, p, (1, 1, 1))
    label(C, ctx, t, 10.4, 13.7, "SENSOR", A, "sensor", dy=-230)
    p = win(t, 13.98, 15.4)
    if p: C.badge(ctx, "FRENAZO: NO", W / 2, H * 0.165, p, (1, 1, 1))
    p = win(t, 17.2, 19.2)
    if p: C.badge(ctx, "CHOQUE: SÍ", W / 2, H * 0.165, p, R, size=80)
    label(C, ctx, t, 20.6, 23.4, "CENTRALITA", A, "ecu", dy=-200, size=62)
    label(C, ctx, t, 24.6, 27.0, "BOLSA PLEGADA", A, "hub", dy=-300, size=58)
    label(C, ctx, t, 28.0, 30.0, "PASTILLA", A, "pill", dy=260)
    label(C, ctx, t, 33.7, 36.0, "GAS", A, "hub", dy=-300, size=84)
    label(C, ctx, t, 46.6, 49.0, "AGUJEROS", A, "vents", dy=-260)
    label(C, ctx, t, 60.2, 65.0, "POLVO", A, "powder", dy=-250, size=80)
    label(C, ctx, t, 65.5, 71.5, "CINTURÓN", A, "belt", dy=-330, size=72)

def sfx_events(C):
    E = []
    E.append((0.0, C.s_buzz(1.6), 0.4))
    E.append((1.6, C.s_clank(), 1.0)); E.append((1.62, C.s_thud(), 1.0)); E.append((1.65, C.s_whoosh(0.3), 1.0))
    for t in (8.7, 9.6, 13.5, 23.6, 33.4, 39.4, 46.4, 58.2, 65.3, 71.8):
        E.append((t, C.s_whoosh(), 0.4))
    E.append((9.6, C.s_buzz(7.6), 0.25))
    E.append((T := 17.2, C.s_clank(), 1.0)); E.append((17.22, C.s_thud(), 1.0))
    for t in (10.4, 20.6, 24.6, 28.0, 46.6, 60.2, 65.5): E.append((t, C.s_pop(), 0.5))
    E.append((19.5, C.s_buzz(4.0), 0.4))
    E.append((30.0, C.s_thud(), 0.9)); E.append((33.7, C.s_whoosh(0.8), 1.0))
    E.append((50.4, C.s_whoosh(5.0), 0.35))
    return E
