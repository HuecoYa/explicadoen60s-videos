# "Inventa una escalera mecánica": vista lateral; cinta -> escalones en cadena -> dos raíles -> peine -> pasamanos -> sensores.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

A30 = math.radians(30); DS = 0.8; NST = 30
STEEL = (0.75, 0.77, 0.82); TREAD = (0.35, 0.37, 0.42); YEL = (1.0, 0.82, 0.2); DARK = (0.16, 0.17, 0.2)
X0, X1 = -5.0, 5.0; ZT = (X1 - X0) * math.tan(A30)
# recorrido cerrado de la referencia del escalón (en x,z)
TOP = [(-9.0, 0.0), (X0, 0.0), (X1, ZT), (9.0, ZT)]
BOT = [(9.0, ZT - 1.4), (X1, ZT - 1.4), (X0, -1.4), (-9.0, -1.4)]
def loop_pts():
    pts = [Vector((x, 0, z)) for x, z in TOP]
    for k in range(1, 12):     # media vuelta arriba
        a = math.pi / 2 - math.pi * k / 12; pts.append(Vector((9.0 + 0.7 * math.cos(a), 0, ZT - 0.7 + 0.7 * math.sin(a))))
    pts += [Vector((x, 0, z)) for x, z in BOT]
    for k in range(1, 12):
        a = -math.pi / 2 - math.pi * k / 12; pts.append(Vector((-9.0 + 0.7 * math.cos(a), 0, -0.7 + 0.7 * math.sin(a))))
    pts.append(pts[0]); return pts
PTS = loop_pts(); SEGL = [(b - a).length for a, b in zip(PTS, PTS[1:])]; TOT = sum(SEGL); NST = int(TOT / DS)

def at(s):
    s %= TOT
    for (a, b), l in zip(zip(PTS, PTS[1:]), SEGL):
        if s <= l: return a.lerp(b, s / l), (b - a).normalized()
        s -= l
    return PTS[0], Vector((1, 0, 0))

def build():
    sc, cam = scene_setup(world=(0.85, 0.9, 0.97))
    S = {"cam": cam}
    box((80, 40, 0.2), (0, 0, -3.2), (0.88, 0.86, 0.84)); box((80, 0.3, 30), (0, 6, 10), (0.78, 0.86, 0.95))
    # suelos de los rellanos y armazón (fondo)
    box((6, 2.2, 0.3), (-12.4, 0, -0.1), (0.85, 0.85, 0.87)); box((6, 2.2, 0.3), (12.4, 0, ZT - 0.1), (0.85, 0.85, 0.87))
    box((24, 0.1, 9), (0, 1.3, ZT / 2 - 1.5), (0.82, 0.84, 0.88))
    # cinta inicial
    S["belt"] = bar_obj((0.25, 0.26, 0.3), 1.0); bar_set(S["belt"], Vector((X0 - 3, 0, 0.0)), Vector((X1 + 3, 0, 0.0)))
    S["ball"] = sph(0.35, (0, 0, -9), (0.95, 0.4, 0.4))
    steps = []
    for k in range(NST):
        e = empty();
        box((DS * 1.02, 1.6, 0.08), (-DS / 2, 0, 0), TREAD, e)                       # pisada (ref = borde delantero)
        box((0.06, 1.6, DS * math.sin(A30) + 0.05), (0.0, 0, -DS * math.sin(A30) / 2 - 0.02), (0.45, 0.47, 0.52), e)
        grooves = empty((0, 0, 0), e)
        for j in range(5): box((DS * 0.95, 0.04, 0.02), (-DS / 2, -0.6 + j * 0.3, 0.05), (0.1, 0.1, 0.12), grooves)
        cyl(0.13, 0.12, (-0.1, -0.9, -0.5), YEL, e, rot=(math.pi / 2, 0, 0)); cyl(0.13, 0.12, (-0.7, -0.9, -0.5), (0.3, 0.75, 1.0), e, rot=(math.pi / 2, 0, 0))
        steps.append((e, grooves))
    S["steps"] = steps
    # raíles (amarillo = ruedas delanteras, azul = traseras), solo el tramo de arriba
    for off, col in ((Vector((-0.1, -0.9, -0.63)), YEL), (Vector((-0.7, -0.9, -0.63)), (0.3, 0.75, 1.0))):
        prev = None
        for x, z in TOP:
            p = Vector((x, 0, z)) + off
            if prev is not None: o = bar_obj(col, 0.05); bar_set(o, prev, p)
            prev = p
    S["chain"] = [bar_obj(DARK, 0.04) for _ in range(NST)]
    # pasamanos
    S["hand"] = []
    for (a, b) in zip(TOP, TOP[1:]):
        o = bar_obj((0.12, 0.12, 0.14), 0.12); bar_set(o, Vector((a[0], -0.8, a[1] + 1.6)), Vector((b[0], -0.8, b[1] + 1.6))); S["hand"].append(o)
    S["marks"] = [sph(0.13, (0, 0, -9), (1, 0.85, 0.2)) for _ in range(8)]
    # peine, cordón, sensores, motor
    comb = empty(Vector((X1 + 2.2, 0, ZT + 0.02))); S["comb"] = comb
    box((0.6, 1.7, 0.08), (0.3, 0, 0.0), YEL, comb)
    for j in range(9): box((0.35, 0.05, 0.03), (-0.1, -0.7 + j * 0.175, 0.0), YEL, comb)
    S["lace"] = bar_obj((1.0, 0.3, 0.3), 0.04)
    S["shoe"] = box((0.7, 0.35, 0.3), (0, 0, -9), (0.3, 0.45, 0.95))
    S["sensor"] = sph(0.12, Vector((X1 + 2.8, -0.9, ZT + 0.25)), (0.3, 0.3, 0.3), unique=True)
    motor = empty(Vector((7.5, 0, ZT - 2.3))); S["motor"] = motor
    cyl(0.6, 1.0, (0, 0, 0), (0.45, 0.6, 0.45), motor, rot=(math.pi / 2, 0, 0)); box((0.15, 1.1, 0.6), (0, 0, 0), DARK, motor)
    join_static([cam, S["belt"], S["ball"], [s for s, g in steps], S["chain"], S["hand"], S["marks"], comb, S["lace"], S["shoe"], S["sensor"], motor])
    return sc, S

V = 0.9
def travel(t):
    if t < 66.3: return V * t
    return V * 66.3 + V * 0.25 * (1 - math.exp(-(t - 66.3) * 4))

def pose(t, S):
    # cinta inclinada al principio, la bola resbala
    belt_on = t < 11.2
    if belt_on: bar_set(S["belt"], Vector((X0, -0.0, -0.15)), Vector((X1, 0.0, ZT - 0.15)))
    else: bar_set(S["belt"], Vector((0, 0, -9)), Vector((0, 0, -9.01)))
    S["belt"].scale = (1.0, 0.8, S["belt"].scale.z) if belt_on else S["belt"].scale
    if 8.3 <= t < 11.0:
        u = (t - 8.3) / 2.7; x = 2.5 - 6.0 * u * u; S["ball"].location = Vector((x, 0, (x - X0) * math.tan(A30) + 0.25))
    else: S["ball"].location = (0, 0, -9)
    d = travel(t); show = seg(t, 11.0, 12.6)
    tilt_k = seg(t, 16.6, 17.4) * (1 - seg(t, 20.9, 21.8))
    for k, (e, gr) in enumerate(S["steps"]):
        p, tang = at(d + k * DS * 1.0)
        ang = math.atan2(tang.z, tang.x)
        upside = p.z < -0.75 + (0 if p.x > -9 else 0) and abs(tang.x) > 0.5 and tang.x < 0
        rot = 0.0
        if tang.x < -0.5: rot = math.pi
        elif abs(tang.x) <= 0.5: rot = math.pi / 2 if tang.z < 0 else -math.pi / 2
        if tang.x > 0.5: rot = -ang * tilt_k
        e.location = p; e.rotation_euler = (0, rot, 0); e.scale = (max(1e-3, show),) * 3
        gr.scale = (1, 1, 1) if t >= 47.2 else (1e-3,) * 3
        q, _ = at(d + (k + 1) * DS); bar_set(S["chain"][k], p + Vector((-0.1, -0.9, -0.5)), q + Vector((-0.1, -0.9, -0.5)))
        if show < 0.01: bar_set(S["chain"][k], Vector((0, 0, -9)), Vector((0, 0, -9.01)))
    # pasamanos: marcas que avanzan a la misma velocidad
    hv = 1.0 if t >= 59.2 else 0.0
    for k, m in enumerate(S["marks"]):
        if t < 57.3: m.location = (0, 0, -9); continue
        s = (d * (1.0 if t >= 59.2 else 0.6) + k * 2.6) % 21.5
        xs = [TOP[0], TOP[1], TOP[2], TOP[3]]; segs = [(Vector((a[0], -0.8, a[1] + 1.75)), Vector((b[0], -0.8, b[1] + 1.75))) for a, b in zip(xs, xs[1:])]
        for a, b in segs:
            l = (b - a).length
            if s <= l: m.location = a.lerp(b, s / l); break
            s -= l
    # cordón atrapado
    if 43.0 <= t < 47.0:
        sp = Vector((X1 + 1.2 + 0.6 * seg(t, 43.0, 45.5), -0.1, ZT + 0.2)); S["shoe"].location = sp
        bar_set(S["lace"], sp + Vector((0.3, -0.1, 0.0)), sp + Vector((0.9, -0.1, -0.25 * seg(t, 44.5, 46.0))))
    else:
        S["shoe"].location = (0, 0, -9); bar_set(S["lace"], Vector((0, 0, -9)), Vector((0, 0, -9.01)))
    S["comb"].scale = (max(1e-3, seg(t, 49.6, 50.2)),) * 3
    set_color(S["sensor"], (1, 0.25, 0.2) if t >= 65.9 else (0.3, 0.3, 0.3))
    S["motor"].rotation_euler = (0, -d * 2, 0)
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.05))

def C(x, z, d=17, lens=30, h=1.5): return ((x, -d, z + h), (x, 0, z), lens)
CAM = [(0.0,) + C(0, 2.5, 26), (4.6,) + C(0, 2.5, 22), (8.4,) + C(-1.0, 1.5, 15), (11.0,) + C(0, 2.5, 22), (16.0,) + C(0.0, 2.8, 20),
       (20.9,) + C(-1.5, 1.0, 9), (26.8,) + C(-1.0, 1.4, 8), (28.2,) + C(0, 2.6, 14), (32.0,) + C(-5.5, 0.0, 9), (34.5,) + C(5.5, ZT, 9),
       (38.9,) + C(0.0, 1.5, 22), (42.0,) + C(6.6, ZT, 7), (46.9,) + C(6.8, ZT, 6), (53.7,) + C(7.0, ZT, 6.5), (57.3,) + C(1.0, 3.5, 16),
       (62.9,) + C(3.0, 4.5, 14), (64.9,) + C(7.6, ZT, 8), (68.9,) + C(7.4, ZT, 8.5), (71.6,) + C(0, 2.5, 26), (85,) + C(0, 2.5, 26)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"rails": Pj(Vector((0, -0.9, ZT / 2 - 0.63))), "flat": Pj(Vector((-6.5, 0, 0.3))), "comb": Pj(Vector((X1 + 2.4, 0, ZT + 0.2))),
            "hand": Pj(Vector((0, -0.8, ZT / 2 + 1.8))), "sensor": Pj(Vector((X1 + 2.8, -0.9, ZT + 0.3))), "lace": Pj(Vector((X1 + 2.0, 0, ZT + 0.3))),
            "wheels": Pj(Vector((-1.5, -0.9, (X0 * 0 - 1.5 - X0) * math.tan(A30) - 0.5))), "chain": Pj(Vector((2.0, -0.9, (2.0 - X0) * math.tan(A30) - 0.5)))}

if __name__ == "__main__":
    run("escalera", build, pose, anchors)
