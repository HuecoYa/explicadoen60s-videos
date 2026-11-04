# «Así funciona la pantalla táctil»: un dedo gigante toca el móvil; el cristal se separa y aparece la rejilla de cables;
# cada cruce guarda carga (bolita cian); el dedo se la lleva y el número baja; barrido de la rejilla; dos dedos; guante,
# puntero y gotas de agua.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector
from pantalla_ov import (T, DUR, NX, NY, GX, GY, GZ, P, Q, GOTAS, dedo1, dedo2, puntero, guante, usa_puntero, gotas_on,
                         toques, carga, nodo_cercano)

BODY = (0.16, 0.17, 0.2); DISP = (0.05, 0.06, 0.1); GLASS = (0.75, 0.88, 1.0); HW = (0.25, 0.55, 1.0); VW = (1.0, 0.55, 0.2)
CHG = (0.35, 0.95, 1.0); LOW = (0.95, 0.25, 0.25); SKIN = (0.93, 0.7, 0.58); NAIL = (0.97, 0.82, 0.78); WOOL = (0.85, 0.2, 0.25)
SPARK = (1.0, 0.9, 0.3); WATER = (0.55, 0.8, 1.0); TABLE = (0.2, 0.22, 0.27)
DIR = Vector((0.62, -0.25, 0.75)).normalized()      # hacia dónde va el dedo desde la punta
DIR2 = Vector((-0.62, -0.25, 0.75)).normalized()

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def dedo(direc, col_skin):
    """punta en el origen del vacío; el dedo sale en la dirección direc"""
    e = empty((0, 0, -20)); parts = []
    up = direc.cross(Vector((0, 1, 0))).cross(direc).normalized()
    if up.z < 0: up = -up
    c = Vector((0, 0, 0.62))
    parts.append(sph(0.66, c, col_skin, parent=e, unique=True))
    o = cyl(0.66, 9, c + direc * 4.5, col_skin, parent=e, unique=True)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direc); parts.append(o)
    for k, d in enumerate((2.3, 4.6)):
        tr = torus(0.66, 0.035, c + direc * d, (0.82, 0.58, 0.48), parent=e, unique=True)
        tr.rotation_mode = 'QUATERNION'; tr.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direc); parts.append(tr)
    n = sph(0.46, c + direc * 0.55 + up * 0.5, NAIL, parent=e, scale=(1, 1, 1), unique=True)
    n.rotation_mode = 'QUATERNION'; n.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(up); n.scale = (1, 1.25, 0.28)
    puno = torus(0.7, 0.16, c + direc * 6.5, WOOL, parent=e, unique=True)
    puno.rotation_mode = 'QUATERNION'; puno.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direc)
    return e, parts, n, puno

def build():
    sc, cam = scene_setup(world=(0.09, 0.1, 0.14), shadow=0.35)
    S = {"cam": cam}
    box((80, 80, 0.1), (0, 0, -0.05), TABLE)
    # móvil
    rounded_slab(7.3, 15.4, 1.0, 0.75, (0, 0, 0), BODY)
    rounded_slab(6.9, 15.0, 0.85, 0.05, (0, 0, 0.75), DISP)
    S["iconos"] = []
    rng = random.Random(3)
    cols = [(0.95, 0.45, 0.3), (0.3, 0.75, 0.45), (0.35, 0.6, 1.0), (0.98, 0.8, 0.3), (0.7, 0.45, 0.95), (0.95, 0.35, 0.6)]
    for i in range(4):
        for j in range(6):
            o = rounded_slab(1.1, 1.1, 0.3, 0.03, (-2.4 + 1.6 * i, -4.2 + 2.0 * j, 0.8), cols[(i + 2 * j) % 6], unique=True)
            S["iconos"].append((o, cols[(i + 2 * j) % 6]))
    # chip (arriba, debajo del cristal)
    S["chip"] = box((1.7, 0.7, 0.14), (0, 6.65, 0.87), (0.08, 0.08, 0.1), unique=True)
    for k in range(7): box((0.05, 0.25, 0.04), (-0.6 + 0.2 * k, 6.2, 0.82), (0.8, 0.75, 0.45))
    # rejilla (capa que se separa)
    S["capa"] = empty((0, 0, 0))
    S["hw"] = []; S["vw"] = []
    for y in GY:
        o = cyl(0.035, 6.3, (0, y, 0.87), HW, parent=S["capa"], rot=(0, math.pi / 2, 0), v=10, unique=True); S["hw"].append(o)
    for x in GX:
        o = cyl(0.035, 13.2, (x, -0.4, 0.9), VW, parent=S["capa"], rot=(math.pi / 2, 0, 0), v=10, unique=True); S["vw"].append(o)
    S["nodos"] = {}
    for i, x in enumerate(GX):
        for j, y in enumerate(GY):
            S["nodos"][(i, j)] = sph(0.11, (x, y, 0.9), CHG, parent=S["capa"], seg=12, unique=True)
    S["barrido"] = box((6.6, 0.5, 0.08), (0, 0, 0.93), (1.0, 0.95, 0.4), parent=S["capa"], unique=True); alpha(S["barrido"], 0.45)
    # cristal (translúcido)
    S["cristal"] = rounded_slab(7.2, 15.3, 1.0, 0.07, (0, 0, GZ - 0.07), GLASS, unique=True); alpha(S["cristal"], 0.22)
    # dedos, puntero, chispas, gotas, ondas
    S["d1"], S["d1p"], S["d1n"], S["d1g"] = dedo(DIR, SKIN)
    S["d2"], S["d2p"], S["d2n"], S["d2g"] = dedo(DIR2, SKIN)
    S["pun"] = empty((0, 0, -20))
    cyl(0.36, 9, Vector((0, 0, 0.4)) + DIR * 4.8, (0.85, 0.87, 0.9), parent=S["pun"]).rotation_euler = Vector((0, 0, 1)).rotation_difference(DIR).to_euler()
    sph(0.42, (0, 0, 0.42), (0.25, 0.25, 0.28), parent=S["pun"])
    S["chispas"] = [sph(0.07, (0, 0, -20), SPARK, seg=8) for _ in range(14)]
    S["gotas"] = []
    for g in GOTAS:
        o = sph(0.42, (g[0], g[1], -20), WATER, scale=(1, 1, 0.35), unique=True); alpha(o, 0.6); S["gotas"].append(o)
    S["onda"] = torus(0.5, 0.04, (P[0], P[1], -20), (1, 1, 1), unique=True); alpha(S["onda"], 0.8)
    dyn = [cam, S["capa"], S["cristal"], S["d1"], S["d2"], S["pun"], S["chispas"], S["gotas"], S["onda"], S["chip"],
           [o for o, _ in S["iconos"]]]
    join_static(dyn)
    return sc, S

def cmix(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))

def pose(t, S):
    t_cru, t_rej, t_hor, t_ver, t_cruce, t_mide = T("debajo del cristal"), T("una rejilla"), T("en horizontal"), T("en vertical"), T("en cada cruce"), T("y el móvil mide")
    # explosión de capas: cristal arriba, rejilla en medio
    ex = seg(t, t_cru, t_cru + 1.0) * (1 - seg(t, t_mide, t_mide + 1.2))
    S["cristal"].location.z = 3.6 * ex
    S["capa"].location.z = 1.8 * ex
    # cables que crecen
    gh = seg(t, t_rej, t_rej + 1.0) if t < t_hor else 1.0
    hgrow = max(seg(t, t_rej, t_rej + 1.4), 0)
    vgrow = seg(t, t_rej + 0.6, t_rej + 2.0)
    for o in S["hw"]: o.scale = (1, 1, max(hgrow, 0.001))
    for o in S["vw"]: o.scale = (1, 1, max(vgrow, 0.001))
    hl_h = win01(t, t_hor - 0.1, t_ver - 0.1); hl_v = win01(t, t_ver - 0.1, t_cruce)
    # barrido de filas
    t_rep, t_300 = T("repasa toda"), T("más de trescientas")
    barre = (t_mide - 0.2 < t < T("tu dedo conduce")) or (T("el chip busca") < t < T("y ahí está")) or (t_rep - 0.2 < t < T("así sabe si"))
    vel = 0.7 if t < t_300 else 0.22
    fila = (t / vel) % 1.0
    yb = mix(GY[0], GY[-1], fila)
    S["barrido"].location = (0, yb, 0.93) if barre else (0, 0, -30)
    for k, o in enumerate(S["hw"]):
        c = cmix(HW, (0.75, 0.9, 1.0), hl_h)
        if barre and abs(GY[k] - yb) < 0.4: c = (1.0, 0.95, 0.5)
        set_color(o, c)
    for o in S["vw"]: set_color(o, cmix(VW, (1.0, 0.85, 0.5), hl_v))
    # cruces con carga
    tq = toques(t)
    for (i, j), o in S["nodos"].items():
        app = seg(t, t_cruce + 0.03 * (i + j), t_cruce + 0.03 * (i + j) + 0.4)
        q = carga(GX[i], GY[j], t, tq)
        u = max(0.0, min(1.0, (100 - q) / 38))
        o.scale = (max(app * (1 - 0.45 * u), 0.001),) * 3
        set_color(o, cmix(CHG, LOW, u))
    # iconos: se apagan cuando aparece la rejilla
    dim = seg(t, t_rej, t_rej + 1.0)
    for o, c in S["iconos"]: set_color(o, cmix(c, DISP, 0.8 * dim))
    # dedos
    p1 = Vector(dedo1(t)); S["d1"].location = p1 if not usa_puntero(t) else (0, 0, -30)
    g = guante(t)
    for o in S["d1p"]: set_color(o, cmix(SKIN, WOOL, g))
    set_color(S["d1n"], cmix(NAIL, WOOL, g)); S["d1g"].scale = (max(g, 0.001),) * 3
    S["d1"].location.z += 0.0
    p2 = Vector(dedo2(t)); S["d2"].location = p2; S["d2g"].scale = (0.001,) * 3
    S["pun"].location = Vector(puntero(t)) if usa_puntero(t) else (0, 0, -30)
    # chispas: la carga sube del cruce al dedo / puntero
    src = None
    if T("cuando lo acercas") + 0.6 < t < T("el chip busca"): src = p1
    elif T("goma conductora") - 0.3 < t < T("y con el dedo mojado") - 0.3: src = Vector(puntero(t))
    for k, c in enumerate(S["chispas"]):
        if src is None: c.location = (0, 0, -20); continue
        u = (t * 1.3 + k / len(S["chispas"])) % 1.0
        r = random.Random(k); off = Vector((r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25), 0))
        a = Vector((src.x, src.y, GZ - 0.05)) + off; b = src + Vector((0, 0, 0.6)) + DIR * 2.5 + off
        c.location = a.lerp(b, u); c.scale = ((1 - u) * 1.2 + 0.3,) * 3
    # gotas
    for o, a in zip(S["gotas"], gotas_on(t)):
        gx, gy = o.location.x, o.location.y
        o.location.z = GZ + 0.02 if a > 0 else -20; o.scale = (max(a, 0.001), max(a, 0.001), max(0.35 * a, 0.001))
    # onda en cada toque inicial
    u = (t % 0.75) / 0.75
    if t < 2.0:
        S["onda"].location = (P[0], P[1], GZ + 0.03); S["onda"].scale = (0.6 + 2.2 * u,) * 3; alpha(S["onda"], 0.8 * (1 - u))
    else: S["onda"].location.z = -20
    # el chip parpadea cuando busca
    set_color(S["chip"], (0.15, 0.4, 0.9) if win01(t, T("el chip busca"), T("pero no mira")) > 0.5 and (t * 6) % 1 < 0.5 else (0.08, 0.08, 0.1))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def orb(tg, d, el, az, lens=35):
    tg = Vector(tg); el, az = math.radians(el), math.radians(az)
    pos = tg + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return (tuple(pos), tuple(tg), lens)

PC = (P[0], P[1], GZ)
def CAM():
    C0 = (0, 0, 1.0)
    return [(0.0,) + orb(PC, 7.5, 38, -28), (2.4,) + orb(PC, 8.5, 42, -18), (T("debajo del cristal") - 0.2,) + orb(PC, 10, 40, -12),
            (T("debajo del cristal") + 1.2,) + orb((0.8, -1.0, 3.4), 19, 20, -40), (T("en horizontal"),) + orb((0.6, -0.5, 3.0), 18, 26, -32),
            (T("en cada cruce"),) + orb((0.5, 0.5, 1.6), 15, 40, -22), (T("y el móvil mide") + 0.6,) + orb(PC, 11, 55, -14),
            (T("tu dedo conduce"),) + orb(PC, 11, 52, -20), (T("cuando lo acercas"),) + orb(PC, 9, 48, -22),
            (T("de golpe"),) + orb(PC, 8, 58, -14), (T("el chip busca"),) + orb((0.4, 2.5, 1.0), 15, 55, -8),
            (T("y ahí está"),) + orb(PC, 10, 58, -12), (T("repasa toda"),) + orb(C0, 17.5, 66, -8),
            (T("así sabe si"),) + orb((0.6, -0.6, 1.0), 13, 58, -14), (T("y si pones dos"),) + orb((-0.5, -0.5, 1.0), 15, 62, -8),
            (T("hacer zoom", fin=True),) + orb((-0.5, -0.5, 1.0), 17, 62, -4), (T("con guantes") - 0.4,) + orb(PC, 9.5, 45, -22),
            (T("por eso los punteros"),) + orb(PC, 9, 45, -26), (T("y con el dedo mojado"),) + orb((0, 1.5, 1.0), 16, 58, -12),
            (T("y la pantalla se"),) + orb((0, 1.5, 1.0), 18, 62, -8), (DUR + 2,) + orb((0, 1.0, 1.0), 21, 60, -14)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); z = S["capa"].location.z
    a = {"P": Pj((P[0], P[1], GZ + z)), "cristal": Pj((-2.6, -5.5, GZ + S["cristal"].location.z)), "rejilla": Pj((-2.6, -5.0, 0.9 + z)),
         "hfila": Pj((-1.5, GY[3], 0.9 + z)), "vcol": Pj((GX[2], GY[8], 0.9 + z)), "chip": Pj((0, 6.65, 1.0)),
         "punta": Pj(tuple(Vector(puntero(t)) + Vector((0, 0, 0.3))))}
    i0, j0 = nodo_cercano(*P)
    for i in range(max(0, i0 - 1), min(NX, i0 + 2)):
        for j in range(max(0, j0 - 1), min(NY, j0 + 2)): a["n%d_%d" % (i, j)] = Pj((GX[i], GY[j], 0.9 + z))
    for x, y, s in toques(t):
        i, j = nodo_cercano(x, y); a["n%d_%d" % (i, j)] = Pj((GX[i], GY[j], 0.9 + z))
    for k, g in enumerate(GOTAS): a["g%d" % k] = Pj((g[0], g[1], GZ))
    return a

if __name__ == "__main__":
    run("pantalla", build, pose, anchors)
