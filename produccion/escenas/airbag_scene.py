# "El airbag": coche cortado por la mitad con un maniquí; sensores, centralita, pastilla, bolsa que se infla y se vacía.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector, Quaternion

CARC = (0.25, 0.55, 0.95); INNER = (0.92, 0.92, 0.9); DUM = (1.0, 0.85, 0.35); DARK = (0.18, 0.19, 0.22); WIRE = (1.0, 0.85, 0.1)
BAG = (0.97, 0.97, 0.98)
WC = Vector((0.22, 0.4, 1.06)); WN = Vector((-0.9, 0, 0.42)).normalized()     # centro y normal del volante (mira al conductor)
HIP = Vector((-0.5, 0.4, 0.62))
SENSOR = Vector((2.12, 0.3, 0.52)); ECU = Vector((-0.42, 0.4, 0.32))

def shell(o, th, inner=None):
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
    if inner is not None:
        o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
    return o

def cutmod(o, cutter):
    m = o.modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = cutter
    try: m.solver = 'MANIFOLD'
    except Exception: m.solver = 'EXACT'

def build():
    sc, cam = scene_setup(world=(0.62, 0.82, 0.98))
    S = {"cam": cam}
    box((200, 200, 0.1), (0, 0, -0.05), (0.55, 0.78, 0.45))
    box((200, 3.2, 0.02), (0, 0.3, 0.005), (0.32, 0.33, 0.37))
    S["dashes"] = [box((1.2, 0.12, 0.01), (-12 + k * 3, -0.9, 0.02), (1, 1, 1)) for k in range(12)]
    S["trees"] = []
    for k in range(10):
        tr = empty((-14 + k * 4, 4.5, 0)); S["trees"].append(tr)
        cyl(0.12, 1.2, (0, 0, 0.6), (0.55, 0.38, 0.25), tr); sph(0.75, (0, 0, 1.6), (0.35, 0.72, 0.4), tr)
    wall = empty((30, 0.3, 0)); S["wall"] = wall
    box((0.6, 3.5, 1.6), (0.3, 0, 0.8), (0.95, 0.95, 0.95), wall)
    for k in range(4): box((0.62, 0.45, 1.62), (0.3, -1.3 + k * 0.85, 0.8), (0.95, 0.3, 0.3), wall)
    # cortadores
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5, 1)); cut1 = bpy.context.object; cut1.scale = (10, 10, 4); cut1.hide_render = True
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5, 1)); cut2 = bpy.context.object; cut2.scale = (2, 10, 3); cut2.hide_render = True
    S["cut1"], S["cut2"] = cut1, cut2
    car = empty(); S["car"] = car
    cuts = []
    lower = box((4.4, 1.8, 0.7), (0, 0, 0.6), CARC); shell(lower, 0.04, INNER); cuts.append(lower)
    cab = box((2.1, 1.7, 0.6), (-0.2, 0, 1.25), CARC); shell(cab, 0.04, INNER); cuts.append(cab)
    for o in cuts: cutmod(o, cut1); o.parent = car
    for x in (-1.4, 1.4):
        for y in (-0.88, 0.88):
            w = cyl(0.33, 0.22, (x, y, 0.33), (0.12, 0.12, 0.14), car, rot=(math.pi / 2, 0, 0)); cyl(0.16, 0.24, (x, y, 0.33), (0.78, 0.8, 0.84), car, rot=(math.pi / 2, 0, 0))
    box((0.6, 1.6, 0.25), (0.62, 0, 0.98), DARK, car)                                   # salpicadero
    box((0.5, 0.5, 0.12), (-0.42, 0.4, 0.5), DARK, car); box((0.12, 0.5, 0.75), (-0.72, 0.4, 0.9), DARK, car, rot=(0, -0.2, 0))
    box((0.12, 0.08, 0.08), SENSOR, (0.95, 0.3, 0.3), car); S["sensor_led"] = sph(0.035, SENSOR + Vector((0.04, -0.05, 0.04)), (0.3, 0.3, 0.3), car, unique=True)
    box((0.22, 0.16, 0.08), ECU, (0.25, 0.6, 0.35), car)
    # volante: aro, radios, columna y buje (cortable)
    q = Vector((0, 0, 1)).rotation_difference(WN)
    wheel = empty(WC, car); wheel.rotation_mode = 'QUATERNION'; wheel.rotation_quaternion = q; S["wheel"] = wheel
    torus(0.19, 0.025, (0, 0, 0), DARK, wheel)
    for a in (0, 2.1, 4.2):
        o = bar_obj(DARK, 0.018, wheel); bar_set(o, (0, 0, 0), (0.19 * math.cos(a), 0.19 * math.sin(a), 0))
    col = bar_obj(DARK, 0.03, car); bar_set(col, WC - 0.02 * WN, Vector((0.65, 0.4, 0.92)))
    hub = cyl(0.085, 0.08, (0, 0, 0.03), (0.3, 0.31, 0.35), wheel); shell(hub, 0.012, (0.85, 0.85, 0.88)); cutmod(hub, cut2)
    S["hub"] = hub
    flaps = []
    for s in (1, -1):
        h = empty((0, 0.085 * s, 0.072), wheel); flaps.append(h)
        f = box((0.16, 0.085, 0.012), (0, -0.0425 * s, 0), (0.3, 0.31, 0.35), h)
    S["flaps"] = flaps
    S["folds"] = [box((0.13, 0.13, 0.006), (0, 0, 0.022 + k * 0.009), BAG, wheel) for k in range(5)]
    S["pill"] = cyl(0.045, 0.018, (0, 0, 0.005), (0.4, 0.4, 0.45), wheel, unique=True)
    # bolsa
    bag = empty(WC + 0.02 * WN, car); bag.rotation_mode = 'QUATERNION'; bag.rotation_quaternion = q; S["bag"] = bag
    sph(0.3, (0, 0, 0.22), BAG, bag, scale=(1.05, 1.05, 0.8))
    S["vents"] = [cyl(0.03, 0.01, (0.12 * s, 0.1, 0.0), (0.25, 0.25, 0.28), bag) for s in (1, -1)]
    # cable con pulsos
    S["wire_pts"] = [SENSOR, Vector((1.9, 0.4, 0.3)), Vector((-0.3, 0.4, 0.28)), ECU, Vector((-0.1, 0.4, 0.4)), Vector((0.62, 0.4, 0.88)), WC - 0.02 * WN]
    for a, b in zip(S["wire_pts"], S["wire_pts"][1:]):
        o = bar_obj(WIRE, 0.008, car); bar_set(o, a, b)
    S["pulses"] = [sph(0.025, (0, 0, -9), (1, 1, 0.7), car) for _ in range(6)]
    S["gas"] = [sph(0.025, (0, 0, -9), (1, 1, 1), wheel) for _ in range(14)]
    S["puffs"] = [sph(0.05, (0, 0, -9), (0.98, 0.98, 1.0), car) for _ in range(10)]
    S["powder"] = [sph(random.Random(k).uniform(0.03, 0.08), (0, 0, -9), (0.97, 0.97, 0.99), car) for k in range(40)]
    # maniquí
    dummy = empty(HIP, car); S["dummy"] = dummy
    torso = empty((0, 0, 0), dummy); S["torso"] = torso
    cyl(0.16, 0.5, (0, 0, 0.27), DUM, torso); sph(0.16, (0, 0, 0.52), DUM, torso)
    neck = empty((0, 0, 0.6), torso); S["neck"] = neck
    sph(0.11, (0, 0, 0.13), DUM, neck); cyl(0.04, 0.1, (0, 0, 0.03), DUM, neck)
    for s in (1, -1):
        sph(0.03, (0.105, 0.05 * s, 0.15), (0.1, 0.1, 0.1), neck)
    S["belt"] = bar_obj((0.55, 0.57, 0.62), 0.03, torso, unique=True); bar_set(S["belt"], (-0.05, -0.17, 0.62), (0.07, -0.16, 0.0))
    for s in (1, -1):
        o = bar_obj(DUM, 0.045, dummy); bar_set(o, (0.05, 0.1 * s, 0.02), (0.55, 0.1 * s, 0.05))
        o = bar_obj(DUM, 0.04, dummy); bar_set(o, (0.55, 0.1 * s, 0.05), (0.75, 0.1 * s, -0.3))
    S["arms"] = [bar_obj(DUM, 0.035, car) for _ in range(2)]
    join_static([cam, cut1, cut2, car, S["dashes"], S["trees"], wall])
    return sc, S

T_HOOK = 1.6; T_HIT = 17.2; T_FIRE = 30.0

def pulses(S, t, a, b):
    pts = S["wire_pts"]; L = [(q - p).length for p, q in zip(pts, pts[1:])]; tot = sum(L)
    for k, p in enumerate(S["pulses"]):
        if not (a <= t < b): p.location = (0, 0, -9); continue
        d = ((t - a) * 0.8 + k / 6) % 1.0 * tot
        for (p0, p1), l in zip(zip(pts, pts[1:]), L):
            if d <= l: p.location = p0.lerp(p1, d / l); break
            d -= l

def bag_state(t):
    """inflado 0..1 del airbag"""
    hook = seg(t, T_HOOK, T_HOOK + 0.12) * (1 - seg(t, 8.6, 9.6))
    main = seg(t, T_FIRE + 3.7, T_FIRE + 6.0) * (1 - 0.92 * seg(t, 50.4, 57.5))
    return max(hook, main)

def lean(t):
    hook = 0.45 * seg(t, T_HOOK, T_HOOK + 0.35) * (1 - seg(t, 8.6, 9.6))
    main = 0.42 * seg(t, 38.5, 41.8) + 0.12 * seg(t, 49.0, 55.4) - 0.54 * seg(t, 57.5, 59.0)
    return max(hook, max(0, main))

def pose(t, S):
    # movimiento del entorno (el coche está quieto): carretera y árboles corren hacia atrás
    if t < T_HOOK: v_off = -12 * t
    elif t < 9.6: v_off = -12 * T_HOOK + 12 * T_HOOK * seg(t, 8.6, 9.6)
    elif t < T_HIT: v_off = -10 * (t - 9.6) * (1 - 0.5 * seg(t, 13.9, 15.3))
    else: v_off = -10 * (T_HIT - 9.6) * 0.75
    for k, d in enumerate(S["dashes"]): d.location.x = ((-12 + k * 3 + v_off) % 36) - 18
    for k, tr in enumerate(S["trees"]): tr.location.x = ((-14 + k * 4 + v_off) % 40) - 20
    if t < 9.6: wx = 2.55 + 12 * (T_HOOK - min(t, T_HOOK)) + 12 * T_HOOK * seg(t, 8.6, 9.6) * 3
    else: wx = 2.55 + 10 * max(0, T_HIT - t) if t > 13.0 else 60
    S["wall"].location.x = wx
    # sacudida del choque
    jolt = Vector((0, 0, 0))
    for a in (T_HOOK, T_HIT):
        if a <= t < a + 0.4: k = t - a; jolt += Vector((-0.06 * math.sin(k * 40), 0, 0.02 * math.sin(k * 55))) * (1 - k / 0.4)
    S["car"].location = jolt
    # cortes: coche desde 9 s, buje desde 23.8 s
    S["cut1"].location.y = -5
    S["cut2"].location = Vector((0, 0.4 - 5 - 20 * (1 - seg(t, 23.8, 24.6)) * (1 - seg(t, 36.2, 36.8)) - 20 * seg(t, 36.2, 36.8), 1.0))
    S["cut2"].location.y = (0.4 - 5) if (24.6 <= t < 36.2) else (0.4 - 5 - 20 * (1 - seg(t, 23.8, 24.6)) if t < 24.6 else -30)
    pulses(S, t, 19.5, 23.5); pulses2 = 29.6 <= t < 30.2
    if pulses2: pulses(S, t, 29.6, 30.2)
    set_color(S["sensor_led"], (1, 0.25, 0.2) if (T_HIT <= t < 20.5 or T_HOOK <= t < 2.2) else (0.3, 0.3, 0.3))
    set_color(S["pill"], (1.0, 0.6, 0.15) if T_FIRE <= t < 34.5 else (0.4, 0.4, 0.45))
    # pliegues -> bolsa
    b = bag_state(t)
    S["bag"].scale = (max(1e-3, b),) * 3
    for o in S["folds"]: o.scale = (0.13, 0.13, 0.006) if b < 0.05 else (1e-3,) * 3
    for k, f in enumerate(S["flaps"]):
        f.rotation_euler = ((1 if k == 0 else -1) * 1.9 * min(1, b * 4), 0, 0)
    # gas de la pastilla
    for k, g in enumerate(S["gas"]):
        if T_FIRE + 0.2 <= t < T_FIRE + 4.0:
            r = random.Random(k); u = ((t - T_FIRE) * 0.9 + r.random()) % 1.0
            g.location = Vector((r.uniform(-0.05, 0.05), r.uniform(-0.05, 0.05), 0.01 + 0.09 * u)); g.scale = (1 + 2 * u,) * 3
        else: g.location = (0, 0, -9)
    # escape por los agujeros
    for k, p in enumerate(S["puffs"]):
        if 50.4 <= t < 57.6:
            r = random.Random(k); u = ((t - 50.4) * 0.8 + k / 10) % 1.0
            side = 1 if k % 2 else -1
            base = WC + 0.06 * WN + Vector((0, 0.12 * side * 0.3, 0.12))
            p.location = base + Vector((0.25 * u, 0.15 * side * u, 0.12 * u)); p.scale = (1 + 2.5 * u,) * 3
        else: p.location = (0, 0, -9)
    for k, p in enumerate(S["powder"]):
        if 58.2 <= t < 66.0:
            r = random.Random(k + 100); g = seg(t, 58.2, 59.2) * (1 - seg(t, 64.5, 66.0))
            p.location = WC + Vector((r.uniform(-0.9, 0.3), r.uniform(-0.4, 0.5), r.uniform(-0.2, 0.45))) + Vector((0, 0, 0.05 * math.sin(t + k)))
            p.scale = (max(1e-3, g),) * 3
        else: p.location = (0, 0, -9)
    # maniquí
    a = lean(t); S["torso"].rotation_euler = (0, -0.18 + a, 0)
    S["neck"].rotation_euler = (0, 0.25 * a, 0)
    sh = S["torso"].matrix_world
    bpy.context.view_layer.update()
    for k, s in enumerate((1, -1)):
        shoulder = S["torso"].matrix_world @ Vector((0.02, 0.15 * s, 0.48))
        hand = WC + Vector((0, 0.15 * s, 0.0)) + Vector((0.0, 0, 0.05))
        bar_set(S["arms"][k], shoulder - S["car"].location, hand)
    set_color(S["belt"], (1.0, 0.82, 0.15) if 65.4 <= t < 72.0 else (0.55, 0.57, 0.62))
    pos, tgt, lens = cam_state(t, CAM, drift=0.015)
    apply_cam(S["cam"], pos + jolt * 0.6, tgt, lens)

CAM = [
    (0.0, (-1.5, -5.5, 2.0), (0.6, 0.3, 0.9), 30), (3.3, (-0.6, -4.0, 1.5), (0.2, 0.4, 1.0), 32), (6.0, (-0.3, -3.6, 1.4), (0.0, 0.4, 1.0), 32),
    (9.0, (-1.0, -5.5, 1.8), (0.3, 0.3, 0.9), 30), (11.5, (1.5, -3.6, 1.0), (1.8, 0.3, 0.5), 32), (13.6, (0.6, -6.0, 1.8), (0.5, 0.3, 0.8), 30),
    (19.2, (0.4, -6.0, 1.8), (0.6, 0.3, 0.8), 30), (23.4, (0.2, -5.2, 1.6), (0.2, 0.3, 0.7), 30),
    (24.4, (0.05, -0.9, 1.2), (0.22, 0.4, 1.06), 35), (29.3, (0.0, -0.8, 1.18), (0.22, 0.4, 1.06), 38),
    (33.5, (-0.2, -1.3, 1.25), (0.15, 0.4, 1.05), 34), (39.3, (-0.6, -2.4, 1.35), (-0.05, 0.4, 1.05), 32), (42.3, (-0.6, -2.3, 1.3), (-0.05, 0.4, 1.05), 32),
    (46.4, (-0.4, -2.0, 1.35), (0.0, 0.4, 1.1), 32), (48.8, (0.6, -1.8, 1.4), (0.25, 0.4, 1.15), 34), (55.6, (0.3, -2.4, 1.45), (0.05, 0.4, 1.1), 32),
    (58.2, (-0.5, -3.0, 1.5), (-0.1, 0.4, 1.05), 30), (65.2, (-0.6, -2.9, 1.45), (-0.1, 0.4, 1.0), 30), (68.0, (-0.9, -2.4, 1.3), (-0.35, 0.4, 0.95), 32),
    (71.8, (-1.4, -5.0, 1.9), (0.3, 0.3, 0.9), 30), (80, (-1.5, -5.5, 2.0), (0.4, 0.3, 0.9), 30),
]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); c = S["car"].location
    return {"sensor": Pj(SENSOR + c), "ecu": Pj(ECU + c), "hub": Pj(WC + c), "pill": Pj(WC + 0.01 * WN + c), "bag": Pj(WC - 0.25 * WN + c + Vector((0, 0, 0.1))),
            "vents": Pj(WC + 0.05 * WN + Vector((0, 0, 0.15)) + c), "head": Pj(S["neck"].matrix_world @ Vector((0, 0, 0.13))),
            "belt": Pj(S["torso"].matrix_world @ Vector((0.02, -0.17, 0.3))), "powder": Pj(WC + Vector((-0.4, 0, 0.3)) + c), "wall": Pj(S["wall"].matrix_world.translation + Vector((0, 0, 1.0)))}

if __name__ == "__main__":
    run("airbag", build, pose, anchors)
