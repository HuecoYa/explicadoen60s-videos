# "El surtidor de gasolina" (versión diagrama grande): boquilla gigante metida en el tubo de llenado; corte por la mitad.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

CARRED = (0.93, 0.3, 0.32); METAL = (0.78, 0.8, 0.84); DARK = (0.2, 0.21, 0.24); FUEL = (1.0, 0.72, 0.18)
NOZ = (0.25, 0.68, 0.45); RUBBER = (0.25, 0.45, 0.98); YEL = (1.0, 0.88, 0.15); INNER = (0.93, 0.92, 0.9)
def P(y, z, x=0.0): return Vector((x, y, z))
M = P(0.0, 1.7); D = Vector((0, 0.894, -0.447)); N = Vector((0, 0.447, 0.894))
TIP = M + 0.62 * D; SP0 = M - 0.4 * D
HOLE = TIP - 0.12 * D - 0.052 * N; HOLE_OUT = HOLE - 0.2 * N - 0.04 * D
BODY_C = M - 0.8 * D + 0.03 * N
MEMB = M - 0.62 * D + 0.17 * N
PIV = M - 0.5 * D - 0.15 * N
PIPE_END = P(1.75, 0.82)
TANK_Y = (1.3, 3.3); TANK_Z = (0.1, 1.0)

def shell(o, th, inner=None):
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
    if inner is not None:
        o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
    return o

def cutmod(o, cutter):
    m = o.modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = cutter
    try: m.solver = 'MANIFOLD'
    except Exception: m.solver = 'EXACT'
    return o

def tube(p0, p1, r, color, th, inner=None):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(p0 + p1) / 2, vertices=40, end_fill_type='NOTHING')
    o = bpy.context.object; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    setup(o, color, smooth=True); shell(o, th, inner); return o

def obox(size, center, color, along=D):
    o = box(size, center, color); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 1, 0)).rotation_difference(along)
    return o

def build():
    sc, cam = scene_setup(world=(0.62, 0.82, 0.98))
    S = {"cam": cam}
    box((80, 80, 0.1), (0, 0, -0.05), (0.78, 0.8, 0.84))
    for k in range(-8, 9): box((80, 0.12, 0.004), (0, k * 4.0 - 2, 0.002), (0.95, 0.95, 0.95))
    pump = Vector((2.5, -3.2, 0))
    box((1.4, 0.9, 3.2), pump + Vector((0, 0, 1.6)), (0.96, 0.96, 0.97)); box((1.42, 0.92, 0.6), pump + Vector((0, 0, 3.0)), (0.95, 0.3, 0.3))
    box((1.0, 0.02, 0.6), pump + Vector((0, -0.46, 2.1)), (0.15, 0.2, 0.25))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-10, 0, 2)); cutter = bpy.context.object; cutter.scale = (20, 30, 10)
    cutter.hide_render = True; S["cutter"] = cutter
    cut = []
    panel = box((5.0, 0.12, 2.3), (1.5, 0.06, 1.25), CARRED); cut.append(panel)
    box((4.6, 0.04, 0.7), (1.5, -0.02, 2.75), (0.6, 0.82, 0.97)); box((5.0, 0.12, 0.15), (1.5, 0.06, 2.45), CARRED)
    cut.append(box((5.0, 0.12, 0.12), (1.5, 0.06, 3.15), CARRED))
    cyl(0.75, 0.4, (3.0, -0.05, 0.75), (0.13, 0.13, 0.15), rot=(math.pi / 2, 0, 0)); cyl(0.38, 0.42, (3.0, -0.05, 0.75), METAL, rot=(math.pi / 2, 0, 0))
    box((0.5, 0.05, 0.42), (0.55, -0.32, 1.7), CARRED, rot=(0, 0, -0.9))
    tank = box((1.8, TANK_Y[1] - TANK_Y[0], TANK_Z[1] - TANK_Z[0]), (0.2, sum(TANK_Y) / 2, sum(TANK_Z) / 2), (0.62, 0.64, 0.7))
    shell(tank, 0.05, (0.86, 0.87, 0.9)); cut.append(tank)
    pipe = tube(M + Vector((0, -0.06, 0.03)), PIPE_END + 0.25 * D, 0.15, (0.62, 0.64, 0.7), 0.025, (0.86, 0.87, 0.9)); cut.append(pipe)
    S["fuel"] = box((1.7, TANK_Y[1] - TANK_Y[0] - 0.1, 1.0), (0.87, sum(TANK_Y) / 2, 0.5), FUEL)
    S["fuel_pipe"] = bar_obj(FUEL, 0.125)
    spout = tube(SP0, TIP, 0.06, METAL, 0.012, (0.88, 0.89, 0.92)); cut.append(spout)
    bodyn = obox((0.36, 0.9, 0.42), BODY_C, NOZ); shell(bodyn, 0.035, (0.86, 0.95, 0.89)); cut.append(bodyn)
    grip = obox((0.24, 0.62, 0.11), M - 0.95 * D - 0.33 * N, DARK); cut.append(grip)
    rear = obox((0.24, 0.12, 0.34), M - 1.22 * D - 0.13 * N, NOZ); cut.append(rear)
    for o in cut: cutmod(o, cutter)
    ex = Vector((0.03, 0, 0))
    S["chan"] = bar_obj((0.72, 0.74, 0.78), 0.075); bar_set(S["chan"], BODY_C - 0.42 * D + ex, SP0 + ex)
    sense = [HOLE, TIP - 0.16 * D - 0.03 * N, SP0 - 0.03 * N, M - 0.62 * D, MEMB - 0.05 * N]
    S["sense_pts"] = sense; S["sense"] = []
    for a, b in zip(sense, sense[1:]):
        o = bar_obj(YEL, 0.014); bar_set(o, a + ex * 1.6, b + ex * 1.6); S["sense"].append(o)
    S["chamber"] = obox((0.02, 0.28, 0.12), MEMB + 0.03 * N, (0.18, 0.19, 0.22))
    S["memb"] = obox((0.02, 0.26, 0.025), MEMB, RUBBER)
    S["latch"] = bar_obj((0.92, 0.3, 0.3), 0.018)
    S["valve"] = obox((0.02, 0.1, 0.12), BODY_C, (0.92, 0.3, 0.3))
    trig = empty(PIV + Vector((0.05, 0, 0))); S["trig"] = trig
    tb = bar_obj(METAL, 0.03, trig); bar_set(tb, (0, 0, 0), (-0.5 * D) - 0.04 * N)
    hose_pts = [M - 1.3 * D - 0.13 * N + Vector((0.12, 0, 0)), Vector((0.3, -1.9, 1.7)), Vector((1.0, -2.6, 1.2)), Vector((1.8, -2.9, 1.6)), pump + Vector((-0.4, -0.2, 2.2))]
    for a, b in zip(hose_pts, hose_pts[1:]):
        o = bar_obj(DARK, 0.07); bar_set(o, a, b)
    S["drops"] = [sph(0.028, (0, 0, -9), FUEL, seg=12) for _ in range(30)]
    S["air"] = [sph(0.022, (0, 0, -9), (1, 1, 1), seg=12) for _ in range(10)]
    S["foam"] = [sph(random.Random(k).uniform(0.03, 0.055), (0, 0, -9), (0.99, 0.96, 0.86), seg=12) for k in range(18)]
    join_static([cam, cutter, S["fuel"], S["fuel_pipe"], S["memb"], S["latch"], S["valve"], trig, S["drops"], S["air"], S["foam"],
                 S["sense"], S["chamber"], S["chan"], cut])
    return sc, S

def along(pts, u):
    L = [(b - a).length for a, b in zip(pts, pts[1:])]; d = u * sum(L)
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l: return a.lerp(b, d / max(l, 1e-6))
        d -= l
    return pts[-1]

T_FULL = 29.4; T_HOLE = 32.6; T_CLAC = 42.78; T_VALVE = 43.45
EX = Vector((0.05, 0, 0))

def pose(t, S):
    S["cutter"].location.x = -10 - 25 * (1 - seg(t, 5.95, 6.8))
    lvl = mix(0.1, 0.8, seg(t, 0, T_FULL) ** 0.8) if t < T_FULL else 0.8
    f = S["fuel"]; f.scale.z = lvl; f.location.z = TANK_Z[0] + 0.05 + lvl / 2
    tip_reach = TIP - 0.02 * D
    if t < T_FULL: bar_set(S["fuel_pipe"], PIPE_END + EX, PIPE_END + EX + Vector((0, 0, 0.0001)))
    else:
        u = seg(t, T_FULL, T_HOLE)
        bar_set(S["fuel_pipe"], PIPE_END + 0.2 * D + EX, (PIPE_END + 0.2 * D).lerp(tip_reach, u) + EX)
    flowing = t < T_VALVE
    path = [BODY_C - 0.4 * D, SP0, TIP, TIP + 0.3 * D, PIPE_END + Vector((0, 0.15, -0.25)), PIPE_END + Vector((0, 0.6, -0.4))]
    path = [p + EX for p in path]
    for k, d in enumerate(S["drops"]):
        if not flowing and t > T_VALVE + 0.5: d.location = (0, 0, -9); continue
        u = (t * 1.5 + k / len(S["drops"])) % 1.0
        if t >= T_FULL and u > 0.55: d.location = (0, 0, -9); continue
        d.location = along(path, u)
    apath = [HOLE_OUT] + S["sense_pts"]; apath = [p + EX * 1.4 for p in apath]
    for k, a in enumerate(S["air"]):
        if 16.9 <= t < T_HOLE: a.location = along(apath, (t * 0.5 + k / len(S["air"])) % 1.0)
        else: a.location = (0, 0, -9)
    m_off = 0.06 * seg(t, 37.7, 39.6) * (1 - seg(t, 44.0, 45.0))
    S["memb"].location = MEMB - m_off * N + Vector((0.05, 0, 0))
    S["chamber"].location = MEMB + 0.03 * N + Vector((0.04, 0, 0))
    l0 = S["memb"].location - 0.02 * N + Vector((0.01, 0, 0))
    drop = 0.09 * seg(t, 40.5, 42.6)
    l1 = PIV + 0.05 * D + 0.06 * N - drop * N - 0.1 * D * seg(t, 41.6, 42.6) + Vector((0.06, 0, 0))
    bar_set(S["latch"], l0, l1)
    ang = 0.0 if t < T_CLAC else -0.3 * min(1, (t - T_CLAC) / 0.07)
    S["trig"].rotation_mode = 'AXIS_ANGLE'; S["trig"].rotation_axis_angle = (ang, 1, 0, 0)
    v = seg(t, T_VALVE, T_VALVE + 0.15)
    S["valve"].location = BODY_C - 0.2 * D + (0.17 - 0.17 * v) * N + Vector((0.06, 0, 0))
    for k, o in enumerate(S["foam"]):
        if 51.7 <= t < 54.2:
            r = random.Random(k); g = seg(t, 51.7 + r.uniform(0, 0.4), 52.3 + r.uniform(0, 0.4))
            o.location = TIP + r.uniform(-0.25, 0.1) * D + r.uniform(-0.12, 0.05) * N + Vector((0.07, 0, 0)); o.scale = (max(1e-3, g),) * 3
        else: o.location = (0, 0, -9)
    pos, tgt, lens = cam_state(t, CAM, drift=0.02)
    if T_CLAC <= t < T_CLAC + 0.5:
        k = (t - T_CLAC); pos = pos + Vector((0, math.sin(k * 90), math.cos(k * 77))) * 0.05 * (1 - k / 0.5)
    apply_cam(S["cam"], pos, tgt, lens)

def C(y, z): return (0.0, y, z)
CAM = [
    (0.0, (-6.5, -7.5, 3.4), (0.8, -0.3, 1.5), 30), (3.5, (-5.0, -5.0, 2.8), (0.3, -0.3, 1.6), 30),
    (5.8, (-5.0, -1.6, 2.2), (0, -0.2, 1.6), 30), (7.6, (-4.2, 0.4, 1.7), C(0.45, 1.45), 30),
    (9.3, (-3.2, 0.6, 1.55), C(0.75, 1.3), 30), (11.6, (-3.6, -0.1, 1.8), C(0.1, 1.7), 30), (14.4, (-3.8, -0.5, 2.0), C(-0.45, 1.95), 30),
    (16.2, (-4.6, 0.0, 1.8), C(0.15, 1.6), 30), (23.7, (-4.6, 0.05, 1.75), C(0.2, 1.55), 30), (24.4, (-3.2, 0.55, 1.5), C(0.7, 1.3), 30),
    (28.8, (-3.2, 0.55, 1.5), C(0.7, 1.3), 30), (30.2, (-5.4, 1.6, 1.4), C(1.6, 0.9), 30), (31.8, (-4.4, 1.0, 1.4), C(0.95, 1.1), 30),
    (34.6, (-3.4, 0.6, 1.45), C(0.7, 1.3), 30), (35.4, (-3.8, -0.4, 2.1), C(-0.45, 2.0), 30), (40.0, (-3.4, -0.5, 2.0), C(-0.55, 1.95), 30),
    (42.6, (-3.3, -0.55, 1.95), C(-0.6, 1.9), 30), (45.2, (-4.4, -0.2, 1.9), C(-0.1, 1.75), 30), (47.4, (-4.6, 0.1, 1.8), C(0.2, 1.6), 30),
    (51.6, (-3.2, 0.6, 1.5), C(0.75, 1.3), 30), (53.8, (-3.2, 0.6, 1.5), C(0.75, 1.3), 30), (56.0, (-4.0, 0.0, 1.8), C(0.1, 1.6), 30),
    (58.8, (-5.5, 0.4, 2.0), C(0.5, 1.4), 30), (63.0, (-6.5, -4.0, 2.8), (0.5, 0.0, 1.5), 30), (68.5, (-7.5, -8.0, 3.6), (0.8, -0.3, 1.5), 30),
    (75, (-7.6, -8.2, 3.7), (0.8, -0.3, 1.5), 30),
]

def _tight(ks, f=0.62, lo=5.0, hi=60.0):
    out = []
    for t, p, g, l in ks:
        if lo < t < hi:
            P_, G_ = Vector(p), Vector(g); p = tuple(G_ + (P_ - G_) * f)
        out.append((t, p, g, l))
    return out
CAM = _tight(CAM)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    sp = S["sense_pts"]
    return {"hole": Pj(HOLE), "hole_out": Pj(HOLE_OUT), "tip": Pj(TIP), "sp0": Pj(SP0), "tube": Pj(sp[2]), "memb": Pj(MEMB),
            "latch": Pj(PIV + 0.05 * D + 0.03 * N), "trig": Pj(PIV - 0.3 * D - 0.05 * N), "tank": Pj(Vector((0, 2.3, 0.6))),
            "valve": Pj(BODY_C - 0.2 * D), "spout_a": Pj(SP0 + 0.1 * N), "spout_b": Pj(TIP + 0.1 * N), "foam": Pj(TIP - 0.05 * D)}

if __name__ == "__main__":
    run("gasolinera", build, pose, anchors)
