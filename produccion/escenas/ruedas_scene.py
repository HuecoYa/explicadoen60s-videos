# «¿Por qué no revientan las ruedas de un avión?»: la rueda toca la pista entre humo y pasa de 0 a 250 km/h; un corte
# muestra la cámara interior llena de gas; al lado aparece la rueda de un coche con mucho menos gas dentro; el gas pasa a
# nitrógeno; si fuera aire, el oxígeno arde y el agua se congela; capas de nailon por dentro; al frenar la llanta se pone al
# rojo y la presión sube; los tapones fusibles se derriten, el gas sale y la rueda se desinfla; 500 aterrizajes y banda nueva.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("ruedas")
BG = (0.07, 0.08, 0.11); ASF = (0.25, 0.26, 0.29); RUB = (0.09, 0.09, 0.1); RUBIN = (0.42, 0.4, 0.42); BAND = (0.13, 0.13, 0.15)
RIM = (0.74, 0.76, 0.8); RIMHOT = (1.0, 0.42, 0.12); STEEL = (0.55, 0.57, 0.62); BRASS = (0.88, 0.66, 0.28)
N2 = (0.45, 0.75, 1.0); O2 = (1.0, 0.32, 0.28); H2O = (0.85, 0.97, 1.0); NEUT = (0.82, 0.84, 0.88)
NYL1 = (1.0, 0.84, 0.32); NYL2 = (0.96, 0.95, 0.88); FIRE = (1.0, 0.55, 0.12); SMOKE = (0.62, 0.63, 0.66)
LEJOS = (0, 0, -300)
R0, RT = 0.98, 0.40            # radio mayor y del tubo del neumático
CZ = R0 + RT                   # altura del eje
CR0, CRT, CCZ, CX = 0.42, 0.2, 0.62, -2.35   # rueda de coche
YC = -0.08                     # plano del corte
random.seed(7)

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def tor(R, r, loc, color, parent=None, wide=1.0, unique=False):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=(math.pi / 2, 0, 0), major_segments=72, minor_segments=24)
    o = bpy.context.object; o.scale = (1, 1, wide); return setup(o, color, parent, True, unique)

def tube(r0, r1, w, color, parent=None, seg=72, unique=False):
    """anillo hueco con eje Y (banda de rodadura)"""
    me = bpy.data.meshes.new("tube"); bm = bmesh.new(); rings = []
    for (r, y) in ((r1, -w / 2), (r1, w / 2), (r0, w / 2), (r0, -w / 2)):
        rings.append([bm.verts.new((r * math.cos(math.tau * k / seg), y, r * math.sin(math.tau * k / seg))) for k in range(seg)])
    for a in range(4):
        A, B = rings[a], rings[(a + 1) % 4]
        for k in range(seg):
            j = (k + 1) % seg; bm.faces.new((A[k], A[j], B[j], B[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new("tube", me); bpy.context.collection.objects.link(o)
    return setup(o, color, parent, True, unique)

def shellcut(o, th, inner, cutter):
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
    o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
    b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
    try: b.solver = 'MANIFOLD'
    except Exception: b.solver = 'EXACT'
    return o

def wheel_parts(G, cutter, R0_, RT_, wide, rim_r, rim_w, S, key):
    ty = tor(R0_, RT_, (0, 0, 0), RUB, parent=G, wide=wide); shellcut(ty, 0.07 * RT_ / 0.4, RUBIN, cutter); S[key + "_ty"] = ty
    R = empty((0, 0, 0), parent=G); S[key + "_R"] = R
    S[key + "_rim"] = cyl(rim_r, rim_w, (0, 0, 0), RIM, parent=R, rot=(math.pi / 2, 0, 0), v=48, unique=True)
    cyl(rim_r * 0.45, rim_w + 0.12, (0, 0, 0), STEEL, parent=R, rot=(math.pi / 2, 0, 0), v=32)
    cyl(rim_r * 0.82, 0.03, (0, -rim_w / 2 - 0.005, 0), (0.62, 0.64, 0.68), parent=R, rot=(math.pi / 2, 0, 0), v=48)
    for k in range(8):
        a = math.tau * k / 8
        cyl(rim_r * 0.06, 0.08, (rim_r * 0.6 * math.cos(a), -rim_w / 2 - 0.03, rim_r * 0.6 * math.sin(a)), (0.3, 0.31, 0.35), parent=R, rot=(math.pi / 2, 0, 0), v=12)
    return R

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    box((400, 60, 0.1), (0, 10, -0.05), ASF)
    S["dash"] = [box((1.6, 0.18, 0.012), (0, -2.6, 0.005), (0.92, 0.92, 0.9)) for _ in range(12)]
    S["dash2"] = [box((2.4, 0.3, 0.012), (0, 4.5, 0.005), (0.92, 0.92, 0.9)) for _ in range(10)]
    S["luz"] = [sph(0.09, (0, 9.0, 0.12), (1.0, 0.85, 0.4), seg=10) for _ in range(14)]
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, YC - 3, 12)); cutter = bpy.context.object; cutter.scale = (9, 6, 9); cutter.hide_render = True
    S["cutter"] = cutter
    # rueda del avión
    S["G"] = G = empty((0, 0, CZ))
    wheel_parts(G, cutter, R0, RT, 1.2, 0.62, 0.86, S, "av")
    S["plugs"] = []
    for k in range(3):
        a = math.radians(90 + 120 * k)
        p = cyl(0.06, 0.1, (0.47 * math.cos(a), -0.44, 0.47 * math.sin(a)), BRASS, parent=S["av_R"], rot=(math.pi / 2, 0, 0), v=16, unique=True)
        S["plugs"].append(p)
    cyl(0.16, 1.3, (0, 0.85, 0), STEEL, parent=G, rot=(math.pi / 2, 0, 0))            # eje
    cyl(0.22, 8, (0, 1.45, 4.0), (0.8, 0.82, 0.86), parent=G)                          # pata del tren
    cyl(0.3, 0.5, (0, 1.45, 0.25), STEEL, parent=G)
    box((0.12, 0.12, 1.6), (0.35, 1.2, 0.9), STEEL, parent=G, rot=(0, -0.35, 0))
    # capas de nailon (por dentro)
    S["nyl"] = []
    for k, r in enumerate((0.318, 0.303, 0.288, 0.273)):
        o = tor(R0, r, LEJOS, NYL2, wide=1.2, unique=True); shellcut(o, 0.014, NYL1, cutter)
        S["nyl"].append(o)
    # banda de rodadura (vieja y nueva)
    def banda(col):
        e = empty(LEJOS); tube(1.355, 1.425, 0.62, col, parent=e, unique=True)
        for y in (-0.17, 0.0, 0.17): tor(1.428, 0.022, (0, y, 0), (0.04, 0.04, 0.05), parent=e)
        return e
    S["band"] = banda(BAND); S["band_new"] = banda((0.06, 0.06, 0.07))
    S["band_m"] = S["band"].children[0]; S["grooves"] = [c for c in S["band"].children[1:]]
    # rueda del coche
    S["C"] = C = empty(LEJOS)
    wheel_parts(C, cutter, CR0, CRT, 1.1, 0.3, 0.42, S, "co")
    # gas
    S["gas"] = []
    for k in range(52):
        o = sph(0.055, LEJOS, NEUT, seg=10, unique=True)
        S["gas"].append((o, random.uniform(0, math.tau), random.uniform(0, 1), random.uniform(0, math.tau), random.uniform(0.6, 1.4)))
    S["hielo"] = [box((0.1, 0.1, 0.1), LEJOS, (0.93, 0.98, 1.0)) for _ in range(6)]
    S["cgas"] = [(sph(0.04, LEJOS, N2, seg=10), random.uniform(0, math.tau), random.uniform(0, 1), random.uniform(0, math.tau)) for _ in range(7)]
    S["fuego"] = [sph(0.07, LEJOS, FIRE if k % 2 else (1.0, 0.85, 0.3), seg=10) for k in range(10)]
    S["humo"] = [sph(0.3, LEJOS, SMOKE, seg=14, unique=True) for _ in range(12)]
    S["fuga"] = [sph(0.045, LEJOS, N2, seg=8) for _ in range(24)]
    # parche de tejido cruzado
    S["tela"] = tela = empty(LEJOS)
    box((1.25, 0.04, 1.25), (0, 0.04, 0), (0.12, 0.13, 0.16), parent=tela)
    strips = []
    for k in range(-4, 5):
        for sgn, col, dy in ((1, NYL1, 0.0), (-1, NYL2, -0.02)):
            o = box((0.07, 0.02, 1.7), (0, 0, 0), col, parent=tela)
            o.rotation_euler = (0, sgn * math.radians(40), 0)
            d = 0.16 * k; o.location = (d * math.cos(math.radians(40)), dy - 0.01, -sgn * d * math.sin(math.radians(40)))
            strips.append(o)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0)); cc = bpy.context.object; cc.scale = (1.2, 0.5, 1.2); cc.hide_render = True; cc.parent = tela
    for o in strips:
        b = o.modifiers.new("i", "BOOLEAN"); b.operation = 'INTERSECT'; b.object = cc
        try: b.solver = 'MANIFOLD'
        except Exception: b.solver = 'EXACT'
    dyn = [cam, cutter, G, C, S["dash"], S["dash2"], S["luz"], S["nyl"], S["band"], S["band_new"], [g[0] for g in S["gas"]], S["hielo"],
           [g[0] for g in S["cgas"]], S["fuego"], S["humo"], S["fuga"], tela]
    join_static(dyn)
    return sc, S

# ---------- giro de la rueda (velocidad angular) ----------
def omega(t):
    TD = T("cero") - 0.1
    if t < TD: return 0.0
    if t < T("por qué no"): return 14 * seg(t, TD, TD + 0.9)
    if t < T("al frenar"): return 14 * (1 - seg(t, T("por qué no"), T("primero")))
    if t < T("y cuánto"): return 12 * (seg(t, T("al frenar") - 0.3, T("al frenar")) - seg(t, T("al frenar"), T("si la presión")))
    if t < T("sígueme"): return 10 * (seg(t, T("y cuánto"), T("y cuánto") + 0.6) - seg(t, T("luego no"), T("le quitan")))
    return 7 * seg(t, T("sígueme"), T("sígueme") + 0.8)
def ang(t):
    a, x, dt = 0.0, 0.0, 1 / 60
    while x < t: a += omega(x) * dt; x += dt
    return a
def vel_plane(t):
    TD = T("cero") - 0.1
    if t < T("por qué no"): return 19.0
    return omega(t) * CZ

_cache = {}
def dist(t):
    a, x, dt = 0.0, 0.0, 1 / 60
    while x < t: a += vel_plane(x) * dt; x += dt
    return a

def wrapx(x, L): return (x + L / 2) % L - L / 2

def pose(t, S):
    TD = T("cero") - 0.1
    al = ang(t); d = dist(t)
    # descenso hasta tocar la pista
    h = 0.75 * (1 - seg(t, -0.2, TD)) + (0.06 * math.sin(14 * (t - TD)) * math.exp(-4 * (t - TD)) if t > TD else 0)
    # desinflado
    t_sue, t_desi = T("sueltan el gas"), T("y la rueda se desinfla")
    df = seg(t, t_sue, T("en vez de reventar")) * (1 - seg(t, T("y cuánto"), T("y cuánto") + 0.8))
    sq = 1 - 0.11 * df
    hinch = 1 + 0.035 * seg(t, T("al frenar"), T("explotaría")) * (1 - seg(t, t_sue, t_sue + 1.0))
    tiem = 0.012 * math.sin(t * 60) * win01(t, T("la rueda explotaría") - 0.2, T("así que la llanta"), 0.2, 0.3)
    cz = CZ * sq * hinch + h
    G = S["G"]; G.location = (tiem, 0, cz)
    ty = S["av_ty"]; ty.scale = (1 / sq ** 0.3 * hinch, sq * hinch, 1.2 * hinch)
    S["av_R"].rotation_euler = (0, al, 0)
    t_nyl = T("capas y capas")
    for k, o in enumerate(S["nyl"]):
        if t > t_nyl - 0.6 + 0.45 * k:
            o.location = G.location; o.scale = ty.scale
        else: o.location = LEJOS
    # corte: el cortador baja desde arriba
    cu = seg(t, T("vamos a mirar") - 0.2, T("primero") + 0.3) * (1 - seg(t, T("y cuánto"), T("unos quinientos")))
    S["cutter"].location = (0, YC - 3, mix(12, CZ, cu))
    cut_open = cu > 0.97
    # pista en movimiento
    for k, o in enumerate(S["dash"]): o.location = (wrapx(-k * 3.4 - d, 40.8), -2.6, 0.005)
    for k, o in enumerate(S["dash2"]): o.location = (wrapx(-k * 5.0 - d, 50), 4.5, 0.005)
    for k, o in enumerate(S["luz"]): o.location = (wrapx(-k * 4.0 - d, 56), 9.0, 0.12)
    # humo al tocar
    for k, o in enumerate(S["humo"]):
        u = (t - TD - 0.04 * k) / 1.6
        if 0 < u < 1:
            o.location = (-0.2 - 2.2 * u - 0.12 * k, 0.15 * math.sin(k * 2.1) - 0.5, 0.1 + 0.7 * u * (0.6 + 0.3 * (k % 3)))
            o.scale = (0.35 + 1.2 * u,) * 3; alpha(o, 0.6 * (1 - u))
        else: o.location = LEJOS
    # rueda del coche (comparación)
    a0, a1 = T("la rueda de tu"), T("pero no está")
    C = S["C"]
    if a0 - 0.2 < t < a1 + 0.6:
        ent = seg(t, a0 - 0.2, a0 + 0.5) * (1 - seg(t, a1, a1 + 0.6))
        C.location = (mix(-9, CX, ent), 0, CCZ); S["co_R"].rotation_euler = (0, 0, 0)
    else: C.location = LEJOS
    for k, (o, a, r, ph) in enumerate(S["cgas"]):
        if C.location.z > -100 and t > T("unos dos") - 0.3 + 0.08 * k:
            aa = a + 0.6 * math.sin(t * 1.3 + ph); rr = CR0 + (r - 0.5) * 0.22
            o.location = C.location + Vector((rr * math.cos(aa), 0.05, rr * math.sin(aa)))
        else: o.location = LEJOS
    # banda de rodadura
    t_qui = T("le quitan"); t_nueva = T("le pegan")
    b, bn = S["band"], S["band_new"]
    sale = seg(t, t_qui, t_qui + 1.0)
    if t < t_nueva + 0.8:
        b.location = G.location + Vector((0, -0.5 * sale, 6.0 * seg(t, t_qui + 0.5, t_nueva + 0.4)))
    else: b.location = LEJOS
    b.rotation_euler = (0, al if t < t_qui else ang(t_qui), 0)
    b.scale = (sq ** -0.3 * hinch, 1, sq * hinch)
    gast = seg(t, T("unos quinientos"), T("luego no"))
    set_color(S["band_m"], tuple(mix(a_, b_, gast) for a_, b_ in zip(BAND, (0.36, 0.35, 0.36))))
    for g in S["grooves"]: g.scale = (1, 1, 1 - 0.85 * gast)
    entra = seg(t, t_nueva - 0.2, t_nueva + 0.9)
    if entra > 0: bn.location = G.location + Vector((0, -0.5 * (1 - entra), 6.0 * (1 - entra))); bn.rotation_euler = (0, al - ang(t_nueva + 0.9) if t > t_nueva + 0.9 else 0, 0)
    else: bn.location = LEJOS
    # llanta al rojo y tapones
    heat = max(0.55 * win01(t, T("con el calor"), T("y el agua"), 0.5, 0.8),
               seg(t, T("al frenar"), T("las llantas se") + 1.2) * (1 - seg(t, T("en vez de"), T("y cuánto") + 0.5)))
    set_color(S["av_rim"], tuple(mix(a_, b_, heat) for a_, b_ in zip(RIM, RIMHOT)))
    t_fun = T("que se funden")
    m = seg(t, t_fun - 0.1, t_fun + 1.4) * (1 - seg(t, T("y cuánto"), T("y cuánto") + 0.5))
    for p in S["plugs"]:
        set_color(p, tuple(mix(a_, b_, min(1, m * 2)) for a_, b_ in zip(BRASS, (1.0, 0.75, 0.3))))
        p.scale = (1, 1 - 0.85 * m, 1)
    # gas dentro de la rueda
    t_n2, t_aire, t_cal, t_agua, t_cong, t_nore = T("está llena de nitrógeno"), T("el aire tiene"), T("el oxígeno puede"), T("y el agua"), T("se congela"), T("el nitrógeno no")
    agit = 1 + 2.5 * seg(t, T("al frenar"), T("explotaría")) * (1 - seg(t, t_sue, t_sue + 1))
    vis_frac = 1 - 0.92 * seg(t, t_sue, T("en vez de reventar") + 0.4)
    ice_i = 0
    n = len(S["gas"])
    for k, (o, a, r, ph, sp) in enumerate(S["gas"]):
        show = cut_open and t < T("y cuánto") and (k / n) < vis_frac
        if not show: o.location = LEJOS; continue
        aa = a - al + 0.35 * math.sin(t * sp * agit + ph)
        rr = (R0 + (r - 0.5) * 0.42 + 0.03 * math.sin(t * 2.3 * sp * agit + ph)) * sq
        o.location = G.location + Vector((rr * math.cos(aa) / sq ** 0.3, 0.06 + 0.12 * ((k * 7) % 5) / 5, rr * math.sin(aa)))
        tipo = "n" if k % 5 else ("o" if k % 10 == 0 else "h")
        es_aire = t_aire - 0.1 < t < T("no reacciona") + 0.2
        if t < t_n2 - 0.3: col = NEUT
        elif es_aire and tipo == "o": col = O2
        elif es_aire and tipo == "h": col = H2O
        else: col = N2
        if t > T("al frenar") and t < T("y cuánto"):
            col = tuple(mix(a_, b_, 0.6 * (agit - 1) / 2.5) for a_, b_ in zip(col, (1.0, 0.75, 0.5)))
        set_color(o, col)
        sc = 1.0 + (0.4 if es_aire and tipo != "n" else 0)
        if es_aire and tipo == "h" and t > t_cong - 0.2 and ice_i < len(S["hielo"]):
            S["hielo"][ice_i].location = o.location; S["hielo"][ice_i].rotation_euler = (t, 0.5 * k, 0.3 * t)
            S["hielo"][ice_i].scale = (min(1, (t - t_cong + 0.2) / 0.4) * 0.13,) * 3; ice_i += 1; o.location = LEJOS
        o.scale = (sc,) * 3
        S.setdefault("anc_o", None)
        if tipo == "o" and k == 0: S["anc_o"] = tuple(o.location)
        if tipo == "h" and k == 5: S["anc_h"] = tuple(o.location)
    for j in range(ice_i, len(S["hielo"])): S["hielo"][j].location = LEJOS
    # llamitas por dentro
    for k, f in enumerate(S["fuego"]):
        if t_cal - 0.1 < t < t_agua:
            aa = math.radians(20 + 14 * k) - al; rr = R0 + 0.27 * (1 if k % 3 else -1)
            f.location = G.location + Vector((rr * math.cos(aa), 0.1, rr * math.sin(aa)))
            f.scale = (0.7 + 0.6 * abs(math.sin(t * 13 + k * 1.7)),) * 3
        else: f.location = LEJOS
    # el gas escapa por los tapones
    for k, f in enumerate(S["fuga"]):
        u = ((t - t_sue) * 1.4 + k / 8.0) % 1.0
        if t_sue < t < T("y cuánto"):
            pk = S["plugs"][k % 3].matrix_world.translation
            dirv = (pk - G.location); dirv.y = 0; dirv = dirv.normalized() if dirv.length > 0 else Vector((0, 0, 1))
            f.location = pk + Vector((0, -0.1 - 1.6 * u, 0)) + dirv * 0.6 * u; f.scale = (1 - 0.5 * u,) * 3
        else: f.location = LEJOS
    # parche de tejido
    tela = S["tela"]; tp = win01(t, T("cruzadas") - 0.2, T("y aquí viene") + 0.2, 0.4, 0.3)
    if tp > 0:
        tela.location = (0.75, -1.3, CZ + 0.85); tela.scale = (tp,) * 3; tela.rotation_euler = (0, 0.15 * math.sin(t * 1.5), 0)
    else: tela.location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.05))

def V_(at, off, lens=40, up=0.95):
    at = Vector(at) + Vector((0, 0, up)); return (tuple(at + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    add(0.0, V_((0.3, 0, 1.0), (-3.4, -6.2, -0.6), 36))
    add(T("cero"), V_((0.2, 0, 1.05), (-2.9, -6.4, -0.7), 36))
    add(T("en un segundo"), V_((0, 0, 1.1), (-2.2, -6.2, 0.0), 36))
    add(T("vamos a mirar"), V_((0, 0, 1.25), (-0.6, -7.4, 0.3), 38))
    add(T("la presión"), V_((0, 0, 1.2), (0, -7.6, 0.4), 38))
    add(T("la rueda de tu") + 0.3, V_((-0.95, 0, 0.6), (0, -13.0, 0.6), 40, 0.7))
    add(T("casi seis"), V_((-0.9, 0, 0.6), (0, -12.8, 0.6), 40, 0.7))
    add(T("pero no está") + 0.6, V_((0, 0, 1.25), (0, -7.2, 0.4), 38))
    add(T("el aire tiene"), V_((0.1, 0, 1.25), (0.6, -6.8, 0.6), 38))
    add(T("y el agua"), V_((-0.1, 0, 1.3), (-0.6, -6.8, 0.6), 38))
    add(T("el nitrógeno no"), V_((0, 0, 1.25), (0, -7.4, 0.4), 38))
    add(T("pero la goma"), V_((0.1, 0, 1.5), (0.2, -7.2, 0.5), 40))
    add(T("cruzadas"), V_((0.25, 0, 1.6), (0.4, -7.4, 0.5), 40))
    add(T("y aquí viene"), V_((0, 0, 1.25), (-0.4, -7.6, 0.6), 38))
    add(T("si la presión"), V_((0, 0, 1.25), (0.3, -7.6, 0.5), 38))
    add(T("así que la llanta"), V_((0, 0, 1.3), (0.2, -7.0, 0.3), 40))
    add(T("y la rueda se"), V_((0, 0, 1.1), (-0.6, -7.2, 0.5), 38))
    add(T("y cuánto"), V_((0, 0, 1.0), (-3.4, -6.4, 0.9), 38))
    add(T("luego no"), V_((0, 0, 1.0), (-3.0, -6.6, 0.8), 38))
    add(T("le quitan") + 0.3, V_((0, -0.4, 1.3), (3.4, -7.6, 1.0), 38))
    add(T("sígueme"), V_((0, -0.6, 1.2), (3.4, -7.8, 1.3), 38))
    add(DUR + 2, V_((0, -0.6, 1.2), (3.6, -9.4, 1.6), 38))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); G = S["G"].location
    C = S["C"].location if S["C"].location.z > -100 else Vector((CX, 0, CCZ))
    pk = S["plugs"][0].matrix_world.translation
    return {"rueda": Pj(G + Vector((0, 0, 1.45))), "coche": Pj(Vector((CX, 0, CCZ)) + Vector((0, 0, 0.7))), "cav": Pj(G + Vector((0.95, 0, 0.35))),
            "o2": Pj(S.get("anc_o") or G), "h2o": Pj(S.get("anc_h") or G), "nyl": Pj(G + Vector((-0.55, -0.6, 1.25))), "tela": Pj((0.75, -1.3, CZ + 1.55)),
            "llanta": Pj(G + Vector((-0.45, -0.5, -0.2))), "tapon": Pj(pk), "banda": Pj(G + Vector((-1.0, -0.4, 1.0))), "hub": Pj(G)}

if __name__ == "__main__":
    run("ruedas", build, pose, anchors)
