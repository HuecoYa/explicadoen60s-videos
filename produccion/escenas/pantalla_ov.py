# Capa 2D de «Así funciona la pantalla táctil» + la lógica compartida de toques y carga (la usa también la escena)
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("pantalla")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"pantalla", "cristal", "rejilla", "cables", "cruce", "carga", "conduce", "agua", "sales", "cien", "sesenta",
            "chip", "ciento", "veinte", "trescientas", "zoom", "lana", "goma", "mojado", "gota", "loca"}

# ---------- rejilla ----------
NX, NY, DX, DY = 9, 17, 0.7, 0.75
GX = [(-(NX - 1) / 2 + i) * DX for i in range(NX)]
GY = [-6.4 + j * DY for j in range(NY)]
GZ = 0.95                      # superficie del cristal
P = (GX[5], GY[9])             # cruce principal (donde toca el dedo)
Q = (GX[2], GY[6])             # segundo dedo
GOTAS = [(GX[1], GY[4]), (GX[6], GY[2]), (GX[3], GY[12]), (GX[7], GY[13]), (GX[2], GY[15])]

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def kf(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b:
            u = ss((t - a) / max(b - a, 1e-4)); return tuple(x + (y - x) * u for x, y in zip(va, vb))
    return keys[-1][1]

def lejos(p, dx=7.0): return (p[0] + 1.6 * dx, p[1] - 1.0, GZ + 11.0)
def sobre(p, h=0.0): return (p[0], p[1], GZ + h)

def dedo1(t):
    """punta del dedo principal (x, y, z)"""
    t_cru = T("debajo del cristal"); t_dedo = T("tu dedo conduce"); t_acer = T("cuando lo acercas")
    t_arr = T("así sabe si arrastras"); t_dos = T("y si pones dos"); t_curioso = T("ahora el dato")
    t_lana = T("con guantes"); t_punt = T("por eso los punteros"); t_moj = T("y con el dedo mojado")
    if t < 2.3:  # toques rápidos desde el primer fotograma
        z = 0.75 * abs(math.sin(math.pi * (t + 0.35) / 0.75)) ** 1.5 if t < 1.85 else 0.0
        return (P[0], P[1], GZ + z)
    D = P2 = (P[0], P[1] - 2.25)
    keys = [(2.3, sobre(P)), (t_cru - 0.3, sobre(P)), (t_cru + 0.5, lejos(P)), (t_dedo, lejos(P, 4)), (t_dedo + 1.0, sobre(P, 2.6)),
            (t_acer, sobre(P, 1.6)), (t_acer + 0.7, sobre(P)), (t_arr, sobre(P)), (t_arr + 1.2, sobre(D)), (T("si pellizcas"), sobre(D)),
            (T("si das dos") , sobre(D)), (T("si das dos") + 0.25, sobre(D, 0.8)), (T("si das dos") + 0.5, sobre(D)),
            (T("si das dos") + 0.75, sobre(D, 0.8)), (T("si das dos") + 1.0, sobre(D)), (t_dos - 0.3, sobre(D, 1.2)),
            (t_dos + 0.5, sobre(P)), (T("por eso puedes"), sobre(P)), (T("hacer zoom", fin=True), sobre((P[0] + 1.4, P[1] + 1.5))),
            (t_curioso + 0.4, lejos(P)), (t_lana - 0.4, lejos(P, 4)), (t_lana + 0.4, sobre(P, 1.5)), (t_lana + 1.0, sobre(P)),
            (t_punt - 0.5, sobre(P)), (t_punt + 0.3, lejos(P)), (t_moj - 0.5, lejos(P, 4)), (t_moj + 0.6, sobre(P, 1.2)),
            (t_moj + 1.2, sobre(P)), (DUR + 2, sobre(P))]
    return kf(t, keys)

def dedo2(t):
    t_dos = T("y si pones dos")
    return kf(t, [(0, lejos(Q, -7)), (t_dos - 0.2, lejos(Q, -7)), (t_dos + 0.5, sobre(Q, 1.2)), (T("bajan dos"), sobre(Q)),
                  (T("por eso puedes"), sobre(Q)), (T("hacer zoom", fin=True), sobre((Q[0] - 1.4, Q[1] - 1.5))),
                  (T("ahora el dato") + 0.4, lejos(Q, -7)), (DUR + 2, lejos(Q, -7))])

def puntero(t):
    t_punt = T("por eso los punteros")
    return kf(t, [(0, lejos(P)), (t_punt, lejos(P)), (t_punt + 0.8, sobre(P, 1.0)), (t_punt + 1.3, sobre(P)),
                  (T("y con el dedo mojado") - 0.3, sobre(P)), (T("y con el dedo mojado") + 0.5, lejos(P)), (DUR + 2, lejos(P))])

def guante(t): return sg(t, T("ahora el dato") + 0.5, T("con guantes")) * (1 - sg(t, T("por eso los punteros") - 0.1, T("por eso los punteros") + 0.2))
def usa_puntero(t): return T("por eso los punteros") - 0.1 < t < T("y con el dedo mojado") + 0.4

def gotas_on(t):
    """aparición de cada gota sobre el cristal (0..1)"""
    t0 = T("cada gota")
    return [sg(t, t0 - 1.6 + 0.35 * k, t0 - 1.3 + 0.35 * k) for k in range(len(GOTAS))]

def toques(t):
    """lista de (x, y, fuerza) que roban carga ahora mismo"""
    out = []
    def contacto(p): return max(0.0, 1 - (p[2] - GZ) / 0.35)
    p1 = dedo1(t); c1 = contacto(p1)
    if c1 > 0 and not usa_puntero(t):
        s = c1 * (1 - guante(t))
        # primera vez que se acerca: baja poco y luego «de golpe» al decir «de cien… a sesenta y dos»
        if T("cuando lo acercas") < t < T("de cien", fin=True) + 1.0:
            s *= 0.12 + 0.88 * sg(t, T("de cien"), T("a sesenta", fin=True))
        if 2.3 < t < T("cuando lo acercas") or t < 2.3: s *= 1.0
        out.append((p1[0], p1[1], s))
    p2 = dedo2(t); c2 = contacto(p2)
    if c2 > 0: out.append((p2[0], p2[1], c2))
    if usa_puntero(t):
        pp = puntero(t); cp = contacto(pp)
        if cp > 0: out.append((pp[0], pp[1], cp * 0.92))
    for k, (g, a) in enumerate(zip(GOTAS, gotas_on(t))):
        if a > 0: out.append((g[0], g[1], a * (0.55 + 0.35 * math.sin(t * 9 + k * 2.1))))
    return out

def carga(x, y, t, tq=None):
    tq = toques(t) if tq is None else tq
    q = 100.0
    for tx, ty, s in tq: q -= 38 * s * math.exp(-((x - tx) ** 2 + (y - ty) ** 2) / 0.3)
    return max(0.0, q)

def nodo_cercano(x, y):
    i = min(range(NX), key=lambda k: abs(GX[k] - x)); j = min(range(NY), key=lambda k: abs(GY[k] - y)); return i, j

def nodos_visibles(t):
    """qué cruces llevan número encima"""
    t_mide, t_fin_dedo = T("y el móvil mide"), T("pero no mira")
    i0, j0 = nodo_cercano(*P)
    if t_mide <= t < t_fin_dedo + 0.6:
        return [(i0 + a, j0 + b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    if t < T("así sabe si"): return []
    out = set()
    for x, y, s in toques(t):
        out.add(nodo_cercano(x, y))
    if T("con guantes") <= t < T("por eso los punteros"): out.add((i0, j0))
    return sorted(out)

# ---------- capa 2D ----------
def ring(ctx, x, y, r, col, a, lw=8):
    if a <= 0: return
    ctx.save(); ctx.set_line_width(lw); ctx.set_source_rgba(*col, a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke(); ctx.restore()

def numero(C, ctx, x, y, v, size, alpha):
    if v > 97: col = (1, 1, 1)
    elif v > 80: col = C.YL
    else: col = (1.0, 0.35, 0.3)
    C.outlined(ctx, "%d" % round(v), x, y, size, fill=col, stroke=9, alpha=alpha, shadow=False)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    # anillo del primer toque: la pantalla sabe dónde
    p = win(t, T("y ella sabe"), T("cómo") + 0.3)
    if p:
        x, y = A("P"); ring(ctx, x, y, 70 + 25 * math.sin(t * 6), Y, p)
        ctx.save(); ctx.set_source_rgba(*Y, p); ctx.set_line_width(5)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ctx.move_to(x + dx * 95, y + dy * 95); ctx.line_to(x + dx * 140, y + dy * 140)
        ctx.stroke(); ctx.restore()
    label(C, ctx, t, T("debajo del cristal") + 0.3, T("una rejilla"), "CRISTAL", A, "cristal", dy=-90, size=60)
    label(C, ctx, t, T("una rejilla") , T("unos van") + 0.3, "CABLES", A, "rejilla", dy=-90, size=60)
    label(C, ctx, t, T("en horizontal") - 0.1, T("y otros en"), "HORIZONTALES", A, "hfila", dy=-120, size=54)
    label(C, ctx, t, T("en vertical") - 0.1, T("en cada cruce"), "VERTICALES", A, "vcol", dy=-140, size=54)
    label(C, ctx, t, T("en cada cruce") + 0.2, T("y el móvil mide"), "CARGA", A, "P", dy=-170, size=64)
    label(C, ctx, t, T("el chip busca") , T("pero no mira"), "CHIP", A, "chip", dy=140, size=62)
    # números de carga sobre los cruces
    vis = nodos_visibles(t)
    if vis:
        tq = toques(t); a = min(1.0, (t - T("y el móvil mide")) / 0.3) if t < T("pero no mira") + 0.6 else 1.0
        if T("pero no mira") < t < T("pero no mira") + 0.6: a = 1 - (t - T("pero no mira")) / 0.6
        for i, j in vis:
            k = "n%d_%d" % (i, j)
            try: x, y = A(k)
            except KeyError: continue
            v = carga(GX[i], GY[j], t, tq)
            grande = (i, j) == nodo_cercano(*P) and T("de golpe") < t < T("pero no mira")
            numero(C, ctx, x, y - 70, v, 74 if grande else 48, max(0.0, a))
    # el chip encuentra el mínimo
    p = win(t, T("y ahí está"), T("pero no mira") + 0.3)
    if p: x, y = A("P"); ring(ctx, x, y, 85, R, p, 10)
    # barridos por segundo
    t_rep, t_300 = T("repasa toda"), T("más de trescientas")
    if T("ciento veinte") - 0.2 <= t < T("así sabe si"):
        n = 120 * sg(t, T("ciento veinte"), T("veces cada", fin=True)) if t < t_300 else 120 + 180 * sg(t, t_300, t_300 + 0.8)
        C.badge(ctx, "%d BARRIDOS/S" % round(n), W / 2, H * 0.265, win(t, T("ciento veinte") - 0.2, T("así sabe si")), B if t < t_300 else Y, size=72)
    # guante: la carga no se va
    p = win(t, T("la lana no"), T("por eso los punteros") - 0.1)
    if p: C.badge(ctx, "✗ 0 TOQUES", W / 2, H * 0.265, p, R, size=72)
    label(C, ctx, t, T("goma conductora") - 0.6, T("y con el dedo") - 0.1, "GOMA\nCONDUCTORA", A, "punta", dx=-120, dy=-120, size=56)
    # gotas: toques fantasma
    if t > T("y la pantalla se"):
        on = gotas_on(t)
        for k, a in enumerate(on):
            if a > 0.5 and math.sin(t * 13 + k * 1.7) > 0:
                x, y = A("g%d" % k); ring(ctx, x, y, 60, R, 0.9)
    p = win(t, T("y la pantalla se"), DUR)
    if p: C.badge(ctx, "✗ %d TOQUES FALSOS" % len(GOTAS), W / 2, H * 0.265, p, R, size=66)

def sfx_events(C):
    E = [(0.0, C.s_pop(), 0.4), (0.75, C.s_pop(), 0.4), (1.5, C.s_pop(), 0.4), (T("debajo del cristal"), C.s_whoosh(), 0.5),
         (T("en cada cruce"), C.s_pop(), 0.4), (T("y el móvil mide"), C.s_whoosh(), 0.4), (T("cuando lo acercas") + 0.6, C.s_thud(), 0.5),
         (T("de cien"), C.s_bleep(880), 1.0), (T("a sesenta"), C.s_bleep(520), 1.0), (T("y ahí está"), C.s_win(), 0.5),
         (T("repasa toda"), C.s_whoosh(), 0.4), (T("más de trescientas"), C.s_whoosh(), 0.5), (T("ahora el dato"), C.s_whoosh(), 0.5),
         (T("la lana no"), C.s_fail(), 0.6), (T("por eso los punteros") + 1.3, C.s_pop(), 0.5), (T("y la pantalla se"), C.s_fail(), 0.6),
         (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(5): E.append((T("si das dos") + 0.25 * k, C.s_pop(), 0.25))
    return E
