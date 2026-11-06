# «¿Y si construyes el depósito de agua de tu pueblo?»: primer plano de un grifo que se abre con fuerza; el pueblo en corte:
# pozo, bomba y tubería bajo tierra hasta una casa y un bloque de 4 plantas; la bomba se para y el grifo se seca; por la mañana
# todos abren y el chorro se queda flojo; depósito en el suelo: el agua solo llega a la planta baja; el depósito sube a 30 m
# (regla de 10 en 10 m = 1 bar), torre de hormigón, forma de copa; de noche la bomba lo llena, de día baja; el agua se renueva
# cada día; se va la luz y el grifo sigue echando agua mientras el nivel baja.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("deposito")
BG = (0.13, 0.15, 0.2); NIGHT = (0.04, 0.05, 0.09)
GRASS = (0.36, 0.6, 0.32); SOIL = (0.42, 0.31, 0.22); CLAY = (0.55, 0.38, 0.26); VOID = (0.1, 0.09, 0.09)
PIPE = (0.85, 0.87, 0.9); WATER = (0.3, 0.62, 1.0); DOT = (0.55, 0.85, 1.0); STALE = (0.42, 0.55, 0.3)
CON = (0.76, 0.76, 0.74); CON_IN = (0.9, 0.9, 0.88); STEEL = (0.5, 0.52, 0.58); WALL = (0.93, 0.91, 0.86); WALL2 = (0.86, 0.84, 0.8)
ROOF = (0.78, 0.32, 0.26); WIN = (1.0, 0.85, 0.45); WOFF = (0.2, 0.22, 0.28); WOOD = (0.55, 0.4, 0.28); CHROME = (0.82, 0.84, 0.88)
LEJOS = (0, 0, -300)
YP = -0.35            # plano de las tuberías (delante del corte del terreno)
XW, XPU = -9.2, -7.4 # pozo y bomba
XT, YT = -3.6, 1.6    # torre
ZM = -1.5             # tubería general
XH, XB = 3.0, 9.6     # subidas de la casa y del bloque
ZTOP = 25.0           # base del depósito arriba
random.seed(3)

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

P_POZO = poly([(XW, YP, -5.6), (XW, YP, 0.7), (XPU, YP, 0.7), (XPU, YP, ZM), (XB, YP, ZM)])
P_CASA = poly([(XH, YP, ZM), (XH, YP, 1.15), (XH + 0.42, YP, 1.15)])
P_BLOQ = [poly([(XB, YP, ZM), (XB, YP, 3 * f + 1.15), (XB + 0.42, YP, 3 * f + 1.15)]) for f in range(4)]
def p_torre(zb): return poly([(XT, YP, ZM), (XT, -0.12, ZM), (XT, -0.12, zb + 0.4)])

def cutmods(o, cutters, th=None, inner=None):
    if th:
        m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
        if inner: o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
    for c in cutters:
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = c
        try: b.solver = 'MANIFOLD'
        except Exception: b.solver = 'EXACT'
    return o

def pipe(p0, p1, r=0.2, col=PIPE):
    o = bar_obj(col, r); bar_set(o, p0, p1); return o

def tap(S, key, x, z, parent=None):
    """grifo: cuerpo, caño hacia +x y palanca; devuelve la palanca y el punto del chorro"""
    cyl(0.07, 0.12, (x, YP, z), CHROME)
    pipe((x, YP, z + 0.03), (x + 0.42, YP, z + 0.03), 0.045, CHROME)
    pipe((x + 0.42, YP, z + 0.03), (x + 0.42, YP, z - 0.06), 0.045, CHROME)
    lev = empty((x, YP, z + 0.07)); box((0.05, 0.05, 0.22), (0, 0, 0.11), CHROME, parent=lev)
    sph(0.04, (0, 0, 0.23), (0.9, 0.25, 0.25), parent=lev)
    box((0.9, 0.7, 0.08), (x + 0.45, YP + 0.05, z - 0.35), (0.95, 0.95, 0.96))          # encimera / lavabo
    box((0.6, 0.5, 0.04), (x + 0.45, YP + 0.05, z - 0.3), (0.75, 0.82, 0.9))
    zf = 3.0 * round((z - 1.15) / 3); box((0.9, 0.7, z - 0.4 - zf), (x + 0.45, YP + 0.05, zf + (z - 0.4 - zf) / 2), WOOD)
    jet = cyl(0.035, 1, LEJOS, (0.55, 0.82, 1.0), unique=True)
    for vv in jet.data.vertices: vv.co.z -= 0.5
    drops = [sph(0.025, LEJOS, (0.65, 0.88, 1.0), seg=8) for _ in range(6)]
    S["taps"][key] = dict(lev=lev, jet=jet, drops=drops, top=Vector((x + 0.42, YP, z - 0.07)), sink=z - 0.3)

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam, "sc": sc, "taps": {}}
    cam.data.clip_start = 0.05
    # terreno en corte (y >= 0)
    box((80, 14, 0.3), (0, 7, -0.15), GRASS)
    box((80, 14, 2.5), (0, 7, -1.55), SOIL); box((80, 14, 7), (0, 7, -6.3), CLAY)
    rng = random.Random(4)
    for k in range(160):
        x, z = rng.uniform(-30, 30), rng.uniform(-9.5, -0.5)
        if abs(x - XW) < 1.0: continue
        c = SOIL if z > -2.8 else CLAY
        sph(rng.uniform(0.08, 0.2), (x, 0.0, z), tuple(v * rng.uniform(0.75, 0.9) for v in c), scale=(1.3, 0.25, 1), seg=8)
    box((1.6, 0.1, 6.2), (XW, -0.02, -3.0), VOID)                     # pozo
    S["pozo_agua"] = box((1.5, 0.1, 1.6), (XW, -0.05, -5.3), WATER)
    # tuberías
    pts = P_POZO[0]
    for a, b in zip(pts, pts[1:]): pipe(a, b, 0.22)
    for P in [P_CASA] + P_BLOQ:
        pipe(P[0][0], P[0][1], 0.16); pipe(P[0][1], P[0][2], 0.1)
    # bomba
    box((1.6, 1.4, 1.3), (XPU, 0.4, 0.65), (0.25, 0.45, 0.8)); cyl(0.45, 0.6, (XPU + 0.9, 0.4, 0.65), (0.3, 0.32, 0.36), rot=(0, math.pi / 2, 0))
    S["rotor"] = empty((XPU, YP - 0.3, 0.65))
    for k in range(4): box((0.08, 0.03, 0.9), (0, 0, 0), (0.95, 0.95, 0.95), parent=S["rotor"], rot=(0, k * math.pi / 4, 0))
    S["lamp"] = sph(0.15, (XPU - 0.5, 0.0, 1.45), (0.3, 0.9, 0.4), seg=12, unique=True)
    # casa (corte: sin pared delantera)
    def casa(x0, x1, floors, roof):
        h = 3.0 * floors
        box((x1 - x0, 6.4, 0.25), ((x0 + x1) / 2, 2.8, 0.12), WALL2)
        box((x1 - x0, 0.25, h), ((x0 + x1) / 2, 6.0, h / 2), WALL)
        for xs in (x0, x1): box((0.25, 6.4, h), (xs, 2.8, h / 2), WALL2)
        for f in range(1, floors): box((x1 - x0, 6.4, 0.25), ((x0 + x1) / 2, 2.8, 3.0 * f), WALL2)
        if roof:
            w = (x1 - x0) / 2 + 0.4
            for s_ in (-1, 1): box((w * 1.15, 6.8, 0.25), ((x0 + x1) / 2 + s_ * w * 0.5, 2.8, h + 0.8), ROOF, rot=(0, s_ * math.radians(-32), 0))
        else: box((x1 - x0 + 0.3, 6.6, 0.3), ((x0 + x1) / 2, 2.8, h + 0.1), (0.6, 0.6, 0.62))
        wins = []
        for f in range(floors):
            for xx in (x0 + (x1 - x0) * 0.3, x0 + (x1 - x0) * 0.72):
                wins.append(box((1.0, 0.1, 1.1), (xx, 5.85, 3.0 * f + 1.7), WIN, unique=True))
        return wins
    S["wins"] = casa(1.8, 6.6, 1, True) + casa(8.4, 13.4, 4, False)
    tap(S, "casa", XH, 1.15)
    for f in range(4): tap(S, f, XB, 3 * f + 1.15)
    # regla de alturas
    S["regla"] = empty(LEJOS)
    box((0.12, 0.12, 30), (0, 0, 15), (0.95, 0.95, 0.95), parent=S["regla"])
    for z in (10, 20, 30): box((0.9, 0.12, 0.12), (0, 0, z), (0.95, 0.95, 0.95), parent=S["regla"])
    S["regla_fill"] = box((0.22, 0.14, 1), LEJOS, WATER)
    S["linea"] = [box((0.5, 0.06, 0.06), LEJOS, (1, 1, 1)) for _ in range(16)]
    # torre: patas de acero, columna de hormigón, tubo que sube
    S["patas"] = [bar_obj(STEEL, 0.14) for _ in range(4)]
    S["riostras"] = [bar_obj(STEEL, 0.07) for _ in range(6)]
    S["col"] = cyl(1.3, 1, LEJOS, CON, v=40)
    for vv in S["col"].data.vertices: vv.co.z += 0.5
    S["sube"] = bar_obj(PIPE, 0.2); S["sube2"] = bar_obj(PIPE, 0.2)
    # depósito: cilindro y copa, con el agua recortada por el nivel
    bpy.ops.mesh.primitive_cube_add(size=1, location=(XT, YT - 5, 20)); cutF = bpy.context.object; cutF.scale = (14, 10, 80); cutF.hide_render = True
    bpy.ops.mesh.primitive_cube_add(size=1, location=(XT, YT, 100)); cutL = bpy.context.object; cutL.scale = (14, 14, 20); cutL.hide_render = True
    S["cutL"] = cutL
    S["tk"] = tk = empty(LEJOS); S["cup"] = cup = empty(LEJOS)
    o = cyl(3.2, 5.6, (0, 0, 2.8), CON, parent=tk, v=56); cutmods(o, [cutF], 0.3, CON_IN)
    S["w_tk"] = cyl(2.9, 5.0, (0, 0, 2.8), WATER, parent=tk, v=56, unique=True); cutmods(S["w_tk"], [cutF, cutL])
    bpy.ops.mesh.primitive_cone_add(radius1=1.8, radius2=4.2, depth=6.0, location=(0, 0, 3.0), vertices=56); o = bpy.context.object
    setup(o, CON, cup, True); cutmods(o, [cutF], 0.3, CON_IN)
    cyl(4.25, 0.5, (0, 0, 6.2), CON, parent=cup, v=56)
    bpy.ops.mesh.primitive_cone_add(radius1=1.5, radius2=3.9, depth=5.7, location=(0, 0, 3.1), vertices=56); o = bpy.context.object
    setup(o, WATER, cup, True, unique=True); cutmods(o, [cutF, cutL]); S["w_cup"] = o
    S["flechas"] = []
    for k in range(3):
        e = empty(LEJOS); S["flechas"].append(e)
        bpy.ops.mesh.primitive_cone_add(radius1=0.6, radius2=0, depth=1.0, location=(0, 0, 0), rotation=(math.pi, 0, 0), vertices=24)
        setup(bpy.context.object, (0.95, 0.28, 0.25), e); cyl(0.22, 1.4, (0, 0, 1.1), (0.95, 0.28, 0.25), parent=e)
    # puntos de agua
    S["d_pozo"] = [sph(0.13, LEJOS, DOT, seg=10) for _ in range(40)]
    S["d_casa"] = [sph(0.06, LEJOS, DOT, seg=8) for _ in range(10)]
    S["d_bloq"] = [[sph(0.1, LEJOS, DOT, seg=8) for _ in range(12)] for _ in range(4)]
    S["d_torre"] = [sph(0.13, LEJOS, DOT, seg=10) for _ in range(30)]
    dyn = [cam, cutF, cutL, S["rotor"], S["lamp"], S["wins"], S["regla"], S["regla_fill"], S["linea"], S["patas"], S["riostras"], S["col"],
           S["sube"], S["sube2"], tk, cup, S["flechas"], S["d_pozo"], S["d_casa"], S["d_bloq"], S["d_torre"], S["pozo_agua"]]
    for v in S["taps"].values(): dyn += [v["lev"], v["jet"], v["drops"]]
    join_static(dyn)
    return sc, S

# ---------- estados ----------
def bomba_on(t):
    return not (T("pero si la bomba") + 0.3 < t < T("y por la mañana") + 0.3) and t < T("por eso", 1) + 0.2
def rot_bomba(t):
    a, x = 0.0, 0.0
    while x < t: a += (9.0 if bomba_on(x) else 0.0) / 30; x += 1 / 30
    return a
def tap_flow(t, key):
    a_man, a_dep, a_sub, a_grav = T("y por la mañana"), T("así que construyes"), T("así que lo subes"), T("ahora la gravedad")
    if key == "casa":
        if t < a_man:
            u = 1 - seg(t, T("pero si la bomba") + 0.3, T("se seca", fin=True))
            return min(seg(t, 0.05, 0.35), u)
        if t < a_sub: return 0.35 + 0.08 * math.sin(t * 9)
        return 0.9
    f = key
    if t < a_man: return 0.0
    if t < a_dep: return 0.35 + 0.08 * math.sin(t * 9 + f) if f < 2 else 0.12 * max(0, math.sin(t * 7 + f))
    if t < a_grav + 0.4:
        return (0.5 if f == 0 else 0.0) if t > T("pero si lo pones") else 0.35
    if t < T("y aquí viene"): return 1.0 * seg(t, a_grav + 0.4, a_grav + 1.4)
    if T("la bomba lo va") - 0.3 < t < T("y cuando todos") - 0.2: return 0.0     # de noche casi nadie gasta
    if T("pero si el agua") < t < T("por eso", 1): return 0.0
    return 1.0

def zbase(t):
    return ZTOP * seg(t, T("así que lo subes"), T("muy alto", fin=True) + 0.3)

def nivel(t):
    return keyed(t, [(0, 0.0), (T("así que construyes") + 0.3, 0.0), (T("pero si lo pones"), 0.85), (T("y aquí viene"), 0.85),
                     (T("el agua del"), 0.6), (T("la bomba lo va"), 0.6), (T("y cuando todos") - 0.2, 0.95), (T("el depósito baja", fin=True) + 0.6, 0.55),
                     (T("así que cada"), 0.55), (T("así que cada") + 1.2, 0.2),
                     (T("y el agua siempre") - 0.2, 0.92), (T("y el agua siempre") + 0.9, 0.3), (T("por eso", 1), 0.9), (T("sigue saliendo", fin=True), 0.45), (DUR + 2, 0.4)])

def torre_dir(t):
    """+1 sube agua al depósito, -1 baja a las casas, 0 quieto"""
    if t < T("así que construyes") + 0.3: return 0
    if t < T("pero si lo pones"): return 1
    if T("la bomba lo va") - 0.3 < t < T("y cuando todos") - 0.2: return 1
    if T("y cuando todos") - 0.2 < t < T("y cubre lo que", fin=True) + 0.4: return -1
    if T("pero si el agua") < t < T("así que cada"): return 0
    if T("así que cada") < t < T("por eso", 1):
        return -1 if (t - T("así que cada")) % 2.4 < 1.2 else 1
    if t > T("por eso", 1): return -1
    if T("ahora la gravedad") < t: return -1
    return 0

def flow_dots(dots, path, t, on, v, rev=False, zmax=None, phase=0.0):
    L = path[1][-1]; n = len(dots)
    for k, d in enumerate(dots):
        if not on: d.location = LEJOS; continue
        s = (L * k / n + v * t + phase) % L
        if rev: s = L - s
        p = at(path, s)
        if zmax is not None and p.z > zmax: d.location = LEJOS; continue
        d.location = p + Vector((0, -0.12, 0))

def pose(t, S):
    sc = S["sc"]
    noche = win01(t, T("la bomba lo va") - 0.5, T("y cuando todos") - 0.2, 0.5, 0.5)
    apagon = seg(t, T("por eso", 1), T("por eso", 1) + 0.6)
    sc.world.color = lin(tuple(mix(a, b, max(noche, 0.7 * apagon)) for a, b in zip(BG, NIGHT)))
    for w in S["wins"]: set_color(w, WOFF if apagon > 0.5 else WIN)
    on = bomba_on(t)
    set_color(S["lamp"], (0.3, 0.9, 0.4) if on else (0.95, 0.25, 0.2))
    S["rotor"].rotation_euler = (0, rot_bomba(t), 0)
    S["pozo_agua"].scale = (1.5, 0.1, 1.6)
    # grifos
    for key, tp in S["taps"].items():
        fl = tap_flow(t, key)
        if key == "casa": tp["lev"].rotation_euler = (0, -0.9 * seg(t, 0.0, 0.3), 0)
        else: tp["lev"].rotation_euler = (0, -0.9 * (1 if fl > 0.05 or t > T("y por la mañana") else 0), 0)
        top = tp["top"]; L = top.z - tp["sink"]
        if fl > 0.04:
            tp["jet"].location = (top.x, top.y, top.z - L / 2); tp["jet"].scale = (0.4 + 0.8 * fl, 0.4 + 0.8 * fl, L)
        else: tp["jet"].location = LEJOS
        for k, d in enumerate(tp["drops"]):
            if fl > 0.04:
                u = (t * (2.5 + 2 * fl) + k / 6) % 1.0
                d.location = (top.x + 0.06 * math.sin(k * 2.3 + t * 11) * fl, top.y + 0.04 * math.cos(k), tp["sink"] + 0.03 + 0.12 * fl * math.sin(math.pi * u))
            else: d.location = LEJOS
    # puntos de agua
    flow_dots(S["d_pozo"], P_POZO, t, on and t > 0.4, 3.0)
    fc = tap_flow(t, "casa")
    flow_dots(S["d_casa"], P_CASA, t, fc > 0.05, 0.6 + 2.0 * fc)
    lvz = zbase(t) + 0.3 + 5.0 * nivel(t)
    for f in range(4):
        ff = tap_flow(t, f)
        flow_dots(S["d_bloq"][f], P_BLOQ[f], t, ff > 0.05, 0.6 + 2.0 * ff, phase=f * 0.37)
    # en el suelo: el agua del bloque solo llega hasta el nivel del depósito
    a0, a1 = T("pero si lo pones"), T("así que lo subes") + 0.4
    if a0 < t < a1:
        flow_dots(S["d_bloq"][3], P_BLOQ[3], t, True, 1.0, zmax=lvz)
    for k, b in enumerate(S["linea"]):
        if a0 + 0.3 < t < a1 and k * 0.8 < (t - a0) * 12:
            b.location = (XT + 3.6 + 0.8 * k, YP - 0.1, lvz)
        else: b.location = LEJOS
    # torre
    zb = zbase(t)
    if t > T("así que construyes") - 0.2:
        crece = seg(t, T("así que construyes") - 0.2, T("así que construyes") + 0.8)
        copa = t > T("y le das forma") + 0.15
        tk, cup = S["tk"], S["cup"]
        on_t, off_t = (cup, tk) if copa else (tk, cup)
        pop = 1 + 0.12 * math.sin(math.pi * seg(t, T("y le das forma"), T("y le das forma") + 0.6)) if copa else crece
        shake = 0.05 * math.sin(t * 40) * win01(t, T("pero tanta"), T("así que lo apoyas"), 0.2, 0.2)
        on_t.location = (XT + shake, YT, zb); on_t.scale = (pop, pop, pop); off_t.location = LEJOS
        S["cutL"].location = (XT, YT, (zb + (0.3 + 5.4 * nivel(t)) * (pop if not copa else 1)) + 10)
        S["cutL"].scale = (14, 14, 20)
        # color del agua (quieta → se estropea)
        stale = seg(t, T("pero si el agua"), T("se estropea", fin=True)) * (1 - seg(t, T("así que cada"), T("y el agua siempre")))
        for w in (S["w_tk"], S["w_cup"]): set_color(w, tuple(mix(a, b, stale) for a, b in zip(WATER, STALE)))
    else:
        S["tk"].location = LEJOS; S["cup"].location = LEJOS
    # patas y columna
    hp = zb
    if hp > 0.2:
        for k, o in enumerate(S["patas"]):
            dx, dy = (1.6 if k % 2 else -1.6), (1.6 if k // 2 else -1.6)
            bar_set(o, (XT + dx, YT + dy, 0), (XT + dx * 0.9, YT + dy * 0.9, hp + 0.1))
        for k, o in enumerate(S["riostras"]):
            z0 = hp * (k % 3 + 0.5) / 3.3; z1 = hp * (k % 3 + 1.2) / 3.3; s_ = 1 if k < 3 else -1
            bar_set(o, (XT - 1.55 * s_, YT - 1.55, z0), (XT + 1.55 * s_, YT - 1.55, z1))
    else:
        for o in S["patas"] + S["riostras"]: o.location = LEJOS
    hc = seg(t, T("así que lo apoyas") - 0.2, T("de hormigón", fin=True))
    if hc > 0 and hp > 0.2:
        S["col"].location = (XT, YT, 0); S["col"].scale = (hc, hc, hp)
        for o in S["patas"] + S["riostras"]:
            if hc > 0.98: o.location = LEJOS
    else: S["col"].location = LEJOS
    # tubo que sube al depósito
    if t > T("así que construyes") + 0.3:
        bar_set(S["sube"], (XT, YP, ZM), (XT, -0.12, ZM)); bar_set(S["sube2"], (XT, -0.12, ZM), (XT, -0.12, zb + 0.5))
    else: S["sube"].location = LEJOS; S["sube2"].location = LEJOS
    dr = torre_dir(t)
    flow_dots(S["d_torre"], p_torre(zb), t, dr != 0, 3.5, rev=(dr < 0))
    # flechas de peso
    pf = win01(t, T("pero tanta") - 0.1, T("así que lo apoyas") + 0.3, 0.3, 0.3)
    for k, e in enumerate(S["flechas"]):
        if pf > 0:
            e.location = (XT - 2.2 + 2.2 * k, YT - 3.8, zb + 8.5 - 0.6 * ((t * 2 + k * 0.3) % 1.0)); e.scale = (pf,) * 3
        else: e.location = LEJOS
    # regla
    r0, r1 = T("cada diez") - 0.4, T("pero tanta")
    if r0 < t < r1:
        S["regla"].location = (XT - 5.6, YP, 0)
        h = keyed(t, [(T("cada diez"), 0.01), (T("de altura"), 10), (T("un depósito de"), 10), (T("treinta") + 0.4, 30)])
        S["regla_fill"].location = (XT - 5.6, YP - 0.08, h / 2); S["regla_fill"].scale = (0.22, 0.14, h)
    else: S["regla"].location = LEJOS; S["regla_fill"].location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def V_(at, off, lens=35):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    tg = Vector((XH + 0.4, YP, 1.0))
    add(0.0, V_(tg + Vector((-0.1, 0, 0.0)), (-0.7, -2.5, 0.45), 35))
    add(T("y el agua sale"), V_(tg + Vector((-0.1, 0, 0.0)), (-0.8, -2.8, 0.5), 35))
    add(T("pero nadie"), V_(tg + Vector((-0.2, 0, 0.5)), (-1.5, -5.5, 0.9), 35))
    add(T("vamos a construir"), V_((2.5, 0, 2.0), (0, -26, 3.0), 35))
    add(T("tu pueblo"), V_((2.6, 0, 4.0), (0, -53, 4.0), 35))
    add(T("pero si la bomba"), V_((-1.5, 0, 2.5), (0, -34, 3.5), 35))
    add(T("y por la mañana"), V_((5.5, 0, 4.0), (0, -27, 3.0), 35))
    add(T("así que construyes"), V_((0.5, 0, 4.5), (0, -38, 3.5), 35))
    add(T("pero si lo pones"), V_((3.5, 0, 6.0), (0, -36, 3.0), 35))
    add(T("así que lo subes") + 0.4, V_((2.0, 0, 9.0), (0, -46, 3.0), 35))
    add(T("ahora la gravedad"), V_((1.6, 0, 19.2), (0, -64, 3.0), 35))
    add(T("un depósito de"), V_((1.6, 0, 19.2), (0, -64, 3.0), 35))
    add(T("pero tanta"), V_((XT, 0, 25.5), (0, -32, 1.0), 35))
    add(T("y le das forma"), V_((XT, 0, 26.5), (0, -28, 0.5), 35))
    add(T("y aquí viene"), V_((1.6, 0, 19.2), (0, -64, 3.0), 35))
    add(T("pero si el agua"), V_((XT + 0.5, 0, 26.0), (0, -30, 0.5), 35))
    add(T("y el agua siempre"), V_((XT + 0.5, 0, 25.5), (0, -32, 0.5), 35))
    add(T("por eso", 1), V_((1.6, 0, 19.2), (0, -64, 3.0), 35))
    add(DUR + 2, V_((1.6, 0, 19.5), (0, -70, 3.0), 35))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); zb = zbase(t)
    lvz = zb + 0.3 + 5.0 * nivel(t)
    return {"grifo": Pj((XH + 0.42, YP, 1.0)), "bomba": Pj((XPU, 0.4, 1.5)), "pozo": Pj((XW, 0, -4.5)), "tubo": Pj((0, YP, ZM)),
            "tk": Pj((XT, YT - 3.3, zb + 6.2)), "tk_mid": Pj((XT, YT, zb + 3.0)), "f0": Pj((XB + 1.2, YP, 1.6)), "f1": Pj((XB + 1.2, YP, 4.6)),
            "f2": Pj((XB + 1.2, YP, 7.6)), "f3": Pj((XB + 1.2, YP, 10.6)), "r10": Pj((XT - 5.6, YP, 10)), "r20": Pj((XT - 5.6, YP, 20)),
            "r30": Pj((XT - 5.6, YP, 30)), "r0": Pj((XT - 5.6, YP, 0)), "col": Pj((XT, YT - 1.3, zb * 0.45)),
            "cupL": Pj((XT - 4.2, YT, zb + 6.6)), "cupR": Pj((XT + 4.2, YT, zb + 6.6)), "botL": Pj((XT - 1.8, YT, zb - 0.4)), "botR": Pj((XT + 1.8, YT, zb - 0.4)),
            "nivel": Pj((XT, YT - 2, lvz)), "flecha": Pj((XT, YT - 3.8, zb + 10.0))}

if __name__ == "__main__":
    run("deposito", build, pose, anchors)
