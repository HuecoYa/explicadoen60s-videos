# Capa 2D de «Así funciona el GPS»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("gps")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"escucha", "veinte", "treinta", "atómico", "hora", "luz", "siete", "distancia", "esfera", "círculo", "puntos", "espacio",
            "cuarto", "cuatro", "millonésima", "trescientos", "rápido", "treinta", "ocho", "einstein", "diez", "ajustan", "nada"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def miles(v): return f"{int(round(v)):,}".replace(",", ".")
BY = H * 0.265

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    # el móvil no envía nada
    for a0, a1 in ((T("sin preguntar"), T("mira hacia") - 0.1), (T("y todo esto") + 0.3, DUR)):
        if a0 <= t < a1:
            C.badge(ctx, "ENVIADO: 0 BYTES", W / 2, BY, win(t, a0, a1), G, size=66)
    # 20.000 km de altura
    a0, a1 = T("veinte mil"), T("hay treinta")
    if a0 <= t < a1 + 0.3:
        v = 20000 * sg(t, a0, a0 + 1.8)
        C.badge(ctx, miles(v) + " KM", W / 2, BY, win(t, a0, a1 + 0.3), Y, size=84)
    # 31 satélites
    a0, a1 = T("hay treinta"), T("cada uno")
    if a0 <= t < a1:
        n = int(31 * sg(t, a0 + 0.1, a0 + 2.4))
        C.badge(ctx, "%d SATÉLITES" % n, W / 2, BY, win(t, a0, a1), B, size=80)
    # el reloj atómico emite la hora
    label(C, ctx, t, T("reloj atómico") - 0.2, T("y no para"), "RELOJ ATÓMICO", A, "sat1", dy=-260, size=58)
    a0, a1 = T("y no para"), T("esa señal")
    if a0 <= t < a1:
        us = int((t - a0) * 1e6) % 1000000
        C.badge(ctx, "12:00:%02d,%06d" % (int(t - a0) % 60, us), W / 2, BY, win(t, a0, a1), Y, size=78)
    # 300.000 km/s y 0,07 s
    a0, a1 = T("esa señal"), T("tu móvil compara")
    if a0 <= t < a1:
        C.badge(ctx, "300.000 KM/S", W / 2, BY, win(t, a0, a1), Y, size=70)
        v = 0.07 * sg(t, a0 + 0.2, a1 - 0.4)
        C.badge(ctx, ("%.3f S" % v).replace(".", ","), W / 2, BY + 150, win(t, a0 + 0.2, a1), B, size=84)
    # comparar horas → retraso → distancia
    a0, a1 = T("tu móvil compara"), T("con un satélite")
    if a0 <= t < a1:
        C.badge(ctx, "SALE  12:00:00,000", W / 2, BY, win(t, a0, a1), Y, size=60)
        C.badge(ctx, "LLEGA 12:00:00,067", W / 2, BY + 120, win(t, a0 + 0.6, a1), B, size=60)
        b0 = T("con el retraso")
        if t > b0:
            km = 20100 * sg(t, T("calcula"), T("distancia", fin=True))
            txt = "0,067 S" if t < T("calcula") else "%s KM" % miles(km)
            C.badge(ctx, txt, W / 2, BY + 260, win(t, b0, a1), G, size=80)
    # esferas: distancia a cada satélite
    for i, (a0, a1, km, col) in enumerate(((T("con un satélite"), T("con dos"), 20100, Y), (T("con dos"), T("con tres"), 21300, (0.3, 0.9, 1.0)),
                                           (T("con tres"), T("pero hay un"), 22700, (1.0, 0.4, 0.85)))):
        if a0 <= t < T("pero hay un"):
            C.badge(ctx, "%d · %s KM" % (i + 1, miles(km * sg(t, a0, a0 + 1.2))), W / 2, BY + 110 * i, win(t, a0, T("pero hay un")), col, size=56)
    label(C, ctx, t, T("esa señal") + 0.3, T("el reloj de tu"), "TÚ", A, "pin", dx=0, dy=130, size=64)
    p = win(t, T("y uno de ellos") + 0.5, T("el reloj de tu"))
    if p:
        x, y = A("space"); C.badge(ctx, "✗ ESPACIO", clampx(x), clampy(y - 120), p, R, size=54)
    # el reloj del móvil se equivoca
    a0, a1 = T("el reloj de tu"), T("así que usas")
    if a0 <= t < a1:
        C.badge(ctx, "CUARZO, NO ATÓMICO", W / 2, BY, win(t, a0, a1), R, size=60)
    # cuarto satélite
    a0, a1 = T("así que usas"), T("y la precisión")
    if a0 <= t < a1:
        n = 3 if t < T("cuarto") + 0.4 else 4
        C.badge(ctx, ("✓ " if n == 4 and t > T("por eso") else "") + "%d SATÉLITES" % n, W / 2, BY, win(t, a0, a1), G if n == 4 else Y, size=78)
    # 1 µs = 300 m
    a0, a1 = T("un error de"), T("y aquí viene")
    if a0 <= t < a1:
        C.badge(ctx, "ERROR: 0,000001 S", W / 2, BY, win(t, a0, a1), R, size=66)
        b0 = T("son trescientos") - 0.4
        if t > b0:
            m = 300 * sg(t, b0, b0 + 1.0)
            C.badge(ctx, "%d M" % m, W / 2, BY + 140, win(t, b0, a1), Y, size=90)
            xa, ya = A("dot"); xb, yb = A("ghost")
            pp = win(t, b0 + 0.3, a1)
            if pp and abs(xb - xa) + abs(yb - ya) > 40:
                ctx.save(); ctx.set_line_cap(1)
                for lw, c in ((18, (0, 0, 0)), (10, Y)):
                    ctx.set_line_width(lw); ctx.set_source_rgba(*c, pp); ctx.move_to(xa, ya); ctx.line_to(xb, yb); ctx.stroke()
                ctx.restore()
    # relojes: el de arriba se adelanta
    label(C, ctx, t, T("allí arriba") - 0.2, T("si nadie"), "TIERRA", A, "ckE", dy=-230, size=58)
    label(C, ctx, t, T("allí arriba") + 0.2, T("si nadie"), "ÓRBITA", A, "ckS", dy=230, size=58)
    a0, a1 = T("los relojes de los"), T("si nadie")
    if a0 <= t < a1:
        d = 1 + min(4, int((t - a0) / 0.9))
        C.badge(ctx, "DÍA %d" % d, W / 2, BY, win(t, a0, a1), B, size=70)
        C.badge(ctx, "+%s S" % ("0,%06d" % (38 * d)).replace("0,0000", "0,0000"), W / 2, BY + 130, win(t, a0 + 0.3, a1), R, size=84)
    label(C, ctx, t, T("lo predijo"), T("si nadie"), "RELATIVIDAD", A, "ckE", dx=200, dy=-420, size=56)
    # desvío de 10 km
    a0, a1 = T("si nadie"), T("así que los relojes")
    if a0 <= t < a1:
        km = 10 * sg(t, T("tu mapa") - 0.3, T("tu mapa") + 2.4)
        C.badge(ctx, ("DESVÍO: %.1f KM" % km).replace(".", ","), W / 2, BY, win(t, a0, a1), R, size=74)
    # ajuste antes del lanzamiento
    a0, a1 = T("así que los relojes"), T("y todo esto")
    if a0 <= t < a1:
        C.badge(ctx, "10,23 MHZ", W / 2, BY, win(t, a0, a0 + 0.9), Y, size=74)
        C.badge(ctx, "10,22999999543 MHZ", W / 2, BY, win(t, a0 + 0.9, a1), G, size=64)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.4), (T("sin preguntar"), C.s_pop(), 0.45), (T("mira hacia"), C.s_whoosh(), 0.55),
         (T("veinte mil"), C.s_buzz(1.8), 0.2), (T("hay treinta"), C.s_whoosh(), 0.35), (T("cada uno"), C.s_whoosh(), 0.45),
         (T("esa señal") + 0.2, C.s_whoosh(0.9), 0.4), (T("tu móvil compara") - 0.3, C.s_thud(), 0.4), (T("calcula"), C.s_coin(), 0.4),
         (T("con un satélite") + 0.3, C.s_pop(), 0.45), (T("con dos"), C.s_pop(), 0.45), (T("con tres"), C.s_pop(), 0.45),
         (T("y uno de ellos") + 0.6, C.s_fail(), 0.4), (T("el reloj de tu"), C.s_whoosh(), 0.4), (T("así que usas"), C.s_whoosh(), 0.4),
         (T("cuarto") + 0.4, C.s_clank(), 0.45), (T("por eso"), C.s_win(), 0.4), (T("y la precisión"), C.s_whoosh(), 0.4),
         (T("son trescientos"), C.s_thud(), 0.5), (T("y aquí viene"), C.s_whoosh(), 0.45), (T("si nadie"), C.s_whoosh(), 0.4),
         (T("tu mapa"), C.s_fail(), 0.4), (T("así que los relojes"), C.s_whoosh(), 0.4), (T("así que los relojes") + 0.9, C.s_clank(), 0.45),
         (T("y todo esto"), C.s_whoosh(), 0.4), (T("sígueme"), C.s_pop(), 0.4)]
    a0 = T("los relojes de los")
    for d in range(5): E.append((a0 + 0.9 * d, C.s_pop(), 0.3))
    for i in range(6): E.append((T("y no para") + 0.6 * i, C.s_bleep(1200), 0.12))
    return E
