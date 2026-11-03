# "Inventa el código de barras": caja del súper, un producto y su etiqueta EAN-13 que se va construyendo.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector, Euler

CODE = "8412345678905"
L = {"0": "0001101", "1": "0011001", "2": "0010011", "3": "0111101", "4": "0100011", "5": "0110001", "6": "0101111", "7": "0111011", "8": "0110111", "9": "0001011"}
G = {k: "".join(v)[::-1].translate(str.maketrans("01", "10"))[::-1] for k, v in L.items()}
G = {k: "".join("1" if c == "0" else "0" for c in L[k])[::-1] for k in L}
R = {k: "".join("1" if c == "0" else "0" for c in L[k]) for k in L}
PAR = {"8": "LGLGGL"}
def modules():
    m = [("101", "g")]
    for d, p in zip(CODE[1:7], PAR[CODE[0]]): m.append(((L if p == "L" else G)[d], "l"))
    m.append(("01010", "g"))
    for d in CODE[7:]: m.append((R[d], "r"))
    m.append(("101", "g"))
    out = []; x = 0
    for bits, kind in m:
        for b in bits:
            out.append((x, b == "1", kind)); x += 1
    return out

MW = 0.1   # ancho de módulo
BOX = (0.95, 0.42, 0.25); LABEL_W, LABEL_H = 11.5, 7.2
PROD = Vector((0, 0, 0))          # centro de la cara frontal de la etiqueta (y = -2.5 del producto)

def build():
    sc, cam = scene_setup(world=(0.78, 0.9, 0.98))
    S = {"cam": cam}
    # suelo y caja registradora
    box((200, 200, 1), (0, 0, -12.5), (0.85, 0.86, 0.9))
    box((60, 22, 10), (0, 12, -6), (0.92, 0.93, 0.95)); box((60, 14, 0.4), (0, 4, -0.95), (0.18, 0.19, 0.22))      # mostrador y cinta
    for k in range(-15, 16): box((0.15, 14, 0.05), (k * 2.0, 4, -0.73), (0.28, 0.29, 0.33))
    box((60, 0.8, 1.6), (0, -3.4, -0.4), (0.75, 0.77, 0.8))
    # escáner (cristal en el mostrador) a la derecha
    SC = Vector((16, 3, -0.7)); S["SC"] = SC
    box((8, 8, 0.2), SC, (0.25, 0.3, 0.35)); box((7, 7, 0.05), SC + Vector((0, 0, 0.12)), (0.45, 0.7, 0.85))
    box((8, 1.5, 9), SC + Vector((0, 4.5, 4.4)), (0.3, 0.32, 0.36)); box((7, 0.05, 6), SC + Vector((0, 3.72, 5.4)), (0.45, 0.7, 0.85))
    # registradora a la izquierda
    RG = Vector((-18, 6, 0)); S["RG"] = RG
    box((12, 9, 4), RG + Vector((0, 0, 2)), (0.3, 0.32, 0.37))
    S["disp"] = box((9, 0.3, 3.2), RG + Vector((0, -2.2, 8.2)), (0.12, 0.14, 0.18), unique=True)
    box((0.8, 0.8, 4.5), RG + Vector((0, 0, 5.5)), (0.3, 0.32, 0.37))
    keys = []
    for r in range(4):
        for c in range(4):
            keys.append(box((1.8, 1.3, 0.5), RG + Vector((-3 + c * 2.0, -2.8 + r * 1.6, 4.25)), (0.9, 0.9, 0.92)))
    S["keys"] = keys; S["keys_home"] = [Vector(k.location) for k in keys]
    # producto: caja de cereales genérica con la etiqueta
    prod = empty((0, 2.5, 0)); S["prod"] = prod
    pb = box((14, 5, 20), (0, 0, 0), BOX, prod)
    box((14.05, 5.05, 4), (0, 0, 7.5), (1.0, 0.85, 0.3), prod)
    sph(3.0, (0, -2.4, 3.0), (1.0, 0.95, 0.85), prod, scale=(1, 0.15, 1)); sph(2.0, (2.5, -2.5, 1.0), (0.95, 0.6, 0.25), prod, scale=(1, 0.1, 1))
    lab = empty((0, -2.53, -5.0), prod); S["lab"] = lab
    box((LABEL_W, 0.04, LABEL_H), (0, 0, 0), (1, 1, 1), lab)
    # barras
    mods = modules(); S["bars"] = []
    x0 = -len(mods) * MW / 2
    run = None
    for i, (x, on, kind) in enumerate(mods + [(len(mods), False, "g")]):
        if on and run is None: run = (x, kind)
        if (not on or (run and kind != run[1])) and run is not None:
            w = (x - run[0]) * MW; cx = x0 + run[0] * MW + w / 2
            bpivot = empty((cx, -0.04, -1.6 + 0.5), lab)    # pivote en la base de la barra
            b = box((w, 0.03, 1.0), (0, 0, 0.5), (0.05, 0.05, 0.06), bpivot, unique=True)
            S["bars"].append((bpivot, b, run[1], cx))
            run = (x, kind) if on else None
    # números (uno por objeto)
    S["digits"] = []
    xs = [x0 - 0.55] + [x0 + (3 + k * 7 + 3.5) * MW for k in range(6)] + [x0 + (50 + k * 7 + 3.5) * MW for k in range(6)]
    for k, (d, x) in enumerate(zip(CODE, xs)):
        o = text3d(d, (x, -0.05, -2.6), 0.85, (0.05, 0.05, 0.06), lab, extrude=0.0, rot=(math.pi / 2, 0, 0), unique=True)
        S["digits"].append(o)
    S["xs"] = xs
    # láser
    S["laser"] = box((LABEL_W * 0.95, 0.02, 0.06), (0, -0.09, 1.2), (1.0, 0.15, 0.15), lab)
    S["dot"] = sph(0.18, (0, -0.1, 1.2), (1.0, 0.3, 0.3), lab)
    S["stain"] = sph(0.9, (1.6, -0.08, 1.4), (0.55, 0.36, 0.2), lab, scale=(1.2, 0.08, 0.8))
    S["checkbox"] = box((0.95, 0.02, 1.25), (xs[-1], -0.07, -2.6), (0.3, 0.9, 0.45), lab)
    # chicles (final)
    gum = empty((0, 0, -50)); S["gum"] = gum
    box((6, 1.6, 2.4), (0, 0, 0), (0.98, 0.9, 0.35), gum); box((6.05, 1.65, 0.7), (0, 0, 0.4), (0.95, 0.35, 0.45), gum)
    for k in range(9): box((0.12, 0.02, 0.9), (-1.0 + k * 0.25, -0.82, -0.6), (0.05, 0.05, 0.05), gum)
    join_static([cam, S["disp"], keys, prod, gum])
    return sc, S

def bar_height(t, kind, cx):
    grow = seg(t, 20.5 + (cx + 5) / 10 * 3.5, 21.0 + (cx + 5) / 10 * 3.5)
    ext = 0.0
    if kind == "g":
        a = 33.4 if cx < -3 else (36.6 if cx > 3 else 35.8)
        ext = 0.9 * seg(t, a, a + 0.4) * grow
    return max(1e-3, 3.6 * grow + ext), ext

def pose(t, S):
    # producto: entra en la cinta, se gira del revés, vuelve
    roll = math.pi * (seg(t, 39.4, 40.6) - seg(t, 49.4, 50.2))
    pos = keyed(t, [(0, Vector((-30, 2.5, 9.25))), (2.0, Vector((0, 2.5, 9.25))), (75.5, Vector((0, 2.5, 9.25))), (76.5, Vector((-40, 2.5, 9.25))), (90, Vector((-40, 2.5, 9.25)))])
    S["prod"].location = pos; S["prod"].rotation_euler = (0, roll, 0)
    for (piv, b, kind, cx) in S["bars"]:
        h, ext = bar_height(t, kind, cx); piv.scale = (1, 1, h)
        col = (0.05, 0.05, 0.06)
        if 41.7 <= t < 49.6 and kind != "g": col = (0.2, 0.4, 0.95) if kind == "l" else (0.95, 0.5, 0.15)
        if 33.2 <= t < 38.3 and kind == "g": col = (0.92, 0.25, 0.25)
        set_color(b, col)
        piv.location.z = -1.6 - ext
    # los números aparecen a los 8.5 s, uno a uno (como si se tecleara) a partir de 11 s
    for k, d in enumerate(S["digits"]):
        a = 8.6 + k * 0.12 if t < 11.0 else 8.6 + k * 0.12
        u = seg(t, a, a + 0.25); d.scale = (u, u, u)
        col = (0.05, 0.05, 0.06)
        if 11.0 <= t < 13.8 and int((t - 11.0) / 0.2) == k: col = (0.95, 0.3, 0.3)
        if 41.7 <= t < 49.6 and 1 <= k <= 6: col = (0.2, 0.4, 0.95)
        if 41.7 <= t < 49.6 and k >= 7: col = (0.95, 0.5, 0.15)
        if 68.8 <= t < 75.3 and k < 2: col = (0.92, 0.2, 0.2)
        if 60.0 <= t < 63.4 and int((t - 60.0) / 0.25) == k: col = (0.25, 0.75, 0.4)
        if 52.9 <= t < 55.0 and k == 9: col = (0.92, 0.2, 0.2)
        set_color(d, col)
    S["checkbox"].scale = (1, 1, 1) if 55.2 <= t < 67.8 else (1e-3, 1e-3, 1e-3)
    # láser: barrido
    on = (25.9 <= t < 30.5) or (42.0 <= t < 49.4) or (51.4 <= t < 55.0) or (63.7 <= t < 67.8) or (77.5 <= t < 81.8)
    S["laser"].scale = (LABEL_W * 0.95, 0.02, 0.06) if on else (1e-3, 1e-3, 1e-3)
    sweep = ((t * 0.9) % 1.0)
    S["dot"].location = Vector((-5.2 + 10.4 * sweep, -0.1, 1.2)) if on else Vector((0, 0, -30))
    S["stain"].scale = (1.2, 0.08, 0.8) if 51.3 <= t < 55.2 else (1e-3, 1e-3, 1e-3)
    # registradora: teclas y pantalla
    for k, (o, h) in enumerate(zip(S["keys"], S["keys_home"])):
        d = 0
        if 2.6 <= t < 8.2 and int(t * 5) % 16 == k and (t * 5) % 1 < 0.5: d = -0.3
        if 11.0 <= t < 13.8 and int((t - 11.0) / 0.2) % 16 == (k * 7) % 16: d = -0.3
        o.location = h + Vector((0, 0, d))
    scr = (0.12, 0.14, 0.18)
    if 6.2 <= t < 8.2: scr = (0.9, 0.25, 0.25)
    if 28.5 <= t < 29.2: scr = (0.3, 0.85, 0.45)
    if 65.6 <= t < 67.8: scr = (0.9, 0.25, 0.25)
    set_color(S["disp"], scr)
    # chicles
    S["gum"].location = keyed(t, [(75.6, Vector((40, 1.5, 1.2))), (76.8, Vector((14, 1.5, 1.2))), (77.6, Vector((16, 1.5, 1.2))), (90, Vector((16, 1.5, 1.2)))]) if t > 75.6 else Vector((0, 0, -50))
    S["gum"].rotation_euler = (0, 0, 0.0)
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.05))

LABC = (0, 0, 2.3)
CAM = [
    (0.0, (8, -48, 22), (0, 2, 6), 30), (2.2, (-6, -40, 20), (-6, 3, 5), 30), (2.8, (-16, -16, 14), (-18, 3, 6), 32),
    (8.2, (-14, -17, 14), (-17, 3, 6), 32), (8.6, (0, -24, 6), (0, 0, 4.0), 32), (13.8, (0, -23, 5.5), (0, 0, 4.2), 32),
    (14.2, (10, -32, 12), (8, 2, 2), 30), (20.1, (8, -30, 10), (6, 1, 3), 30), (20.5, (0, -22, 5), LABC, 34), (25.6, (0, -21, 5), LABC, 34),
    (26.0, (2.5, -19, 6), LABC, 36), (30.6, (1.5, -19, 5.5), LABC, 36), (31.0, (0, -20, 4.5), LABC, 34), (38.4, (0, -20, 4.0), LABC, 34),
    (39.0, (-6, -24, 10), (0, 0, 7.5), 32), (41.6, (0, -20, 14.3), (0, 0, 12.3), 34), (49.5, (0, -20, 14.3), (0, 0, 12.3), 34), (50.2, (3, -19, 6), LABC, 36),
    (55.2, (2, -18, 5.5), (2.5, 0, 2.6), 38), (59.7, (3, -16, 4), (4.5, 0, 1.8), 40), (60.1, (0, -20, 4.5), LABC, 34), (63.4, (0, -20, 4.5), LABC, 34),
    (63.8, (-12, -22, 12), (-12, 3, 5.5), 30), (67.8, (-13, -21, 12), (-14, 3, 6), 30), (68.2, (-3, -16, 3.5), (-4, 0, 1.8), 40),
    (75.3, (-3, -16, 3.5), (-4, 0, 1.8), 40), (76.0, (10, -26, 8), (14, 2, 1.5), 32), (81.8, (12, -18, 6), (16, 1.5, 1.2), 32),
    (84.6, (4, -46, 18), (4, 2, 4), 30), (95, (4, -46, 18), (4, 2, 4), 30),
]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    lab = S["lab"].matrix_world
    xs = S["xs"]
    return {"label": Pj(lab @ Vector((0, 0, 1.0))), "digits": Pj(lab @ Vector((0, 0, -2.6))), "first2": Pj(lab @ Vector(((xs[0] + xs[1]) / 2, 0, -2.6))),
            "last": Pj(lab @ Vector((xs[-1], 0, -2.6))), "d9": Pj(lab @ Vector((xs[9], 0, -2.6))), "start": Pj(lab @ Vector((xs[0] + 0.6, 0, -1.9))),
            "mid": Pj(lab @ Vector((0, 0, -1.9))), "end": Pj(lab @ Vector((-xs[0] - 0.6, 0, -1.9))), "left": Pj(lab @ Vector((-2.6, 0, 2.2))),
            "right": Pj(lab @ Vector((2.6, 0, 2.2))), "stain": Pj(lab @ Vector((1.6, 0, 1.4))), "disp": Pj(S["RG"] + Vector((0, -2.4, 8.2))),
            "scanner": Pj(S["SC"] + Vector((0, 0, 1))), "gum": Pj(S["gum"].matrix_world.translation), "laser": Pj(lab @ Vector((0, 0, 1.2)))}

if __name__ == "__main__":
    run("barras", build, pose, anchors)
