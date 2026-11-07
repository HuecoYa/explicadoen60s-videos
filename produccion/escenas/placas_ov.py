# Capa 2D de «Así funcionan las placas solares en un apagón»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("placas")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"luz", "placas", "sol", "continua", "alterna", "doscientos", "treinta", "voltios", "cincuenta", "inversor", "ritmo",
            "cuarenta", "ocho", "uno", "dos", "segundos", "técnicos", "electrocutarle", "antiisla", "tres", "minutos", "baterías",
            "híbrido", "interruptor", "isla"}
BY = H * 0.265

def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def onda(C, ctx, x, y, w, h, t, p, tipo, col, titulo=None, fase=0.0):
    """mini osciloscopio: línea plana (continua) o seno que corre (alterna)"""
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(C.back(p) if C.back(p) > 1e-3 else 1e-3, C.back(p) if C.back(p) > 1e-3 else 1e-3)
    C.rrect(ctx, -w / 2, -h / 2, w, h, 22); ctx.set_source_rgba(0.04, 0.06, 0.12, 0.85 * p); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.5 * p); ctx.set_line_width(3); ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, 0.25 * p); ctx.move_to(-w / 2 + 16, 0); ctx.line_to(w / 2 - 16, 0); ctx.stroke()
    ctx.set_line_width(9); ctx.set_source_rgba(*col, p)
    for i in range(61):
        u = i / 60; xx = -w / 2 + 20 + u * (w - 40)
        if tipo == "cc": yy = -h * 0.28
        else: yy = -h * 0.36 * math.sin(u * math.tau * 2 - t * 6 + fase)
        (ctx.move_to if i == 0 else ctx.line_to)(xx, yy)
    ctx.stroke()
    if tipo == "cc":       # puntitos que avanzan siempre hacia la derecha
        for k in range(4):
            u = (k / 4 + t * 0.5) % 1.0; ctx.arc(-w / 2 + 20 + u * (w - 40), -h * 0.28, 10, 0, math.tau); ctx.fill()
    ctx.restore()
    if titulo: C.outlined(ctx, titulo, x, y + h / 2 + 50, 60, fill=(1, 1, 1), stroke=8, alpha=p, shadow=False)

def dial(C, ctx, x, y, r, hz, p):
    """medidor de frecuencia 46-54 Hz con la franja buena 48-51 en verde"""
    if p <= 0: return
    a = lambda v: math.pi + (v - 46) / 8 * math.pi
    ctx.save(); ctx.set_line_cap(1)
    C.rrect(ctx, x - r - 40, y - r - 40, 2 * r + 80, r + 140, 30); ctx.set_source_rgba(0.04, 0.06, 0.12, 0.85 * p); ctx.fill()
    for v0, v1, col in ((46, 48, C.RED), (48, 51, C.GREEN), (51, 54, C.RED)):
        ctx.set_line_width(34); ctx.set_source_rgba(*col, p); ctx.arc(x, y, r, a(v0) + 0.01, a(v1) - 0.01); ctx.stroke()
    for v in (48, 50, 51):
        ang = a(v); C.outlined(ctx, str(v), x + (r - 72) * math.cos(ang), y + (r - 72) * math.sin(ang), 40, alpha=p, shadow=False, stroke=6)
    ang = a(max(46, min(54, hz)))
    ctx.set_line_width(12); ctx.set_source_rgba(1, 1, 1, p); ctx.move_to(x, y); ctx.line_to(x + (r + 10) * math.cos(ang), y + (r + 10) * math.sin(ang)); ctx.stroke()
    ctx.arc(x, y, 18, 0, math.tau); ctx.fill()
    ok = 48 <= hz <= 51
    C.outlined(ctx, ("%.1f Hz" % hz).replace(".", ","), x, y + 70, 64, fill=C.GREEN if ok else C.RED, stroke=10, alpha=p)
    ctx.restore()

def cuenta(C, ctx, x, y, txt, frac, col, p, w=520):
    if p <= 0: return
    C.badge(ctx, txt, x, y, p, col, size=84)
    C.rrect(ctx, x - w / 2, y + 70, w, 26, 13); ctx.set_source_rgba(0.1, 0.12, 0.18, 0.85 * p); ctx.fill()
    if frac > 0.01:
        C.rrect(ctx, x - w / 2, y + 70, w * frac, 26, 13); ctx.set_source_rgba(*col, p); ctx.fill()

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    # la casa se queda a cero
    a0, a1 = 1.7, T("mira dentro")
    if a0 <= t < a1:
        v = 2400 * (1 - seg01(t, 2.3, 3.4)); C.badge(ctx, "CASA: %s W" % miles(v), W / 2, BY, win(t, a0, a1), Y if v > 10 else R, size=78)
    label(C, ctx, t, T("aunque haga") , T("mira dentro"), "PLACAS", A, "panel", dy=-150, size=60)
    # continua / alterna
    p = win(t, T("da corriente") - 0.2, T("así que en medio"))
    if p: onda(C, ctx, W * 0.3, H * 0.66, 380, 170, t, p, "cc", Y)
    p = win(t, T("tus enchufes"), T("así que en medio"))
    if p: onda(C, ctx, W * 0.68, H * 0.66, 380, 170, t, p, "ca", (0.45, 0.75, 1.0))
    a0, a1 = T("doscientos"), T("que cambia")
    if a0 - 0.2 <= t < a1: C.badge(ctx, "%d V" % int(230 * seg01(t, a0 - 0.2, a0 + 0.9)), W / 2, BY, win(t, a0 - 0.2, a1), Y, size=100)
    a0, a1 = T("cincuenta"), T("así que en medio")
    if a0 - 0.3 <= t < a1: C.badge(ctx, "%d Hz" % int(50 * seg01(t, a0 - 0.3, a0 + 0.9)), W / 2, BY, win(t, a0 - 0.3, a1), Y, size=100)
    label(C, ctx, t, T("el inversor") , T("pero para hacerlo"), "INVERSOR", A, "inv", dy=-120, size=64)
    p = win(t, T("convierte"), T("pero para hacerlo"))
    if p:
        onda(C, ctx, W * 0.29, H * 0.66, 340, 150, t, p, "cc", Y); onda(C, ctx, W * 0.67, H * 0.66, 340, 150, t, p, "ca", (0.45, 0.75, 1.0))
        C.outlined(ctx, "→", W * 0.48, H * 0.66, 90, alpha=p)
    # copia el ritmo
    p = win(t, T("copia el ritmo") - 0.2, T("vigila"))
    if p:
        onda(C, ctx, W / 2, H * 0.5, 560, 170, t, p, "ca", (0.45, 0.75, 1.0), "RED")
        onda(C, ctx, W / 2, H * 0.5 + 280, 560, 170, t, p * seg01(t, T("copia") + 0.3, T("copia") + 0.6), "ca", Y, "INVERSOR")
    # medidor de frecuencia
    a0, a1 = T("vigila"), T("y aquí viene")
    if a0 <= t < a1:
        hz = 50 + 0.15 * math.sin(t * 5)
        hz = mix(hz, 47.6, seg01(t, T("baja de") , T("cuarenta y ocho", fin=True) + 0.3))
        hz = mix(hz, 51.4, seg01(t, T("o pasa"), T("cincuenta y uno", fin=True)))
        hz = mix(hz, 47.6, seg01(t, T("algo va"), T("algo va") + 0.2) * 0)
        dial(C, ctx, W / 2, H * 0.6, 230, hz, win(t, a0, a1))
    # se va la luz: relé y 2 s
    a0, a1 = T("si se va"), T("aunque tus placas")
    badge(C, ctx, t, a0, T("se desconecta"), "RED: 0 V", R, size=86)
    if T("se desconecta") <= t < a1:
        u = seg01(t, T("se desconecta"), T("dos segundos", fin=True))
        cuenta(C, ctx, W / 2, BY, ("%.1f s" % (2 * (1 - u))).replace(".", ","), 1 - u, Y if u < 1 else R, win(t, T("se desconecta"), a1))
    label(C, ctx, t, T("se desconecta") + 0.3, T("aunque tus placas"), "RELÉ", A, "rele", dx=60, dy=150, size=60)
    a0, a1 = T("aunque tus placas"), T("por los técnicos")
    if a0 <= t < a1:
        v = 2900 + 60 * math.sin(t * 3); C.badge(ctx, "PLACAS: %s W" % miles(v), W / 2, BY, win(t, a0, a1), Y, size=74)
    # técnico
    label(C, ctx, t, T("cuando hay") , T("si tu tejado"), "AVERÍA", A, "linea", dx=-60, dy=170, size=60)
    a0, a1 = T("si tu tejado"), T("a esto se")
    if a0 <= t < a1:
        v = 230 * seg01(t, T("ese cable"), T("tensión", fin=True))
        C.badge(ctx, "CABLE: %d V" % int(v), W / 2, BY, win(t, a0 + 0.4, a1), R if v > 20 else Y, size=84)
    a0, a1 = T("a esto se"), T("cuando vuelve")
    if a0 <= t < a1:
        C.badge(ctx, "✓ CABLE: 0 V", W / 2, BY, win(t, a0, a1), G, size=84)
    # vuelve la luz: 3 minutos
    badge(C, ctx, t, T("cuando vuelve"), T("espera"), "RED: 230 V", G, size=86)
    a0, a1 = T("espera"), T("y si quieres")
    if a0 <= t < a1:
        u = seg01(t, a0 + 0.2, T("reconectarse", fin=True) - 0.2); s = int(round(180 * (1 - u)))
        cuenta(C, ctx, W / 2, BY, "%d:%02d" % (s // 60, s % 60), 1 - u, Y if s else G, win(t, a0, a1))
    # apagón con batería
    badge(C, ctx, t, T("y si quieres"), T("necesitas") + 0.3, "RED: 0 V", R, size=86)
    label(C, ctx, t, T("baterías") , T("con un interruptor"), "BATERÍA", A, "bat", dy=-150, size=60)
    label(C, ctx, t, T("inversor híbrido"), T("con un interruptor"), "HÍBRIDO", A, "inv", dy=-120, size=60)
    label(C, ctx, t, T("con un interruptor") + 0.3, T("así tu casa"), "ABIERTO", A, "sw", dy=-140, size=60)
    a0, a1 = T("así tu casa"), DUR + 1
    if a0 <= t < a1:
        v = 100 - 3 * seg01(t, a0, DUR); C.badge(ctx, "BATERÍA %d %%" % int(v), W / 2, BY, win(t, a0, a1), G, size=78)

def seg01(t, a, b):
    x = max(0.0, min(1.0, (t - a) / max(b - a, 1e-4))); return x * x * (3 - 2 * x)
def mix(a, b, u): return a + (b - a) * u

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.4), (1.3, C.s_thud(), 0.6), (2.4, C.s_fail(), 0.4), (T("mira dentro"), C.s_whoosh(), 0.45),
         (T("da corriente"), C.s_pop(), 0.4), (T("tus enchufes"), C.s_buzz(1.2), 0.3), (T("doscientos"), C.s_pop(), 0.45),
         (T("cincuenta"), C.s_pop(), 0.4), (T("el inversor"), C.s_clank(), 0.45), (T("copia el ritmo"), C.s_whoosh(), 0.35),
         (T("vigila"), C.s_pop(), 0.4), (T("baja de") + 0.4, C.s_fail(), 0.4), (T("o pasa") + 0.4, C.s_fail(), 0.4),
         (T("si se va"), C.s_thud(), 0.55), (T("se desconecta"), C.s_clank(), 0.6), (T("aunque tus placas"), C.s_pop(), 0.4),
         (T("por los técnicos"), C.s_whoosh(), 0.4), (T("ese cable"), C.s_buzz(1.6), 0.45), (T("electrocutarle"), C.s_fail(), 0.5),
         (T("a esto se"), C.s_win(), 0.4), (T("cuando vuelve"), C.s_pop(), 0.45), (T("reconectarse"), C.s_clank(), 0.55),
         (T("y si quieres"), C.s_thud(), 0.5), (T("baterías"), C.s_pop(), 0.45), (T("con un interruptor") + 0.2, C.s_clank(), 0.55),
         (T("así tu casa"), C.s_whoosh(), 0.45), (T("isla"), C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
