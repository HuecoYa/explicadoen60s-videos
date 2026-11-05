# «¿Y si construyes un pozo?»: corte del terreno bajo una casa; la broca gira y baja hasta la arena empapada (contador de metros);
# las paredes se desmoronan; tubo de 15 cm; rejilla con ranuras (pasa el agua, no la arena); grava; tapón de cemento;
# bomba arriba aspirando: el agua solo sube 10 m (el aire empuja); bomba sumergida que empuja hasta arriba;
# el nivel del agua forma un embudo que crece y deja seco el pozo del vecino; caudalímetro para controlarlo.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("pozo")
BG = (0.15, 0.17, 0.22)
GRASS = (0.38, 0.62, 0.32); SOIL = (0.42, 0.31, 0.22); CLAY = (0.6, 0.4, 0.27); SAND = (0.84, 0.72, 0.5); SAND2 = (0.66, 0.56, 0.4)
ROCK = (0.45, 0.45, 0.48); WET = (0.3, 0.52, 0.82); WATER = (0.35, 0.65, 1.0); VOID = (0.1, 0.09, 0.09)
PVC = (0.88, 0.9, 0.94); PVC_IN = (0.5, 0.53, 0.58); STEEL = (0.62, 0.64, 0.68); YEL = (1.0, 0.78, 0.15); BLUE = (0.2, 0.42, 0.85)
GRAV = (0.62, 0.62, 0.64); CEM = (0.78, 0.78, 0.76); MUD = (0.45, 0.33, 0.2); RED = (0.9, 0.3, 0.25)
LEJOS = (0, 0, -200)
Z_AQ = -18.0          # nivel del agua subterránea (techo de la arena empapada)
Z_FONDO = -23.0       # fondo del pozo
Z_REJ = -17.5         # inicio de la rejilla
RB, RT = 0.8, 0.42    # radio del agujero y del tubo (estilizados)
XV = 8.0              # pozo del vecino
ZV = -19.2            # fondo del pozo del vecino
NS = 96               # franjas de agua en la arena

def hide(o): o.location = LEJOS

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam}
    # terreno en corte (y>=0); la cámara mira desde y<0
    box((50, 12, 0.25), (0, 6, 0.125), GRASS); cam.data.clip_start = 0.5
    for z0, z1, c in ((-2, 0, SOIL), (-9, -2, CLAY), (-18, -9, SAND), (-26, -18, SAND2), (-42, -26, ROCK)):
        box((50, 12, z1 - z0), (0, 6, (z0 + z1) / 2), c)
    rng = random.Random(4)
    for k in range(380):   # granos y piedras en la cara del corte
        x, z = rng.uniform(-24.5, 24.5), rng.uniform(-30.5, -0.3)
        if abs(x) < RB + 0.3 or abs(x - XV) < 0.7 or -26.5 < z < -17.5: continue
        c = SOIL if z > -2 else CLAY if z > -9 else SAND if z > -18 else SAND2 if z > -26 else ROCK
        c = tuple(v * rng.uniform(0.75, 0.9) for v in c)
        sph(rng.uniform(0.06, 0.22), (x, 0.0, z), c, scale=(1.3, 0.25, 1), seg=8)
    # casa y casa del vecino
    for hx, wc in ((-4.8, (0.95, 0.93, 0.88)), (XV + 1.6, (0.92, 0.85, 0.7))):
        box((3.2, 3.0, 2.4), (hx, 3.0, 1.45), wc)
        for s_ in (-1, 1):
            box((1.9, 3.2, 0.18), (hx + s_ * 0.8, 3.0, 3.25), (0.8, 0.3, 0.25), rot=(0, s_ * math.radians(-35), 0))
        box((0.7, 0.05, 1.3), (hx + 0.6, 1.48, 0.9), (0.45, 0.3, 0.2))
        box((0.7, 0.05, 0.6), (hx - 0.8, 1.48, 1.6), (0.6, 0.8, 0.95))
    # agua en la arena: franjas cuyo techo baja con el embudo
    S["agua"] = [box((48 / NS + 0.02, 0.02, 1), LEJOS, WET) for _ in range(NS)]
    S["chispas"] = [sph(0.07, LEJOS, (0.7, 0.88, 1.0), seg=8) for _ in range(28)]
    # perforadora
    S["rig"] = empty((0, 0, 0))
    box((3.0, 2.0, 1.2), (2.6, 1.6, 0.9), YEL, parent=S["rig"]); box((1.2, 1.8, 1.0), (4.4, 1.6, 1.0), (0.3, 0.32, 0.36), parent=S["rig"])
    for wx in (1.6, 3.6):
        cyl(0.45, 0.3, (wx, 0.55, 0.45), (0.15, 0.15, 0.17), parent=S["rig"], rot=(math.pi / 2, 0, 0))
    box((0.35, 0.35, 7.0), (0.7, 0.6, 3.8), YEL, parent=S["rig"]); box((1.0, 1.0, 0.45), (0.25, 0.25, 7.0), (0.3, 0.32, 0.36), parent=S["rig"])
    S["varilla"] = bar_obj(STEEL, 0.09)
    S["broca"] = empty(LEJOS)
    bpy.ops.mesh.primitive_cone_add(radius1=0.62, radius2=0.05, depth=0.9, location=(0, 0, -0.35), rotation=(math.pi, 0, 0), vertices=6)
    setup(bpy.context.object, (0.55, 0.57, 0.62), parent=S["broca"])
    for k in range(10):   # espiral
        a = k * 0.9
        box((1.15, 0.12, 0.08), (0.0, 0, 0.15 + 0.17 * k), (0.75, 0.77, 0.8), parent=S["broca"], rot=(0.25, 0, a))
    S["tierra"] = [box((0.16, 0.16, 0.16), LEJOS, (SOIL, CLAY, SAND)[k % 3], unique=True) for k in range(26)]
    # agujero (hueco oscuro delante del corte)
    S["hueco"] = box((2 * RB, 0.02, 1), LEJOS, VOID)
    S["trozos"] = [sph(0.22, LEJOS, (CLAY, SAND, SOIL)[k % 3], scale=(1.2, 0.5, 0.9), seg=10) for k in range(18)]
    S["bultos"] = [box((1, 0.03, 0.9), LEJOS, (CLAY, SAND, SAND2)[k % 3]) for k in range(8)]
    # tubo (media sección: dos paredes y el fondo interior más oscuro), con la rejilla abajo
    tb = empty((0, 0, 30)); S["tubo"] = tb
    L1 = 0.4 - Z_REJ
    box((2 * RT, 0.02, L1), (0, -0.05, 0.4 - L1 / 2), PVC_IN, parent=tb)
    for s_ in (-1, 1): box((0.08, 0.08, L1), (s_ * (RT - 0.04), -0.08, 0.4 - L1 / 2), PVC, parent=tb)
    L2 = Z_REJ - (Z_FONDO - 0.2)
    S["liso"] = empty((0, 0, Z_REJ)); S["liso"].parent = tb
    box((2 * RT, 0.02, L2), (0, -0.05, -L2 / 2), PVC_IN, parent=S["liso"])
    for s_ in (-1, 1): box((0.08, 0.08, L2), (s_ * (RT - 0.04), -0.08, -L2 / 2), PVC, parent=S["liso"])
    box((2 * RT, 0.08, 0.1), (0, -0.08, Z_FONDO - 0.15), PVC, parent=tb)
    S["rej"] = []          # segmentos con ranuras (aparecen de abajo arriba)
    nr = int(L2 / 0.26)
    for k in range(nr):
        z = Z_FONDO - 0.2 + 0.26 * k + 0.09
        e = empty((0, 0, z)); e.parent = tb
        box((2 * RT, 0.02, 0.18), (0, -0.05, 0), PVC_IN, parent=e)
        for s_ in (-1, 1): box((0.08, 0.08, 0.18), (s_ * (RT - 0.04), -0.08, 0), PVC, parent=e)
        S["rej"].append(e)
    S["agua_in"] = box((2 * RT - 0.16, 0.02, 1), LEJOS, WATER)
    S["gotas"] = [sph(0.1, LEJOS, WATER, seg=10) for _ in range(14)]
    S["arena"] = [sph(0.1, LEJOS, (0.95, 0.8, 0.5), seg=10) for _ in range(10)]
    # grava, relleno y cemento alrededor del tubo
    S["grava"] = []
    rg = random.Random(9); z = Z_FONDO - 0.1
    while z < -16.3:
        for s_ in (-1, 1):
            for xx in (RT + 0.1, RT + 0.28):
                S["grava"].append((z, sph(rg.uniform(0.08, 0.11), LEJOS, tuple(v * rg.uniform(0.8, 1.05) for v in GRAV), seg=8)))
        z += 0.19
    S["relleno"] = [box((RB - RT, 0.03, 1), LEJOS, (0.5, 0.38, 0.27)) for _ in range(2)]
    S["cemento"] = [box((RB - RT, 0.04, 1), LEJOS, CEM) for _ in range(2)]
    S["losa"] = box((2.6, 1.6, 0.18), LEJOS, CEM)
    S["sucia"] = [sph(0.11, LEJOS, MUD, seg=10) for _ in range(8)]
    # bomba de superficie con tubo de aspiración
    S["bomba"] = empty(LEJOS)
    box((1.1, 0.8, 0.7), (0.35, -0.2, 0.0), BLUE, parent=S["bomba"]); cyl(0.3, 0.8, (1.0, -0.2, 0.0), (0.3, 0.32, 0.36), parent=S["bomba"], rot=(0, math.pi / 2, 0))
    S["asp"] = bar_obj(STEEL, 0.17)
    S["colw"] = bar_obj(WATER, 0.14)
    S["flechas"] = []
    for k in range(6):
        bpy.ops.mesh.primitive_cone_add(radius1=0.2 if k < 2 else 0.6, radius2=0, depth=0.5 if k < 2 else 1.3, location=LEJOS, rotation=(math.pi, 0, 0))
        f = bpy.context.object; setup(f, (0.95, 0.95, 1.0)); S["flechas"].append(f)
    # bomba sumergida, tubería de subida, grifo, cubo y caudalímetro
    S["sumer"] = empty(LEJOS)
    cyl(0.24, 0.7, (0, 0, -0.3), (0.3, 0.32, 0.36), parent=S["sumer"]); cyl(0.24, 0.5, (0, 0, 0.3), YEL, parent=S["sumer"])
    for k in range(4): box((0.5, 0.05, 0.04), (0, -0.2, 0.15 + 0.1 * k), (0.15, 0.15, 0.17), parent=S["sumer"])
    S["subida"] = bar_obj(STEEL, 0.15)
    S["colw2"] = bar_obj(WATER, 0.12)
    S["salida"] = empty(LEJOS)
    box((1.6, 0.2, 0.2), (-0.7, 0, 0), STEEL, parent=S["salida"]); box((0.2, 0.2, 0.35), (-1.5, 0, -0.1), STEEL, parent=S["salida"])
    cyl(0.3, 0.12, (-0.55, -0.12, 0.0), (0.97, 0.97, 0.97), parent=S["salida"], rot=(math.pi / 2, 0, 0))
    S["aguja"] = box((0.04, 0.03, 0.24), LEJOS, RED, unique=True)
    S["cubo"] = cyl(0.42, 0.6, LEJOS, (0.85, 0.3, 0.3))
    S["chorro"] = [sph(0.08, LEJOS, WATER, seg=8) for _ in range(10)]
    S["subeflechas"] = []
    for k in range(4):
        bpy.ops.mesh.primitive_cone_add(radius1=0.32, radius2=0, depth=0.7, location=LEJOS); f = bpy.context.object; setup(f, (0.6, 0.95, 0.6))
        S["subeflechas"].append(f)
    S["flujo"] = [sph(0.09, LEJOS, (0.6, 0.85, 1.0), seg=8) for _ in range(16)]
    # pozo del vecino (siempre en su sitio)
    box((0.7, 0.02, 0.25 - ZV), (XV, -0.04, (0.25 + ZV) / 2), VOID)
    box((0.5, 0.02, 0.6 - ZV), (XV, -0.05, (0.6 + ZV) / 2), PVC_IN)
    for s_ in (-1, 1): box((0.07, 0.07, 0.6 - ZV), (XV + s_ * 0.25, -0.08, (0.6 + ZV) / 2), PVC)
    box((0.7, 0.6, 0.15), (XV, 0.0, 0.65), (0.4, 0.42, 0.46))
    S["agua_v"] = box((0.42, 0.02, 1), LEJOS, WATER)
    dyn = [cam, S["agua"], S["chispas"], S["rig"], S["varilla"], S["broca"], S["tierra"], S["hueco"], S["trozos"], S["bultos"], S["tubo"],
           S["agua_in"], S["gotas"], S["arena"], [g for _, g in S["grava"]], S["relleno"], S["cemento"], S["losa"], S["sucia"], S["bomba"], S["asp"],
           S["colw"], S["flechas"], S["sumer"], S["subida"], S["colw2"], S["salida"], S["aguja"], S["cubo"], S["chorro"], S["subeflechas"],
           S["flujo"], S["agua_v"]]
    join_static(dyn)
    return sc, S

def tiempos():
    return dict(perf=T("perforas"), broca=T("una broca"), veinte=T("a veinte"), subt=T("el agua subterránea"), paredes=T("pero las paredes"),
                tubo=T("así que metes"), quince=T("quince"), cerr=T("pero el tubo"), fondo=T("en el fondo"), rej=T("la rejilla"),
                deja=T("deja pasar"), grava=T("rellenas con"), arriba=T("arriba"), sucia=T("para que no"), ahora=T("ahora"),
                aspire=T("podrías poner"), aspir=T("aspirando"), aire=T("en realidad"), bajas=T("así que bajas"), envez=T("y en vez"),
                bomb=T("pero al bombear"), embudo=T("y forma"), rapido=T("si bombeas"), crece=T("el embudo crece"), vecino=T("y puedes secar"),
                mide=T("por eso se mide"), sig=T("sígueme"))

def cono(t, K):
    """profundidad D y anchura w del embudo"""
    D = keyed(t, [(0, 0.0), (K["bomb"] + 0.3, 0.0), (K["embudo"] + 1.0, 1.2), (K["rapido"], 1.3), (K["vecino"] + 0.3, 3.0),
                  (K["mide"] + 1.3, 3.0), (K["mide"] + 3.3, 1.0), (DUR + 2, 0.9)])
    w = keyed(t, [(0, 2.0), (K["bomb"] + 0.3, 2.0), (K["embudo"] + 1.0, 3.2), (K["rapido"], 3.5), (K["vecino"] + 0.3, 10.0),
                  (K["mide"] + 1.3, 10.0), (K["mide"] + 3.3, 4.0), (DUR + 2, 4.0)])
    return D, w

def nivel(x, D, w): return Z_AQ - D * math.exp(-abs(x) / w)

def caudal(t, K):
    return keyed(t, [(0, 0.0), (K["envez"], 0.0), (K["envez"] + 1.5, 1.8), (K["rapido"], 1.8), (K["rapido"] + 1.2, 3.0), (K["mide"] + 1.3, 3.0),
                     (K["mide"] + 3.2, 1.2), (DUR + 2, 1.2)])

def pose(t, S):
    K = S.setdefault("K", tiempos())
    D, w = cono(t, K)
    # agua en la arena
    for i, o in enumerate(S["agua"]):
        x = -24 + (i + 0.5) * 48 / NS; top = nivel(x, D, w)
        o.location = (x, -0.025, (top - 26) / 2); o.scale = (48 / NS + 0.08, 0.02, top + 26)
    rs = random.Random(2)
    for k, c in enumerate(S["chispas"]):
        x0, z0 = rs.uniform(-15, 15), rs.uniform(-25.5, -18.5); ph = rs.uniform(0, 6)
        z = z0 + 0.15 * math.sin(t * 2 + ph)
        if abs(x0) < RB + 0.2 or abs(x0 - XV) < 0.5 or z > nivel(x0, D, w) - 0.15: hide(c); continue
        c.location = (x0 + 0.2 * math.sin(t * 0.7 + ph), -0.04, z); s = 0.6 + 0.4 * abs(math.sin(t * 3 + ph)); c.scale = (s, s, s)
    # broca: perfora, baja hasta el agua y sale
    zb = keyed(t, [(0, -0.2), (K["broca"], -1.6), (K["veinte"] + 0.2, -19.6), (K["subt"] + 1.0, Z_FONDO + 0.4), (K["subt"] + 1.3, Z_FONDO + 0.4),
                   (K["paredes"] - 0.1, 9.0)])
    perfora = t < K["subt"] + 1.3
    S["broca"].location = (0, -0.15, zb) if t < K["paredes"] else LEJOS
    S["broca"].rotation_euler = (0, 0, -t * 9 if perfora else 0)
    S["rig"].location = (0, 0, 0) if t < K["tubo"] + 0.6 else LEJOS
    if t < K["paredes"]: bar_set(S["varilla"], (0, -0.15, zb + 1.8), (0, -0.15, 7.0))
    else: bar_set(S["varilla"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    rt = random.Random(5)
    for k, o in enumerate(S["tierra"]):
        ph = rt.uniform(0, 1); sx = rt.choice((-1, 1)); vx = rt.uniform(1.2, 2.6); vz = rt.uniform(3.0, 5.0)
        u = (t * 1.4 + ph) % 1.0
        if perfora and t < K["subt"]:
            x = sx * (0.5 + vx * u); z = 0.3 + vz * u - 6 * u * u
            if z < 0.25: hide(o); continue
            o.location = (x, -0.3 - 0.4 * ph, z); o.rotation_euler = (t * 5 + k, t * 3, 0)
        else: hide(o)
    # agujero
    fondo = min(zb - 0.75, -0.1) if t < K["paredes"] else Z_FONDO
    S["hueco"].location = (0, -0.04, (0.26 + fondo) / 2); S["hueco"].scale = (2 * RB, 0.02, 0.26 - fondo)
    # derrumbe
    rr = random.Random(7); der = K["paredes"] < t < K["tubo"]
    for k, o in enumerate(S["trozos"]):
        z0 = rr.uniform(-15, -2); sx = rr.choice((-1, 1)); t0 = K["paredes"] + 0.3 + rr.uniform(0, 1.6)
        u = seg(t, t0, t0 + 0.9)
        if der and t > t0: o.location = (sx * mix(RB - 0.15, rr.uniform(0, 0.5), u), -0.07, mix(z0, z0 - 4 - 6 * u, u))
        else: hide(o)
    for k, o in enumerate(S["bultos"]):
        z0 = -2.5 - 1.6 * k; sx = 1 if k % 2 else -1; g = seg(t, K["paredes"] + 0.1 * k, K["paredes"] + 1.2 + 0.1 * k)
        if der:
            wd = 0.05 + 0.4 * g; o.location = (sx * (RB - wd / 2), -0.06, z0); o.scale = (wd, 0.03, 0.9 + 0.3 * g)
        else: hide(o)
    # tubo
    tz = keyed(t, [(0, 30.0), (K["tubo"], 30.0), (K["quince"] - 0.3, 0.0)])
    S["tubo"].location = (0, 0, tz)
    nr = len(S["rej"]); prog = seg(t, K["fondo"] + 0.3, K["rej"] + 0.3)
    S["liso"].location = (0, 0, Z_REJ) if prog < 0.99 else LEJOS
    S["liso"].scale = (1, 1, max(0.001, 1 - prog))
    for k, e in enumerate(S["rej"]):
        on = prog * nr > k
        e.scale = (1, 1, 1) if on else (0, 0, 0)
    # agua dentro del tubo
    wl = keyed(t, [(0, Z_FONDO - 0.2), (K["deja"] - 0.2, Z_FONDO - 0.2), (K["deja"] + 1.4, Z_AQ)])
    wl = min(wl, nivel(0, D, w)) if t > K["bomb"] else wl
    S["_wl"] = wl
    if wl > Z_FONDO - 0.15 and t > K["tubo"]:
        S["agua_in"].location = (0, -0.06, (wl + Z_FONDO - 0.15) / 2); S["agua_in"].scale = (2 * RT - 0.16, 0.02, wl - Z_FONDO + 0.15)
    else: hide(S["agua_in"])
    # gotas que intentan entrar (cerrado) y que entran (rejilla)
    rg = random.Random(11)
    for k, o in enumerate(S["gotas"]):
        sx = 1 if k % 2 else -1; z = rg.uniform(Z_FONDO + 0.3, Z_AQ - 0.6); ph = rg.uniform(0, 1)
        if K["cerr"] < t < K["fondo"]:
            u = ((t - K["cerr"]) * 0.8 + ph) % 1.0; x = sx * (2.6 - (2.6 - RT - 0.1) * min(1, u * 1.4))
            o.location = (x, -0.09, z)
        elif K["deja"] - 0.3 < t < K["grava"] + 1.5:
            u = ((t - K["deja"]) * 0.7 + ph) % 1.0; x = sx * 2.8 * (1 - u)
            o.location = (x, -0.09, z) if abs(x) > 0.1 else LEJOS
        else: hide(o)
    for k, o in enumerate(S["arena"]):
        sx = 1 if k % 2 else -1; z = rg.uniform(Z_FONDO + 0.3, Z_AQ - 0.6); ph = rg.uniform(0, 1)
        if K["deja"] - 0.3 < t < K["arriba"]:
            stop = RT + 0.1 if t < K["grava"] + 0.4 else RB + 0.1
            u = ((t - K["deja"]) * 0.6 + ph) % 1.0; x = sx * max(stop, 2.8 - 3.2 * u)
            o.location = (x, -0.09, z)
        else: hide(o)
    # grava, relleno y cemento
    gl = keyed(t, [(0, Z_FONDO - 1), (K["grava"], Z_FONDO - 0.3), (K["grava"] + 1.4, -16.2)])
    rg2 = random.Random(9)
    for i, (z, g) in enumerate(S["grava"]):
        xx = rg2.uniform(-0.03, 0.03)
        if gl > z and t > K["grava"] - 0.1:
            idx = i % 4
            sx = -1 if idx < 2 else 1; xb = (RT + 0.1, RT + 0.28)[idx % 2]
            g.location = (sx * xb + xx, -0.07, z)
        else: hide(g)
    rl = keyed(t, [(0, -16.2), (K["grava"] + 1.4, -16.2), (K["arriba"], -3.0)])
    cl = keyed(t, [(0, -3.0), (K["arriba"], -3.0), (K["arriba"] + 1.0, 0.25)])
    for s_, o in zip((-1, 1), S["relleno"]):
        if t > K["grava"] + 1.4: o.location = (s_ * (RB + RT) / 2, -0.06, (rl - 16.2) / 2); o.scale = (RB - RT, 0.03, rl + 16.2)
        else: hide(o)
    for s_, o in zip((-1, 1), S["cemento"]):
        if t > K["arriba"]: o.location = (s_ * (RB + RT) / 2, -0.065, (cl - 3.0) / 2); o.scale = (RB - RT, 0.04, max(0.01, cl + 3.0))
        else: hide(o)
    S["losa"].location = (0, 0.0, 0.3) if t > K["arriba"] + 0.9 else LEJOS
    for k, o in enumerate(S["sucia"]):
        u = ((t - K["sucia"]) * 0.9 + k / 8) % 1.0; sx = 1 if k % 2 else -1
        if K["sucia"] - 0.4 < t < K["ahora"]:
            z = max(0.5, 3.0 - 3.6 * u); o.location = (sx * (0.7 + 0.25 * (k % 3)), -0.3, z); o.scale = (1, 1, 0.5 if z <= 0.5 else 1)
        else: hide(o)
    # bomba de superficie: el agua sube 10 m y se queda
    top_on = K["aspire"] < t < K["bajas"]
    S["bomba"].location = (0, -0.05, 0.75) if top_on else LEJOS
    if top_on: bar_set(S["asp"], (0, -0.15, Z_AQ - 2.0), (0, -0.15, 0.6))
    else: bar_set(S["asp"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    wt = keyed(t, [(0, Z_AQ), (K["aspir"], Z_AQ), (K["aspir"] + 1.8, Z_AQ + 10.6), (K["aspir"] + 2.4, Z_AQ + 10.0)])
    wt += 0.12 * math.sin(t * 5) * seg(t, K["aspir"] + 2.4, K["aspir"] + 3)
    S["_wt"] = wt
    if top_on and t > K["aspir"] - 0.2: bar_set(S["colw"], (0, -0.24, Z_AQ - 0.2), (0, -0.24, wt))
    else: bar_set(S["colw"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    fl = S["flechas"]
    for k, f in enumerate(fl):
        if K["aire"] - 0.2 < t < K["bajas"]:
            u = ((t - K["aire"]) * 1.2 + k * 0.33) % 1.0
            if k < 2: f.location = ((-0.24, 0.24)[k], -0.3, Z_AQ + 1.0 - 0.6 * u)
            else: f.location = ((-6.0, -3.0, 3.0, 6.0)[k - 2], -0.6, 4.2 - 2.4 * u)
        else: hide(f)
    # bomba sumergida
    zs = keyed(t, [(0, 3.0), (K["bajas"], 3.0), (K["bajas"] + 2.2, Z_FONDO + 0.9)])
    sub_on = t > K["bajas"]
    S["sumer"].location = (0, -0.16, zs) if sub_on else LEJOS
    S["_zs"] = zs
    if sub_on: bar_set(S["subida"], (0, -0.16, zs + 0.5), (0, -0.16, 1.5))
    else: bar_set(S["subida"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    S["salida"].location = (0, -0.16, 1.5) if sub_on else LEJOS
    S["cubo"].location = (-1.5, -0.3, 0.55) if sub_on else LEJOS
    w2 = keyed(t, [(0, Z_FONDO + 1.4), (K["envez"], Z_FONDO + 1.4), (K["envez"] + 1.6, 1.5)])
    S["_w2"] = w2
    if t > K["envez"] - 0.1: bar_set(S["colw2"], (0, -0.24, Z_FONDO + 1.4), (0, -0.24, w2))
    else: bar_set(S["colw2"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    for k, f in enumerate(S["subeflechas"]):
        if K["envez"] < t < K["bomb"] + 0.5:
            u = ((t - K["envez"]) * 0.5 + k / 4) % 1.0; z = mix(Z_FONDO + 2, 0.0, u)
            f.location = (0.0, -0.4, z) if z < w2 else LEJOS
        else: hide(f)
    q = caudal(t, K)
    S["aguja"].location = (-0.55, -0.32, 1.5) if sub_on else LEJOS
    S["aguja"].rotation_euler = (0, mix(1.2, -1.2, q / 3.2), 0)
    S["aguja"].location.x -= 0.1 * math.sin(mix(1.2, -1.2, q / 3.2)) if sub_on else 0
    for k, o in enumerate(S["chorro"]):
        if t > K["envez"] + 1.6 and q > 0.2:
            u = (t * (0.8 + 0.5 * q) + k / 10) % 1.0; o.location = (-1.5 + 0.02 * math.sin(k * 3), -0.16, mix(1.2, 0.8, u))
        else: hide(o)
    # flujo hacia el pozo cuando se bombea
    rf = random.Random(13)
    for k, o in enumerate(S["flujo"]):
        sx = 1 if k % 2 else -1; ph = rf.uniform(0, 1); dz = rf.uniform(0.4, 3.0)
        if K["bomb"] < t < DUR + 1:
            u = (t * 0.35 + ph) % 1.0; x = sx * mix(6.5, RB + 0.1, u); z = max(nivel(x, D, w) - dz, -25.5)
            o.location = (x, -0.05, z)
        else: hide(o)
    # pozo del vecino
    lv = nivel(XV, D, w)
    if lv > ZV + 0.05:
        S["agua_v"].location = (XV, -0.06, (lv + ZV) / 2); S["agua_v"].scale = (0.42, 0.02, lv - ZV)
    else: hide(S["agua_v"])
    S["_lv"] = lv
    apply_cam(S["cam"], *cam_state(t, CAM(K), drift=0.12))

def V(at, off, lens=40): at = Vector(at); return (tuple(at + Vector(off)), tuple(at), lens)
def CAM(K):
    k = []
    def add(t, v, hold=0.0):
        k.append((t,) + v)
        if hold: k.append((t + hold,) + v)
    add(0.0, V((0, 0, -0.6), (-1.4, -4.6, 1.3), 35))
    add(1.2, V((0, 0, -1.6), (-2.5, -9, 2.2), 38))
    add(2.6, V((-1.5, 0, -7.5), (-5, -48, 8), 40))
    add(3.6, V((-1.0, 0, -7.0), (-4, -44, 7), 40))
    add(K["broca"], V((0, 0, -3), (-2, -11, 2), 40))
    add(K["veinte"], V((0, 0, -18.5), (-2, -11, 2), 40))
    add(K["subt"] + 0.4, V((0, 0, -20), (-3, -14, 2.5), 40))
    add(K["paredes"] + 0.3, V((0, 0, -8.5), (-2.5, -13, 1.5), 40))
    add(K["tubo"] + 0.6, V((0, 0, -9), (-3, -22, 3), 40))
    add(K["quince"], V((0, 0, -5), (-1.5, -8, 1.5), 40))
    add(K["cerr"] + 0.4, V((0, 0, -20), (-2, -9, 1.5), 40))
    add(K["fondo"] + 0.3, V((0, 0, -20), (1.5, -8.5, 1.5), 40))
    add(K["deja"], V((0, 0, -20.2), (1.0, -8.5, 1.2), 40))
    add(K["grava"] + 0.6, V((0, 0, -19), (-2, -10, 2), 40))
    add(K["arriba"] + 0.3, V((0, 0, -0.5), (-3, -10, 2.5), 40))
    add(K["ahora"], V((0, 0, -0.5), (-2, -10, 2.5), 40))
    add(K["aspire"] + 0.8, V((0, 0, -7.0), (-5, -44, 6), 40))
    add(K["aspir"] + 1.5, V((0, 0, -7.0), (-4, -42, 5), 40))
    add(K["aire"] + 0.5, V((0, 0, -9.5), (-3, -30, 3), 40))
    add(K["bajas"] - 0.3, V((0, 0, -9.5), (-3, -31, 3), 40))
    add(K["bajas"] + 1.0, V((0, 0, -9.5), (-5, -59, 7), 40))
    add(K["envez"] + 1.0, V((0, 0, -9.5), (-4, -59, 7), 40))
    add(K["bomb"] + 0.6, V((3.5, 0, -9.5), (-4, -60, 7), 40))
    add(K["rapido"], V((3.8, 0, -9.5), (-4, -60, 7), 40))
    add(K["vecino"] - 0.2, V((6.0, 0, -18), (-2, -25, 3), 40))
    add(K["mide"] + 0.2, V((5.5, 0, -18), (-2, -25, 3), 40))
    add(K["mide"] + 1.6, V((2.5, 0, -9.5), (-4, -60, 7), 40))
    add(DUR + 2, V((2.5, 0, -9.5), (2, -58, 7), 40))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); K = S["K"]; D, w = cono(t, K)
    zb = S["broca"].location.z if S["broca"].location.z > -100 else -20
    return {"casa": Pj((-4.8, 1.5, 3.6)), "acu": Pj((-3.0, -0.1, -21.5)), "broca": Pj((0.6, -0.1, zb)), "tl": Pj((-RT, -0.1, -5)),
            "tr": Pj((RT, -0.1, -5)), "tubo": Pj((RT, -0.1, -12)), "rej": Pj((-RT, -0.1, -20.5)), "rej2": Pj((RT, -0.1, -21.2)),
            "grava": Pj((RB, -0.1, -18.5)), "cem": Pj((RB, -0.1, -1.0)), "bomba": Pj((0.4, -0.3, 1.2)), "colw": Pj((0, -0.2, S["_wt"])),
            "aire": Pj((0.0, -0.2, Z_AQ + 0.5)), "sumer": Pj((0.3, -0.2, S["_zs"])), "cono": Pj((3.0, -0.1, nivel(3.0, D, w))),
            "vecino": Pj((XV, -0.1, -18.5)), "dial": Pj((-0.55, -0.3, 1.8)), "suelo": Pj((-1.5, -0.3, 0.3))}

if __name__ == "__main__":
    run("pozo", build, pose, anchors)
