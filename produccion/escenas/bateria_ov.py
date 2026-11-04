# Capa 2D de «Así funciona la batería del móvil»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("bateria")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"átomos", "batería", "láminas", "plástico", "poros", "grafito", "litio", "óxido", "líquido", "electrón", "electrones",
            "porcentaje", "veinte", "cincuenta", "cien", "desgaste", "atrapados", "mil", "ciclos", "ochenta", "ciclo", "mitad", "calor", "sol"}

def ring(ctx, x, y, r, col, a, lw=8):
    if a <= 0: return
    ctx.save(); ctx.set_line_width(lw); ctx.set_source_rgba(*col, a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke(); ctx.restore()

def big(C, ctx, s, x, y, a, col, size=120):
    if a > 0: C.outlined(ctx, s, x, y, size, fill=col, stroke=14, alpha=min(1, a), scale=0.9 + 0.1 * min(1, a))

def overlay(ctx, t, A, C):
    Y, R, G, B, P = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0), (0.75, 0.55, 1.0)
    # el porcentaje del móvil baja desde el primer fotograma
    p = win(t, 0, T("abre la batería") + 0.3)
    if p:
        x, y = A("icono"); v = round(64 - 14 * min(1, t / 4.5))
        big(C, ctx, "%d%%" % v, x, y - 170, p, Y if v < 58 else (1, 1, 1), 110)
    label(C, ctx, t, T("abre la batería"), T("son dos"), "BATERÍA", A, "pouch", dy=-160, size=66)
    label(C, ctx, t, T("son dos") + 0.3, T("separadas por"), "COBRE", A, "cu", dy=-90, size=52)
    label(C, ctx, t, T("son dos") + 0.3, T("separadas por"), "ALUMINIO", A, "al", dy=-90, size=52)
    label(C, ctx, t, T("separadas por") + 0.4, T("a un lado"), "POROS", A, "sep", dy=-110, size=62)
    label(C, ctx, t, T("grafito") - 0.1, T("al otro"), "GRAFITO", A, "graf", dy=-110, size=62)
    label(C, ctx, t, T("un óxido") - 0.1, T("y entre medias"), "ÓXIDO", A, "oxi", dy=-110, size=62)
    label(C, ctx, t, T("lleno de litio") , T("y entre medias") + 0.5, "LITIO", A, "ion0", dy=-120, size=56)
    label(C, ctx, t, T("un líquido"), T("cuando enchufas"), "LÍQUIDO", A, "elec", dy=-80, size=60)
    label(C, ctx, t, T("cuando enchufas"), T("el litio suelta") + 0.6, "CARGADOR", A, "dev", dy=-100, size=58)
    label(C, ctx, t, T("suelta un electrón"), T("se mete entre"), "ELECTRÓN", A, "wire", dy=-80, size=56)
    label(C, ctx, t, T("esa corriente"), T("pero cada"), "PANTALLA", A, "dev", dy=-100, size=58)
    # el porcentaje sube: veinte, cincuenta, cien
    a0, a1 = T("y el porcentaje"), T("cuando usas")
    if a0 <= t < a1:
        k0, k1, k2 = T("veinte"), T("cincuenta"), T("cien")
        v = 20 if t < k0 else (20 + 30 * min(1, (t - k0) / (k1 - k0)) if t < k1 else 50 + 50 * min(1, (t - k1) / (k2 - k1)))
        C.badge(ctx, "%d%%" % v, W / 2, H * 0.265, win(t, a0, a1), G if v == 100 else Y, size=110)
    # atrapados
    if T("algunos átomos") + 1.0 < t < T("muchos móviles"):
        for k in (2, 9, 13):
            x, y = A("st%d" % k); ring(ctx, x, y, 45, R, win(t, T("algunos átomos") + 1.0, T("muchos móviles")))
    p = win(t, T("por eso con"), T("muchos móviles"))
    if p:
        v = round(100 - 8 * min(1, (t - T("por eso con")) / 1.5))
        C.badge(ctx, "CAPACIDAD %d%%" % v, W / 2, H * 0.265, p, Y, size=70)
    # mil ciclos y ochenta por ciento
    a0, a1 = T("muchos móviles"), T("pero ojo")
    if a0 <= t < a1:
        u = min(1, (t - a0) / max(T("ciclos", fin=True) - a0, 0.5)); cyc = round(1000 * u ** 1.5)
        cap = round(100 - 20 * min(1, (t - a0) / max(T("ochenta", fin=True) - a0, 0.5)))
        C.badge(ctx, "%d CICLOS" % cyc, W / 2, H * 0.265, win(t, a0, a1), B, size=72)
        C.badge(ctx, "CAPACIDAD %d%%" % cap, W / 2, H * 0.265 + 125, win(t, a0 + 0.4, a1), Y if cap > 85 else (1.0, 0.6, 0.25), size=72)
    # un ciclo = 50 % hoy + 50 % mañana
    a0 = T("si gastas")
    p = win(t, a0, T("y un truco"))
    if p:
        hoy = "HOY 50%" if t >= a0 + 0.3 else ""
        txt = "HOY 50%" + ("  +  MAÑANA 50%" if t >= T("y la otra") else "")
        C.badge(ctx, txt, W / 2, H * 0.265, p, B, size=60)
        if t >= T("eso es un"): C.badge(ctx, "= 1 CICLO", W / 2, H * 0.265 + 120, win(t, T("eso es un"), T("y un truco")), G, size=76)
    p = win(t, T("el calor"), DUR)
    if p:
        v = round(25 + 20 * min(1, (t - T("el calor")) / 1.5))
        C.badge(ctx, "%d °C" % v, W / 2, H * 0.265, p, R if v > 35 else Y, size=96)

def sfx_events(C):
    E = [(0.1, C.s_bleep(660), 0.8), (T("abre la batería"), C.s_whoosh(), 0.6), (T("son dos") - 0.3, C.s_whoosh(1.0), 0.6)]
    for w in ("grafito", "un óxido", "un líquido", "cuando enchufas"): E.append((T(w), C.s_pop(), 0.45))
    for w in ("veinte", "cincuenta"): E.append((T(w), C.s_bleep(880), 1.0))
    E += [(T("cien"), C.s_win(), 0.5), (T("ocurre al"), C.s_whoosh(), 0.5), (T("algunos átomos") + 1.0, C.s_fail(), 0.5),
          (T("muchos móviles"), C.s_whoosh(), 0.5), (T("eso es un"), C.s_pop(), 0.6), (T("el calor"), C.s_fail(), 0.6),
          (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
