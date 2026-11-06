# Capa 2D de «Si tuvieras que inventar WhatsApp…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("whatsapp")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"mensajes", "cien", "servidor", "candado", "secreto", "llave", "letras", "problema", "copiarla", "dos", "llaves",
            "pública", "privada", "mismo", "nada", "setenta", "ocho", "universo", "robara", "cambia", "cuándo"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((24, (0, 0, 0)), (14, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.arc(x, y, r, 0, math.tau); ctx.stroke()
        ctx.move_to(x - r * 0.7, y - r * 0.7); ctx.line_to(x + r * 0.7, y + r * 0.7); ctx.stroke()
    ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # mensajes al día
    a0, a1 = T("cada día"), T("lo primero")
    if a0 <= t < a1:
        v = 1e11 * sg(t, a0 + 0.2, T("millones", fin=True)) ** 2
        C.badge(ctx, miles(v), W / 2, BY, win(t, a0, a1), G, size=84)
    label(C, ctx, t, T("y todos pasan") + 0.3, T("lo primero"), "SERVIDOR", A, "srv", dy=-120, size=60)
    label(C, ctx, t, T("un candado") + 0.1, T("antes de salir"), "CANDADO", A, "lock", dx=60, dy=-150, size=60)
    label(C, ctx, t, T("un número secreto"), T("sale convertido"), "LLAVE", A, "ks", dx=-40, dy=-150, size=60)
    # el amigo no puede abrirlo
    p = win(t, T("tu amigo necesita") + 0.6, T("y si se la mandas"))
    if p: x, y = A("lock"); cross(ctx, x, y - 140, 70, p)
    label(C, ctx, t, T("alguien podría"), T("así que cada móvil"), "COPIA", A, "kc", dx=0, dy=-140, size=60)
    label(C, ctx, t, T("una pública") + 0.4, T("tu móvil mezcla"), "PÚBLICA", A, "pubA", dx=-20, dy=-120, size=50)
    label(C, ctx, t, T("una pública") + 0.6, T("tu móvil mezcla"), "PÚBLICA", A, "pubB", dx=20, dy=-120, size=50)
    label(C, ctx, t, T("y una privada") + 0.4, T("tu móvil mezcla"), "PRIVADA", A, "privA", dx=0, dy=150, size=50)
    label(C, ctx, t, T("y una privada") + 0.6, T("tu móvil mezcla"), "PRIVADA", A, "privB", dx=0, dy=150, size=50)
    # los dos números iguales
    a0, a1 = T("y los dos llegan"), T("y el servidor")
    if a0 <= t < a1:
        p = win(t, a0 + 0.3, a1)
        xa, ya = A("numA"); xb, yb = A("numB")
        C.outlined(ctx, "=", (xa + xb) / 2, (ya + yb) / 2, 120, fill=G, stroke=12, alpha=p, scale=C.back(p))
        C.badge(ctx, "✓ 0 ENVÍOS", W / 2, BY, win(t, T("sin habérselo"), a1), G, size=70)
    # el servidor
    a0, a1 = T("no tiene ninguna"), T("y aquí viene")
    if a0 <= t < a1: C.badge(ctx, "✗ 0 PRIVADAS", W / 2, BY, win(t, a0, a1), R, size=74)
    # número de 78 cifras y años para probarlas
    a0, a1 = T("esa llave es"), T("pero aún falta")
    if a0 <= t < a1:
        n = int(78 * sg(t, a0, a0 + 1.4))
        C.badge(ctx, "%d CIFRAS" % n, W / 2, BY, win(t, a0, T("probando")), Y, size=84)
        b0 = T("tardarías")
        if t > T("probando"):
            e = 1 + 62 * sg(t, b0 - 0.6, T("universo", fin=True) + 0.3)       # años: 10^1 … 10^63
            n = int(e)
            yrs = (miles(10 ** n) + " AÑOS") if n <= 9 else ("1 Y %d CEROS DE AÑOS" % n)
            C.badge(ctx, yrs, W / 2, BY + 40, win(t, T("probando"), a1), R if n > 10 else Y, size=60)
            if n > 10:
                C.badge(ctx, "UNIVERSO: 13.800.000.000 AÑOS", W / 2, BY + 170, win(t, b0 + 0.4, a1), B, size=44)
    label(C, ctx, t, T("si un día alguien") + 0.4, T("así que la llave"), "LADRÓN", A, "numA", dx=0, dy=-260, size=56)
    # una llave por mensaje
    a0, a1 = T("así que la llave cambia"), T("eso sí")
    if a0 <= t < a1:
        i = int((t - a0) / 1.3) + 1
        C.badge(ctx, "LLAVE Nº %d" % i, W / 2, BY, win(t, a0, a1), Y, size=78)
    a0, a1 = T("el servidor sigue"), DUR
    if a0 <= t < a1:
        label(C, ctx, t, a0 + 0.3, a1 - 0.3, "QUIÉN · CUÁNDO", A, "srv", dy=-150, size=56)

def sfx_events(C):
    E = [(0.0, C.s_pop(), 0.5), (0.55, C.s_pop(), 0.5), (0.6, C.s_whoosh(), 0.5), (T("cada día"), C.s_buzz(2.0), 0.25),
         (T("un candado"), C.s_clank(), 0.5), (T("el mensaje se mezcla") + 0.3, C.s_whoosh(), 0.4), (T("sale convertido") + 0.2, C.s_clank(), 0.45),
         (T("sale convertido") + 1.0, C.s_whoosh(), 0.4), (T("tu amigo necesita") + 0.6, C.s_fail(), 0.4), (T("y si se la mandas"), C.s_whoosh(), 0.4),
         (T("alguien podría"), C.s_fail(), 0.45), (T("así que cada móvil") + 0.3, C.s_pop(), 0.45), (T("una pública"), C.s_whoosh(), 0.35),
         (T("y una privada"), C.s_thud(), 0.45), (T("tu móvil mezcla") + 1.2, C.s_pop(), 0.45), (T("su móvil hace") + 1.2, C.s_pop(), 0.45),
         (T("y los dos llegan") + 0.3, C.s_win(), 0.45), (T("no tiene ninguna"), C.s_fail(), 0.4), (T("esa llave es"), C.s_whoosh(), 0.4),
         (T("tardarías"), C.s_coin(), 0.4), (T("si un día alguien"), C.s_whoosh(), 0.45), (T("podría leer"), C.s_fail(), 0.4),
         (T("así que la llave cambia"), C.s_clank(), 0.45), (T("eso sí"), C.s_thud(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(4): E.append((T("cada mensaje tiene") - 1.6 + 1.3 * k, C.s_pop(), 0.3))
    return E
