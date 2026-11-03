# "Inventa un mechero": sobre una mesa se va montando pieza a pieza (rueda, piedra, depósito, válvula, regulador, chimenea, muelle, piezoeléctrico).
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

WOOD = (1.0, 0.8, 0.58); STEEL = (0.75, 0.77, 0.82); RED = (0.95, 0.32, 0.32); BUT = (0.55, 0.8, 1.0)
NOZ = Vector((-0.6, 0, 6.55)); WHEEL = Vector((0.6, 0, 6.85)); FLAME = Vector((-0.6, 0, 7.5))

def shell(o, th, inner=None):
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
    if inner is not None:
        o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1

def build():
    sc, cam = scene_setup(world=(0.62, 0.82, 0.98))
    S = {"cam": cam}
    box((120, 60, 1.0), (0, 10, -0.5), WOOD)
    for k in range(-14, 15): box((120, 0.1, 0.02), (0, 10 + k * 2.4, 0.0), (0.86, 0.62, 0.4))
    rng = random.Random(5)
    for k in range(8):
        cx, cz = rng.uniform(-50, 50), rng.uniform(12, 26)
        for j in range(5): sph(rng.uniform(3, 5), (cx + j * 3.5 - 7, 60, cz), (1, 1, 1), scale=(1.3, 0.5, 0.8))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 3)); cutter = bpy.context.object; cutter.scale = (10, 10, 12); cutter.hide_render = True
    parts = {}
    # depósito (cortado por delante)
    tank = empty(); parts["tank"] = tank
    tb = box((3.0, 1.4, 6.0), (0, 0, 3.0), RED, tank); shell(tb, 0.12, (0.95, 0.88, 0.86))
    m = tb.modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = cutter
    S["liquid"] = box((2.7, 1.1, 1.0), (0, 0.06, 0.6), BUT, tank)
    S["balloon"] = sph(3.5, (0, 0.2, 9.5), (0.7, 0.88, 1.0))
    # rueda y piedra con muelle
    wheel = empty(WHEEL); parts["wheel"] = wheel; S["wheel"] = wheel
    cyl(0.55, 0.5, (0, 0, 0), STEEL, wheel, rot=(math.pi / 2, 0, 0), v=24, smooth=False)
    for k in range(16):
        a = k / 16 * 2 * math.pi; box((0.08, 0.52, 0.08), (0.56 * math.cos(a), 0, 0.56 * math.sin(a)), (0.6, 0.62, 0.66), wheel)
    flint = empty(); parts["flint"] = flint
    cyl(0.18, 0.35, WHEEL + Vector((0, 0, -0.75)), (0.45, 0.45, 0.48), flint)
    for k in range(6): torus(0.16, 0.025, WHEEL + Vector((0, 0, -1.0 - k * 0.1)), STEEL, flint)
    # válvula, botón (palanca), regulador, muelle del botón
    valve = empty(); parts["valve"] = valve
    cyl(0.16, 0.5, NOZ + Vector((0, 0, -0.2)), STEEL, valve)
    lever = empty(Vector((1.2, 0, 6.35))); parts["lever"] = lever; S["lever"] = lever
    box((2.4, 1.0, 0.25), (-1.2, 0, 0), (0.25, 0.26, 0.3), lever)
    S["spring"] = empty(Vector((-0.6, 0, 6.05))); parts["spring"] = S["spring"]
    for k in range(5): torus(0.3, 0.04, (0, 0, -0.08 * k), STEEL, S["spring"])
    reg = empty(Vector((-0.6, -0.78, 5.6))); parts["reg"] = reg; S["reg"] = reg
    cyl(0.32, 0.18, (0, 0, 0), (0.95, 0.75, 0.25), reg, rot=(math.pi / 2, 0, 0), v=12, smooth=False)
    # chimenea con agujeros
    chim = empty(); parts["chim"] = chim
    for (sx, sy, dx, dy) in ((3.0, 0.06, 0, 0.75), (3.0, 0.06, 0, -0.75), (0.06, 1.5, 1.5, 0), (0.06, 1.5, -1.5, 0)):
        box((sx, sy, 1.9), (dx, dy, 7.0), STEEL, chim)
    for k in range(3):
        for j in range(2): cyl(0.13, 0.08, (-1.0 + k * 0.5, -0.78, 7.2 + j * 0.5), (0.2, 0.2, 0.22), chim, rot=(math.pi / 2, 0, 0))
    # cristal piezoeléctrico
    piezo = empty(Vector((-2.6, 0, 6.8))); parts["piezo"] = piezo
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, segments=4, ring_count=2, location=(0, 0, 0)); cr = bpy.context.object; setup(cr, (0.98, 0.55, 0.85), piezo)
    S["hammer"] = box((0.5, 0.5, 0.5), (0, 0, 1.0), STEEL, piezo)
    S["parts"] = parts
    # efectos
    S["sparks"] = [sph(0.06, (0, 0, -9), (1.0, 0.65, 0.15)) for _ in range(16)]
    S["gas"] = [sph(0.09, (0, 0, -9), BUT) for _ in range(12)]
    S["flame"] = empty(FLAME); sph(0.45, (0, 0, 0.1), (1.0, 0.55, 0.15), S["flame"], scale=(1, 1, 1.9)); sph(0.28, (0, -0.15, -0.05), (1.0, 0.92, 0.4), S["flame"], scale=(1, 1, 1.6))
    S["wind"] = [bar_obj((1, 1, 1), 0.035) for _ in range(5)]
    S["bolt"] = [bar_obj((0.5, 0.8, 1.0), 0.05) for _ in range(4)]
    join_static([cam, cutter, list(parts.values()), S["liquid"], S["balloon"], S["sparks"], S["gas"], S["flame"], S["wind"], S["bolt"]])
    return sc, S

APPEAR = {"wheel": 3.6, "flint": 5.3, "tank": 17.7, "valve": 33.8, "lever": 34.6, "reg": 48.4, "chim": 54.2, "spring": 58.3, "piezo": 63.1}

def pose(t, S):
    P = S["parts"]
    for k, a in APPEAR.items():
        u = seg(t, a, a + 0.5); b = 1 + 0.2 * math.sin(min(1, max(0, (t - a - 0.5) / 0.3)) * math.pi)
        sc = max(1e-3, u * b)
        if k in ("wheel", "flint") and t >= 63.1: sc = max(1e-3, 1 - seg(t, 63.1, 63.6))
        if k == "piezo" and t < 63.1: sc = 1e-3
        if t < 2.3 and k not in ("piezo", "spring"): sc = max(1e-3, 1 - seg(t, 1.9, 2.3))
        P[k].scale = (sc,) * 3
    # rueda gira
    spin = 0.0
    for a, b in ((5.3, 8.1), (8.4, 14.9), (40.9, 41.6), (54.6, 55.3)):
        if t >= a: spin += min(t, b) - a
    S["wheel"].rotation_euler = (0, -spin * 9, 0)
    # chispas
    bursts = [(8.4, 14.9)] + [(41.0, 41.6), (54.7, 55.2)]
    for k, s in enumerate(S["sparks"]):
        s.location = (0, 0, -9)
        for a, b in bursts:
            if a <= t < b:
                r = random.Random(k); u = ((t - a) * 1.6 + r.random()) % 1.0
                s.location = WHEEL + Vector((-0.3, 0, -0.3)) + Vector((-1.6 * u * r.uniform(0.4, 1), r.uniform(-0.4, 0.4) * u, 1.2 * u - 1.4 * u * u))
                s.scale = (1 - u + 0.1,) * 3
    # depósito: líquido y globo de gas
    bal = seg(t, 20.4, 21.4) * (1 - seg(t, 23.8, 25.3))
    S["balloon"].scale = (max(1e-3, bal),) * 3
    lvl = 0.3 + 4.3 * seg(t, 23.8, 26.3)
    S["liquid"].scale.z = lvl if t >= 17.7 else (4.6 if t < 2.3 else 1e-3); S["liquid"].location.z = 0.15 + lvl / 2
    # gas que se escapa (sin válvula) o sale al pulsar
    leak = 30.3 <= t < 34.0
    press = (37.8 <= t < 62.7) and not (52.5 <= t < 54.6)
    for k, g in enumerate(S["gas"]):
        if leak or (press and t < 44.5):
            u = (t * 1.2 + k / 12) % 1.0; g.location = NOZ + Vector((0.2 * math.sin(k * 3 + t * 4) * u, 0, 0.3 + 1.6 * u)); g.scale = (1 + 2 * u,) * 3
        else: g.location = (0, 0, -9)
    # palanca y muelle
    down = 0.25 if press else 0.0
    S["lever"].rotation_euler = (0, -0.18 * (down / 0.25), 0)
    S["spring"].scale.z = (1 - 0.45 * down / 0.25) * S["spring"].scale.x
    # llama
    f = 0.0
    if 44.4 <= t < 52.5: f = 1.0 + 0.9 * seg(t, 45.2, 45.8) * (1 - seg(t, 49.5, 51.8))
    if 52.5 <= t < 53.4: f = 1.0 * (1 - seg(t, 52.8, 53.4))
    if 55.3 <= t < 59.6: f = 1.0
    if 68.3 <= t < 72.6: f = 1.0
    if t < 1.95: f = 1.0
    fl = 1 + 0.07 * math.sin(t * 23)
    S["flame"].scale = (max(1e-3, f * fl), max(1e-3, f), max(1e-3, f * fl))
    bend = 0.6 * seg(t, 52.5, 53.0) if 52.5 <= t < 54.2 else 0.0
    S["flame"].rotation_euler = (0, -bend, 0)
    S["reg"].rotation_euler = (0, 6.0 * seg(t, 49.0, 51.8), 0)
    for k, w in enumerate(S["wind"]):
        if 52.5 <= t < 58.0:
            u = (t * 1.3 + k / 5) % 1.0; y = 7.0 + k * 0.35
            bar_set(w, Vector((5.0 - 9.0 * u, -0.4, y)), Vector((3.8 - 9.0 * u, -0.4, y)))
        else: bar_set(w, Vector((0, 0, -9)), Vector((0, 0, -9.01)))
    # piezo: martillo golpea y rayo azul
    S["hammer"].location.z = 1.0 - 0.45 * (seg(t, 65.6, 65.8) - seg(t, 66.6, 67.2)) - 0.45 * (seg(t, 67.4, 67.55) - seg(t, 68.4, 68.9))
    hit = (65.8 <= t < 66.4) or (67.55 <= t < 68.6)
    pts = [Vector((-2.6, -0.1, 7.1)), Vector((-2.0, -0.1, 7.5)), Vector((-1.6, -0.1, 7.1)), Vector((-1.1, -0.1, 7.6)), NOZ + Vector((0, -0.1, 0.4))]
    for k, b in enumerate(S["bolt"]):
        if hit: bar_set(b, pts[k] + Vector((0, 0, 0.05 * math.sin(t * 60 + k))), pts[k + 1])
        else: bar_set(b, Vector((0, 0, -9)), Vector((0, 0, -9.01)))
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.05))

def V(z, d=13, h=0.0, x=0.0, lens=32): return ((x, -d * 0.62, z + h * 0.7), (x * 0.2, 0, z), lens)
CAM = [(0.0,) + V(5.0, 14, 2), (2.0,) + V(5.0, 16, 2.5), (3.4,) + V(6.5, 9, 1.5, 1.5), (8.2,) + V(6.6, 7, 1.0, 2.0), (14.9,) + V(6.8, 7.5, 1.0, 1.0),
       (17.6,) + V(4.0, 15, 3), (20.3,) + V(6.0, 24, 4), (24.0,) + V(5.0, 18, 3), (29.9,) + V(4.5, 15, 3),
       (30.3,) + V(6.5, 9, 1.5, -1.0), (37.6,) + V(6.5, 9, 1.0, -1.0), (44.2,) + V(6.8, 10, 1.0, 0.5), (48.2,) + V(6.5, 12, 1.5),
       (49.0, (-4, -7.5, 6.5), (-0.6, -0.5, 5.8), 32), (52.2, (-4, -8.0, 6.8), (-0.6, -0.5, 6.0), 32), (52.6,) + V(6.8, 12, 1.5, 2.0),
       (58.2,) + V(6.8, 12, 1.5, 0.0), (62.7,) + V(6.3, 10, 1.0, -1.0), (63.4, (-1.8, -7.2, 7.8), (-1.3, 0, 6.8), 32), (69.8, (-1.6, -7.4, 7.8), (-1.1, 0, 6.8), 32),
       (72.6,) + V(4.5, 22, 4), (85,) + V(4.5, 22, 4)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"wheel": Pj(WHEEL), "flint": Pj(WHEEL + Vector((0, 0, -0.8))), "tank": Pj((0, 0, 3.0)), "liquid": Pj((0, 0, 1.5)), "valve": Pj(NOZ),
            "lever": Pj((0, 0, 6.4)), "reg": Pj((-0.6, -0.8, 5.6)), "chim": Pj((0, -0.8, 7.9)), "spring": Pj((-0.6, 0, 5.9)), "flame": Pj(FLAME + Vector((0, 0, 0.6))),
            "piezo": Pj((-2.6, 0, 6.8)), "balloon": Pj((0, 0, 9.5))}

if __name__ == "__main__":
    run("mechero", build, pose, anchors)
