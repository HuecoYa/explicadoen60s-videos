# «¿Tus antenas del router apuntan a tu cuarto?»: el router en primer plano gira las antenas hacia el cuarto; los datos
# entran por el cable y salen anillos de ondas; la onda de 2,4 GHz con su regla de 12,5 cm; la antena en corte con su
# varilla y la corriente que sube y baja; el donut de señal; la casa en sección con el donut tumbado, el piso de arriba en
# el agujero y la antena inclinada; 5 GHz (6 cm) frente a 2,4 GHz atravesando a una persona y una pared; y dónde ponerlo.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Euler

T, DUR = cargar("router")
BG = (0.06, 0.07, 0.11); WALL = (0.84, 0.84, 0.86); FLOOR = (0.55, 0.42, 0.3); SLAB = (0.7, 0.7, 0.72); DARK = (0.12, 0.13, 0.16)
ROUT = (0.16, 0.17, 0.2); LED = (0.3, 1.0, 0.5); YEL = (1.0, 0.85, 0.2); CYAN = (0.3, 0.85, 1.0); DON = (0.15, 0.45, 1.0); RED = (0.95, 0.25, 0.22)
WOOD = (0.6, 0.42, 0.26); METAL = (0.82, 0.84, 0.88); SKIN = (0.93, 0.72, 0.6); SHIRT = (0.85, 0.35, 0.3); JEANS = (0.22, 0.3, 0.5)
BED = (0.9, 0.9, 0.95); SOFA = (0.35, 0.45, 0.6); PHONE = (0.08, 0.08, 0.1); SCREEN = (0.3, 0.6, 1.0)
LEJOS = (0, 0, -300)
RC = Vector((0.0, 2.0, 0.8))              # techo del router (centro)
PIV = [Vector((-0.11, 2.08, 0.8)), Vector((0.11, 2.08, 0.8))]
ALEN = 0.17
LANE_X0, LANE_X1 = -0.16, -2.75
LANES = {"24": (1.12, 0.125, YEL), "5": (0.9, 0.06, CYAN)}     # altura, longitud de onda, color
PERSON_X, WALL_X = -1.0, -1.9
PH = {"cuarto": Vector((3.2, 2.0, 0.62)), "arriba": Vector((0.0, 2.0, 3.72)), "salon": Vector((-3.0, 2.0, 0.55))}

def alpha_mat(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a)
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    m.use_backface_culling = False

def ribbon(n, color):
    me = bpy.data.meshes.new("rib"); bm = bmesh.new(); vs = []
    for i in range(n): vs.append((bm.verts.new((i, 0, 0)), bm.verts.new((i, 0, 0.01))))
    for i in range(n - 1): bm.faces.new((vs[i][0], vs[i + 1][0], vs[i + 1][1], vs[i][1]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("rib", me); bpy.context.collection.objects.link(o)
    return setup(o, color, unique=True)

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam}
    # casa en sección (sin fachada): dos plantas
    box((40, 40, 0.2), (0, 0, -0.1), (0.2, 0.24, 0.2))
    box((8.2, 4.0, 0.08), (0, 2.0, 0.04), FLOOR)
    box((8.2, 0.15, 5.6), (0, 4.07, 2.8), WALL)
    for sx in (-1, 1): box((0.15, 4.0, 5.6), (sx * 4.1, 2.0, 2.8), WALL)
    box((8.35, 4.15, 0.2), (0, 2.0, 2.8), SLAB); box((8.2, 4.0, 0.06), (0, 2.0, 2.93), FLOOR)
    box((8.6, 4.4, 0.22), (0, 2.0, 5.7), (0.55, 0.3, 0.25))
    for sx in (-1, 1): box((0.16, 0.01, 5.6), (sx * 4.1, -0.005, 2.8), (1, 1, 1))
    box((8.35, 0.01, 0.2), (0, -0.005, 2.8), (1, 1, 1))
    # tabique del cuarto con puerta, y cuarto
    box((0.12, 2.6, 2.7), (2.2, 2.7, 1.35), WALL); box((0.12, 1.4, 0.6), (2.2, 0.7, 2.4), WALL)
    box((1.6, 2.0, 0.45), (3.25, 2.4, 0.225), WOOD); box((1.5, 1.9, 0.12), (3.25, 2.4, 0.5), BED)
    box((0.5, 0.35, 0.12), (3.25, 3.2, 0.62), (0.95, 0.95, 1.0))
    # tabique del salón y sofá
    S["pared5"] = box((0.12, 3.6, 2.7), (WALL_X, 2.2, 1.35), WALL, unique=True)
    box((1.4, 0.8, 0.4), (-3.1, 2.6, 0.2), SOFA); box((1.4, 0.2, 0.5), (-3.1, 3.0, 0.65), SOFA)
    # arriba: escritorio
    box((1.2, 0.6, 0.05), (0.0, 2.1, 3.65), WOOD)
    for sx in (-0.55, 0.55): box((0.05, 0.5, 0.72), (sx, 2.1, 3.28), WOOD)
    # teléfonos
    S["phones"] = {}
    for k, p in PH.items():
        e = empty(p); S["phones"][k] = e
        box((0.08, 0.16, 0.012), (0, 0, 0), PHONE, parent=e); box((0.07, 0.14, 0.004), (0, 0, 0.008), SCREEN, parent=e)
    # mesa y router
    box((1.2, 0.7, 0.05), (0.0, 2.0, 0.715), WOOD)
    for sx in (-0.55, 0.55):
        for sy in (-0.3, 0.3): box((0.05, 0.05, 0.69), (sx, 2.0 + sy, 0.345), WOOD)
    rounded_slab(0.3, 0.2, 0.03, 0.06, (0, 2.0, 0.74), ROUT)
    S["leds"] = [box((0.012, 0.004, 0.006), (-0.08 + 0.04 * k, 1.899, 0.775), LED, unique=True) for k in range(5)]
    o = bar_obj((0.85, 0.85, 0.9), 0.006); bar_set(o, (0, 2.1, 0.77), (0, 3.99, 0.77))
    S["bits"] = [box((0.016, 0.016, 0.016), LEJOS, (0.95, 0.95, 1.0) if k % 2 else (0.3, 0.6, 1.0)) for k in range(12)]
    # antenas: cada una cuelga de su pivote; funda (transparente en el corte), varilla interior y punta
    S["ant"], S["shell"], S["rod"] = [], [], []
    for p in PIV:
        e = empty(p); S["ant"].append(e)
        cyl(0.016, 0.02, (0, 0, 0.0), DARK, parent=e)
        sh = cyl(0.01, ALEN, (0, 0, ALEN / 2), DARK, parent=e, unique=True); S["shell"].append(sh)
        sph(0.01, (0, 0, ALEN), DARK, parent=e)
        r = cyl(0.0035, ALEN * 0.85, (0, 0, ALEN * 0.5), METAL, parent=e, unique=True); S["rod"].append(r)
    S["cur"] = [sph(0.0045, LEJOS, YEL, seg=8) for _ in range(8)]
    # anillos de onda (en el plano perpendicular a la antena)
    S["rings"] = []
    for k in range(5):
        r = torus(1.0, 0.03, LEJOS, CYAN, unique=True); alpha_mat(r, 0.8); S["rings"].append(r)
    # donuts de señal
    S["don"] = []
    for k in range(2):
        d = torus(1.0, 0.86, LEJOS, DON, unique=True); alpha_mat(d, 0.3); S["don"].append(d)
        for pp in d.data.polygons: pp.use_smooth = True
    # ondas 2,4 y 5 GHz y reglas
    S["lane"] = {k: ribbon(420 if k == "5" else 220, v[2]) for k, v in LANES.items()}
    S["ruler"] = {}
    for k, (z, lam, col) in LANES.items():
        e = empty(LEJOS); S["ruler"][k] = e
        box((lam, 0.006, 0.014), (lam / 2, 0, 0), (0.95, 0.95, 0.95), parent=e)
        for q in range(6): box((0.0015, 0.008, 0.02 if q in (0, 5) else 0.012), (lam * q / 5, -0.002, 0.004), DARK, parent=e)
    # persona
    S["person"] = empty(LEJOS)
    for sx in (-0.09, 0.09): cyl(0.07, 0.85, (sx, 0, 0.425), JEANS, parent=S["person"])
    cyl(0.19, 0.6, (0, 0, 1.15), SHIRT, parent=S["person"]); sph(0.12, (0, 0, 1.6), SKIN, parent=S["person"])
    for sx in (-0.24, 0.24): cyl(0.05, 0.55, (sx, 0, 1.1), SHIRT, parent=S["person"])
    # obstáculos: mueble, tele, microondas
    S["mueble"] = empty(LEJOS)
    for loc, sz in (((0, 0.25, 0), (0.6, 0.02, 0.3)), ((-0.3, 0, 0), (0.02, 0.5, 0.3)), ((0.3, 0, 0), (0.02, 0.5, 0.3)), ((0, 0, 0.15), (0.62, 0.5, 0.02))):
        box(sz, loc, WOOD, parent=S["mueble"])
    S["puerta"] = box((0.6, 0.02, 0.3), LEJOS, (0.7, 0.5, 0.32), unique=True)
    S["tele"] = empty(LEJOS)
    box((1.1, 0.04, 0.62), (0, 0, 0.42), (0.08, 0.08, 0.1), parent=S["tele"]); box((1.04, 0.01, 0.56), (0, -0.025, 0.42), (0.15, 0.2, 0.35), parent=S["tele"])
    box((0.3, 0.15, 0.03), (0, 0.05, 0.0), (0.2, 0.2, 0.22), parent=S["tele"]); box((0.04, 0.03, 0.12), (0, 0.05, 0.06), (0.2, 0.2, 0.22), parent=S["tele"])
    S["micro"] = empty(LEJOS)
    box((0.5, 0.35, 0.28), (0, 0, 0.14), (0.88, 0.88, 0.9), parent=S["micro"]); box((0.32, 0.01, 0.2), (-0.05, -0.176, 0.14), (0.1, 0.12, 0.14), parent=S["micro"])
    box((0.08, 0.01, 0.2), (0.18, -0.176, 0.14), (0.6, 0.6, 0.62), parent=S["micro"])
    dyn = [cam, S["pared5"], list(S["phones"].values()), S["leds"], S["bits"], S["ant"], S["cur"], S["rings"], S["don"], list(S["lane"].values()),
           list(S["ruler"].values()), S["person"], S["mueble"], S["puerta"], S["tele"], S["micro"]]
    join_static(dyn)
    return sc, S

# ---------------- antenas ----------------
def ant_rot(t, i):
    """rotación (x, y) de cada antena; y = +90º apunta al cuarto (+x)"""
    t_apu, t_pues, t_por = 0.0, T("pues no"), T("por eso apuntarla")
    t_pie, t_inc, t_aqui = T("si las pones"), T("inclina"), T("y aquí viene")
    ry = keyed(t, [(0, 0.35), (1.6, 1.5708), (t_pues + 0.8, 1.5708), (T("vamos a ver") + 0.6, 0.0),
                   (t_por + 0.3, 0.0), (t_por + 1.3, 1.5708), (t_pie - 0.1, 1.5708), (t_pie + 0.8, 0.0)])
    if i == 1:
        ry = keyed(t, [(0, 0.2), (1.8, 1.5708), (t_pues + 0.9, 1.5708), (T("vamos a ver") + 0.7, 0.0),
                       (t_por + 0.3, 0.0), (t_por + 1.3, 1.5708), (t_pie - 0.1, 1.5708), (t_pie + 0.8, 0.0),
                       (t_inc, 0.0), (t_inc + 0.8, 1.5708), (t_aqui + 0.5, 1.5708), (t_aqui + 1.2, 0.0)])
    return (0.0, ry, 0.0)

def ant_mid(S, i):
    e = S["ant"][i]; return e.matrix_world @ Vector((0, 0, ALEN / 2))

def lane_shape(S, k, t, on):
    o = S["lane"][k]; z0, lam, col = LANES[k]; n = len(o.data.vertices) // 2
    if not on: o.location = LEJOS; return
    o.location = (0, 0, 0)
    t_par = T("las paredes")
    att_on = seg(t, t_par - 0.2, t_par + 1.2)
    grow = seg(t, T("en la banda") - 0.2, T("en la banda") + 1.2) if k == "24" else seg(t, T("la banda de cinco"), T("la banda de cinco") + 1.2)
    co = []
    for i in range(n):
        x = mix(LANE_X0, LANE_X1, i / (n - 1))
        reach = (LANE_X0 - x) / (LANE_X0 - LANE_X1)
        A = 0.055 if reach <= grow else 0.0
        if att_on > 0:
            f = 1.0
            if x < PERSON_X: f *= mix(1, 0.6 if k == "24" else 0.25, att_on)
            if x < WALL_X: f *= mix(1, 0.6 if k == "24" else 0.15, att_on)
            A *= f
        z = z0 + A * math.sin(2 * math.pi * x / lam + t * 9.0)
        co += [x, 2.0, z - 0.007, x, 2.0, z + 0.007]
    o.data.vertices.foreach_set("co", co); o.data.update()

def pose(t, S):
    t_conv, t_dent, t_cor, t_lados, t_punta = T("tu router convierte"), T("dentro de cada"), T("la corriente"), T("y suelta"), T("pero no por la punta")
    t_don, t_por, t_pie, t_arr, t_inc = T("la señal tiene"), T("por eso apuntarla"), T("si las pones"), T("pero el piso"), T("inclina")
    t_aqui, t_cinco, t_par, t_otra, t_donde = T("y aquí viene"), T("la banda de cinco"), T("las paredes"), T("en la otra"), T("y dónde")
    t_mue, t_tele, t_mic = T("nunca dentro"), T("ni detrás"), T("ni junto")
    for i, e in enumerate(S["ant"]): e.rotation_euler = ant_rot(t, i)
    bpy.context.view_layer.update()
    for k, l in enumerate(S["leds"]): set_color(l, LED if math.sin(t * (7 + 3 * k) + k) > -0.3 else (0.1, 0.3, 0.15))
    # bits entrando por el cable
    for k, b in enumerate(S["bits"]):
        if t_conv - 0.2 < t < T("en la banda"):
            u = (k / len(S["bits"]) + (t - t_conv) * 0.6) % 1.0; b.location = Vector((0, 3.95, 0.77)).lerp(Vector((0, 2.12, 0.77)), u)
        else: b.location = LEJOS
    # funda transparente durante el corte
    corte = seg(t, t_dent, t_dent + 0.6) * (1 - seg(t, t_don + 1.0, t_don + 1.6))
    for sh in S["shell"]:
        m = sh.active_material; m.diffuse_color = (*m.diffuse_color[:3], 1 - 0.75 * corte)
        try: m.surface_render_method = 'BLENDED' if corte > 0.01 else 'DITHERED'
        except Exception: pass
    for r in S["rod"]: set_color(r, YEL if (t_cor < t < t_punta + 1 and math.sin(t * 9) > 0) else METAL)
    for k, c in enumerate(S["cur"]):
        if t_cor - 0.2 < t < t_don and corte > 0.5:
            e = S["ant"][0]; zz = ALEN * (0.15 + 0.7 * (k / len(S["cur"]))) + 0.04 * math.sin(t * 9)
            c.location = e.matrix_world @ Vector((0, 0, zz))
        else: c.location = LEJOS
    # anillos: al principio (antenas hacia el cuarto), al convertir y al soltar ondas por los lados
    act = (t < T("vamos a ver")) or (t_conv + 0.6 < t < T("en la banda")) or (t_lados - 0.1 < t < t_don + 0.5)
    rmax = (0.3 if t < T("vamos a ver") else 0.55) if t < t_dent else 0.35
    for k, r in enumerate(S["rings"]):
        if act:
            i = k % 2 if t < t_dent else 0
            u = (k / len(S["rings"]) + t * 0.55) % 1.0
            r.location = ant_mid(S, i); r.rotation_euler = S["ant"][i].rotation_euler
            r.scale = (0.03 + rmax * u,) * 3; alpha_mat(r, 0.85 * (1 - u))
        else: r.location = LEJOS
    # donuts
    don_close = seg(t, t_don, t_don + 1.0) * (1 - seg(t, t_pie - 0.3, t_pie + 0.2))
    don_big = seg(t, t_pie + 0.4, T("el donut queda") + 0.6) * (1 - seg(t, t_aqui - 0.3, t_aqui))
    plac = seg(t, t_donde, t_donde + 0.6) * (1 - seg(t, DUR - 0.2, DUR + 2))
    d0, d1 = S["don"]
    if don_close > 0.01:
        d0.location = ant_mid(S, 0); d0.rotation_euler = S["ant"][0].rotation_euler; d0.scale = (0.16 * don_close,) * 3
        alpha_mat(d0, 0.5)
    elif don_big > 0.01 or plac > 0.01:
        sz = max(don_big, plac)
        # se encoge con cada obstáculo
        enc = 1 - 0.3 * seg(t, t_mue, t_mue + 0.6) - 0.25 * seg(t, t_tele, t_tele + 0.5) - 0.25 * seg(t, t_mic, t_mic + 0.5)
        if don_big > 0.01: enc = 1
        d0.location = RC + Vector((0, 0, 0.1)); d0.rotation_euler = (0, 0, 0); d0.scale = (3.4 * sz * enc, 3.4 * sz * enc, 0.85 * sz * enc)
        set_color(d0, DON if enc > 0.9 else mix_col(DON, RED, (1 - enc) / 0.8)); alpha_mat(d0, 0.42)
    else: d0.location = LEJOS
    don2 = seg(t, t_inc + 0.4, t_inc + 1.2) * (1 - seg(t, t_aqui - 0.3, t_aqui))
    if don2 > 0.01:
        d1.location = RC + Vector((0.1, 0, 0.1)); d1.rotation_euler = (0, math.pi / 2, 0); d1.scale = (3.0 * don2, 3.0 * don2, 1.1 * don2)
        alpha_mat(d1, 0.4)
    else: d1.location = LEJOS
    # ondas 2,4 y 5 GHz
    on24 = T("en la banda") - 0.2 < t < t_dent - 0.2 or t_aqui + 0.5 < t < t_donde
    on5 = t_cinco - 0.2 < t < t_donde
    lane_shape(S, "24", t, on24); lane_shape(S, "5", t, on5)
    r24 = seg(t, T("cada onda"), T("cada onda") + 0.5) * (1 - seg(t, t_dent - 0.6, t_dent - 0.2)) + seg(t, T("pero sus ondas"), T("pero sus ondas") + 0.5) * (1 - seg(t, t_par - 0.4, t_par))
    r5 = seg(t, T("pero sus ondas"), T("pero sus ondas") + 0.5) * (1 - seg(t, t_par - 0.4, t_par))
    for k, u in (("24", r24), ("5", r5)):
        z0, lam, _ = LANES[k]
        # ancla la regla a una cresta: x tal que 2π x/λ + 9t = π/2  → regla de cresta a cresta
        x_c = (math.pi / 2 - 9.0 * t) * lam / (2 * math.pi)
        base = -0.75
        x_c = base - ((base - x_c) % lam)
        S["ruler"][k].location = (x_c, 1.99, z0 + 0.06) if u > 0.01 else LEJOS
        S["ruler"][k].scale = (1, 1, max(u, 0.01))
    # persona y pared
    up = seg(t, t_par + 0.1, t_par + 0.7)
    S["person"].location = (PERSON_X, 2.0, -1.8 * (1 - up)) if t_par < t < t_donde else LEJOS
    # obstáculos
    um = seg(t, t_mue, t_mue + 0.4) * (1 - seg(t, t_tele - 0.1, t_tele + 0.2))
    S["mueble"].location = (RC.x, RC.y, RC.z - 0.08 + (1 - um) * 2.0) if um > 0.01 else LEJOS
    S["puerta"].location = (RC.x, RC.y - 0.25, RC.z - 0.08) if um > 0.9 else LEJOS
    ut = seg(t, t_tele, t_tele + 0.4) * (1 - seg(t, t_mic - 0.1, t_mic + 0.2))
    S["tele"].location = (RC.x + (1 - ut) * 2.5, RC.y - 0.3, 0.74) if ut > 0.01 else LEJOS
    uw = seg(t, t_mic, t_mic + 0.4)
    S["micro"].location = (RC.x + 0.42 + (1 - uw) * 2.0, RC.y, 0.74) if uw > 0.01 else LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def mix_col(a, b, u): u = max(0, min(1, u)); return tuple(mix(x, y, u) for x, y in zip(a, b))

def cam_lin(t, ks, drift=0.004):
    if t <= ks[0][0]: a = b = ks[0]; u = 0
    elif t >= ks[-1][0]: a = b = ks[-1]; u = 0
    else:
        for i in range(len(ks) - 1):
            if ks[i][0] <= t <= ks[i + 1][0]: break
        a, b = ks[i], ks[i + 1]; u = ss((t - a[0]) / max(b[0] - a[0], 1e-4))
    pos = Vector(a[1]).lerp(Vector(b[1]), u); tgt = Vector(a[2]).lerp(Vector(b[2]), u); lens = mix(a[3], b[3], u)
    d = (pos - tgt).length
    pos += Vector((math.sin(t * 0.9), 0.7 * math.sin(t * 0.7), 0.8 * math.sin(t * 1.1))) * drift * d
    return pos, tgt, lens

def V(at_, off, lens=35): at_ = Vector(at_); return (tuple(at_ + Vector(off)), tuple(at_), lens)
def CAM():
    k = []
    def add(t, v, hold=0.0):
        k.append((t,) + v)
        if hold: k.append((t + hold,) + v)
    rt = RC + Vector((0.02, 0.0, 0.08))
    casa = V((0.0, 2.0, 2.4), (0.0, -11.0, 0.9), 30)
    planta = V((0.5, 2.0, 1.1), (0.0, -9.0, 1.5), 30)
    add(0.0, V(rt, (0.25, -0.5, 0.18), 32))
    add(3.5, V(rt + Vector((0.06, 0, 0)), (0.4, -0.75, 0.25), 32), 2.0)
    add(T("tu router convierte") + 0.3, V(rt, (-0.25, -0.75, 0.3), 32))
    add(T("en la banda"), V((-0.75, 2.0, 1.05), (0.15, -1.6, 0.15), 35), 5.5)
    add(T("cada onda") + 0.3, V((-0.7, 2.0, 1.12), (0.05, -0.75, 0.05), 35), 1.6)
    add(T("dentro de cada") + 0.4, V(PIV[0] + Vector((0, 0, 0.09)), (0.1, -0.32, 0.05), 40), 4.8)
    add(T("pero no por") , V(PIV[0] + Vector((0, 0, 0.12)), (0.08, -0.36, 0.12), 40))
    add(T("la señal tiene") + 0.5, V(PIV[0] + Vector((0, 0, 0.09)), (0.4, -0.95, 0.5), 35), 2.0)
    add(T("por eso apuntarla") + 0.4, V((1.5, 2.0, 0.8), (0.2, -6.0, 1.1), 28), 3.0)
    add(T("si las pones") + 0.4, casa, 4.5)
    add(T("pero el piso") + 0.3, V((0.0, 2.0, 2.6), (0.0, -10.5, 0.4), 30), 4.6)
    add(T("y aquí viene") + 0.6, V((-1.0, 2.0, 1.0), (0.3, -3.2, 0.25), 30), 1.0)
    add(T("pero sus ondas") + 0.4, V((-0.7, 2.0, 1.0), (0.1, -1.1, 0.05), 35), 1.8)
    add(T("las paredes") + 0.3, V((-1.15, 2.0, 1.0), (0.3, -3.6, 0.3), 30), 3.0)
    add(T("por eso", 2), V((-1.5, 2.0, 0.9), (0.2, -4.8, 0.4), 30), 2.2)
    add(T("y dónde") + 0.3, casa, 3.5)
    add(T("nunca dentro"), V(RC, (0.2, -2.4, 0.5), 32), 3.6)
    add(T("sígueme") + 0.2, planta)
    add(DUR + 2, V((0.5, 2.0, 1.1), (0.0, -9.5, 1.6), 30))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    tip = S["ant"][0].matrix_world @ Vector((0, 0, ALEN + 0.02))
    rod = S["ant"][0].matrix_world @ Vector((0, 0, ALEN * 0.45))
    return {"router": P(RC + Vector((0, -0.1, 0.0))), "tip": P(tip), "rod": P(rod), "cuarto": P(PH["cuarto"]), "arriba": P(PH["arriba"]),
            "salon": P(PH["salon"]), "ruler24": P((-0.8, 2.0, LANES["24"][0] + 0.09)), "ruler5": P((-0.8, 2.0, LANES["5"][0] - 0.07)),
            "persona": P((PERSON_X, 2.0, 1.75)), "pared": P((WALL_X, 2.0, 1.9)), "ant1": P(S["ant"][1].matrix_world @ Vector((0, 0, ALEN)))}

if __name__ == "__main__":
    run("router", build, pose, anchors)
