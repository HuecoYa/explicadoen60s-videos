# «Si tuvieras que inventar la tostadora…»: tostadora en corte (sin la pared delantera). Un dedo baja la palanca y la tostada
# salta; todo desaparece menos el pan. Fuego (✗), hilo de nicrom en zigzag por el que la corriente avanza a duras penas y se
# pone al rojo, rayos infrarrojos que van del hilo al pan sin tocarlo, el pan que se seca y se dora al pasar de 140 °C, hilos a
# los dos lados, bandeja con muelle y palanca, electroimán que la engancha (y la suelta si desenchufas), reloj o lámina
# bimetálica que se curva con el calor hasta abrir el contacto, el imán suelta, el muelle tira y la tostada salta. La ruedecita.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("tostadora")
BG = (0.1, 0.1, 0.13); WALLC = (0.16, 0.17, 0.21); WOOD = (0.55, 0.4, 0.28); SHELL = (0.86, 0.24, 0.2); SHELLIN = (0.78, 0.79, 0.82)
MICA = (0.85, 0.78, 0.6); NICR = (0.6, 0.6, 0.58); METAL = (0.72, 0.74, 0.78); DARK = (0.12, 0.12, 0.14); COPPER = (0.9, 0.5, 0.25)
CORE = (0.45, 0.47, 0.52); SKIN = (0.93, 0.72, 0.6); NAIL = (0.98, 0.85, 0.8); CUR = (1.0, 0.9, 0.3); IR = (1.0, 0.25, 0.15)
RAW = (0.96, 0.88, 0.66); GOLD = (0.84, 0.55, 0.22); BURNT = (0.42, 0.24, 0.1); CRUST = (0.62, 0.4, 0.2); FLUX = (0.78, 0.45, 1.0)
BRASS = (0.92, 0.7, 0.3); STEEL = (0.55, 0.57, 0.62); GLOW = (1.0, 0.32, 0.08)
LEJOS = (0, 0, -300)
YF, YB = -0.42, 0.42                 # hilos delante / detrás del pan
ZUP, ZDN = 1.6, 0.6                 # bandeja arriba / abajo
XS = 2.15                            # muelle e imán
BX0, BX1, BZ = -2.2, -0.6, 0.47
BY = -0.72     # lámina bimetálica

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'
def cmix(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))
def hsh(k, s=1.0): return (math.sin(k * 12.9898 + s * 78.233) * 43758.5453) % 1.0

def zigzag(y):
    pts = []
    for k in range(9):
        x = -1.6 + 3.2 * k / 8
        z0, z1 = (0.75, 3.15) if k % 2 == 0 else (3.15, 0.75)
        pts += [(x, y, z0), (x, y, z1)]
    return [Vector(p) for p in pts]

def poly(pts):
    pts = [Vector(p) for p in pts]; L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    return pts, L
def at(path, s):
    pts, L = path; s = max(0.0, min(L[-1], s))
    for i in range(len(pts) - 1):
        if L[i] <= s <= L[i + 1]: return pts[i].lerp(pts[i + 1], (s - L[i]) / max(L[i + 1] - L[i], 1e-6))
    return pts[-1]

PLUG_IN = Vector((-4.35, 0.2, 0.3))
CORD = [PLUG_IN, Vector((-3.4, 0.6, 0.08)), Vector((-2.6, 0.6, 0.08)), Vector((-2.0, 0.6, 0.75)), Vector((-1.75, YF, 0.75))]
WPATH = poly(CORD + zigzag(YF))
NCORD = poly(CORD)[1][-1]

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    box((30, 14, 0.4), (0, 3, -0.2), WOOD)                       # encimera
    box((30, 0.3, 14), (0, 4.5, 6.5), WALLC)                    # pared
    box((1.0, 0.7, 0.5), (-4.9, 0.2, 0.25), (0.92, 0.92, 0.94))  # regleta
    for dz in (-0.08, 0.08): cyl(0.03, 0.2, (-4.4, 0.2, 0.3 + dz), DARK, rot=(0, math.pi / 2, 0), v=8)
    # carcasa (sin pared delantera)
    S["shell"] = sh = empty((0, 0, 0))
    box((5.0, 0.1, 3.2), (0, 1.05, 1.8), SHELL, parent=sh); box((4.8, 0.02, 3.0), (0, 0.99, 1.8), SHELLIN, parent=sh)
    for sx in (-1, 1): box((0.1, 2.2, 3.2), (sx * 2.45, 0, 1.8), SHELL, parent=sh)
    for sy in (-1, 1): box((5.0, 0.85, 0.08), (0, sy * 0.68, 3.4), SHELL, parent=sh)
    box((5.0, 2.2, 0.1), (0, 0, 0.25), SHELLIN, parent=sh)
    box((5.0, 0.1, 0.22), (0, -1.05, 3.29), SHELL, parent=sh); box((5.0, 0.1, 0.3), (0, -1.05, 0.35), SHELL, parent=sh)
    for sx in (-1, 1): box((0.18, 0.1, 3.2), (sx * 2.41, -1.05, 1.8), SHELL, parent=sh)
    for sx in (-2.2, 2.2):
        for sy in (-0.8, 0.8): cyl(0.12, 0.2, (sx, sy, 0.1), DARK, parent=sh, v=12)
    S["ranura"] = box((0.1, 0.12, 2.0), (2.5, 0, 1.6), DARK, parent=sh)
    S["rueda"] = rd = empty((2.52, -0.55, 0.85), parent=sh)
    cyl(0.28, 0.12, (0.06, 0, 0), DARK, parent=rd, rot=(0, math.pi / 2, 0), v=32)
    box((0.04, 0.06, 0.24), (0.13, 0, 0.12), (1, 1, 1), parent=rd)
    S["shell_parts"] = list(sh.children_recursive)
    # placas de mica y nicrom
    S["micaB"] = box((3.6, 0.04, 2.7), (0, YB + 0.12, 1.95), MICA, unique=True)
    S["hiloF"], S["hiloB"] = [], []
    for y, lst in ((YF, S["hiloF"]), (YB, S["hiloB"])):
        p = zigzag(y)
        for a, b in zip(p, p[1:]):
            o = bar_obj(NICR, 0.035); bar_set(o, a, b); lst.append(o)
    S["cable"] = []
    for a, b in zip(CORD, CORD[1:]):
        o = bar_obj(DARK, 0.06); S["cable"].append(o)
    S["clavija"] = box((0.35, 0.3, 0.3), LEJOS, DARK)
    # pan
    S["pan"] = pn = empty((0, 0, 0.9))
    S["miga"] = rounded_slab(2.9, 2.9, 0.55, 0.3, (0, 0.15, 1.45), RAW, parent=pn, unique=True); S["miga"].rotation_euler = (math.pi / 2, 0, 0)
    S["corteza"] = rounded_slab(3.1, 3.1, 0.6, 0.26, (0, 0.13, 1.45), CRUST, parent=pn, unique=True); S["corteza"].rotation_euler = (math.pi / 2, 0, 0)
    S["corteza"].location = (0, 0.13, 1.45)
    # bandeja, palanca y muelle
    S["band"] = bd = empty(LEJOS)
    box((3.3, 0.5, 0.08), (0, 0, -0.04), METAL, parent=bd)
    for sx in (-1.5, -0.5, 0.5, 1.5): box((0.06, 0.06, 0.5), (sx, -0.27, 0.2), METAL, parent=bd)
    box((1.2, 0.12, 0.12), (2.15, 0, 0), METAL, parent=bd)
    box((0.3, 0.3, 0.12), (XS, 0, -0.08), STEEL, parent=bd)
    S["palanca"] = box((0.55, 0.45, 0.25), (2.95, 0, 0.0), DARK, parent=bd)
    S["muelle"] = [torus(0.16, 0.03, LEJOS, (0.82, 0.84, 0.88)) for _ in range(12)]
    S["anclaje"] = box((0.4, 0.3, 0.12), (XS, 0, 3.25), STEEL, unique=True)
    # electroimán
    S["iman"] = im = empty(LEJOS)
    cyl(0.12, 0.42, (0, 0, 0.0), CORE, parent=im, v=16)
    S["bobina"] = [torus(0.17, 0.05, (0, 0, -0.15 + 0.075 * k), COPPER, parent=im, unique=True) for k in range(5)]
    S["campo"] = [sph(0.06, LEJOS, FLUX, seg=8) for _ in range(10)]
    S["corr_bob"] = [sph(0.05, LEJOS, CUR, seg=8) for _ in range(6)]
    # reloj
    S["reloj"] = rl = empty(LEJOS)
    cyl(0.5, 0.1, (0, 0, 0), (0.95, 0.95, 0.95), parent=rl, rot=(math.pi / 2, 0, 0), v=40)
    torus(0.5, 0.05, (0, 0, 0), (0.85, 0.3, 0.25), parent=rl, rot=(math.pi / 2, 0, 0))
    S["aguja"] = box((0.05, 0.03, 0.38), (0, -0.07, 0.15), DARK, parent=rl)
    # lámina bimetálica (segmentos) y contacto
    S["bim_a"] = [box((0.21, 0.3, 0.07), LEJOS, BRASS, unique=True) for _ in range(8)]
    S["bim_b"] = [box((0.21, 0.3, 0.07), LEJOS, STEEL, unique=True) for _ in range(8)]
    S["bim_base"] = box((0.2, 0.4, 0.3), LEJOS, DARK)
    S["contacto"] = cyl(0.07, 0.12, LEJOS, (0.95, 0.75, 0.3))
    S["chispa"] = [sph(0.04, LEJOS, CUR, seg=8) for _ in range(8)]
    # fuego, dedo, partículas
    S["fuego"] = []
    for _ in range(7):
        bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0, depth=0.7, location=LEJOS, vertices=16); S["fuego"].append(bpy.context.object)
    for k, f in enumerate(S["fuego"]): setup(f, (1.0, 0.55 if k % 2 else 0.35, 0.1))
    S["dedo"] = dd = empty(LEJOS)
    cyl(0.22, 2.0, (0, 0, 1.15), SKIN, parent=dd, v=20); sph(0.22, (0, 0, 0.15), SKIN, parent=dd)
    nl = sph(0.15, (0.0, -0.12, 0.25), NAIL, parent=dd, scale=(1, 0.35, 1.3))
    S["corr"] = [sph(0.06, LEJOS, CUR, seg=8) for _ in range(26)]
    S["ir"] = [sph(0.06, LEJOS, IR, seg=8, unique=True) for _ in range(28)]
    S["vapor"] = [sph(0.1, LEJOS, (0.9, 0.9, 0.92), seg=8, unique=True) for _ in range(12)]
    S["humo"] = [sph(0.15, LEJOS, (0.45, 0.45, 0.48), seg=8) for _ in range(10)]
    S["termo"] = sph(0.08, LEJOS, (1, 1, 1), seg=8)
    dyn = [cam, sh, S["micaB"], S["hiloF"], S["hiloB"], S["cable"], S["clavija"], pn, bd, S["muelle"], S["anclaje"], im, S["campo"],
           S["corr_bob"], rl, S["bim_a"], S["bim_b"], S["bim_base"], S["contacto"], S["chispa"], S["fuego"], dd, S["corr"], S["ir"],
           S["vapor"], S["humo"], S["termo"]]
    join_static(dyn)
    for o in S["hiloF"] + S["hiloB"]: o.data.materials[0] = S["hiloF"][0].data.materials[0]
    return sc, S

def show(objs, v):
    for o in objs: o.hide_render = not v

def pose(t, S):
    t_salta, t_inv, t_calor, t_fuego, t_elec = T("y la tostada"), T("vamos a"), T("primero"), T("pero el fuego"), T("así que usas")
    t_nic, t_cuesta, t_calienta, t_rojo, t_aguanta = T("el nicrom"), T("le cuesta"), T("así que se calienta"), T("y se pone"), T("aguanta")
    t_cont, t_ir, t_dora, t_debajo, t_dos = T("pero el pan"), T("ese hilo"), T("pero solo"), T("por debajo"), T("así que pones hilos")
    t_suj, t_band, t_bajar, t_iman, t_cur = T("pero ahora"), T("así que pones una"), T("al bajar"), T("y un imán"), T("y aquí viene")
    t_corr, t_desen, t_noqueda, t_falta, t_reloj = T("ese imán"), T("si la tostadora"), T("la palanca no"), T("pero falta"), T("así que añades")
    t_lam, t_calent, t_dobla, t_todo, t_corta = T("o una lámina"), T("al calentarse"), T("y la lámina"), T("cuando se dobla"), T("corta la")
    t_suelta, t_tira, t_salta2, t_rueda, t_sig = T("el imán se"), T("el muelle tira"), T("y la tostada", 2), T("si giras"), T("sígueme")
    intro = t < t_inv
    gone = seg(t, t_inv - 0.1, t_inv + 0.5)
    back = seg(t, t_rueda - 0.6, t_rueda + 0.2)
    # ---------- estado de la bandeja ----------
    if intro:
        cz = keyed(t, [(0, ZUP - 0.2), (1.4, ZDN), (t_salta + 0.5, ZDN), (t_salta + 0.75, ZUP + 0.25), (t_salta + 1.1, ZUP)])
    else:
        cz = keyed(t, [(t_band, ZUP), (t_bajar + 0.1, ZUP), (T("estiras") + 0.2, ZDN), (t_desen + 1.2, ZDN), (t_noqueda + 0.1, ZUP),
                       (t_falta + 0.3, ZUP), (t_falta + 1.3, ZDN), (t_tira - 0.1, ZDN), (t_tira + 0.25, ZUP + 0.25), (t_tira + 0.6, ZUP)])
    band_on = intro or t > t_band
    bd = S["band"]
    if band_on:
        u = 1.0 if intro else seg(t, t_band, t_band + 0.5)
        bd.location = (0, 0, cz + (1 - u) * -2.0) if not intro else (0, 0, cz)
        if intro: bd.scale = (max(1 - gone, 0.01),) * 3
        else: bd.scale = (1, 1, 1)
    else: bd.location = LEJOS
    # ---------- pan ----------
    pn = S["pan"]
    if intro:
        jump = 0.0
        if t > t_salta + 0.55:
            u = (t - t_salta - 0.55) / 2.4
            jump = max(0.0, 2.4 * 4 * u * (1 - u)) if u < 1 else 0.0
        pz = cz + 0.04 + jump; prot = 0.25 * math.sin(math.pi * min(1, max(0, (t - t_salta - 0.55) / 2.4)))
    elif t < t_suj + 0.3:
        pz = 0.9 + 0.04 * math.sin(2 * t); prot = 0.0
    elif t < t_band + 0.3:
        u = seg(t, t_suj + 0.3, t_band + 0.2); pz = 0.9 - 0.6 * u * u; prot = 0.08 * math.sin(10 * t) * u
    else:
        pz = cz + 0.04 if t > t_band + 0.5 else mix(0.3, ZUP + 0.04, seg(t, t_band + 0.1, t_band + 0.5)); prot = 0
        if t > t_salta2 - 0.3:
            u = (t - (t_tira + 0.2)) / 2.0
            if 0 < u < 1: pz += 2.6 * 4 * u * (1 - u); prot = 0.3 * math.sin(math.pi * u)
    if intro and gone > 0: pz = mix(pz, 0.9, gone)
    pn.location = (0, 0, pz); pn.rotation_euler = (0, prot, 0)
    # tostado del pan (0 crudo · 0.5 dorado · 1 quemado)
    b = keyed(t, [(0, 0.55), (t_inv - 0.1, 0.55), (t_inv + 0.4, 0.0), (t_dos, 0.0), (T("muy cerca") + 0.8, 0.45), (t_falta + 1.3, 0.45),
                  (T("saber cuándo", fin=True), 0.62), (t_corta, 0.68), (DUR + 2, 0.68)])
    col = cmix(RAW, GOLD, b / 0.5) if b < 0.5 else cmix(GOLD, BURNT, (b - 0.5) / 0.5)
    if t_debajo - 0.2 < t < t_dos: col = cmix(RAW, (0.99, 0.93, 0.76), seg(t, t_debajo, t_dos))
    set_color(S["miga"], col); set_color(S["corteza"], cmix(CRUST, BURNT, max(0, b - 0.4)))
    # ---------- carcasa ----------
    sh = S["shell"]; vis = (1 - gone) if intro else back
    sh.scale = (max(vis, 0.01),) * 3; show(S["shell_parts"], vis > 0.02)
    S["rueda"].rotation_euler = (math.radians(-170 * seg(t, t_rueda + 0.2, T("cambias") + 0.6)), 0, 0)
    # ---------- energía: ¿pasa corriente? ----------
    if intro: on = 1.0
    elif t < t_band: on = seg(t, t_nic, t_cuesta)
    else:
        on = 0.0
        if T("estiras") < t < t_desen + 0.3: on = 1.0
        if t_falta + 1.3 < t < t_corta + 0.1: on = 1.0
    glow = keyed(t, [(0, 1.0), (t_inv - 0.1, 1.0), (t_inv + 0.3, 0.0), (t_calienta, 0.0), (t_rojo + 0.6, 1.0), (t_band, 1.0), (t_band + 1.0, 0.0),
                     (T("estiras"), 0.0), (T("estiras") + 1.2, 1.0), (t_desen + 0.3, 1.0), (t_desen + 1.3, 0.0), (t_falta + 1.3, 0.0),
                     (t_falta + 2.3, 1.0), (t_corta + 0.1, 1.0), (t_corta + 1.6, 0.0), (DUR + 2, 0.0)])
    set_color(S["hiloF"][0], cmix(NICR, GLOW, glow) if glow < 0.6 else cmix(cmix(NICR, GLOW, 0.6), (1.0, 0.75, 0.3), (glow - 0.6) / 0.4 * 0.6))
    hilos_on = intro or t > t_elec + 0.3
    show(S["hiloF"], hilos_on and (not intro or gone < 0.99))
    show(S["hiloB"], intro or t > t_dos + 0.2); show([S["micaB"]], intro or t > t_dos + 0.2)
    if intro and gone > 0:
        for o in S["hiloB"] + [S["micaB"]]: o.hide_render = gone > 0.5
    # cable y clavija
    plug_out = keyed(t, [(0, 0.0), (t_desen, 0.0), (t_desen + 0.5, 1.0), (t_falta, 1.0), (t_falta + 0.6, 0.0)])
    cord_on = intro or t > t_elec
    P0 = PLUG_IN + Vector((0.9 * plug_out, -0.3 * plug_out, 0.1 * plug_out))
    pts = [P0] + CORD[1:]
    for o, a, b2 in zip(S["cable"], pts, pts[1:]):
        o.hide_render = not cord_on
        if cord_on: bar_set(o, a, b2)
    S["clavija"].location = P0 + Vector((0.1, 0, 0)) if cord_on else LEJOS
    # partículas de corriente
    vc = 2.0; vw = 2.0 if t < t_cuesta else 0.45
    Lw = WPATH[1][-1] - NCORD; tau = NCORD / vc + Lw / vw; n = len(S["corr"])
    for k, d in enumerate(S["corr"]):
        if on < 0.5 or not cord_on: d.location = LEJOS; continue
        u = (t + k * tau / n) % tau
        s = u * vc if u < NCORD / vc else NCORD + (u - NCORD / vc) * vw
        p = at(WPATH, s)
        if s > NCORD and t > t_cuesta: p = p + Vector((0.03 * math.sin(40 * t + k), 0, 0.03 * math.cos(37 * t + k)))
        d.location = p
    # ---------- fuego ----------
    fu = win01(t, t_fuego, t_elec + 0.2, 0.3, 0.3)
    for k, f in enumerate(S["fuego"]):
        if fu < 0.02: f.location = LEJOS; continue
        x = -1.2 + 0.4 * k; fl = 1 + 0.3 * math.sin(14 * t + 2 * k)
        f.location = (x, 0, 0.45 + 0.3 * fl * fu); f.scale = (fu, fu, fu * fl)
    # ---------- infrarrojo ----------
    irv = win01(t, t_ir, t_band, 0.3, 0.4) * min(1, glow * 1.5)
    for k, d in enumerate(S["ir"]):
        if irv < 0.05: d.location = LEJOS; continue
        side = 1 if (k % 2 and t > t_dos) else -1
        u = (t * 1.6 + hsh(k)) % 1.0
        x = -1.4 + 2.8 * hsh(k, 3); z = 0.9 + 2.2 * hsh(k, 4)
        y = side * mix(0.4, 0.16, u)
        d.location = (x, y, z + (pz - 0.9)); d.scale = (irv * (1 - 0.5 * u),) * 3
    # vapor (el pan se seca) y humo (se pasa)
    for k, d in enumerate(S["vapor"]):
        v = win01(t, t_debajo, t_dos + 0.5, 0.3, 0.4)
        if v < 0.05: d.location = LEJOS; continue
        u = (t * 0.7 + k / 12) % 1.0; d.location = (-1.3 + 2.6 * hsh(k), -0.2 + 0.4 * hsh(k, 2), pz + 2.9 + 1.2 * u); d.scale = (v * (0.6 + u),) * 3
    for k, d in enumerate(S["humo"]):
        v = win01(t, T("saber cuándo") - 0.3, t_corta + 1.0, 0.4, 0.6)
        if v < 0.05: d.location = LEJOS; continue
        u = (t * 0.5 + k / 10) % 1.0; d.location = (-1.0 + 2.0 * hsh(k), 0.0, pz + 3.0 + 1.6 * u); d.scale = (v * (0.6 + 1.2 * u),) * 3
    # ---------- muelle ----------
    m_on = t > t_band + 0.3 and not intro
    top = Vector((XS, 0, 3.19)); bot = Vector((XS, 0, cz + 0.06))
    for k, r in enumerate(S["muelle"]):
        if not m_on: r.location = LEJOS; continue
        u = seg(t, t_band + 0.3 + 0.03 * k, t_band + 0.6 + 0.03 * k)
        r.location = top.lerp(bot, (k + 0.5) / 12) if u > 0 else LEJOS; r.scale = (u, u, 1)
        r.rotation_euler = (0.25, 0, 0)
    S["anclaje"].location = (XS, 0, 3.25) if m_on else LEJOS
    # ---------- electroimán ----------
    im = S["iman"]; iu = seg(t, t_iman - 0.2, t_iman + 0.3)
    im.location = (XS, 0, 0.24) if (iu > 0 and not intro) else LEJOS; im.scale = (max(iu, 0.01),) * 3
    mag = 1.0 if (T("estiras") < t < t_desen + 0.3 or t_falta + 1.3 < t < t_suelta) else 0.0
    if not (t > t_iman) or intro: mag = 0.0
    for o in S["bobina"]: set_color(o, cmix(COPPER, (1.0, 0.85, 0.4), mag * (0.5 + 0.5 * math.sin(10 * t))))
    for k, d in enumerate(S["campo"]):
        if mag < 0.5 or im.location.z < -100: d.location = LEJOS; continue
        side = 1 if k % 2 else -1; a = ((t * 0.8 + k / 10) % 1.0) * math.pi
        d.location = (XS + side * 0.35 * math.sin(a), -0.2, 0.24 + 0.35 * math.cos(a))
    for k, d in enumerate(S["corr_bob"]):
        if mag < 0.5 or im.location.z < -100 or not (t > t_corr - 0.5): d.location = LEJOS; continue
        a = t * 6 + k * math.tau / 6
        d.location = (XS + 0.24 * math.cos(a), 0.24 * math.sin(a), 0.1 + 0.05 * ((t * 3 + k) % 4))
    # ---------- reloj ----------
    rv = win01(t, t_reloj + 0.2, t_lam + 0.3, 0.3, 0.3)
    S["reloj"].location = (-1.6, -0.75, 1.0) if rv > 0.02 else LEJOS; S["reloj"].scale = (max(rv, 0.01),) * 3
    S["aguja"].rotation_euler = (0, t * 4, 0); S["aguja"].location = (0.15 * math.sin(t * 4), -0.07, 0.15 * math.cos(t * 4))
    # ---------- lámina bimetálica ----------
    lv = seg(t, t_lam, t_lam + 0.5) if not intro else 0
    curv = keyed(t, [(0, 0.0), (t_calent, 0.0), (t_dobla + 0.8, 0.55), (t_todo + 0.6, 1.0), (DUR + 2, 1.0)])
    if t > t_rueda: curv = mix(1.0, 0.0, seg(t, t_rueda, t_rueda + 1.0))
    heat = seg(t, t_calent, t_calent + 1.5) * (1 - seg(t, t_corta + 0.5, t_corta + 3.0))
    L = BX1 - BX0; ang_tot = math.radians(50) * curv
    for k in range(8):
        for lst, dz in ((S["bim_a"], 0.035), (S["bim_b"], -0.035)):
            o = lst[k]
            if lv < 0.02: o.location = LEJOS; continue
            s0 = (k + 0.5) / 8 * L; ang = ang_tot * (k + 0.5) / 8
            if ang_tot > 1e-4:
                R = L / ang_tot; x = BX0 + R * math.sin(s0 / R); z = BZ + R * (1 - math.cos(s0 / R))
            else: x, z = BX0 + s0, BZ
            o.location = (x - math.sin(ang) * dz, BY, z + math.cos(ang) * dz + (1 - lv) * 1.0); o.rotation_euler = (0, -ang, 0)
            o.scale = (0.21 * (1.0 + (0.06 * heat if lst is S["bim_a"] else 0)), 0.3, 0.07)
            base = BRASS if lst is S["bim_a"] else STEEL
            set_color(o, cmix(base, (1.0, 0.4, 0.2), 0.45 * heat))
    S["bim_base"].location = (BX0 - 0.08, BY, BZ - 0.1) if lv > 0.02 else LEJOS
    S["contacto"].location = (BX1 - 0.06, BY, BZ - 0.12 - 0.06 * seg(t, t_rueda, t_rueda + 1.0)) if lv > 0.02 else LEJOS
    for k, d in enumerate(S["chispa"]):
        u = (t - (t_corta - 0.1)) / 0.4
        if 0 < u < 1:
            a = k * math.tau / 8; d.location = (BX1 + 0.3 * u * math.cos(a), BY - 0.2, BZ - 0.02 + 0.3 * u * math.sin(a)); d.scale = (1 - u,) * 3
        else: d.location = LEJOS
    # ---------- dedo ----------
    dd = S["dedo"]
    w = max(win01(t, T("al bajar") - 0.6, T("estiras") + 0.6, 0.35, 0.4), win01(t, t_falta + 0.2, t_falta + 1.6, 0.3, 0.3))
    if t < 2.0: dd.location = (2.95, 0, cz + 0.13 + 0.6 * seg(t, 1.5, 2.0)); dd.rotation_euler = (0, 0.15, 0)
    elif w > 0.01 and not intro: dd.location = (2.95, 0, cz + 0.13 + 0.8 * (1 - w)); dd.rotation_euler = (0, 0.15, 0)
    else: dd.location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def orb(tg, d, el, az, lens=35, up=0.1):
    tg = Vector(tg); el, az = math.radians(el), math.radians(az)
    pos = tg + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return (tuple(pos), tuple(tg + Vector((0, 0, up * d))), lens)

def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    add(0.0, orb((2.2, 0, 1.6), 6.0, 14, 32))
    add(1.5, orb((1.2, 0, 2.0), 8.0, 12, 22))
    add(T("y la tostada") + 0.5, orb((0.2, 0, 2.8), 10.5, 10, 12))
    add(T("vamos a"), orb((0, 0, 2.2), 11.0, 12, -10))
    add(T("pero el fuego"), orb((0, 0, 1.6), 10.0, 8, -14))
    add(T("así que usas") + 0.5, orb((-0.4, 0, 1.6), 9.5, 10, -18))
    add(T("le cuesta"), orb((-0.2, -0.4, 1.9), 6.5, 6, -14))
    add(T("aguanta"), orb((0, -0.4, 1.9), 8.0, 8, -12))
    add(T("pero el pan") + 0.3, orb((0, 0, 1.9), 8.0, 10, 70))
    add(T("ese hilo") + 1.0, orb((0, 0, 1.9), 6.5, 12, 80))
    add(T("pero solo") + 0.6, orb((0, 0, 2.1), 9.0, 10, -14))
    add(T("así que pones hilos") + 0.6, orb((0, 0, 1.6), 7.0, 58, -20, up=0.0))
    add(T("pero ahora"), orb((0.4, 0, 1.6), 10.5, 14, -18))
    add(T("así que pones una") + 0.6, orb((0.8, 0, 1.8), 10.5, 10, -24))
    add(T("y un imán"), orb((1.6, 0, 0.7), 7.0, 10, -30, up=0.0))
    add(T("ese imán"), orb((2.0, 0, 0.35), 4.8, 8, -26, up=-0.02))
    add(T("si la tostadora") - 0.4, orb((-0.6, 0, 1.4), 12.0, 10, -12))
    add(T("pero falta") + 1.4, orb((0, 0, 2.0), 10.0, 10, -14))
    add(T("así que añades"), orb((-1.4, 0, 1.0), 6.5, 10, -16))
    add(T("o una lámina") + 0.4, orb((-1.4, BY, 0.6), 3.4, 10, -12, up=0.04))
    add(T("cuando se dobla"), orb((-1.3, BY, 0.7), 3.6, 10, -8, up=0.04))
    add(T("el imán se"), orb((0.6, 0, 1.8), 10.5, 10, -16))
    add(T("y la tostada", 2) + 0.4, orb((0.4, 0, 3.0), 11.5, 10, -10))
    add(T("si giras"), orb((2.5, -0.4, 1.0), 5.0, 10, 55))
    add(T("sígueme"), orb((0.5, 0, 1.8), 10.5, 12, 25))
    add(DUR + 2, orb((0.5, 0, 1.8), 12.0, 12, 30))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); pz = S["pan"].location.z
    return {"hilo": Pj((1.2, YF, 3.15)), "pan": Pj((0, -0.2, pz + 3.0)), "panc": Pj((0, -0.2, pz + 1.45)), "band": Pj((-1.0, -0.3, S["band"].location.z)),
            "muelle": Pj((XS, 0, 2.5)), "iman": Pj((XS, 0, 0.3)), "lamina": Pj(((BX0 + BX1) / 2, BY, BZ + 0.1)), "cont": Pj((BX1, BY, BZ - 0.1)),
            "clavija": Pj(S["clavija"].location), "reloj": Pj((-1.6, -0.75, 1.5)), "rueda": Pj((2.6, -0.55, 0.85)), "palanca": Pj((2.95, 0, S["band"].location.z))}

if __name__ == "__main__":
    run("tostadora", build, pose, anchors)
