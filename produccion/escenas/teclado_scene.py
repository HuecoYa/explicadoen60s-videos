# «¿Cómo sabe el ordenador qué tecla pulsas?»: dedos tecleando en primer plano; las teclas se levantan y aparecen las
# láminas (pistas de arriba, separador con agujeros, pistas de abajo); un dedo aprieta y el contacto de arriba baja por el
# agujero hasta tocar el de abajo; la cuadrícula de filas y columnas con sus cables hasta el chip; el chip mete corriente
# columna a columna y la fila 3 responde en la columna 5; barrido sin parar; tres teclas a la vez hacen aparecer una
# cuarta fantasma; los diodos cortan el camino de vuelta y las teclas vuelven a su sitio.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("teclado")
BG = (0.08, 0.085, 0.11); DESK = (0.3, 0.24, 0.2); CASE = (0.17, 0.18, 0.21); KEY = (0.9, 0.9, 0.92)
SHEET = (0.6, 0.78, 1.0); BSHEET = (0.2, 0.22, 0.28); SPACER = (0.95, 0.95, 0.97); TRACE = (0.45, 0.62, 0.95); RTRACE = (0.85, 0.55, 0.3); PAD = (0.8, 0.82, 0.86)
SKIN = (0.93, 0.7, 0.56); CHIP = (0.1, 0.1, 0.12); PCB = (0.1, 0.4, 0.25); METAL = (0.75, 0.77, 0.8)
COLON = (1.0, 0.82, 0.2); ROWON = (0.3, 0.95, 0.5); GHOST = (1.0, 0.3, 0.3); DIOD = (0.92, 0.92, 0.88)
LEJOS = (0, 0, -300)
NR, NC = 6, 18
def XC(c): return c - 8.5
def YR(r): return 2.5 - r
CHIPX = -11.6
PR = (2, 4)                              # fila 3, columna 5 (pulsada)
GH = [(1, 1), (1, 5), (4, 5)]; GQ = (4, 1)  # tres teclas y la fantasma
ZT0, ZT1, ZS0, ZS1 = 0.14, 1.25, 0.07, 0.62

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def poly(pts):
    pts = [Vector(p) for p in pts]; L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    return pts, L
def at(path, s):
    pts, L = path; s = max(0.0, min(L[-1], s))
    for i in range(len(pts) - 1):
        if L[i] <= s <= L[i + 1]: return pts[i].lerp(pts[i + 1], (s - L[i]) / max(L[i + 1] - L[i], 1e-6))
    return pts[-1]

def joinl(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); return bpy.context.object

def wire(pts, r, m, parent):
    out = []
    for a, b in zip(pts, pts[1:]):
        o = bar_obj(None, r, parent=parent); o.data.materials.append(m); bar_set(o, a, b); o.location = Vector(a); out.append(o)
    return joinl(out) if len(out) > 1 else out[0]

def col_bus(c):
    yb = 3.25 + 0.05 * c
    return [(XC(c), 3.0, 0), (XC(c), yb, 0), (-10.4, yb, 0), (CHIPX + 0.7, 0.15 + 0.055 * c, 0)]
def row_bus(r):
    return [(-9.3, YR(r), 0), (-10.2, YR(r), 0), (CHIPX + 0.7, -1.15 + 0.16 * r, 0)]

def TT():
    d = {}
    d["has pulsado"] = T("has pulsado", 2); d["cada tecla"] = T("cada tecla", 2)
    for k in ("y no tiene", "cómo sabe", "vamos a abrirlo", "debajo de cada", "dos capas", "y entre ellas", "una capa con", "al pulsar",
              "la capa de arriba", "toca la de", "y cierra", "pero no hay", "las pistas forman", "filas y", "columnas",
              "con ocho", "dieciocho", "ciento cuarenta", "con solo", "ahora un", "un pequeño chip", "mete corriente", "y mira",
              "luego en la segunda", "luego en la tercera", "si la corriente", "y aquí viene", "el chip repasa",
              "sin parar", "y en un teclado", "se lo cuenta", "mil veces", "pero si pulsas", "la corriente puede", "y aparece",
              "por eso los", "una válvula", "en un solo", "sígueme"):
        d[k] = T(k)
    return d
TM = TT()

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35, light_rot=50)
    S = {"cam": cam}
    box((80, 60, 0.4), (0, 0, -0.75), DESK)
    box((23.2, 7.8, 0.4), (-1.6, 0.1, -0.35), CASE)
    for sx, w in ((-13.1, 0.3), (9.85, 0.3)): box((w, 7.8, 1.2), (sx, 0.1, 0.05), CASE)
    for sy in (-3.85, 4.05): box((23.2, 0.3, 1.2), (-1.6, sy, 0.05), CASE)
    box((2.8, 5.0, 0.1), (CHIPX, 0, -0.1), PCB)
    box((1.4, 2.6, 0.9), (CHIPX, 0, 0.35), CHIP)
    for k in range(7):
        for sx in (-1, 1): box((0.25, 0.12, 0.08), (CHIPX + sx * 0.78, -1.05 + 0.35 * k, 0.0), METAL)
    # lámina de abajo (con las filas)
    S["BOT"] = BOT = empty((0, 0, 0))
    box((19.2, 6.9, 0.03), (0.1, 0.05, 0.0), BSHEET, parent=BOT)
    S["rowm"] = [mat(RTRACE, unique=True) for _ in range(NR)]
    S["roww"] = []
    for r in range(NR):
        S["roww"].append(wire([(9.2, YR(r), 0.035), (-9.3, YR(r), 0.035)] + [(x, y, 0.035) for x, y, _ in row_bus(r)[1:]], 0.05, S["rowm"][r], BOT))
        for c in range(NC):
            if (r, c) not in GH + [GQ, PR]: cyl(0.26, 0.02, (XC(c), YR(r), 0.03), PAD, parent=BOT, v=20)
    S["bpad"] = {}
    for rc in GH + [GQ, PR]:
        S["bpad"][rc] = cyl(0.26, 0.02, (XC(rc[1]), YR(rc[0]), 0.03), PAD, parent=BOT, v=20, unique=True)
    # separador con agujeros
    S["SPL"] = SPL = empty((0, 0, ZS0))
    sp = box((19.2, 6.9, 0.05), (0.1, 0.05, 0), SPACER, parent=SPL, unique=True)
    holes = [cyl(0.36, 0.4, (XC(c), YR(r), ZS0), PAD, v=20) for r in range(NR) for c in range(NC)]
    hj = joinl(holes); hj.parent = None
    md = sp.modifiers.new("b", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = hj; md.solver = 'FLOAT'
    bpy.context.view_layer.objects.active = sp; bpy.ops.object.modifier_apply(modifier="b")
    bpy.data.objects.remove(hj, do_unlink=True)
    alpha(sp, 0.55); S["spacer"] = sp
    # lámina de arriba (con las columnas)
    S["TOP"] = TOP = empty((0, 0, ZT0))
    S["topsheet"] = box((19.2, 6.9, 0.03), (0.1, 0.05, 0.0), SHEET, parent=TOP, unique=True); alpha(S["topsheet"], 0.22)
    S["colm"] = [mat(TRACE, unique=True) for _ in range(NC)]
    for c in range(NC):
        wire([(XC(c), -3.0, -0.03)] + [(x, y, -0.03) for x, y, _ in col_bus(c)], 0.05, S["colm"][c], TOP)
        for r in range(NR):
            if (r, c) not in GH + [GQ, PR]: cyl(0.26, 0.02, (XC(c), YR(r), -0.035), PAD, parent=TOP, v=20)
    S["tpad"] = {}
    for rc in GH + [GQ, PR]:
        S["tpad"][rc] = cyl(0.26, 0.04, (XC(rc[1]), YR(rc[0]), -0.035), PAD, parent=TOP, v=20, unique=True)
    # teclas
    S["KEYS"] = KEYS = empty((0, 0, 0))
    S["keys"] = {}
    for r in range(NR):
        for c in range(NC):
            if r == 5 and 4 <= c <= 10 and c != 7: continue
            w = 6.8 if (r == 5 and c == 7) else 0.84
            cx = XC(c) if not (r == 5 and c == 7) else XC(7)
            k = rounded_slab(w, 0.84, 0.12, 0.38, (cx, YR(r), 0.32), KEY, parent=KEYS)
            S["keys"][(r, c)] = k
    S["keymat"] = S["keys"][(0, 0)].active_material
    # diodos (uno por tecla), en un solo objeto
    ds = []
    for r in range(NR):
        for c in range(NC):
            ds.append(cyl(0.13, 0.42, (XC(c), YR(r), 0.33), DIOD, v=12))
            ds.append(cyl(0.135, 0.08, (XC(c), YR(r), 0.47), (0.1, 0.1, 0.12), v=12))
    S["diod"] = joinl(ds); S["diod"]["o"] = tuple(S["diod"].location); S["diod"].location = LEJOS
    # marcas: fantasma, contacto
    S["ghost"] = cyl(0.5, 0.06, LEJOS, GHOST, v=24, unique=True)
    S["okm"] = cyl(0.42, 0.05, LEJOS, ROWON, v=24, unique=True)
    # dedos
    S["fing"] = [(bar_obj(SKIN, 0.3), sph(0.3, LEJOS, SKIN, seg=16)) for _ in range(4)]
    S["dots"] = [sph(0.15, LEJOS, COLON, seg=8, unique=True) for _ in range(90)]
    dyn = [cam, BOT, SPL, TOP, KEYS, S["diod"], S["ghost"], S["okm"], S["dots"]] + [x for f in S["fing"] for x in f]
    join_static(dyn)
    return sc, S

# ---------- estado ----------
def explode(t):
    m = TM
    return seg(t, m["vamos a abrirlo"], m["debajo de cada"] + 1.2) * (1 - seg(t, m["sígueme"] - 0.4, m["sígueme"] + 0.5))
def keys_lift(t):
    m = TM
    return seg(t, m["vamos a abrirlo"] - 0.1, m["vamos a abrirlo"] + 0.9) * (1 - seg(t, m["sígueme"] - 0.3, m["sígueme"] + 0.5))
def zt(t): return mix(ZT0, ZT1, explode(t))
def zs(t): return mix(ZS0, ZS1, explode(t))

def pr_down(t):
    m = TM
    a = seg(t, m["la capa de arriba"] - 0.2, m["toca la de"] + 0.1) * (1 - seg(t, m["pero no hay"] + 0.6, m["pero no hay"] + 1.2))
    b = seg(t, m["si la corriente"] - 0.6, m["si la corriente"]) * (1 - seg(t, m["sin parar"] + 1.0, m["pero si pulsas"]))
    return max(a, b)
def gh_down(t):
    m = TM
    return seg(t, m["pero si pulsas"] + 0.3, m["pero si pulsas"] + 1.0) * (1 - seg(t, m["sígueme"] - 0.7, m["sígueme"] - 0.2))

def scan_col(t):
    """columna con corriente (o None)"""
    m = TM
    if m["y cierra"] <= t < m["pero no hay"] + 0.5: return PR[1]
    if m["mete corriente"] <= t < m["luego en la segunda"]: return 0
    if m["luego en la segunda"] <= t < m["luego en la tercera"]: return 1
    if m["luego en la tercera"] <= t < m["si la corriente"]: return 2
    if m["si la corriente"] <= t < m["si la corriente"] + 0.7: return 3
    if m["si la corriente"] + 0.7 <= t < m["y aquí viene"]: return 4
    if m["el chip repasa"] <= t < m["pero si pulsas"]:
        f = 6 if t < m["y en un teclado"] else 14
        return int((t - m["el chip repasa"]) * f) % NC
    if m["la corriente puede"] - 0.3 <= t < m["sígueme"] - 0.5: return GQ[1]
    return None

def tip_pos(rc, z): return Vector((XC(rc[1]), YR(rc[0]), z))

def pose(t, S):
    m = TM; ZT, ZS = zt(t), zs(t); ex = explode(t)
    S["TOP"].location = (0, 0, ZT); S["SPL"].location = (0, 0, ZS)
    lift = keys_lift(t)
    S["KEYS"].location = (0, 2.5 * lift, 7.0 * lift) if lift < 0.999 else LEJOS
    m_ = S["keymat"]; m_.diffuse_color = (*m_.diffuse_color[:3], 1 - lift); m_.surface_render_method = 'BLENDED'
    # tecleo al principio y al final
    typing = t < m["vamos a abrirlo"] + 0.2 or t > m["sígueme"] + 0.3
    taps = [((1, 3), 0.0), ((2, 6), 0.17), ((1, 9), 0.09), ((3, 12), 0.26)]
    targets = [(2, 2), (1, 5), (3, 8), (2, 11)]
    for k, ((fb, fh), (rc0, ph)) in enumerate(zip(S["fing"], taps)):
        tip = None
        if typing:
            per = 0.42
            seq = [targets[k], rc0, (targets[k][0] + 1, targets[k][1] + 1)]
            n = int((t + ph) / per); u = ((t + ph) / per) % 1.0
            rc = seq[n % 3]
            z = 0.75 + 0.75 * abs(math.sin(math.pi * u)) ** 0.8
            if t > m["vamos a abrirlo"] - 0.3 and t < m["sígueme"]: z += 6 * seg(t, m["vamos a abrirlo"] - 0.3, m["vamos a abrirlo"] + 0.2)
            if t > m["sígueme"]: z += 6 * (1 - seg(t, m["sígueme"] + 0.3, m["sígueme"] + 0.8))
            tip = tip_pos(rc, z) + Vector((0, -0.15, 0))
            key = S["keys"].get(rc)
        # dedo de la demostración
        if k == 0 and m["al pulsar"] - 0.5 < t < m["pero no hay"] + 1.4:
            d = pr_down(t)
            tip = tip_pos(PR, ZT + 0.32 + 1.6 * (1 - seg(t, m["al pulsar"] - 0.5, m["al pulsar"] + 0.3)) - (ZT - 0.08) * d)
            tip.z += 3.0 * seg(t, m["pero no hay"] + 0.4, m["pero no hay"] + 1.4)
        if k == 0 and m["si la corriente"] - 1.2 < t < m["pero si pulsas"]:
            d = pr_down(t)
            tip = tip_pos(PR, ZT + 0.32 + 3.0 * (1 - seg(t, m["si la corriente"] - 1.2, m["si la corriente"] - 0.6)) - (ZT - 0.08) * d)
        if k < 3 and m["pero si pulsas"] - 0.3 < t < m["sígueme"] - 0.2:
            d = gh_down(t); rc = GH[k]
            tip = tip_pos(rc, ZT + 0.32 + 3.0 * (1 - seg(t, m["pero si pulsas"] - 0.3, m["pero si pulsas"] + 0.3)) - (ZT - 0.08) * d)
            tip.z += 4.0 * seg(t, m["por eso los"] - 0.2, m["por eso los"] + 0.6)
        if tip is None: fb.location = LEJOS; fh.location = LEJOS; continue
        demo = (k == 0 and m["al pulsar"] - 0.5 < t < m["pero no hay"] + 1.4) or (k < 3 and m["pero si pulsas"] - 0.3 < t < m["sígueme"] - 0.2)
        fh.location = tip; bar_set(fb, tip, tip + (Vector((0.6, 2.2, 3.0)) if demo else Vector((-0.4, -2.2, 3.0))))
    # teclas que bajan bajo los dedos
    for rc, kobj in S["keys"].items():
        z = 0.32
        for fb, fh in S["fing"]:
            p = fh.location
            if p.z < 1.0 and abs(p.x - XC(rc[1])) < 0.45 and abs(p.y + 0.15 - YR(rc[0])) < 0.45: z = 0.32 - 0.18 * (1.0 - (p.z - 0.75) / 0.25)
        kobj.location.z = min(0.32, max(0.14, z))
    # contactos que bajan
    for rc, o in S["tpad"].items():
        d = pr_down(t) if rc == PR else (gh_down(t) if rc in GH else 0.0)
        o.location.z = -0.035 - (ZT - 0.07) * d
    # columnas y filas con corriente
    col = scan_col(t)
    for c in range(NC):
        S["colm"][c].diffuse_color = (*lin(COLON if c == col else TRACE), 1)
    rows_on = set()
    if col == PR[1] and pr_down(t) > 0.9: rows_on.add(PR[0])
    gpath = col == GQ[1] and gh_down(t) > 0.9
    ghost_on = gpath and t < m["una válvula"] + 0.6
    if ghost_on: rows_on.add(GQ[0])
    for r in range(NR):
        S["rowm"][r].diffuse_color = (*lin(ROWON if r in rows_on and not (r == GQ[0] and ghost_on) else (GHOST if r in rows_on else RTRACE)), 1)
    # marcas
    if col == PR[1] and pr_down(t) > 0.9 and (m["si la corriente"] < t < m["y aquí viene"] + 0.3 or t < m["pero no hay"] + 0.5):
        S["okm"].location = (XC(PR[1]), YR(PR[0]), 0.01)
    else: S["okm"].location = LEJOS
    gq = ghost_on and t > m["y aparece"] - 0.1
    S["ghost"].location = (XC(GQ[1]), YR(GQ[0]), 0.06 + 0.03 * math.sin(t * 20)) if gq else LEJOS
    # diodos
    u = seg(t, m["por eso los"] + 1.2, m["por eso los"] + 2.0) * (1 - seg(t, m["sígueme"] - 0.4, m["sígueme"]))
    S["diod"].location = S["diod"]["o"] if u > 0 else LEJOS; S["diod"].scale = (1, 1, max(u, 0.01))
    # puntos de corriente
    pts = []
    if col is not None and ex > 0.5:
        cp = [(x, y, ZT - 0.03) for x, y, _ in reversed(col_bus(col))] + [(XC(col), -3.0, ZT - 0.03)]
        path = poly([Vector((CHIPX, 0.4, 0.75))] + [Vector(p) for p in cp])
        L = path[1][-1]; v = 7.0 if t < m["el chip repasa"] else 18.0; t0 = m["mete corriente"]
        age = (t - t0) if m["mete corriente"] < t < m["el chip repasa"] else 99
        for k in range(30):
            s = ((t * v) + k * L / 30) % L
            if s > age * 9: continue
            pts.append((at(path, s), COLON))
        ret = []
        if col == PR[1] and pr_down(t) > 0.9:
            ret.append(poly([tip_pos(PR, ZT - 0.03), tip_pos(PR, 0.04), Vector((-9.3, YR(PR[0]), 0.04)), Vector((-10.2, YR(PR[0]), 0.04)),
                             Vector((CHIPX + 0.7, -1.15 + 0.16 * PR[0], 0.04))]))
        if gpath:
            a, b, c3 = GH
            gp = [tip_pos(a, ZT - 0.03), tip_pos(a, 0.04), tip_pos(b, 0.04), tip_pos(b, ZT - 0.03), tip_pos(c3, ZT - 0.03),
                  tip_pos(c3, 0.04), Vector((-9.3, YR(c3[0]), 0.04)), Vector((-10.2, YR(c3[0]), 0.04)), Vector((CHIPX + 0.7, -1.15 + 0.16 * c3[0], 0.04))]
            ret.append(poly(gp))
        blocked = t > m["una válvula"] + 0.6
        for pth in ret:
            L2 = pth[1][-1]
            for k in range(24):
                s = ((t * 5.0) + k * L2 / 24) % L2
                if gpath and pth is ret[-1] and blocked and s > pth[1][2]: continue
                pts.append((at(pth, s), ROWON if not (gpath and pth is ret[-1]) else ((1.0, 0.55, 0.2) if not blocked else GHOST)))
    for k, o in enumerate(S["dots"]):
        if k < len(pts): o.location = pts[k][0]; set_color(o, pts[k][1])
        else: o.location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.04))

def CAM():
    m = TM; k = []
    def add(t, p, g, l): k.append((t, p, g, l))
    F = ((-3.0, -7.4, 4.6), (-0.5, 1.0, 0.3), 36)
    add(0.0, *F)
    add(m["y no tiene"] - 0.2, (-3.0, -7.0, 4.2), (-0.5, 1.0, 0.3), 36)
    add(m["cómo sabe"] + 0.3, (-12, -12, 12), (-1, 0.5, 0), 30)
    add(m["vamos a abrirlo"] + 0.6, (-11, -10, 9), (-2, 0.5, 0.3), 32)
    add(m["debajo de cada"] + 1.2, (-10.5, -8.5, 5.0), (-5.5, -0.8, 0.5), 34)
    add(m["una capa con"], (-10.0, -8.0, 4.4), (-5.5, -0.8, 0.5), 34)
    add(m["al pulsar"] - 0.3, (-3.4, -4.6, 3.0), (-4.6, 0.5, 0.75), 36)
    add(m["al pulsar"] + 1.2, (-3.3, -4.4, 2.9), (-4.6, 0.5, 0.7), 36)
    add(m["y cierra"], (-3.3, -4.5, 3.0), (-4.6, 0.4, 0.7), 36)
    add(m["pero no hay"] - 0.1, (-3.2, -4.8, 3.3), (-4.6, 0.3, 0.7), 36)
    add(m["las pistas forman"] + 0.3, (-15, -10, 15), (-1, 0.5, 0), 30)
    add(m["cada tecla"] + 0.5, (-14, -9, 13), (-1.5, 0.5, 0), 30)
    add(m["con ocho"] + 1.0, (-16, -11, 16), (-2, 0.5, 0), 28)
    add(m["con solo"] + 0.2, (-17, -7, 11), (-7, 0.5, 0), 30)
    add(m["ahora un"] + 0.8, (-16, -5, 7), (-10.5, 0.3, 0.4), 32)
    add(m["mete corriente"] + 0.5, (-14, -9.5, 11), (-7, 0.8, 0), 32)
    add(m["si la corriente"], (-13, -9.5, 11), (-6, 0.8, 0), 32)
    add(m["has pulsado"], (-9, -6.5, 6), (-5, 0.8, 0.3), 34)
    add(m["el chip repasa"] + 0.4, (-15, -11, 15), (-1.5, 0.5, 0), 28)
    add(m["se lo cuenta"] + 0.5, (-14, -11, 14), (-1, 0.5, 0), 28)
    add(m["pero si pulsas"] - 0.2, (-9, -2, 16), (-4.5, 0.5, 0), 30)
    add(m["pero si pulsas"] + 0.8, (-5.8, -7.5, 10.5), (-5.2, 0.2, 0), 32)
    add(m["y aparece"] + 0.5, (-5.6, -7.0, 9.8), (-5.2, 0.0, 0), 32)
    add(m["por eso los"] + 1.0, (-2.4, -3.4, 3.8), (-3.4, 1.0, 0.3), 36)
    add(m["en un solo"], (-2.2, -3.2, 3.6), (-3.4, 1.0, 0.3), 36)
    add(m["sígueme"] + 0.6, *F)
    add(DUR + 2, (-2.2, -5.8, 3.4), (-0.5, 1.2, 0.3), 36)
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); ZT, ZS = zt(t), zs(t)
    return {"top": Pj((-8.5, -3.4, ZT)), "spc": Pj((-5.5, -3.4, ZS)), "bot": Pj((-2.5, -3.4, 0.0)),
            "pr": Pj((XC(PR[1]), YR(PR[0]), ZT + 0.3)), "chip": Pj((CHIPX, 0, 1.0)), "colh": Pj((XC(9), -3.1, ZT)),
            "rowh": Pj((9.3, YR(3), 0.05)), "ghost": Pj((XC(GQ[1]), YR(GQ[0]), 0.4)), "diodo": Pj((XC(5), YR(1) - 0.2, 0.4)),
            "col0": Pj((XC(0), -3.1, ZT)), "col1": Pj((XC(1), -3.1, ZT)), "col2": Pj((XC(2), -3.1, ZT)), "col4": Pj((XC(4), -3.1, ZT)),
            "row2": Pj((9.3, YR(2), 0.05))}

if __name__ == "__main__":
    run("teclado", build, pose, anchors)
