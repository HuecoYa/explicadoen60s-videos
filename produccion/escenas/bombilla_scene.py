# «Si tuvieras que inventar la bombilla»: bombilla clásica encendida que se desmonta; hilo que se calienta y brilla;
# en el aire se quema; ampolla sin oxígeno; 90 % calor / 10 % luz; se cambia por un chip LED (los electrones saltan y
# sueltan luz azul); capa de fósforo amarilla → blanco; circuito en la base; disipador de aluminio; resultado.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("bombilla")
BRASS = (0.85, 0.75, 0.45); GLASS = (0.85, 0.92, 1.0); WIRE = (0.55, 0.55, 0.6); COLD = (0.3, 0.3, 0.33); HOT = (1.0, 0.85, 0.45)
RED = (0.95, 0.35, 0.2); O2C = (0.95, 0.3, 0.3); PCB = (0.95, 0.95, 0.95); CHIP = (0.95, 0.85, 0.35); NC = (0.35, 0.5, 0.9); PC = (0.9, 0.4, 0.35)
BLUE = (0.3, 0.55, 1.0); YEL = (1.0, 0.85, 0.25); ALU = (0.75, 0.78, 0.82); GREEN = (0.15, 0.55, 0.3)
CZ = 3.6       # centro de la ampolla
FZ = 3.55      # altura del hilo
CHZ = 3.05     # altura del chip LED

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def helix(x0, x1, r, turns, z, color):
    cu = bpy.data.curves.new("hx", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.022; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); n = int(turns * 16); sp.points.add(n)
    for k in range(n + 1):
        u = k / n; a = 2 * math.pi * turns * u
        sp.points[k].co = (mix(x0, x1, u), r * math.cos(a), z + r * math.sin(a), 1)
    o = bpy.data.objects.new("hx", cu); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(color, unique=True)); return o

def build():
    sc, cam = scene_setup(world=(0.07, 0.08, 0.11), shadow=0.3)
    S = {"cam": cam}
    bpy.ops.mesh.primitive_cube_add(size=1, location=(12, -5.0, 1.5)); cutter = bpy.context.object; cutter.scale = (10, 10, 10); cutter.hide_render = True
    S["cutter"] = cutter
    # casquillo de rosca (con corte para ver el circuito)
    S["base"] = base = cyl(0.62, 1.2, (0, 0, 1.5), BRASS, v=40, unique=True)
    base.data.materials.append(mat((0.55, 0.5, 0.35), unique=True))
    m = base.modifiers.new("sol", "SOLIDIFY"); m.thickness = 0.06; m.offset = -1; m.material_offset = 1; m.material_offset_rim = 1
    b = base.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
    S["roscas"] = []
    for k in range(4):
        o = torus(0.63, 0.05, (0, 0, 1.05 + 0.25 * k), (0.75, 0.66, 0.38), unique=True)
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter; S["roscas"].append(o)
    cyl(0.25, 0.2, (0, 0, 0.85), (0.15, 0.15, 0.16))
    S["cuello"] = cyl(0.66, 0.35, (0, 0, 2.25), (0.92, 0.92, 0.9), v=40, unique=True)
    # circuito dentro del casquillo
    S["driver"] = drv = empty((0, 0, 0))
    box((0.7, 0.06, 1.0), (0, 0.05, 1.55), GREEN, parent=drv)
    cyl(0.12, 0.35, (-0.15, -0.12, 1.75), (0.2, 0.3, 0.75), parent=drv); cyl(0.08, 0.25, (0.18, -0.1, 1.4), (0.85, 0.75, 0.3), parent=drv)
    box((0.22, 0.06, 0.18), (0.15, -0.04, 1.85), (0.1, 0.1, 0.12), parent=drv)
    # soportes y hilo
    S["sop"] = [bar_obj(WIRE, 0.025, unique=True) for _ in range(2)]
    bar_set(S["sop"][0], (-0.18, 0, 2.35), (-0.6, 0, FZ)); bar_set(S["sop"][1], (0.18, 0, 2.35), (0.6, 0, FZ))
    S["hiloL"] = helix(-0.6, 0.0, 0.07, 6, FZ, COLD); S["hiloR"] = helix(0.0, 0.6, 0.07, 6, FZ, COLD)
    S["pivL"] = empty((-0.6, 0, FZ)); S["pivR"] = empty((0.6, 0, FZ))
    S["hiloL"].parent = S["pivL"]; S["hiloL"].location = (0.6, 0, -FZ); S["hiloR"].parent = S["pivR"]; S["hiloR"].location = (-0.6, 0, -FZ)
    # ampolla
    S["amp"] = amp = empty((0, 0, 0))
    S["vidrio"] = sph(1.5, (0, 0, CZ), GLASS, parent=amp, seg=48, unique=True); alpha(S["vidrio"], 0.18)
    cyl(0.62, 0.6, (0, 0, 2.5), GLASS, parent=amp, unique=True)
    # LED: placa, chip con dos capas, fósforo y disipador
    S["led"] = led = empty((0, 0, 0))
    cyl(0.95, 0.08, (0, 0, CHZ - 0.1), PCB, parent=led, v=48)
    S["capN"] = box((0.5, 0.5, 0.08), (0, 0, CHZ + 0.08), NC, parent=led, unique=True)
    S["capP"] = box((0.5, 0.5, 0.08), (0, 0, CHZ), PC, parent=led, unique=True)
    box((0.08, 0.6, 0.03), (-0.45, 0, CHZ - 0.04), (0.85, 0.75, 0.4), parent=led); box((0.08, 0.6, 0.03), (0.45, 0, CHZ - 0.04), (0.85, 0.75, 0.4), parent=led)
    S["fosforo"] = sph(0.42, (0, 0, CHZ + 0.06), YEL, scale=(1, 1, 0.7), unique=True); alpha(S["fosforo"], 0.55)
    S["aletas"] = []
    for k in range(14):
        a = 2 * math.pi * k / 14
        o = box((0.32, 0.05, 0.6), (0.82 * math.cos(a), 0.82 * math.sin(a), 2.45), ALU, rot=(0, 0, a), unique=True); S["aletas"].append(o)
    # partículas
    S["rayos"] = [bar_obj(HOT, 0.03, unique=True) for _ in range(14)]
    S["anillos"] = [torus(1.0, 0.04, (0, 0, -30), RED, unique=True) for _ in range(4)]
    S["o2"] = []
    for k in range(9):
        e = empty((0, 0, -30)); sph(0.08, (-0.06, 0, 0), O2C, parent=e, seg=10); sph(0.08, (0.06, 0, 0), O2C, parent=e, seg=10); S["o2"].append(e)
    S["humo"] = [sph(0.12, (0, 0, -30), (0.45, 0.45, 0.48), seg=10) for _ in range(8)]
    S["els"] = [sph(0.035, (0, 0, -30), (0.3, 0.75, 1.0), seg=8) for _ in range(10)]
    S["fot"] = [sph(0.03, (0, 0, -30), BLUE, seg=8, unique=True) for _ in range(16)]
    S["corr"] = [sph(0.04, (0, 0, -30), (0.3, 0.75, 1.0), seg=8) for _ in range(12)]
    join_static([cam, cutter, base, S["roscas"], S["driver"], S["sop"], S["pivL"], S["pivR"], amp, led, S["fosforo"], S["aletas"],
                 S["rayos"], S["anillos"], S["o2"], S["humo"], S["els"], S["fot"], S["corr"], S["cuello"]])
    return sc, S

def cmix(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))
def sc3(o, s): s = max(s, 0.001); o.scale = (s, s, s)

def calor(t):
    """temperatura del hilo (0 frío … 1 blanco)"""
    t_corr, t_quema, t_amp, t_func, t_chip = T("le pasas"), T("se quema"), T("así que lo metes"), T("funciona"), T("así que cambias")
    if t < T("si tuvieras", 1) + 3.6: return 1.0 * (1 - seg(t, 3.4, 4.3))
    h = seg(t, t_corr + 0.3, t_corr + 1.8) * (1 - seg(t, t_quema + 0.2, t_quema + 0.6))
    h = max(h, seg(t, t_func - 0.6, t_func + 0.3) * (1 - seg(t, t_chip, t_chip + 0.8)))
    return h

def roto(t): return win01(t, T("se quema") + 0.2, T("así que lo metes") + 0.6, 0.4, 0.3)

def pose(t, S):
    t_chip, t_aqui, t_capa, t_mez, t_base, t_dis, t_ult, t_res = (T("así que cambias"), T("aquí la luz"), T("así que lo cubres"),
        T("y todo mezclado"), T("así que en la base"), T("así que le pones"), T("por último"), T("resultado"))
    h = calor(t); r = roto(t)
    hilo_on = (t < 4.3) or (T("un hilo") - 0.3 < t < t_chip + 0.9)
    s_hilo = (1 - seg(t, 3.5, 4.3)) if t < 4.5 else seg(t, T("un hilo") - 0.3, T("un hilo") + 0.3) * (1 - seg(t, t_chip, t_chip + 0.8))
    for piv, o, sgn in ((S["pivL"], S["hiloL"], 1), (S["pivR"], S["hiloR"], -1)):
        sc3(piv, s_hilo); piv.rotation_euler = (0, sgn * 1.0 * r, 0)
        set_color(o, cmix(cmix(COLD, RED, min(1, h * 2)), HOT, max(0, h * 2 - 1)) if r < 0.5 else (0.2, 0.2, 0.22))
    for o in S["sop"]: o.scale.x = o.scale.y = 0.025 * (1 if s_hilo > 0.05 else 0.0001)
    # ampolla: al principio, luego se va y vuelve «sin oxígeno»; en el LED se ve lechosa
    t_amp = T("así que lo metes")
    up = seg(t, 3.4, 4.4) * (1 - seg(t, t_amp + 0.2, t_amp + 1.2))
    up = max(up, seg(t, t_chip + 0.2, t_chip + 1.0) * (1 - seg(t, t_mez - 0.2, t_mez + 0.8)))
    S["amp"].location = (0, 0, 7.0 * up)
    lech = seg(t, t_mez, t_mez + 0.8)
    S["vidrio"].active_material.diffuse_color = (*lin(cmix(cmix(GLASS, (1.0, 0.85, 0.5), 0.7 * h), (1, 1, 1), lech)), 0.18 + 0.12 * h + 0.4 * lech)
    # LED
    led_s = seg(t, t_chip + 0.5, t_chip + 1.3)
    sc3(S["led"], led_s)
    salto = win01(t, T("sale de los electrones"), t_mez + 0.5, 0.3, 0.3) + (t > t_mez) * 1.0
    sc3(S["fosforo"], seg(t, t_capa, t_capa + 0.8)); S["fosforo"].location.z = CHZ + 0.06
    hot_chip = win01(t, T("el chip se estropea"), t_dis + 1.2, 0.4, 0.6)
    set_color(S["capN"], cmix(NC, (1, 0.3, 0.2), hot_chip)); set_color(S["capP"], cmix(PC, (1, 0.3, 0.2), hot_chip))
    for k, a in enumerate(S["aletas"]):
        g = seg(t, t_dis + 0.05 * k, t_dis + 0.4 + 0.05 * k); a.scale = (max(0.32 * g, 0.001), 0.05, max(0.6 * g, 0.001))
    # corte del casquillo para ver el circuito
    cut = seg(t, t_base, t_base + 0.8) * (1 - seg(t, t_ult, t_ult + 0.6))
    S["cutter"].location = (12 * (1 - cut), -5.0, 1.5)
    sc3(S["driver"], 1.0 if cut > 0.05 else 0.0)
    # rayos de luz
    luz_vieja = h * (1 - r); luz_led = seg(t, T("lo ves blanco") - 0.8, T("lo ves blanco")) if t < t_tens_fin() else 1.0
    luz_led = max(luz_led, seg(t, t_res, t_res + 0.6))
    if T("pero el led quiere") < t < t_res: luz_led = 0.35
    L = max(luz_vieja, luz_led); col = HOT if luz_vieja >= luz_led else (1, 1, 1)
    diez = win01(t, T("de cada cien"), T("por eso quemaban"), 0.3, 0.3)
    for k, ray in enumerate(S["rayos"]):
        a = 2 * math.pi * k / len(S["rayos"]) + 0.2 * math.sin(k); el = 0.5 * math.sin(k * 1.7)
        d = Vector((math.cos(a) * math.cos(el), 0.35 + 0.3 * abs(math.sin(a)) * math.cos(el), math.sin(el))).normalized()
        n_on = len(S["rayos"]) if diez < 0.5 else 2       # «solo diez» de cada cien: pocos rayos
        if L < 0.05 or k >= n_on: ray.location = (0, 0, -30); continue
        p0 = Vector((0, 0, CZ)) + d * 1.7; ln = (0.6 + 0.4 * math.sin(t * 7 + k)) * 1.6 * L
        bar_set(ray, p0, p0 + d * ln); ray.scale.x = ray.scale.y = 0.035; set_color(ray, col)
    # anillos de calor: con el hilo encendido (sobre todo en «noventa se van en calor») y con el chip caliente
    calor_on = max(win01(t, T("pero hay un"), T("así que cambias"), 0.3, 0.4) * h, hot_chip * 0.9)
    for k, a in enumerate(S["anillos"]):
        u = (t * 0.55 + k / 4) % 1.0
        if calor_on < 0.05: a.location = (0, 0, -30); continue
        if hot_chip > 0.05:
            sale = seg(t, t_dis + 0.3, t_dis + 1.0)
            a.location = (0, 0, CHZ + 0.1 - 0.8 * sale * u); sc3(a, (0.3 + 0.8 * u) if sale < 0.5 else (0.9 + 0.8 * u))
        else:
            a.location = (0, 0, CZ + 0.3 + 2.2 * u); sc3(a, (1.2 + 1.2 * u) * calor_on)
        set_color(a, cmix(RED, (1.0, 0.6, 0.3), u))
    # oxígeno: ataca al hilo en el aire; luego se va de la ampolla
    t_aire = T("pero en el aire")
    for k, e in enumerate(S["o2"]):
        rr = random.Random(k)
        if t_aire - 0.2 < t < t_amp + 0.2:
            u = seg(t, t_aire - 0.2 + 0.08 * k, t_aire + 0.9 + 0.08 * k)
            far = Vector((rr.uniform(-2.5, 2.5), rr.uniform(-1.0, 1.0), FZ + rr.uniform(-1.6, 1.8)))
            near = Vector((rr.uniform(-0.5, 0.5), rr.uniform(-0.15, 0.15), FZ + rr.uniform(-0.15, 0.15)))
            e.location = far.lerp(near, u) + Vector((0, 0, 0.05 * math.sin(t * 9 + k))); e.rotation_euler = (0, t * 3 + k, k)
            sc3(e, 1 - seg(t, t_amp - 0.3, t_amp + 0.2))
        else: e.location = (0, 0, -30)
    for k, hm in enumerate(S["humo"]):
        if T("se quema") + 0.2 < t < t_amp + 0.4:
            u = (t * 0.7 + k / 8) % 1.0
            hm.location = (0.25 * math.sin(k * 2.0 + t), 0.1, FZ + 0.2 + 1.6 * u); sc3(hm, (0.6 + 1.6 * u) * (1 - seg(t, t_amp, t_amp + 0.4)))
        else: hm.location = (0, 0, -30)
    # corriente por los soportes
    for k, c in enumerate(S["corr"]):
        if hilo_on and h > 0.05 and r < 0.5:
            u = (t * 0.8 + k / 12) % 1.0
            p = Vector((-0.18, 0, 2.35)).lerp(Vector((-0.6, 0, FZ)), u * 2) if u < 0.5 else Vector((0.6, 0, FZ)).lerp(Vector((0.18, 0, 2.35)), u * 2 - 1)
            c.location = p
        else: c.location = (0, 0, -30)
    # electrones que saltan (de la capa N a la P) y fotones
    for k, e in enumerate(S["els"]):
        if salto > 0.05 and led_s > 0.5:
            u = (t * 0.9 + k / 10) % 1.0; rr = random.Random(k)
            x, y = rr.uniform(-0.2, 0.2), rr.uniform(-0.22, -0.05)
            e.location = (x, y - 0.04, CHZ + 0.1 - 0.12 * seg(u, 0.4, 0.6) + 0.03 * math.sin(u * 20))
        else: e.location = (0, 0, -30)
    fos = seg(t, t_capa + 0.5, t_capa + 1.2)
    for k, f in enumerate(S["fot"]):
        if salto > 0.05 and led_s > 0.5:
            u = (t * 0.9 + k / 16) % 1.0; rr = random.Random(100 + k)
            a = rr.uniform(0, 2 * math.pi); el = rr.uniform(0.6, 1.4)
            d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el) * 0.5 - 0.5 * math.cos(el), math.sin(el)))
            f.location = Vector((0, -0.1, CHZ + 0.06)) + d * (0.05 + 1.0 * u)
            c = BLUE
            if fos > 0.5 and u > 0.35: c = [YEL, (1.0, 0.45, 0.3), BLUE, YEL][k % 4]
            if t > t_mez + 0.3: c = (1, 1, 1)
            set_color(f, c); sc3(f, 1.2)
        else: f.location = (0, 0, -30)
    # giro final
    rot = 0.6 * seg(t, t_res, DUR) if t > t_res else 0.0
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.01))

def t_tens_fin(): return T("pero el led quiere")

def orb(tg, d, el, az, lens=40, up=0.06):
    tg = Vector(tg); el, az = math.radians(el), math.radians(az)
    pos = tg + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return (tuple(pos), tuple(tg + Vector((0, 0, up * d))), lens)

def CAM():
    C = (0, 0, 3.2); F = (0, 0, FZ); K = (0, -0.05, CHZ + 0.05)
    return [(0.0,) + orb(F, 3.6, 12, -20), (2.4,) + orb(C, 6.5, 12, -12), (T("lo primero"),) + orb(C, 8.5, 10, -6),
            (T("un hilo"),) + orb(F, 3.8, 10, -10), (T("le pasas") + 1.0,) + orb(F, 3.4, 14, 8), (T("pero en el aire"),) + orb(F, 5.5, 10, -12),
            (T("se quema"),) + orb(F, 3.6, 12, 10), (T("así que lo metes"),) + orb(C, 8.5, 12, -10), (T("funciona"),) + orb(C, 8.0, 14, 8),
            (T("de cada cien"),) + orb(C, 10.5, 12, -6), (T("por eso quemaban"),) + orb(C, 9.0, 12, 10), (T("así que cambias"),) + orb(C, 6.5, 22, -8),
            (T("un led"),) + orb(K, 2.6, 30, -14), (T("aquí la luz"),) + orb(K, 1.9, 16, -12), (T("sale de los electrones"),) + orb(K, 1.35, 8, -8, 40, 0.1),
            (T("cada salto"),) + orb(K, 1.5, 10, 10, 40, 0.1), (T("pero ese chip"),) + orb(K, 2.0, 20, 4), (T("así que lo cubres"),) + orb(K, 2.2, 22, -10),
            (T("absorbe"),) + orb(K, 2.6, 18, 8), (T("y todo mezclado"),) + orb(C, 7.0, 14, -6), (T("pero el led quiere"),) + orb(C, 8.0, 12, 8),
            (T("así que en la base"),) + orb((0, 0, 1.7), 4.6, 8, -6), (T("por último"),) + orb((0, 0, 2.7), 5.0, 22, -12),
            (T("así que le pones"),) + orb((0, 0, 2.6), 5.4, 18, 10), (T("resultado"),) + orb(C, 8.5, 12, -10), (DUR + 2,) + orb(C, 8.5, 12, 30)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"hilo": Pj((0.3, 0, FZ + 0.1)), "amp": Pj((0, 0, CZ + 1.5 + S["amp"].location.z)), "ampc": Pj((0, 0, CZ)),
            "chip": Pj((0.25, 0, CHZ + 0.12)), "capN": Pj((-0.25, -0.25, CHZ + 0.1)), "capP": Pj((-0.25, -0.25, CHZ)),
            "fos": Pj((0, 0, CHZ + 0.35)), "base": Pj((0.3, -0.2, 1.6)), "aletas": Pj((1.0, -0.3, 2.6)), "o2": Pj((1.2, 0, FZ + 0.8))}

if __name__ == "__main__":
    run("bombilla", build, pose, anchors)
