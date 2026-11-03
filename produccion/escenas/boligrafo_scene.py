# «Si tuvieras que inventar el bolígrafo»: pluma y tintero → tubo con tinta (gotea) → tinta espesa → bolita que rueda y escribe
# → demasiado justa / suelta → casquillo → vacío arriba → agujerito de aire → capuchón con agujero.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Matrix

T, DUR = cargar("boligrafo")
INK = (0.12, 0.25, 0.85); INK2 = (0.08, 0.14, 0.55); BARREL = (0.45, 0.68, 0.92); METAL = (0.75, 0.77, 0.8); PAPER = (0.99, 0.98, 0.95)
DESK = (0.72, 0.52, 0.34); TILT = math.radians(38)

def cut(o, c):
    b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = c

def build():
    sc, cam = scene_setup(world=(0.86, 0.9, 0.98))
    S = {"cam": cam}
    box((60, 60, 0.1), (0, 0, -0.05), DESK)
    box((60, 0.2, 30), (0, 7, 10), (0.97, 0.88, 0.7))
    box((6, 8, 0.02), (0.5, 1.0, 0.01), PAPER)
    for k in range(9): box((5.6, 0.015, 0.004), (0.5, -2.6 + k * 0.8, 0.022), (0.75, 0.82, 0.95))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 2)); cutter = bpy.context.object; cutter.scale = (14, 10, 14); cutter.hide_render = True
    S["cutter"] = cutter
    # bolígrafo: grupo con la punta en el origen y el eje en +Z local
    pen = empty((0, 0, 0)); S["pen"] = pen
    S["barrel"] = cyl(0.27, 5.0, (0, 0, 3.4), BARREL, parent=pen, v=48, unique=True); cut(S["barrel"], cutter)
    m = S["barrel"].modifiers.new("sol", "SOLIDIFY"); m.thickness = 0.04; m.offset = -1
    S["barrel"].modifiers.move(1, 0)
    bpy.ops.mesh.primitive_cone_add(radius1=0.075, radius2=0.24, depth=0.95, location=(0, 0, 0.47), vertices=48)
    S["punta"] = bpy.context.object; setup(S["punta"], METAL, parent=pen, smooth=True, unique=True); cut(S["punta"], cutter)
    S["tubo"] = cyl(0.11, 4.6, (0, 0, 3.25), (0.98, 0.98, 1.0), parent=pen, unique=True); cut(S["tubo"], cutter)
    S["tinta"] = cyl(0.095, 1.0, (0, 0, 2.0), INK, parent=pen, unique=True)
    S["bola"] = sph(0.075, (0, 0, 0.02), (0.88, 0.9, 0.95), parent=pen, seg=24, unique=True)
    S["raya"] = box((0.02, 0.16, 0.02), (0, 0, 0.02), (0.3, 0.32, 0.36), parent=S["bola"])   # marca para ver girar la bola
    S["aire"] = cyl(0.05, 0.12, (-0.27, 0, 5.3), (0.15, 0.15, 0.18), parent=pen, rot=(0, math.pi / 2, 0), unique=True)
    S["cap"] = empty((0, 0, 0), parent=pen)
    capb = cyl(0.33, 1.9, (0, 0, 0.6), (0.15, 0.3, 0.8), parent=S["cap"], unique=True)
    cyl(0.07, 0.05, (0, 0, -0.36), (0.05, 0.05, 0.08), parent=S["cap"])
    # pluma y tintero del principio
    S["tintero"] = empty((-2.6, 2.2, 0))
    cyl(0.6, 0.9, (0, 0, 0.45), (0.15, 0.22, 0.4), parent=S["tintero"]); cyl(0.3, 0.2, (0, 0, 1.0), (0.1, 0.1, 0.12), parent=S["tintero"])
    S["pluma"] = empty((-2.6, 2.2, 3))
    cyl(0.09, 2.6, (0, 0, 1.4), (0.35, 0.12, 0.1), parent=S["pluma"]);
    bpy.ops.mesh.primitive_cone_add(radius1=0.0, radius2=0.09, depth=0.3, location=(0, 0, 0)); setup(bpy.context.object, (0.9, 0.75, 0.3), parent=S["pluma"])
    # desodorante (bola que gira)
    S["deo"] = empty((3.6, 1.2, -9))
    cyl(0.5, 1.6, (0, 0, 0.8), (0.4, 0.75, 0.9), parent=S["deo"]); S["deo_bola"] = sph(0.42, (0, 0, 1.75), (0.92, 0.94, 0.97), parent=S["deo"], unique=True)
    box((0.05, 0.6, 0.06), (0, 0, 0.42), (0.6, 0.62, 0.7), parent=S["deo_bola"])
    S["gotas"] = [sph(0.06, (0, 0, -9), INK) for _ in range(6)]
    S["manchas"] = [cyl(0.14, 0.01, (0, 0, -9), INK, v=24) for _ in range(5)]
    S["trazo"] = [box((0.09, 0.05, 0.006), (0, 0, -9), INK2) for _ in range(60)]
    S["burb"] = [sph(0.03, (0, 0, -9), (0.95, 0.97, 1)) for _ in range(8)]
    join_static([cam, cutter, pen, S["tintero"], S["pluma"], S["deo"], S["gotas"], S["manchas"], S["trazo"], S["burb"]])
    return sc, S

def path(u):
    """recorrido de escritura sobre el papel (una línea ondulada)"""
    return Vector((-1.8 + 4.4 * u, -1.0 + 0.18 * math.sin(u * 30), 0.025))

def pose(t, S):
    t_dep, t_got, t_esp, t_bol, t_gir = T("depósito"), T("gotea"), T("espesa"), T("bolita"), T("la bola gira")
    t_deo, t_rod, t_tapa, t_justa, t_suel = T("desodorante"), T("al rodar"), T("mientras no"), T("demasiado justa"), T("suelta")
    t_casq, t_ult, t_vac, t_aguj, t_cap, t_biro = T("casquillo"), T("último problema"), T("se forma un vacío"), T("agujerito"), T("capuchón"), T("patentó")
    pass
    # pluma mojándose en el tintero (primeros segundos)
    dip = 0.5 + 0.5 * math.cos(t * 4.5)
    S["pluma"].location = (-2.6, 2.2, (1.0 + 1.6 * dip) if t < t_dep else -9)
    S["tintero"].location.z = 0 if t < t_dep + 1 else -9
    # bolígrafo: aparece al decir «depósito»
    aparece = seg(t, t_dep - 0.3, t_dep + 0.3)
    escribiendo = (t_rod - 0.2 < t < t_tapa) or (t_casq + 0.8 < t < t_vac + 1.0) or (t_aguj + 1.0 < t < t_cap - 0.3)
    u_esc = (t * 0.22) % 1.0
    tip = path(u_esc) if escribiendo else Vector((0.4, -1.0, 1.1 if t < t_rod else 0.9))
    S["pen"].location = tip + Vector((0, 0, 0.06))
    S["cutter"].location.y = tip.y - 5.0 - 25 * (1 - seg(t, t_dep - 0.2, t_dep + 0.7))
    S["pen"].rotation_euler = (0, -TILT, 0)
    S["pen"].scale = (aparece,) * 3
    # tinta: líquida (clara) → espesa (oscura); nivel baja al final
    esp = seg(t, t_esp, t_esp + 0.6)
    set_color(S["tinta"], tuple(mix(a, b, esp) for a, b in zip(INK, INK2)))
    nivel = 3.6 - 1.6 * seg(t, t_ult, t_ult + 1.4)
    S["tinta"].scale.z = nivel; S["tinta"].location.z = 1.0 + nivel / 2
    # gotas que caen y manchan mientras la tinta es líquida
    for k, g in enumerate(S["gotas"]):
        if t_got - 0.4 < t < t_esp:
            u = ((t - t_got + 0.4) * 1.3 + k / 6) % 1.0
            g.location = Vector((tip.x, tip.y - 0.05, tip.z - 0.1 - 1.0 * u * u))
        else: g.location = (0, 0, -9)
    rng = random.Random(4)
    for k, mch in enumerate(S["manchas"]):
        x, y = rng.uniform(0, 0.9), rng.uniform(-1.4, -0.6)
        mch.location = (x, y, 0.025) if t_got + 0.3 * k < t < t_bol else (0, 0, -9)
        mch.scale = (1 + 0.4 * k % 2, 1, 1)
    # bola: aparece con «bolita», gira al escribir y con «la bola gira»; demasiado justa = quieta; suelta = se sale
    S["bola"].hide_render = t < t_bol
    gira = escribiendo or (t_gir < t < t_rod)
    if t_justa < t < t_suel: gira = False
    S["bola"].rotation_euler = (t * 9 if gira else 0, 0, 0)
    sale = seg(t, t_suel + 0.3, t_suel + 1.2) * (1 - seg(t, t_casq - 0.3, t_casq))
    S["bola"].location = (0, -1.2 * sale, 0.02 - 0.4 * sale)
    S["punta"].scale = (1, 1, 1) if t > t_casq else (0.85, 0.85, 1)
    # desodorante de comparación
    S["deo"].location.z = 0 if t_deo - 0.2 < t < t_rod + 0.2 else -9
    S["deo_bola"].rotation_euler = (t * 3, 0, 0)
    # trazo sobre el papel
    for k, s in enumerate(S["trazo"]):
        uk = k / 60
        hecho = escribiendo and uk < u_esc or (t > t_rod and uk < u_esc and t < t_cap + 3)
        if t_vac < t < t_aguj + 1.0 and uk > 0.6: hecho = False   # deja de salir tinta con el vacío
        p = path(uk); s.location = p if hecho else (0, 0, -9); s.rotation_euler = (0, 0, 0.18 * 30 * math.cos(uk * 30) * 0.18)
    # agujero de aire y burbujas que entran
    S["aire"].hide_render = t < t_aguj
    for k, b in enumerate(S["burb"]):
        if t_aguj + 0.4 < t < t_cap:
            u = (t * 0.8 + k / 8) % 1.0
            b.location = S["pen"].matrix_world @ Vector((-0.6 + 0.35 * u, 0, 5.3 + 0.2 * u))
        else: b.location = (0, 0, -9)
    # capuchón
    cp = seg(t, t_cap - 0.1, t_cap + 0.7)
    S["cap"].location = (0, 0, mix(-3.0, 0.0, cp)) if t > t_cap - 0.1 else (0, 0, 60)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def V(at, d, h=1.2, lens=34, dx=0.0): at = Vector(at); return ((at.x + dx, at.y - d, at.z + h), tuple(at), lens)
def CAM():
    tip = Vector((0.4, -1.0, 1.1)); mid = tip + Vector((-1.6, 0, 2.1)); top = tip + Vector((-3.1, 0, 4.1))
    return [(0.0,) + V((-2.4, 2.2, 1.2), 7.0, 1.6), (T("depósito") - 0.3,) + V((-1.0, 0.8, 1.6), 8.0, 1.4),
            (T("depósito") + 1.0,) + V(mid, 8.5, 0.6), (T("gotea"),) + V(tip + Vector((-0.6, 0, 0.6)), 6.0, 0.6),
            (T("bolita"),) + V(tip, 2.6, 0.4, 40), (T("grano de arena"),) + V(tip, 1.6, 0.2, 45), (T("desodorante"),) + V((2.0, 0, 1.0), 6.5, 0.8),
            (T("al rodar"),) + V((0.2, -1, 0.4), 3.6, 0.7, 40), (T("mientras no"),) + V((0.4, -1, 0.6), 3.0, 0.4, 42),
            (T("demasiado justa"),) + V(tip, 2.0, 0.3, 44), (T("casquillo"),) + V(tip, 1.8, 0.3, 46), (T("último problema"),) + V(mid + Vector((0, 0, 0.6)), 7.0, 0.6),
            (T("agujerito"),) + V(top, 3.6, 0.4, 40), (T("capuchón"),) + V(mid, 7.5, 0.8),
            (T("patentó"),) + V(mid, 9.5, 1.0), (DUR + 2,) + V(mid, 10.0, 1.2)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    M = S["pen"].matrix_world
    return {"tip": Pj(M @ Vector((0, 0, 0.05))), "tinta": Pj(M @ Vector((0, 0, 2.5))), "aire": Pj(M @ Vector((-0.27, 0, 5.3))),
            "casq": Pj(M @ Vector((0, 0, 0.5))), "cap": Pj(M @ Vector((0, 0, -0.3))), "deo": Pj((3.6, 1.2, 1.9))}

if __name__ == "__main__":
    run("boligrafo", build, pose, anchors)
