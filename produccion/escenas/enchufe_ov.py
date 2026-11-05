# Capa 2D de «Si tuvieras que inventar el enchufe…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("enchufe")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"enchufe", "agujeros", "corriente", "voltios", "cincuenta", "dedos", "metal", "hueco", "clavija", "lavadora", "carcasa",
            "tercer", "láminas", "tierra", "barra", "fuga", "diferencial", "iguales", "treinta", "miliamperios", "veinte",
            "milisegundos", "parpadeo", "tapas", "clip"}

def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def contador(C, ctx, x, y, titulo, valor, col, p, size=60):
    if p <= 0: return
    C.outlined(ctx, titulo, x, y - size * 1.05, size * 0.8, fill=(1, 1, 1), stroke=8, alpha=p, shadow=False)
    C.badge(ctx, valor, x, y, p, col, size=size)

def barras(C, ctx, t, a, b):
    p = win(t, a, b)
    if not p: return
    x0, y0, L = 170, H * 0.36, 740
    for k, (txt, ms, col) in enumerate((("DIFERENCIAL 20 ms", 20, C.GREEN), ("PARPADEO ~150 ms", 150, C.YL))):
        y = y0 + k * 150; u = min(1, max(0, (t - a - 0.3 * k) / 0.7)) * p
        C.rrect(ctx, x0, y, L, 60, 14); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.85 * p); ctx.fill()
        C.rrect(ctx, x0, y, max(28, L * ms / 150 * u), 60, 14); ctx.set_source_rgba(*col, p); ctx.fill()
        C.outlined(ctx, txt, x0 + L / 2, y - 36, 58, fill=(1, 1, 1), stroke=8, alpha=p, shadow=False)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    label(C, ctx, t, T("dos agujeros") + 0.4, T("por uno llega"), "CONTACTOS", A, "contacto", dx=60, dy=-170, size=58)
    label(C, ctx, t, T("por uno llega") + 0.2, T("en españa"), "FASE", A, "fase", dx=-60, dy=-60, size=56)
    label(C, ctx, t, T("y por el otro"), T("en españa"), "NEUTRO", A, "neutro", dx=80, dy=-60, size=56)
    a0, a1 = T("doscientos"), T("y cambia de")
    if a0 - 0.2 <= t < a1:
        v = 230 * min(1, (t - a0 + 0.2) / 1.0); C.badge(ctx, f"{int(v)} V", W / 2, H * 0.265, win(t, a0 - 0.2, a1), Y, size=100)
    a0, a1 = T("cincuenta"), T("pero si alguien")
    if a0 - 0.3 <= t < a1:
        v = min(50, 50 * (t - a0 + 0.3) / 1.0); C.badge(ctx, f"{int(v)} VECES / S", W / 2, H * 0.265, win(t, a0 - 0.3, a1), Y, size=86)
    badge(C, ctx, t, T("podría tocar") + 0.3, T("así que hundes"), "✗ DESCARGA", R, size=88)
    label(C, ctx, t, T("hundes") + 0.4, T("y la clavija"), "HUECO", A, "hueco", dx=0, dy=170, size=62)
    badge(C, ctx, t, T("antes de que") , T("y si un cable"), "✓ PATAS TAPADAS", G, size=78)
    label(C, ctx, t, T("toca la carcasa") - 0.2, T("así que añades"), "CARCASA", A, "carcasa", dx=-80, dy=-180, size=58)
    badge(C, ctx, t, T("toca la carcasa") + 0.4, T("así que añades"), "✗ 230 V", R, size=96)
    label(C, ctx, t, T("esas dos láminas"), T("une la carcasa"), "TIERRA", A, "lamina", dx=0, dy=180, size=62)
    label(C, ctx, t, T("barra enterrada") - 0.2, T("pero aún falta"), "PICA", A, "pica", dx=-130, dy=0, size=60)
    badge(C, ctx, t, T("y no por ti"), T("pero aún falta"), "✓ A SALVO", G, size=88)
    label(C, ctx, t, T("el diferencial"), T("mide sin parar"), "DIFERENCIAL", A, "dif", dx=0, dy=-180, size=60)
    # sale / vuelve
    a0, a1 = T("mide sin parar"), T("y corta") + 1.2
    if a0 <= t < a1:
        p = win(t, a0, a1); ft = T("si faltan")
        sale = 10000; vuelve = 10000 - 30 * min(1, max(0, (t - ft) / 0.8))
        if t > T("y corta") + 0.1: sale = vuelve = 0
        (xs, ys), (xv, yv) = A("sale"), A("vuelve")
        contador(C, ctx, W * 0.28, H * 0.66, "SALE", miles(sale) + " mA", Y, p, size=56)
        contador(C, ctx, W * 0.68, H * 0.66, "VUELVE", miles(vuelve) + " mA", Y if vuelve > 9999 or sale == 0 else R, p, size=56)
    badge(C, ctx, t, T("tienen que") , T("si faltan"), "✓ IGUALES", G, size=84)
    badge(C, ctx, t, T("si faltan") + 0.6, T("y corta"), "✗ FALTAN 30 mA", R, size=80)
    a0 = T("y corta")
    if a0 <= t < T("más rápido"):
        v = min(20, 20 * (t - a0) / 0.6); C.badge(ctx, f"{int(v)} ms", W / 2, H * 0.265, win(t, a0, T("más rápido")), G, size=100)
    barras(C, ctx, t, T("más rápido"), T("y un detalle") + 0.3)
    label(C, ctx, t, T("unas tapas") , T("así un niño"), "TAPAS", A, "tapa", dx=60, dy=170, size=60)
    badge(C, ctx, t, T("si entran") + 0.4, T("así un niño"), "✓ ABIERTAS", G, size=80)
    badge(C, ctx, t, T("meter un clip"), T("sígueme") + 1.0, "✗ CERRADA", R, size=84)

def sfx_events(C):
    E = [(0.05, C.s_whoosh(), 0.4), (0.85, C.s_clank(), 0.5), (3.15, C.s_clank(), 0.4), (T("dos agujeros"), C.s_pop(), 0.5),
         (T("por uno llega"), C.s_buzz(1.5), 0.35), (T("doscientos"), C.s_pop(), 0.45), (T("cincuenta"), C.s_buzz(1.0), 0.35),
         (T("podría tocar") + 0.3, C.s_fail(), 0.55), (T("hundes"), C.s_whoosh(), 0.4), (T("la clavija") + 2.0, C.s_clank(), 0.5),
         (T("y toca") + 0.3, C.s_buzz(1.2), 0.5), (T("añades un tercer"), C.s_pop(), 0.45), (T("es la toma") + 0.5, C.s_clank(), 0.5),
         (T("une la carcasa"), C.s_whoosh(), 0.4), (T("y no por ti"), C.s_win(), 0.4), (T("en tu cuadro"), C.s_whoosh(), 0.4),
         (T("tienen que"), C.s_pop(), 0.4), (T("si faltan") + 0.6, C.s_fail(), 0.5), (T("y corta"), C.s_clank(), 0.7),
         (T("más rápido"), C.s_pop(), 0.4), (T("muchos enchufes"), C.s_whoosh(), 0.4), (T("si entran") + 0.4, C.s_clank(), 0.45),
         (T("meter un clip"), C.s_fail(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
