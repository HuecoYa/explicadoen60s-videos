# «¿Y si construyes una depuradora?»: primer plano de un váter tirando de la cadena (remolino); el agua baja por la tubería
# a la alcantarilla; cubo de 128 L junto al váter; la ciudad aparece y un cubo gigante de 12.800 m³ (23,4 m de lado);
# la planta en corte, de izquierda a derecha: reja (toallitas, plástico, palo y rastrillo), la arena rompería una bomba,
# canal lento (la arena cae), aire que sube la grasa y un rascador, decantador (lo pesado se hunde, lo disuelto no),
# reactor con bacterias que se comen los puntos, se paran sin aire y vuelven con los difusores, forman grumos,
# decantador final (agua transparente) y río con peces; el lodo va a un digestor en forma de huevo, el biogás mueve
# un motor y la electricidad enciende las farolas de la planta.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("depuradora")
BG = (0.11, 0.13, 0.17)
GRASS = (0.36, 0.6, 0.32); SOIL = (0.42, 0.31, 0.22); CLAY = (0.52, 0.37, 0.26)
CON = (0.72, 0.73, 0.74); CON_IN = (0.86, 0.87, 0.86); PIPE = (0.62, 0.66, 0.72)
SEWAGE = (0.5, 0.45, 0.32); TURBID = (0.46, 0.52, 0.42); CLEAN = (0.32, 0.62, 0.95); RIVER = (0.3, 0.58, 0.9)
DOT = (0.62, 0.82, 1.0); DIRT = (0.3, 0.22, 0.14); SAND = (0.88, 0.74, 0.45); GREASE = (1.0, 0.84, 0.3)
BACT = (0.35, 0.85, 0.35); BACT_OFF = (0.45, 0.48, 0.45); FLOC = (0.45, 0.42, 0.24); SLUDGE = (0.36, 0.27, 0.16)
WHITE = (0.96, 0.96, 0.97); WALL = (0.93, 0.91, 0.86); WALL2 = (0.86, 0.84, 0.8); ROOF = (0.78, 0.32, 0.26)
WIN = (1.0, 0.85, 0.45); WOFF = (0.22, 0.24, 0.3); BULB_OFF = (0.35, 0.36, 0.4); BULB_ON = (1.0, 0.9, 0.45)
LEJOS = (0, 0, -300)
YP = -0.3               # plano de las tuberías visibles (delante del corte del terreno)
YD = -0.06              # plano de las partículas dentro de los depósitos (delante del agua)
XH = -34.0              # casa del váter
TB = Vector((XH, 3.0, 0.3))   # base del váter
ZS = -1.6               # alcantarilla
# depósitos: (x0, x1, fondo, nivel)
CANAL = (-16.0, 9.0, -2.2, -0.6)
PRIM = (12.0, 19.0, -6.0, -0.6)
REAC = (23.0, 30.0, -6.0, -0.6)
SEC = (34.0, 41.0, -6.0, -0.6)
RIO = (45.0, 55.0, -2.0, -0.5)
XR = -12.0              # reja
XG = (65.0, 3.0)        # digestor (x, y)
ZG = 7.0; RG = 4.4; KZ = 1.5   # centro, radio y estiramiento vertical del huevo
XM = 74.0               # motor-generador
LAMPS = [10.3, 21.0, 32.0, 43.0, 58.0]
random.seed(7)

def poly(pts):
    pts = [Vector(p) for p in pts]; L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    return pts, L
def at(path, s):
    pts, L = path; s = max(0.0, min(L[-1], s))
    for i in range(len(pts) - 1):
        if L[i] <= s <= L[i + 1]: return pts[i].lerp(pts[i + 1], (s - L[i]) / max(L[i + 1] - L[i], 1e-6))
    return pts[-1]

P_WC = poly([(XH, YP, 0.15), (XH, YP, ZS), (CANAL[0] - 0.2, YP, ZS)])
P_SEW = poly([(-62, YP, ZS), (CANAL[0] - 0.2, YP, ZS)])
P_PR = poly([(CANAL[1], YP, -1.2), (PRIM[0], YP, -1.2)])
P_RE = poly([(PRIM[1], YP, -1.2), (REAC[0], YP, -1.2)])
P_SE = poly([(REAC[1], YP, -1.2), (SEC[0], YP, -1.2)])
P_RI = poly([(SEC[1], YP, -0.9), (RIO[0] + 0.6, YP, -0.9), (RIO[0] + 0.6, YP, -0.6)])
P_LODO = poly([(SEC[1], YP, -5.4), (43.0, YP, -5.4), (43.0, YP, 1.4), (XG[0] - 6.5, YP, 1.4), (XG[0] - 6.5, YP, 0.9), (XG[0] - 3.0, YP, 0.9)])
P_GAS = poly([(XG[0], XG[1], ZG + RG * KZ - 0.2), (XG[0], XG[1], ZG + RG * KZ + 1.2), (XM, XG[1], ZG + RG * KZ + 1.2), (XM, XG[1], 3.4)])
P_LUZ = poly([(XM - 1.2, -0.9, 0.35), (LAMPS[0], -0.9, 0.35)])

def flow_dots(dots, path, t, on, v, phase=0.0, dy=-0.18):
    L = path[1][-1]; n = len(dots)
    for k, d in enumerate(dots):
        if not on: d.location = LEJOS; continue
        s = (L * k / n + v * t + phase) % L
        d.location = at(path, s) + Vector((0, dy, 0))

def pipe(p0, p1, r=0.25, col=PIPE):
    o = bar_obj(col, r); bar_set(o, p0, p1); return o
def pipe_path(path, r=0.25, col=PIPE):
    pts = path[0]
    for a, b in zip(pts, pts[1:]): pipe(a, b, r, col)
    for p in pts[1:-1]: sph(r, p, col, seg=12)

def tank(x0, x1, zf, back=3.4, top=0.3, col=CON):
    """depósito de hormigón cortado por delante (y=0): fondo, pared de atrás y paredes laterales"""
    box((x1 - x0 + 0.8, back + 0.4, 0.4), ((x0 + x1) / 2, back / 2, zf - 0.2), col)
    box((x1 - x0 + 0.8, 0.4, top - zf), ((x0 + x1) / 2, back + 0.2, (top + zf) / 2), CON_IN)
    for xs in (x0 - 0.2, x1 + 0.2): box((0.4, back + 0.4, top - zf + 0.4), (xs, back / 2, (top + zf) / 2 - 0.2), col)
    # cantos del corte (hormigón visto en sección)
    box((x1 - x0 + 0.8, 0.06, 0.4), ((x0 + x1) / 2, -0.03, zf - 0.2), (0.6, 0.6, 0.6))

def water(x0, x1, zf, lvl, col, back=3.4):
    o = box((x1 - x0, back - 0.15, lvl - zf), ((x0 + x1) / 2, 0.15 + (back - 0.15) / 2, (lvl + zf) / 2), col, unique=True); return o

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam, "sc": sc}
    cam.data.clip_start = 0.02
    # --- terreno en corte, con huecos para los depósitos
    holes = [(CANAL[0] - 0.4, CANAL[1] + 0.4, CANAL[2] - 0.4), (PRIM[0] - 0.4, PRIM[1] + 0.4, PRIM[2] - 0.4), (REAC[0] - 0.4, REAC[1] + 0.4, REAC[2] - 0.4),
             (SEC[0] - 0.4, SEC[1] + 0.4, SEC[2] - 0.4), (RIO[0], RIO[1], RIO[2])]
    xs = [-90.0]
    for a, b, _ in holes: xs += [a, b]
    xs.append(130.0)
    for i in range(len(xs) - 1):
        a, b = xs[i], xs[i + 1]
        hole = next((h for h in holes if abs(h[0] - a) < 1e-6 and abs(h[1] - b) < 1e-6), None)
        ztop = h_ztop = hole[2] if hole else 0.0
        if not hole:
            box((b - a, 60, 0.3), ((a + b) / 2, 30, -0.15), GRASS)
            ztop = -0.3
        else:
            box((b - a, 60 - 4, 0.3), ((a + b) / 2, 32, -0.15), GRASS)
            box((b - a, 56, 2.2), ((a + b) / 2, 32, -1.4), SOIL)      # terreno detrás del depósito
        z1 = ztop
        if z1 > -2.5:
            box((b - a, 60, z1 + 2.5), ((a + b) / 2, 30, (z1 - 2.5) / 2), SOIL); z1 = -2.5
        box((b - a, 60, z1 + 24), ((a + b) / 2, 30, (z1 - 24) / 2), CLAY)
    rng = random.Random(4)
    for k in range(220):
        x, z = rng.uniform(-70, 110), rng.uniform(-11.5, -0.6)
        if any(h[0] - 0.3 < x < h[1] + 0.3 and z > h[2] - 0.6 for h in holes): continue
        c = SOIL if z > -2.5 else CLAY
        sph(rng.uniform(0.1, 0.25), (x, 0.0, z), tuple(v * rng.uniform(0.75, 0.9) for v in c), scale=(1.3, 0.25, 1), seg=8)
    # --- casas: la del váter, en corte
    def casa_corte(x0, x1):
        h = 3.0
        box((x1 - x0, 6.4, 0.3), ((x0 + x1) / 2, 3.0, 0.15), WALL2)
        box((x1 - x0, 0.25, h), ((x0 + x1) / 2, 6.1, 0.3 + h / 2), (0.75, 0.86, 0.9))
        for xx in (x0, x1): box((0.25, 6.4, h), (xx, 3.0, 0.3 + h / 2), WALL2)
        w = (x1 - x0) / 2 + 0.4
        for s_ in (-1, 1): box((w * 1.15, 6.8, 0.25), ((x0 + x1) / 2 + s_ * w * 0.5, 3.0, h + 1.1), ROOF, rot=(0, s_ * math.radians(-32), 0))
        # azulejos
        for k in range(int(x1 - x0) * 3):
            box((0.02, 0.02, h), (x0 + 0.33 * k, 5.97, 0.3 + h / 2), (0.65, 0.78, 0.82))
    casa_corte(XH - 4, XH + 4)
    S["wins"] = []
    for x in (-58, -50, -42, -26):
        box((7, 6, 4), (x, 3.3, 2.0), WALL); box((7.4, 6.4, 0.3), (x, 3.3, 4.15), (0.6, 0.6, 0.62))
        for xx in (x - 1.8, x + 1.8): S["wins"].append(box((1.2, 0.1, 1.3), (xx, 0.27, 2.4), WIN, unique=True))
    # váter: taza (hueca), tanque con pulsador y tapa levantada
    S["wc"] = wc = empty((TB.x, TB.y, TB.z)); wc.scale = (1, 1.25, 1)
    bpy.ops.mesh.primitive_cone_add(radius1=0.18, radius2=0.31, depth=0.5, location=(0, 0, 0.25), vertices=48, end_fill_type='NOTHING')
    setup(bpy.context.object, WHITE, wc, True)
    bpy.ops.mesh.primitive_cone_add(radius1=0.06, radius2=0.27, depth=0.28, location=(0, 0, 0.36), vertices=48, end_fill_type='NOTHING')
    o = bpy.context.object; o.data.flip_normals(); setup(o, (0.93, 0.94, 0.96), wc, True)
    torus(0.29, 0.035, (0, 0, 0.5), WHITE, parent=wc)
    S["tq"] = box((0.56, 0.2, 0.42), (TB.x, TB.y + 0.48, TB.z + 0.72), WHITE)
    box((0.6, 0.24, 0.04), (TB.x, TB.y + 0.48, TB.z + 0.95), WHITE)
    S["btn"] = cyl(0.06, 0.04, (TB.x, TB.y + 0.48, TB.z + 0.98), (0.8, 0.82, 0.86))
    lid = rounded_slab(0.6, 0.7, 0.25, 0.03, (0, 0, 0), WHITE); lid.location = (TB.x, TB.y + 0.33, TB.z + 0.52); lid.rotation_euler = (math.radians(-80), 0, 0)
    S["wcw"] = cyl(1.0, 0.01, LEJOS, (0.55, 0.8, 1.0), v=40, unique=True)
    S["hole"] = cyl(1.0, 0.012, LEJOS, (0.15, 0.25, 0.4), v=24)
    S["swirl"] = [sph(0.012, LEJOS, (0.88, 0.96, 1.0), scale=(2.4, 1, 0.4), seg=8) for _ in range(30)]
    pipe((XH, 3.0, 0.15), (XH, YP, 0.15), 0.12)
    # cubo de 128 L (0,504 m de lado) y cubo de la ciudad (12.800 m³ → 23,4 m)
    S["c128"] = box((1, 1, 1), LEJOS, (0.4, 0.68, 1.0))
    S["cbig"] = box((1, 1, 1), LEJOS, (0.4, 0.68, 1.0))
    # ciudad
    S["city"] = []
    rr = random.Random(11)
    for row in range(5):
        for col in range(8):
            e = empty(LEJOS); S["city"].append((e, row, col))
            hgt = rr.choice((4, 5, 7, 10, 13))
            box((6.0, 6.0, hgt), (0, 0, hgt / 2), rr.choice((WALL, WALL2, (0.82, 0.78, 0.7), (0.75, 0.78, 0.82))), parent=e)
            box((6.3, 6.3, 0.3), (0, 0, hgt + 0.15), (0.55, 0.55, 0.58), parent=e)
            for z in range(1, int(hgt / 3) + 1): box((4.0, 0.1, 0.9), (0, -3.02, 3 * z - 1.2), (0.55, 0.65, 0.78), parent=e)
    # tuberías
    pipe_path(P_WC, 0.12)
    pipe((-62, YP, ZS), (CANAL[0] + 0.2, YP, ZS), 0.45, (0.55, 0.52, 0.5))
    for P in (P_PR, P_RE, P_SE): pipe_path(P, 0.3)
    pipe_path(P_RI, 0.3)
    pipe_path(P_LODO, 0.22, (0.55, 0.4, 0.3))
    # --- canal: reja + desarenador + desengrasador
    tank(CANAL[0], CANAL[1], CANAL[2])
    S["w_canal"] = water(CANAL[0], CANAL[1], CANAL[2], CANAL[3], SEWAGE)
    S["reja"] = []
    for k in range(10):
        y = 0.25 + 0.3 * k
        o = box((0.07, 0.07, 3.2), (XR, y, -0.6), (0.3, 0.32, 0.36), rot=(0, math.radians(-14), 0)); S["reja"].append(o)
    box((0.2, 3.2, 0.12), (XR - 0.4, 1.6, 0.95), (0.3, 0.32, 0.36))
    S["rake"] = empty(LEJOS)
    box((0.12, 3.0, 0.16), (0, 0, 0), (0.95, 0.55, 0.15), parent=S["rake"])
    for k in range(10): box((0.25, 0.04, 0.04), (-0.12, -1.35 + 0.3 * k, -0.05), (0.95, 0.55, 0.15), parent=S["rake"])
    box((1.2, 1.2, 0.8), (XR + 1.6, 1.8, 0.7), (0.3, 0.45, 0.35))     # contenedor de basura
    S["deb"] = [rounded_slab(0.9, 0.7, 0.1, 0.04, (0, 0, 0), WHITE),
                cyl(0.17, 0.8, LEJOS, (0.3, 0.6, 0.95), rot=(0, math.pi / 2, 0)),
                cyl(0.08, 1.4, LEJOS, (0.5, 0.33, 0.18), rot=(0, math.pi / 2, 0.3)),
                rounded_slab(0.75, 0.6, 0.08, 0.04, (0, 0, 0), (0.95, 0.9, 0.85))]
    S["sand"] = [sph(0.06, LEJOS, SAND, seg=8) for _ in range(26)]
    S["sandbed"] = box((1, 1, 1), LEJOS, SAND)
    S["pump"] = empty(LEJOS)
    box((1.0, 0.9, 1.0), (0, 0, 0), (0.25, 0.42, 0.75), parent=S["pump"])
    S["pump_l"] = sph(0.12, (0.3, -0.46, 0.38), (0.3, 0.9, 0.4), parent=S["pump"], seg=10, unique=True)
    S["imp"] = empty((0, -0.47, 0), parent=S["pump"])
    for k in range(3): box((0.08, 0.03, 0.7), (0, 0, 0), (0.92, 0.92, 0.95), parent=S["imp"], rot=(0, k * math.pi / 3, 0))
    S["bub_g"] = [sph(0.07, LEJOS, (0.92, 0.96, 1.0), seg=8) for _ in range(24)]
    S["grease"] = [sph(0.17, LEJOS, GREASE, scale=(1.4, 0.6, 0.7), seg=12) for _ in range(10)]
    for k in range(4): box((0.35, 0.3, 0.06), (2.7 + 1.6 * k, 1.2, CANAL[2] + 0.03), (0.25, 0.25, 0.28))
    S["skim"] = empty(LEJOS)
    box((0.12, 3.0, 0.5), (0, 0, 0), (0.92, 0.3, 0.25), parent=S["skim"])
    box((0.5, 0.5, 0.5), (8.6, 1.6, -0.25), (0.92, 0.3, 0.25))
    S["w_dots"] = [sph(0.045, LEJOS, DOT, seg=8) for _ in range(40)]
    # --- decantador primario
    tank(PRIM[0], PRIM[1], PRIM[2])
    S["w_prim"] = water(PRIM[0], PRIM[1], PRIM[2], PRIM[3], SEWAGE)
    S["heavy"] = [sph(0.15, LEJOS, DIRT, seg=10) for _ in range(26)]
    S["diss1"] = [sph(0.055, LEJOS, (0.22, 0.17, 0.1), seg=6) for _ in range(46)]
    S["bed1"] = box((1, 1, 1), LEJOS, SLUDGE)
    S["scraper"] = box((0.15, 3.0, 0.4), LEJOS, (0.9, 0.55, 0.2))
    # --- reactor biológico
    tank(REAC[0], REAC[1], REAC[2])
    S["w_reac"] = water(REAC[0], REAC[1], REAC[2], REAC[3], SEWAGE)
    S["diss2"] = [sph(0.06, LEJOS, (0.22, 0.17, 0.1), seg=6) for _ in range(70)]
    S["bact"] = [sph(0.13, LEJOS, BACT, scale=(1.9, 0.8, 0.9), seg=12, unique=True) for _ in range(34)]
    for k in range(7): cyl(0.3, 0.12, (REAC[0] + 0.6 + 0.95 * k, 1.4, REAC[2] + 0.06), (0.22, 0.24, 0.28))
    S["bub_r"] = [sph(0.08, LEJOS, (0.92, 0.96, 1.0), seg=8) for _ in range(46)]
    S["flocs"] = [sph(0.35, LEJOS, FLOC, seg=14) for _ in range(6)]
    box((1.4, 1.4, 1.6), (REAC[0] + 2.0, 4.6, 1.0), (0.3, 0.45, 0.75))                    # soplantes (detrás)
    S["fan"] = empty((REAC[0] + 2.0, 3.85, 1.0))
    for k in range(3): box((0.08, 0.03, 1.0), (0, 0, 0), (0.92, 0.92, 0.95), parent=S["fan"], rot=(0, k * math.pi / 3, 0))
    # --- decantador secundario
    tank(SEC[0], SEC[1], SEC[2])
    S["w_sec"] = water(SEC[0], SEC[1], SEC[2], SEC[3], TURBID)
    S["flocs2"] = [sph(0.22, LEJOS, FLOC, seg=10) for _ in range(30)]
    S["bed2"] = box((1, 1, 1), LEJOS, SLUDGE)
    # --- río
    box((RIO[1] - RIO[0], 8, 0.3), ((RIO[0] + RIO[1]) / 2, 4, RIO[2] - 0.15), (0.6, 0.55, 0.4))
    box((RIO[1] - RIO[0], 0.3, 2.5), ((RIO[0] + RIO[1]) / 2, 8.0, -0.9), (0.5, 0.42, 0.3))
    water(RIO[0], RIO[1], RIO[2], RIO[3], RIVER, back=8.0)
    S["fish"] = []
    for k in range(2):
        e = empty(LEJOS); S["fish"].append(e)
        sph(0.28, (0, 0, 0), (0.98, 0.55, 0.2), parent=e, scale=(1.6, 0.5, 0.8), seg=14)
        bpy.ops.mesh.primitive_cone_add(radius1=0.25, radius2=0, depth=0.4, location=(-0.55, 0, 0), rotation=(0, math.pi / 2, 0), vertices=12)
        setup(bpy.context.object, (0.98, 0.55, 0.2), e); sph(0.04, (0.28, -0.14, 0.06), (0.05, 0.05, 0.05), parent=e, seg=6)
    S["rio_dots"] = [sph(0.06, LEJOS, (0.85, 0.95, 1.0), seg=8) for _ in range(22)]
    S["dots_pipe"] = [sph(0.09, LEJOS, DOT, seg=8) for _ in range(60)]
    S["dots_lodo"] = [sph(0.12, LEJOS, SLUDGE, seg=8) for _ in range(28)]
    # --- digestor (huevo) en corte
    bpy.ops.mesh.primitive_cube_add(size=1, location=(XG[0], XG[1] - 6, ZG)); cutF = bpy.context.object; cutF.scale = (14, 12, 30); cutF.hide_render = True
    bpy.ops.mesh.primitive_cube_add(size=1, location=(XG[0], XG[1], ZG + 20)); cutL = bpy.context.object; cutL.scale = (14, 14, 20); cutL.hide_render = True
    S["cutL"] = cutL
    def cutmods(o, cutters, th=None, inner=None):
        if th:
            m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
            if inner: o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
        for c in cutters:
            b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = c
            try: b.solver = 'MANIFOLD'
            except Exception: b.solver = 'EXACT'
        return o
    S["egg"] = o = sph(RG, (XG[0], XG[1], ZG), (0.82, 0.84, 0.88), scale=(1, 1, KZ), seg=48); cutmods(o, [cutF], 0.35, (0.6, 0.62, 0.66))
    S["egg_s"] = o = sph(RG - 0.36, (XG[0], XG[1], ZG), SLUDGE, scale=(1, 1, (RG * KZ - 0.36) / (RG - 0.36)), seg=48, unique=True); cutmods(o, [cutF, cutL])
    for dx in (-2.6, 2.6): box((0.6, 0.6, 2.6), (XG[0] + dx, XG[1] + 2.5, 1.3), CON)
    S["gas_b"] = [sph(0.14, LEJOS, (0.95, 0.85, 0.5), seg=8) for _ in range(30)]
    S["gas_d"] = [sph(0.13, LEJOS, (0.95, 0.85, 0.5), seg=8) for _ in range(20)]
    S["stir"] = empty((XG[0], XG[1] - 0.1, ZG - 1.0))
    for k in range(2): box((2.4, 0.06, 0.18), (0, 0, 0), (0.7, 0.72, 0.76), parent=S["stir"], rot=(0, k * math.pi / 2, 0))
    pipe((XG[0], XG[1] - 0.1, ZG - 1.0), (XG[0], XG[1] - 0.1, ZG + RG * KZ), 0.07, (0.7, 0.72, 0.76))
    pipe_path(P_GAS, 0.16, (0.95, 0.8, 0.3))
    # motor-generador con ventana de llama, volante y casa de control
    box((3.4, 3.0, 2.8), (XM, XG[1], 1.7), (0.3, 0.36, 0.45))
    box((1.5, 0.1, 1.1), (XM - 0.5, XG[1] - 1.52, 1.9), (0.08, 0.08, 0.1))
    S["flame"] = [sph(0.2, LEJOS, c, seg=10, unique=True) for c in ((1.0, 0.55, 0.15), (1.0, 0.8, 0.25), (1.0, 0.45, 0.1))]
    S["fly"] = empty((XM + 1.0, XG[1] - 1.6, 1.6))
    cyl(0.7, 0.15, (0, 0, 0), (0.75, 0.77, 0.8), parent=S["fly"], rot=(math.pi / 2, 0, 0))
    box((1.2, 0.05, 0.14), (0, -0.09, 0), (0.95, 0.3, 0.25), parent=S["fly"])
    box((6, 5, 4), (XM + 6.5, 4, 2.0), WALL)
    for xx in (XM + 5.0, XM + 8.0): S["wins"].append(box((1.4, 0.1, 1.3), (xx, 1.45, 2.4), WOFF, unique=True))
    # farolas y cable
    S["bulbs"] = []
    for x in LAMPS:
        cyl(0.08, 4.5, (x, -1.0, 2.25), (0.35, 0.37, 0.42)); box((0.8, 0.12, 0.1), (x + 0.35, -1.0, 4.5), (0.35, 0.37, 0.42))
        S["bulbs"].append(sph(0.42, (x + 0.7, -1.0, 4.35), BULB_OFF, seg=12, unique=True))
    pipe_path(P_LUZ, 0.05, (0.15, 0.15, 0.18))
    S["sparks"] = [sph(0.13, LEJOS, (1.0, 0.9, 0.3), seg=8) for _ in range(36)]
    dyn = [cam, cutF, cutL, S["wc"], S["btn"], S["wcw"], S["hole"], S["swirl"], S["c128"], S["cbig"], [e for e, _, _ in S["city"]],
           S["rake"], S["deb"], S["sand"], S["sandbed"], S["pump"], S["bub_g"], S["grease"], S["skim"], S["w_dots"], S["heavy"], S["diss1"],
           S["bed1"], S["scraper"], S["diss2"], S["bact"], S["bub_r"], S["flocs"], S["fan"], S["flocs2"], S["bed2"], S["fish"], S["rio_dots"],
           S["dots_pipe"], S["dots_lodo"], S["egg"], S["egg_s"], S["gas_b"], S["gas_d"], S["stir"], S["flame"], S["fly"], S["bulbs"],
           S["sparks"], S["wins"], S["w_canal"], S["w_prim"], S["w_reac"], S["w_sec"]]
    join_static(dyn)
    return sc, S

# ---------- utilidades de estado ----------
R = random.Random(21)
SAND0 = [(R.uniform(0, 1), R.uniform(-2.0, -0.8)) for _ in range(26)]
HEAVY0 = [(R.uniform(PRIM[0] + 0.5, PRIM[1] - 0.5), R.uniform(-5.0, -1.0), R.uniform(0, 6.28)) for _ in range(26)]
DISS1 = [(R.uniform(PRIM[0] + 0.4, PRIM[1] - 0.4), R.uniform(-5.6, -0.9), R.uniform(0, 6.28)) for _ in range(46)]
DISS2 = [(R.uniform(REAC[0] + 0.4, REAC[1] - 0.4), R.uniform(-5.6, -0.9), R.uniform(0, 6.28)) for _ in range(70)]
BACT0 = [(R.uniform(REAC[0] + 0.6, REAC[1] - 0.6), R.uniform(-5.4, -1.0), R.uniform(0, 6.28)) for _ in range(34)]
FLOC_C = [(REAC[0] + 1.0 + 1.0 * k, -2.0 - 1.8 * (k % 2) - 0.6 * ((k * 7) % 3)) for k in range(6)]
FLOCS2 = [(R.uniform(SEC[0] + 0.6, SEC[1] - 0.6), R.uniform(-4.6, -1.2), R.uniform(0.6, 1.2)) for _ in range(30)]

def colmix(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))

def eaten(t):
    """fracción de suciedad disuelta comida en el reactor"""
    a, b = T("se comen"), T("pero necesitan") + 0.3
    c, d = T("así que unas máquinas") + 0.6, T("esas bacterias")
    return 0.45 * seg(t, a, b) + 0.45 * seg(t, c, d)

def asleep(t): return win01(t, T("pero necesitan") + 0.2, T("así que unas máquinas") + 0.6, 0.3, 0.3)

def pose(t, S):
    sc = S["sc"]
    # --- váter: pulsador y remolino
    S["btn"].location.z = TB.z + 0.98 - 0.025 * win01(t, 0.0, 0.7, 0.05, 0.2)
    flush = win01(t, -0.1, 4.6, 0.05, 0.8)
    zw = TB.z + keyed(t, [(0, 0.42), (2.0, 0.3), (3.4, 0.27), (5.0, 0.42)])
    rw = 0.06 + 0.21 * (zw - TB.z - 0.22) / 0.28
    if t < 9:
        S["wcw"].location = (TB.x, TB.y, zw); S["wcw"].scale = (rw, rw * 1.25, 1)
        hr = 0.03 + 0.07 * flush
        S["hole"].location = (TB.x, TB.y, zw + 0.004); S["hole"].scale = (hr * flush + 0.001, hr * 1.25 * flush + 0.001, 1)
        for k, d in enumerate(S["swirl"]):
            u = ((k / 30) - t * 0.5) % 1.0
            r = (0.03 + rw * 0.95 * u)
            a = 3.2 * u * 6.28 * 0.5 - t * (9 + 6 * flush) + k * 0.6
            if flush < 0.05: d.location = LEJOS; continue
            d.location = (TB.x + r * math.cos(a), TB.y + 1.25 * r * math.sin(a), zw + 0.008)
            d.rotation_euler = (0, 0, a + math.pi / 2)
    else:
        S["wcw"].location = LEJOS; S["hole"].location = LEJOS
        for d in S["swirl"]: d.location = LEJOS
    # --- cubos
    c0, c1 = T("cada persona"), T("en una ciudad")
    if c0 - 0.2 < t < T("todos acaban") + 1:
        s = 0.504 * seg(t, c0 + 0.6, T("al día", fin=True))
        S["c128"].location = (TB.x + 1.15, 2.5, 0.3 + s / 2); S["c128"].scale = (0.504, 0.504, max(s, 0.001))
    else: S["c128"].location = LEJOS
    g = seg(t, T("son casi"), T("diarios", fin=True))
    dr = seg(t, T("todos acaban") + 0.2, T("primero llegan"))
    if g > 0 and dr < 1:
        h = 23.4 * g * (1 - dr)
        S["cbig"].location = (-46, 24, max(h, 0.01) / 2); S["cbig"].scale = (23.4, 23.4, max(h, 0.01))
    else: S["cbig"].location = LEJOS
    cp = seg(t, c1 - 0.2, T("de cien mil", fin=True) + 0.3)
    for e, row, col in S["city"]:
        d = (row * 8 + col) / 40
        p = ss((cp - d * 0.7) / 0.3) * (1 - seg(t, T("primero llegan") + 0.5, T("plásticos")))
        if p > 0.01:
            e.location = (-66 + 7.5 * col + (row % 2) * 3.5, 12 + 8.5 * row, 0); e.scale = (1, 1, p)
        else: e.location = LEJOS
    # --- puntos en tuberías
    dots = S["dots_pipe"]
    for d in dots: d.location = LEJOS
    if 1.2 < t < 8.0: flow_dots(dots[:14], P_WC, t, True, 3.0, dy=-0.15)
    elif 12 < t < T("primero llegan") + 3.0:
        flow_dots(dots[:40], P_SEW, t, True, 7.0 * (0.5 + seg(t, T("todos acaban"), T("todos acaban") + 1)), dy=-0.5)
    elif T("ahora el agua") - 0.4 < t < T("lo más pesado"): flow_dots(dots[:10], P_PR, t, True, 2.5, dy=-0.33)
    elif T("pero lo peor") < t < T("bacterias"): flow_dots(dots[:10], P_RE, t, True, 2.5, dy=-0.33)
    elif T("en otro depósito") - 0.3 < t < T("los grumos se"): flow_dots(dots[:10], P_SE, t, True, 2.5, dy=-0.33)
    elif T("esa agua vuelve") - 0.4 < t < T("y el lodo") + 0.5: flow_dots(dots[:16], P_RI, t, True, 3.0, dy=-0.33)
    flow_dots(S["dots_lodo"], P_LODO, t, T("y el lodo") < t < T("ese gas"), 3.2, dy=-0.25)
    # --- reja: basura que llega y rastrillo
    r0 = T("primero llegan") - 1.5; rk0, rk1 = T("plásticos") + 0.3, T("pero la arena") + 0.6
    zr = keyed(t, [(rk0, -2.1), (rk1, 1.0)]) if t > rk0 else -2.1
    S["rake"].location = (XR - 0.45 - 0.25 * (zr + 0.6), 1.6, zr) if r0 < t < T("así que el agua cruza") else LEJOS
    lands = [T("toallitas") - 0.9, T("plásticos") - 1.2, T("palos") - 0.9, T("toallitas") - 0.2]
    ys = [0.9, 1.9, 1.4, 2.5]
    for k, o in enumerate(S["deb"]):
        if not (r0 < t < T("así que el agua cruza")): o.location = LEJOS; continue
        x = mix(XR - 4.5, XR - 0.45, seg(t, lands[k] - 1.2, lands[k]))
        z = -0.75 + 0.06 * math.sin(t * 3 + k)
        if t > rk0 and zr > z - 0.15: z = zr + 0.15; x = XR - 0.45 - 0.25 * (z + 0.6) - 0.15
        if t > rk1 - 0.2: o.location = LEJOS; continue
        o.location = (x, ys[k], z)
        if k in (0, 3): o.rotation_euler = (math.radians(70), 0, 0.2 * k)
    # --- arena: pasa la reja, golpea la bomba o cae en el canal lento
    a_ar, a_bo, a_ca, a_fo = T("pero la arena"), T("y destrozaría"), T("así que el agua cruza"), T("y la arena cae")
    pump_on = a_ar - 0.2 < t < a_ca + 0.2
    if pump_on:
        sh = 0.06 * math.sin(t * 50) * seg(t, a_bo, a_bo + 0.3)
        S["pump"].location = (XR + 2.5 + sh, -0.4, -1.4 + sh); S["pump"].scale = (1, 1, 1) if t < a_ca else (0.01,) * 3
        S["imp"].rotation_euler = (0, t * 14 * (1 - 0.7 * seg(t, a_bo, a_bo + 1.0)), 0)
        set_color(S["pump_l"], (0.95, 0.25, 0.2) if t > a_bo and int(t * 6) % 2 else (0.3, 0.9, 0.4))
    else: S["pump"].location = LEJOS
    for k, d in enumerate(S["sand"]):
        u0, z0 = SAND0[k]
        if a_ar - 0.4 < t < a_ca:
            s = ((t - (a_ar - 0.4)) * 2.6 + u0 * 3.0) % 3.0
            d.location = (XR - 1.0 + s, YD, z0 + 0.4 * math.sin(s * 2 + k))
        elif a_ca <= t < DUR:
            if t > T("y aquí viene") and not (a_ca < t < T("ahora el agua") + 3): d.location = LEJOS; continue
            u = seg(t, a_ca + 0.2 + u0 * 1.0, a_fo + 0.8 + u0 * 1.2)
            x = mix(-7.5 + u0 * 1.5, -6.5 + u0 * 7.5, u)
            z = mix(z0, CANAL[2] + 0.07 + 0.08 * (k % 3), u ** 1.6)
            d.location = (x, YD, z)
        else: d.location = LEJOS
    hb = 0.28 * seg(t, a_fo, a_fo + 1.6)
    if hb > 0.005 and t < T("y aquí viene"):
        S["sandbed"].location = (-3.2, 1.7, CANAL[2] + hb / 2); S["sandbed"].scale = (8.0, 3.3, hb)
    else: S["sandbed"].location = LEJOS
    # agua del canal: puntos rápidos antes, lentos en el desarenador
    for k, d in enumerate(S["w_dots"]):
        if not (T("todos acaban") < t < T("lo más pesado")): d.location = LEJOS; continue
        z = -0.85 - 1.2 * ((k * 0.37) % 1.0)
        L = CANAL[1] - CANAL[0]
        s = (k / 40 * L + t * (1.0 if t > a_ca else 2.6)) % L
        x = CANAL[0] + s
        v = 2.6 if x < -8 else 0.7
        d.location = (x, YD - 0.02, z)
    # aire y grasa
    a_so, a_su, a_re = T("así que soplas"), T("la grasa sube"), T("y la retiras")
    for k, d in enumerate(S["bub_g"]):
        if a_so - 0.1 < t < T("lo más pesado"):
            u = ((t - a_so) * 0.9 + k / 24) % 1.0
            d.location = (2.7 + 1.6 * (k % 4) + 0.15 * math.sin(k + t * 4), YD, CANAL[2] + 0.1 + u * (CANAL[3] - CANAL[2] - 0.15))
        else: d.location = LEJOS
    xs_ = keyed(t, [(a_re - 0.1, 2.3), (T("ahora el agua") - 0.1, 8.3)]) if t > a_re - 0.1 else 2.3
    S["skim"].location = (xs_, 1.6, CANAL[3] + 0.05) if T("pero aún flota") - 0.5 < t < T("lo más pesado") else LEJOS
    for k, d in enumerate(S["grease"]):
        if not (T("pero aún flota") - 0.6 < t < T("lo más pesado")): d.location = LEJOS; continue
        x0 = 2.6 + 0.55 * k
        zf = keyed(t, [(a_so + 0.3 + 0.08 * k, -1.7 + 0.25 * (k % 3)), (a_su + 0.5 + 0.1 * k, CANAL[3] + 0.04)])
        x = x0 + 0.08 * math.sin(t * 2 + k)
        if t > a_re - 0.1 and xs_ + 0.25 > x: x = xs_ + 0.25 + 0.05 * (k % 3)
        if x > 8.25: d.location = (8.6, 1.6, 0.05); continue
        d.location = (x, YD - 0.05, zf)
    # --- decantador primario
    a_pe, a_pp = T("lo más pesado"), T("pero lo peor")
    for k, d in enumerate(S["heavy"]):
        if not (T("ahora el agua") - 0.3 < t < T("y aquí viene")): d.location = LEJOS; continue
        x, z0, ph = HEAVY0[k]
        u = seg(t, a_pe + 0.1 + 0.03 * k, a_pp - 0.2 + 0.04 * k)
        d.location = (x + 0.08 * math.sin(t + ph), YD, mix(z0, PRIM[2] + 0.12, u))
    hb1 = 0.35 * seg(t, a_pe + 0.5, a_pp + 0.5)
    if hb1 > 0.005: S["bed1"].location = ((PRIM[0] + PRIM[1]) / 2, 1.7, PRIM[2] + hb1 / 2); S["bed1"].scale = (PRIM[1] - PRIM[0], 3.3, hb1)
    else: S["bed1"].location = LEJOS
    S["scraper"].location = (PRIM[1] - 0.5 - ((t * 0.8) % (PRIM[1] - PRIM[0] - 1.0)), 1.7, PRIM[2] + hb1 + 0.2)
    pulse = win01(t, T("y eso no"), T("así que contratas"), 0.2, 0.3)
    for k, d in enumerate(S["diss1"]):
        x, z, ph = DISS1[k]
        d.location = (x + 0.12 * math.sin(t * 1.3 + ph), YD, z + 0.1 * math.cos(t * 1.7 + ph))
        sz = 1 + 0.9 * pulse * (0.5 + 0.5 * math.sin(t * 8 + ph))
        d.scale = (sz, sz, sz)
    set_color(S["w_prim"], colmix(SEWAGE, (0.55, 0.52, 0.4), seg(t, a_pe, a_pp)))
    # --- reactor
    fr = eaten(t); sl = asleep(t)
    b_in = seg(t, T("bacterias") - 0.2, T("bacterias") + 0.5)
    a_gr, a_ot = T("esas bacterias"), T("en otro depósito")
    clump = seg(t, a_gr + 0.2, T("forman grumos", fin=True) + 0.2)
    for k, d in enumerate(S["diss2"]):
        x, z, ph = DISS2[k]
        if (k + 0.5) / 70 < fr * 0.98 or t > T("y el lodo") + 1: d.location = LEJOS; continue
        d.location = (x + 0.12 * math.sin(t * 1.3 + ph), YD, z + 0.1 * math.cos(t * 1.7 + ph))
    for k, b in enumerate(S["bact"]):
        if b_in <= 0.01 or t > a_ot + 3.0: b.location = LEJOS; continue
        x, z, ph = BACT0[k]
        act = 1 - 0.85 * sl
        px = x + 0.7 * math.sin(t * 0.9 * act + ph) * act + 0.2 * math.sin(ph * 3)
        pz = z + 0.4 * math.cos(t * 0.7 * act + ph * 1.3) * act
        cx, cz = FLOC_C[k % 6]
        p = Vector((px, YD - 0.05, pz)).lerp(Vector((cx + 0.35 * math.cos(k * 2.1), YD - 0.1, cz + 0.3 * math.sin(k * 2.1))), clump)
        b.location = p; b.scale = (1.9 * b_in, 0.8 * b_in, 0.9 * b_in)
        b.rotation_euler = (0, math.sin(t * 3 * act + ph) * 0.6, 0)
        set_color(b, colmix(BACT, BACT_OFF, sl))
    for k, f in enumerate(S["flocs"]):
        if clump > 0.3 and t < a_ot + 3.0:
            cx, cz = FLOC_C[k]; s = 1.0 + 0.6 * seg(t, a_gr + 0.8, a_ot)
            f.location = (cx, YD + 0.25, cz); f.scale = (s * clump, s * clump * 0.5, s * clump)
        else: f.location = LEJOS
    air = seg(t, T("así que unas máquinas") + 0.3, T("así que unas máquinas") + 1.0) * (1 - seg(t, T("y el lodo"), T("y el lodo") + 0.5))
    S["fan"].rotation_euler = (0, t * 12 * air, 0)
    for k, d in enumerate(S["bub_r"]):
        if air > 0.02:
            u = ((t - T("así que unas máquinas")) * 0.8 + k / 46) % 1.0
            d.location = (REAC[0] + 0.6 + 0.95 * (k % 7) + 0.15 * math.sin(k + t * 3), YD - 0.12, REAC[2] + 0.2 + u * 5.2)
            d.scale = (air,) * 3
        else: d.location = LEJOS
    set_color(S["w_reac"], colmix(SEWAGE, TURBID, fr / 0.9))
    # --- decantador secundario
    a_hu, a_ar2 = T("los grumos se"), T("y arriba queda")
    for k, f in enumerate(S["flocs2"]):
        if not (a_ot - 0.3 < t < DUR): f.location = LEJOS; continue
        x, z0, sp = FLOCS2[k]
        u = seg(t, a_hu - 0.2 + 0.03 * k, a_ar2 + 0.6 + 0.03 * k)
        f.location = (x + 0.1 * math.sin(t + k), YD - 0.05, mix(z0, SEC[2] + 0.15 + 0.1 * (k % 3), u))
        f.scale = (sp, sp * 0.5, sp * 0.8)
    hb2 = 0.4 * seg(t, a_ar2 - 0.3, a_ar2 + 1.0) * (1 - 0.6 * seg(t, T("y el lodo") + 0.5, T("sin aire")))
    if hb2 > 0.005: S["bed2"].location = ((SEC[0] + SEC[1]) / 2, 1.7, SEC[2] + hb2 / 2); S["bed2"].scale = (SEC[1] - SEC[0], 3.3, hb2)
    else: S["bed2"].location = LEJOS
    set_color(S["w_sec"], colmix(TURBID, CLEAN, seg(t, a_ar2 - 0.2, T("transparente", fin=True) + 0.3)))
    # --- río
    for k, d in enumerate(S["rio_dots"]):
        s = (k / 22 * 10 + t * 1.6) % 10
        d.location = (RIO[0] + s, YD, -0.9 - 0.9 * ((k * 0.41) % 1.0)) if t > 56 else LEJOS
    for k, e in enumerate(S["fish"]):
        if t > 56:
            x = RIO[0] + 1.5 + ((t * (0.9 + 0.3 * k) + 4 * k) % 7)
            e.location = (x, YD - 0.25, -1.2 - 0.5 * k + 0.12 * math.sin(t * 3 + k)); e.rotation_euler = (0, 0.1 * math.sin(t * 4 + k), 0.25 * math.sin(t * 6 + k))
        else: e.location = LEJOS
    # --- digestor
    a_me, a_sa, a_ot2, a_ga, a_el = T("lo metes"), T("sin aire"), T("otras bacterias"), T("ese gas"), T("y da electricidad")
    lvl = keyed(t, [(0, 0.35), (a_me, 0.35), (a_sa + 0.4, 0.72), (DUR + 1, 0.72)])
    ztop = ZG - RG * KZ + 0.36 + lvl * (2 * RG * KZ - 0.72)
    S["cutL"].location = (XG[0], XG[1], ztop + 10)
    S["stir"].rotation_euler = (0, t * 1.5, 0)
    for k, d in enumerate(S["gas_b"]):
        if t > a_ot2 + 0.2:
            u = ((t - a_ot2) * 0.7 + k / 30) % 1.0
            x = XG[0] - 2.8 + 5.6 * ((k * 0.618) % 1.0)
            z0 = 1.8 + 1.0 * ((k * 0.37) % 1.0)
            z = mix(z0, ztop + 1.6, u)
            d.location = (x + 0.15 * math.sin(t * 3 + k), XG[1] - 0.15, z)
            d.scale = (0.6 + 0.5 * u,) * 3
        else: d.location = LEJOS
    flow_dots(S["gas_d"], P_GAS, t, t > a_ot2 + 1.0, 4.0, dy=-0.25)
    burn = seg(t, a_ga, a_ga + 0.4)
    for k, f in enumerate(S["flame"]):
        if burn > 0:
            s = burn * (0.8 + 0.35 * math.sin(t * 17 + k * 2))
            f.location = (XM - 0.9 + 0.4 * k, XG[1] - 1.5, 1.7 + 0.15 * math.sin(t * 13 + k)); f.scale = (s, 0.4 * s, 1.4 * s)
        else: f.location = LEJOS
    S["fly"].rotation_euler = (0, t * 10 * burn, 0)
    el = seg(t, a_el, a_el + 0.4)
    flow_dots(S["sparks"], P_LUZ, t, el > 0, 14.0, dy=-0.12)
    for k, b in enumerate(S["bulbs"]):
        on = seg(t, a_el + 0.25 * (len(LAMPS) - k), a_el + 0.25 * (len(LAMPS) - k) + 0.3)
        set_color(b, colmix(BULB_OFF, BULB_ON, on))
    for w in S["wins"][-2:]: set_color(w, colmix(WOFF, WIN, el))
    apply_cam(S["cam"], *cam_smooth(t, CAMK))

def V_(at, off, lens=35):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)
def cam_smooth(t, ks, drift=0.02):
    if t <= ks[0][0]: a = b = ks[0]; u = 0
    else:
        for i in range(len(ks) - 1):
            if ks[i][0] <= t <= ks[i + 1][0]: break
        a, b = ks[i], ks[i + 1]; u = ss((t - a[0]) / max(b[0] - a[0], 1e-4))
    pos = Vector(a[1]).lerp(Vector(b[1]), u); tgt = Vector(a[2]).lerp(Vector(b[2]), u); lens = mix(a[3], b[3], u)
    pos += Vector((math.sin(t * 0.9), 0.7 * math.sin(t * 0.7), 0.8 * math.sin(t * 1.1))) * drift
    return pos, tgt, lens
def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    PC = (PRIM[0] + PRIM[1]) / 2; RC = (REAC[0] + REAC[1]) / 2; SCX = (SEC[0] + SEC[1]) / 2
    add(0.0, V_(TB + Vector((0, 0.05, 0.3)), (0.0, -0.75, 0.75), 32))
    add(T("y en unos"), V_(TB + Vector((0, 0.05, 0.3)), (0.0, -0.95, 0.85), 32))
    add(T("el agua ha"), V_((XH, 1.0, -0.2), (0.0, -6.5, 1.0), 30))
    add(T("y si tuvieras"), V_((XH + 1, 0, -0.4), (0, -14, 1.2), 35))
    add(T("vamos a construir"), V_((XH + 3, 0, 0.5), (0, -20, 2.0), 35))
    add(T("cada persona") + 0.4, V_((TB.x + 0.6, 2.5, 0.75), (0, -3.6, 0.7), 35))
    add(T("al día", fin=True), V_((TB.x + 0.6, 2.5, 0.75), (0, -3.9, 0.8), 35))
    add(T("en una ciudad") + 0.6, V_((-40, 14, 7), (0, -70, 14), 35))
    add(T("diarios", fin=True), V_((-41, 14, 9), (0, -82, 14), 35))
    add(T("todos acaban") + 0.7, V_((-20, 0, -1.2), (0, -10, 1.2), 35))
    add(T("primero llegan") + 0.5, V_((XR - 1.4, 1.2, -0.9), (-2.6, -4.6, 1.5), 32))
    add(T("palos", fin=True), V_((XR - 1.0, 1.2, -0.7), (-2.4, -4.8, 1.8), 32))
    add(T("pero la arena") + 0.4, V_((XR + 1.4, 0.5, -1.3), (-0.8, -6.0, 1.0), 32))
    add(T("así que el agua cruza") + 0.4, V_((-4.5, 0, -1.6), (0, -6.0, 0.7), 35))
    add(T("pero aún flota"), V_((-3.0, 0, -1.6), (0, -6.0, 0.7), 35))
    add(T("así que soplas") + 0.2, V_((4.6, 0, -1.4), (0, -7.0, 0.8), 35))
    add(T("y la retiras", fin=True), V_((6.2, 0, -1.4), (0, -7.0, 0.8), 35))
    add(T("ahora el agua") + 0.8, V_((PC, 0, -3.0), (0, -12.5, 1.2), 35))
    add(T("pero lo peor") + 0.5, V_((PC, 0, -3.0), (0, -10.5, 0.8), 35))
    add(T("así que contratas") + 0.3, V_((RC, 0, -3.0), (0, -12.5, 1.2), 35))
    add(T("bacterias") + 0.3, V_((RC - 0.5, 0, -2.8), (0, -8.0, 0.6), 35))
    add(T("pero necesitan"), V_((RC, 0, -2.8), (0, -8.0, 0.6), 35))
    add(T("así que unas máquinas") + 0.3, V_((RC, 0, -3.0), (0, -12.5, 1.0), 35))
    add(T("esas bacterias"), V_((RC, 0, -3.0), (0, -11.0, 0.9), 35))
    add(T("forman grumos", fin=True) + 0.2, V_((RC, 0, -3.0), (0, -10.0, 0.8), 35))
    add(T("en otro depósito") + 0.5, V_((SCX, 0, -3.0), (0, -12.5, 1.2), 35))
    add(T("y arriba queda") + 0.5, V_((SCX, 0, -2.8), (0, -12.5, 1.2), 35))
    add(T("esa agua vuelve") + 0.2, V_((46.5, 0, -1.2), (0, -11, 1.4), 35))
    add(T("y el lodo") + 0.3, V_((41.5, 0, -3.0), (0, -12, 1.0), 35))
    add(T("lo metes") + 0.3, V_((XG[0], 0, 6.2), (0, -27, 2.0), 35))
    add(T("otras bacterias") + 0.5, V_((XG[0], 0, 6.2), (0, -24, 1.5), 35))
    add(T("ese gas"), V_((XM - 1, 0, 3.4), (0, -13, 1.5), 35))
    add(T("y da electricidad") + 0.3, V_((XM - 2, 0, 3.4), (0, -16, 1.8), 35))
    add(T("sígueme"), V_((XG[0] - 4, 0, 3.0), (0, -38, 5.0), 35))
    add(DUR + 2, V_((XG[0] - 5, 0, 3.0), (0, -42, 6.0), 35))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"wc": Pj(TB + Vector((0, 0, 0.6))), "c128": Pj((TB.x + 1.15, 2.5, 0.85)), "cbig": Pj((-46, 12.2, 11.7)),
            "reja": Pj((XR, 0.2, 0.9)), "pump": Pj((XR + 2.5, -0.4, -0.7)), "sand": Pj((-3.0, 0.0, CANAL[2] + 0.4)),
            "grasa": Pj((6.0, 0.0, CANAL[3] + 0.3)), "aire": Pj((4.0, 0.0, CANAL[2] + 0.4)),
            "prim": Pj(((PRIM[0] + PRIM[1]) / 2, 0, PRIM[2] + 0.4)), "diss": Pj((15.5, 0, -2.0)),
            "reac": Pj(((REAC[0] + REAC[1]) / 2, 0, REAC[3] + 0.3)), "bact": Pj((26.5, 0, -1.2)), "difu": Pj((26.5, 0, REAC[2] + 0.3)),
            "sec": Pj(((SEC[0] + SEC[1]) / 2, 0, SEC[3] + 0.3)), "sec_bot": Pj(((SEC[0] + SEC[1]) / 2, 0, SEC[2] + 0.3)),
            "rio": Pj((50, 0, 0.3)), "egg": Pj((XG[0], XG[1] - RG, ZG + 2.0)), "egg_top": Pj((XG[0], XG[1], ZG + RG * KZ + 1.5)),
            "motor": Pj((XM, XG[1] - 1.5, 3.6)), "lamp": Pj((LAMPS[-1] + 0.7, -1.0, 5.0)), "lodo": Pj((43, YP, 1.4))}

CAMK = CAM()

if __name__ == "__main__":
    run("depuradora", build, pose, anchors)
