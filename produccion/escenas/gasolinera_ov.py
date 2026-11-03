# Elementos gráficos puntuales: "El surtidor de gasolina"
import math
SUB_Y = 0.66
KEYWORDS = {"sensor", "agujerito", "agujero", "boquilla", "tubo", "gatillo", "succión", "venturi", "aire", "lleno", "llena",
            "membrana", "pestillo", "¡clac", "clac", "válvula", "espuma", "chip", "física", "gota"}
W, H = 1080, 1920

def clampx(x, m=260): return max(m, min(W - m, x))
def clampy(y, lo=330, hi=1080): return max(lo, min(hi, y))
def win(t, a, b, fade=0.15):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / 0.22) * min(1.0, (b - t) / fade)

def label(C, ctx, t, a, b, text, A, key, dx=0, dy=-220, size=68):
    p = win(t, a, b)
    if p:
        x, y = A(key); C.callout(ctx, text, clampx(x + dx), clampy(y + dy), p, size=size)

def arrow(ctx, x0, y0, x1, y1, col, p, lw=12):
    if p <= 0: return
    x1 = x0 + (x1 - x0) * p; y1 = y0 + (y1 - y0) * p
    ang = math.atan2(y1 - y0, x1 - x0)
    for st, c in ((lw + 8, (0, 0, 0)), (lw, col)):
        ctx.set_line_width(st); ctx.set_source_rgb(*c); ctx.set_line_cap(1); ctx.set_line_join(1)
        ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()
        for s in (1, -1):
            ctx.move_to(x1, y1); ctx.line_to(x1 - 34 * math.cos(ang + s * 0.5), y1 - 34 * math.sin(ang + s * 0.5)); ctx.stroke()

def ring(ctx, x, y, r, p):
    if p <= 0: return
    ctx.save(); ctx.set_line_width(9); ctx.set_source_rgba(1, 0.82, 0.16, p); ctx.arc(x, y, r * (0.7 + 0.3 * p), 0, 2 * math.pi); ctx.stroke(); ctx.restore()

def overlay(ctx, t, A, C):
    Y = C.YL
    # el agujerito
    p = win(t, 6.0, 9.2)
    if p: x, y = A("hole"); ring(ctx, x, y, 48, p)
    label(C, ctx, t, 6.2, 9.2, "AGUJERO", A, "hole", dy=230)
    label(C, ctx, t, 10.3, 14.4, "TUBO", A, "tube", dy=-200, size=76)
    # efecto Venturi: flujo rápido + aire aspirado
    p = win(t, 14.9, 23.8)
    if p:
        (xa, ya), (xb, yb) = A("spout_a"), A("spout_b"); arrow(ctx, xa, ya - 40, xb, yb - 40, (1, 1, 1), min(1, (t - 14.9) / 0.6))
    label(C, ctx, t, 19.1, 23.8, "EFECTO\nVENTURI", A, "sp0", dy=-300, size=70)
    p = win(t, 20.6, 29.1)
    if p:
        (xo, yo), (xh, yh) = A("hole_out"), A("hole"); arrow(ctx, xo, yo, xh, yh, Y, min(1, (t - 20.6) / 0.4))
    label(C, ctx, t, 24.2, 28.9, "AIRE", A, "hole_out", dy=150)
    p = win(t, 33.7, 35.0)
    if p: C.badge(ctx, "AIRE: 0", W / 2, H * 0.165, p, C.RED, size=76)
    label(C, ctx, t, 37.7, 40.2, "MEMBRANA", A, "memb", dy=-230)
    label(C, ctx, t, 40.5, 42.6, "PESTILLO", A, "latch", dy=260)
    p = win(t, 42.75, 43.6, fade=0.3)
    if p: C.outlined(ctx, "¡CLAC!", W / 2, H * 0.3, 150, fill=Y, stroke=18, italic=True, scale=C.back(p), rot=-0.08)
    label(C, ctx, t, 43.6, 45.1, "VÁLVULA CERRADA", A, "valve", dy=-240, size=58)
    label(C, ctx, t, 51.9, 54.0, "ESPUMA", A, "foam", dy=220)
    p = win(t, 53.9, 55.9)
    if p: C.badge(ctx, "0 CHIPS", W / 2, H * 0.165, p, Y, size=80)

def sfx_events(C):
    E = []
    for t in (3.6, 5.95, 9.3, 16.2, 24.3, 30.0, 35.3, 47.4, 56.0, 58.8):
        E.append((t, C.s_whoosh(), 0.45))
    E.append((0.0, C.s_buzz(43.4), 0.12))
    for t in (6.2, 10.3, 19.1, 24.2, 37.7, 40.5, 51.9, 53.9):
        E.append((t, C.s_pop(), 0.5))
    E.append((33.7, C.s_fail(), 0.6))
    E.append((42.75, C.s_clank(), 1.0)); E.append((42.75, C.s_thud(), 0.9))
    return E
