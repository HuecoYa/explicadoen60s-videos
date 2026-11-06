# «¿Se te ha mojado el móvil? El arroz no hace lo que crees»: el móvil cae al agua y salen burbujas por el puerto; se mete en
# arroz; se abre: juntas de goma (pantalla, botón, tapa); el puerto en corte con los pines, el agua con sales, el cargador,
# la corriente que salta de pin a pin y el óxido; la prueba de 24 h con barras (el arroz, la más baja); el móvil en el cuenco
# en corte (el agua del puerto sigue ahí y se cuelan granitos); qué hacer: secar, golpecitos, sitio ventilado, esperar.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Euler

T, DUR = cargar("arroz")
BG = (0.08, 0.09, 0.12); TABLE = (0.17, 0.18, 0.22)
FRAME = (0.24, 0.26, 0.31); BACK = (0.33, 0.36, 0.44); SCREEN = (0.12, 0.2, 0.36); BLACK = (0.04, 0.04, 0.05)
GASK = (1.0, 0.5, 0.15); PCB = (0.1, 0.34, 0.22); BATT = (0.18, 0.19, 0.23); METAL = (0.72, 0.74, 0.78); GOLD = (0.95, 0.75, 0.3)
WATER = (0.35, 0.65, 1.0); RICE = (0.96, 0.94, 0.86); RICE2 = (0.9, 0.87, 0.76); BOWL = (0.85, 0.35, 0.25)
YEL = (1.0, 0.9, 0.3); RUST = (0.35, 0.75, 0.45); ION = (1.0, 1.0, 1.0); PLUG = (0.92, 0.92, 0.94)
LEJOS = (0, 0, -400)
BOWL_C = Vector((0, 0, -17.5)); RICE_TOP = -14.8; FLAT_Z = -14.75
BARS = Vector((40, 0, -5)); BAR_H = [7.5, 6.0, 4.2, 2.6]; BAR_X = [-3.9, -1.3, 1.3, 3.9]
PORT = Vector((0, -7.12, 0))          # centro del puerto, coordenadas locales del móvil (plano)
PINX = [-0.3 + 0.12 * k for k in range(6)]

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def cutter_box(size, loc, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); c = bpy.context.object; c.scale = size; c.hide_render = True
    c.display_type = 'WIRE'
    if parent: c.parent = parent
    return c

def bool_cut(o, c, name="cut"):
    m = o.modifiers.new(name, "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = c; return o

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    rng = random.Random(7)
    # ---------- móvil (coordenadas locales: plano, pantalla hacia +z, puerto en -y) ----------
    S["PH"] = PH = empty((0, 0, 0)); PH.rotation_mode = 'XYZ'
    S["PHL"] = PHL = empty((0, 0, 0), parent=PH); PHL.rotation_euler = (math.pi / 2, 0, 0)
    S["frontcut"] = fc = cutter_box((2.4, 1.5, 0.9), (0, -7.0, 0.45 + 50), parent=PHL)
    cav = cutter_box((0.9, 0.8, 0.28), (0, -7.12, 0), parent=PHL)
    S["back"] = rounded_slab(7.2, 15.0, 1.0, 0.25, (0, 0, -0.4), BACK, parent=PHL)
    S["frame"] = fr = rounded_slab(7.2, 15.0, 1.0, 0.45, (0, 0, -0.15), FRAME, parent=PHL, unique=True)
    bool_cut(fr, cav, "cav"); bool_cut(fr, fc)
    g = rounded_slab(7.0, 14.8, 0.9, 0.03, (0, 0, 0.3), GASK, parent=PHL); bool_cut(g, fc)
    S["gasket"] = g
    inner = rounded_slab(6.5, 14.3, 0.7, 0.04, (0, 0, 0.3), PCB, parent=PHL); bool_cut(inner, fc)
    box((5.2, 8.0, 0.06), (0, 1.0, 0.34), BATT, parent=PHL)
    S["FRONT"] = FR = empty((0, 0, 0), parent=PHL)
    d = rounded_slab(6.9, 14.7, 0.88, 0.03, (0, 0, 0.33), BLACK, parent=FR); bool_cut(d, fc)
    gl = rounded_slab(7.1, 14.9, 0.95, 0.07, (0, 0, 0.36), SCREEN, parent=FR, unique=True); bool_cut(gl, fc)
    S["glass"] = gl
    # icono de aviso en la pantalla (gota azul dentro de un anillo rojo) y «todo bien» al final
    S["warn"] = w = empty((0, 0, 0), parent=FR)
    torus(1.25, 0.12, (0, 1.5, 0.45), (0.95, 0.25, 0.25), parent=w)
    sph(0.55, (0, 1.35, 0.45), WATER, parent=w, scale=(1, 1, 0.3))
    bpy.ops.mesh.primitive_cone_add(radius1=0.48, depth=0.8, location=(0, 1.85, 0.46), rotation=(-math.pi / 2, 0, 0))
    o = bpy.context.object; setup(o, WATER, w); o.scale = (1, 1, 1)
    S["ok"] = sph(0.9, (0, 1.5, 0.45), (0.3, 0.9, 0.45), parent=FR, scale=(1, 1, 0.15))
    S["iconos"] = []
    cols = [(0.95, 0.45, 0.3), (0.3, 0.75, 0.45), (0.35, 0.6, 1.0), (0.98, 0.8, 0.3)]
    for i in range(4):
        for j in range(2):
            S["iconos"].append(rounded_slab(1.0, 1.0, 0.25, 0.02, (-2.4 + 1.6 * i, -2.6 - 1.6 * j, 0.43), cols[(i + j) % 4], parent=FR))
    # botón lateral con su junta
    S["btn"] = box((0.22, 1.6, 0.22), (3.66, 3.2, 0.07), (0.45, 0.48, 0.55), parent=PHL)
    S["btng"] = box((0.06, 1.75, 0.3), (3.6, 3.2, 0.07), GASK, parent=PHL)
    # puerto por dentro
    box((0.9, 0.75, 0.025), (0, -7.12, -0.13), METAL, parent=PHL)
    for sx in (-0.44, 0.44): box((0.025, 0.75, 0.27), (sx, -7.12, 0), METAL, parent=PHL)
    box((0.9, 0.025, 0.27), (0, -6.76, 0), METAL, parent=PHL)
    box((0.66, 0.62, 0.05), (0, -7.05, 0), (0.12, 0.12, 0.14), parent=PHL)
    S["pins"] = [box((0.07, 0.44, 0.014), (x, -7.1, 0.031), GOLD, parent=PHL, unique=True) for x in PINX]
    S["rust"] = [sph(0.035, (x + 0.02 * rng.uniform(-1, 1), -7.1 + 0.3 * rng.uniform(-1, 1), 0.04), RUST, parent=PHL, scale=(1, 1.4, 0.5))
                 for x in PINX for _ in range(2)]
    S["pwater"] = pw = box((0.86, 0.72, 0.26), (0, -7.13, 0), WATER, parent=PHL, unique=True); alpha(pw, 0.45)
    S["ions"] = [sph(0.022, (0, 0, 0), ION if k % 2 else (1.0, 0.85, 0.35), parent=PHL, seg=8) for k in range(14)]
    S["ionp"] = [(rng.uniform(-0.38, 0.38), rng.uniform(-7.45, -6.82), rng.uniform(0.05, 0.11), rng.uniform(0, 6.28)) for _ in range(14)]
    S["spark"] = [sph(0.026, (0, 0, 0), YEL, parent=PHL, seg=8) for _ in range(10)]
    S["grains_in"] = [sph(0.05, (0, 0, 0), RICE, parent=PHL, scale=(1, 2.2, 1), seg=8) for _ in range(6)]
    # cargador (enchufa por el puerto; en local se mueve en -y)
    S["plug"] = pl = empty((500, 0, 0), parent=PHL)
    box((1.05, 1.6, 0.42), (0, -0.85, 0), PLUG, parent=pl)
    box((0.84, 0.7, 0.02), (0, 0.35, -0.11), METAL, parent=pl)
    for sx in (-0.41, 0.41): box((0.02, 0.7, 0.24), (sx, 0.35, 0), METAL, parent=pl)
    cyl(0.18, 6, (0, -5.2, 0), PLUG, parent=pl, rot=(math.pi / 2, 0, 0))
    # gotas sobre la pantalla
    S["drops"] = [sph(0.28 + 0.12 * rng.random(), (rng.uniform(-2.8, 2.8), rng.uniform(-6, 6.5), 0.45), WATER, parent=PHL,
                      scale=(1, 1.2, 0.35), unique=True) for _ in range(9)]
    for o in S["drops"]: alpha(o, 0.75)
    # ---------- agua del principio ----------
    S["water"] = wbox = box((40, 30, 20), (0, 6, -13), WATER, unique=True); alpha(wbox, 0.32)
    S["surf"] = sf = box((40, 30, 0.04), (0, 6, -3.0), (0.6, 0.82, 1.0), unique=True); alpha(sf, 0.45)
    S["splash"] = [sph(0.35, LEJOS, (0.7, 0.88, 1.0), seg=8) for _ in range(16)]
    S["bub"] = [sph(0.12 + 0.08 * (k % 3), LEJOS, (0.8, 0.92, 1.0), seg=10, unique=True) for k in range(14)]
    for o in S["bub"]: alpha(o, 0.7)
    S["fall"] = [sph(0.16, LEJOS, WATER, seg=8) for _ in range(8)]
    # ---------- cuenco de arroz (en corte por delante) ----------
    bc = cutter_box((40, 20, 30), (0, -7.6 - 10, BOWL_C.z))
    bw = cyl(10.0, 5.0, BOWL_C, BOWL, v=64, unique=True)
    m = bw.modifiers.new("s", "SOLIDIFY"); m.thickness = 0.5
    bm = bw.data
    # quitar la tapa de arriba del cilindro para que sea un cuenco
    import bmesh
    b = bmesh.new(); b.from_mesh(bm)
    top = [f for f in b.faces if f.normal.z > 0.9]; bmesh.ops.delete(b, geom=top, context='FACES'); b.to_mesh(bm); b.free()
    bool_cut(bw, bc)
    rf = cyl(9.7, 4.6, (0, 0, RICE_TOP - 2.3), RICE2, v=64); bool_cut(rf, bc)
    S["bowl"] = [bw, rf]
    gr = []
    for _ in range(520):
        a = rng.uniform(0, math.tau); r = 9.4 * math.sqrt(rng.random()); x, y = r * math.cos(a), r * math.sin(a)
        if y < -7.5: continue
        o = sph(0.32, (x, y, RICE_TOP + rng.uniform(0, 0.25)), RICE, scale=(1, 0.42, 0.42), seg=8)
        o.rotation_euler = (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, math.pi)); gr.append(o)
    # granos sueltos en el corte delantero
    for _ in range(90):
        x = rng.uniform(-9.3, 9.3); z = rng.uniform(RICE_TOP - 4.3, RICE_TOP)
        if x * x > 9.3 ** 2 - 7.6 ** 2: continue
        o = sph(0.3, (x, -7.58, z), RICE, scale=(1, 0.42, 0.42), seg=8); o.rotation_euler = (0, rng.uniform(0, 3.1), rng.uniform(-0.4, 0.4))
    # ---------- prueba de 24 h (barras) ----------
    box((13, 4, 0.5), BARS + Vector((0, 0, -0.25)), TABLE)
    S["bars"] = []
    cols = [(0.4, 0.7, 1.0), (0.4, 0.7, 1.0), (0.4, 0.7, 1.0), (0.95, 0.3, 0.3)]
    for x, c in zip(BAR_X, cols):
        cyl(1.05, 0.15, BARS + Vector((x, 0, 0.08)), (0.3, 0.32, 0.38))
        o = box((1.8, 1.8, 1), BARS + Vector((x, 0, 0.5)), c, unique=True); S["bars"].append(o)
    sph(0.9, BARS + Vector((-3.9, 0, -20)), (0.9, 0.9, 0.9))
    # ---------- final: soporte, paño, mano, aire, secador y bastoncillo ----------
    S["cloth"] = rounded_slab(4.0, 4.0, 0.6, 0.25, LEJOS, (0.55, 0.75, 0.95), unique=True)
    S["cloth"].rotation_euler = (math.pi / 2, 0, 0)
    S["palm"] = rounded_slab(8.0, 5.0, 2.0, 1.2, LEJOS, (0.93, 0.7, 0.58))
    S["stand"] = st = empty(LEJOS)
    box((6, 4, 0.6), (0, 0, -0.3), (0.32, 0.34, 0.4), parent=st); box((6, 0.5, 2.0), (0, 1.3, 0.6), (0.32, 0.34, 0.4), parent=st)
    S["air"] = [sph(0.1, LEJOS, (0.85, 0.95, 1.0), scale=(3, 1, 1), seg=8) for _ in range(18)]
    S["dryer"] = dr = empty(LEJOS)
    cyl(1.3, 4.0, (0, 0, 0), (0.9, 0.35, 0.5), parent=dr, rot=(0, math.pi / 2, 0))
    cyl(0.8, 1.6, (2.6, 0, 0), (0.75, 0.25, 0.4), parent=dr, rot=(0, math.pi / 2, 0))
    box((1.1, 1.0, 4.0), (-0.6, 0, -2.4), (0.9, 0.35, 0.5), parent=dr, rot=(0, 0.2, 0))
    S["swab"] = sw = empty(LEJOS)
    cyl(0.12, 6.0, (0, 0, 0), (0.95, 0.95, 0.97), parent=sw)
    for z in (3.1, -3.1): sph(0.32, (0, 0, z), (1, 1, 1), parent=sw, scale=(1, 1, 1.6))
    dyn = [cam, PH, S["water"], S["surf"], S["splash"], S["bub"], S["fall"], S["bars"], S["cloth"], S["palm"], S["stand"],
           S["air"], S["dryer"], S["swab"], bw, rf, bc]
    join_static(dyn)
    return sc, S

# ---------- tiempos ----------
def tiempos():
    return dict(arroz=T("meterlo en"), mira=T("mira dentro"), sell=T("tu móvil está"), pant=T("la pantalla"), bot=T("los botones"),
                tapa=T("y la tapa"), chap=T("por eso aguanta"), sitio=T("pero hay un sitio"), puerto=T("el puerto de"),
                pines=T("ahí dentro"), sales=T("el agua del grifo"), cond=T("y conduce"), ench=T("si enchufas"), salta=T("la corriente salta"),
                corr=T("y eso corroe"), mide=T("por eso tu móvil mide"), avisa=T("te avisa"), yarroz=T("y el arroz"),
                prueba=T("en una prueba"), crudo=T("el arroz crudo"), aire=T("incluso al aire"), toca=T("el arroz solo toca"),
                ni=T("el agua del puerto"), polvo=T("y encima"), entonces=T("entonces"), seca=T("sécalo"), golpe=T("dale golpecitos"),
                vent=T("déjalo en"), espera=T("espera al menos"), dia=T("y hasta un día"), nada=T("nada de secador"), sig=T("sígueme"))

def ph_pose(t, K):
    """posición del móvil (loc, rot_x extra: 0 = de pie, -pi/2 = tumbado)"""
    up, fl = 0.0, -math.pi / 2
    keys = [(0.0, (0, 0, 8.0), up), (0.6, (0, 0, -5.0), up), (1.3, (0, 0, -6.2), up), (2.4, (0, 0, -6.0), up),
            (3.6, (0, 0, 4.5), up), (K["arroz"] - 0.5, (0, 0, 4.5), up), (K["arroz"] + 0.5, (0, 0, FLAT_Z), fl),
            (K["mira"] - 0.5, (0, 0, FLAT_Z), fl), (K["mira"] + 0.6, (0, 0, 0), up), (K["yarroz"] - 0.3, (0, 0, 0), up),
            (K["yarroz"] + 0.8, (0, 0, FLAT_Z), fl), (K["entonces"], (0, 0, FLAT_Z), fl), (K["entonces"] + 1.2, (0, 0, 0), up),
            (DUR + 2, (0, 0, 0), up)]
    if t <= keys[0][0]: return Vector(keys[0][1]), keys[0][2]
    for (a, pa, ra), (b, pb, rb) in zip(keys, keys[1:]):
        if a <= t <= b:
            u = ((t - a) / (b - a)) ** 1.4 if a == 0.0 else ss((t - a) / max(b - a, 1e-4))
            return Vector(pa).lerp(Vector(pb), u), mix(ra, rb, u)
    return Vector(keys[-1][1]), keys[-1][2]

def loc2w(S, v):
    return S["PHL"].matrix_world @ Vector(v)

def pose(t, S):
    K = tiempos()
    loc, rx = ph_pose(t, K)
    # golpecitos con el puerto hacia abajo
    if K["golpe"] < t < K["vent"] - 0.2:
        loc = loc + Vector((0, 0, 0.5 * abs(math.sin((t - K["golpe"]) * math.pi * 2.2)) ** 0.6))
    S["PH"].location = loc; S["PH"].rotation_euler = (rx, 0, 0)
    bpy.context.view_layer.update()
    # despiece (juntas)
    ex = seg(t, K["pant"] - 0.3, K["pant"] + 0.4) * (1 - seg(t, K["chap"] - 0.2, K["chap"] + 0.4))
    S["FRONT"].location = (0, 0, 2.6 * ex)
    eb = seg(t, K["bot"], K["bot"] + 0.5) * (1 - seg(t, K["chap"] - 0.2, K["chap"] + 0.4))
    S["btn"].location = (3.66 + 1.0 * eb, 3.2, 0.07)
    et = seg(t, K["tapa"] - 0.1, K["tapa"] + 0.4) * (1 - seg(t, K["chap"] - 0.2, K["chap"] + 0.4))
    S["back"].location = (0, 0, -0.4 - 2.0 * et)
    # corte delantero del puerto
    cut_on = (K["sitio"] - 0.2 < t < K["yarroz"] + 0.6) or (K["toca"] - 1.5 < t < K["entonces"] + 0.8)
    S["frontcut"].location = (0, -7.0, 0.45 + (0 if cut_on else 50))
    # agua dentro del puerto
    lvl = seg(t, K["sitio"] + 0.3, K["puerto"] + 0.6)
    if t > K["golpe"]: lvl *= 1 - seg(t, K["golpe"], K["vent"])
    pw = S["pwater"]; pw.hide_render = lvl < 0.02
    pw.scale = (0.86, 0.72 * max(lvl, 0.02), 0.26); pw.location = (0, -7.49 + 0.36 * max(lvl, 0.02), 0)
    for (x, y, z, ph), o in zip(S["ionp"], S["ions"]):
        on = K["sales"] - 0.2 < t < K["yarroz"] and lvl > 0.5
        o.hide_render = not on
        o.location = (x + 0.03 * math.sin(t * 2 + ph), y + 0.03 * math.cos(t * 1.7 + ph), z + 0.02 * math.sin(t * 3 + ph))
        o.scale = (1.4 if K["sales"] < t < K["cond"] + 0.5 else 1.0,) * 3
    # cargador
    pin = seg(t, K["ench"], K["ench"] + 1.2) * (1 - seg(t, K["mide"] + 2.4, K["mide"] + 3.0))
    S["plug"].location = (0, -7.42 - 6.0 * (1 - pin), 0) if pin > 0.001 else (500, 0, 0)
    # chispas de pin a pin
    sp_on = K["salta"] - 0.1 < t < K["mide"] + 2.0
    for k, o in enumerate(S["spark"]):
        o.hide_render = not sp_on
        if sp_on:
            i = k % 5; u = ((t * 2.3 + k * 0.37) % 1.0); x = mix(PINX[i] + 0.035, PINX[i + 1] - 0.035, u)
            o.location = (x, -7.1 + 0.32 * math.sin(k * 2.1), 0.055 + 0.02 * math.sin(u * math.pi))
            o.scale = (1.0 if t < K["mide"] else 0.6,) * 3
    # óxido
    ru = seg(t, K["corr"], K["corr"] + 2.2)
    for k, o in enumerate(S["rust"]):
        s = ru * (0.7 + 0.6 * ((k * 37) % 10) / 10); o.hide_render = s < 0.02; o.scale = (s, 1.4 * s, 0.5 * s)
    for p in S["pins"]:
        set_color(p, tuple(mix(a, b, 0.55 * ru) for a, b in zip(GOLD, (0.55, 0.6, 0.35))))
    # granitos que se cuelan
    for k, o in enumerate(S["grains_in"]):
        u = seg(t, K["polvo"] + 0.6 + 0.3 * k, K["polvo"] + 1.6 + 0.3 * k)
        on = u > 0 and t < K["golpe"] + 0.3
        o.hide_render = not on
        o.location = (PINX[k] * 0.9, mix(-8.2, -7.05 - 0.05 * k, u), mix(0.35, 0.09, u))
        o.rotation_euler = (0, 0, 0.4 * k)
    # aviso en pantalla
    warn = (K["avisa"] - 0.1 < t < K["yarroz"] + 0.2) or (K["espera"] - 0.2 < t < K["nada"] + 0.4)
    S["warn"].location = (0, 0, 0) if warn else (500, 0, 0)
    S["ok"].location = (0, 0, 0) if t > K["sig"] - 0.2 else (500, 0, 0)
    # gotas sobre la pantalla: mojado al salir del agua y después del arroz; el paño las quita
    wipe_x = mix(-8, 8, seg(t, K["seca"], K["seca"] + 0.9))
    for k, o in enumerate(S["drops"]):
        x0 = o.location.x
        on = (2.0 < t < K["arroz"] + 0.6) or (K["entonces"] + 0.6 < t < K["seca"] + 1.0 and x0 > wipe_x - 0.5)
        o.hide_render = not on
        if on and t < K["arroz"]: o.location.y = o.location.y
    cl = S["cloth"]
    if K["seca"] - 0.2 < t < K["seca"] + 1.2:
        cl.location = (wipe_x, -1.0, -2 + 3 * math.sin((t - K["seca"]) * 6));
    else: cl.location = LEJOS
    # mano para los golpecitos
    S["palm"].location = LEJOS
    # soporte y aire
    S["stand"].location = (0, 0.3, -7.55) if t > K["vent"] - 0.1 else LEJOS
    for k, o in enumerate(S["air"]):
        if K["vent"] < t < K["nada"]:
            u = (t * 0.5 + k / 18) % 1.0; o.location = (mix(-9, 9, u), -1.5 - 1.2 * (k % 3), -6 + 13 * ((k * 7) % 18) / 18)
        else: o.location = LEJOS
    # secador y bastoncillo
    dn = seg(t, K["nada"] - 0.2, K["nada"] + 0.4) * (1 - seg(t, K["sig"], K["sig"] + 0.4))
    S["dryer"].location = (mix(-14, -5.2, dn), -3.5, 4.0) if dn > 0 else LEJOS
    S["swab"].location = (mix(14, 4.6, dn), -3.5, -2.5) if dn > 0 else LEJOS
    S["swab"].rotation_euler = (0, 0.5, 0)
    # agua del principio: salpicadura, burbujas, desaparece
    wv = 1 - seg(t, 3.2, 5.5)
    S["water"].location = (0, 6, -13 - 30 * (1 - wv)); S["surf"].location = (0, 6, -3.0 - 30 * (1 - wv))
    for k, o in enumerate(S["splash"]):
        u = (t - 0.25) / 1.0
        if 0 < u < 1:
            a = k * math.tau / 16; v = 2.5 + (k % 3)
            o.location = (v * u * math.cos(a) * 1.4, -0.6 + v * u * math.sin(a) * 0.6, -3.0 + 5 * u - 6 * u * u)
            o.scale = (1 - 0.5 * u,) * 3
        else: o.location = LEJOS
    port_w = loc2w(S, (0, -7.5, 0))
    for k, o in enumerate(S["bub"]):
        u = ((t * 0.9 + k / 14) % 1.0)
        if 0.6 < t < 3.3 and port_w.z + 5 * u < -3.1:
            o.location = port_w + Vector((0.6 * math.sin(k * 1.9 + t * 3), -0.8 - 0.3 * (k % 3), 5.0 * u))
        else: o.location = LEJOS
    for k, o in enumerate(S["fall"]):
        dr = (2.4 < t < K["arroz"] - 0.6) or (K["golpe"] < t < K["vent"])
        if dr:
            u = ((t * 1.3 + k / 8) % 1.0); o.location = port_w + Vector((0.3 * math.sin(k * 2.3), -0.1, -6 * u * u)); o.scale = (1 - 0.4 * u,) * 3
        else: o.location = LEJOS
    # barras de la prueba (24 h)
    pr = seg(t, K["prueba"] + 0.6, K["crudo"] + 0.3)
    for o, h, x in zip(S["bars"], BAR_H, BAR_X):
        hh = max(0.05, h * pr); o.scale = (1.8, 1.8, hh); o.location = BARS + Vector((x, 0, hh / 2 + 0.15))
    apply_cam(S["cam"], *cam_state(t, CAM(K), drift=0.03))

def V_(at, off, lens=40):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)

def CAM(K):
    k = []
    def add(t, v): k.append((t,) + v)
    P = (0, 0, -7.15)                        # puerto (de pie)
    BC = BARS + Vector((0.4, 0, 3.4))
    add(0.0, V_((0, 0, -1.0), (5.0, -21.0, 1.5), 38))
    add(1.5, V_((0, 0, -3.0), (4.0, -20.0, 1.0), 38))
    add(3.6, V_((0, 0, 1.5), (4.0, -21.0, 1.0), 38))
    add(K["arroz"] - 0.4, V_((0, 0, -2.0), (4.0, -21, 2.0), 38))
    add(K["arroz"] + 0.6, V_((0, -2, -15.0), (5.0, -17, 9.0), 38))
    add(K["mira"] - 0.3, V_((0, -2, -14.5), (4.0, -17, 8.0), 38))
    add(K["sell"], V_((0, -0.6, 0.0), (-14, -15, 5.0), 38))
    add(K["pant"] + 0.4, V_((0, -1.4, 0.5), (-17, -10, 5.0), 38))
    add(K["tapa"], V_((1.0, -0.8, 1.0), (17, -11, 5.0), 38))
    add(K["chap"], V_((0, 0, 0.0), (6, -21, 3.0), 38))
    add(K["sitio"], V_((0, 0, -3.5), (3, -16, 0.5), 38))
    add(K["puerto"] - 0.2, V_((0, 0, -6.6), (1.2, -6.0, 0.4), 40))
    add(K["puerto"] + 0.6, V_(P, (0.6, -3.4, 0.5), 40))
    add(K["pines"] + 0.5, V_(P, (0.35, -2.4, 0.35), 42))
    add(K["sales"] + 0.5, V_(P, (0.2, -2.1, 0.3), 42))
    add(K["ench"], V_((0, 0, -7.4), (1.0, -3.4, 0.6), 40))
    add(K["salta"], V_(P, (0.3, -2.3, 0.45), 42))
    add(K["corr"] + 0.5, V_(P, (-0.3, -2.1, 0.4), 42))
    add(K["mide"], V_(P, (0.3, -2.6, 0.5), 42))
    add(K["mide"] + 1.0, V_(P, (0.4, -3.0, 0.6), 42))
    add(K["mide"] + 1.8, V_((0, 0, -6.0), (1.0, -6.0, 0.8), 42))
    add(K["avisa"] - 0.4, V_((0, 0, -1.0), (3, -20, 1.0), 40))
    add(K["yarroz"] - 0.1, V_((0, 0, -0.5), (3, -21, 1.0), 40))
    add(K["yarroz"] + 0.9, V_((0, -3, -15.0), (6, -18, 9.0), 38))
    add(K["prueba"] - 0.2, V_((0, -3, -15.0), (6, -20, 10.0), 38))
    add(K["prueba"] + 0.6, V_(tuple(BC), (1.0, -23, 3.0), 34))
    add(K["prueba"] + 2.0, V_(tuple(BC), (0.5, -23, 2.8), 34))
    add(K["aire"] + 0.6, V_(tuple(BC), (-0.5, -23, 2.6), 34))
    add(K["aire"] + 1.5, V_(tuple(BC), (-1.0, -23, 2.5), 34))
    add(K["toca"] - 0.1, V_((0, -7.1, FLAT_Z + 0.2), (5.0, -12.0, 5.0), 38))
    add(K["ni"], V_((0, -7.2, FLAT_Z), (1.4, -3.6, 2.0), 40))
    add(K["polvo"] + 0.6, V_((0, -7.2, FLAT_Z), (1.2, -3.2, 1.8), 40))
    add(K["entonces"], V_((0, -7.2, FLAT_Z), (2.0, -4.5, 2.6), 40))
    add(K["entonces"] + 1.3, V_((0, 0, 0), (4, -22, 2.0), 38))
    add(K["seca"] + 1.0, V_((0, 0, 0), (-4, -22, 1.5), 38))
    add(K["golpe"] + 0.5, V_((0, 0, -3.0), (3, -19, 0.5), 38))
    add(K["vent"], V_((0, 0, -1.0), (4, -23, 1.5), 38))
    add(K["espera"], V_((0, 0, 0.5), (2, -21, 1.0), 38))
    add(K["nada"], V_((-0.3, 0, 0.5), (0, -31, 1.5), 38))
    add(K["sig"], V_((0, 0, 0.5), (2, -28, 1.5), 38))
    add(DUR + 2, V_((0, 0, 0.5), (3, -27, 2.0), 38))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); L = lambda v: Pj(loc2w(S, v))
    d = {"port": L((0, -7.5, 0.0)), "pins": L((0, -7.1, 0.05)), "ions": L((0.2, -7.3, 0.1)), "gask": L((-3.45, 3.0, 0.32)),
         "btn": L((3.9, 3.2, 0.1)), "back": L((-2.5, 4.0, -0.5)), "screen": L((0, 1.5, 0.6)), "plug": L((0, -8.6, 0)),
         "dryer": Pj(S["dryer"].location), "swab": Pj(S["swab"].location), "phone": L((0, 0, 0.4)), "case": L((3.6, -5.0, 0.2))}
    for k, (x, h) in enumerate(zip(BAR_X, BAR_H)):
        o = S["bars"][k]; d["bar%d" % k] = Pj(BARS + Vector((x, -0.9, 0))); d["bartop%d" % k] = Pj(BARS + Vector((x, 0, o.scale.z + 0.2)))
    return d

if __name__ == "__main__":
    run("arroz", build, pose, anchors)
