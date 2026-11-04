# Capa 2D de «Si tuvieras que inventar los auriculares»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("auriculares")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"auriculares", "sonido", "aire", "membrana", "bobina", "cobre", "imán", "corriente", "sentido", "empuja", "tira", "atrae",
            "repele", "grave", "veinte", "aguda", "mil", "anula", "carcasa", "agujeritos", "tela", "almohadilla", "graves", "agudos", "dieciséis"}

def arrow(ctx, x0, y0, x1, y1, col, p, lw=12):
    if p <= 0: return
    x1 = x0 + (x1 - x0) * p; y1 = y0 + (y1 - y0) * p; ang = math.atan2(y1 - y0, x1 - x0)
    for st, c in ((lw + 8, (0, 0, 0)), (lw, col)):
        ctx.set_line_width(st); ctx.set_source_rgb(*c); ctx.set_line_cap(1); ctx.set_line_join(1)
        ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()
        for s in (1, -1):
            ctx.move_to(x1, y1); ctx.line_to(x1 - 30 * math.cos(ang + s * 0.5), y1 - 30 * math.sin(ang + s * 0.5)); ctx.stroke()

def barra(C, ctx, x, y, w, h, frac, col, a, txt):
    ctx.save(); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.9 * a); C.rrect(ctx, x - 12, y - 12, w + 24, h + 24, 18); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.15 * a); C.rrect(ctx, x, y, w, h, 10); ctx.fill()
    if frac > 0.002: ctx.set_source_rgba(*col, a); C.rrect(ctx, x, y, max(w * frac, 20), h, 10); ctx.fill()
    ctx.restore(); C.outlined(ctx, txt, x + w / 2, y + h / 2, 46, fill=(1, 1, 1), stroke=8, alpha=a, shadow=False)

def miles(n): return "{:,}".format(int(n)).replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    label(C, ctx, t, T("el sonido es") + 0.2, T("así que necesitas"), "AIRE", A, "aire", dy=-60, size=64)
    label(C, ctx, t, T("una membrana"), T("pero cómo la"), "MEMBRANA", A, "mem", dx=60, dy=-120, size=60)
    label(C, ctx, t, T("una bobina") - 0.6, T("y la colocas") + 0.4, "BOBINA", A, "bob", dx=150, dy=40, size=60)
    label(C, ctx, t, T("en un imán") , T("cuando llega"), "IMÁN", A, "iman", dx=150, dy=60, size=64)
    # la corriente cambia de sentido
    a0, a1 = T("cuando llega"), T("y cada vez")
    p = win(t, a0, a1)
    if p:
        x, y = A("cab"); s = 1 if math.sin(t * 2 * math.pi * 0.8) > 0 else -1
        C.badge(ctx, "CORRIENTE " + ("IDA" if s > 0 else "VUELTA"), W / 2, H * 0.265, p, Y, size=72)
    # la bobina es un imán: N / S, atrae y repele
    a0, a1 = T("y cada vez"), T("una nota grave")
    p = win(t, a0, a1)
    if p:
        x, y = A("bob")
        up = math.sin(2 * math.pi * 1.5 * t) > 0
        C.outlined(ctx, "N" if up else "S", clampx(x + 180), y - 40, 90, fill=R if up else B, stroke=12, alpha=p)
    p = win(t, T("el imán fijo"), T("y la repele"))
    if p:
        C.badge(ctx, "ATRAE", W / 2, H * 0.265, p, B, size=76); x, y = A("mem"); arrow(ctx, x + 120, y - 160, x + 120, y - 20, B, p)
    p = win(t, T("y la repele"), T("y la membrana va") + 0.4)
    if p:
        C.badge(ctx, "REPELE", W / 2, H * 0.265, p, R, size=76); x, y = A("mem"); arrow(ctx, x + 120, y - 20, x + 120, y - 160, R, p)
    # frecuencias
    a0, a1 = T("una nota grave"), T("pero la membrana también")
    if a0 <= t < a1:
        if t < T("una aguda"): n = 20 * min(1, (t - a0) / 0.8); col = B
        else: n = 20 + 19980 * min(1, (t - T("hasta veinte")) / 1.0) if t > T("hasta veinte") else 20; col = Y
        C.badge(ctx, "%s VECES/S" % miles(round(n)), W / 2, H * 0.265, win(t, a0, a1), col, size=76)
    # cancelación
    a0, a1 = T("pero la membrana también"), T("así que cierras") + 0.8
    if a0 <= t < a1:
        p = win(t, a0, a1); x0, w, h = 160, 760, 70; y0 = H * 0.24
        v = 1 - seg01(t, T("lo anula") - 0.6, T("lo anula") + 0.3)
        v = max(v, seg01(t, T("así que cierras"), T("así que cierras") + 0.8))
        barra(C, ctx, x0, y0, w, h, v, G if v > 0.5 else R, p, "VOLUMEN %d%%" % round(100 * v))
        label(C, ctx, t, T("hacia atrás") - 0.3, T("lo anula"), "ATRÁS", A, "back", dx=200, dy=0, size=58)
    label(C, ctx, t, T("con una carcasa") - 0.4, T("pero el aire"), "CARCASA", A, "car", dx=120, dy=40, size=60)
    # el aire encerrado frena: recorrido de la membrana
    a0, a1 = T("pero el aire encerrado"), T("por último")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        v = 1 - 0.7 * seg01(t, a0, a0 + 0.8) + 0.7 * seg01(t, T("así que le haces"), T("así que le haces") + 1.0)
        barra(C, ctx, 160, H * 0.24, 760, 70, v, G if v > 0.6 else R, p, "MOVIMIENTO %d%%" % round(100 * v))
    label(C, ctx, t, T("agujeritos") - 0.2, T("tapados"), "AGUJERITOS", A, "aguj", dx=60, dy=110, size=56)
    label(C, ctx, t, T("tapados"), T("por último"), "TELA", A, "aguj", dx=60, dy=110, size=58)
    label(C, ctx, t, T("la almohadilla"), T("y un dato"), "ALMOHADILLA", A, "almo", dx=-40, dy=-110, size=56)
    # oído con los años
    a0 = T("y un dato")
    if t >= a0:
        p = win(t, a0, DUR + 1)
        u = seg01(t, T("a muchos adultos"), T("dieciséis", fin=True) + 0.3)
        hz = 20000 - 4000 * u
        barra(C, ctx, 160, H * 0.24, 760, 70, hz / 20000, Y if u < 0.5 else (1.0, 0.6, 0.25), p, "OYES HASTA %s" % miles(round(hz, -2)))

def seg01(t, a, b):
    x = max(0.0, min(1.0, (t - a) / max(b - a, 1e-4))); return x * x * (3 - 2 * x)

def sfx_events(C):
    E = [(0.0, C.s_buzz(5.5), 0.5), (T("el sonido es") - 0.3, C.s_whoosh(), 0.5), (T("una membrana"), C.s_pop(), 0.5), (T("una bobina"), C.s_pop(), 0.5),
         (T("en un imán"), C.s_clank(), 0.5), (T("cuando llega"), C.s_buzz(2.5), 0.4), (T("una nota grave"), C.s_thud(), 0.7),
         (T("hasta veinte"), C.s_bleep(1800), 1.0), (T("lo anula"), C.s_fail(), 0.6), (T("con una carcasa"), C.s_clank(), 0.5),
         (T("agujeritos"), C.s_pop(), 0.5), (T("la almohadilla"), C.s_thud(), 0.5), (T("dieciséis"), C.s_pop(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
