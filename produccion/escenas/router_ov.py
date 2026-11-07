# Capa 2D de «¿Tus antenas del router apuntan a tu cuarto?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("router")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"antenitas", "router", "habitación", "ondas", "radio", "dos", "coma", "cuatro", "gigahercios", "millones", "doce",
            "centímetros", "varilla", "lados", "punta", "donut", "agujero", "tumbado", "arriba", "inclina", "tumbada", "cinco", "seis",
            "paredes", "agua", "lenta", "centro", "mesa", "mueble", "tele", "microondas"}
BY = H * 0.265

def miles(v): return f"{int(round(v)):,}".replace(",", ".")
def s01(t, a, b): x = max(0.0, min(1.0, (t - a) / max(b - a, 1e-4))); return x * x * (3 - 2 * x)

def senal(C, ctx, x, y, pct, p, titulo):
    """barras de wifi + porcentaje junto a un móvil"""
    if p <= 0: return
    x = clampx(x, 200); y = clampy(y, 380, 1380)
    col = C.GREEN if pct >= 60 else (C.YL if pct >= 30 else C.RED)
    ctx.save()
    C.rrect(ctx, x - 150, y - 120, 300, 160, 24); ctx.set_source_rgba(0.04, 0.06, 0.12, 0.85 * p); ctx.fill()
    for k in range(4):
        on = pct >= 15 + 25 * k
        hh = 24 + 18 * k; ctx.rectangle(x - 120 + 30 * k, y - 20 - hh, 20, hh)
        ctx.set_source_rgba(*(col if on else (0.3, 0.32, 0.38)), p); ctx.fill()
    C.outlined(ctx, "%d %%" % int(pct), x + 60, y - 50, 54, fill=col, stroke=8, alpha=p, shadow=False)
    ctx.restore()
    C.outlined(ctx, titulo, x, y + 10, 40, fill=(1, 1, 1), stroke=6, alpha=p, shadow=False)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    label(C, ctx, t, 1.0, T("pues no"), "AL CUARTO", A, "router", dx=60, dy=240, size=58)
    badge(C, ctx, t, T("pues no"), T("vamos a ver") + 0.3, "✗ ASÍ NO", R, size=86)
    label(C, ctx, t, T("los datos"), T("en la banda"), "DATOS", A, "router", dx=0, dy=200, size=58)
    # 2,4 GHz y oscilaciones
    a0, a1 = T("en la banda"), T("cada onda")
    if a0 <= t < a1:
        v = 2.4 * s01(t, a0 + 0.3, T("gigahercios", fin=True))
        C.badge(ctx, ("%.1f GHz" % v).replace(".", ","), W / 2, BY, win(t, a0, a1), Y, size=96)
        if t > T("la señal oscila"):
            n = 2.4e9 * s01(t, T("la señal oscila"), T("por segundo", fin=True))
            C.badge(ctx, miles(n) + " / s", W / 2, BY + 150, win(t, T("la señal oscila"), a1), Y, size=66)
    a0, a1 = T("cada onda"), T("dentro de cada") - 0.2
    if a0 <= t < a1:
        v = 12.5 * s01(t, a0 + 0.3, T("medio", fin=True))
        C.badge(ctx, ("%.1f cm" % v).replace(".", ","), W / 2, BY, win(t, a0, a1), Y, size=96)
    label(C, ctx, t, T("una varilla"), T("pero no por"), "METAL", A, "rod", dx=-170, dy=0, size=58)
    a0, a1 = T("la corriente"), T("y suelta")
    if a0 <= t < a1:
        x, y = A("rod"); u = math.sin(t * 9); p = win(t, a0, a1); x = clampx(x + 150); y = clampy(y); d = -1 if u > 0 else 1
        ctx.save(); ctx.set_line_join(1)
        for lw, col in ((16, (0, 0, 0)), (0, Y)):
            ctx.move_to(x - 18, y - 50 * d); ctx.line_to(x + 18, y - 50 * d); ctx.line_to(x + 18, y + 10 * d); ctx.line_to(x + 45, y + 10 * d)
            ctx.line_to(x, y + 70 * d); ctx.line_to(x - 45, y + 10 * d); ctx.line_to(x - 18, y + 10 * d); ctx.close_path()
            ctx.set_source_rgba(*col, p)
            if lw: ctx.set_line_width(lw); ctx.stroke()
            else: ctx.fill()
        ctx.restore()
    label(C, ctx, t, T("pero no por"), T("la señal tiene"), "0 %", A, "tip", dx=0, dy=-110, size=80)
    label(C, ctx, t, T("con la antena"), T("por eso apuntarla"), "AGUJERO", A, "tip", dx=0, dy=-120, size=60)
    # apuntando al cuarto: la señal del cuarto cae
    a0, a1 = T("por eso apuntarla"), T("si las pones")
    if a0 <= t < a1:
        x, y = A("cuarto"); pct = 85 - 75 * s01(t, a0 + 0.4, a0 + 1.6)
        senal(C, ctx, x, y - 200, pct, win(t, a0 + 0.2, a1), "TU CUARTO")
    # de pie: planta baja bien, arriba en el agujero
    a0, a1 = T("si las pones") + 0.6, T("y aquí viene")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        x, y = A("salon"); senal(C, ctx, x + 40, y - 190, 92, p, "SALÓN")
        x, y = A("cuarto"); senal(C, ctx, x - 30, y - 190, 88, p, "CUARTO")
        x, y = A("arriba")
        pct = 90
        if t > T("pero el piso"): pct = 90 - 78 * s01(t, T("pero el piso") + 0.3, T("agujero", 2, fin=True))
        if t > T("inclina"): pct = mix(12, 76, s01(t, T("inclina") + 0.6, T("tumbada", fin=True)))
        senal(C, ctx, x, y - 200, pct, win(t, T("pero el piso") - 0.2, a1), "ARRIBA")
    # 5 GHz frente a 2,4 GHz
    a0, a1 = T("la banda de cinco"), T("pero sus ondas")
    if a0 <= t < a1: C.badge(ctx, "5 GHz", W / 2, BY, win(t, a0, a1), B, size=96)
    a0, a1 = T("pero sus ondas"), T("las paredes")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        x, y = A("ruler24"); C.outlined(ctx, "12,5 cm", clampx(x), clampy(y - 60), 60, fill=Y, stroke=9, alpha=p)
        x, y = A("ruler5"); C.outlined(ctx, "6 cm", clampx(x), clampy(y + 70), 60, fill=B, stroke=9, alpha=p)
    label(C, ctx, t, T("y tu cuerpo"), T("por eso", 2), "AGUA", A, "persona", dx=0, dy=-90, size=64)
    label(C, ctx, t, T("las paredes") + 0.3, T("y tu cuerpo"), "PARED", A, "pared", dx=40, dy=320, size=60)
    a0, a1 = T("las paredes") + 0.4, T("y dónde")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        a = s01(t, a0, a0 + 1.2)
        C.badge(ctx, "2,4 GHz: %d %%" % int(100 - 64 * a), W / 2, BY, p, Y, size=70)
        C.badge(ctx, "5 GHz: %d %%" % int(100 - 96 * a), W / 2, BY + 130, p, B, size=70)
    a0, a1 = T("el móvil se pasa"), T("y dónde")
    if a0 <= t < a1:
        C.badge(ctx, "MÓVIL: 2,4 GHz", W / 2, BY + 260, win(t, a0, a1), G, size=62)
    # dónde ponerlo
    badge(C, ctx, t, T("en el centro"), T("nunca dentro"), "✓ CENTRO", G, size=86)
    label(C, ctx, t, T("a la altura"), T("nunca dentro"), "~1 m", A, "router", dx=0, dy=200, size=70)
    badge(C, ctx, t, T("nunca dentro") + 0.3, T("ni detrás"), "✗ MUEBLE", R, size=86)
    badge(C, ctx, t, T("ni detrás") + 0.2, T("ni junto"), "✗ TELE", R, size=86)
    badge(C, ctx, t, T("ni junto") + 0.2, T("sígueme") + 0.4, "✗ MICROONDAS", R, size=80)

def mix(a, b, u): return a + (b - a) * u

def sfx_events(C):
    return [(0.0, C.s_whoosh(), 0.4), (0.4, C.s_clank(), 0.35), (1.6, C.s_clank(), 0.35), (T("pues no"), C.s_fail(), 0.5),
            (T("vamos a ver"), C.s_whoosh(), 0.4), (T("tu router convierte"), C.s_buzz(1.5), 0.25), (T("en la banda"), C.s_pop(), 0.45),
            (T("la señal oscila"), C.s_coin(), 0.35), (T("cada onda"), C.s_pop(), 0.45), (T("dentro de cada"), C.s_whoosh(), 0.4),
            (T("la corriente"), C.s_buzz(1.6), 0.3), (T("pero no por"), C.s_fail(), 0.4), (T("la señal tiene"), C.s_pop(), 0.5),
            (T("por eso apuntarla") + 0.4, C.s_clank(), 0.4), (T("por la punta casi"), C.s_fail(), 0.4), (T("si las pones"), C.s_whoosh(), 0.45),
            (T("y cubre"), C.s_win(), 0.35), (T("pero el piso"), C.s_fail(), 0.45), (T("inclina") + 0.4, C.s_clank(), 0.45),
            (T("tumbada"), C.s_win(), 0.35), (T("y aquí viene"), C.s_whoosh(), 0.4), (T("la banda de cinco"), C.s_pop(), 0.45),
            (T("pero sus ondas"), C.s_pop(), 0.4), (T("las paredes"), C.s_thud(), 0.5), (T("agua", 2), C.s_pop(), 0.4),
            (T("el móvil se pasa"), C.s_bleep(880), 0.3), (T("y dónde"), C.s_whoosh(), 0.4), (T("en el centro"), C.s_win(), 0.4),
            (T("nunca dentro") + 0.3, C.s_thud(), 0.5), (T("ni detrás") + 0.2, C.s_thud(), 0.5), (T("ni junto") + 0.2, C.s_fail(), 0.5),
            (T("sígueme"), C.s_whoosh(), 0.4)]
