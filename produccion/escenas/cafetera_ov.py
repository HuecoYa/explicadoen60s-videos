# Capa 2D de «Así funciona la cafetera italiana»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("cafetera")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"cafetera", "bomba", "motor", "depósito", "embudo", "jarra", "fuego", "vapor", "rosca", "presión", "bar", "tubo",
            "fondo", "filtro", "goma", "chimenea", "gorgoteo", "válvula", "seguridad", "nueve", "dos", "exprés", "atasca"}

def arrow(ctx, x0, y0, x1, y1, col, p, lw=12):
    if p <= 0: return
    x1 = x0 + (x1 - x0) * p; y1 = y0 + (y1 - y0) * p; ang = math.atan2(y1 - y0, x1 - x0)
    for st, c in ((lw + 8, (0, 0, 0)), (lw, col)):
        ctx.set_line_width(st); ctx.set_source_rgb(*c); ctx.set_line_cap(1); ctx.set_line_join(1)
        ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()
        for s in (1, -1):
            ctx.move_to(x1, y1); ctx.line_to(x1 - 30 * math.cos(ang + s * 0.5), y1 - 30 * math.sin(ang + s * 0.5)); ctx.stroke()

def bar_txt(v):
    s = ("%.1f" % v).replace(".", ","); return s[:-2] if s.endswith(",0") else s

def gauge(C, ctx, cx, cy, r, v, vmax, a, col):
    """manómetro: arco de 0 a vmax y aguja"""
    if a <= 0: return
    ctx.save(); ctx.translate(cx, cy); s = C.back(a); ctx.scale(s, s)
    ctx.arc(0, 0, r + 22, math.pi, 2 * math.pi); ctx.close_path(); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92); ctx.fill()
    ctx.set_line_width(18); ctx.set_source_rgba(1, 1, 1, 0.2); ctx.arc(0, 0, r, math.pi, 2 * math.pi); ctx.stroke()
    ctx.set_source_rgb(*col); ctx.arc(0, 0, r, math.pi, math.pi * (1 + min(v, vmax) / vmax)); ctx.stroke()
    for k in range(0, int(vmax) + 1):
        an = math.pi * (1 + k / vmax); ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.move_to(math.cos(an) * (r - 30), math.sin(an) * (r - 30)); ctx.line_to(math.cos(an) * (r - 14), math.sin(an) * (r - 14)); ctx.stroke()
    an = math.pi * (1 + min(v, vmax) / vmax); ctx.set_line_width(9); ctx.set_source_rgb(1, 1, 1); ctx.set_line_cap(1)
    ctx.move_to(0, 0); ctx.line_to(math.cos(an) * (r - 25), math.sin(an) * (r - 25)); ctx.stroke()
    ctx.arc(0, 0, 14, 0, 7); ctx.fill(); ctx.restore()
    C.outlined(ctx, bar_txt(v) + " BAR", cx, cy + 48, 54, fill=col, stroke=9, alpha=a, shadow=False)

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

def presion(t):
    """bar"""
    t0 = T("y la presión sube")
    p = keyed(t, [(T("pones el fuego"), 0.0), (t0, 0.3), (T("medio bar"), 0.5), (T("un bar"), 1.0), (T("uno y medio"), 1.5),
                  (T("así que el agua sube"), 1.5), (T("ese gorgoteo"), 1.2), (T("es la señal"), 0.2), (T("apagar el fuego") + 1, 0.0),
                  (T("si el café está"), 0.0), (T("la presión seguiría"), 1.6), (T("subiendo", fin=True), 2.6), (T("así que la válvula"), 2.9),
                  (T("se abre") + 0.2, 3.0), (T("suelta el vapor") + 0.8, 0.6), (T("ahora un dato"), 0.0)])
    return p

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    label(C, ctx, t, T("abajo"), T("en medio"), "DEPÓSITO", A, "dep", dy=-60, size=60)
    label(C, ctx, t, T("en medio") + 0.2, T("arriba", 2), "EMBUDO", A, "emb", dy=-170, size=60)
    label(C, ctx, t, T("arriba", 2) + 0.2, T("pones el fuego"), "JARRA", A, "jar", dy=-60, size=62)
    label(C, ctx, t, T("pones el fuego"), T("el agua se calienta") + 0.5, "FUEGO", A, "fuego", dy=150, size=60)
    label(C, ctx, t, T("soltar vapor") - 0.3, T("pero el depósito"), "VAPOR", A, "vapor", dx=-160, dy=-60, size=58)
    label(C, ctx, t, T("cerrado a rosca") - 0.3, T("y la presión"), "ROSCA", A, "rosca", dx=150, dy=-100, size=58)
    # presión
    a0, a1 = T("y la presión"), T("es la señal") + 0.5
    if a0 <= t < a1:
        v = presion(t); C.badge(ctx, bar_txt(v) + " BAR", W / 2, H * 0.265, win(t, a0, a1), Y, size=96)
    # el vapor empuja el agua hacia abajo
    p = win(t, T("ese vapor aprieta"), T("así que el agua sube") + 0.6)
    if p:
        for k in ("supL", "sup", "supR"):
            x, y = A(k); u = (t * 1.5) % 1.0; arrow(ctx, x, y - 150 + 40 * u, x, y - 30 + 40 * u, Y, p)
    label(C, ctx, t, T("y la única") + 0.3, T("que llega"), "TUBO", A, "tubo", dx=170, dy=0, size=60)
    p = win(t, T("que llega"), T("así que el agua sube"))
    if p:
        x, y = A("fondo"); C.callout(ctx, "FONDO", clampx(x + 170), clampy(y + 40, 330, 1450), p, size=54)
    p = win(t, T("así que el agua sube"), T("atraviesa"))
    if p:
        (x0, y0), (x1, y1) = A("fondo"), A("cafe"); arrow(ctx, x0 + 60, y0, x1 + 60, y1, B, min(1, (t - T("así que el agua sube")) / 0.8))
    label(C, ctx, t, T("un filtro") , T("impiden"), "FILTRO", A, "filtro", dx=160, dy=-90, size=56)
    label(C, ctx, t, T("y una goma"), T("por fin"), "GOMA", A, "goma", dx=-130, dy=-90, size=56)
    label(C, ctx, t, T("la chimenea") - 0.2, T("y cae en"), "CHIMENEA", A, "chim", dy=-110, size=58)
    label(C, ctx, t, T("es una válvula") - 0.3, T("si el café"), "VÁLVULA", A, "valv", dx=60, dy=-130, size=60)
    a0, a1 = T("si el café está"), T("ahora un dato")
    if a0 <= t < a1:
        v = presion(t); C.badge(ctx, bar_txt(v) + " BAR", W / 2, H * 0.265, win(t, a0, a1), R if v > 2 else Y, size=96)
    label(C, ctx, t, T("y el filtro se"), T("así que la válvula"), "ATASCADO", A, "filtro", dx=0, dy=-120, size=56)
    # comparación final de manómetros
    a0 = T("una cafetera de bar")
    if t >= a0:
        p = win(t, a0, DUR + 1)
        v = 9 * min(1, (t - a0) / 1.6)
        gauge(C, ctx, W * 0.29, H * 0.36, 140, v, 10, p, R)
        C.outlined(ctx, "BAR", W * 0.29, H * 0.36 - 200, 50, fill=(1, 1, 1), stroke=8, alpha=p, shadow=False)
        if t >= T("la tuya"):
            p2 = win(t, T("la tuya"), DUR + 1); v2 = 1.5 * min(1, (t - T("la tuya")) / 1.0)
            gauge(C, ctx, W * 0.69, H * 0.36, 140, v2, 10, p2, G)
            C.outlined(ctx, "LA TUYA", W * 0.69, H * 0.36 - 200, 50, fill=(1, 1, 1), stroke=8, alpha=p2, shadow=False)

def sfx_events(C):
    E = [(0.0, C.s_buzz(2.8), 0.6), (T("tiene tres"), C.s_whoosh(), 0.5), (T("pones el fuego"), C.s_thud(), 0.6)]
    for w in ("abajo", "en medio", "arriba", "medio bar", "un bar", "uno y medio", "un filtro", "la chimenea"): E.append((T(w), C.s_pop(), 0.45))
    E += [(T("así que el agua sube"), C.s_whoosh(), 0.5), (T("ese gorgoteo"), C.s_buzz(2.0), 0.7), (T("y el filtro se"), C.s_fail(), 0.5),
          (T("se abre"), C.s_clank(), 0.6), (T("suelta el vapor"), C.s_whoosh(1.2), 0.7), (T("una cafetera de bar"), C.s_pop(), 0.5),
          (T("la tuya"), C.s_pop(), 0.5), (T("no es un"), C.s_fail(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
