# «Así funciona la cerradura»: cerradura de pernos en una puerta; corte lateral, llave que entra, pernos que suben, línea de corte, gira y mueve el pestillo.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("cerradura")
BRASS = (0.93, 0.72, 0.28); STEEL = (0.62, 0.68, 0.78); KEYC = (0.82, 0.84, 0.88); WOOD = (0.62, 0.4, 0.24); RED = (0.95, 0.3, 0.25)
HOUSE = (0.8, 0.82, 0.86); SPRING = (0.45, 0.47, 0.52)
PX = [-1.6, -0.8, 0.0, 0.8, 1.6]          # posiciones de los pernos
SHEAR = 0.62                               # borde superior del cilindro (línea de corte)
BIT = [0.05, -0.25, 0.2, -0.1, 0.12]       # altura de cada diente de la llave buena
BIT_MAL = [0.05, -0.25, 0.48, -0.1, 0.12]  # llave con un diente demasiado alto
KTOP0 = -0.32                              # reposo de los pernos inferiores sin llave
DRV = 0.62                                 # largo de los pernos superiores

def perfil(bits, x):
    """altura del borde superior de la llave en x local (punta en x=2.3)"""
    if x > 2.35 or x < -2.6: return None
    if x > 1.9: return mix(bits[-1], -0.45, (x - 1.9) / 0.45)
    pts = [(-2.6, -0.1)] + [(p, b) for p, b in zip(PX, bits)] + [(1.9, bits[-1])]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if a <= x <= b:
            m = (a + b) / 2; valle = min(va, vb) - 0.18
            return mix(va, valle, (x - a) / (m - a)) if x < m else mix(valle, vb, (x - m) / (b - m))
    return -0.1

def llave(bits, color):
    me = bpy.data.meshes.new("llave"); bm = bmesh.new()
    xs = [-2.6 + i * 0.05 for i in range(int(4.95 / 0.05) + 1)]
    top = [(x, perfil(bits, x)) for x in xs]
    poly = [(x, -0.48) for x in reversed(xs)] + top
    vf = [bm.verts.new((x, -0.09, z)) for x, z in poly]; vb_ = [bm.verts.new((x, 0.09, z)) for x, z in poly]
    bm.faces.new(vf); bm.faces.new(list(reversed(vb_)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((vf[i], vb_[i], vb_[j], vf[j]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("llave", me); bpy.context.collection.objects.link(o); setup(o, color, unique=True)
    cab = rounded_slab(1.5, 1.5, 0.45, 0.18, (-3.25, 0.09, -0.1), color, parent=o); cab.rotation_euler = (math.pi / 2, 0, 0)
    agujero = cyl(0.22, 0.25, (-3.6, 0, -0.1), (0.5, 0.75, 0.95), parent=o, rot=(math.pi / 2, 0, 0))
    return o

def build():
    sc, cam = scene_setup(world=(0.93, 0.9, 0.84))
    S = {"cam": cam}
    box((60, 60, 0.1), (0, 0, -6.05), (0.88, 0.84, 0.78))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 0)); cutter = bpy.context.object; cutter.scale = (14, 10, 14); cutter.hide_render = True
    S["cutter"] = cutter
    def cortar(o):
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter; b.solver = 'MANIFOLD' if hasattr(b, "solver") else b.solver
    # puerta con agujero para la cerradura
    puerta = box((0.4, 7, 9), (-2.65, 0, -1.0), WOOD, unique=True)
    hp = cyl(0.8, 1, (-2.65, 0, 0), (0, 0, 0), rot=(0, math.pi / 2, 0)); hp.hide_render = True
    b = puerta.modifiers.new("hole", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = hp
    cortar(puerta); S["puerta"] = puerta
    S["roseta"] = torus(0.85, 0.08, (-2.88, 0, 0), BRASS, rot=(0, math.pi / 2, 0))
    # carcasa con hueco del cilindro
    casa = box((4.8, 1.6, 3.4), (0, 0, 0.75), HOUSE, unique=True)
    hc = cyl(0.66, 6, (0, 0, 0), (0, 0, 0), rot=(0, math.pi / 2, 0)); hc.hide_render = True
    b = casa.modifiers.new("hole", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = hc
    cortar(casa); S["casa"] = casa
    # cilindro (gira) con su ranura y canales
    piv = empty((0, 0, 0)); S["piv"] = piv
    plug = cyl(0.62, 4.7, (0, 0, 0), BRASS, parent=piv, rot=(0, math.pi / 2, 0), v=48, unique=True)
    ranura = box((4.8, 0.22, 0.62), (0, 0, -0.18), (0.35, 0.3, 0.22)); ranura.hide_render = True
    b = plug.modifiers.new("slot", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = ranura
    cortar(plug); S["plug"] = plug
    cara = cyl(0.63, 0.04, (-2.37, 0, 0), BRASS, parent=piv, rot=(0, math.pi / 2, 0))
    box((0.06, 0.24, 0.66), (-2.4, 0, -0.18), (0.18, 0.15, 0.1), parent=piv)
    # canales oscuros detrás de los pernos
    for x in PX: box((0.36, 0.02, 2.75), (x, 0.03, 1.0), (0.42, 0.42, 0.46))
    S["kp"] = [cyl(0.16, 1, (x, 0, 0), (0.9, 0.45, 0.3), unique=True) for x in PX]
    S["dp"] = [cyl(0.16, DRV, (x, 0, 0), STEEL, unique=True) for x in PX]
    S["sp"] = [[torus(0.13, 0.035, (x, 0, 0), SPRING) for _ in range(7)] for x in PX]
    for kp, x, b_ in zip(S["kp"], PX, BIT):  # largo = de la cresta del diente a la línea de corte
        kp.scale.z = SHEAR - b_
    S["shear"] = box((4.7, 0.03, 0.035), (0, -0.2, SHEAR), (1, 0.82, 0.15), unique=True)
    S["key"] = llave(BIT, KEYC); S["keyb"] = llave(BIT_MAL, (0.95, 0.6, 0.55))
    # leva y pestillo
    S["leva"] = box((0.2, 0.25, 0.9), (2.5, 0, -0.45), STEEL, parent=piv)
    S["pest"] = box((2.0, 0.6, 0.55), (3.6, 0, -1.6), (0.75, 0.77, 0.8), unique=True)
    box((0.3, 1.2, 1.0), (4.7, 0, -1.6), (0.5, 0.52, 0.56))
    join_static([cam, cutter, puerta, hp, casa, hc, piv, ranura, S["kp"], S["dp"], S["sp"], S["shear"], S["key"], S["keyb"], S["pest"], S["roseta"]])
    return sc, S

def estado_pernos(t, S, xk, bits, gira):
    """xk: desplazamiento de la llave (0 = metida del todo). Devuelve si algún perno cruza la línea de corte."""
    cruza = False
    for i, x in enumerate(PX):
        L = SHEAR - BIT[i]
        p = perfil(bits, x - xk) if xk is not None else None
        base = max(KTOP0, p) if p is not None else KTOP0
        top = base + L
        S["kp"][i].location = (x, 0, base + L / 2)
        dz = top + DRV / 2
        S["dp"][i].location = (x, 0, dz)
        mal = abs(top - SHEAR) > 0.04 and xk is not None and xk > -0.05
        cruza |= abs(top - SHEAR) > 0.04
        set_color(S["kp"][i], RED if mal and (t % 0.5 < 0.3) else (0.9, 0.45, 0.3))
        tope = 2.3; ztop = top + DRV
        for k, c in enumerate(S["sp"][i]):
            c.location = (x, 0, ztop + (tope - ztop) * (k + 0.5) / 7)
    return cruza

def pose(t, S):
    S["cutter"].location.y = -5.0 - 25 * (1 - seg(t, T("mira") - 0.2, T("mira") + 0.9))
    S["puerta"].location.x = -2.65; S["puerta"].hide_render = False
    # llave buena: entra al decir «metes la llave», sale antes de la llave mala
    t_in = T("metes la llave"); t_gira = T("cilindro gira"); t_mal = T("si un solo diente")
    xk = keyed(t, [(0, -14.0), (t_in - 0.6, -14.0), (t_in, -7.0), (t_in + 2.4, 0.0), (t_mal - 1.2, 0.0), (t_mal - 0.3, -14.0)])
    xm = keyed(t, [(0, -14.0), (t_mal - 0.5, -14.0), (t_mal, -7.0), (t_mal + 1.6, 0.0), (T("combinaciones") - 0.3, 0.0), (T("combinaciones") + 0.6, -14.0)])
    S["key"].location = (xk, 0, 0); S["keyb"].location = (xm, 0, 0)
    if xm > -7.5:
        estado_pernos(t, S, xm, BIT_MAL, 0)
    else:
        estado_pernos(t, S, xk if xk > -7.5 else None, BIT, 0)
    # giro del cilindro con la llave buena; intento fallido con la mala
    ang = 1.35 * seg(t, t_gira, t_gira + 0.9) * (1 - seg(t, t_mal - 1.6, t_mal - 1.2))
    if xm > -0.3: ang = 0.06 * math.sin(t * 22) * (t < T("combinaciones"))
    S["piv"].rotation_euler = (ang, 0, 0)
    for o in (S["key"], S["keyb"]): o.rotation_euler = (ang if o.location.x > -0.3 else 0, 0, 0)
    for i in range(5):
        if abs(ang) > 0.1:
            S["kp"][i].location = Vector((PX[i], 0, 0)) + Matrix_rot(ang) @ Vector((0, 0, S["kp"][i].location.z))
            S["kp"][i].rotation_euler = (ang, 0, 0)
        else: S["kp"][i].rotation_euler = (0, 0, 0)
    S["pest"].location.x = 3.6 - 1.4 * seg(t, t_gira + 0.4, t_gira + 1.1) * (1 - seg(t, t_mal - 1.6, t_mal - 1.2))
    # línea de corte brilla al nombrarla
    w = win01(t, T("línea de corte") - 0.2, T("ya nada") + 0.8)
    S["shear"].scale = (4.7, 0.03, 0.035 + 0.05 * w); set_color(S["shear"], mix_c((0.9, 0.85, 0.6), (1, 0.85, 0.1), w))
    # madera en el dato de los egipcios
    eg = win01(t, T("egipcios") - 0.3, T("linus") - 0.2)
    for kp in S["kp"]:
        if eg: set_color(kp, WOOD)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.04))

from mathutils import Matrix
def Matrix_rot(a): return Matrix.Rotation(a, 3, 'X')
def mix_c(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))

def V(x, z, d, h=0.6, lens=32, sx=0.0): return ((x + sx, -d, z + h), (x, 0, z), lens)
def CAM():
    m = T("mira"); k = T("metes la llave"); g = T("cilindro gira"); mal = T("si un solo diente")
    return [(0.0, (-11, -3.2, 1.2), (-2.6, 0, 0.2), 38), (m - 0.4, (-8.5, -4.5, 1.4), (-1.5, 0, 0.3), 36),
            (m + 1.0,) + V(0, 0.6, 10.5), (T("dos pernos") - 0.3,) + V(0.2, 1.0, 7.5), (T("sin llave"),) + V(0, 0.8, 8.5),
            (k - 0.3,) + V(-1.5, 0.4, 10.5), (k + 2.6,) + V(0.2, 0.5, 8.0), (T("línea de corte"),) + V(0.4, 0.6, 6.5),
            (g + 0.2, (-3, -8.5, 3.5), (0.8, 0, -0.2), 34), (g + 2.2, (1.5, -9.5, 2.5), (2.2, 0, -0.8), 34),
            (mal - 0.2,) + V(0, 0.6, 9.5), (mal + 1.8,) + V(0.2, 0.7, 7.5), (T("combinaciones") + 0.5,) + V(0, 0.5, 10),
            (T("egipcios"),) + V(0.3, 1.0, 8.0), (T("sígueme"),) + V(0, 0.5, 11), (DUR + 2,) + V(0, 0.5, 11.5)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"plug": Pj((0, -0.6, -0.3)), "casa": Pj((0, -0.8, 1.9)), "pernos": Pj((0, -0.2, 1.2)), "shear": Pj((1.9, -0.2, SHEAR)),
            "muelle": Pj((0.8, -0.2, 2.0)), "pest": Pj((S["pest"].location.x, -0.3, -1.6)), "llave": Pj((-3.0, -0.2, -0.1)), "p3": Pj((0, -0.2, 0.9))}

if __name__ == "__main__":
    run("cerradura", build, pose, anchors)
