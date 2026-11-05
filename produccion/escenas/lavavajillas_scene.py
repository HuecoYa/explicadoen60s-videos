# «Si tuvieras que inventar el lavavajillas…»: primer plano de un plato sucio recibiendo los chorros del brazo que gira;
# luego se construye pieza a pieza en corte (sin puerta): caja y 10 litros de agua, bomba y brazo con agujeros inclinados
# (flechas de chorro y de empuje), resistencia y termómetro hasta 65 °C, recirculación por el filtro, cal en la tubería,
# depósito de resina que la atrapa, sal que la limpia, abrillantador (gotas → capa fina) y secado por condensación.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Quaternion

T, DUR = cargar("lavavajillas")
BG = (0.07, 0.08, 0.11); STEEL = (0.7, 0.73, 0.78); STEEL2 = (0.5, 0.53, 0.58); DARK = (0.18, 0.19, 0.23); CAB = (0.86, 0.87, 0.88)
WATER = (0.3, 0.6, 0.95); JET = (0.6, 0.85, 1.0); PLATE = (0.97, 0.97, 0.95); DIRT = (0.5, 0.3, 0.12); GREASE = (0.95, 0.75, 0.2)
HOT = (1.0, 0.35, 0.08); RESIN = (0.95, 0.62, 0.2); CAL = (1.0, 1.0, 1.0); RINSE = (0.35, 0.9, 0.85); MOTOR = (0.25, 0.4, 0.75)
LEJOS = (0, 0, -900)
PZ = 29.0                        # centro del plato
HUB = Vector((0, 4, 9))          # eje del brazo
NOZ = (-20, -13, -6, 6, 13, 20)  # agujeros del brazo
TANK = Vector((-40, 0, 20))      # depósito de resina

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def poly(pts, u):
    """punto a lo largo de una polilínea (u 0→1 por longitud)"""
    P = [Vector(p) for p in pts]; L = [(b - a).length for a, b in zip(P, P[1:])]; s = u * sum(L)
    for a, b, l in zip(P, P[1:], L):
        if s <= l: return a.lerp(b, s / max(l, 1e-6))
        s -= l
    return P[-1]

def arrow(col):
    e = empty(LEJOS)
    cyl(0.45, 5.0, (0, 0, 2.5), col, parent=e, v=12)
    bpy.ops.mesh.primitive_cone_add(radius1=1.2, radius2=0, depth=2.4, location=(0, 0, 6.2), vertices=16); setup(bpy.context.object, col, parent=e)
    return e

def aim(o, p, d, s=1.0):
    o.location = p; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
    o.scale = (s, s, s)

def show(o, on, loc=None):
    o.hide_render = not on
    for c in o.children: show(c, on)

def grow(o, u, base=1.0):
    u = max(u, 0.001); o.scale = (base * u, base * u, base * u)

RNG = random.Random(7)
DIRT_P = [(-6, 4), (5, 6), (-2, -5), (7, -3), (-8, -2), (2, 1), (0, 8)]
GREASE_P = [(4, -7), (-5, 7), (8, 3), (-3, -1)]
CAL_P = [(-7, 5), (6, 7), (-4, -7), (8, -5), (1, -2), (-1, 4)]
DROP_P = [(RNG.uniform(-8, 8), RNG.uniform(-8, 8)) for _ in range(12)]
BALLS = []
while len(BALLS) < 34:
    x, y = RNG.uniform(-4.5, 4.5), RNG.uniform(-4.5, 4.5)
    if x * x + y * y < 20: BALLS.append((x, y, RNG.uniform(-10, 10)))
WALLD = [((-1) ** k, RNG.uniform(-22, 18), RNG.uniform(12, 58), RNG.uniform(0.5, 1.0)) for k in range(36)]
VAP = [(RNG.uniform(-8, 8), RNG.uniform(-8, 8), (-1) ** k, RNG.uniform(-20, 15), RNG.uniform(20, 56)) for k in range(26)]
PIPE = [(-58, 0, 38), (-40, 0, 38), (-40, 0, 5), (-28, 0, 5), (-16, -6, 2.5)]
LOOP = [(0, -4, 22), (0, -10, 4), (0, -10, -2), (0, 1, -9), (0, 4, -9), (0, 4, 8), (14, 4, 10), (12, -1, 27), (0, -4, 22)]

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    # cuba y mueble en corte (sin puerta)
    box((1.6, 59, 84), (-28.8, 0, 21.8), CAB); box((1.6, 59, 84), (28.8, 0, 21.8), CAB)
    box((59, 1.6, 84), (0, 29.3, 21.8), CAB); box((59, 59, 1.6), (0, 0, 63.6), CAB)
    box((0.3, 56, 62), (-27.9, 0, 31), STEEL); box((0.3, 56, 62), (27.9, 0, 31), STEEL); box((56, 0.3, 62), (0, 28.4, 31), STEEL2)
    box((56, 56, 1.6), (0, 0, -0.8), STEEL)
    box((59, 59, 1.6), (0, 0, -20.2), DARK); box((56, 0.6, 19), (0, 28.2, -10.5), DARK)
    for sx in (-1, 1): box((0.6, 56, 19), (sx * 27.9, 0, -10.5), DARK)
    # cestas y vajilla de fondo
    for z in (16, 44):
        for y in (-22, 22): box((52, 0.5, 0.5), (0, y, z), (0.55, 0.57, 0.6))
        for x in (-25, 25): box((0.5, 44, 0.5), (x, 0, z), (0.55, 0.57, 0.6))
        for x in range(-24, 25, 4): box((0.3, 44, 0.3), (x, 0, z - 0.4), (0.55, 0.57, 0.6))
    for y in (7, 14): cyl(11, 1.0, (0, y, PZ), PLATE, rot=(math.pi / 2, 0, 0))
    for x in (-15, -5, 5, 15):
        cyl(3.5, 9, (x, 6, 49.5), (0.75, 0.85, 0.95)); cyl(3.6, 0.6, (x, 6, 45.2), (0.6, 0.7, 0.85))
    # tubería de entrada (agua del grifo)
    for a, b in zip(PIPE[:-1], PIPE[1:-1]):
        o = bar_obj((0.55, 0.57, 0.6), 1.0); bar_set(o, a, b)
    box((3, 3, 4), (-58, 0, 38), (0.8, 0.3, 0.25))
    # plato principal
    S["plato"] = empty((0, 0, PZ)); p = S["plato"]
    S["loza"] = cyl(11, 1.2, (0, 0, 0), PLATE, parent=p, rot=(math.pi / 2, 0, 0), unique=True)
    torus(10.4, 0.5, (0, -0.5, 0), PLATE, parent=p, rot=(math.pi / 2, 0, 0))
    def spots(P, col, r, sy=0.3):
        return [sph(r, (x, -0.75, z), col, parent=p, scale=(1, sy, 1), seg=12, unique=True) for x, z in P]
    S["sucio"] = spots(DIRT_P, DIRT, 1.4); S["grasa"] = spots(GREASE_P, GREASE, 1.6)
    S["calp"] = spots(CAL_P, (0.92, 0.92, 0.88), 1.2, 0.15); S["marcas"] = spots(DROP_P, (0.88, 0.88, 0.84), 0.9, 0.12)
    S["gotas"] = spots(DROP_P, (0.55, 0.8, 1.0), 0.9, 0.7)
    S["capa"] = cyl(10.3, 0.2, (0, -0.8, 0), RINSE, parent=p, rot=(math.pi / 2, 0, 0), unique=True); alpha(S["capa"], 0.45)
    # agua del fondo
    S["agua"] = box((54, 54, 1), (0, 0, 0.5), WATER, unique=True); alpha(S["agua"], 0.8)
    S["entrada"] = bar_obj(JET, 0.9, unique=True)
    # bomba (debajo del suelo) + tubo hasta el brazo
    S["bomba"] = empty((0, 4, -9)); b = S["bomba"]
    cyl(4.5, 6, (0, 0, 0), MOTOR, parent=b, rot=(math.pi / 2, 0, 0)); cyl(3.5, 9, (8.5, 0, 0), (0.35, 0.36, 0.4), parent=b, rot=(0, math.pi / 2, 0))
    cyl(1.3, 17, (0, 0, 8.5), STEEL2, parent=b)
    S["filtro"] = empty((0, -10, 0)); f = S["filtro"]
    cyl(5, 6, (0, 0, 1.5), (0.45, 0.47, 0.5), parent=f)
    for k in range(10): cyl(5.05, 0.25, (0, 0, -1.0 + 0.55 * k), (0.75, 0.77, 0.8), parent=f)
    o = bar_obj(STEEL2, 1.3, parent=f); bar_set(o, (0, 0, -2), (0, 11, -9))
    # brazo aspersor
    S["brazo"] = empty(HUB); a = S["brazo"]
    box((46, 3, 1.6), (0, 0, 0), (0.62, 0.64, 0.68), parent=a); cyl(2.6, 2.4, (0, 0, 0), (0.5, 0.52, 0.56), parent=a)
    for x in NOZ: cyl(0.55, 0.4, (x, 0, 0.85), (0.15, 0.15, 0.18), parent=a)
    S["chorros"] = [bar_obj(JET, 0.42, unique=True) for _ in NOZ]
    S["gotitas"] = [sph(0.55, LEJOS, JET, seg=8) for _ in range(18)]
    S["fl_chorro"] = [arrow((0.3, 0.85, 1.0)) for _ in range(2)]
    S["fl_empuje"] = [arrow((1.0, 0.3, 0.25)) for _ in range(2)]
    # resistencia y termómetro
    S["resist"] = torus(19, 0.8, (0, 0, 3.6), STEEL2, unique=True)
    S["termo"] = empty((24, 12, 30)); th = S["termo"]
    o = cyl(1.4, 24, (0, 0, 0), (0.95, 0.95, 1.0), parent=th, unique=True); alpha(o, 0.35)
    sph(2.2, (0, 0, -12.5), (0.95, 0.2, 0.2), parent=th)
    S["columna"] = cyl(0.75, 1, (0, 0, 0), (0.95, 0.2, 0.2), parent=th)
    for k in range(6): box((1.6, 0.2, 0.25), (-1.6, -0.8, -9 + 4 * k), (0.9, 0.9, 0.9), parent=th)
    # recirculación
    S["recic"] = [sph(0.8, LEJOS, WATER, seg=8) for _ in range(22)]
    # cal y agua por la tubería, depósito de resina, sal
    S["cal"] = [sph(0.9, LEJOS, CAL, seg=8) for _ in range(30)]
    S["azul"] = [sph(0.6, LEJOS, WATER, seg=8) for _ in range(14)]
    S["resina"] = empty(TANK); r = S["resina"]
    o = cyl(6.2, 26, (0, 0, 0), (0.85, 0.9, 1.0), parent=r, unique=True); alpha(o, 0.28)
    cyl(6.6, 1.2, (0, 0, 13.3), (0.4, 0.42, 0.46), parent=r); cyl(6.6, 1.2, (0, 0, -13.3), (0.4, 0.42, 0.46), parent=r)
    S["bolas"] = [sph(1.25, b_, RESIN, parent=r, seg=12, unique=True) for b_ in BALLS]
    S["salero"] = empty(TANK + Vector((0, 0, 17))); sl = S["salero"]
    bpy.ops.mesh.primitive_cone_add(radius1=5, radius2=1.5, depth=5, location=(0, 0, 0), rotation=(math.pi, 0, 0), vertices=24)
    setup(bpy.context.object, (0.4, 0.42, 0.46), parent=sl)
    S["sal"] = [box((0.9, 0.9, 0.9), LEJOS, (0.97, 0.97, 1.0), rot=(RNG.random(), RNG.random(), 0)) for _ in range(16)]
    S["desague"] = bar_obj((0.55, 0.57, 0.6), 1.0)
    # abrillantador
    S["dosif"] = empty((14, -6, 46)); d = S["dosif"]
    box((7, 5, 5), (0, 0, 0), (0.3, 0.32, 0.36), parent=d); cyl(1.6, 1.0, (0, 0, -2.8), RINSE, parent=d)
    S["chorrito"] = bar_obj(RINSE, 0.35, unique=True)
    # secado
    S["vent"] = empty((0, 27.5, 53)); v = S["vent"]
    torus(5.5, 0.5, (0, 0, 0), (0.35, 0.36, 0.4), parent=v, rot=(math.pi / 2, 0, 0))
    S["aspas"] = empty((0, -0.3, 0), parent=v)
    for k in range(4): box((4.6, 0.3, 1.6), (2.4 * math.cos(k * math.pi / 2), 0, 2.4 * math.sin(k * math.pi / 2)), (0.6, 0.62, 0.66), parent=S["aspas"], rot=(0, -k * math.pi / 2, 0))
    S["vapor"] = [sph(1.0, LEJOS, (0.92, 0.95, 1.0), seg=8, unique=True) for _ in VAP]
    for o in S["vapor"]: alpha(o, 0.6)
    S["frias"] = [box((0.2, 54, 60), (sx * 27.7, 0, 31), STEEL, unique=True) for sx in (-1, 1)]
    S["condens"] = [sph(w, (sx * 27.5, y, z), (0.6, 0.8, 1.0), scale=(0.35, 1, 1.2), seg=10) for sx, y, z, w in WALLD]
    dyn = [cam, S["plato"], S["agua"], S["entrada"], S["bomba"], S["filtro"], S["brazo"], S["chorros"], S["gotitas"], S["fl_chorro"],
           S["fl_empuje"], S["resist"], S["termo"], S["recic"], S["cal"], S["azul"], S["resina"], S["salero"], S["sal"], S["desague"],
           S["dosif"], S["chorrito"], S["vent"], S["vapor"], S["frias"], S["condens"]]
    join_static(dyn)
    return sc, S

# --------------------------------------------------------------------------------------------------
def jets_on(t):
    return t < T("lo primero") - 0.1 or (T("lanza") - 0.2 < t < T("pero el agua del") - 0.2) or (T("suelta") + 0.3 < t < T("y por último"))

def omega(t):
    if not jets_on(t): return 0.0
    if T("y fíjate") - 0.5 < t < T("gira solo"): return 1.3
    return 4.2

_ANG = {}
def ang(t):
    f = int(round(t * 30))
    if f in _ANG: return _ANG[f]
    a = 0.0
    for k in range(f): a += omega(k / 30) / 30
    _ANG[f] = a; return a

def nozzle(a, x, z=0.9):
    return HUB + Vector((x * math.cos(a), x * math.sin(a), z))

def jetdir(a, x):
    s = 1 if x > 0 else -1; tg = Vector((-math.sin(a), math.cos(a), 0)) * s
    return (Vector((0, 0, 1)) - 0.42 * tg).normalized(), tg

def hide_bar(o): bar_set(o, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))

def pose(t, S):
    t_prim, t_caja, t_diez, t_mano, t_quieta = T("lo primero"), T("una caja"), T("solo unos"), T("fregando"), T("pero el agua quieta")
    t_bomba, t_lanza, t_brazos, t_fij, t_incl, t_gira = T("así que pones"), T("lanza"), T("brazos"), T("y fíjate"), T("los agujeros"), T("gira solo")
    t_fria, t_res, t_65, t_rec, t_filt = T("pero el agua fría"), T("resistencia"), T("hasta sesenta"), T("y la misma"), T("pasando")
    t_cal, t_manch, t_dep, t_bol, t_sal, t_limp = T("pero el agua del"), T("y deja"), T("así que añades"), T("bolitas"), T("y la sal"), T("sirve")
    t_secar, t_got, t_abr, t_resb, t_ult, t_nosop, t_calien, t_cond = T("pero al secarse"), T("las gotas"), T("así que en el"), T("hace que"), T("y por último"), T("muchos"), T("los platos calientes"), T("y se condensa")
    a = ang(t); built = t < t_prim - 0.1
    # agua del fondo
    h = 3.0 if built else 3.0 * seg(t, t_caja + 0.6, t_diez + 1.0)
    S["agua"].hide_render = h < 0.05; S["agua"].scale = (54, 54, max(h, 0.05)); S["agua"].location = (0, 0, max(h, 0.05) / 2)
    rinse = seg(t, t_abr + 0.8, t_abr + 2.5)
    set_color(S["agua"], tuple(mix(c, d, 0.5 * rinse) for c, d in zip(WATER, RINSE)))
    fill = (t_caja + 0.4 < t < t_diez + 1.0) or (t_cal - 0.1 < t < t_secar - 0.3)
    if fill:
        L = 9 + 0.8 * math.sin(t * 20); bar_set(S["entrada"], (-27.9, 0, 5), (-27.9 + L, -2, 5 - 0.35 * L))
    else: hide_bar(S["entrada"])
    # bomba, filtro, brazo
    bom = built or t > t_bomba
    S["bomba"].location = (0, 4 - (0 if built else 35 * (1 - seg(t, t_bomba, t_bomba + 0.9))), -9) if bom else LEJOS
    show(S["bomba"], bom)
    fil = built or t > t_filt - 0.4
    S["filtro"].location = (0, -10, 0) if fil else LEJOS; show(S["filtro"], fil)
    if not built: grow(S["filtro"], seg(t, t_filt - 0.4, t_filt + 0.3))
    else: grow(S["filtro"], 1)
    arm = built or t > t_brazos - 0.6
    S["brazo"].location = HUB if arm else LEJOS; show(S["brazo"], arm)
    grow(S["brazo"], 1 if built else seg(t, t_brazos - 0.6, t_brazos + 0.2))
    S["brazo"].rotation_euler = (0, 0, a)
    on = jets_on(t) and arm
    for k, (x, o) in enumerate(zip(NOZ, S["chorros"])):
        if on:
            p0 = nozzle(a, x); d, _ = jetdir(a, x); L = 17 + 2.0 * math.sin(t * 23 + k * 1.7)
            bar_set(o, p0, p0 + d * L)
        else: hide_bar(o)
    for k, g in enumerate(S["gotitas"]):
        if on:
            x = NOZ[k % 6]; p0 = nozzle(a, x); d, _ = jetdir(a, x); u = (t * 2.2 + k / 18 * 3) % 1
            g.location = p0 + d * (u * 19)
        else: g.location = LEJOS
    fl = t_incl - 0.2 < t < t_fria - 0.2
    for k, x in enumerate((20, -20)):
        p0 = nozzle(a, x, 1.3); d, tg = jetdir(a, x)
        if fl:
            u = seg(t, t_incl - 0.2, t_incl + 0.4); aim(S["fl_chorro"][k], p0, d, 1.2 * u)
            v = seg(t, T("empuja") - 0.2, T("empuja") + 0.4); aim(S["fl_empuje"][k], p0 + Vector((0, 0, 0.6)), tg, 1.1 * v + 0.001)
        else: S["fl_chorro"][k].location = LEJOS; S["fl_empuje"][k].location = LEJOS
        for e in (S["fl_chorro"][k], S["fl_empuje"][k]): show(e, fl)
    # plato: suciedad, grasa, cal, gotas, capa
    for k, o in enumerate(S["sucio"]):
        gone = seg(t, t_lanza + 1.0 + 0.3 * k, t_lanza + 1.4 + 0.3 * k)
        o.hide_render = gone > 0.98 and not built
        s = 1.0 if built else 1 - gone; o.scale = (s, 0.3 * s, s)
    for k, o in enumerate(S["grasa"]):
        gone = seg(t, T("grados") + 0.2 * k, T("grados") + 0.6 + 0.2 * k)
        o.hide_render = gone > 0.98; s = 1 - gone; o.scale = (s, 0.3 * s, s)
    for k, o in enumerate(S["calp"]):
        u = seg(t, t_manch + 0.15 * k, t_manch + 0.4 + 0.15 * k) * (1 - seg(t, t_bol + 0.5, t_bol + 1.5))
        o.hide_render = u < 0.02; o.scale = (u, 0.15 * u, u)
    drops = seg(t, t_secar - 0.3, t_secar + 0.3) * (1 - seg(t, t_got + 0.4, t_got + 1.0))
    marks = seg(t, t_got + 0.5, t_got + 1.0) * (1 - seg(t, t_resb - 0.2, t_resb + 0.6))
    flat = seg(t, t_resb - 0.4, T("sin formar") + 0.6)
    film = seg(t, t_resb + 0.2, T("sin formar") + 0.6) * (1 - seg(t, t_calien + 0.3, t_cond + 0.8))
    for k, (g, m) in enumerate(zip(S["gotas"], S["marcas"])):
        gd = max(drops, win01(t, t_resb - 0.6, T("sin formar") + 0.6, 0.3, 0.4))
        sx = mix(1.0, 2.6, flat); sy = mix(0.7, 0.05, flat)
        g.hide_render = gd < 0.02; g.scale = (gd * sx, gd * sy, gd * sx)
        m.hide_render = marks < 0.02; m.scale = (marks, 0.12 * marks, marks)
    S["capa"].hide_render = film < 0.02; S["capa"].active_material.diffuse_color[3] = 0.45 * film
    heat = win01(t, t_calien - 0.4, DUR + 5, 0.6, 0.1)
    set_color(S["loza"], tuple(mix(c, d, 0.55 * heat) for c, d in zip(PLATE, (1.0, 0.55, 0.4))))
    # resistencia y termómetro
    res = t_res - 0.5 < t < t_rec + 2.0
    S["resist"].hide_render = not res; grow(S["resist"], seg(t, t_res - 0.5, t_res + 0.2))
    hh = seg(t, t_res + 0.3, T("más de lo"))
    set_color(S["resist"], tuple(mix(c, d, hh) for c, d in zip(STEEL2, HOT)))
    th = t_res - 0.5 < t < t_cal
    S["termo"].location = (24, 12, 30) if th else LEJOS; show(S["termo"], th)
    temp = keyed(t, [(0, 20), (t_65 - 0.4, 20), (T("grados", fin=True), 65)])
    cz = 3 + 18 * (temp - 20) / 45; S["columna"].scale = (0.75, 0.75, cz); S["columna"].location = (0, 0, -11 + cz / 2)
    # recirculación
    rc = t_rec - 0.2 < t < t_cal - 0.2
    for k, o in enumerate(S["recic"]):
        o.location = poly(LOOP, (t * 0.45 + k / 22) % 1) if rc else LEJOS
    # cal y agua por la tubería → depósito de resina
    t_stick = t_bol + 0.2
    cal_on = t_cal - 0.2 < t < t_limp + 2.6
    for k, o in enumerate(S["cal"]):
        if not cal_on: o.location = LEJOS; continue
        tf = min(t, t_stick); u = (tf * 0.32 + k / 30) % 1; p = poly(PIPE, u)
        ball = TANK + Vector(BALLS[k % len(BALLS)]) + Vector((0, -1.1, 0))
        if t > t_stick:
            v = seg(t, t_stick + 0.05 * k, t_stick + 0.6 + 0.05 * k); p = p.lerp(ball, v)
        if t > t_limp:
            w = seg(t, t_limp + 0.05 * k, t_limp + 1.6 + 0.05 * k)
            p = poly([ball, TANK + Vector((0, -1, -12)), (-40, -1, -9), (-56, -1, -9)], w)
        o.location = p
    for k, o in enumerate(S["azul"]):
        o.location = poly(PIPE, (t * 0.32 + k / 14 + 0.017) % 1) if (t_cal - 0.2 < t < t_secar - 0.3) else LEJOS
    rz = t > t_dep + 0.2 and t < t_secar
    S["resina"].location = TANK if rz else LEJOS; show(S["resina"], rz); grow(S["resina"], seg(t, t_dep + 0.2, t_dep + 1.0))
    load = seg(t, t_stick, t_stick + 2.2) * (1 - seg(t, t_limp + 0.4, t_limp + 2.0))
    for o in S["bolas"]: set_color(o, tuple(mix(c, 0.95, load) for c in RESIN))
    sl = t_sal - 0.4 < t < t_secar
    S["salero"].location = TANK + Vector((0, 0, 17)) if sl else LEJOS; show(S["salero"], sl)
    for k, o in enumerate(S["sal"]):
        st = t_sal + 0.1 + 0.08 * k
        if sl and t > st:
            u = seg(t, st, st + 0.7); diss = seg(t, t_limp + 0.3, t_limp + 1.2)
            o.location = TANK + Vector(((k % 4 - 1.5) * 1.6, (k // 4 - 1.5) * 1.4, 19 - 10 * u))
            s = 0.9 * (1 - diss) + 0.001; o.scale = (s, s, s)
        else: o.location = LEJOS
    if t_limp - 0.3 < t < t_secar: bar_set(S["desague"], TANK + Vector((0, 0, -13)), (-56, 0, -9))
    else: hide_bar(S["desague"])
    # abrillantador
    dz = t_abr - 0.2 < t < t_ult
    S["dosif"].location = (14, -6, 46) if dz else LEJOS; show(S["dosif"], dz)
    if T("chorrito") - 0.2 < t < t_resb + 0.3:
        L = 41 * seg(t, T("chorrito") - 0.2, T("chorrito") + 0.4); bar_set(S["chorrito"], (14, -6, 43), (14, -6, 43 - L))
    else: hide_bar(S["chorrito"])
    # secado
    vt = t_nosop - 0.6 < t < t_calien + 0.2
    S["vent"].location = (0, 27.5, 53) if vt else LEJOS; show(S["vent"], vt)
    S["aspas"].rotation_euler = (0, t * 9 * (1 - seg(t, T("caliente") - 0.3, T("caliente") + 0.6)), 0)
    vp = t_calien - 0.2 < t
    for k, (o, (x0, z0, sx, y1, z1)) in enumerate(zip(S["vapor"], VAP)):
        if vp:
            u = (t * 0.55 + k / len(VAP)) % 1
            p0 = Vector((x0, -1.2, PZ + z0)); p1 = Vector((sx * 26.8, y1, z1))
            o.location = p0.lerp(p1, u) + Vector((0, 0, 4 * math.sin(u * math.pi)))
        else: o.location = LEJOS
    cold = seg(t, t_cond - 0.3, t_cond + 1.2)
    for o in S["frias"]: set_color(o, tuple(mix(c, d, 0.7 * cold) for c, d in zip(STEEL, (0.45, 0.65, 1.0))))
    for k, o in enumerate(S["condens"]):
        u = seg(t, t_cond + 0.05 * k, t_cond + 0.9 + 0.05 * k); o.hide_render = u < 0.02
        o.scale = (0.35 * u, u, 1.2 * u)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.4))

def VD(at, dist, yaw, pitch, lens=40):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    add(0.0, VD((0, 0, 25), 56, -16, 8))
    add(2.6, VD((0, 0, 26), 60, 8, 10))
    add(T("lo primero"), VD((0, 0, 24), 70, 0, 12))
    add(T("y un poco"), VD((-4, 0, 26), 135, -12, 10))
    add(T("pero el agua quieta"), VD((-2, 0, 25), 125, 8, 10))
    add(T("así que pones") + 0.8, VD((0, 0, 8), 110, -14, 1))
    add(T("y fíjate") - 0.2, VD((0, 2, 8), 95, 8, 6))
    add(T("los agujeros"), VD((0, 4, 9), 62, -12, 42))
    add(T("gira solo"), VD((0, 4, 9), 66, 14, 40))
    add(T("pero el agua fría") + 0.4, VD((8, 4, 18), 105, -10, 12))
    add(T("más de lo") + 0.3, VD((8, 4, 20), 98, 8, 12))
    add(T("y la misma") + 0.8, VD((0, 0, 15), 128, -8, 12))
    add(T("pero el agua del") + 0.5, VD((-20, 0, 26), 125, 0, 8))
    add(T("así que añades") - 0.1, VD((-21, 0, 26), 122, -3, 8))
    add(T("así que añades") + 0.8, VD((-36, 0, 22), 82, -16, 10))
    add(T("y la sal"), VD((-38, 0, 26), 76, 8, 14))
    add(T("pero al secarse") - 0.5, VD((-30, 0, 24), 85, 0, 10))
    add(T("pero al secarse") + 0.6, VD((8, 0, 36), 80, -4, 8))
    add(T("hace que"), VD((8, 0, 35), 74, 8, 8))
    add(T("y por último") + 0.3, VD((0, 0, 32), 128, -10, 10))
    add(T("los platos calientes") + 0.5, VD((0, 0, 33), 112, 8, 10))
    add(DUR, VD((0, 0, 30), 140, 0, 12))
    add(DUR + 3, VD((0, 0, 30), 145, 2, 12))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); a = ang(t)
    return {"plato": Pj((0, -1, PZ)), "bomba": Pj((0, -1, -9)), "brazo": Pj(nozzle(a, -16)), "noz": Pj(nozzle(a, 20, 4)),
            "noz2": Pj(nozzle(a, -20, 4)), "resist": Pj((0, -19, 2.5)), "termo": Pj((24, 12, 44)), "filtro": Pj((0, -15, 2)),
            "tubo": Pj((-50, 0, 40)), "tanque": Pj(tuple(TANK + Vector((0, -6, 8)))), "sal": Pj(tuple(TANK + Vector((0, 0, 21)))),
            "dosif": Pj((14, -6, 48)), "pared": Pj((-27, -12, 40)), "pared2": Pj((27, -12, 40)), "vent": Pj((0, 27, 59)),
            "manchas": Pj((0, -1, PZ + 8)), "agua": Pj((-10, -26, 3))}

if __name__ == "__main__":
    run("lavavajillas", build, pose, anchors)
