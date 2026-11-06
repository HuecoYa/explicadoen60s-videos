# «¿Y si construyes un tanque de tormentas?»: ciudad en corte bajo una tormenta nocturna. La lluvia cae por la rejilla al
# colector, donde se junta con el agua sucia de las casas; el colector se llena, el agua sube por la rejilla y la calle se
# inunda. Tubo más grande = levantar la calle. Se excava un depósito bajo tierra, muros de hormigón, la tierra empuja,
# pilares y techo, parque encima. La compuerta se abre y el tanque se llena, rejas que atrapan la basura, el récord de
# Madrid (cinco campos, seis plantas, 400.000 m³), el agua se pudre, las bombas la mandan a la depuradora y el río queda limpio.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("tormentas")
SKY = (0.11, 0.13, 0.17); SOIL = (0.46, 0.34, 0.24); SOIL2 = (0.38, 0.28, 0.2); ASPH = (0.22, 0.23, 0.26); WALK = (0.6, 0.6, 0.62)
CONC = (0.72, 0.72, 0.74); CONC2 = (0.85, 0.85, 0.86); RAIN = (0.75, 0.85, 1.0); WATER = (0.25, 0.55, 0.95); DIRTY = (0.55, 0.42, 0.22)
GRASS = (0.35, 0.62, 0.3); TRUNK = (0.45, 0.32, 0.2); LEAF = (0.3, 0.55, 0.28); STEEL = (0.5, 0.52, 0.56); RED = (0.95, 0.25, 0.2)
ROT = (0.4, 0.42, 0.18); CLEAN = (0.4, 0.75, 1.0)
LEJOS = (0, 0, -300)
# geometría (x a lo largo del corte, z arriba, y hacia el fondo)
PZ0, PZ1 = -2.8, -1.6                  # interior del colector
GX = -8.0                              # rejilla
HX = -13.0                             # bajante de la casa
TX0, TX1, TZ0, TZ1 = -1.0, 11.0, -10.0, -4.0   # interior del tanque
IX0, IX1 = 0.0, 1.0                    # entrada (compuerta)
DX = 14.0                              # subida a la depuradora
RX0, RX1 = 20.5, 27.0                  # río

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def unir(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); return objs[0]

def bx(x0, x1, y0, y1, z0, z1, col, unique=False):
    return box((x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), col, unique=unique)

def hsh(k, s=1.0): return (math.sin(k * 12.9898 + s * 78.233) * 43758.5453) % 1.0

def build():
    sc, cam = scene_setup(world=SKY, shadow=0.35)
    S = {"cam": cam}
    # ---- terreno con los huecos ya recortados (booleana aplicada) ----
    for x0, x1 in ((-40, HX - 0.25), (HX + 0.25, GX - 0.5), (GX + 0.5, DX - 0.4), (DX + 0.4, RX0), (RX1, 40)):
        bx(x0, x1, 0, 16, -1.4, -0.3, SOIL)
    bx(DX + 0.4, 30, 0, 16, -3.0, -1.4, SOIL); bx(-30, DX + 0.4, 1.6, 16, -3.0, -1.4, SOIL)
    bx(-30, IX0, 0, 16, -3.4, -3.0, SOIL); bx(IX1, 30, 0, 16, -3.4, -3.0, SOIL)
    bx(-30, TX0 - 0.5, 0, 16, TZ0 - 0.5, -3.4, SOIL); bx(TX1 + 0.5, 30, 0, 16, TZ0 - 0.5, -3.4, SOIL)
    bx(TX0 - 0.5, TX1 + 0.5, 10.6, 16, TZ0 - 0.5, -3.4, SOIL); bx(-40, 40, 0, 16, -40, TZ0 - 0.5, SOIL)
    bx(RX0, RX1, 0, 16, -1.4, -1.25, SOIL)
    # piedrecitas en la cara del corte
    rng = random.Random(3)
    for k in range(70):
        x, z = rng.uniform(-28, 28), rng.uniform(-13.5, -0.6)
        if -3.1 < z < -1.3 or (TX0 - 0.6 < x < TX1 + 0.6 and z > TZ0 - 0.6) or RX0 - 0.3 < x < RX1 + 0.3 and z > -1.5: continue
        sph(rng.uniform(0.07, 0.18), (x, -0.02, z), SOIL2, scale=(1.4, 0.3, 1))
    # ---- calle (losas de asfalto que se levantan), acera, rejilla ----
    S["losas"] = []
    for k, (x0, x1) in enumerate(((-30, -22), (-22, -16), (-16, -11), (-11, -8.5), (-7.5, -4), (-4, -1.6))):
        o = bx(x0, x1, 0, 6, -0.3, 0, ASPH, unique=True); S["losas"].append((o, Vector(o.location), k))
    bx(-30, -1.6, 6, 8, -0.3, 0.15, WALK); bx(-30, -1.6, 8, 16, -0.3, 0.1, (0.3, 0.32, 0.36))
    for k in range(6): box((2.4, 0.15, 0.02), ((-26 + 4.5 * k), 3.0, 0.005), (0.9, 0.9, 0.85))
    for k in range(5): bx(GX - 0.5, GX + 0.5, 0.15 + 0.22 * k, 0.27 + 0.22 * k, -0.12, 0.0, (0.15, 0.15, 0.17))
    bx(GX - 0.55, GX + 0.55, 0.0, 1.25, -0.16, -0.12, (0.15, 0.15, 0.17))
    # zona del parque (asfalto al principio, césped después) y depuradora
    S["plaza"] = bx(-1.6, 12.5, 0, 16, -0.3, 0, ASPH, unique=True)
    S["cesped"] = bx(-1.6, 12.5, 0, 16, -0.3, 0.06, GRASS, unique=True)
    bx(12.5, RX0, 0, 16, -0.3, 0, (0.55, 0.55, 0.58)); bx(RX1, 30, 0, 16, -0.3, 0, GRASS)
    # casas
    for x0, x1, h, col in ((-17.5, -11.5, 5.0, (0.85, 0.78, 0.66)), (-24, -18, 7.0, (0.75, 0.7, 0.75)), (-29.5, -24.5, 4.0, (0.7, 0.78, 0.72))):
        bx(x0, x1, 9, 15, 0, h, col)
        for i in range(int((x1 - x0) // 1.5)):
            for j in range(int(h // 1.5)):
                bx(x0 + 0.5 + 1.5 * i, x0 + 1.2 + 1.5 * i, 8.95, 9.0, 0.8 + 1.5 * j, 1.6 + 1.5 * j, (1.0, 0.85, 0.45) if (i + j) % 3 else (0.25, 0.3, 0.4))
    # bajante de la casa al colector
    o = bar_obj((0.9, 0.9, 0.92), 0.18); bar_set(o, (HX, 0.4, -0.1), (HX, 0.4, -1.4))
    o = bar_obj((0.9, 0.9, 0.92), 0.18); bar_set(o, (HX, 0.4, -0.1), (HX, 9.0, -0.1))
    # farolas
    for x in (-20, -10, 5, 10):
        cyl(0.08, 4, (x, 6.6, 2), (0.3, 0.3, 0.32)); sph(0.25, (x, 6.6, 4.1), (1.0, 0.9, 0.6))
    # ---- colector ----
    for x0, x1 in ((-30, IX0), (IX1, DX + 0.4)): bx(x0, x1, 0, 1.6, -3.0, PZ0, CONC)
    for x0, x1 in ((-40, HX - 0.25), (HX + 0.25, GX - 0.5), (GX + 0.5, DX - 0.4)): bx(x0, x1, 0, 1.6, PZ1, -1.4, CONC)
    bx(-30, DX + 0.4, 1.4, 1.6, PZ0, PZ1, CONC2); bx(DX + 0.2, DX + 0.4, 0, 1.6, PZ0, PZ1, CONC)
    for x in (GX, DX):
        bx(x - 0.5, x - 0.4, 0, 1.2, -1.4, -0.3, CONC); bx(x + 0.4, x + 0.5, 0, 1.2, -1.4, -0.3, CONC); bx(x - 0.5, x + 0.5, 1.1, 1.2, -1.4, -0.3, CONC2)
    S["agua_tubo"] = bx(-30, DX + 0.2, 0.02, 1.4, 0, 1, WATER, unique=True); alpha(S["agua_tubo"], 0.75)
    S["agua_pozo"] = bx(GX - 0.4, GX + 0.4, 0.02, 1.1, 0, 1, WATER, unique=True); alpha(S["agua_pozo"], 0.75)
    S["charco"] = bx(-30, -1.6, -0.2, 6, 0, 1, WATER, unique=True); alpha(S["charco"], 0.55)
    S["grande"] = bx(-30, DX, -0.05, 1.7, -4.4, -0.3, RED, unique=True); alpha(S["grande"], 0.3)
    # compuerta y rejas
    S["comp"] = bx(IX0, IX1, 0, 1.4, -3.0, PZ0, (0.85, 0.55, 0.15), unique=True)
    S["rejas"] = rj = empty(LEJOS)
    for k in range(6):
        box((0.06, 0.06, 1.15), (0, 0.12 + 0.22 * k, 0), STEEL, parent=rj)
    box((0.08, 1.4, 0.08), (0, 0.7, 0.55), STEEL, parent=rj)
    S["tapon"] = bx(IX0, IX1, 0, 1.2, -3.4, -3.0, SOIL, unique=True)
    # ---- tanque ----
    S["excav"] = bx(TX0 - 0.5, TX1 + 0.5, 0.0, 10.6, TZ0 - 0.5, 0, SOIL, unique=True)
    S["muros"] = []
    for (x0, x1, y0, y1) in ((TX0 - 0.5, TX0, 0, 10.6), (TX1, TX1 + 0.5, 0, 10.6), (TX0, TX1, 10.1, 10.6)):
        o = bx(x0, x1, y0, y1, TZ0, TZ1, CONC, unique=True); S["muros"].append((o, Vector(o.location)))
    S["losa"] = bx(TX0 - 0.5, TX1 + 0.5, 0, 10.6, TZ0 - 0.5, TZ0, CONC, unique=True)
    S["techo"] = [bx(TX0 - 0.5, IX0, 0, 10.6, TZ1, -3.4, CONC, unique=True), bx(IX1, TX1 + 0.5, 0, 10.6, TZ1, -3.4, CONC, unique=True)]
    for o in S["techo"]: o["w"] = o.scale.x; o["xa"] = o.location.x - o.scale.x / 2
    S["pilares"] = []
    for i in range(7):
        for j, y in enumerate((2.0, 5.0, 8.0)):
            x = TX0 + 0.9 + i * 1.7
            if abs(x - 0.5) < 0.7 and j == 0: continue
            o = box((0.45, 0.45, 1), (x, y, TZ0), CONC2, unique=True); S["pilares"].append((o, i, j))
    S["flechas"] = []
    for k in range(6):
        bpy.ops.mesh.primitive_cone_add(radius1=0.45, radius2=0, depth=1.1, location=LEJOS, vertices=16); f = bpy.context.object
        setup(f, RED); S["flechas"].append(f)
    S["agua_t"] = bx(TX0, TX1, 0.02, 10.1, 0, 1, WATER, unique=True); alpha(S["agua_t"], 0.8)
    S["burbujas"] = [sph(0.12, LEJOS, (0.55, 0.6, 0.25), seg=8) for _ in range(14)]
    # bombas y tubo de subida
    for x in (9.4, 10.3):
        cyl(0.3, 0.6, (x, 0.9, TZ0 + 0.3), (0.25, 0.45, 0.75)); cyl(0.2, 0.3, (x, 0.9, TZ0 + 0.75), (0.6, 0.62, 0.66))
    o = bar_obj((0.9, 0.9, 0.92), 0.14); bar_set(o, (10.3, 0.9, TZ0 + 0.9), (10.3, 0.9, -3.0))
    o = bar_obj((0.9, 0.9, 0.92), 0.14); bar_set(o, (9.4, 0.9, TZ0 + 0.9), (9.4, 0.9, TZ0 + 1.2))
    o = bar_obj((0.9, 0.9, 0.92), 0.14); bar_set(o, (9.4, 0.9, TZ0 + 1.2), (10.3, 0.9, TZ0 + 1.2))
    # edificio fantasma de 6 plantas (comparación de profundidad)
    S["plantas"] = []
    hz = (TZ1 - TZ0) / 6
    for k in range(6):
        e = empty(LEJOS)
        box((1.6, 1.0, hz - 0.08), (0, 0, 0), (0.92, 0.9, 0.85), parent=e)
        for w in range(2): box((0.45, 0.05, hz * 0.45), (-0.4 + 0.8 * w, -0.52, 0.02), (0.35, 0.55, 0.85), parent=e)
        S["plantas"].append((e, Vector((TX1 + 1.9, -0.7, TZ0 + hz * (k + 0.5)))))
    # parque: árboles, campos
    S["arboles"] = []
    for k, (x, y) in enumerate(((0.5, 4), (3.2, 9), (6.0, 4.5), (8.6, 10), (10.6, 5), (2.0, 13), (7.5, 14))):
        e = empty((x, y, 0))
        cyl(0.14, 1.4, (0, 0, 0.7), TRUNK, parent=e); sph(0.9, (0, 0, 1.8), LEAF, parent=e, scale=(1, 1, 1.15))
        S["arboles"].append((e, k))
    S["campos"] = []
    for k in range(5):
        e = empty(LEJOS)
        box((2.2, 3.3, 0.04), (0, 0, 0), (0.3, 0.68, 0.32), parent=e)
        for sx in (-1, 1): box((2.0, 0.05, 0.02), (0, sx * 1.55, 0.03), (1, 1, 1), parent=e); box((0.05, 3.1, 0.02), (sx * 1.0, 0, 0.03), (1, 1, 1), parent=e)
        box((2.0, 0.05, 0.02), (0, 0, 0.03), (1, 1, 1), parent=e); torus(0.35, 0.025, (0, 0, 0.03), (1, 1, 1), parent=e)
        S["campos"].append((e, Vector((TX0 + 1.2 + 2.4 * k, 2.2, 0.08))))
    # depuradora y río
    for x, y in ((16.0, 3.5), (18.6, 3.5), (16.0, 8.0)):
        cyl(1.1, 0.9, (x, y, 0.45), (0.8, 0.8, 0.82), v=40); cyl(0.95, 0.05, (x, y, 0.88), (0.35, 0.6, 0.55), v=40)
    bx(17.8, 20.0, 7.0, 10.0, 0, 2.2, (0.88, 0.86, 0.8))
    o = bar_obj((0.9, 0.9, 0.92), 0.15); bar_set(o, (DX, 0.6, -0.3), (DX, 0.6, 0.3))
    o = bar_obj((0.9, 0.9, 0.92), 0.15); bar_set(o, (DX, 0.6, 0.3), (15.0, 2.6, 0.3))
    o = bar_obj((0.9, 0.9, 0.92), 0.15); bar_set(o, (19.5, 1.0, 0.3), (RX0 + 0.3, 1.0, 0.3))
    S["rio"] = bx(RX0, RX1, 0.02, 16, -1.2, -0.25, WATER, unique=True); alpha(S["rio"], 0.85)
    # partículas
    S["lluvia"] = [bar_obj(RAIN, 0.025) for _ in range(70)]
    S["gotas_t"] = [sph(0.09, LEJOS, WATER, seg=8, unique=True) for _ in range(34)]
    S["gotas_c"] = [sph(0.1, LEJOS, DIRTY, seg=8) for _ in range(8)]
    S["caida"] = [sph(0.12, LEJOS, WATER, seg=8, unique=True) for _ in range(12)]
    S["bombeo"] = [sph(0.11, LEJOS, DIRTY, seg=8, unique=True) for _ in range(16)]
    S["limpia"] = [sph(0.11, LEJOS, CLEAN, seg=8) for _ in range(6)]
    S["basura"] = []
    for k, col in enumerate(((0.9, 0.25, 0.25), (0.95, 0.85, 0.3), (0.3, 0.75, 0.4), (0.95, 0.95, 0.95), (0.4, 0.5, 0.95), (0.85, 0.5, 0.2))):
        o = box((0.32, 0.22, 0.14), LEJOS, col) if k % 2 else cyl(0.09, 0.4, LEJOS, col, rot=(0, math.pi / 2, 0))
        S["basura"].append(o)
    dyn = [cam, [o for o, _, _ in S["losas"]], S["plaza"], S["cesped"], S["agua_tubo"], S["agua_pozo"], S["charco"], S["grande"],
           S["comp"], rj, S["tapon"], S["excav"], [o for o, _ in S["muros"]], S["losa"], S["techo"], [o for o, _, _ in S["pilares"]],
           S["flechas"], S["agua_t"], S["burbujas"], [e for e, _ in S["plantas"]], [e for e, _ in S["arboles"]], [e for e, _ in S["campos"]],
           S["rio"], S["lluvia"], S["gotas_t"], S["gotas_c"], S["caida"], S["bombeo"], S["limpia"], S["basura"]]
    join_static(dyn)
    return sc, S

def at(pts, s):
    pts = [Vector(p) for p in pts]; L = [(b - a).length for a, b in zip(pts, pts[1:])]; d = max(0.0, min(1.0, s)) * sum(L)
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l: return a.lerp(b, d / max(l, 1e-6))
        d -= l
    return pts[-1]

def pose(t, S):
    t_rej, t_sucia, t_torm, t_sube, t_inund = T("cae por"), T("la lluvia y"), T("y en una"), T("así que el agua"), T("y la calle")
    t_tubos, t_levant, t_dep, t_exc, t_muros = T("podrías"), T("pero tendrías"), T("así que construyes"), T("excavas"), T("y levantas")
    t_emp, t_pil, t_parq, t_ahora, t_comp = T("pero la tierra"), T("así que llenas"), T("encima"), T("ahora"), T("una compuerta")
    t_basu, t_rejas, t_cur, t_mad, t_campos = T("pero esa agua"), T("así que a la"), T("y aquí viene"), T("el más grande"), T("ocupa")
    t_plant, t_cab, t_pudre, t_pasa, t_bomb = T("es tan"), T("y le caben"), T("pero si el"), T("cuando pasa"), T("unas bombas")
    t_14, t_rio, t_sig = T("el de madrid"), T("así el"), T("sígueme")
    # ---- lluvia ----
    llueve = (t < t_tubos) or (t_ahora - 0.3 < t < t_pasa)
    fuerte = 1.0 if t < t_tubos else 0.7
    cx = S["cam"].location.x
    for k, o in enumerate(S["lluvia"]):
        if not llueve or k > 70 * fuerte: o.hide_render = True; continue
        o.hide_render = False
        x = cx + (hsh(k) - 0.5) * 16; y = hsh(k, 2) * 6
        if k < 14: x = GX + (hsh(k, 3) - 0.5) * 2.5; y = hsh(k, 2) * 1.2
        z = 9 - ((t * 16 + hsh(k, 4) * 9) % 9)
        bar_set(o, (x, y, z), (x, y, z + 0.6))
    # ---- nivel del colector ----
    hp = keyed(t, [(0, 0.3), (t_sucia, 0.35), (t_torm, 0.45), (T("cae más") + 0.8, 1.0), (t_tubos + 1.5, 1.0), (t_dep, 0.3),
                   (t_comp, 0.3), (t_comp + 0.6, 1.0), (T("y se va") + 0.5, 0.55), (t_pasa, 0.55), (t_pasa + 1.0, 0.3), (DUR + 2, 0.3)])
    h = hp * (PZ1 - PZ0); S["agua_tubo"].scale.z = h; S["agua_tubo"].location.z = PZ0 + h / 2
    sube = keyed(t, [(0, 0), (t_sube, 0), (t_inund, 1.0), (t_tubos + 1.0, 1.0), (t_dep - 0.5, 0)])
    hz = (0.0 - PZ1) * sube; S["agua_pozo"].hide_render = hz < 0.02
    S["agua_pozo"].scale.z = max(hz, 0.01); S["agua_pozo"].location.z = PZ1 + hz / 2
    ch = 0.3 * keyed(t, [(0, 0), (t_inund - 0.4, 0), (t_inund + 0.9, 1.0), (t_tubos + 1.0, 1.0), (t_dep - 0.5, 0)])
    S["charco"].hide_render = ch < 0.01; S["charco"].scale.z = max(ch, 0.01); S["charco"].location.z = ch / 2
    # ---- tubo más grande / levantar la calle ----
    g = win01(t, t_tubos + 0.2, t_dep - 0.2, 0.5, 0.4)
    S["grande"].hide_render = g < 0.02; alpha(S["grande"], 0.35 * g)
    lv = win01(t, t_levant, t_dep + 0.2, 0.4, 0.5)
    for o, p, k in S["losas"]:
        u = lv * (0.6 + 0.4 * math.sin(k * 1.7))
        o.location = p + Vector((0, 0, 1.6 * u * (1 + 0.15 * math.sin(4 * t + k)))); o.rotation_euler = (0.25 * u * math.sin(k * 2.3), 0.2 * u * math.cos(k), 0)
    # ---- tanque: excavación, muros, losa, pilares, techo ----
    zc = keyed(t, [(0, -3.4), (t_exc - 0.2, -3.4), (t_muros + 0.3, TZ0 - 0.5)])
    ex = S["excav"]; hgt = zc - (TZ0 - 0.5); ex.hide_render = hgt < 0.05
    ex.scale.z = max(hgt, 0.01); ex.location.z = (TZ0 - 0.5) + hgt / 2
    m = seg(t, t_muros, t_emp - 0.2)
    for o, p in S["muros"]:
        o.hide_render = m < 0.02; hh = (TZ1 - TZ0) * max(m, 0.01); o.scale.z = hh; o.location.z = TZ0 + hh / 2
    S["losa"].hide_render = t < t_muros - 0.2
    # la tierra empuja: flechas y muros que se curvan un poco
    pe = win01(t, t_emp, t_pil + 1.6, 0.3, 0.5)
    for k, f in enumerate(S["flechas"]):
        if pe < 0.02: f.hide_render = True; continue
        f.hide_render = False; side = -1 if k < 3 else 1; z = TZ0 + 1.2 + 2.0 * (k % 3)
        osc = 0.25 * math.sin(6 * t + k)
        x = (TX0 - 1.5 - osc) if side < 0 else (TX1 + 1.5 + osc)
        f.location = (x, -0.3, z); f.rotation_euler = (0, side * math.pi / 2 * -1 if side > 0 else math.pi / 2, 0)
        f.rotation_euler = (0, -math.pi / 2 if side < 0 else math.pi / 2, 0)
        f.scale = (pe,) * 3
    pil = seg(t, t_pil + 0.6, T("que sujetan") + 0.6)
    for o, i, j in S["pilares"]:
        u = seg(t, t_pil + 0.5 + 0.12 * i + 0.05 * j, t_pil + 1.1 + 0.12 * i + 0.05 * j)
        o.hide_render = u < 0.02; hh = (TZ1 - TZ0) * max(u, 0.01); o.scale.z = hh; o.location.z = TZ0 + hh / 2
    tc = seg(t, T("el techo") - 0.4, T("el techo") + 0.6)
    for o in S["techo"]:
        o.hide_render = tc < 0.02; w = o["w"] * max(tc, 0.01); o.scale.x = w; o.location.x = o["xa"] + w / 2
    S["tapon"].hide_render = t > t_ahora
    # ---- parque ----
    pq = seg(t, t_parq, t_parq + 0.8)
    S["cesped"].hide_render = pq < 0.02; S["cesped"].scale.z = 0.36 * max(pq, 0.01); S["cesped"].location.z = -0.3 + 0.36 * max(pq, 0.01) / 2
    S["plaza"].hide_render = pq > 0.98
    for e, k in S["arboles"]:
        u = seg(t, t_parq + 0.3 + 0.15 * k, t_parq + 0.9 + 0.15 * k); e.hide_render = u < 0.02
        e.scale = (max(u, 0.01),) * 3
        for c in e.children: c.hide_render = u < 0.02
    # ---- compuerta, llenado ----
    op = seg(t, t_comp + 0.2, t_comp + 1.0) * (1 - seg(t, t_pasa, t_pasa + 1.0))
    S["comp"].location.x = (IX0 + IX1) / 2 + 1.05 * op
    S["comp"].scale.z = 0.2; S["comp"].location.z = -2.9
    lvl = keyed(t, [(0, 0), (t_comp + 0.8, 0), (t_basu, 0.18), (t_cab, 0.3), (T("cúbicos", fin=True), 0.95), (t_bomb + 0.3, 0.95),
                    (T("catorce") + 2.5, 0.05), (DUR + 2, 0.05)])
    ht = (TZ1 - TZ0) * lvl; S["agua_t"].hide_render = ht < 0.03
    S["agua_t"].scale.z = max(ht, 0.01); S["agua_t"].location.z = TZ0 + max(ht, 0.01) / 2
    rot = seg(t, t_pudre, T("se pudre", fin=True) + 0.3) * (1 - seg(t, t_bomb + 0.5, t_14 + 1.5))
    set_color(S["agua_t"], tuple(mix(a, b, rot) for a, b in zip(WATER, ROT)))
    for k, b in enumerate(S["burbujas"]):
        if rot < 0.2 or ht < 0.5: b.hide_render = True; continue
        b.hide_render = False; u = (t * 0.5 + hsh(k)) % 1.0
        b.location = (TX0 + 0.5 + hsh(k, 5) * (TX1 - TX0 - 1), 0.4 + hsh(k, 6) * 0.3, TZ0 + 0.2 + u * (ht - 0.3)); b.scale = (0.6 + 0.6 * u,) * 3
    # ---- rejas y basura ----
    rj = S["rejas"]; ru = seg(t, t_rejas + 0.4, t_rejas + 1.1)
    rj.location = (IX0 - 0.15, 0, (PZ0 + PZ1) / 2) if ru > 0 else LEJOS; rj.scale = (1, 1, max(ru, 0.01))
    for c in rj.children: c.hide_render = ru <= 0
    for k, o in enumerate(S["basura"]):
        a = t_basu - 0.3 + 0.35 * k
        if t < a or t > t_14: o.hide_render = True; continue
        o.hide_render = False
        x = -9 + 4.0 * (t - a)
        stop = IX0 - 0.35 - 0.12 * (k % 3) if t > t_rejas + 0.6 else None
        if stop is not None and x > stop and (a + (stop + 9) / 4.0) > t_rejas + 0.5:
            x = stop; z = PZ0 + 0.2 + 0.18 * (k % 4)
        elif x > IX0 + 0.1:
            fall = (x - IX0 - 0.1) / 4.0; z = PZ0 - 9 * fall * fall * 4; x = IX0 + 0.4
            if z < TZ0 + ht: z = TZ0 + ht + 0.05
        else: z = PZ0 + 0.25 + 0.1 * math.sin(3 * t + k)
        o.location = (x, 0.25 + 0.18 * (k % 5), z); o.rotation_euler = (0, 0.3 * math.sin(t + k), t * (1 + k % 3))
    # ---- agua que corre por el colector ----
    for k, d in enumerate(S["gotas_t"]):
        if t > t_dep - 0.3 and t < t_ahora - 0.3: d.hide_render = True; continue
        d.hide_render = False
        dirty = k % 3 == 0 or t_pudre < t
        set_color(d, DIRTY if dirty else WATER)
        if k < 8 and (t < t_tubos or t_ahora < t < t_pasa):          # bajando por la rejilla
            u = (t * 1.3 + k / 8) % 1.0
            d.location = (GX + 0.25 * math.sin(k * 2), 0.3 + 0.1 * k, mix(0.0, PZ0 + 0.3, u)); set_color(d, WATER); continue
        speed = 2.2 if op < 0.5 else 2.6
        x = -16 + ((t * speed + hsh(k) * 30) % 30)
        if op > 0.5 and x > IX0 + 0.5: x = IX0 + 0.5 - ((x - IX0 - 0.5) % 0.5)
        zt = PZ0 + 0.1 + hsh(k, 7) * max(0.05, h - 0.2)
        d.location = (x, 0.2 + hsh(k, 8) * 1.1, zt)
    for k, d in enumerate(S["gotas_c"]):
        if not (t_sucia - 0.5 < t < t_dep - 0.3 or t_ahora < t < t_pasa): d.hide_render = True; continue
        d.hide_render = False; u = (t * 0.9 + k / 8) % 1.0
        d.location = (HX, 0.4, mix(-0.3, PZ0 + 0.3, u))
    for k, d in enumerate(S["caida"]):
        if op < 0.3 or t > t_pasa: d.hide_render = True; continue
        d.hide_render = False; u = (t * 1.2 + k / 12) % 1.0
        zb = TZ0 + ht
        d.location = (IX0 + 0.2 + 0.6 * hsh(k), 0.15 + 1.0 * hsh(k, 2), mix(PZ0, zb, u * u))
        set_color(d, ROT if t > t_pudre else WATER)
    # ---- bombeo a la depuradora y río ----
    bon = t_bomb - 0.2 < t < T("catorce") + 2.5
    path = [(10.3, 0.9, TZ0 + 0.9), (10.3, 0.9, -2.5), (DX, 0.6, -2.5), (DX, 0.6, 0.3), (15.0, 2.6, 0.3)]
    for k, d in enumerate(S["bombeo"]):
        if not bon: d.hide_render = True; continue
        d.hide_render = False; d.location = at(path, (t * 0.35 + k / 16) % 1.0)
        set_color(d, tuple(mix(a, b, rot) for a, b in zip(DIRTY, ROT)))
    path2 = [(19.5, 1.0, 0.3), (RX0 + 0.3, 1.0, 0.3), (RX0 + 1.2, 1.0, -0.4)]
    for k, d in enumerate(S["limpia"]):
        if not (t_bomb + 1 < t): d.hide_render = True; continue
        d.hide_render = False; d.location = at(path2, (t * 0.6 + k / 6) % 1.0)
    # ---- récord de Madrid ----
    for k, (e, p) in enumerate(S["campos"]):
        u = seg(t, t_campos + 0.3 + 0.32 * k, t_campos + 0.6 + 0.32 * k) * (1 - seg(t, t_pudre, t_pudre + 0.5))
        e.location = p if u > 0.01 else LEJOS; e.scale = (max(u, 0.01),) * 3
    for k, (e, p) in enumerate(S["plantas"]):
        u = seg(t, t_plant + 0.25 + 0.3 * k, t_plant + 0.55 + 0.3 * k) * (1 - seg(t, t_cab + 0.6, t_cab + 1.1))
        e.location = p + Vector((0, 0, 0.6 * (1 - u))) if u > 0.01 else LEJOS; e.scale = (max(u, 0.01),) * 3
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.08))

def V_(at, off, lens=35):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    add(0.0, V_((GX, 0.6, -0.6), (-1.0, -4.5, 2.6)))
    add(2.2, V_((GX, 0.6, -1.2), (-1.5, -6.5, 2.2)))
    add(T("cae por") + 0.8, V_((GX + 0.5, 0.6, -2.0), (-1.5, -8.5, 1.2)))
    add(T("la lluvia y"), V_((-10.5, 0.6, -0.8), (-2.0, -16, 2.5)))
    add(T("y en una") + 0.5, V_((-9.0, 0.6, -1.8), (-1.5, -11, 1.5)))
    add(T("así que el agua"), V_((-9.0, 0.6, -0.8), (-2.0, -12, 2.5)))
    add(T("y la calle") + 0.5, V_((-9.0, 1.0, 0.0), (-2.0, -13, 4.0)))
    add(T("podrías") + 0.5, V_((-7.0, 0.6, -0.8), (-2.0, -26, 4.0)))
    add(T("pero tendrías") + 1.0, V_((-7.0, 0.6, 0.0), (-3.0, -28, 6.0)))
    add(T("así que construyes") + 1.0, V_((5.0, 0.6, -5.0), (-2.0, -33, 3.0)))
    add(T("excavas") + 0.5, V_((5.0, 0.6, -6.5), (-2.0, -27, 2.0)))
    add(T("pero la tierra") + 0.5, V_((5.0, 0.6, -6.8), (-1.5, -28, 1.5)))
    add(T("así que llenas") + 1.0, V_((5.0, 0.6, -6.5), (-4.0, -24, 3.0)))
    add(T("encima") + 0.2, V_((5.0, 3.0, -2.5), (-3.0, -24, 9.0)))
    add(T("ahora") + 0.2, V_((4.0, 3.0, -2.0), (-3.0, -22, 7.0)))
    add(T("una compuerta") + 0.5, V_((1.5, 0.6, -4.2), (-2.0, -15, 2.5)))
    add(T("pero esa agua") + 0.3, V_((0.5, 0.6, -3.6), (-4.0, -12.0, 2.5)))
    add(T("así que a la") + 1.2, V_((0.0, 0.6, -3.0), (-4.0, -10.0, 2.0)))
    add(T("y aquí viene"), V_((3.0, 0.6, -4.0), (-2.0, -18, 3.0)))
    add(T("ocupa"), V_((5.0, 2.0, -3.0), (-2.0, -30, 9.0)))
    add(T("es tan") + 0.3, V_((6.0, 0.6, -6.0), (-2.0, -30, 3.0)))
    add(T("y le caben") + 0.5, V_((5.0, 0.6, -6.0), (-2.0, -26, 2.0)))
    add(T("pero si el") + 0.4, V_((5.0, 0.6, -7.0), (-2.0, -20, 1.5)))
    add(T("unas bombas") + 0.5, V_((9.0, 0.6, -6.5), (-2.5, -18, 2.0)))
    add(T("el de madrid") + 0.5, V_((8.0, 0.6, -4.5), (-2.0, -27, 2.5)))
    add(T("así el"), V_((17.5, 2.0, -0.5), (-3.0, -22, 5.0)))
    add(T("sígueme"), V_((10.0, 2.0, -3.5), (-3.0, -40, 7.0)))
    add(DUR + 2, V_((10.0, 2.0, -3.5), (-3.0, -43, 8.0)))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"rejilla": Pj((GX, 0.6, 0.1)), "colector": Pj((-11.0, 0.0, PZ0 - 0.2)), "tubo": Pj((-6.0, 0.0, -4.4)),
            "tanque": Pj((5.0, 0.0, TZ0 + 1.0)), "muro": Pj((TX0 - 0.25, 0.0, TZ1 - 0.5)), "pilar": Pj((TX0 + 0.9 + 1.7 * 3, 2.0, TZ0 + 1.5)),
            "tierra": Pj((TX0 - 2.5, 0.0, TZ0 + 3.0)), "comp": Pj((IX1 + 0.6, 0.0, PZ0)), "rejas": Pj((IX0 - 0.15, 0.0, PZ1)),
            "bombas": Pj((9.8, 0.9, TZ0 + 0.8)), "rio": Pj(((RX0 + RX1) / 2, 0.0, -0.3)), "depu": Pj((17.0, 3.5, 1.2)),
            "plantas": Pj((TX1 + 1.9, -0.7, TZ1 + 0.3)), "campos": Pj((5.0, 2.2, 0.5))}

if __name__ == "__main__":
    run("tormentas", build, pose, anchors)
