# «¿Y si construyes un parking subterráneo?»: primer plano de un coche bajando la rampa dentro del parking terminado;
# todo desaparece y queda el solar en corte; regla de 10 m y 3 plantas; un agujero sin muros se derrumba; zanjas con
# cuchara, jaula de acero y hormigón (muros pantalla); se vacía la tierra y los muros se doblan con flechas de empuje;
# los forjados los sujetan; nivel freático, el agua empuja hacia arriba y gotea por las juntas; pozo con bomba que la saca;
# vuelve el edificio con coches; moléculas de CO salen del tubo de escape y se acumulan; detectores, ventiladores y
# chimenea sacan el aire viciado, entra aire limpio; al final, un coche en marcha llena el garaje de CO.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("parking")
BG = (0.11, 0.13, 0.18)
GRASS = (0.36, 0.6, 0.32); SOIL = (0.47, 0.34, 0.23); CLAY = (0.55, 0.39, 0.27); WET = (0.3, 0.32, 0.4); VOID = (0.2, 0.16, 0.14)
CON = (0.74, 0.74, 0.74); CON2 = (0.84, 0.84, 0.82); ROAD = (0.25, 0.26, 0.29); STEEL = (0.95, 0.45, 0.18)
WALLB = (0.9, 0.88, 0.83); GLASS = (0.45, 0.6, 0.75); YELLOW = (0.98, 0.75, 0.15); WATER = (0.3, 0.6, 1.0)
LEJOS = (0, 0, -300)
XI = 7.7; XO = 8.3; ZW = -14.0            # cara interior / exterior de los muros, fondo de los muros
FLOORS = [-3.3, -6.6, -9.9]               # suelo de cada planta (cara superior)
ZDIG = 10.4                               # profundidad de la excavación
ZWT = -4.0                                # nivel freático
YC = 13.0                                 # carril de la rampa
YP = -0.35                                # plano de tuberías y flechas
random.seed(5)

def prism(pts_xz, y0, y1, color, unique=False):
    """prisma a partir de un polígono en el plano xz (origen en su centro)"""
    cx = sum(p[0] for p in pts_xz) / len(pts_xz); cz = sum(p[1] for p in pts_xz) / len(pts_xz); cy = (y0 + y1) / 2
    pts_xz = [(x - cx, z - cz) for x, z in pts_xz]; y0 -= cy; y1 -= cy
    me = bpy.data.meshes.new("pr"); bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts_xz]; b = [bm.verts.new((x, y1, z)) for x, z in pts_xz]
    bm.faces.new(a); bm.faces.new(list(reversed(b))); n = len(a)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((a[j], a[i], b[i], b[j]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("pr", me); bpy.context.collection.objects.link(o); o.location = (cx, cy, cz)
    return setup(o, color, unique=unique)

def arrow(color, L=1.0, r=0.12):
    e = empty(LEJOS)
    cyl(r, L, (0, 0, L / 2), color, parent=e, v=16)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.6, radius2=0, depth=r * 5, location=(0, 0, L + r * 2.5), vertices=16)
    setup(bpy.context.object, color, e); return e

def car(color):
    e = empty(LEJOS)
    box((4.2, 1.8, 0.65), (0, 0, 0.62), color, parent=e)
    box((2.2, 1.62, 0.55), (-0.25, 0, 1.2), (0.18, 0.24, 0.32), parent=e)
    box((2.0, 1.66, 0.08), (-0.25, 0, 1.5), color, parent=e)
    for sx in (1.35, -1.35):
        for sy in (0.82, -0.82):
            cyl(0.34, 0.24, (sx, sy, 0.34), (0.1, 0.1, 0.12), parent=e, rot=(math.pi / 2, 0, 0))
            cyl(0.17, 0.26, (sx, sy, 0.34), (0.7, 0.72, 0.75), parent=e, rot=(math.pi / 2, 0, 0))
    for sy in (0.6, -0.6):
        box((0.06, 0.38, 0.16), (2.11, sy, 0.72), (1.0, 0.95, 0.7), parent=e)
        box((0.06, 0.36, 0.14), (-2.11, sy, 0.75), (0.9, 0.15, 0.15), parent=e)
    cyl(0.06, 0.25, (-2.18, -0.55, 0.3), (0.4, 0.4, 0.42), parent=e, rot=(0, math.pi / 2, 0))
    return e

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam, "sc": sc}
    cam.data.clip_start = 0.05
    D = 40.0
    # --- terreno estático (deja huecos para el núcleo, las zanjas y los bordes que se derrumban)
    for sx in (-1, 1):
        cx = sx * (11 + 40) / 2
        box((40 - 11, D, 40), (cx, D / 2, -20), SOIL); box((40 - 11, D, 0.3), (cx, D / 2, 0.15), GRASS)
        box((11 - XO, D, 37), (sx * (XO + 11) / 2, D / 2, -21.5), SOIL)
        box((2 * XO, D, 26), (0, D / 2, -27), CLAY)
        box((2 * XI, D, 14 - ZDIG), (0, D / 2, (ZW - ZDIG) / 2), CLAY)
        box((XO - XI, D - 16, 14), (sx * (XI + XO) / 2, 16 + (D - 16) / 2, -7), SOIL)   # detrás de los muros
    box((2 * XI, D - 16, 10.4), (0, 16 + (D - 16) / 2, -5.2), SOIL)
    for sx in (-1, 1):
        box((11 - XO, D - 16, 3), (sx * (XO + 11) / 2, 16 + (D - 16) / 2, -1.5), SOIL); box((11 - XO, D - 16, 0.3), (sx * (XO + 11) / 2, 16 + (D - 16) / 2, 0.15), GRASS)
        box((11 - XO, 0.1, 3), (sx * (XO + 11) / 2, 16.0, -1.5), VOID)                   # detrás del hueco
    box((2 * XI, 0.1, ZDIG), (0, 16.0, -ZDIG / 2), VOID)                               # pared del fondo del hueco
    for sx in (-1, 1): box((XO - XI, 0.1, 14), (sx * (XI + XO) / 2, 16.0, -7), VOID)
    rng = random.Random(4)
    for k in range(150):
        x, z = rng.uniform(-30, 30), rng.uniform(-19.5, -0.6)
        if abs(x) < 11.4 and z > -14.5: continue
        sph(rng.uniform(0.12, 0.3), (x, 0.0, z), tuple(v * rng.uniform(0.78, 0.9) for v in SOIL), scale=(1.3, 0.25, 1), seg=8)
    box((19, 6, 0.08), (11 + 9.5, 3, 0.33), ROAD)
    for k in range(5): box((1.2, 0.2, 0.02), (12.5 + 3.5 * k, 1.0, 0.38), (0.95, 0.95, 0.9))
    # --- piezas dinámicas de terreno
    S["core"] = box((2 * XI, 16, 1), LEJOS, SOIL)
    S["core_g"] = box((2 * XI, 16, 0.3), (0, 8, 0.15), GRASS)
    S["lips"] = [box((11 - XO, 16, 3), (sx * (XO + 11) / 2, 8, -1.5), SOIL) for sx in (-1, 1)]
    S["lips_g"] = [box((11 - XO, 16, 0.3), (sx * (XO + 11) / 2, 8, 0.15), GRASS) for sx in (-1, 1)]
    S["slot"] = [box((XO - XI, 16, 1), LEJOS, SOIL) for _ in (-1, 1)]
    S["trench"] = [box((XO - XI - 0.04, 15.9, 1), LEJOS, VOID) for _ in (-1, 1)]
    S["wedge"] = []
    for sx in (-1, 1):
        o = prism([(sx * XI, 0.3), (sx * 11.0, 0.3), (sx * XI, -3.0)], 0.0, 16.0, SOIL)
        S["wedge"].append(o)
    S["wedge_home"] = [o.location.copy() for o in S["wedge"]]
    S["crumbs"] = [sph(0.18, LEJOS, SOIL, seg=8) for _ in range(16)]
    # --- muros pantalla: crecen desde el fondo y pueden inclinarse (pivote abajo)
    S["wall"] = []
    for sx in (-1, 1):
        e = empty(LEJOS); box((XO - XI, 16.04, 14), (0, 0, 7), CON, parent=e)
        box((XO - XI + 0.02, 0.04, 14), (0, -8.03, 7), CON2, parent=e)
        S["wall"].append(e)
    S["cage"] = []
    for sx in (-1, 1):
        e = empty(LEJOS)
        for dx in (-0.18, 0.18): box((0.05, 0.05, 13.6), (dx, 0, 6.8), STEEL, parent=e)
        for k in range(28): box((0.4, 0.04, 0.04), (0, 0, 0.25 + 0.48 * k), STEEL, parent=e)
        S["cage"].append(e)
    S["grab"] = empty(LEJOS)
    box((0.5, 2.0, 1.2), (0, 0, 0), YELLOW, parent=S["grab"])
    for sx in (-1, 1): box((0.1, 2.0, 0.6), (sx * 0.2, 0, -0.85), (0.3, 0.3, 0.32), parent=S["grab"], rot=(0, sx * 0.25, 0))
    S["cable"] = bar_obj((0.15, 0.15, 0.15), 0.03)
    S["crane"] = empty(LEJOS)
    box((0.6, 0.6, 12), (0, 0, 6), YELLOW, parent=S["crane"]); box((6, 0.5, 0.5), (-2.4, 0, 12), YELLOW, parent=S["crane"])
    box((3, 2.6, 1.2), (0, 0, 0.6), (0.25, 0.25, 0.28), parent=S["crane"])
    # --- excavadora
    S["exc"] = ex = empty(LEJOS)
    box((3.4, 2.4, 0.7), (0, 0, 0.35), (0.15, 0.15, 0.17), parent=ex)
    box((2.6, 2.1, 1.0), (-0.2, 0, 1.2), YELLOW, parent=ex); box((1.1, 1.1, 1.1), (-0.6, 0.4, 2.25), (0.35, 0.45, 0.55), parent=ex)
    S["boom"] = empty((0.9, -0.3, 1.6), parent=ex); box((3.0, 0.35, 0.35), (1.5, 0, 0), YELLOW, parent=S["boom"])
    S["stick"] = empty((3.0, 0, 0), parent=S["boom"]); box((0.3, 0.3, 2.2), (0, 0, -1.1), YELLOW, parent=S["stick"])
    S["bucket"] = empty((0, 0, -2.2), parent=S["stick"]); box((0.7, 0.9, 0.6), (0.2, 0, -0.2), (0.3, 0.3, 0.32), parent=S["bucket"])
    # --- forjados, columnas, rampa, pozo
    S["slabs"] = []
    o = empty(LEJOS); box((2 * XI, 10, 0.3), (0, 5, -0.15), CON2, parent=o); box((XI - 1.0, 6, 0.3), (-(XI + 1.0) / 2, 13, -0.15), CON2, parent=o)
    S["slabs"].append(o)
    for z in FLOORS[:2]:
        o = empty(LEJOS); box((2 * XI, 16, 0.3), (0, 8, -0.15), CON2, parent=o); S["slabs"].append(o)
    o = empty(LEJOS)
    box((XI - 6.2, 16, 0.5), (-(XI + 6.2) / 2, 8, -0.25), CON2, parent=o); box((XI + 4.6, 16, 0.5), ((XI - 4.6) / 2, 8, -0.25), CON2, parent=o)
    box((0.2, 3, 1.0), (-6.3, 1.5, -1.0), CON, parent=o); box((0.2, 3, 1.0), (-4.5, 1.5, -1.0), CON, parent=o); box((1.8, 3, 0.2), (-5.4, 1.5, -1.6), CON, parent=o)
    S["slabs"].append(o)
    S["slab_z"] = [0.0] + FLOORS
    S["back"] = empty(LEJOS)
    box((2 * XI, 0.1, ZDIG), (0, 15.9, -ZDIG / 2), (0.62, 0.63, 0.65), parent=S["back"])
    for z in FLOORS: box((2 * XI, 0.12, 0.5), (0, 15.85, z + 0.9), (0.95, 0.75, 0.15), parent=S["back"])
    for z in FLOORS[:2] + [0.0]:
        for x in (-5, 0, 5): box((0.6, 0.6, 0.12), (x, 8, z - 0.36), (1.0, 0.97, 0.85), parent=S["back"])
    S["lines"] = []
    for z in FLOORS:
        for k in range(5): S["lines"].append((box((0.12, 4.0, 0.02), (-6 + 3.0 * k, 3.5, z + 0.01), (0.95, 0.95, 0.9)), z))
    S["cols"] = []
    for zt, zb in ((0.0, FLOORS[0]), (FLOORS[0], FLOORS[1]), (FLOORS[1], FLOORS[2])):
        for x in (-3.0, 3.0): S["cols"].append(box((0.45, 0.45, zt - zb - 0.3), (x, 1.0, (zt - 0.3 + zb) / 2), CON))
    S["cols_home"] = [o.location.copy() for o in S["cols"]]; S["lines_home"] = [o.location.copy() for o, _ in S["lines"]]
    L = math.hypot(XI + 1.0, 3.3); ang = math.atan2(3.3, XI + 1.0)
    S["ramp"] = box((L, 5, 0.25), ((XI - 1.0) / 2, YC, -1.65 - 0.12), CON2, rot=(0, -ang, 0))
    # --- edificio (planta baja diáfana)
    S["bld"] = b = empty(LEJOS)
    for x in (-XO + 0.3, -2.5, 2.5): box((0.5, 0.5, 3), (x, 1.0, 1.5), CON, parent=b)
    box((2 * XO, 16, 15), (0, 8, 3 + 7.5), WALLB, parent=b); box((2 * XO + 0.4, 16.4, 0.4), (0, 8, 18.2), (0.6, 0.6, 0.62), parent=b)
    for f in range(5):
        for x in (-5.5, -2, 2, 5.5): box((2.2, 0.1, 1.5), (x, -0.03, 4.8 + 3 * f), GLASS, parent=b)
    # --- coches
    S["car"] = car((0.85, 0.15, 0.15))
    cols_ = [(0.2, 0.45, 0.85), (0.95, 0.95, 0.95), (0.2, 0.2, 0.22), (0.95, 0.75, 0.2), (0.3, 0.65, 0.4), (0.6, 0.6, 0.65)]
    S["parked"] = [(car(c), pos) for c, pos in zip(cols_, [(-5.2, FLOORS[1]), (1.0, FLOORS[1]), (-1.5, FLOORS[2]), (4.5, FLOORS[2]), (-5.2, FLOORS[2]), (5.2, FLOORS[0])])]
    # --- flechas: empuje de tierra, forjados, agua
    S["push"] = []
    for sx in (-1, 1):
        for k, z in enumerate((-1.0, -2.3, -3.6)):
            S["push"].append((arrow((0.93, 0.25, 0.22), 0.25 + 0.25 * k, 0.12), sx, z, k))
    S["strut"] = [(arrow((0.3, 0.85, 0.45), 0.7, 0.1), sx, z) for sx in (-1, 1) for z in (-0.15, FLOORS[0] - 0.15, FLOORS[1] - 0.15)]
    S["up"] = [arrow((0.35, 0.65, 1.0), 1.0, 0.11) for _ in range(5)]
    S["wet"] = [box((1, 0.03, 1), LEJOS, WET) for _ in range(3)]
    S["wline"] = box((1, 0.05, 0.08), LEJOS, (0.45, 0.75, 1.0))
    S["wdots"] = [sph(0.09, LEJOS, (0.55, 0.8, 1.0), seg=8) for _ in range(36)]
    S["drops"] = [sph(0.08, LEJOS, WATER, seg=8) for _ in range(20)]
    S["puddle"] = box((1, 1, 1), LEJOS, WATER)
    S["pump"] = empty(LEJOS)
    box((0.9, 0.9, 0.8), (0, 0, 0), (0.25, 0.42, 0.75), parent=S["pump"])
    S["imp"] = empty((0, -0.47, 0), parent=S["pump"])
    for k in range(3): box((0.07, 0.03, 0.6), (0, 0, 0), (0.92, 0.92, 0.95), parent=S["imp"], rot=(0, k * math.pi / 3, 0))
    S["pipe"] = []
    PP = [(-5.4, YP, -10.6), (-5.4, YP, -9.4), (-7.25, YP, -9.4), (-7.25, YP, 0.6), (-10.5, YP, 0.6), (-10.5, YP, 0.3)]
    for a, b2 in zip(PP, PP[1:]):
        o = bar_obj((0.85, 0.87, 0.9), 0.12); S["pipe"].append((o, a, b2))
    S["pp"] = PP
    S["pdots"] = [sph(0.09, LEJOS, WATER, seg=8) for _ in range(30)]
    # --- aire: moléculas de CO, detectores, ventiladores, chimenea, aire limpio
    S["co"] = []
    for k in range(70):
        e = empty(LEJOS); sph(0.13, (-0.11, 0, 0), (0.12, 0.12, 0.14), parent=e, seg=10); sph(0.12, (0.11, 0, 0), (0.92, 0.22, 0.22), parent=e, seg=10)
        S["co"].append(e)
    S["duct"] = empty(LEJOS)
    box((0.8, 1.0, 10.0), (0, 0.5, -5.0), (0.55, 0.58, 0.62), parent=S["duct"])
    box((2.4, 1.0, 0.8), (-0.8, 0.5, 0.4), (0.55, 0.58, 0.62), parent=S["duct"])
    box((0.8, 1.0, 21.0), (-1.6, 0.5, 10.8), (0.55, 0.58, 0.62), parent=S["duct"])
    box((1.4, 1.4, 0.3), (-1.6, 0.5, 21.6), (0.4, 0.42, 0.46), parent=S["duct"])
    S["fans"] = []
    for z in (0.0, FLOORS[0], FLOORS[1]):
        e = empty(LEJOS); S["fans"].append(e)
        torus(0.85, 0.1, (0, 0, 0), (0.3, 0.32, 0.36), parent=e, rot=(math.pi / 2, 0, 0))
        hub = empty((0, 0, 0), parent=e); e["hub"] = hub.name
        for k in range(4): box((1.5, 0.04, 0.3), (0, 0, 0), (0.9, 0.9, 0.92), parent=hub, rot=(0, k * math.pi / 4, 0))
        cyl(0.12, 0.1, (0, -0.05, 0), (0.2, 0.2, 0.22), parent=hub, rot=(math.pi / 2, 0, 0))
    S["hubs"] = [bpy.data.objects[e["hub"]] for e in S["fans"]]
    S["dets"] = []
    for z in (0.0, FLOORS[0], FLOORS[1]):
        e = empty(LEJOS); box((0.5, 0.15, 0.32), (0, 0, 0), (0.95, 0.95, 0.96), parent=e)
        led = sph(0.08, (0.12, -0.09, -0.02), (0.3, 0.9, 0.4), parent=e, seg=10, unique=True)
        S["dets"].append((e, led, z))
    S["fresh"] = [sph(0.1, LEJOS, (0.6, 0.85, 1.0), seg=8) for _ in range(30)]
    S["ruler"] = empty(LEJOS)
    box((0.12, 0.12, 10.0), (0, 0, -5), (0.95, 0.95, 0.95), parent=S["ruler"])
    for z in (0, -3.3, -6.6, -10.0): box((0.8, 0.12, 0.1), (0, 0, z), (0.95, 0.95, 0.95), parent=S["ruler"])
    S["rfill"] = box((0.22, 0.14, 1), LEJOS, YELLOW)
    S["ghost"] = [box((2 * XI, 0.04, 0.08), LEJOS, (0.95, 0.95, 0.95)) for _ in range(3)]
    dyn = [cam, S["back"], S["core"], S["core_g"], S["lips"], S["lips_g"], S["slot"], S["trench"], S["wedge"], S["crumbs"], S["wall"], S["cage"],
           S["grab"], S["cable"], S["crane"], S["exc"], S["slabs"], [o for o, _ in S["lines"]], S["cols"], S["ramp"], S["bld"], S["car"],
           [c for c, _ in S["parked"]], [a for a, *_ in S["push"]], [a for a, *_ in S["strut"]], S["up"], S["wet"], S["wline"], S["wdots"],
           S["drops"], S["puddle"], S["pump"], [o for o, *_ in S["pipe"]], S["pdots"], S["co"], S["duct"], S["fans"], [e for e, *_ in S["dets"]],
           S["fresh"], S["ruler"], S["rfill"], S["ghost"]]
    join_static(dyn)
    return sc, S

# ---------- estados ----------
def done(t):
    """1 = parking terminado (al principio y desde «y aquí viene»)"""
    return max(1 - seg(t, T("y si tuvieras") - 0.1, T("y si tuvieras") + 0.5), seg(t, T("y aquí viene"), T("y aquí viene") + 1.0))

def dig(t):
    demo = keyed(t, [(T("pero si cavas") - 0.1, 0.0), (T("un agujero", fin=True), 3.0)]) if T("pero si cavas") - 0.1 < t < T("así que antes") + 0.2 else 0.0
    main = keyed(t, [(T("vacías la"), 0.0), (T("de dentro", fin=True), 3.6), (T("así que haces el suelo"), 3.6), (T("de cada planta", fin=True), 7.0),
                     (T("como un puntal", fin=True), ZDIG)])
    if done(t) > 0.99 or t < T("y si tuvieras"): return ZDIG
    return max(demo, main)

def trench(t):
    return 14.0 * seg(t, T("haces zanjas") - 0.2, T("y profundas", fin=True)) if t < T("y aquí viene") else 14.0
def concrete(t):
    if done(t) > 0.99 or t < T("y si tuvieras"): return 1.0
    return seg(t, T("y hormigón") - 0.2, T("se llaman") + 0.3)
def bend(t):
    return win01(t, T("pero la tierra de fuera") + 0.4, T("que los sujeta") + 0.6, 1.2, 0.8)
def slab_on(t, k):
    if done(t) > 0.99 or t < T("y si tuvieras"): return 1.0
    ts = [T("así que haces el suelo") + 0.3, T("de cada planta"), T("que los sujeta"), T("como un puntal") + 0.2][k]
    return seg(t, ts, ts + 0.4)
def ppm(t):
    a, b = T("los tubos de escape"), T("cuando llegan")
    v = keyed(t, [(a, 0.0), (T("no huele"), 12.0), (T("se acumula", fin=True), 34.0), (T("cuando llegan") + 0.3, 42.0), (T("por millón", fin=True), 50.0),
                  (T("se encienden") + 0.6, 52.0), (T("cuando el aire"), 18.0), (T("se vuelven"), 8.0), (T("por eso nunca"), 8.0), (DUR, 180.0)])
    return v if t > a else 0.0
def fans_on(t): return T("se encienden") < t < T("se vuelven") + 0.4

def car_path(t):
    """coche que baja la rampa al principio: posición, cabeceo"""
    pts = [(7.2, 0.0), (-1.0, -3.3), (-3.6, -3.3)]
    s = keyed(t, [(0.0, 0.25), (2.3, 1.0), (3.6, 1.55), (4.1, 1.6)])
    if s <= 1.0:
        x = mix(pts[0][0], pts[1][0], s); z = mix(pts[0][1], pts[1][1], s)
        pitch = math.atan2(3.3, 8.2) * min(1, s / 0.08) * min(1, (1 - s) / 0.08)
    else:
        u = min(1, (s - 1) / 0.6); x = mix(pts[1][0], pts[2][0], u); z = -3.3; pitch = 0.0
    return Vector((x, YC, z)), pitch

def put(o, on, loc, scale=None):
    if on: o.location = loc
    else: o.location = LEJOS
    if scale is not None and on: o.scale = scale

def pose(t, S):
    dn = done(t); building = dn > 0.01
    # terreno
    d = dig(t)
    put(S["core"], d < ZDIG - 0.01, (0, 8, (-ZDIG - d) / 2), (2 * XI, 16, max(ZDIG - d, 0.01)))
    put(S["core_g"], d < 0.05, (0, 8, 0.15))
    a_der, a_asi = T("la tierra de los lados"), T("así que antes")
    col = win01(t, a_der - 0.1, a_asi + 0.1, 0.05, 0.05)
    for k, sx in enumerate((-1, 1)):
        put(S["lips"][k], col < 0.01, (sx * (XO + 11) / 2, 8, -1.5)); put(S["lips_g"][k], col < 0.01, (sx * (XO + 11) / 2, 8, 0.15))
        w = S["wedge"][k]
        if col > 0.01:
            u = seg(t, a_der, T("se derrumba", fin=True))
            w.location = S["wedge_home"][k] + Vector((-sx * 2.6 * u, 0, -2.4 * u)); w.rotation_euler = (0, sx * 0.5 * u, 0)
        else: w.location = LEJOS
        tr = trench(t); cc = concrete(t)
        hs = 14 - tr
        put(S["slot"][k], hs > 0.01 and col < 0.01 and cc < 0.001, (sx * (XI + XO) / 2, 8, ZW + hs / 2), (XO - XI, 16, max(hs, 0.01)))
        trv = tr > 0.05 and cc < 0.999 and t > T("y si tuvieras")
        put(S["trench"][k], trv, (sx * (XI + XO) / 2, 8.05, -tr / 2), (XO - XI - 0.04, 15.9, max(tr, 0.01)))
        wl = S["wall"][k]
        if cc > 0.001:
            wl.location = (sx * (XI + XO) / 2, 8, ZW); wl.scale = (1, 1, cc); wl.rotation_euler = (0, -sx * 0.07 * bend(t), 0)
        else: wl.location = LEJOS
        cg = S["cage"][k]
        a_ac = T("acero")
        if a_ac - 1.0 < t < T("se llaman") + 0.5:
            zc = keyed(t, [(a_ac - 1.0, 16.0), (T("y hormigón"), ZW + 0.2)])
            cg.location = (sx * (XI + XO) / 2, -0.06, zc)
        else: cg.location = LEJOS
    for k, c in enumerate(S["crumbs"]):
        if col > 0.01:
            u = seg(t, a_der + 0.05 * (k % 5), T("se derrumba", fin=True) + 0.3)
            sx = -1 if k % 2 else 1
            c.location = (sx * (XI + 0.5 - 2.5 * u + 0.4 * math.sin(k)), -0.15, 0.3 - 3.2 * u * u - 0.2 * (k % 3))
        else: c.location = LEJOS
    # grúa con cuchara en la zanja derecha
    a_z0, a_z1 = T("haces zanjas") - 0.8, T("y las rellenas") + 0.2
    if a_z0 < t < a_z1:
        tr = trench(t); zg = -tr + 0.9 + 0.5 * abs(math.sin(t * 4))
        S["grab"].location = ((XI + XO) / 2, 4.0, min(zg, 2.0)); S["crane"].location = (12.5, 4.0, 0.3)
        bar_set(S["cable"], ((XI + XO) / 2, 4.0, 12.3), ((XI + XO) / 2, 4.0, min(zg, 2.0) + 0.6))
    else: S["grab"].location = LEJOS; S["crane"].location = LEJOS; S["cable"].location = LEJOS
    # excavadora
    a_ex = T("vamos a excavar")
    exc_on = (a_ex - 0.3 < t < T("así que antes") + 0.3) or (T("ahora sí") - 0.3 < t < T("pero al bajar") + 0.6)
    if exc_on:
        S["exc"].location = (-3.2, 7.5, -d + 0.02)
        ph = t * 3.2
        S["boom"].rotation_euler = (0, -0.35 + 0.35 * math.sin(ph), 0)
        S["stick"].rotation_euler = (0, 0.6 + 0.5 * math.sin(ph + 1.2), 0)
        S["bucket"].rotation_euler = (0, 0.5 * math.sin(ph + 2.0), 0)
    else: S["exc"].location = LEJOS
    # regla de 10 m y plantas fantasma
    a_tr = T("quieres tres")
    if a_tr - 0.2 < t < T("pero si cavas"):
        S["ruler"].location = (-6.0, YP - 0.3, 0)
        h = 10.0 * seg(t, T("unos diez"), T("de hondo", fin=True))
        put(S["rfill"], h > 0.02, (-6.0, YP - 0.38, -h / 2), (0.22, 0.14, max(h, 0.01)))
        for k, g in enumerate(S["ghost"]):
            p = seg(t, a_tr + 0.4 + 0.35 * k, a_tr + 0.7 + 0.35 * k)
            put(g, p > 0.01, (0, YP + 0.1, FLOORS[k]), (2 * XI * p, 0.04, 0.08))
    else:
        S["ruler"].location = LEJOS; S["rfill"].location = LEJOS
        for g in S["ghost"]: g.location = LEJOS
    # forjados, columnas, rampa, líneas
    for k, o in enumerate(S["slabs"]):
        p = slab_on(t, k)
        put(o, p > 0.01, (0, 0, S["slab_z"][k]), (p, 1, 1))
    for k, c in enumerate(S["cols"]):
        put(c, slab_on(t, k // 2 + 1) > 0.99, S["cols_home"][k])
    for (o, z), h in zip(S["lines"], S["lines_home"]): put(o, dn > 0.5, h)
    put(S["back"], dn > 0.5, (0, 0, 0))
    put(S["ramp"], dn > 0.5, ((XI - 1.0) / 2, YC, -1.65 - 0.12))
    put(S["bld"], building, (0, 0, 0), (1, 1, max(dn, 0.01)))
    # coches
    if t < T("y si tuvieras") + 0.3:
        p, pitch = car_path(t); S["car"].location = p; S["car"].rotation_euler = (0, pitch, math.pi)
    elif T("el mayor peligro") - 0.5 < t < T("por eso nunca") + 0.2:
        x = keyed(t, [(T("el mayor peligro") - 0.5, 6.5), (T("y en un sitio"), -1.5), (T("así que en cada planta"), -1.5), (T("por eso nunca"), -1.5)])
        S["car"].location = (x, 5.0, FLOORS[1]); S["car"].rotation_euler = (0, 0, math.pi)
    elif t >= T("por eso nunca") + 0.2:
        S["car"].location = (-1.5, 5.0, FLOORS[1]); S["car"].rotation_euler = (0, 0, math.pi)
    else: S["car"].location = LEJOS
    for c, (x, z) in S["parked"]:
        put(c, dn > 0.5, (x, 5.0 + (0.3 if x > 0 else -0.2), z)); c.rotation_euler = (0, 0, 0 if x > 0 else math.pi)
    # flechas de empuje y de los forjados
    pb = bend(t) * (1 - seg(t, T("que los sujeta"), T("como un puntal", fin=True)))
    for a, sx, z, k in S["push"]:
        if pb > 0.02:
            L = 0.25 + 0.25 * k
            a.location = (sx * (XO + 0.1 + L + 0.6 + 0.1 * math.sin(t * 6 + k)), YP - 0.3, z); a.rotation_euler = (0, -sx * math.pi / 2, 0); a.scale = (pb,) * 3
        else: a.location = LEJOS
    ps = win01(t, T("que los sujeta") - 0.2, T("pero al bajar"), 0.3, 0.3)
    for k, (a, sx, z) in enumerate(S["strut"]):
        if ps > 0.02 and slab_on(t, k % 3) > 0.9:
            a.location = (sx * (XI - 1.3), YP, z); a.rotation_euler = (0, sx * math.pi / 2, 0); a.scale = (ps,) * 3
        else: a.location = LEJOS
    # agua
    a_ag = T("aparece el agua")
    wet = seg(t, T("pero al bajar"), T("en muchas")) if t < T("y aquí viene") else 1.0
    if t < T("y si tuvieras"): wet = 0
    for k, w in enumerate(S["wet"]):
        if wet > 0.01:
            hgt = (40 + ZWT) * wet
            if k < 2:
                sx = (-1, 1)[k]; w.location = (sx * (XO + 16), -0.02, ZWT - hgt / 2); w.scale = (32, 0.03, hgt)
            else: w.location = (0, -0.02, -ZDIG - (40 - ZDIG) * wet / 2); w.scale = (2 * XO, 0.03, (40 - ZDIG) * wet)
        else: w.location = LEJOS
    put(S["wline"], wet > 0.5 and t < T("y aquí viene"), (0, -0.06, ZWT), (64, 0.05, 0.08))
    for k, dd in enumerate(S["wdots"]):
        if wet > 0.3 and t < T("y aquí viene"):
            sx = -1 if k % 2 else 1
            x = sx * (XO + 1.0 + (k * 1.7) % 12); z = ZWT - 0.6 - ((k * 2.3) % 9) + 0.25 * math.sin(t * 2 + k)
            dd.location = (x, -0.12, z)
        else: dd.location = LEJOS
    a_em, a_pz, a_cur = T("esa agua empuja"), T("así que en el fondo"), T("y aquí viene")
    up = win01(t, a_em, a_pz + 0.5, 0.3, 0.3)
    for k, a in enumerate(S["up"]):
        if up > 0.02:
            a.location = (-6 + 3 * k, YP, -13.2 + 0.25 * ((t * 2 + k * 0.3) % 1.0)); a.rotation_euler = (0, 0, 0); a.scale = (up,) * 3
        else: a.location = LEJOS
    leak = a_ag < t < a_cur
    for k, dd in enumerate(S["drops"]):
        if leak and t > T("y se cuela") - 1.5 or (leak and k < 6):
            sx = -1 if k % 2 else 1
            u = ((t - a_ag) * 0.8 + k / 20) % 1.0
            dd.location = (sx * (XI - 0.05 - 1.6 * u), -0.1, FLOORS[2] + 0.1 + 0.25 * math.sin(math.pi * u))
        else: dd.location = LEJOS
    pud = keyed(t, [(a_ag, 0.0), (a_pz + 0.5, 0.35), (T("sin parar", fin=True), 0.03)]) if a_ag < t < a_cur else 0.0
    put(S["puddle"], pud > 0.02, (0.6, 8, FLOORS[2] + pud / 2), (2 * XI - 1.2, 16, max(pud, 0.01)))
    pump_on = t > a_pz
    put(S["pump"], pump_on, (-5.4, 0.2, FLOORS[2] - 0.95), (seg(t, a_pz, a_pz + 0.4) + 0.001,) * 3)
    S["imp"].rotation_euler = (0, t * 12, 0)
    for o, a, b2 in S["pipe"]:
        if pump_on: bar_set(o, a, b2)
        else: o.location = LEJOS
    PPth = [Vector(p) for p in S["pp"]]; Ls = [0.0]
    for a, b2 in zip(PPth, PPth[1:]): Ls.append(Ls[-1] + (b2 - a).length)
    for k, dd in enumerate(S["pdots"]):
        if pump_on and T("con bombas") < t < a_cur + 1.0:
            s_ = (Ls[-1] * k / 30 + t * 4.0) % Ls[-1]
            for i in range(len(PPth) - 1):
                if Ls[i] <= s_ <= Ls[i + 1]:
                    dd.location = PPth[i].lerp(PPth[i + 1], (s_ - Ls[i]) / max(Ls[i + 1] - Ls[i], 1e-6)) + Vector((0, -0.18, 0)); break
        else: dd.location = LEJOS
    # aire
    vent = dn > 0.5 and t > T("y aquí viene")
    put(S["duct"], vent, (-7.25, 0.0, 0.0))
    for k, (e, led, z) in enumerate(S["dets"]):
        on = t > T("así que en cada planta") + 0.25 * k
        put(e, on, (2.0, -0.08, z - 0.55), (seg(t, T("así que en cada planta") + 0.25 * k, T("así que en cada planta") + 0.25 * k + 0.4) + 0.001,) * 3)
        alarm = ppm(t) >= 49.5
        set_color(led, (0.95, 0.2, 0.2) if alarm and int(t * 5) % 2 == 0 else ((0.95, 0.2, 0.2) if alarm else (0.3, 0.9, 0.4)))
    fo = fans_on(t)
    for k, (e, hub) in enumerate(zip(S["fans"], S["hubs"])):
        z = [0.0, FLOORS[0], FLOORS[1]][k]
        put(e, vent, (-5.9, -0.12, z - 1.6))
        hub.rotation_euler = (0, (t - T("se encienden")) * 14 * seg(t, T("se encienden"), T("se encienden") + 0.6) * (1 - seg(t, T("se vuelven"), T("se vuelven") + 0.6)) if t > T("se encienden") else 0, 0)
    # CO
    p = ppm(t); NC = len(S["co"]); n = int(NC * min(1.0, p / 50.0))
    a_sa, a_pe = T("sacan el aire"), T("por eso nunca")
    exhaust = S["car"].location + Vector((2.3, 0.55, 0.3))
    rr = random.Random(9)
    for k, e in enumerate(S["co"]):
        lev = k % 3
        home = Vector((rr.uniform(-6.0, 6.5), rr.uniform(-0.35, 0.1), FLOORS[lev] + 0.6 + rr.uniform(0, 2.0)))
        if k < 30: home = Vector((rr.uniform(-5.0, 6.5), -0.3, FLOORS[1] + 0.5 + rr.uniform(0, 2.1))); lev = 1
        ph = rr.uniform(0, 6.28)
        wob = Vector((0.25 * math.sin(t * 0.8 + ph), 0, 0.2 * math.cos(t * 0.9 + ph)))
        if t >= a_pe:                                   # coche en marcha en un garaje cerrado
            tb = a_pe + 0.3 + 3.6 * k / NC
            if t < tb: e.location = LEJOS; continue
            near = Vector((rr.uniform(-1.0, 6.5), -0.3, FLOORS[1] + 0.4 + rr.uniform(0, 2.4)))
            e.location = exhaust.lerp(near, seg(t, tb, tb + 1.2)) + wob; e.rotation_euler = (0, t * 1.5 + ph, 0); continue
        if t < T("los tubos de escape") or k >= n and not (fans_on(t) and t > a_sa - 1.0): e.location = LEJOS; continue
        if not fans_on(t) and t > T("se encienden"): e.location = LEJOS; continue
        tb = T("los tubos de escape") + 0.3 + 5.0 * (k / NC)
        pos = (exhaust.lerp(home, seg(t, tb, tb + 1.6)) if t < tb + 1.6 else home) + wob
        if fans_on(t) and t > a_sa - 1.0:
            ts = a_sa - 1.0 + 1.6 * ((k * 0.37) % 1.0)
            fz = [0.0, FLOORS[0], FLOORS[1]][lev] - 1.6
            if lev == 2: fz = FLOORS[1] - 1.6
            fan = Vector((-6.3, -0.2, fz))
            u = seg(t, ts, ts + 1.4); pos = pos.lerp(fan, u)
            if t > ts + 1.4:
                zz = fz + (t - ts - 1.4) * 9.0
                if zz < 0.5: pos = Vector((-7.25, -0.2, zz))
                elif zz < 22: pos = Vector((-8.85, -0.2, zz))
                else: e.location = LEJOS; continue
        e.location = pos; e.rotation_euler = (0, t * 1.5 + ph, 0)
    for k, d2 in enumerate(S["fresh"]):
        if T("y entra aire") - 0.3 < t < T("se vuelven") + 0.3:
            u = ((t - T("y entra aire")) * 0.45 + k / 30) % 1.0
            path = [Vector((16, -0.2, 1.2)), Vector((7.6, -0.2, 0.5)), Vector((5.0, -0.2, -1.5)), Vector((5.0, -0.2, [-1.5, -4.8, -8.1][k % 3]))]
            seglen = len(path) - 1; f = u * seglen; i = min(int(f), seglen - 1)
            d2.location = path[i].lerp(path[i + 1], f - i) + Vector((0, 0, 0.3 * math.sin(k)))
            if i == seglen - 1: d2.location.x -= 9.0 * (f - i) * ((k % 5) / 5 + 0.3)
        else: d2.location = LEJOS
    apply_cam(S["cam"], *camera(t, S))

def V_(at, off, lens=35):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    add(T("y si tuvieras") + 0.15, V_((-3.0, 2.0, -1.8), (0, -3.0, 0.0), 35))
    add(T("vamos a excavar"), V_((0, 0, -2.0), (0, -27, 2.0), 35))
    add(T("quieres tres") + 0.5, V_((-1.0, 0, -5.0), (0, -27, 2.0), 35))
    add(T("pero si cavas"), V_((0, 0, -2.5), (0, -22, 2.5), 35))
    add(T("se derrumba", fin=True), V_((0, 0, -2.0), (0, -20, 3.0), 35))
    add(T("construyes las paredes"), V_((0, 0, -5.0), (0, -27, 2.0), 35))
    add(T("haces zanjas") + 0.3, V_((6.5, 0, -6.0), (0, -18, 2.0), 35))
    add(T("y hormigón", fin=True), V_((6.5, 0, -6.5), (0, -18, 2.0), 35))
    add(T("ahora sí"), V_((0, 0, -5.0), (0, -27, 2.0), 35))
    add(T("pero la tierra de fuera") + 0.4, V_((0, 0, -3.5), (0, -42, 2.0), 35))
    add(T("así que haces el suelo") + 0.3, V_((0, 0, -5.0), (0, -28, 2.0), 35))
    add(T("pero al bajar"), V_((0, 0, -6.0), (0, -30, 2.0), 35))
    add(T("en muchas") + 0.3, V_((0, 0, -7.0), (0, -33, 2.0), 35))
    add(T("esa agua empuja") + 0.3, V_((0, 0, -9.5), (0, -21, 1.6), 35))
    add(T("así que en el fondo") + 0.4, V_((-3.5, 0, -8.5), (0, -16, 1.4), 35))
    add(T("que la sacan", fin=True), V_((-4.5, 0, -6.0), (0, -24, 1.6), 35))
    add(T("y aquí viene") + 0.5, V_((0, 0, 1.0), (0, -38, 3.0), 35))
    add(T("el mayor peligro") + 0.5, V_((1.5, 0, -5.2), (0, -15, 1.2), 35))
    add(T("los tubos de escape") + 0.3, V_((0.5, 0, -5.2), (0, -11, 1.0), 35))
    add(T("y en un sitio"), V_((0, 0, -5.0), (0, -20, 1.2), 35))
    add(T("así que en cada planta") + 0.4, V_((0, 0, -4.5), (0, -24, 1.5), 35))
    add(T("se encienden"), V_((-2.0, 0, -4.5), (0, -22, 1.5), 35))
    add(T("sacan el aire") + 0.5, V_((-2.0, 0, 3.0), (0, -38, 2.0), 35))
    add(T("y entra aire") + 0.5, V_((2.0, 0, -2.5), (0, -26, 1.5), 35))
    add(T("cuando el aire"), V_((0, 0, -4.5), (0, -24, 1.5), 35))
    add(T("por eso nunca") + 0.3, V_((0.0, 5.0, -5.6), (-1.5, -9.5, 0.6), 35))
    add(T("garaje cerrado", fin=True), V_((0.0, 5.0, -5.6), (-1.5, -10.5, 0.8), 35))
    add(DUR + 2, V_((0, 0, 1.0), (0, -40, 3.0), 35))
    return k
CAMK = None
def camera(t, S):
    global CAMK
    if CAMK is None: CAMK = CAM()
    a0 = T("y si tuvieras") + 0.15
    if t < a0:
        p, _ = car_path(t)
        tgt = p + Vector((0, 0, 0.7)); pos = Vector((max(p.x - 3.6, -6.0), 6.4, -1.55))
        intro = (pos, tgt, 30.0)
        if t < T("y si tuvieras") - 0.25: return intro
        k0 = CAMK[0]; u = seg(t, T("y si tuvieras") - 0.25, a0)
        return pos.lerp(Vector(k0[1]), u), tgt.lerp(Vector(k0[2]), u), mix(30.0, k0[3], u)
    ks = CAMK
    if t >= ks[-1][0]: a = b = ks[-1]; u = 0
    else:
        for i in range(len(ks) - 1):
            if ks[i][0] <= t <= ks[i + 1][0]: break
        a, b = ks[i], ks[i + 1]; u = ss((t - a[0]) / max(b[0] - a[0], 1e-4))
    pos = Vector(a[1]).lerp(Vector(b[1]), u); tgt = Vector(a[2]).lerp(Vector(b[2]), u)
    pos += Vector((math.sin(t * 0.9), 0.7 * math.sin(t * 0.7), 0.8 * math.sin(t * 1.1))) * 0.03
    return pos, tgt, mix(a[3], b[3], u)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"car": Pj(S["car"].location + Vector((0, 0, 1.6))), "ruler": Pj((-6.0, YP, -10.0)), "pit": Pj((0, 0, -1.5)),
            "trench": Pj((XO, -0.1, -3.0)), "cage": Pj((XO, -0.1, 0.8)), "wallL": Pj((-XO, 0, -6.0)), "wallR": Pj((XO, 0, -6.0)),
            "push": Pj((XO + 2.5, YP, -2.3)), "slab": Pj((3.5, 0, FLOORS[0])), "wt": Pj((-XO - 6, 0, ZWT)), "up": Pj((0, YP, -12.5)),
            "pump": Pj((-5.4, 0, FLOORS[2] - 0.4)), "exhaust": Pj(S["car"].location + Vector((2.4, -0.5, 0.4))), "det": Pj((2.0, 0, FLOORS[0] - 0.55)),
            "fan": Pj((-6.3, 0, FLOORS[0] - 1.6)), "chim": Pj((-8.85, 0, 19.0)), "fresh": Pj((10.0, 0, 1.5)), "exc": Pj((-1.0, 7.5, -dig(t) + 3.0))}

if __name__ == "__main__":
    run("parking", build, pose, anchors)
