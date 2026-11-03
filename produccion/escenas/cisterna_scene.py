# "La cisterna del váter": váter con la cisterna cortada; tapón, boya, grifo, rebosadero, fuga, colorante, doble botón.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

WHITE = (0.96, 0.96, 0.97); WATER = (0.55, 0.8, 1.0); DYE = (0.25, 0.35, 0.95); PLAS = (0.95, 0.55, 0.25); GREY = (0.7, 0.72, 0.76)
TZ0, TZ1 = 3.1, 5.0; VALVE = Vector((0.4, 0.3, 3.12)); FILL = Vector((-1.05, 0.3, 4.45))

def build():
    sc, cam = scene_setup(world=(0.7, 0.88, 0.85))
    S = {"cam": cam}
    box((40, 40, 0.1), (0, 0, -0.05), (0.92, 0.88, 0.8))
    for k in range(-20, 21): box((0.03, 40, 0.004), (k * 1.0, 0, 0.002), (0.8, 0.76, 0.7)); box((40, 0.03, 0.004), (0, k * 1.0, 0.002), (0.8, 0.76, 0.7))
    box((40, 0.2, 14), (0, 1.0, 7), (0.62, 0.86, 0.8))
    for k in range(-20, 21): box((0.03, 0.02, 14), (k * 1.0, 0.89, 7), (1, 1, 1))
    for k in range(0, 14): box((40, 0.02, 0.03), (0, 0.89, k * 1.0), (1, 1, 1))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 3)); cutter = bpy.context.object; cutter.scale = (10, 10, 12); cutter.hide_render = True
    S["cutter"] = cutter
    def cutobj(o, inner=(0.88, 0.9, 0.93)):
        m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = 0.08; m.offset = -1
        o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
    tank = box((3.0, 1.0, 2.0), (0, 0.4, 4.0), WHITE); cutobj(tank); S["tank"] = tank
    box((3.15, 1.15, 0.15), (0, 0.4, 5.08), WHITE)
    S["btn_small"] = cyl(0.18, 0.12, (-0.2, 0.4, 5.2), GREY, unique=True); S["btn_big"] = cyl(0.3, 0.12, (0.4, 0.4, 5.2), GREY, unique=True)
    # váter (taza)
    bowl = cyl(1.3, 1.6, (0, -0.4, 1.4), WHITE, v=48); bowl.scale = (1, 1.25, 1); cutobj(bowl); S["bowl"] = bowl
    cyl(0.8, 1.0, (0, -0.4, 0.5), WHITE, v=32)
    box((2.8, 3.3, 0.12), (0, -0.4, 2.25), (0.95, 0.95, 0.96))
    S["bowlw"] = cyl(0.95, 0.2, (0, -0.2, 1.3), WATER, unique=True); S["bowlw"].scale = (1, 1.2, 1)
    cyl(0.18, 1.0, (0.4, 0.3, 2.7), WHITE)
    # agua de la cisterna
    S["water"] = box((2.84, 0.5, 1.0), (0, 0.62, 4.0), WATER, unique=True)
    # rebosadero y tapón
    cyl(0.12, 1.5, (0.4, 0.3, 3.9), (0.85, 0.87, 0.9))
    S["plug"] = cyl(0.3, 0.1, VALVE, (0.25, 0.25, 0.28)); S["rod"] = bar_obj(GREY, 0.03)
    # grifo de llenado y boya
    cyl(0.1, 1.35, (FILL.x, FILL.y, (TZ0 + FILL.z) / 2), GREY); cyl(0.22, 0.3, FILL, PLAS)
    S["arm"] = bar_obj(GREY, 0.035); S["float"] = sph(0.32, (0, 0, -9), PLAS)
    S["spray"] = [sph(0.05, (0, 0, -9), WATER) for _ in range(10)]
    S["flow"] = [sph(0.09, (0, 0, -9), WATER) for _ in range(16)]
    S["leak"] = [sph(0.05, (0, 0, -9), WATER) for _ in range(8)]
    S["drops"] = [sph(0.08, (0, 0, -9), DYE) for _ in range(4)]
    join_static([cam, cutter, S["tank"], S["bowl"], S["btn_small"], S["btn_big"], S["bowlw"], S["water"], S["plug"], S["rod"], S["arm"], S["float"], S["spray"], S["flow"], S["leak"], S["drops"]])
    return sc, S

def level(t):
    full = 4.45
    v = keyed(t, [(0, full), (7.1, full), (10.6, 3.2), (17.6, 3.2), (24.4, full), (30.2, full), (33.0, 4.9), (35.6, 4.9), (37.0, full),
                  (59.2, full), (60.3, 3.85), (61.5, full), (61.9, full), (63.6, 3.2), (66.0, full), (99, full)])
    return v

def pose(t, S):
    S["cutter"].location.y = -4.67 - 20 * (1 - seg(t, 4.7, 5.5))
    L = level(t); w = S["water"]; w.scale.z = L - TZ0; w.location.z = TZ0 + (L - TZ0) / 2
    dye = seg(t, 51.8, 53.5)
    set_color(w, tuple(mix(a, b, dye) for a, b in zip(WATER, DYE)))
    set_color(S["bowlw"], tuple(mix(a, b, seg(t, 56.2, 57.8)) for a, b in zip(WATER, DYE)))
    # botones
    big = (5.7 <= t < 6.6) or (61.9 <= t < 62.6); small = 59.2 <= t < 59.9
    S["btn_big"].location.z = 5.2 - (0.08 if big else 0); S["btn_small"].location.z = 5.2 - (0.08 if small else 0)
    set_color(S["btn_big"], (1, 0.82, 0.2) if 61.9 <= t < 64.2 else GREY); set_color(S["btn_small"], (1, 0.82, 0.2) if 59.2 <= t < 61.6 else GREY)
    # tapón: se levanta al descargar
    lift = max(seg(t, 6.0, 6.5) * (1 - seg(t, 10.4, 10.9)), seg(t, 59.5, 59.8) * (1 - seg(t, 60.2, 60.5)), seg(t, 62.2, 62.5) * (1 - seg(t, 63.4, 63.8)))
    leakplug = 39.3 <= t < 50.4
    S["plug"].location = VALVE + Vector((0, 0, 0.5 * lift + (0.04 if leakplug else 0))); S["plug"].rotation_euler = (0, 0.15 if leakplug else 0, 0)
    bar_set(S["rod"], S["plug"].location, Vector((0.4, 0.3, 5.1)))
    # boya: brazo desde el grifo hasta la superficie
    mis = 0.35 if 39.3 <= t < 50.4 else 0.0
    fz = max(TZ0 + 0.3, L + 0.05 - mis)
    dx = -math.sqrt(max(0.01, 1.4 ** 2 - (FILL.z - fz) ** 2))
    fpos = Vector((FILL.x - dx, FILL.y, fz)); S["float"].location = fpos; bar_set(S["arm"], FILL, fpos)
    # chorro del grifo
    filling = (17.2 <= t < 24.4) or (40.0 <= t < 50.4) or (60.4 <= t < 61.5) or (63.7 <= t < 66.0)
    for k, s in enumerate(S["spray"]):
        if filling:
            u = (t * 2 + k / 10) % 1.0; s.location = FILL + Vector((0.15 + 0.4 * u, -0.05, 0.1 - 1.2 * u * u))
        else: s.location = (0, 0, -9)
    # descarga hacia la taza
    flushing = (6.4 <= t < 10.8) or (59.6 <= t < 60.4) or (62.4 <= t < 63.7)
    for k, f in enumerate(S["flow"]):
        if flushing:
            u = (t * 1.5 + k / 16) % 1.0; f.location = Vector((0.4, 0.3, 3.0 - 1.5 * u)) if u < 0.6 else Vector((0.4 - 1.0 * (u - 0.6) / 0.4, 0.0 - 0.6 * (u - 0.6), 1.9 - 0.4 * (u - 0.6) / 0.4))
        else: f.location = (0, 0, -9)
    # fuga silenciosa (por el rebosadero y el tapón)
    overflow = (33.0 <= t < 35.8) or (41.0 <= t < 50.4)
    for k, l in enumerate(S["leak"]):
        if overflow or leakplug:
            u = (t * 0.9 + k / 8) % 1.0
            l.location = Vector((0.4, 0.25, 4.6 - 1.7 * u)) if (overflow and k % 2 == 0) else Vector((0.4 + 0.25, 0.25, 3.1 - 0.4 * u))
            if not leakplug and k % 2: l.location = (0, 0, -9)
        else: l.location = (0, 0, -9)
    for k, d in enumerate(S["drops"]):
        if 51.4 <= t < 52.4 + k * 0.2:
            u = min(1, (t - 51.4 - k * 0.2) / 0.6); d.location = Vector((-0.5 + k * 0.3, 0.3, 6.2 - (6.2 - L) * max(0, u) * max(0, u)))
        else: d.location = (0, 0, -9)
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.03))

def V(x, z, d=7.5, h=1.0, lens=32): return ((x, -d, z + h), (x, 0.2, z), lens)
CAM = [(0.0,) + V(0, 3.0, 12, 1.5), (4.4,) + V(0, 3.4, 10, 1.2), (5.6,) + V(0, 4.0, 7.5), (10.8,) + V(0.2, 3.4, 8.5, 0.6), (12.0,) + V(-0.6, 4.0, 6.5),
       (16.4,) + V(-0.8, 4.2, 5.5), (19.9,) + V(-0.6, 4.0, 6.5), (25.5,) + V(0, 4.0, 8), (29.4,) + V(0.4, 4.3, 5.5), (37.2,) + V(0.3, 4.2, 6.5),
       (43.0,) + V(0.2, 3.8, 6.0), (50.6,) + V(0, 4.3, 7.5), (54.8,) + V(0, 3.0, 10, 1.5), (58.8,) + V(0, 2.8, 10.5, 1.5), (59.2,) + V(0.1, 4.6, 6.5, 1.2),
       (64.2,) + V(0, 3.5, 9, 1.2), (65.5,) + V(0, 3.0, 12, 1.5), (80,) + V(0, 3.0, 12, 1.5)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"float": Pj(S["float"].location), "plug": Pj(S["plug"].location), "fill": Pj(FILL), "overflow": Pj((0.4, 0.3, 4.7)), "bowl": Pj((0, -0.3, 1.6)),
            "small": Pj((-0.2, 0.4, 5.3)), "big": Pj((0.4, 0.4, 5.3)), "tank": Pj((0, 0.4, 4.0))}

if __name__ == "__main__":
    run("cisterna", build, pose, anchors)
