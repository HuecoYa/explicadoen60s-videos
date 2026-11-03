# "El semáforo que te ve": cruce, espira bajo el asfalto (la tapa se levanta), campo magnético, caja y semáforo.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

ASF = (0.32, 0.33, 0.37); COPPER = (0.95, 0.52, 0.22); DARK = (0.15, 0.16, 0.19)
LOOP = Vector((-2.2, -0.9, 0)); POLE = Vector((0.6, -2.4, 0)); BOXP = Vector((1.4, -2.6, 0))

def car(color, scale=1.0):
    e = empty((0, 0, -20))
    box((2.0, 1.0, 0.45), (0, 0, 0.45), color, e); box((1.1, 0.9, 0.4), (-0.15, 0, 0.85), color, e)
    box((1.12, 0.92, 0.25), (-0.15, 0, 0.86), (0.6, 0.82, 0.97), e)
    for x in (-0.65, 0.65):
        for y in (-0.5, 0.5): cyl(0.22, 0.14, (x, y, 0.22), (0.12, 0.12, 0.14), e, rot=(math.pi / 2, 0, 0))
    e.scale = (scale,) * 3; return e

def bike():
    e = empty((0, 0, -20))
    for x in (-0.55, 0.55): cyl(0.28, 0.08, (x, 0, 0.28), (0.12, 0.12, 0.14), e, rot=(math.pi / 2, 0, 0))
    o = bar_obj((0.95, 0.5, 0.15), 0.05, e); bar_set(o, (-0.55, 0, 0.3), (0.45, 0, 0.7))
    box((0.5, 0.2, 0.12), (-0.1, 0, 0.62), DARK, e); sph(0.14, (0.0, 0, 1.25), (0.95, 0.95, 0.97), e); box((0.2, 0.25, 0.45), (-0.1, 0, 0.9), (0.3, 0.5, 0.9), e)
    return e

def build():
    sc, cam = scene_setup(world=(0.62, 0.82, 0.98))
    S = {"cam": cam}
    box((120, 120, 0.1), (0, 0, -0.06), (0.55, 0.78, 0.45))
    x0, x1, y0, y1 = LOOP.x - 1.6, LOOP.x + 1.6, LOOP.y - 1.3, LOOP.y + 1.3
    box((x0 + 60, 7, 0.02), ((x0 - 60) / 2, 0, 0.0), ASF); box((60 - x1, 7, 0.02), ((x1 + 60) / 2, 0, 0.0), ASF)
    box((x1 - x0, y0 + 3.5, 0.02), (LOOP.x, (y0 - 3.5) / 2, 0.0), ASF); box((x1 - x0, 3.5 - y1, 0.02), (LOOP.x, (y1 + 3.5) / 2, 0.0), ASF)
    box((7, 120, 0.019), (3.5, 0, -0.001), ASF)
    box((0.3, 3.2, 0.005), (-0.3, -1.6, 0.012), (1, 1, 1))
    for k in range(-20, 6): box((1.5, 0.15, 0.005), (k * 3.0 - 4, 0.0, 0.012), (1, 1, 1)) if (k * 3.0 - 4 < -4.6) else None
    box((120, 1.5, 0.15), (0, -4.25, 0.07), (0.85, 0.85, 0.87)); box((120, 1.5, 0.15), (0, 4.25, 0.07), (0.85, 0.85, 0.87))
    # hueco bajo la tapa y espira de cobre
    box((3.2, 2.6, 0.05), LOOP + Vector((0, 0, -0.03)), (0.55, 0.42, 0.3))
    loops = []
    for k in range(4):
        w, h = 2.9 - k * 0.12, 2.3 - k * 0.12
        for (sx, sy, dx, dy) in ((w, 0.05, 0, h / 2), (w, 0.05, 0, -h / 2), (0.05, h, w / 2, 0), (0.05, h, -w / 2, 0)):
            loops.append(box((sx, sy, 0.03), LOOP + Vector((dx, dy, -0.012)), COPPER))
    lid = empty(LOOP + Vector((1.6, 0, 0))); S["lid"] = lid
    box((3.18, 2.58, 0.06), (-1.6, 0, -0.02), ASF, lid)
    for (sx, sy, dx, dy) in ((3.0, 0.06, 0, 1.2), (3.0, 0.06, 0, -1.2), (0.06, 2.4, 1.5, 0), (0.06, 2.4, -1.5, 0)):
        box((sx, sy, 0.006), (dx - 1.6, dy, 0.013), (0.12, 0.12, 0.14), lid)
    # semáforo y caja
    cyl(0.09, 4.0, POLE + Vector((0, 0, 2.0)), DARK); box((0.4, 0.4, 1.2), POLE + Vector((-0.1, 0, 3.6)), DARK)
    S["lights"] = [sph(0.14, POLE + Vector((-0.31, 0, 4.0 - k * 0.38)), (0.25, 0.25, 0.25), unique=True) for k in range(3)]
    S["cam_icon"] = box((0.35, 0.2, 0.2), POLE + Vector((-0.35, 0, 4.45)), (0.85, 0.87, 0.9))
    box((0.6, 0.45, 1.1), BOXP + Vector((0, 0, 0.55)), (0.55, 0.6, 0.55)); S["led"] = sph(0.06, BOXP + Vector((-0.31, 0, 0.9)), (0.3, 0.3, 0.3), unique=True)
    S["wire"] = [LOOP + Vector((1.45, -1.15, 0.0)), Vector((0.8, -2.4, 0.02)), BOXP + Vector((0, 0, 0.1))]
    for a, b in zip(S["wire"], S["wire"][1:]):
        o = bar_obj(COPPER, 0.03); bar_set(o, a, b)
    S["pulses"] = [sph(0.06, (0, 0, -9), (1, 1, 0.6)) for _ in range(5)]
    S["rings"] = [torus(1.0, 0.025, LOOP, (0.45, 0.78, 1.0), unique=True) for _ in range(4)]
    S["c1"] = car((0.95, 0.35, 0.35)); S["c2"] = car((0.35, 0.6, 0.95)); S["c3"] = car((0.98, 0.8, 0.3)); S["bike"] = bike()
    join_static([cam, lid, S["lights"], S["led"], S["pulses"], S["rings"], S["c1"], S["c2"], S["c3"], S["bike"], S["cam_icon"]])
    return sc, S

STOP = Vector((-2.2, -0.9, 0))
def pose(t, S):
    # coche 1: llega y el semáforo se pone verde (gancho); luego se va
    c1 = keyed(t, [(0, Vector((-18, -0.9, 0))), (2.0, STOP), (3.4, STOP), (5.5, Vector((25, -0.9, 0))), (21.0, Vector((-18, -0.9, 0))), (23.3, STOP),
                   (33.0, STOP), (35.0, Vector((25, -0.9, 0))), (90, Vector((25, -0.9, 0)))])
    if 5.5 <= t < 21.0: c1 = Vector((0, 0, -20))
    S["c1"].location = c1
    S["c2"].location = keyed(t, [(33.6, Vector((-22, -0.9, 0))), (36.2, Vector((25, -0.9, 0)))]) if 33.6 <= t < 36.3 else \
        (keyed(t, [(37.3, Vector((-18, -0.9, 0))), (39.0, Vector((-5.6, -0.9, 0))), (99, Vector((-5.6, -0.9, 0)))]) if 37.3 <= t < 42.2 else Vector((0, 0, -20)))
    S["c3"].location = keyed(t, [(34.4, Vector((-22, -0.9, 0))), (37.0, Vector((25, -0.9, 0)))]) if 34.4 <= t < 37.1 else Vector((0, 0, -20))
    S["bike"].location = keyed(t, [(42.3, Vector((-18, -0.9, 0))), (44.0, STOP), (99, STOP)]) if 42.3 <= t < 48.2 else Vector((0, 0, -20))
    # semáforo: 0 rojo, 1 ámbar, 2 verde
    state = 0
    if 2.1 <= t < 5.6 or 31.6 <= t < 37.2: state = 2
    for k, l in enumerate(S["lights"]):
        on = (k == 0 and state == 0) or (k == 2 and state == 2)
        set_color(l, [(1, 0.2, 0.2), (1, 0.75, 0.2), (0.3, 1, 0.4)][k] if on else (0.22, 0.22, 0.24))
    S["lid"].rotation_euler = (0, 1.35 * (seg(t, 11.7, 12.6) - seg(t, 55.0, 55.8)), 0)
    car_on = (22.9 <= t < 33.5) or (0.9 <= t < 3.6)
    bike_on = 43.6 <= t < 48.2
    act = 16.7 <= t < 55.0
    for k, r in enumerate(S["rings"]):
        if not act: r.location = (0, 0, -9); continue
        ph = (t * 0.45 + k / 4) % 1.0
        wob = 0.25 * math.sin(t * 9 + k) if car_on else (0.05 * math.sin(t * 9 + k) if bike_on else 0)
        r.location = LOOP + Vector((0, 0, 0.05 + 1.6 * ph)); r.scale = (1.45 * (1 + 0.5 * ph) + wob, 1.15 * (1 + 0.5 * ph) - wob, 1)
        set_color(r, (1.0, 0.6, 0.2) if car_on and 23.5 <= t else (0.45, 0.78, 1.0))
    sig = (26.7 <= t < 31.3)
    pts = S["wire"]
    for k, p in enumerate(S["pulses"]):
        if not (sig or 16.7 <= t < 21.4): p.location = (0, 0, -9); continue
        u = (t * 0.7 + k / 5) % 1.0; p.location = pts[0].lerp(pts[1], u * 2) if u < 0.5 else pts[1].lerp(pts[2], (u - 0.5) * 2)
    set_color(S["led"], (0.3, 1, 0.4) if (27.5 <= t < 33.5) else (0.3, 0.3, 0.3))
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.04))

CAM = [(0.0, (-9, -9, 4.5), (-1.5, -0.5, 1.2), 30), (3.4, (-6, -7.5, 3.5), (-1, -1, 1.0), 30), (5.6, (-4.0, -4.6, 2.2), (-2.0, -0.9, 0), 32),
       (8.4, (-3.8, -4.4, 3.0), (-2.2, -0.9, 0), 32), (11.6, (-3.5, -4.6, 3.6), (-2.2, -0.9, 0), 32), (16.0, (-3.0, -4.2, 2.5), (-2.2, -0.9, -0.05), 34),
       (21.4, (-4.5, -5.4, 2.8), (-2.2, -0.9, 0.4), 32), (26.4, (-4.0, -5.0, 2.6), (-2.2, -0.9, 0.5), 32), (27.5, (-0.6, -6.0, 2.4), (0.7, -2.4, 1.0), 32),
       (31.2, (-0.8, -6.2, 2.8), (0.5, -2.4, 2.4), 32), (31.6, (-2.0, -7.5, 3.6), (0.2, -1.6, 3.0), 30), (37.2, (-6.0, -8.0, 3.8), (-2.5, -0.9, 0.6), 30),
       (42.0, (-6.2, -7.8, 3.6), (-3.0, -0.9, 0.6), 30), (44.0, (-4.2, -5.2, 2.4), (-2.2, -0.9, 0.5), 32), (48.0, (-4.0, -5.0, 2.3), (-2.2, -0.9, 0.5), 32),
       (48.6, (-1.0, -5.0, 4.8), (0.3, -2.4, 4.3), 32), (50.6, (-1.2, -5.2, 4.6), (0.3, -2.4, 4.2), 32), (55.4, (-5, -7, 3.2), (-2.2, -0.9, 0.2), 30),
       (60.0, (-9, -10, 5), (-1.5, -0.5, 1.0), 30), (75, (-10, -11, 5.5), (-1.5, -0.5, 1.0), 30)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"loop": Pj(LOOP), "rect": Pj(LOOP + Vector((0, -1.2, 0))), "box": Pj(BOXP + Vector((0, 0, 1.2))), "light": Pj(POLE + Vector((-0.3, 0, 4.0))),
            "camicon": Pj(POLE + Vector((-0.35, 0, 4.45))), "field": Pj(LOOP + Vector((0, 0, 1.2))), "car2": Pj(Vector((-5.6, -0.9, 1.2)))}

if __name__ == "__main__":
    run("semaforo", build, pose, anchors)
