# "La máquina expendedora": máquina cortada de lado; la moneda pasa tamaño, peso (rampa) y metal (bobinas); trampilla.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

BODY = (0.95, 0.35, 0.35); INNER = (0.92, 0.92, 0.9); METAL = (0.78, 0.8, 0.84); COPPER = (0.95, 0.52, 0.22); DARK = (0.18, 0.19, 0.22)
GOLD = (0.98, 0.8, 0.35); SILV = (0.85, 0.86, 0.9)
YM = 0.12   # plano del mecanismo
def P(x, z, y=YM): return Vector((x, y, z))
SLOT = P(-1.25, 1.78); IN1 = P(-0.86, 1.78); GAUGE = P(-0.72, 1.74); RAMP0 = P(-0.6, 1.6); RAMP1 = P(0.05, 1.36)
COIL = P(-0.2, 1.47); GATE = P(0.13, 1.12); CASH = P(-0.35, 0.42); DROP = P(0.13, 0.75); TRAY = P(-1.08, 0.62)
R_COIN = 0.06

def shell(o, th, inner=None):
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
    if inner is not None:
        o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
    return o

def coin(kind):
    e = empty((0, 0, -9))
    rot = (math.pi / 2, 0, 0)
    if kind == "euro":
        cyl(R_COIN, 0.016, (0, 0, 0), SILV, e, rot=rot); cyl(R_COIN * 0.68, 0.02, (0, 0, 0), GOLD, e, rot=rot)
    elif kind == "washer":
        torus(R_COIN * 0.75, R_COIN * 0.28, (0, 0, 0), (0.6, 0.62, 0.66), e, rot=rot)
    elif kind == "foreign":
        cyl(R_COIN * 0.9, 0.02, (0, 0, 0), (0.85, 0.45, 0.3), e, rot=rot); cyl(R_COIN * 0.5, 0.024, (0, 0, 0), (0.75, 0.38, 0.25), e, rot=rot)
    elif kind == "choco":
        cyl(R_COIN * 1.05, 0.03, (0, 0, 0), (1.0, 0.85, 0.3), e, rot=rot); cyl(R_COIN * 0.7, 0.034, (0, 0, 0), (0.95, 0.75, 0.25), e, rot=rot)
    return e

def build():
    sc, cam = scene_setup(world=(0.75, 0.88, 0.98))
    S = {"cam": cam}
    box((60, 60, 0.1), (0, 0, -0.05), (0.9, 0.82, 0.7))
    for k in range(-20, 21): box((0.02, 60, 0.003), (k * 0.6, 0, 0.002), (0.8, 0.7, 0.58))
    box((60, 0.2, 8), (0, 4, 4), (0.62, 0.86, 0.76))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5, 2)); cutter = bpy.context.object; cutter.scale = (10, 10, 8); cutter.hide_render = True
    S["cutter"] = cutter
    body = box((2.4, 1.3, 3.3), (0, 0.55, 1.65), BODY); shell(body, 0.06, INNER)
    m = body.modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = cutter
    try: m.solver = 'MANIFOLD'
    except Exception: pass
    # frente (cara -x): cristal con productos, ranura, bandeja
    box((0.02, 1.0, 1.5), (-1.21, 0.55, 2.35), (0.6, 0.85, 0.98))
    for r in range(3):
        for c in range(3):
            box((0.1, 0.22, 0.3), (-1.0, 0.25 + c * 0.3, 1.8 + r * 0.45), [(0.3, 0.7, 0.95), (0.98, 0.8, 0.25), (0.4, 0.85, 0.45)][(r + c) % 3])
    box((0.04, 0.22, 0.3), (-1.21, 0.15, 1.78), DARK); box((0.05, 0.03, 0.14), (-1.235, 0.12, 1.78), (0.05, 0.05, 0.05))
    box((0.2, 0.3, 0.16), (-1.15, 0.12, 0.58), DARK)
    # mecanismo (placa de fondo y piezas)
    box((1.5, 0.02, 1.7), (-0.35, YM + 0.06, 1.25), (0.85, 0.87, 0.9))
    gauge = empty(GAUGE); box((0.03, 0.06, 0.2), (0, 0, 0.14), METAL, gauge); box((0.03, 0.06, 0.2), (0, 0, -0.14), METAL, gauge)
    ramp = bar_obj(METAL, 0.012); bar_set(ramp, RAMP0 - Vector((0, 0, R_COIN + 0.012)), RAMP1 - Vector((0, 0, R_COIN + 0.012)))
    for dy in (-0.07, 0.07):
        c = cyl(0.11, 0.05, COIL + Vector((0, dy, 0.0)), COPPER, rot=(math.pi / 2, 0, 0)); cyl(0.05, 0.06, COIL + Vector((0, dy, 0)), DARK, rot=(math.pi / 2, 0, 0))
    S["rings"] = [torus(0.12, 0.008, COIL + Vector((0, 0.0, 0)), (0.45, 0.78, 1.0), rot=(math.pi / 2, 0, 0)) for _ in range(3)]
    gate = empty(GATE); S["gate"] = gate
    o = bar_obj((0.95, 0.35, 0.3), 0.014, gate); bar_set(o, (0, 0, 0), (-0.22, 0, -0.18))
    # canales
    for a, b in ((P(0.0, 1.05), P(-0.35, 0.55)), (P(0.25, 1.05), P(0.25, 0.75)), (P(0.25, 0.75), P(-1.0, 0.62)), (P(0.02, 0.9), P(0.02, 0.75))):
        o = bar_obj((0.6, 0.62, 0.68), 0.01); bar_set(o, a, b)
    box((0.42, 0.24, 0.02), CASH - Vector((0, 0, 0.12)), METAL); box((0.02, 0.24, 0.26), CASH + Vector((-0.21, 0, 0.0)), METAL); box((0.02, 0.24, 0.26), CASH + Vector((0.21, 0, 0.0)), METAL)
    S["pile"] = [cyl(R_COIN, 0.016, CASH + Vector((random.Random(k).uniform(-0.12, 0.12), random.Random(k + 5).uniform(-0.05, 0.05), -0.1 + 0.017 * k)), GOLD) for k in range(6)]
    S["coins"] = {k: coin(k) for k in ("euro", "washer", "foreign", "choco", "intro")}
    join_static([cam, cutter, body, gate, S["rings"], list(S["coins"].values())])
    return sc, S

def path_accept(): return [SLOT, IN1, GAUGE, RAMP0, RAMP1, P(0.12, 1.25), GATE + Vector((-0.04, 0, -0.06)), P(-0.18, 0.7), CASH]
def path_reject(): return [SLOT, IN1, GAUGE, RAMP0, RAMP1, P(0.13, 1.25), P(0.16, 0.95), DROP, P(-0.6, 0.66), TRAY]

def along(pts, u):
    L = [(b - a).length for a, b in zip(pts, pts[1:])]; d = max(0, min(1, u)) * sum(L)
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l: return a.lerp(b, d / max(l, 1e-6))
        d -= l
    return pts[-1]

# tramos (t, u) a lo largo del recorrido aceptado para la moneda de 1 €
EURO_U = [(6.0, 0.0), (8.5, 0.12), (10.0, 0.16), (16.0, 0.2), (17.6, 0.24), (23.4, 0.43), (27.3, 0.47), (43.5, 0.47), (47.4, 0.52), (49.1, 0.62), (51.9, 1.0), (99, 1.0)]

def pose(t, S):
    S["cutter"].location.y = -5 - 20 * (1 - seg(t, 5.1, 5.9))
    C = S["coins"]
    for c in C.values(): c.location = (0, 0, -9)
    # gancho inicial: moneda falsa que entra y vuelve
    if 1.8 <= t < 4.7:
        u = seg(t, 1.8, 3.3); C["intro"].location = along(path_reject(), u); C["intro"].rotation_euler = (0, -u * 25, 0)
    # moneda de 1 €
    if 5.8 <= t:
        u = keyed(t, EURO_U); C["euro"].location = along(path_accept(), u); C["euro"].rotation_euler = (0, -u * 30, 0)
    # 36.8-43.6: la moneda se acerca a cámara para enseñar los dos metales
    if 36.8 <= t < 43.6:
        k = seg(t, 36.9, 37.6) * (1 - seg(t, 42.9, 43.5))
        C["euro"].location = C["euro"].location + Vector((0, -0.25 * k, 0.05 * k)); C["euro"].scale = (1 + 1.2 * k,) * 3
    else: C["euro"].scale = (1, 1, 1)
    # rechazos
    for name, a, b in (("washer", 52.3, 58.9), ("foreign", 59.3, 62.6), ("choco", 60.9, 64.4)):
        if a <= t < b + 3: C[name].location = along(path_reject(), seg(t, a, b)); C[name].rotation_euler = (0, -seg(t, a, b) * 30, 0)
    if 59.34 <= t < 62.0 and C["washer"].location.z > -5: pass
    # trampilla: se abre para la buena
    S["gate"].rotation_euler = (0, -0.9 * (seg(t, 48.9, 49.3) - seg(t, 51.8, 52.2)), 0)
    # anillos del campo magnético
    act = 27.2 <= t < 47.5
    for k, r in enumerate(S["rings"]):
        if not act: r.location = (0, 0, -9); continue
        ph = (t * 0.8 + k / 3) % 1.0
        r.location = COIL + Vector((0, -0.03 - 0.12 * ph, 0)); r.scale = (1 + 1.4 * ph,) * 3
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.01))

def V(x, z, d=1.6, lens=32, dx=0.0, dz=0.0): return ((x + dx, YM - d, z + dz), (x, YM, z), lens)
CAM = [(0.0, (-4.2, -1.6, 2.2), (-1.0, 0.4, 1.7), 30), (2.0, (-3.0, -0.8, 1.9), (-1.2, 0.2, 1.7), 32), (4.6, (-2.8, -0.9, 1.9), (-1.2, 0.2, 1.4), 30),
       (6.0,) + V(-0.4, 1.4, 2.6), (8.6,) + V(-0.8, 1.7, 1.4), (16.0,) + V(-0.72, 1.72, 1.1), (17.6,) + V(-0.4, 1.55, 1.4),
       (23.4,) + V(-0.15, 1.45, 1.4), (27.0,) + V(-0.2, 1.42, 1.6), (36.6,) + V(-0.2, 1.42, 1.7), (37.6,) + V(-0.2, 1.45, 1.3),
       (43.5,) + V(-0.2, 1.45, 1.5), (47.5,) + V(-0.1, 1.2, 1.7), (52.0,) + V(-0.25, 0.8, 1.8), (55.0,) + V(-0.3, 1.1, 2.2),
       (59.0,) + V(-0.4, 1.1, 2.4), (64.6,) + V(-0.4, 1.2, 2.6), (68.0, (-4.4, -2.2, 2.4), (-0.6, 0.3, 1.5), 30), (80, (-4.6, -2.4, 2.5), (-0.6, 0.3, 1.5), 30)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    eu = S["coins"]["euro"].matrix_world.translation
    return {"gauge": Pj(GAUGE), "ramp": Pj((RAMP0 + RAMP1) / 2), "coil": Pj(COIL), "gate": Pj(GATE), "cash": Pj(CASH), "tray": Pj(TRAY),
            "euro": Pj(eu), "ring": Pj(eu + Vector((0.0, -0.05, 0.12))), "center": Pj(eu + Vector((0, -0.05, 0))), "slot": Pj(SLOT)}

if __name__ == "__main__":
    run("moneda", build, pose, anchors)
