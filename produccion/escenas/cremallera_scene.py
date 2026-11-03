# "Inventa la cremallera": una chaqueta abierta sobre la mesa; ganchos -> dientes -> cursor en Y -> topes.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

NR = 40; SP = 0.25; MAXO = 0.75
BRASS = (0.92, 0.74, 0.32); TAPE = (0.2, 0.22, 0.3); JACK = (0.92, 0.32, 0.36); WOOD = (1.0, 0.8, 0.58)
def yk(k, side): return k * SP + (SP / 2 if side > 0 else 0)

def build():
    sc, cam = scene_setup(world=(0.62, 0.82, 0.98))
    S = {"cam": cam}
    box((80, 60, 1.0), (0, 8, -0.55), WOOD)
    for k in range(-12, 13): box((0.08, 60, 0.02), (k * 2.2, 8, -0.04), (0.86, 0.62, 0.4))
    rng = random.Random(5)
    for k in range(8):
        cx, cz = rng.uniform(-40, 40), rng.uniform(10, 22)
        for j in range(5): sph(rng.uniform(2.5, 4), (cx + j * 3 - 6, 55, cz), (1, 1, 1), scale=(1.3, 0.5, 0.8))
    rows = []
    for k in range(NR):
        R = {}
        for side in (-1, 1):
            y = yk(k, side)
            e = empty((0, y, 0)); R[side] = e
            box((0.6, SP * 1.02, 0.04), (side * 0.42, 0, 0.0), TAPE, e)
            box((3.0, SP * 1.02, 0.06), (side * 2.2, 0, 0.0), JACK, e)
            tooth = empty((side * 0.06, 0, 0.03), e)
            box((0.24, 0.13, 0.08), (0, 0, 0), BRASS, tooth); sph(0.035, (-side * 0.05, 0, 0.045), (0.98, 0.82, 0.4), tooth)
            R["t%d" % side] = tooth
            if k % 4 == 1:
                hk = empty((0, 0, 0.03), e); R["h%d" % side] = hk
                if side < 0:
                    o = bar_obj((0.75, 0.77, 0.82), 0.02, hk); bar_set(o, (-0.15, 0, 0), (0.12, 0, 0))
                    o = bar_obj((0.75, 0.77, 0.82), 0.02, hk); bar_set(o, (0.12, 0, 0), (0.12, 0, 0.06))
                else:
                    torus(0.06, 0.018, (0.06, 0, 0.0), (0.75, 0.77, 0.82), hk)
        rows.append(R)
    S["rows"] = rows
    # topes
    S["stops"] = [box((0.2, 0.12, 0.12), (s * 0.12, yk(NR - 1, s) + 0.1, 0.06), (0.75, 0.77, 0.82)) for s in (-1, 1)]
    S["bstop"] = box((0.5, 0.18, 0.14), (0, -0.1, 0.07), (0.75, 0.77, 0.82))
    # cursor en Y
    sl = empty(); S["slider"] = sl
    for s in (-1, 1):
        box((0.06, 0.7, 0.16), (s * 0.3, 0, 0.09), (0.8, 0.82, 0.86), sl)
    box((0.66, 0.7, 0.03), (0, 0, 0.01), (0.8, 0.82, 0.86), sl)
    for s in (-1, 1):
        o = bar_obj((0.95, 0.35, 0.3), 0.03, sl); bar_set(o, (s * 0.25, 0.35, 0.09), (s * 0.06, -0.05, 0.09))
    wedge = box((0.12, 0.22, 0.14), (0, 0.22, 0.09), (0.95, 0.35, 0.3), sl)
    lid = empty((0, 0.35, 0.18), sl); S["lid"] = lid
    box((0.66, 0.7, 0.04), (0, -0.35, 0), (0.8, 0.82, 0.86), lid)
    tab = box((0.22, 0.5, 0.04), (0, -0.55, 0.05), (0.8, 0.82, 0.86), lid)
    join_static([cam, rows, S["stops"], S["bstop"], sl])
    return sc, S

def offsets(t):
    """apertura de cada fila (0 = cerrada)"""
    o = []
    yc = slider_y(t)
    for k in range(NR):
        y = k * SP
        if t < 5.3: v = MAXO
        elif t < 9.25: v = MAXO * (1 - seg(t, 5.3 + k * 0.08, 5.6 + k * 0.08))
        elif t < 13.1:
            r = random.Random(k).random()
            v = 0.05 * math.sin(t * 12 + k) * seg(t, 9.25, 10.0)
            if r < 0.45: v = max(v, MAXO * 0.7 * seg(t, 10.8 + r * 3, 11.2 + r * 3))
        elif t < 21.37: v = MAXO * 0.75
        elif t < 25.5: v = MAXO * 0.75 * (1 - seg(t, 21.37 + k * 0.05, 21.7 + k * 0.05))
        elif t < 29.0: v = MAXO * 0.75 * seg(t, 25.5, 25.9) * (1 - seg(t, 26.4 + k * 0.22, 26.6 + k * 0.22))
        elif t < 51.1 or t >= 58.0:
            v = 0.0 if y < yc - 0.1 else min(MAXO, 0.08 + (y - yc) * 0.22)
            if 47.75 <= t < 51.1 and yc > NR * SP: v = 0.0
        else:
            v = MAXO * seg(t, 51.2 + (NR - k) * 0.01, 52.4)
            if t >= 55.6: v = v * (1 - seg(t, 55.6, 56.4)) if k < 2 else v
        o.append(v)
    return o

def slider_y(t):
    if t < 29.0: return -3.0
    return keyed(t, [(29.0, -1.0), (31.2, 0.2), (38.0, 0.2), (43.6, 7.0), (45.0, 7.0), (47.4, 3.0), (47.8, 3.0), (49.6, NR * SP + 0.3),
                     (50.8, NR * SP + 3.0), (58.0, -1.0), (59.0, 0.2), (64.5, NR * SP - 0.55), (90, NR * SP - 0.55)])

def pose(t, S):
    off = offsets(t)
    teeth_s = seg(t, 13.1, 14.6); hook_s = 1 - seg(t, 13.1, 13.9)
    for k, R in enumerate(S["rows"]):
        for side in (-1, 1):
            R[side].location.x = side * off[k]
            R["t%d" % side].scale = (max(1e-3, teeth_s),) * 3
            if "h%d" % side in R: R["h%d" % side].scale = (max(1e-3, hook_s),) * 3
    yc = slider_y(t)
    sl = S["slider"]
    if 50.8 <= t < 58.0 or t < 29.0:
        sl.location = (0, -30, 0)
    else:
        sl.location = (0, yc + 0.2, 0.0)
        if 49.6 <= t < 50.8: sl.location = (0.6 * seg(t, 49.6, 50.8), yc, 0.5 * seg(t, 49.6, 50.8))
    sl.scale = (max(1e-3, seg(t, 29.0, 29.6)),) * 3 if t < 50 else (max(1e-3, seg(t, 58.0, 58.6)),) * 3 if t >= 58 else (1, 1, 1)
    S["lid"].rotation_euler = (1.6 * (seg(t, 32.4, 33.0) - seg(t, 37.4, 38.0)), 0, 0)
    for o in S["stops"]: o.scale = (max(1e-3, seg(t, 53.8, 54.3)),) * 3
    S["bstop"].scale = (max(1e-3, seg(t, 55.7, 56.2)),) * 3
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.03))

def F(y, d=7.0, h=7.5, lens=30, tx=0.0):
    return ((tx, y - d, h), (tx, y + 1.0, 0.0), lens)
CAM = [(0.0,) + F(5, 12, 13), (4.2,) + F(5, 11, 12), (5.3,) + F(3.0, 6, 6.5), (9.2,) + F(4.5, 6.5, 7), (12.8,) + F(5, 8, 8.5),
       (15.7, (1.4, 0.0, 1.8), (0.0, 2.2, 0.05), 34), (19.0, (1.2, 0.3, 1.6), (0.0, 2.4, 0.05), 34),
       (21.3,) + F(4, 6.5, 7), (25.0,) + F(4, 6.5, 7), (26.3,) + F(1.5, 4.5, 4.5), (28.7,) + F(2.2, 4.5, 4.5),
       (31.2, (1.6, -2.4, 2.6), (0.0, 0.3, 0.1), 34), (37.5, (1.4, -2.2, 2.4), (0.0, 0.4, 0.1), 34),
       (40.0,) + F(3.5, 5.5, 5.5), (43.6,) + F(6.5, 5.5, 5.5), (47.4,) + F(3.5, 5.5, 5.5), (50.8,) + F(8.5, 6, 6.5),
       (53.4,) + F(3.0, 8, 8.5), (54.3, (2.6, 5.4, 3.6), (0.0, 9.4, 0.1), 32), (55.5, (2.4, 5.6, 3.4), (0.0, 9.4, 0.1), 32),
       (56.6, (2.6, -3.8, 3.6), (0.0, 0.6, 0.1), 32), (57.7, (2.4, -3.6, 3.4), (0.0, 0.6, 0.1), 32),
       (60.0,) + F(1.0, 6, 6.5), (64.5,) + F(8.5, 6.5, 7), (68.6,) + F(5, 13, 14), (80,) + F(5, 13, 14)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); yc = slider_y(t)
    return {"slider": Pj((0, yc + 0.2, 0.2)), "tooth": Pj((-0.06, 2.0 * 1.0, 0.1)), "hook": Pj((0, 2.25, 0.1)), "stops": Pj((0, NR * SP, 0.1)),
            "bstop": Pj((0, -0.1, 0.1)), "zip": Pj((0, 5, 0.1)), "y": Pj((0, yc + 0.2, 0.25))}

if __name__ == "__main__":
    run("cremallera", build, pose, anchors)
