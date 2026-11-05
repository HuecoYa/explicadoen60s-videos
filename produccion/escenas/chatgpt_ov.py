# Capa 2D de «Así escribe ChatGPT»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("chatgpt")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"chatgpt", "frase", "tokens", "trozo", "trozos", "doscientos", "mil", "números", "red", "adivinar", "probabilidades",
            "playa", "cuarenta", "cama", "veinte", "oficina", "diez", "final", "segundo", "probable", "robot", "distinta",
            "inventa", "verdad", "falso", "seguridad", "compruébalo"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def ciclos_pick():
    t1, t2 = T("otra vez"), T("y otra")
    out = [T("elige una") + 0.35, t1 + 0.35, t2 + 0.3]
    s = t2 + 0.4; dt = 0.55
    for k in range(4): out.append(s + dt * 0.75); s += dt; dt *= 0.8
    return out

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    label(C, ctx, t, T("no sabe") + 0.3, T("cómo escribe") + 0.3, "???", A, "cursor", dx=-60, dy=200, size=80)
    label(C, ctx, t, T("tokens") - 0.1, T("su diccionario"), "TOKENS", A, "prompt", dx=0, dy=-60, size=64)
    a0, a1 = T("su diccionario"), T("cada trozo se")
    if a0 <= t < a1:
        v = 200000 * ss((t - a0 - 0.2) / max(0.1, T("distintos", fin=True) - a0 - 0.2))
        C.badge(ctx, miles(v), W / 2, H * 0.265, win(t, a0, a1), Y, size=96)
    p = win(t, T("lista") - 0.1, T("y con esos") + 0.6)
    if p:
        x, y = A("vec"); C.badge(ctx, "[ 0,21 · −0,83 · 0,47 … ]", W / 2 - 30, clampy(y, 600, 1400), p, (0.45, 0.75, 1.0), size=62)
    label(C, ctx, t, T("una red") + 0.3, T("no sabe", 2), "RED", A, "red", dx=0, dy=-70, size=64)
    picks = ciclos_pick()
    a0, a1 = T("elige una"), T("por eso ves") - 0.3
    if a0 <= t < a1:
        n = 4 + sum(1 for p in picks if t >= p)
        C.badge(ctx, f"TROZOS: {n}", W / 2, H * 0.265, win(t, a0, a1), Y, size=82)
    badge(C, ctx, t, T("sonaría") + 0.2, T("así que a veces"), "✗ IGUAL ×3", R, size=84)
    badge(C, ctx, t, T("y cada respuesta"), T("y por qué") - 0.1, "✓ 3 DISTINTAS", G, size=84)
    badge(C, ctx, t, T("lo escribe") + 0.2, T("así que compruébalo"), "SEGURIDAD: 100 %", Y, size=78)
    badge(C, ctx, t, T("así que compruébalo") + 0.2, DUR + 1, "✗ REAL: 384.400 km", R, size=80)

def sfx_events(C):
    E = [(0.05, C.s_whoosh(), 0.4)]
    for k in range(7): E.append((0.05 + 0.3 * k, C.s_pop(), 0.3))
    E += [(T("cómo escribe"), C.s_whoosh(), 0.4), (T("trocea") + 0.6, C.s_clank(), 0.4), (T("su diccionario"), C.s_buzz(2.5), 0.25),
          (T("cada trozo se"), C.s_whoosh(), 0.4), (T("una red"), C.s_buzz(3.0), 0.25), (T("adivinar") + 0.5, C.s_pop(), 0.45),
          (T("playa"), C.s_pop(), 0.4), (T("cama"), C.s_pop(), 0.4), (T("oficina"), C.s_pop(), 0.4)]
    for p in ciclos_pick(): E.append((p, C.s_coin(), 0.35))
    E += [(T("por eso ves"), C.s_whoosh(), 0.4), (T("sonaría"), C.s_fail(), 0.4), (T("de abajo"), C.s_pop(), 0.45),
          (T("y cada respuesta"), C.s_win(), 0.4), (T("y por qué"), C.s_whoosh(), 0.4), (T("si un dato") + 0.3, C.s_coin(), 0.4),
          (T("así que compruébalo"), C.s_fail(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
