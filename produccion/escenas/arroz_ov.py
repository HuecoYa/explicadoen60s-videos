# Capa 2D de «¿Se te ha mojado el móvil? El arroz no hace lo que crees»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("arroz")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"agua", "arroz", "juntas", "goma", "puerto", "pines", "sales", "electricidad", "corriente", "corroe", "avisa",
            "veinticuatro", "menos", "aire", "carcasa", "polvo", "golpecitos", "ventilado", "media", "día", "secador", "bastoncillos"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((26, (0, 0, 0)), (16, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.arc(x, y, r, 0, math.tau); ctx.stroke()
        ctx.move_to(x - r * 0.7, y - r * 0.7); ctx.line_to(x + r * 0.7, y + r * 0.7); ctx.stroke()
    ctx.restore()

def gauge(ctx, C, cx, cy, v, p):
    """medidor de corriente entre pines: 0 = seco (verde), 1 = agua (rojo)"""
    if p <= 0: return
    R = 150
    ctx.save(); ctx.translate(cx, cy); s = C.back(p); ctx.scale(s, s)
    C.rrect(ctx, -R - 40, -R - 40, 2 * R + 80, R + 110, 30); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92); ctx.fill()
    for a0, a1, col in ((math.pi, math.pi * 1.55, C.GREEN), (math.pi * 1.55, math.pi * 1.7, C.YL), (math.pi * 1.7, math.pi * 2, C.RED)):
        ctx.set_line_width(30); ctx.set_source_rgb(*col); ctx.arc(0, 0, R - 15, a0, a1); ctx.stroke()
    a = math.pi + math.pi * v
    ctx.set_line_width(12); ctx.set_line_cap(1); ctx.set_source_rgb(1, 1, 1)
    ctx.move_to(0, 0); ctx.line_to((R - 30) * math.cos(a), (R - 30) * math.sin(a)); ctx.stroke()
    ctx.arc(0, 0, 16, 0, math.tau); ctx.fill()
    ctx.restore()
    C.outlined(ctx, "SECO", cx - 120, cy + 45, 38, fill=C.GREEN, stroke=6, alpha=p, shadow=False)
    C.outlined(ctx, "AGUA", cx + 120, cy + 45, 38, fill=C.RED, stroke=6, alpha=p, shadow=False)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # «meterlo en arroz»: tachado sobre el cuenco
    p = win(t, T("meterlo en") + 0.5, T("mira dentro") + 0.2)
    if p: cross(ctx, W / 2, H * 0.5, 170, p)
    # juntas
    label(C, ctx, t, T("de goma") - 0.1, T("los botones"), "JUNTA", A, "gask", dx=-60, dy=-140, size=60)
    label(C, ctx, t, T("los botones") + 0.3, T("y la tapa"), "JUNTA", A, "btn", dx=40, dy=-150, size=60)
    label(C, ctx, t, T("y la tapa") + 0.2, T("por eso aguanta"), "TAPA", A, "back", dx=-40, dy=-120, size=60)
    # puerto
    label(C, ctx, t, T("el puerto de") + 0.2, T("ahí dentro"), "PUERTO", A, "port", dx=0, dy=170, size=62)
    label(C, ctx, t, T("unos pines") , T("el agua del grifo"), "PINES", A, "pins", dx=-200, dy=-260, size=62)
    label(C, ctx, t, T("lleva sales"), T("si enchufas"), "SALES", A, "ions", dx=200, dy=-260, size=62)
    a0, a1 = T("la corriente salta"), T("por eso tu móvil")
    if a0 - 0.6 <= t < a1:
        C.badge(ctx, "5 V", W / 2, BY, win(t, a0 - 0.6, a1), Y, size=90)
    label(C, ctx, t, T("y eso corroe") + 0.4, T("por eso tu móvil"), "ÓXIDO", A, "pins", dx=200, dy=-240, size=62)
    # medidor de corriente entre pines
    a0, a1 = T("por eso tu móvil mide"), T("y el arroz")
    if a0 <= t < a1:
        v = 0.12 + 0.8 * sg(t, T("entre los pines"), T("si detecta", fin=True) + 0.4) + 0.03 * math.sin(t * 20)
        gauge(ctx, C, W / 2, H * 0.64, v, win(t, a0, a1))
    # prueba de 24 h
    a0, a1 = T("en una prueba"), T("el arroz solo toca")
    if a0 <= t < a1:
        h = 24 * sg(t, a0 + 0.6, T("el arroz crudo") + 0.3)
        C.badge(ctx, "%d h" % round(h), W / 2, BY, win(t, a0, a1), B, size=96)
        for k, nm in enumerate(("GEL", "CUSCÚS", "AIRE", "ARROZ")):
            x, y = A("bar%d" % k)
            col = R if k == 3 else (1, 1, 1)
            pp = win(t, a0 + 0.3 + 0.15 * k, a1)
            if pp: C.outlined(ctx, nm, x, y + 50, 44, fill=col, stroke=8, alpha=pp, scale=C.back(pp), shadow=False)
        p = win(t, T("el arroz crudo") + 0.4, a1)
        if p: x, y = A("bartop3"); cross(ctx, x, y - 90, 60, p)
    # el arroz y la carcasa
    label(C, ctx, t, T("el arroz solo toca") + 0.6, T("el agua del puerto"), "SECA", A, "case", dx=40, dy=-170, size=62)
    a0, a1 = T("el agua del puerto"), T("y encima")
    if a0 <= t < a1:
        C.badge(ctx, "AGUA: 100 %", W / 2, BY, win(t, a0, a1), B, size=80)
    label(C, ctx, t, T("el polvo") , T("entonces"), "POLVO", A, "port", dx=0, dy=-260, size=62)
    # qué hacer
    a0, a1 = T("espera al menos"), T("nada de secador")
    if a0 <= t < a1:
        t_dia = T("y hasta un día")
        if t < t_dia:
            m = 30 * sg(t, a0 + 0.3, T("media hora", fin=True) + 0.3)
            C.badge(ctx, "%d MIN" % round(m), W / 2, BY, win(t, a0, a1), Y, size=96)
        else:
            h = 0.5 + 23.5 * sg(t, t_dia, T("un día entero", fin=True) + 0.2)
            C.badge(ctx, ("%d h" % round(h)) if h >= 1 else "30 MIN", W / 2, BY, win(t, a0, a1), Y, size=96)
    p = win(t, T("nada de secador") + 0.3, T("sígueme") + 0.3)
    if p:
        for k in ("dryer", "swab"):
            x, y = A(k); cross(ctx, clampx(x, 170), clampy(y, 400, 1400), 130, p)

def sfx_events(C):
    E = [(0.45, C.s_thud(), 0.6), (0.5, C.s_whoosh(), 0.5), (T("meterlo en") + 0.3, C.s_whoosh(), 0.4), (T("meterlo en") + 0.7, C.s_fail(), 0.35),
         (T("mira dentro"), C.s_whoosh(), 0.45), (T("la pantalla"), C.s_pop(), 0.4), (T("los botones"), C.s_pop(), 0.4),
         (T("y la tapa"), C.s_pop(), 0.4), (T("por eso aguanta"), C.s_clank(), 0.5), (T("pero hay un sitio"), C.s_whoosh(), 0.4),
         (T("lleva sales"), C.s_pop(), 0.35), (T("si enchufas") + 0.9, C.s_clank(), 0.5), (T("la corriente salta"), C.s_buzz(1.8), 0.35),
         (T("y eso corroe"), C.s_fail(), 0.3), (T("si detecta"), C.s_bleep(880), 0.6), (T("te avisa"), C.s_fail(), 0.45),
         (T("y el arroz"), C.s_whoosh(), 0.45), (T("en una prueba") + 1.0, C.s_whoosh(), 0.35), (T("el arroz crudo") + 0.4, C.s_fail(), 0.45),
         (T("el arroz solo toca"), C.s_whoosh(), 0.4), (T("el polvo"), C.s_pop(), 0.35), (T("entonces"), C.s_whoosh(), 0.45),
         (T("sécalo"), C.s_whoosh(), 0.4), (T("déjalo en"), C.s_whoosh(), 0.35), (T("espera al menos"), C.s_coin(), 0.35),
         (T("nada de secador") + 0.3, C.s_fail(), 0.45), (T("sígueme"), C.s_win(), 0.4)]
    for k in range(4): E.append((T("dale golpecitos") + 0.45 * k, C.s_thud(), 0.35))
    return E
