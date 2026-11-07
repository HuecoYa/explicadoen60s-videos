# «Si tuvieras que inventar la placa de inducción»: olla hirviendo sobre la placa (en corte) y un dedo que toca el cristal
# de al lado; el fuego de gas pierde calor por los lados; bajo el cristal, una bobina de cobre con corriente alterna;
# el campo magnético sube, atraviesa el cristal y entra en el fondo de la olla; remolinos de corriente calientan el
# metal; el imán se pega a la olla de hierro pero no a la sartén de aluminio (no se calienta); el cristal solo se
# calienta por la olla y se enfría al quitarla; sin metal encima, la placa corta la corriente y el piloto parpadea.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("induccion")
BG = (0.09, 0.09, 0.11); WOODC = (0.26, 0.19, 0.14); GLASS = (0.07, 0.07, 0.09); HOUSE = (0.3, 0.31, 0.35); INNER = (0.55, 0.56, 0.6); CU = (0.92, 0.52, 0.25)
CU_ON = (1.0, 0.8, 0.45); FERR = (0.2, 0.2, 0.22); STEEL = (0.72, 0.74, 0.78); IRON = (0.32, 0.33, 0.36); WATER = (0.35, 0.6, 0.95)
ALU = (0.86, 0.87, 0.9); FIELD = (0.35, 0.85, 1.0); HOT = (1.0, 0.35, 0.1); SKIN = (0.93, 0.7, 0.58); FLAME = (0.35, 0.6, 1.0)
FLAME2 = (1.0, 0.65, 0.2); RED = (0.95, 0.25, 0.2); WOOD = (0.55, 0.38, 0.25); PCB = (0.15, 0.45, 0.3); WHITE = (0.96, 0.96, 0.98)
LEJOS = Vector((0, 0, -300))
FONT = os.path.expanduser("~/.fonts/Poppins-Bold.ttf")
PR = 1.45   # radio de la olla

def put(o, p, s=1.0):
    o.location = p; o.scale = (s, s, s) if isinstance(s, (int, float)) else s
def hide(o): o.location = LEJOS

def vaso(r, h, loc, color, v=64):
    me = bpy.data.meshes.new("vaso"); bm = bmesh.new()
    a = [bm.verts.new((r * math.cos(0.01 + 2 * math.pi * k / v), r * math.sin(0.01 + 2 * math.pi * k / v), 0)) for k in range(v)]
    b = [bm.verts.new((r * math.cos(0.01 + 2 * math.pi * k / v), r * math.sin(0.01 + 2 * math.pi * k / v), h)) for k in range(v)]
    for k in range(v): j = (k + 1) % v; bm.faces.new((a[k], a[j], b[j], b[k]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("vaso", me); bpy.context.collection.objects.link(o); o.location = loc
    return setup(o, color, unique=True)

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam}; dyn = [cam]
    rng = random.Random(3)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(5.0, -5.0, 0)); cutter = bpy.context.object; cutter.scale = (10, 10, 20); cutter.hide_render = True
    bpy.ops.mesh.primitive_cube_add(size=1, location=(5.0, -5.0, 0)); cut2 = bpy.context.object; cut2.scale = (10, 10, 20); cut2.hide_render = True
    dyn += [cutter, cut2]
    def cortar(o, th=None, inner=INNER, c=cutter):
        if th:
            o.data.materials.append(mat(inner, unique=True))
            m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1; m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = c; return o
    # encimera de madera
    box((30, 20, 1.0), (0, 4, -1.45), WOODC)
    # placa: cristal negro y carcasa, cortados por la esquina delantera derecha
    S["glass"] = cortar(box((7.5, 5.2, 0.12), (0.4, 0.6, -0.06), GLASS, unique=True)); dyn.append(S["glass"])
    S["house"] = cortar(box((7.3, 5.0, 0.8), (0.4, 0.6, -0.52), HOUSE, unique=True)); dyn.append(S["house"])
    for x, y in ((0, 0), (-2.9, 1.6)):
        torus(1.55 if x == 0 else 0.9, 0.02, (x, y, 0.002), (0.45, 0.45, 0.5), unique=False)
    # mandos táctiles
    for k in range(4): sph(0.08, (-2.2 + 0.5 * k, -1.65, 0.003), (0.5, 0.5, 0.55), scale=(1, 1, 0.1), seg=8)
    S["led"] = text3d("U", (-1.0, -1.7, 0.01), 0.9, (1.0, 0.15, 0.1), extrude=0.005, unique=True)
    if os.path.exists(FONT): S["led"].data.font = bpy.data.fonts.load(FONT, check_existing=True)
    dyn.append(S["led"])
    # mancha de calor en el cristal (solo por la olla)
    S["spot"] = cortar(cyl(1.45, 0.01, (0, 0, 0.004), GLASS, unique=True)); dyn.append(S["spot"])
    # bobina: anillos de cobre, ferritas y placa electrónica
    S["coil"] = [torus(0.32 + 0.105 * k, 0.042, (0, 0, -0.26), CU, unique=True) for k in range(10)]
    dyn += S["coil"]
    for k in range(8):
        a = k * math.tau / 8
        box((1.2, 0.18, 0.1), (0.85 * math.cos(a), 0.85 * math.sin(a), -0.4), FERR, rot=(0, 0, a))
    box((2.4, 1.2, 0.06), (-2.2, 1.6, -0.7), PCB)
    for k in range(5): cyl(0.12, 0.3, (-3.0 + 0.4 * k, 1.5, -0.52), (0.2, 0.3, 0.6))
    S["scan"] = [torus(1.0, 0.03, LEJOS, (1.0, 0.9, 0.3), unique=True) for _ in range(2)]; dyn += S["scan"]
    S["els"] = [sph(0.06, LEJOS, (1.0, 0.95, 0.5), seg=8, unique=True) for _ in range(10)]; dyn += S["els"]
    # olla de acero con fondo de hierro, en corte
    S["pot"] = pot = empty((0, 0, 0)); dyn.append(pot)
    w = cortar(vaso(PR, 1.45, (0, 0, 0.18), STEEL), th=0.07, c=cut2); w.parent = pot; dyn.append(w)
    S["bottom"] = b = cortar(cyl(PR, 0.18, (0, 0, 0.09), IRON, unique=True), c=cut2); b.parent = pot; dyn.append(b)
    S["water"] = wa = cortar(cyl(PR - 0.08, 0.85, (0, 0, 0.6), WATER, unique=True), c=cut2); wa.parent = pot; dyn.append(wa)
    for sx in (-1, 1):
        box((0.55, 0.22, 0.14), (sx * (PR + 0.25), 0, 1.4), (0.15, 0.15, 0.17), parent=pot)
    S["bub"] = [sph(rng.uniform(0.05, 0.1), LEJOS, (0.8, 0.9, 1.0), seg=8) for _ in range(16)]
    S["bubp"] = [(rng.uniform(0.1, 1.2), rng.uniform(0, math.tau), rng.uniform(0, 1)) for _ in range(16)]
    S["steam"] = [sph(0.35, LEJOS, (0.92, 0.94, 0.97), seg=12, unique=True, scale=(1, 1, 0.6)) for _ in range(6)]
    for o in S["steam"]:
        m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], 0.45); m.surface_render_method = 'BLENDED'

    dyn += S["bub"] + S["steam"]
    # remolinos en el fondo
    S["eddy"] = []
    for k in range(3):
        e = empty(LEJOS); torus(0.26, 0.035, (0, 0, 0), (1.0, 0.9, 0.3), parent=e)
        sph(0.08, (0.26, 0, 0), (1.0, 0.9, 0.3), parent=e, seg=8)
        S["eddy"].append(e)
    dyn += S["eddy"]
    # líneas de campo
    S["loops"] = []
    for k in range(6):
        a = k * math.tau / 6 + 0.3
        o = torus(1.0, 0.03, LEJOS, FIELD, unique=True); o["a"] = a; S["loops"].append(o)
    dyn += S["loops"]
    # fuego de gas
    S["burner"] = bu = empty(LEJOS)
    cyl(0.9, 0.15, (0, 0, 0.07), (0.15, 0.15, 0.17), parent=bu)
    S["flames"] = []
    for k in range(16):
        a = k * math.tau / 16
        o = sph(0.12, (0.85 * math.cos(a), 0.85 * math.sin(a), 0.4), FLAME, parent=bu, scale=(1, 1, 2.6), seg=10, unique=True); S["flames"].append(o)
    S["heat"] = [bar_obj(FLAME2, 0.06, unique=True) for _ in range(8)]
    dyn += [bu] + S["heat"]
    # sartén de aluminio
    S["pan"] = pan = empty(LEJOS)
    cyl(1.3, 0.08, (0, 0, 0.04), ALU, parent=pan)
    vv = vaso(1.3, 0.45, (0, 0, 0.0), ALU); vv.parent = pan
    m = vv.modifiers.new("s", "SOLIDIFY"); m.thickness = 0.05
    box((1.8, 0.2, 0.1), (-2.1, 0, 0.35), (0.15, 0.15, 0.17), parent=pan)
    dyn.append(pan)
    # imán de herradura
    S["mag"] = mg = empty(LEJOS)
    torus(0.32, 0.12, (0, 0, 0), RED, parent=mg, rot=(math.pi / 2, 0, 0))
    for sx in (-1, 1):
        box((0.24, 0.24, 0.45), (sx * 0.32, 0, -0.22), RED, parent=mg)
        box((0.24, 0.24, 0.14), (sx * 0.32, 0, -0.5), (0.85, 0.86, 0.9), parent=mg)
    dyn.append(mg)
    # dedo
    S["finger"] = fi = empty(LEJOS)
    d = Vector((-0.35, 0.25, 1.0)).normalized()
    sph(0.28, (0, 0, 0.28), SKIN, parent=fi)
    o = cyl(0.3, 2.6, d * 1.3 + Vector((0, 0, 0.28)), SKIN, parent=fi); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    sph(0.2, (0.02, -0.1, 0.48), (0.97, 0.82, 0.78), parent=fi, scale=(1, 0.5, 1.1))
    dyn.append(fi)
    join_static(dyn)
    return sc, S

def K():
    return dict(frio=T("pero el cristal"), como=T("¿cómo?"), quieres=T("quieres calentar"), fuego=T("con fuego"), gas=T("con gas"),
                dentro=T("así que pones"), bobina=T("debajo del cristal"), corriente=T("le metes"), campo=T("eso crea"), atrav=T("atraviesa"),
                entra=T("y entra"), remol=T("ahí dentro"), metal=T("y el metal"), calienta=T("se calienta"), noval=T("pero no vale"),
                iman=T("tiene que ser"), hierro=T("como el hierro"), sarten=T("si tu sartén"), entera=T("la placa ni"), curioso=T("y aquí viene"),
                nocal=T("la bobina no"), solo=T("el cristal solo"), enfria=T("por eso se enfría"), noventa=T("y así aprovechas"),
                prob=T("pero ahora hay"), quitas=T("si quitas"), mide=T("así que la placa"), nodet=T("si no detecta"), corta=T("corta la"),
                parp=T("por eso parpadea"), sig=T("sígueme"))

def pot_state(t, k):
    """posición de la olla y si está sobre la zona"""
    p = Vector((0, 0, 0))
    up = seg(t, k["fuego"] - 0.4, k["fuego"] + 0.2) * (1 - seg(t, k["dentro"], k["dentro"] + 0.6))
    p.z += 0.75 * up
    out = seg(t, k["sarten"] - 0.5, k["sarten"] + 0.3) * (1 - seg(t, k["curioso"] - 0.3, k["curioso"] + 0.4))
    p.x += 4.6 * out
    lift = seg(t, k["enfria"] - 0.2, k["enfria"] + 0.6) * (1 - seg(t, k["noventa"], k["noventa"] + 0.6))
    p.z += 1.3 * lift
    lift2 = seg(t, k["quitas"] - 0.2, k["quitas"] + 0.6) * (1 - seg(t, k["sig"] - 0.2, k["sig"] + 0.4))
    hover = 0.6 * (0.5 + 0.5 * math.sin((t - k["parp"]) * 4.5)) * seg(t, k["parp"], k["parp"] + 0.3) * (1 - seg(t, k["sig"] - 0.4, k["sig"]))
    p.z += 1.2 * lift2 if t < k["parp"] else (0.9 + hover) * lift2
    p.x -= 2.8 * lift2 * (1 - seg(t, k["parp"] - 0.6, k["parp"]))
    on = p.length < 0.3
    return p, on, out

def pose(t, S):
    k = K()
    p, on_zone, out = pot_state(t, k)
    S["pot"].location = p
    # ¿hay corriente en la bobina?
    detect_off = k["corta"] < t < k["sig"] - 0.2
    gas_phase = k["fuego"] - 0.4 < t < k["dentro"] + 0.4
    coil_on = (not gas_phase) and not detect_off and not (k["bobina"] - 0.1 < t < k["corriente"])
    coil_vis = seg(t, k["bobina"], k["bobina"] + 1.4)
    pre = t < k["fuego"] - 0.4
    for i, o in enumerate(S["coil"]):
        g = 1.0 if (pre or t > k["corriente"]) else (seg(t, k["bobina"] + 0.12 * i, k["bobina"] + 0.12 * i + 0.4) if t > k["bobina"] else 0.0)
        if gas_phase or g <= 0: hide(o); continue
        put(o, Vector((0, 0, -0.26)), g)
        if coil_on and t > k["corriente"] - 0.1 or (pre and coil_on):
            f = 0.5 + 0.5 * math.sin(t * 22 + i * 0.6)
            set_color(o, tuple(mix(a, b, f) for a, b in zip(CU, CU_ON)))
        else: set_color(o, CU)
    # electrones que van y vienen por la bobina
    for i, e in enumerate(S["els"]):
        if k["corriente"] < t < k["campo"] + 1.0:
            ang = i * math.tau / 10 + 0.9 * math.sin(t * 9)
            r = 1.27
            put(e, Vector((r * math.cos(ang), r * math.sin(ang), -0.2)), 1.0)
        else: hide(e)
    # líneas de campo
    field_on = coil_on and on_zone and (t < k["fuego"] - 0.4 or t > k["campo"]) and not (k["entera"] < t < k["curioso"] and False)
    if k["sarten"] - 0.5 < t < k["curioso"]: field_on = coil_on    # con la sartén de aluminio el campo pasa, pero no calienta
    rise = seg(t, k["campo"], k["atrav"] + 0.8) if t < k["remol"] + 2 else 1.0
    if t < k["fuego"]: rise = 1.0
    for o in S["loops"]:
        if not field_on: hide(o); continue
        a = o["a"]; puls = 1 + 0.06 * math.sin(t * 14)
        o.location = Vector((0.75 * math.cos(a), 0.75 * math.sin(a), -0.75 + 0.75 * rise))
        o.rotation_euler = (math.pi / 2, 0, a + math.pi / 2)
        o.scale = (0.55 * puls, 0.75 * rise * puls + 0.001, 0.55 * puls)
    # fondo de la olla: se calienta
    heat = 0.0
    if t < k["fuego"] - 0.4: heat = 1.0
    elif t > k["remol"]: heat = seg(t, k["remol"], k["calienta"] + 0.6)
    if k["sarten"] - 0.5 < t < k["curioso"]: heat *= 0.3
    if t > k["corta"]: heat *= 1 - seg(t, k["corta"], k["parp"])
    if t > k["sig"]: heat = seg(t, k["sig"], k["sig"] + 0.8)
    set_color(S["bottom"], tuple(mix(a, b, heat) for a, b in zip(IRON, HOT)))
    # remolinos
    for i, e in enumerate(S["eddy"]):
        if k["remol"] < t < k["noval"]:
            g = seg(t, k["remol"] + 0.2 * i, k["remol"] + 0.2 * i + 0.4)
            pos = Vector((0.45 + 0.42 * i, -0.35 - 0.3 * i, 0.19)) + p
            put(e, pos, g + 0.001); e.rotation_euler = (0, 0, t * 9 * (1 if i % 2 else -1))
        else: hide(e)
    # burbujas y vapor (cuando hierve)
    boil = 1.0 if t < k["fuego"] - 0.4 else 0.0
    if t > k["calienta"]: boil = 1.0 if (t < k["sarten"] - 0.5 or t > k["curioso"]) else 0.0
    if k["corta"] < t < k["sig"]: boil = 0.0
    if k["enfria"] - 0.2 < t: boil = boil if (t > k["sig"]) else 0.0
    if t > k["sig"]: boil = 1.0
    for (o, (r, a, ph)) in zip(S["bub"], S["bubp"]):
        if boil:
            u = (t * 0.9 + ph) % 1.0
            put(o, p + Vector((r * math.cos(a), r * math.sin(a), 0.25 + 0.75 * u)), 1.0)
        else: hide(o)
    for i, o in enumerate(S["steam"]):
        if boil:
            u = (t * 0.35 + i / 6) % 1.0
            put(o, p + Vector((0.6 * math.sin(i * 2.3), 0.4 * math.cos(i * 1.7), 1.7 + 1.6 * u)), ((0.3 + 0.8 * u) * (1 - u) * 2,) * 2 + ((0.3 + 0.8 * u) * (1 - u) * 1.2,))
        else: hide(o)
    # mancha de calor en el cristal: solo por contacto con la olla caliente
    gw = 0.0
    if t < k["fuego"] - 0.4: gw = 0.35
    elif t > k["solo"]: gw = 0.6 * seg(t, k["solo"], k["solo"] + 2.0) * (1 - seg(t, k["enfria"] + 0.3, k["enfria"] + 2.4))
    set_color(S["spot"], tuple(mix(a, b, gw) for a, b in zip(GLASS, (0.55, 0.12, 0.06))))
    # fuego de gas
    if gas_phase:
        g = seg(t, k["fuego"] - 0.3, k["fuego"] + 0.2) * (1 - seg(t, k["dentro"], k["dentro"] + 0.4))
        put(S["burner"], Vector((0, 0, 0)), g + 0.001)
        for i, f in enumerate(S["flames"]):
            f.scale = (1, 1, 2.6 * (0.8 + 0.25 * math.sin(t * 17 + i)))
        for i, h in enumerate(S["heat"]):
            a = i * math.tau / 8 + 0.2
            u = ((t * 0.8 + i * 0.37) % 1.0)
            b0 = Vector(((PR + 0.05) * math.cos(a), (PR + 0.05) * math.sin(a), 0.65))
            b1 = b0 + Vector((math.cos(a) * 0.9, math.sin(a) * 0.9, 1.6)) * (0.3 + 0.7 * u)
            if g > 0.5 and t > k["fuego"] + 0.6: bar_set(h, b0 + Vector((math.cos(a), math.sin(a), 1.2)) * 0.6 * u, b1)
            else: hide(h); h.scale = (0.001,) * 3
    else:
        hide(S["burner"])
        for h in S["heat"]: hide(h); h.scale = (0.001,) * 3
    # sartén de aluminio
    if k["sarten"] - 0.6 < t < k["curioso"] + 0.4:
        inn = seg(t, k["sarten"] - 0.5, k["sarten"] + 0.3) * (1 - seg(t, k["curioso"] - 0.3, k["curioso"] + 0.4))
        put(S["pan"], Vector((-4.6 * (1 - inn), 0, 0)), 1.0)
    else: hide(S["pan"])
    # imán: se pega a la olla de hierro, resbala de la de aluminio
    mg = S["mag"]
    if k["iman"] < t < k["hierro"] + 1.6:
        u = seg(t, k["iman"] + 0.3, k["iman"] + 1.1)
        put(mg, Vector((mix(-3.4, -PR - 0.1, u), -0.4, 1.0)), 1.0); mg.rotation_euler = (0, -math.pi / 2, 0)
        if t > k["hierro"] + 0.6: mg.location.z += 4 * seg(t, k["hierro"] + 0.6, k["hierro"] + 1.6)
    elif k["sarten"] < t < k["entera"] + 0.8:
        u = seg(t, k["sarten"] + 0.1, k["sarten"] + 0.8); fall = seg(t, k["sarten"] + 0.9, k["sarten"] + 1.5)
        put(mg, Vector((mix(-3.4, -1.45, u), -0.4, mix(0.6, 0.1, fall))), 1.0); mg.rotation_euler = (0, -math.pi / 2 + 1.2 * fall, 0)
    else: hide(mg)
    # dedo que toca el cristal frío
    fi = S["finger"]
    if t < k["como"] + 0.3:
        press = 0.25 * (0.5 + 0.5 * math.cos(t * 4.0))
        put(fi, Vector((-2.35, -0.9, 0.0 + press + 3.0 * seg(t, k["como"] - 0.4, k["como"] + 0.3))), 1.0)
    else: hide(fi)
    # la placa busca metal: ondas que salen de la bobina
    for i, o in enumerate(S["scan"]):
        if k["mide"] < t < k["corta"]:
            u = ((t - k["mide"]) * 0.9 + i / 2) % 1.0
            put(o, Vector((0, 0, 0.02 + 1.4 * u)), 0.4 + 1.2 * u)
        else: hide(o)
    # piloto que parpadea
    led_on = k["parp"] < t < k["sig"] and (int(t * 3) % 2 == 0)
    S["led"].hide_render = not led_on
    apply_cam(S["cam"], *cam_state(t, CAM(k), drift=0.03))

def V_(at, off, lens=50):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)

def CAM(k):
    c = []
    def add(t, v): c.append((t,) + v)
    add(-1, V_((-0.8, -0.3, 0.6), (3.0, -7.4, 4.0)))
    add(0.0, V_((-0.8, -0.3, 0.6), (2.8, -7.0, 3.8)))
    add(k["frio"] + 0.5, V_((-1.3, -0.5, 0.4), (2.5, -7.5, 3.8)))
    add(k["quieres"], V_((0.0, 0, 1.0), (3.5, -9.5, 4.0)))
    add(k["gas"], V_((0.0, 0, 1.5), (3.0, -10.5, 3.2)))
    add(k["dentro"] + 0.5, V_((0.3, -0.3, 0.6), (3.5, -9, 3.5)))
    add(k["bobina"] + 0.6, V_((0.3, -0.6, -0.1), (3.4, -7.4, 3.0)))
    add(k["corriente"] + 2.5, V_((0.3, -0.6, -0.1), (2.8, -7.2, 2.4)))
    add(k["campo"] + 0.3, V_((0.25, -0.5, 0.2), (3.3, -7.8, 2.0)))
    add(k["entra"] + 0.5, V_((0.25, -0.5, 0.3), (3.0, -7.6, 2.1)))
    add(k["remol"] + 0.5, V_((0.35, -0.6, 0.2), (2.6, -6.6, 3.0)))
    add(k["calienta"] + 0.3, V_((0.3, -0.5, 0.4), (3.0, -7.4, 3.0)))
    add(k["iman"], V_((-0.6, -0.3, 0.7), (1.0, -9.5, 2.8)))
    add(k["hierro"] + 0.5, V_((-0.6, -0.3, 0.7), (0.6, -9.3, 2.6)))
    add(k["sarten"] + 0.5, V_((-0.3, -0.3, 0.4), (1.5, -8.5, 3.2)))
    add(k["curioso"] + 0.3, V_((0.0, -0.3, 0.6), (2.5, -9.0, 3.4)))
    add(k["solo"] + 1.0, V_((0.0, -0.3, 0.4), (2.0, -8.0, 3.8)))
    add(k["enfria"] + 1.2, V_((0.0, -0.3, 0.8), (1.5, -9.0, 3.5)))
    add(k["noventa"] + 1.0, V_((0.0, -0.3, 0.8), (3.0, -9.0, 3.5)))
    add(k["quitas"] + 0.5, V_((-0.6, -0.3, 0.8), (2.5, -11.0, 3.4)))
    add(k["mide"] + 0.5, V_((0.4, -0.4, 0.3), (2.2, -7.5, 3.6)))
    add(k["corta"] + 0.5, V_((0.6, -0.5, 0.2), (2.0, -6.8, 3.0)))
    add(k["parp"] + 0.5, V_((0.0, -0.6, 0.9), (1.8, -10.5, 3.2)))
    add(k["sig"] + 0.5, V_((0.0, -0.3, 0.8), (2.6, -9.0, 3.6)))
    add(DUR + 2, V_((0.0, -0.3, 0.8), (2.8, -9.8, 3.8)))
    return c

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    p = S["pot"].location
    return {"pot": Pj(p + Vector((0, 0, 1.6))), "bottom": Pj(p + Vector((0.9, -0.9, 0.1))), "glassF": Pj(Vector((-2.35, -0.9, 0.0))),
            "coil": Pj(Vector((1.0, -0.9, -0.3))), "glass": Pj(Vector((1.5, -1.6, 0.0))), "mag": Pj(S["mag"].location),
            "pan": Pj(S["pan"].location + Vector((0, 0, 0.5))), "led": Pj(Vector((-1.0, -1.7, 0.0))), "flame": Pj(Vector((0, -1.0, 0.4)))}

if __name__ == "__main__":
    run("induccion", build, pose, anchors)
