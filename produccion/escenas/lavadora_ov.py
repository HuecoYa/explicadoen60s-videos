# Capa 2D de «Si tuvieras que inventar la lavadora…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("lavadora")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"centrifugar", "mil", "doscientas", "minuto", "andando", "frotar", "tambor", "paletas", "caer", "golpe", "empapada",
            "rápido", "agujeros", "disparada", "pared", "cuatrocientas", "problema", "vibrar", "muelles", "amortiguadores",
            "hormigón", "veinticinco", "kilos", "menos", "moverla", "amontonada", "despacio", "repartirla", "lento", "no"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def gauge(C, ctx, t, a, b, frac, col, title):
    p = win(t, a, b)
    if not p: return
    w, h = 620, 46; x0 = W / 2 - w / 2; y0 = H * 0.265 + 70
    ctx.save()
    C.rrect(ctx, x0 - 14, y0 - 14, w + 28, h + 28, 22); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92 * p); ctx.fill()
    C.rrect(ctx, x0, y0, max(h, w * frac), h, 16); ctx.set_source_rgba(*col, p); ctx.fill()
    ctx.restore()
    C.badge(ctx, title, W / 2, H * 0.265 - 20, p, col, size=52)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # revoluciones del gancho
    a0, a1 = 0.0, T("vamos a inventarla")
    if t < a1:
        v = 1200 * sg(t, 0.2, T("minuto", fin=True))
        C.badge(ctx, miles(v) + " RPM", W / 2, BY, win(t, -1, a1), Y, size=84)
    label(C, ctx, t, T("unas paletas") + 0.2, T("y la dejan"), "PALETA", A, "top", dy=-120, size=64)
    a0, a1 = T("pero la ropa"), T("así que haces")
    if a0 <= t < a1: C.badge(ctx, "AGUA 100 %", W / 2, BY, win(t, a0, a1), B, size=78)
    a0, a1 = T("así que haces"), T("pero hay un")
    if a0 <= t < a1:
        v = 50 + 1150 * sg(t, a0 + 0.3, T("el tambor tiene"))
        C.badge(ctx, miles(v) + " RPM", W / 2, BY, win(t, a0, a1), Y, size=84)
    label(C, ctx, t, T("el tambor tiene") + 0.2, T("el agua sale") + 0.5, "AGUJEROS", A, "hole", dx=40, dy=90, size=64)
    a0, a1 = T("a mil doscientas"), T("pero hay un")
    if a0 <= t < a1:
        v = 1 + 399 * sg(t, T("la ropa pesa"), T("cuatrocientas", fin=True))
        C.badge(ctx, "× %d" % round(v), W / 2, BY + 130, win(t, T("la ropa pesa") - 0.2, a1), R, size=96)
    # vibración
    def vib(t):
        a = 0.45 * sg(t, T("la ropa nunca"), T("y todo empieza") + 0.4) * (1 - sg(t, T("así que cuelgas"), T("como un coche")) * 0.4)
        a *= 1 - 0.85 * sg(t, T("ese peso"), T("se mueva mucho", fin=True))
        a += 0.38 * sg(t, T("si la ropa está"), T("amontonada", fin=True)) * (1 - sg(t, T("el motor gira"), T("para repartirla")))
        return a / 0.45
    for a0, a1 in ((T("un lado pesa"), T("así que cuelgas")), (T("ese peso"), T("por eso cuesta")), (T("si la ropa está"), T("si no lo consigue"))):
        if a0 <= t < a1:
            f = min(1.0, vib(t)); col = R if f > 0.5 else (Y if f > 0.25 else G)
            gauge(C, ctx, t, a0, a1, f, col, "VIBRACIÓN")
    label(C, ctx, t, T("de muelles") + 0.1, T("y aquí viene"), "MUELLE", A, "spring", dx=-40, dy=-110, size=58)
    label(C, ctx, t, T("amortiguadores") + 0.2, T("y aquí viene"), "AMORTIGUADOR", A, "damp", dx=60, dy=150, size=52)
    a0, a1 = T("tu lavadora lleva"), T("ese peso")
    if a0 <= t < a1:
        v = 25 * sg(t, T("pueden pesar"), T("kilos", fin=True))
        if t >= T("pueden pesar"): C.badge(ctx, "%d KG" % round(v), W / 2, BY, win(t, T("pueden pesar"), a1), Y, size=90)
    label(C, ctx, t, T("hormigón", fin=True) - 0.2, T("ese peso"), "HORMIGÓN", A, "conc2", dy=170, size=62)
    a0, a1 = T("el motor gira"), T("si no lo consigue")
    if a0 <= t < a1:
        s = "◀  ▶"
        d = math.cos((t - T("así que antes")) * 2.4)
        C.badge(ctx, ("IZQUIERDA" if d > 0 else "DERECHA"), W / 2, BY + 150, win(t, a0, a1), B, size=64)
    a0, a1 = T("si no lo consigue"), T("sígueme")
    if a0 <= t < a1:
        v = 1200 - 400 * sg(t, T("centrifuga más"), T("lento", fin=True)) - 800 * sg(t, T("o no centrifuga"), T("o no centrifuga") + 0.8)
        C.badge(ctx, miles(v) + " RPM", W / 2, BY, win(t, a0, a1), R if v < 1150 else Y, size=84)

def sfx_events(C):
    E = [(0.0, C.s_buzz(4.6), 0.35), (T("y por qué"), C.s_buzz(1.5), 0.3), (T("vamos a inventarla"), C.s_whoosh(), 0.5),
         (T("así que la metes"), C.s_whoosh(), 0.4), (T("con agua"), C.s_whoosh(0.9), 0.3), (T("y la dejan") + 0.3, C.s_thud(), 0.5),
         (T("ese golpe"), C.s_thud(), 0.55), (T("así que haces"), C.s_buzz(2.0), 0.3), (T("el agua sale"), C.s_whoosh(), 0.45),
         (T("cuatrocientas"), C.s_coin(), 0.45), (T("pero hay un"), C.s_fail(), 0.4), (T("y todo empieza"), C.s_buzz(1.2), 0.35),
         (T("de muelles"), C.s_clank(), 0.5), (T("amortiguadores"), C.s_clank(), 0.5), (T("hormigón") + 0.2, C.s_thud(), 0.7),
         (T("kilos"), C.s_coin(), 0.4), (T("ese peso"), C.s_win(), 0.35), (T("por eso cuesta"), C.s_thud(), 0.5),
         (T("si la ropa está"), C.s_buzz(1.6), 0.3), (T("ni el hormigón"), C.s_fail(), 0.4), (T("el motor gira"), C.s_whoosh(), 0.35),
         (T("para repartirla"), C.s_win(), 0.35), (T("centrifuga más"), C.s_fail(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(3): E.append((T("al girar") + 0.9 + 1.8 * k, C.s_thud(), 0.35))
    return E
