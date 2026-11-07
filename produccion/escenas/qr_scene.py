# «Si tuvieras que inventar el código QR…»: un móvil escanea el QR de la carta del bar y se abre la carta; el código se
# deshace y se construye: cuadrícula 21×21 (negro = 1, blanco = 0), se tuerce, tres cuadrados de esquina lo orientan, la
# esquina que falta marca abajo-derecha, una zona blanca despista, la máscara reparte los negros, se rompe un trozo y se
# sigue leyendo (datos repartidos, hasta un 30 % de daño), un dibujo en medio, versiones más grandes (+4 por lado hasta
# 177×177) y, al final, una pieza de coche con su QR en una cinta (1994).
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("qr")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]
N = 21; M = 0.2                       # módulos y tamaño de módulo
QC = Vector((0, 0, 3.0))              # centro del código
BLK = (0.06, 0.07, 0.09); WHT = (0.95, 0.95, 0.93); CARD = (0.97, 0.97, 0.95)
BODY = (0.17, 0.18, 0.22); SCREEN = (0.08, 0.1, 0.14); GRN = (0.25, 0.85, 0.45); RED = (0.95, 0.28, 0.28)
BLUE = (0.25, 0.55, 1.0); YEL = (1.0, 0.8, 0.2); STEEL = (0.62, 0.65, 0.7); GREY = (0.55, 0.57, 0.62)
GROUPS = [(0.25, 0.55, 1.0), (0.95, 0.45, 0.2), (0.7, 0.4, 1.0), (0.25, 0.8, 0.5)]
FONT = os.path.expanduser("~/.fonts/Poppins-Bold.ttf")
LEJOS = Vector((0, 200, -200))

rng = random.Random(1994)
BASE = [[rng.random() < 0.5 for c in range(N)] for r in range(N)]
FINDERS = [(0, 0), (0, 14), (14, 0)]
def in_finder(r, c):
    return any(r0 - 1 <= r <= r0 + 7 and c0 - 1 <= c <= c0 + 7 for r0, c0 in FINDERS)
def finder_bit(r, c):
    for r0, c0 in FINDERS:
        if r0 <= r < r0 + 7 and c0 <= c < c0 + 7:
            d = max(abs(r - r0 - 3), abs(c - c0 - 3)); return d != 2
    return False
def timing(r, c): return (r == 6 or c == 6) and not in_finder(r, c)
ZONE = lambda r, c: 8 <= r <= 13 and 7 <= c <= 13          # zona toda blanca
CH = lambda r, c: 13 <= r <= 19 and 9 <= c <= 16            # trozo que se rompe
CENTER = lambda r, c: 8 <= r <= 12 and 8 <= c <= 12          # dibujo en medio
MASKED = lambda r, c: (r + c) % 2 == 0
DAMAGE = [(r, c) for r in range(N) for c in range(N) if not in_finder(r, c) and not CH(r, c)]
random.Random(7).shuffle(DAMAGE)
DMG_RANK = {rc: i for i, rc in enumerate(DAMAGE)}
GRP = {(r, c): random.Random(r * 31 + c).randrange(4) for r in range(N) for c in range(N)}

def tpos(r, c): return Vector(((c - (N - 1) / 2) * M, 0, ((N - 1) / 2 - r) * M))

def font(o):
    if os.path.exists(FONT):
        try: o.data.font = bpy.data.fonts.load(FONT, check_existing=True)
        except Exception: pass

def txt(s, loc, size, col, parent=None, rot=(math.pi / 2, 0, 0)):
    o = text3d(s, loc, size, col, parent=parent, extrude=0.005, rot=rot, unique=True); font(o); return o

def qr_mesh(n, mod, col, name, seed):
    """un QR entero de n×n en un solo objeto (cuadrados negros), centrado, en el plano XZ, mirando a -Y"""
    r0 = random.Random(seed)
    fins = [(0, 0), (0, n - 7), (n - 7, 0)]
    def bit(r, c):
        for a, b in fins:
            if a <= r < a + 7 and b <= c < b + 7: return max(abs(r - a - 3), abs(c - b - 3)) != 2
            if a - 1 <= r <= a + 7 and b - 1 <= c <= b + 7: return False
        if r == 6 or c == 6: return (r + c) % 2 == 0
        return r0.random() < 0.5
    me = bpy.data.meshes.new(name); bm = bmesh.new(); h = (n - 1) / 2
    for r in range(n):
        for c in range(n):
            if not bit(r, c): continue
            x = (c - h) * mod; z = (h - r) * mod; s = mod / 2
            vs = [bm.verts.new((x - s, 0, z - s)), bm.verts.new((x + s, 0, z - s)), bm.verts.new((x + s, 0, z + s)), bm.verts.new((x - s, 0, z + s))]
            bm.faces.new(vs)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(col)); return o

def phone_build():
    e = empty(LEJOS); e.rotation_euler = (math.pi / 2, 0, 0)
    rounded_slab(1.6, 3.3, 0.25, 0.18, (0, 0, -0.18), BODY, parent=e)
    S = {"e": e}
    S["scr"] = rounded_slab(1.48, 3.18, 0.2, 0.02, (0, 0, 0.0), SCREEN, parent=e, unique=True)
    # visor: esquinas verdes y un mini QR
    vf = empty((0, 0.1, 0.03), e); S["vf"] = vf
    for sx in (-1, 1):
        for sy in (-1, 1):
            box((0.32, 0.06, 0.02), (sx * 0.45, sy * 0.6, 0), GRN, vf); box((0.06, 0.32, 0.02), (sx * 0.6, sy * 0.45, 0), GRN, vf)
    mini = qr_mesh(21, 0.04, (0.85, 0.87, 0.9), "mini", 3); mini.parent = vf; mini.rotation_euler = (-math.pi / 2, 0, 0); mini.location = (0, 0, 0.01)
    S["scan"] = box((1.1, 0.04, 0.02), (0, 0, 0.02), GRN, vf)
    # carta
    menu = empty((0, 0, 0.03), e); S["menu"] = menu
    box((1.3, 0.5, 0.02), (0, 1.1, 0), (0.95, 0.6, 0.25), menu)
    t = txt("CARTA", (0, 1.1, 0.02), 0.26, (1, 1, 1), parent=menu, rot=(0, 0, 0))
    for k in range(5):
        y = 0.5 - k * 0.42
        box((0.3, 0.3, 0.02), (-0.45, y, 0), (0.9, 0.75 - 0.1 * k, 0.4), menu)
        box((0.7, 0.07, 0.02), (0.2, y + 0.07, 0), (0.85, 0.87, 0.9), menu); box((0.45, 0.06, 0.02), (0.08, y - 0.08, 0), (0.5, 0.52, 0.58), menu)
    # estado (aro de color sobre la pantalla)
    S["st"] = cyl(0.22, 0.03, (0, 0.1, 0.06), GRN, parent=e, rot=(0, 0, 0), unique=True)
    S["q"] = txt("?", (0, 0.1, 0.09), 0.5, (1, 1, 1), parent=e, rot=(0, 0, 0))
    return S

def build():
    sc, cam = scene_setup(world=(0.09, 0.1, 0.13), shadow=0.35)
    S = {"cam": cam}
    # ---- tarjeta (soporte de mesa) y módulos ----
    card = empty(QC); S["card"] = card
    q = N * M / 2 + 0.45                                   # medio lado con margen
    hx0, hx1 = tpos(0, 9).x - M / 2, tpos(0, 16).x + M / 2  # hueco del trozo que se rompe
    hz0, hz1 = tpos(19, 0).z - M / 2, tpos(13, 0).z + M / 2
    for (x0, x1, z0, z1) in ((-q, hx0, -q, q), (hx1, q, -q, q), (hx0, hx1, hz1, q), (hx0, hx1, -q, hz0)):
        box((x1 - x0, 0.12, z1 - z0), ((x0 + x1) / 2, 0.06, (z0 + z1) / 2), CARD, card)
    box((2 * q + 0.1, 0.14, 0.12), (0, 0.06, q + 0.03), (0.2, 0.22, 0.26), card)     # canto superior
    box((3.2, 2.2, 0.35), (0, 0.6, -q - 0.17), (0.2, 0.22, 0.26), card)               # base del soporte
    box((0.15, 1.2, 2.5), (0, 0.7, -q + 0.9), (0.2, 0.22, 0.26), card, rot=(-0.45, 0, 0))
    chunk = empty((0, 0, 0), card); S["chunk"] = chunk
    box((hx1 - hx0, 0.12, hz1 - hz0), ((hx0 + hx1) / 2, 0.06, (hz0 + hz1) / 2), CARD, chunk)
    S["tiles"] = {}
    for r in range(N):
        for c in range(N):
            piv = empty(tpos(r, c), chunk if CH(r, c) else card)
            b = box((M * 0.98, 0.06, M * 0.98), (0, -0.03, 0), BLK, piv, unique=True)
            S["tiles"][(r, c)] = (piv, b)
    # líneas de la cuadrícula
    gl = empty((0, -0.075, 0), card); S["gl"] = gl
    for k in range(N + 1):
        v = (k - N / 2) * M
        box((0.018, 0.01, N * M), (v, 0, 0), (0.55, 0.6, 0.7), gl); box((N * M, 0.01, 0.018), (0, 0, v), (0.55, 0.6, 0.7), gl)
    # enlace (texto 3D)
    S["link"] = txt("carta.bar/menu", (0, -0.6, 0), 0.42, (0.3, 0.6, 1.0), parent=card)
    # barrido de la máscara
    S["sweep"] = box((0.08, 0.2, N * M + 0.4), (0, -0.12, 0), BLUE, card)
    # marcador que cuenta blancos
    S["cnt"] = box((M * 0.95, 0.3, M * 0.95), (0, -0.2, 0), YEL, card, unique=True)
    # líneas entre esquinas y marca de la esquina que falta
    S["L1"] = bar_obj(GRN, r=0.05, parent=card); S["L2"] = bar_obj(GRN, r=0.05, parent=card)
    br = tpos(17, 17)
    S["miss"] = torus(0.72, 0.07, br + Vector((0, -0.12, 0)), RED, card, rot=(math.pi / 2, 0, 0), unique=True)
    # dibujo en medio
    logo = empty(tpos(10, 10) + Vector((0, -0.08, 0)), card); S["logo"] = logo
    cyl(0.56, 0.08, (0, 0, 0), WHT, logo, rot=(math.pi / 2, 0, 0))
    cyl(0.46, 0.1, (0, -0.02, 0), (0.95, 0.55, 0.2), logo, rot=(math.pi / 2, 0, 0))
    cyl(0.22, 0.2, (0, -0.05, 0.05), WHT, logo, rot=(math.pi / 2, 0, 0)); torus(0.13, 0.04, (0.26, -0.08, 0.05), WHT, logo, rot=(math.pi / 2, 0, 0))
    # ---- versiones más grandes (un objeto por versión) ----
    S["vers"] = []
    for v, n in ((2, 25), (3, 29), (4, 33), (40, 177)):
        e = empty(LEJOS)
        back = box((n * M + 0.9, 0.1, n * M + 0.9), (0, 0.06, 0), CARD, e)
        o = qr_mesh(n, M, BLK, "v%d" % v, v); o.parent = e; o.location = (0, -0.02, 0)
        S["vers"].append((v, n, e))
    # ---- cinta con piezas de coche ----
    belt = empty(LEJOS); S["belt"] = belt
    box((40, 3.0, 0.5), (0, 0, 0), (0.2, 0.21, 0.24), belt)
    for k in range(-20, 21): box((0.08, 3.02, 0.52), (k * 1.0, 0, 0), (0.14, 0.15, 0.17), belt)
    S["gears"] = []
    for k in range(4):
        g = empty((0, 0, 0), belt)
        cyl(1.25, 0.6, (0, 0, 1.55), STEEL, g, rot=(math.pi / 2, 0, 0), v=40)
        for j in range(16):
            a = j / 16 * math.tau
            box((0.32, 0.6, 0.34), (1.38 * math.cos(a), 0, 1.55 + 1.38 * math.sin(a)), STEEL, g, rot=(0, -a, 0))
        cyl(0.35, 0.64, (0, 0, 1.55), (0.3, 0.32, 0.36), g, rot=(math.pi / 2, 0, 0))
        box((0.95, 0.04, 0.95), (0.0, -0.33, 1.55 + 0.72), WHT, g)
        st = qr_mesh(21, 0.04, BLK, "st%d" % k, 20 + k); st.parent = g; st.location = (0, -0.36, 1.55 + 0.72)
        S["gears"].append(g)
    S["ph"] = phone_build()
    join_static([cam, card, S["vers"][0][2], S["vers"][1][2], S["vers"][2][2], S["vers"][3][2], belt, S["ph"]["e"]])
    return sc, S

def bit(r, c, t):
    """estado del módulo (r, c) en el instante t: True = negro"""
    fin = (r * 0.7 + c) / (N * 1.7)
    final = finder_bit(r, c) if in_finder(r, c) else ((r + c) % 2 == 0 if timing(r, c) else BASE[r][c] ^ MASKED(r, c))
    if t < T("vamos a inventarlo") + 0.3 + 0.8 * fin: return final
    if t < T("cuadrado negro") + 1.6 * (r * N + c) / (N * N): return False
    b = BASE[r][c]
    if t >= T("así que pones") + 0.6 + 0.04 * (r + c) * 0 and (in_finder(r, c) or timing(r, c)):
        if t >= T("así que pones") + 0.4 + (0 if r < 8 and c < 8 else (0.35 if c > 12 else 0.7)):
            return finder_bit(r, c) if in_finder(r, c) else (r + c) % 2 == 0
    if ZONE(r, c) and t >= T("una zona toda") + 0.05 * (c - 7): b = False
    if t >= T("así que lo mezclas") + 0.4 + 1.6 * c / N and not in_finder(r, c) and not timing(r, c):
        b = (False if ZONE(r, c) else BASE[r][c]) ^ MASKED(r, c)
    return b

def pose(t, S):
    card = S["card"]
    # tarjeta: se tuerce y se endereza
    a0, a1 = T("tu móvil no sabe"), T("al verlos") + 0.6
    tilt = math.radians(25) * (seg(t, T("ni si está") - 0.4, T("ni si está") + 0.4) - seg(t, a1, T("cómo está girado")))
    card.rotation_euler = (0.15 * seg(t, T("ni si está") - 0.4, T("ni si está") + 0.4) * (1 - seg(t, a1, T("cómo está girado"))), tilt, 0)
    show = 1.0 if t < T("haces la cuadrícula") + 0.3 else 0.0
    card.location = QC if show else LEJOS
    # módulos
    pop_f = T("así que pones") + 0.4
    for (r, c), (piv, b) in S["tiles"].items():
        on = bit(r, c, t)
        col = BLK
        if in_finder(r, c) and pop_f <= t < T("al verlos") + 2.5 and on: col = BLUE
        if T("porque guardas") <= t < T("en el nivel") and on and not in_finder(r, c) and not timing(r, c):
            k = GRP[(r, c)]; ph = (t - T("porque guardas")) * 2.2
            col = GROUPS[k] if int(ph) % 4 == k or t > T("repartida") else BLK
        dm = DMG_RANK.get((r, c), 10 ** 6)
        if T("en el nivel") <= t < T("por eso algunos") + 0.3:
            frac = 0.30 * seg(t, T("se recupera") - 0.2, T("datos", fin=True))
            if dm < frac * len(DAMAGE): col = RED; on = True
        if CENTER(r, c) and t >= T("por eso algunos") + 0.6: on = False
        sc = 1.0 if on else 0.0
        # rebote al cambiar de estado en el barrido de la máscara y al aparecer las esquinas
        bump = 0.0
        if in_finder(r, c): bump = 0.5 * math.sin(math.pi * seg(t, pop_f, pop_f + 0.5)) if t < pop_f + 0.6 else 0
        piv.scale = (max(sc, 1e-3), 1 + bump * 4 if sc else 1, max(sc, 1e-3))
        set_color(b, col if on else WHT)
    # el trozo se rompe y cae
    k0 = T("puedes romper") + 0.6
    u = max(0.0, t - k0)
    ch = S["chunk"]
    if t > k0:
        ch.location = Vector((0.6 * u, -2.2 * u, -0.6 * u - 4.5 * u * u)); ch.rotation_euler = (-1.2 * u, 0.6 * u, 0.3 * u)
    else:
        ch.location = Vector((0, 0, 0)); ch.rotation_euler = (0, 0, 0)
    if t > k0 + 2.5: ch.location = LEJOS
    # cuadrícula
    g = seg(t, T("así que usas"), T("así que usas") + 0.7) * (1 - seg(t, T("pero hay un"), T("pero hay un") + 0.5))
    S["gl"].scale = (1, 1, 1) if g > 0.01 else (1e-3, 1e-3, 1e-3)
    S["gl"].location = (0, -0.075 - 0.5 * (1 - g), 0)
    # enlace
    lp = seg(t, T("quieres guardar"), T("quieres guardar") + 0.4) * (1 - seg(t, T("cuadrado negro") - 0.4, T("cuadrado negro") + 0.3))
    S["link"].scale = (max(lp, 1e-3),) * 3
    S["link"].location = (0, -0.6 - 0.5 * math.sin(t * 2.0) * 0.2, 0.0 + 0.1 * math.sin(t * 1.7))
    # barrido de la máscara
    m0 = T("así que lo mezclas") + 0.4
    if m0 - 0.1 <= t <= m0 + 1.7:
        S["sweep"].location = (-N * M / 2 + N * M * (t - m0) / 1.6, -0.12, 0)
    else: S["sweep"].location = LEJOS
    # contador de blancos
    c0, c1 = T("el móvil se pierde"), T("así que lo mezclas")
    if c0 <= t < c1:
        k = min(6, int((t - c0) / 0.25)); S["cnt"].location = tpos(10, 7 + k) + Vector((0, -0.12, 0))
        set_color(S["cnt"], YEL if t < c0 + 1.6 else RED)
    else: S["cnt"].location = LEJOS
    # líneas entre esquinas
    lp = seg(t, T("al verlos"), T("al verlos") + 0.6) * (1 - seg(t, T("pero ahora tienes") - 0.3, T("pero ahora tienes")))
    tl, tr, bl = tpos(3, 3) + Vector((0, -0.15, 0)), tpos(3, 17) + Vector((0, -0.15, 0)), tpos(17, 3) + Vector((0, -0.15, 0))
    if lp > 0.01:
        bar_set(S["L1"], tl, tl.lerp(tr, lp)); bar_set(S["L2"], tl, tl.lerp(bl, lp))
    else:
        bar_set(S["L1"], LEJOS, LEJOS + Vector((0, 0, 0.01))); bar_set(S["L2"], LEJOS, LEJOS + Vector((0, 0, 0.01)))
    mp = win01(t, T("y como falta"), T("pero ahora tienes"), 0.3, 0.3)
    S["miss"].scale = (max(mp, 1e-3) * (1 + 0.08 * math.sin(t * 9)),) * 3
    set_color(S["miss"], RED if t < T("sabe cuál") + 0.3 else GRN)
    # dibujo en medio
    lg = seg(t, T("por eso algunos") + 0.5, T("por eso algunos") + 1.0)
    S["logo"].scale = (max(lg, 1e-3),) * 3
    # versiones
    v0 = T("haces la cuadrícula") + 0.3
    vt = [v0, T("cada versión") + 0.2, T("cada versión") + 1.2, T("hasta ciento") + 0.8]
    for i, (v, n, e) in enumerate(S["vers"]):
        on = vt[i] <= t < (vt[i + 1] if i + 1 < len(vt) else T("lo inventó") + 0.5)
        e.location = QC if on else LEJOS
        if on:
            p = seg(t, vt[i], vt[i] + 0.35); e.scale = (0.92 + 0.08 * p,) * 3
    # cinta con piezas
    b0 = T("lo inventó") - 0.2
    if t >= b0:
        S["belt"].location = Vector((0, -40, 0.2))
        for k, g in enumerate(S["gears"]):
            g.location = Vector((-14 + 4.6 * k + 1.15 * (t - b0) + 18 * (1 - seg(t, b0, b0 + 0.9)), 0, 0.25))
            g.rotation_euler = (0, 0, 0)
    else: S["belt"].location = LEJOS
    # móvil
    ph = S["ph"]; pe = ph["e"]
    P = None
    s1 = T("la más pequeña"); s2 = T("tu móvil no sabe")
    kf = [(0.0, (-2.3, -4.4, 1.2), 0.35), (0.8, (-1.3, -4.0, 1.75), 0.15), (T("cómo lee") + 0.2, (-1.25, -4.0, 1.8), 0.15),
          (T("vamos a inventarlo"), (-4.0, -5.0, -3.0), 0.4)]
    if t < T("vamos a inventarlo") + 0.1:
        P = keyed(t, [(a, Vector(p)) for a, p, _ in kf]); yaw = keyed(t, [(a, y) for a, _, y in kf])
    elif s2 - 0.6 <= t < T("al verlos") + 3.2:
        P = keyed(t, [(s2 - 0.6, Vector((-4.5, -7, -1))), (s2, Vector((-1.35, -4.6, 1.0))), (T("al verlos") + 2.6, Vector((-1.35, -4.6, 1.0))), (T("al verlos") + 3.2, Vector((-4.5, -7, -2)))]); yaw = 0.22
    elif T("y se sigue") - 0.6 <= t < T("porque guardas"):
        P = keyed(t, [(T("y se sigue") - 0.6, Vector((-4.5, -7, -1))), (T("y se sigue"), Vector((-1.35, -4.6, 1.0))), (T("porque guardas") - 0.4, Vector((-1.35, -4.6, 1.0))), (T("porque guardas"), Vector((-4.5, -7, -2)))]); yaw = 0.22
    elif t >= T("para seguir") - 0.6:
        P = keyed(t, [(T("para seguir") - 0.6, Vector((-4.0, -47.5, -1))), (T("para seguir"), Vector((-1.5, -45.0, 2.3))), (99, Vector((-1.5, -45.0, 2.3)))]); yaw = 0.25
    if P is None: pe.location = LEJOS
    else:
        pe.location = P; pe.rotation_euler = (math.pi / 2 - 0.05, 0, -yaw + 0.03 * math.sin(t * 2.3))
    # pantalla del móvil
    menu_on = T("tu móvil abre") - 0.3 <= t < T("vamos a inventarlo") + 0.2 or T("y se sigue") + 0.5 <= t < T("porque guardas")
    ph["menu"].scale = (1, 1, 1) if menu_on else (1e-3,) * 3
    ph["vf"].scale = (1e-3,) * 3 if menu_on else (1, 1, 1)
    ph["scan"].location = (0, 0.55 * math.sin(t * 5.0), 0.02)
    ok = (T("y en menos") - 0.3 <= t < T("tu móvil abre") - 0.3) or (T("y se sigue") <= t < T("y se sigue") + 0.5) or (T("al verlos") + 0.2 <= t < T("al verlos") + 3.2) or t >= T("para seguir") + 0.4
    bad = s2 + 0.3 <= t < T("al verlos") + 0.2
    ph["st"].scale = (1, 1, 1) if (ok or bad) else (1e-3,) * 3
    set_color(ph["st"], GRN if ok else RED)
    ph["q"].scale = (1, 1, 1) if bad else (1e-3,) * 3
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def CAM():
    F = ((0, -12.2, 2.7), (0, 0, 3.0), 40)
    c = [
        (0.0, (-1.0, -11.6, 2.2), (-0.3, 0, 2.8), 36), (2.5, (-0.7, -12.0, 2.3), (-0.2, 0, 2.85), 36),
        (T("cómo lee"), (-0.3, -12.0, 2.5), (0, 0, 3.0), 38),
        (T("vamos a inventarlo") + 0.2, (0.6, -6.5, 2.6), (0.2, 0, 3.1), 36),
        (T("quieres guardar"), (0.3, -9.0, 2.4), (0, 0, 2.8), 36),
        (T("así que usas"), (0, -11.8, 2.6), (0, 0, 3.0), 40),
        (T("la más pequeña"), (0.3, -12.0, 2.7), (0, 0, 3.0), 40),
        (T("pero hay un"), (-0.6, -12.6, 2.5), (-0.3, 0, 2.9), 40),
        (T("así que pones"), (0.4, -11.6, 2.6), (0, 0, 3.0), 40),
        (T("y como falta"), (0.8, -11.8, 2.4), (0.3, 0, 2.8), 40),
        (T("pero ahora tienes"), (0.2, -12.0, 2.8), (0.1, 0, 3.0), 40),
        (T("el móvil se pierde"), (0.0, -11.6, 2.8), (0.0, 0, 3.0), 40),
        (T("así que lo mezclas"), (0.0, -11.0, 2.8), (0, 0, 3.0), 40),
        (T("y aquí viene"), (0.3, -11.6, 2.6), (0, 0, 3.0), 40),
        (T("puedes romper") + 0.4, (1.4, -10.4, 1.8), (0.5, 0, 2.6), 38),
        (T("y se sigue"), (-0.4, -12.2, 2.6), (-0.2, 0, 2.9), 40),
        (T("en el nivel"), (0.2, -11.4, 2.7), (0, 0, 3.0), 40),
        (T("por eso algunos"), (0.0, -11.0, 2.8), (0, 0, 3.0), 40),
        (T("haces la cuadrícula"), (0.0, -12.5, 2.7), (0, 0, 3.0), 40),
        (T("cada versión"), (0.0, -15.5, 2.6), (0, 0, 3.0), 40),
        (T("hasta ciento"), (0.0, -20.0, 2.6), (0, 0, 3.0), 40),
        (T("hasta ciento") + 0.9, (0.0, -58.0, 1.5), (0, 0, 3.0), 40),
        (T("hasta ciento") + 1.8, (0.0, -76.0, 1.0), (0, 0, 3.0), 40),
        (T("lo inventó") - 0.1, (0.0, -78.0, 1.0), (0, 0, 3.0), 40),
        (T("lo inventó") + 0.9, (0.0, -53.0, 3.6), (0, -40, 2.3), 38),
        (T("para seguir"), (0.6, -52.0, 3.4), (-0.4, -40, 2.4), 38),
        (DUR + 1, (0.4, -51.5, 3.4), (-0.4, -40, 2.4), 38),
    ]
    return c

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    mw = S["card"].matrix_world
    tp = lambda r, c: Pj(mw @ (tpos(r, c) + Vector((0, -0.1, 0))))
    out = {"qr": tp(10, 10), "top": Pj(mw @ Vector((0, 0, N * M / 2 + 0.2))), "tl": tp(0, 0), "tr": tp(0, 20), "bl": tp(20, 0), "br": tp(17, 17),
           "f1": tp(3, 3), "f2": tp(3, 17), "f3": tp(17, 3), "t1": tp(*ONE), "t0": tp(*ZERO), "zone": tp(10, 10), "chunk": tp(16, 12),
           "logo": tp(10, 10), "ph": Pj(S["ph"]["e"].matrix_world.translation), "gear": Pj(Vector((0, -40.5, 2.6)))}
    return out

ONE = next((r, c) for r in range(9, 13) for c in range(9, 13) if BASE[r][c])
ZERO = next((r, c) for r in range(9, 13) for c in range(9, 13) if not BASE[r][c])

if __name__ == "__main__":
    run("qr", build, pose, anchors)
