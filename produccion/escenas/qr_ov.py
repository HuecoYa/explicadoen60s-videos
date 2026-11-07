# Capa 2D de «Si tuvieras que inventar el código QR…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("qr")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"qr", "segundo", "cuadraditos", "enlace", "cuadrícula", "negro", "uno", "blanco", "cero", "veintiuno", "problema",
            "torcido", "tres", "esquinas", "girado", "cuarta", "blanca", "patrón", "repartidos", "romper", "leyendo", "sobra",
            "treinta", "dibujo", "cuatro", "ciento", "setenta", "siete", "noventa", "japonesa", "coche"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # cronómetro de lectura
    a0, a1 = T("y en menos"), T("cómo lee")
    if a0 <= t < a1:
        v = 0.31 * sg(t, a0, T("segundo", fin=True))
        C.badge(ctx, ("%.2f s" % v).replace(".", ","), W / 2, BY, win(t, a0, a1), G if v > 0.3 else (1, 1, 1), size=84)
    label(C, ctx, t, T("cuadrado negro") + 0.2, T("blanco"), "1", A, "t1", dy=-170, size=110)
    label(C, ctx, t, T("blanco"), T("la más pequeña"), "0", A, "t0", dy=-170, size=110)
    # 21 × 21
    a0, a1 = T("la más pequeña"), T("pero hay un")
    if a0 <= t < a1:
        n = max(1, int(round(21 * sg(t, a0 + 0.2, T("por veintiuno", fin=True)))))
        C.badge(ctx, "%d × %d" % (n, n), W / 2, BY, win(t, a0, a1), Y, size=90)
        xl, yl = A("tl"); xr, _ = A("tr")
        C.arrow_dim(ctx, xl - 12, xr + 12, yl - 60, Y, sg(t, a0 + 0.2, a0 + 1.2))
    # ángulo
    a0, a1 = T("tu móvil no sabe"), T("y como falta")
    if a0 <= t < a1:
        ang = 25 * sg(t, T("ni si está") - 0.4, T("ni si está") + 0.4) * (1 - sg(t, T("al verlos") + 0.6, T("cómo está girado")))
        ok = t > T("cómo está girado")
        C.badge(ctx, ("✓ " if ok else "") + "%d°" % round(ang), W / 2, BY, win(t, T("ni si está") - 0.3, a1), G if ok else R, size=84)
    for k, key in enumerate(("f1", "f2", "f3")):
        label(C, ctx, t, T("así que pones") + 0.5 + 0.35 * k, T("al verlos"), str(k + 1), A, key, dy=-150, size=100)
    label(C, ctx, t, T("y como falta") + 0.3, T("pero ahora tienes"), "?", A, "br", dy=-170, size=120)
    # blancos seguidos
    a0, a1 = T("el móvil se pierde"), T("así que lo mezclas")
    if a0 <= t < a1:
        k = int((t - a0) / 0.25) + 1
        s = ("✗ ¿%d?" % k) if k > 7 else str(k)
        C.badge(ctx, s, W / 2, BY, win(t, a0, a1), R if k > 7 else Y, size=90)
    a0, a1 = T("así que lo mezclas"), T("y aquí viene")
    if a0 <= t < a1: C.badge(ctx, "MÁSCARA", W / 2, BY, win(t, a0 + 0.3, a1), B, size=78)
    label(C, ctx, t, T("puedes romper") + 0.8, T("y se sigue"), "ROTO", A, "chunk", dy=-200, size=80)
    a0, a1 = T("y se sigue"), T("porque guardas")
    if a0 <= t < a1: C.badge(ctx, "✓ LEÍDO", W / 2, BY, win(t, a0, a1), G, size=84)
    a0, a1 = T("porque guardas"), T("en el nivel")
    if a0 <= t < a1: C.badge(ctx, "CORRECCIÓN DE ERRORES", W / 2, BY, win(t, a0 + 0.3, a1), B, size=58)
    # daño hasta 30 %
    a0, a1 = T("en el nivel"), T("por eso algunos") + 0.3
    if a0 <= t < a1:
        v = 30 * sg(t, T("se recupera") - 0.2, T("datos", fin=True))
        C.badge(ctx, ("✓ " if v > 29.5 else "") + "DAÑO %d %%" % round(v), W / 2, BY, win(t, a0, a1), G if v > 29.5 else R, size=84)
    label(C, ctx, t, T("por eso algunos") + 1.0, T("y si quieres"), "LOGO", A, "logo", dy=-210, size=80)
    # versiones
    a0, a1 = T("haces la cuadrícula"), T("lo inventó")
    if a0 <= t < a1:
        vt = [(T("haces la cuadrícula") + 0.3, 2), (T("cada versión") + 0.2, 3), (T("cada versión") + 1.2, 4)]
        v = 1
        for tt, vv in vt:
            if t >= tt: v = vv
        if t >= T("hasta ciento"): v = max(4, int(round(4 + 36 * sg(t, T("hasta ciento"), T("siete", 2, fin=True)))))
        n = 17 + 4 * v
        C.badge(ctx, "%d × %d" % (n, n), W / 2, BY, win(t, T("y si quieres"), a1), Y, size=90, sub=None)
        C.badge(ctx, "VERSIÓN %d" % v, W / 2, BY + 140, win(t, T("y si quieres"), a1), B, size=54)
    a0, a1 = T("cada versión"), T("hasta ciento")
    if a0 <= t < a1:
        p = win(t, a0 + 0.3, a1)
        _, yc = A("qr")
        for key, dx in (("tl", -1), ("tr", 1)):
            x, y = A(key); C.callout(ctx, "+2", max(110, min(W - 200, x + dx * 70)), yc, p, size=70)
    a0, a1 = T("lo inventó"), DUR
    if a0 <= t < a1:
        y = int(round(1994 * 1 if t > T("noventa y cuatro", fin=True) else 1960 + 34 * sg(t, a0 + 0.4, T("noventa y cuatro", fin=True))))
        C.badge(ctx, str(y), W / 2, BY, win(t, T("mil"), T("sígueme")), Y, size=96)
    label(C, ctx, t, T("de piezas") + 0.2, T("sígueme"), "PIEZA", A, "gear", dy=-250, size=72)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.4), (0.3, C.s_bleep(1200), 1.0), (T("y en menos") + 0.4, C.s_bleep(1568), 2.5),
         (T("vamos a inventarlo"), C.s_whoosh(), 0.45), (T("quieres guardar"), C.s_pop(), 0.5), (T("así que usas"), C.s_whoosh(), 0.35),
         (T("cuadrado negro"), C.s_pop(), 0.45), (T("blanco"), C.s_pop(), 0.45), (T("ni si está"), C.s_fail(), 0.4),
         (T("así que pones") + 0.4, C.s_thud(), 0.5), (T("así que pones") + 0.75, C.s_thud(), 0.5), (T("así que pones") + 1.1, C.s_thud(), 0.5),
         (T("cómo está girado"), C.s_win(), 0.4), (T("y como falta"), C.s_pop(), 0.45), (T("una zona toda"), C.s_whoosh(), 0.35),
         (T("así que lo mezclas") + 0.4, C.s_whoosh(), 0.5), (T("puedes romper") + 0.6, C.s_clank(), 0.6), (T("y se sigue"), C.s_bleep(1568), 2.5),
         (T("y se sigue") + 0.2, C.s_win(), 0.4), (T("se recupera"), C.s_buzz(1.8), 0.25), (T("por eso algunos") + 0.5, C.s_pop(), 0.5),
         (T("haces la cuadrícula") + 0.3, C.s_whoosh(), 0.4), (T("cada versión") + 0.2, C.s_pop(), 0.45), (T("cada versión") + 1.2, C.s_pop(), 0.45),
         (T("hasta ciento"), C.s_whoosh(1.2), 0.5), (T("lo inventó"), C.s_whoosh(), 0.45), (T("noventa y cuatro", fin=True), C.s_coin(), 0.5),
         (T("para seguir") + 0.4, C.s_bleep(1568), 2.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(7): E.append((T("el móvil se pierde") + 0.25 * k, C.s_bleep(900 + 60 * k), 1.0))
    return E
