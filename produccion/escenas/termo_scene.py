# "Inventa un termo": vaso con café cortado por la mitad; tres caminos del calor; doble pared, vacío, plata, tapón.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

WOOD = (1.0, 0.8, 0.58); COFFEE = (0.45, 0.26, 0.14); WALL = (0.85, 0.87, 0.92); OUTER = (0.3, 0.55, 0.95); SILVER = (0.93, 0.94, 0.97)

def shell(o, th, inner=None):
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
    if inner is not None:
        o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1

def cut(o, c):
    m = o.modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = c

def cup(r, h, color, cutter, z0=0.0, unique=True, cap=True):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(0, 0, z0 + h / 2), vertices=48, end_fill_type='NGON')
    o = bpy.context.object
    # quitar la tapa de arriba
    import bmesh
    bm = bmesh.new(); bm.from_mesh(o.data)
    top = [f for f in bm.faces if f.normal.z > 0.9]; bmesh.ops.delete(bm, geom=top, context='FACES'); bm.to_mesh(o.data); bm.free()
    setup(o, color, smooth=True, unique=unique); shell(o, 0.07); cut(o, cutter); return o

def build():
    sc, cam = scene_setup(world=(0.62, 0.82, 0.98))
    S = {"cam": cam}
    box((120, 60, 1.0), (0, 10, -0.5), WOOD)
    for k in range(-14, 15): box((120, 0.1, 0.02), (0, 10 + k * 2.4, 0.0), (0.86, 0.62, 0.4))
    rng = random.Random(5)
    for k in range(8):
        cx, cz = rng.uniform(-50, 50), rng.uniform(12, 26)
        for j in range(5): sph(rng.uniform(3, 5), (cx + j * 3.5 - 7, 60, cz), (1, 1, 1), scale=(1.3, 0.5, 0.8))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 4)); cutter = bpy.context.object; cutter.scale = (10, 10, 12); cutter.hide_render = True
    S["inner"] = cup(1.3, 5.6, WALL, cutter, 0.3)
    S["outer"] = cup(1.75, 6.0, OUTER, cutter, 0.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.22, depth=1.0, location=(0, 0, 0.9), vertices=48); cof = bpy.context.object; setup(cof, COFFEE, unique=True); cut(cof, cutter)
    S["coffee"] = cof
    S["ice"] = [box((0.5, 0.5, 0.5), (0, 0, -9), (0.85, 0.95, 1.0)) for _ in range(4)]
    S["cap"] = cyl(1.12, 1.0, (0, 0, -9), (0.85, 0.6, 0.35))
    S["gap"] = [sph(0.06, (0, 0, -9), (1, 1, 1)) for _ in range(30)]
    S["rays"] = [box((0.5, 0.06, 0.06), (0, 0, -9), (1.0, 0.45, 0.2)) for _ in range(14)]
    S["steam"] = [sph(0.22, (0, 0, -9), (0.98, 0.98, 1.0)) for _ in range(10)]
    S["cold"] = [sph(0.18, (0, 0, -9), (0.55, 0.78, 1.0)) for _ in range(6)]
    join_static([cam, cutter, S["inner"], S["outer"], cof, S["ice"], S["cap"], S["gap"], S["rays"], S["steam"], S["cold"]])
    return sc, S

def pose(t, S):
    outer_s = seg(t, 27.2, 28.2)
    S["outer"].scale = (max(1e-3, outer_s),) * 3
    S["inner"].active_material.diffuse_color = (*lin(tuple(mix(a, b, seg(t, 9.9, 11.4) * (1 - seg(t, 25.9, 26.6))) for a, b in zip(WALL, (1.0, 0.5, 0.25)))), 1)
    if t >= 44.4: S["inner"].active_material.diffuse_color = (*lin(tuple(mix(a, b, seg(t, 44.4, 45.4)) for a, b in zip(WALL, SILVER))), 1)
    lvl = 4.2; S["coffee"].scale.z = lvl; S["coffee"].location.z = 0.4 + lvl / 2
    cold = seg(t, 65.6, 66.6)
    S["coffee"].active_material.diffuse_color = (*lin(tuple(mix(a, b, cold) for a, b in zip(COFFEE, (0.55, 0.78, 1.0)))), 1)
    for k, ic in enumerate(S["ice"]):
        ic.location = Vector((-0.5 + (k % 2) * 0.8, 0.3 + (k // 2) * 0.3, 4.3 + 0.1 * math.sin(t * 2 + k))) if cold > 0.5 else Vector((0, 0, -9))
        ic.rotation_euler = (0.3 * k, 0.5, 0.2 * k)
    # aire entre paredes: aparece 32, se va 35.7-37.4
    for k, g in enumerate(S["gap"]):
        r = random.Random(k)
        if 32.0 <= t < 37.6:
            ang = r.uniform(0.05, math.pi - 0.05); z = r.uniform(0.3, 5.8)
            out = seg(t, 35.7, 37.4); rr = 1.52 + 0.05 * math.sin(t * 7 + k)
            g.location = Vector((rr * math.cos(ang), rr * math.sin(ang), z + out * (7.5 - z) + 0.05 * math.sin(t * 9 + k))); g.scale = (max(1e-3, 1 - out * 0.9),) * 3
        else: g.location = (0, 0, -9)
    # radiación: rayos que salen (y rebotan con la plata)
    for k, ry in enumerate(S["rays"]):
        r = random.Random(k + 50); ang = r.uniform(-1.2, 1.2) + (math.pi if k % 2 else 0); z = r.uniform(1.0, 4.0)
        if 20.3 <= t < 26.0 or 42.9 <= t < 50.8:
            u = (t * 0.9 + k / 14) % 1.0
            dist = 1.3 + 3.5 * u
            if t >= 44.4: dist = 1.3 + 0.35 * (1 - abs(2 * u - 1))
            ry.location = Vector((dist * math.cos(ang), -0.05, z))
        else: ry.location = (0, 0, -9)
    # convección / escape por arriba
    for k, s in enumerate(S["steam"]):
        r = random.Random(k + 7)
        if (0.0 <= t < 8.0) or (14.0 <= t < 19.2) or (52.8 <= t < 57.2):
            u = (t * 0.5 + k / 10) % 1.0; s.location = Vector((r.uniform(-0.8, 0.8) + 0.3 * math.sin(t + k), r.uniform(-0.3, 0.3), 6.2 + 4.0 * u)); s.scale = (1 + u,) * 3
        else: s.location = (0, 0, -9)
    for k, c in enumerate(S["cold"]):
        if 17.5 <= t < 19.4:
            u = ((t - 17.5) * 0.6 + k / 6) % 1.0; side = 1 if k % 2 else -1
            c.location = Vector((side * (2.6 - 1.2 * u), 0, 8.5 - 3.5 * u))
        else: c.location = (0, 0, -9)
    cp = seg(t, 56.3, 57.2)
    S["cap"].location = Vector((0, 0, 6.2 + 3.0 * (1 - cp))) if t >= 56.3 else Vector((0, 0, -9))
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.04))

def V(z, d=14, h=2.0, x=0.0, lens=32): return ((x, -d, z + h), (x * 0.3, 0, z), lens)
CAM = [(0.0,) + V(4.0, 16), (4.5,) + V(3.6, 14), (8.2,) + V(3.0, 9, 1.0, 1.5), (13.9,) + V(4.5, 13, 2.0), (19.4,) + V(3.5, 14),
       (25.9,) + V(3.5, 15), (31.9,) + V(3.5, 9, 1.0, 1.2), (37.4,) + V(4.5, 10, 2.0, 1.0), (42.6,) + V(3.5, 13), (51.0,) + V(5.5, 12, 2.5),
       (58.8,) + V(4.5, 15, 3.0), (65.4,) + V(4.0, 13, 3.0), (69.8,) + V(4.0, 16, 3.0), (85,) + V(4.0, 16, 3.0)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"wall": Pj((-1.3, 0, 3.0)), "air": Pj((0, 0, 7.5)), "rays": Pj((2.8, 0, 2.5)), "gap": Pj((-1.52, 0.2, 4.5)), "top": Pj((0, 0, 6.5)),
            "cap": Pj((0, 0, 7.2)), "cup": Pj((0, 0, 3.0))}

if __name__ == "__main__":
    run("termo", build, pose, anchors)
