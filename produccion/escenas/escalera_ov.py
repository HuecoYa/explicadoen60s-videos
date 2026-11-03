# Elementos gráficos puntuales: "Inventa una escalera mecánica"
SUB_Y = 0.72
KEYWORDS = {"escalera", "mecánica", "cinta", "resbalas", "escalones", "cadena", "caerías", "ruedas", "raíl", "plano", "liso", "regresan",
            "atrapado", "ranuras", "peine", "pasamanos", "velocidad", "motor", "sensores", "cordón"}
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
    p = win(t, 8.5, 10.9)
    if p: C.badge(ctx, "¡RESBALAS!", W / 2, H * 0.165, p, R, size=80)
    p = win(t, 17.4, 20.8)
    if p: C.badge(ctx, "ESCALONES INCLINADOS", W / 2, H * 0.165, p, R, size=60)
    label(C, ctx, t, 21.0, 26.6, "2 PARES\nDE RUEDAS", A, "wheels", dy=260, size=60)
    label(C, ctx, t, 28.2, 31.8, "RAÍLES", A, "rails", dy=-300, size=76)
    label(C, ctx, t, 34.6, 38.5, "SUELO LISO", A, "flat", dy=-240, size=64)
    p = win(t, 43.0, 46.9)
    if p: C.badge(ctx, "¡ATRAPADO!", W / 2, H * 0.165, p, R, size=80)
    label(C, ctx, t, 47.3, 49.4, "RANURAS", A, "comb", dx=-120, dy=-240)
    label(C, ctx, t, 49.7, 57.0, "PEINE", A, "comb", dy=-250, size=80)
    label(C, ctx, t, 59.3, 64.5, "PASAMANOS", A, "hand", dy=-250)
    p = win(t, 59.3, 64.5)
    if p: C.badge(ctx, "MISMA VELOCIDAD", W / 2, H * 0.165, p, G, size=66)
    label(C, ctx, t, 66.3, 69.0, "SENSOR", A, "sensor", dy=-250)
def sfx_events(C):
    E = [(0.0, C.s_buzz(66.3), 0.12)]
    for t in (0.2, 4.8, 11.0, 16.4, 20.9, 28.2, 32.1, 38.9, 42.1, 47.2, 57.4, 64.9, 69.2): E.append((t, C.s_whoosh(), 0.4))
    E.append((8.6, C.s_fail(), 0.7)); E.append((10.7, C.s_thud(), 0.8)); E.append((18.4, C.s_fail(), 0.6)); E.append((45.4, C.s_fail(), 0.7))
    for t in (21.0, 28.2, 34.6, 47.3, 49.7, 59.3, 66.3): E.append((t, C.s_pop(), 0.5))
    E.append((66.3, C.s_clank(), 0.8))
    return E
