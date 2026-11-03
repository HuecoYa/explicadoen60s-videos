# «Si tuvieras que inventar la lata»: lata cortada por la mitad que se va construyendo; gas, pared fina, fondo en cúpula,
# barniz, cuello estrecho, anilla vs lengüeta, bota encima (aguanta) y mano que aplasta la vacía.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("lata")
ALU = (0.82, 0.85, 0.9); RED = (0.9, 0.18, 0.2); DRINK = (0.32, 0.16, 0.08); VARN = (0.95, 0.85, 0.55); TABLE = (0.95, 0.9, 0.82)
R0, H0 = 0.66, 2.44

def cutter_mod(o, c):
    b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = c

def build():
    sc, cam = scene_setup(world=(0.98, 0.86, 0.72))
    S = {"cam": cam}
    box((60, 60, 0.1), (0, 0, -0.05), TABLE)
    box((60, 0.2, 30), (0, 9, 10), (0.98, 0.78, 0.6))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 1)); cutter = bpy.context.object; cutter.scale = (10, 10, 14); cutter.hide_render = True
    S["cutter"] = cutter
    lata = empty((0, 0, 0)); S["lata"] = lata
    # cuerpo: tubo fino (exterior rojo, interior aluminio / barniz)
    bpy.ops.mesh.primitive_cylinder_add(radius=R0, depth=H0 - 0.5, location=(0, 0, 0.25 + (H0 - 0.5) / 2), vertices=64, end_fill_type='NOTHING')
    body = bpy.context.object; setup(body, RED, parent=lata, smooth=True, unique=True)
    body.data.materials.append(mat(ALU, unique=True))
    m = body.modifiers.new("sol", "SOLIDIFY"); m.thickness = 0.025; m.offset = -1; m.material_offset = 1; m.material_offset_rim = 1
    cutter_mod(body, cutter); S["body"] = body
    # parte baja: fondo plano (se abomba) y fondo en cúpula
    S["base_ring"] = cyl(R0, 0.25, (0, 0, 0.125), ALU, parent=lata, v=64)
    cutter_mod(S["base_ring"], cutter)
    S["plano"] = cyl(R0 - 0.02, 0.03, (0, 0, 0.02), ALU, parent=lata, v=64, unique=True); cutter_mod(S["plano"], cutter)
    S["domo"] = sph(R0 - 0.06, (0, 0, 0.03), ALU, parent=lata, scale=(1, 1, 0.33), seg=48, unique=True); cutter_mod(S["domo"], cutter)
    # cuello recto y cuello estrecho
    bpy.ops.mesh.primitive_cone_add(radius1=R0, radius2=R0, depth=0.25, location=(0, 0, H0 - 0.125), vertices=64, end_fill_type='NOTHING')
    S["cuello_r"] = bpy.context.object; setup(S["cuello_r"], ALU, parent=lata, smooth=True, unique=True); cutter_mod(S["cuello_r"], cutter)
    bpy.ops.mesh.primitive_cone_add(radius1=R0, radius2=0.5, depth=0.25, location=(0, 0, H0 - 0.125), vertices=64, end_fill_type='NOTHING')
    S["cuello_e"] = bpy.context.object; setup(S["cuello_e"], ALU, parent=lata, smooth=True, unique=True); cutter_mod(S["cuello_e"], cutter)
    S["tapa"] = cyl(0.66, 0.06, (0, 0, H0), ALU, parent=lata, v=64, unique=True); cutter_mod(S["tapa"], cutter)
    S["piv_tab"] = empty((0.1, 0.05, H0 + 0.04), parent=lata)
    S["tab"] = rounded_slab(0.42, 0.2, 0.09, 0.025, (0.1, 0, 0), ALU, parent=S["piv_tab"], unique=True)
    S["panel"] = cyl(0.12, 0.02, (-0.22, 0.05, H0 + 0.03), (0.7, 0.72, 0.76), parent=lata, unique=True)
    S["anilla"] = torus(0.1, 0.02, (0, 0, -9), ALU)
    S["anillas_suelo"] = [torus(0.1, 0.02, (0, 0, -9), ALU) for _ in range(9)]
    # bebida y burbujas, flechas de presión
    S["liq"] = cyl(R0 - 0.03, 1.0, (0, 0, 0.9), DRINK, parent=lata, v=48, unique=True); cutter_mod(S["liq"], cutter)
    S["burb"] = [sph(0.035, (0, 0, -9), (0.95, 0.9, 0.8)) for _ in range(26)]
    S["flechas"] = []
    for k in range(10):
        a = k / 10 * math.tau; z = 0.6 + (k % 3) * 0.6
        bpy.ops.mesh.primitive_cone_add(radius1=0.09, radius2=0, depth=0.24, location=(0, 0, -9)); f = bpy.context.object; setup(f, (1, 0.82, 0.2), unique=False)
        f["a"] = a; f["z"] = z; S["flechas"].append(f)
    # rueda de coche y hoja de papel de referencia
    S["rueda"] = empty((3.4, 0.8, -9))
    torus(1.0, 0.38, (0, 0, 0), (0.12, 0.12, 0.14), parent=S["rueda"], rot=(math.pi / 2, 0, 0)); cyl(0.65, 0.5, (0, 0, 0), (0.75, 0.77, 0.8), parent=S["rueda"], rot=(math.pi / 2, 0, 0))
    S["papel"] = box((1.4, 0.006, 1.9), (2.4, -0.2, -9), (1, 1, 1))
    S["barniz"] = []
    # bota y mano
    S["bota"] = empty((0, 0, 30))
    rounded_slab(1.9, 0.9, 0.35, 0.35, (0, 0, 0), (0.25, 0.2, 0.18), parent=S["bota"]); box((0.9, 0.9, 2.4), (-0.4, 0, 1.5), (0.3, 0.42, 0.62), parent=S["bota"])
    S["mano"] = sph(0.75, (0, 0, 30), (0.95, 0.75, 0.62), scale=(1.2, 1, 0.8), unique=True)
    join_static([cam, cutter, lata, S["anilla"], S["anillas_suelo"], S["burb"], S["flechas"], S["rueda"], S["papel"], S["bota"], S["mano"]])
    return sc, S

def show(o, on):
    o.hide_render = not on

def pose(t, S):
    t_alu, t_fina = T("aluminio"), T("tan finas"); t_plano, t_cup = T("fondo plano"), T("cúpula")
    t_barniz, t_tapa, t_cuello = T("barniz"), T("la tapa necesita"), T("estrechas")
    t_abrir, t_anilla, t_leng = T("cómo la abres"), T("anilla"), T("lengüeta")
    t_bota, t_vacia, t_gas = T("cerrada aguanta"), T("pero vacía"), T("el propio gas")
    S["cutter"].location.y = -5.0 - 25 * (1 - seg(t, t_alu - 0.2, t_alu + 0.6)) if t < t_bota - 0.5 else -30
    # cuerpo crece al principio
    g = seg(t, 0.0, 0.8); S["lata"].scale = (1, 1, max(0.02, g))
    # paredes: gruesas al principio, finas al decirlo
    S["body"].modifiers["sol"].thickness = mix(0.09, 0.012, seg(t, t_fina, t_fina + 0.8))
    # papel de comparación
    S["papel"].location.z = 1.2 if t_fina - 0.1 < t < t_plano - 0.3 else -9
    # rueda de coche al comparar presiones
    S["rueda"].location.z = 1.2 if T("rueda") - 0.2 < t < t_alu - 0.2 else -9
    S["rueda"].rotation_euler.y = t * 2
    # fondo plano que se abomba / cúpula
    abom = seg(t, t_plano + 0.3, t_plano + 1.2) * (1 - seg(t, t_cup - 0.1, t_cup + 0.3))
    show(S["plano"], t < t_cup); show(S["domo"], t >= t_cup)
    S["plano"].scale = (1, 1, 1 + 8 * abom); S["plano"].location.z = 0.02 - 0.12 * abom
    tilt = 0.18 * abom * math.sin(t * 6)
    S["lata"].rotation_euler = (0, tilt, 0)
    # barniz interior
    body = S["body"]; body.data.materials[1].diffuse_color = (*lin(tuple(mix(a, b, seg(t, t_barniz, t_barniz + 0.6)) for a, b in zip(ALU, VARN))), 1)
    # cuello
    est = t >= t_cuello + 0.3
    show(S["cuello_r"], not est); show(S["cuello_e"], est)
    S["tapa"].scale = (0.76 if est else 1, 0.76 if est else 1, 1.6 if t >= t_tapa else 1)
    # anilla antigua: sale volando y se acumula en el suelo
    if t_anilla < t < t_leng:
        u = seg(t, t_anilla + 0.4, t_anilla + 1.4)
        S["anilla"].location = Vector((0.15 + 2.2 * u, -0.1, H0 + 0.1 + 1.6 * math.sin(u * math.pi)))
    else: S["anilla"].location = (0, 0, -9)
    rng = random.Random(3)
    for k, a in enumerate(S["anillas_suelo"]):
        x, y = rng.uniform(1.4, 4.2), rng.uniform(-1.5, 1.5)
        a.location = (x, y, 0.03) if t_anilla + 1.2 + k * 0.12 < t < t_bota else (0, 0, -9)
        a.rotation_euler = (0, 0, rng.uniform(0, 3))
    show(S["tab"], t >= t_leng)
    lev = seg(t, t_leng + 1.2, t_leng + 1.9)
    S["piv_tab"].rotation_euler = (0, -0.9 * lev, 0); S["panel"].location.z = H0 + 0.03 - 0.12 * lev
    # gas: burbujas y flechas de presión
    gas_on = t < T("tan finas") or (t_plano - 0.2 < t < t_cup + 1.5) or (t_gas - 0.3 < t)
    for k, b in enumerate(S["burb"]):
        r = random.Random(k)
        if gas_on and t < t_vacia:
            u = (t * 0.35 + k / 26) % 1.0; a = r.uniform(0, math.pi)
            b.location = Vector((r.uniform(-0.45, 0.45), r.uniform(0.0, 0.4), 0.3 + 1.4 * u))
        else: b.location = (0, 0, -9)
    fl = win01(t, T("empuja"), T("y quieres")) + win01(t, T("empuja hacia todos"), t_plano + 1.2) + win01(t, t_gas - 0.2, DUR)
    for f in S["flechas"]:
        a, z = f["a"], f["z"]
        if fl > 0.01 and math.cos(a) > -0.2 and t < t_vacia or (t > t_gas and fl > 0.01):
            d = 0.25 + 0.15 * math.sin(t * 5 + a * 3)
            f.location = Vector((math.cos(a) * d, math.sin(a) * d * 0.4 - 0.1, z)); f.scale = (fl,) * 3
            f.rotation_euler = (0, math.pi / 2, a)
        else: f.location = (0, 0, -9)
    # bota que pisa la lata llena (aguanta) y mano que aplasta la vacía
    bz = keyed(t, [(0, 30.0), (t_bota - 0.2, 12.0), (t_bota + 0.8, H0 + 0.06), (t_vacia - 0.4, H0 + 0.06), (t_vacia, 30.0)])
    S["bota"].location = (0.2, 0, bz)
    crush = seg(t, t_vacia + 0.9, t_vacia + 1.6) * (1 - seg(t, t_gas + 0.3, t_gas + 1.0))
    S["mano"].location = (0, 0, mix(9, H0 * 0.5 + 0.7, seg(t, t_vacia, t_vacia + 0.9)) - 1.25 * crush if t_vacia < t < t_gas + 1.0 else 30)
    S["lata"].scale = (1 + 0.12 * crush, 1 + 0.12 * crush, max(0.02, g) * (1 - 0.5 * crush))
    S["liq"].scale.z = 1.0 if t < t_vacia - 0.2 or t > t_gas + 0.5 else 0.0001
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def V(z, d, x=0.0, h=0.7, lens=34): return ((x, -d, z + h), (x * 0.4, 0, z), lens)
def CAM():
    return [(0.0,) + V(1.2, 8.5), (T("rueda") - 0.3,) + V(1.3, 9.5, 1.2), (T("aluminio"),) + V(1.2, 7.2), (T("tan finas"),) + V(1.5, 5.0, 0.8),
            (T("fondo plano"),) + V(0.6, 6.5, 0, 0.3), (T("cúpula") + 0.5,) + V(0.4, 4.6, 0, -0.1), (T("barniz"),) + V(1.4, 5.4),
            (T("la tapa necesita"),) + V(2.3, 5.0, 0, 1.0), (T("cómo la abres"),) + V(2.4, 4.2, 0, 1.4), (T("anilla") + 0.8,) + V(1.2, 8.5, 1.8, 2.0),
            (T("lengüeta"),) + V(2.4, 3.6, 0, 1.3), (T("cerrada aguanta") - 0.2,) + V(2.4, 12.0, 0, 1.0), (T("pero vacía"),) + V(1.6, 9.0, 0, 0.8),
            (T("el propio gas"),) + V(1.2, 7.5), (T("sígueme"),) + V(1.2, 8.5), (DUR + 2,) + V(1.2, 9.0)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"pared": Pj((-R0, -0.05, 1.4)), "fondo": Pj((0, -0.3, 0.1)), "tapa": Pj((0, -0.3, H0 + 0.1)), "lata": Pj((0, -R0, 1.2)),
            "rueda": Pj((3.4, 0.8, 1.2)), "tab": Pj((0.3, 0, H0 + 0.1)), "papel": Pj((2.4, -0.2, 1.9)), "suelo": Pj((2.8, 0, 0.05))}

if __name__ == "__main__":
    run("lata", build, pose, anchors)
