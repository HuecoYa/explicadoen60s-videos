# Capa 2D de «Si tuvieras que inventar la bombilla»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("bombilla")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"bombilla", "hilo", "corriente", "brilla", "quema", "ampolla", "oxígeno", "noventa", "calor", "diez", "luz", "chip",
            "led", "electrones", "azul", "fósforo", "amarillo", "rojo", "blanco", "tensión", "sentido", "voltios", "circuito",
            "disipador", "aluminio", "veinticinco"}

def barra(ctx, x, y, w, h, frac, col, a, txt, C):
    ctx.save(); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.9 * a); C.rrect(ctx, x - 12, y - 12, w + 24, h + 24, 18); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.15 * a); C.rrect(ctx, x, y, w, h, 10); ctx.fill()
    if frac > 0.002: ctx.set_source_rgba(*col, a); C.rrect(ctx, x, y, max(w * frac, 20), h, 10); ctx.fill()
    ctx.restore()
    C.outlined(ctx, txt, x + w / 2, y + h / 2, 46, fill=(1, 1, 1), stroke=8, alpha=a, shadow=False)

def onda(ctx, x0, y0, w, amp, a, col, ac=True, t=0):
    ctx.save(); ctx.set_line_width(9); ctx.set_source_rgba(*col, a); ctx.set_line_cap(1)
    for k in range(0, 101):
        u = k / 100; x = x0 + w * u
        y = y0 - amp * math.sin(2 * math.pi * (2 * u - t * 1.5)) if ac else y0 - amp
        (ctx.move_to if k == 0 else ctx.line_to)(x, y)
    ctx.stroke(); ctx.set_source_rgba(1, 1, 1, 0.35 * a); ctx.set_line_width(3); ctx.move_to(x0, y0); ctx.line_to(x0 + w, y0); ctx.stroke(); ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    label(C, ctx, t, T("un hilo"), T("le pasas"), "HILO", A, "hilo", dy=-150, size=64)
    # temperatura del hilo
    a0 = T("le pasas")
    p = win(t, a0 + 0.2, T("así que lo metes"))
    if p:
        v = 20 + 2480 * min(1, max(0, (t - a0 - 0.3) / 1.5)) if t < T("se quema") + 0.3 else 2500
        C.badge(ctx, "%d °C" % round(v, -1 if v > 100 else 0), W / 2, H * 0.265, p, R if v > 1000 else Y, size=90)
    label(C, ctx, t, T("pero en el aire"), T("se quema") + 0.3, "OXÍGENO", A, "o2", dx=40, dy=-60, size=58)
    p = win(t, T("se quema") + 0.4, T("así que lo metes"))
    if p: C.outlined(ctx, "¡ROTO!", W / 2, H * 0.4, 110, fill=R, stroke=14, italic=True, scale=C.back(p), rot=-0.08, alpha=p)
    # oxígeno dentro de la ampolla
    a0 = T("así que lo metes"); p = win(t, a0 + 0.6, T("es la bombilla"))
    if p:
        v = 21 * (1 - min(1, max(0, (t - a0 - 1.0) / 1.4)))
        C.badge(ctx, "OXÍGENO %d%%" % round(v), W / 2, H * 0.265 + 120, p, G if v < 1 else Y, size=72)
    label(C, ctx, t, T("en una ampolla"), T("funciona"), "AMPOLLA", A, "amp", dy=-60, size=60)
    # 100 → 90 calor + 10 luz
    a0 = T("de cada cien")
    if a0 <= t < T("así que cambias"):
        p = win(t, a0, T("así que cambias"))
        x, w, h = 160, 760, 74; y0 = H * 0.22
        barra(ctx, x, y0, w, h, 1.0, Y, p, "ENERGÍA 100", C)
        if t >= T("noventa"): barra(ctx, x, y0 + 115, w, h, 0.9 * min(1, (t - T("noventa")) / 0.6), R, win(t, T("noventa"), T("así que cambias")), "CALOR 90", C)
        if t >= T("solo diez"): barra(ctx, x, y0 + 230, w, h, 0.1 * min(1, (t - T("solo diez")) / 0.4), (1, 0.9, 0.4), win(t, T("solo diez"), T("así que cambias")), "LUZ 10", C)
    label(C, ctx, t, T("un led"), T("aquí la luz"), "LED", A, "chip", dy=-150, size=72)
    label(C, ctx, t, T("al saltar"), T("cada salto"), "N", A, "capN", dx=-130, dy=-40, size=60)
    label(C, ctx, t, T("al saltar"), T("cada salto"), "P", A, "capP", dx=-130, dy=70, size=60)
    a0 = T("cada salto")
    if a0 <= t < T("así que lo cubres"):
        n = int(max(0, t - a0) * 37)
        C.badge(ctx, "%d FOTONES" % n, W / 2, H * 0.265, win(t, a0, T("así que lo cubres")), B, size=74)
    label(C, ctx, t, T("el fósforo") - 0.2, T("y todo mezclado"), "FÓSFORO", A, "fos", dy=-140, size=62)
    # tensión: lo que quiere el LED y lo que hay en casa
    a0 = T("pero el led quiere")
    if a0 <= t < T("así que en la base") + 0.5:
        p = win(t, a0, T("así que en la base") + 0.5)
        x0, w = 150, 780; y = H * 0.25
        C.outlined(ctx, "LED: 3 V", x0 + 150, y - 50, 60, fill=G, stroke=8, alpha=p, shadow=False)
        onda(ctx, x0, y + 70, w, 40, p, G, ac=False)
        if t >= T("y en casa"):
            p2 = win(t, T("y en casa"), T("así que en la base") + 0.5)
            C.outlined(ctx, "CASA: 230 V", x0 + 200, y + 170, 60, fill=R, stroke=8, alpha=p2, shadow=False)
            onda(ctx, x0, y + 330, w, 110, p2, R, ac=True, t=t)
    label(C, ctx, t, T("un pequeño circuito"), T("por último"), "CIRCUITO", A, "base", dx=120, dy=-90, size=58)
    label(C, ctx, t, T("un disipador") , T("resultado"), "DISIPADOR", A, "aletas", dx=40, dy=-160, size=58)
    p = win(t, T("el chip se estropea"), T("un disipador"))
    if p: C.badge(ctx, "✗ CHIP CALIENTE", W / 2, H * 0.265, p, R, size=70)
    # resultado
    a0 = T("gasta hasta")
    if a0 <= t:
        p = win(t, a0, DUR + 1); x, w, h = 160, 760, 70; y0 = H * 0.2
        u = min(1, (t - a0) / 1.2)
        barra(ctx, x, y0, w, h, 1.0, R, p, "CLÁSICA: 100", C)
        barra(ctx, x, y0 + 105, w, h, 1 - 0.9 * u, G, p, "LED: %d" % round(100 - 90 * u), C)
        if t >= T("y dura hasta"):
            n = min(25, int(1 + (t - T("y dura hasta")) * 18))
            C.badge(ctx, "DURA ×%d" % n, W / 2, y0 + 270, win(t, T("y dura hasta"), DUR + 1), Y, size=90)

def sfx_events(C):
    E = [(0.0, C.s_buzz(3.6), 0.5), (3.5, C.s_whoosh(), 0.5), (T("un hilo"), C.s_pop(), 0.5), (T("le pasas"), C.s_buzz(2.0), 0.5),
         (T("se quema") + 0.3, C.s_fail(), 0.6), (T("así que lo metes"), C.s_whoosh(), 0.5), (T("funciona"), C.s_win(), 0.4),
         (T("noventa"), C.s_pop(), 0.5), (T("solo diez"), C.s_pop(), 0.5), (T("un led"), C.s_pop(), 0.5), (T("aquí la luz"), C.s_whoosh(), 0.5),
         (T("el fósforo"), C.s_pop(), 0.5), (T("lo ves blanco"), C.s_win(), 0.4), (T("y en casa"), C.s_buzz(1.5), 0.5),
         (T("así que en la base"), C.s_whoosh(), 0.5), (T("el chip se estropea"), C.s_fail(), 0.5), (T("un disipador"), C.s_clank(), 0.5),
         (T("gasta hasta"), C.s_pop(), 0.5), (T("y dura hasta"), C.s_win(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
