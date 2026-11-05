# «Si tuvieras que inventar el cargador de tu móvil…»: el cargador entra en el enchufe y la corriente baja por el cable
# hasta la batería; la carcasa se levanta y queda la placa vacía; la corriente alterna va y vuelve; se colocan pieza a pieza
# los diodos (ya solo avanza), el condensador (avanza lisa), el transformador (crece si va a 50 cambios por segundo),
# el interruptor que parpadea (el transformador encoge), la carcasa grande de antes frente a la pequeña de ahora,
# el campo magnético que salta de bobina a bobina sin tocarse, el chip que habla con la batería y la carga que se llena.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("cargador")
BG = (0.07, 0.08, 0.11); WALL = (0.15, 0.16, 0.2); PLATE = (0.86, 0.86, 0.88); CASE = (0.93, 0.93, 0.95)
PCB = (0.1, 0.38, 0.24); TRACE = (0.85, 0.66, 0.3); METAL = (0.75, 0.77, 0.8); DARK = (0.1, 0.1, 0.12)
COPPER = (0.9, 0.48, 0.22); COPPER2 = (0.95, 0.68, 0.3); CORE = (0.42, 0.44, 0.5); CAPC = (0.2, 0.35, 0.85)
HOT = (1.0, 0.42, 0.18); LOW = (0.3, 0.78, 1.0); FLUX = (0.78, 0.45, 1.0); YEL = (1.0, 0.9, 0.35); BATG = (0.3, 0.9, 0.45)
LEJOS = (0, 0, -300)
TC = Vector((0, -0.9, -0.9))          # centro del transformador
YB = -8.4                              # centro de la batería

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def poly(pts):
    pts = [Vector(p) for p in pts]; L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    return pts, L
def at(path, s):
    pts, L = path; s = max(0.0, min(L[-1], s))
    for i in range(len(pts) - 1):
        if L[i] <= s <= L[i + 1]: return pts[i].lerp(pts[i + 1], (s - L[i]) / max(L[i + 1] - L[i], 1e-6))
    return pts[-1]

Y0 = -0.06
PRIM = poly([(-1.6, Y0, 4.05), (-1.6, Y0, 2.6), (1.6, Y0, 2.6), (1.6, Y0, 1.4), (-1.6, Y0, 1.4), (-1.6, Y0, 0.0), (-0.75, Y0, 0.0)])
SEC = poly([(0.75, Y0, -1.8), (1.6, Y0, -1.8), (1.6, Y0, -3.0), (0.0, Y0, -3.0), (0.0, Y0, -4.1), (0.0, -0.3, -4.4), (0.0, -0.3, YB + 1.8)])
CABLE_S = SEC[1][5]                    # longitud donde empieza el cable
FLUXP = poly([(0, -0.9, -2.3), (0, -0.9, 0.5), (1.2, -0.9, 0.5), (1.2, -0.9, -2.3), (0, -0.9, -2.3)])

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    # pared y enchufe (estático)
    box((40, 0.2, 50), (0, 1.6, -5), WALL)
    cyl(2.1, 0.2, (0, 1.42, 1.2), PLATE, rot=(math.pi / 2, 0, 0), v=48)
    cyl(1.5, 0.25, (0, 1.36, 1.2), (0.78, 0.78, 0.8), rot=(math.pi / 2, 0, 0), v=48)
    for sx in (-0.9, 0.9): cyl(0.2, 0.3, (sx, 1.3, 1.2), DARK, rot=(math.pi / 2, 0, 0), v=16)
    # batería del móvil (estática) y su relleno
    box((3.0, 0.6, 3.8), (0, -0.3, YB), (0.2, 0.21, 0.25))
    box((1.0, 0.4, 0.3), (0, -0.3, YB + 2.05), METAL)
    box((2.6, 0.05, 3.4), (0, -0.62, YB), (0.08, 0.09, 0.1))
    S["fill"] = box((2.5, 0.05, 1), LEJOS, BATG, unique=True)
    # el cargador (todo lo suyo cuelga de CH)
    S["CH"] = CH = empty((0, -1.3, 0))
    box((4.4, 0.15, 8.2), (0, 0.075, 0), PCB, parent=CH)
    for p in (PRIM, SEC):
        pts = p[0]
        for a, b in zip(pts, pts[1:]):
            if a.y < -0.1 or b.y < -0.1: continue
            d = b - a; c = (a + b) / 2
            box((abs(d.x) + 0.16, 0.02, abs(d.z) + 0.16), (c.x, -0.005, c.z), TRACE, parent=CH)
    for sx in (-0.9, 0.9): cyl(0.13, 1.25, (sx, 1.0, 1.2), METAL, parent=CH, rot=(math.pi / 2, 0, 0), v=16)
    S["case"] = box((4.8, 2.0, 8.7), (0, -0.6, 0), CASE, parent=CH, unique=True); alpha(S["case"], 1.0)
    S["cable"] = bar_obj((0.92, 0.92, 0.94), 0.16)
    # piezas que se colocan
    S["diodos"] = []
    for k, x in enumerate((-1.05, -0.35, 0.35, 1.05)):
        e = empty(LEJOS, parent=CH)
        cyl(0.17, 0.55, (0, 0, 0), DARK, parent=e, rot=(0, math.pi / 2, 0), v=20)
        cyl(0.18, 0.1, (0.18, 0, 0), METAL, parent=e, rot=(0, math.pi / 2, 0), v=20)
        S["diodos"].append((e, Vector((x, -0.2, 2.6))))
    e = empty(LEJOS, parent=CH)
    cyl(0.5, 1.5, (0, -0.75, 0), CAPC, parent=e, rot=(math.pi / 2, 0, 0), v=40)
    cyl(0.44, 0.03, (0, -1.51, 0), METAL, parent=e, rot=(math.pi / 2, 0, 0), v=40)
    S["cap"] = (e, Vector((-1.0, -0.1, 1.4)))
    e = empty(LEJOS, parent=CH)
    box((0.7, 0.3, 0.6), (0, -0.25, 0.1), DARK, parent=e); box((0.75, 0.08, 0.3), (0, -0.1, 0.5), METAL, parent=e)
    for dx in (-0.22, 0, 0.22): box((0.06, 0.06, 0.35), (dx, -0.25, -0.35), METAL, parent=e)
    S["led"] = sph(0.12, (0, -0.42, 0.1), (0.3, 0.3, 0.3), parent=e, seg=12, unique=True)
    S["sw"] = (e, Vector((0.55, -0.0, 1.4)))
    S["trafo"] = tr = empty(LEJOS, parent=CH)
    box((0.5, 0.6, 3.4), (0, 0, 0), CORE, parent=tr)
    for sx in (-1.25, 1.25): box((0.4, 0.6, 3.4), (sx, 0, 0), CORE, parent=tr)
    for sz in (1.5, -1.5): box((2.9, 0.6, 0.4), (0, 0, sz), CORE, parent=tr)
    for k in range(4): torus(0.55, 0.13, (0, 0, 1.05 - 0.27 * k), COPPER, parent=tr)
    for k in range(4): torus(0.55, 0.13, (0, 0, -0.45 - 0.27 * k), COPPER2, parent=tr)
    S["trafo_obj"] = tr
    e = empty(LEJOS, parent=CH)
    box((1.0, 0.25, 1.0), (0, -0.12, 0), DARK, parent=e)
    for k in range(5):
        for sx in (-1, 1): box((0.2, 0.05, 0.07), (sx * 0.58, -0.04, -0.36 + 0.18 * k), METAL, parent=e)
    S["chip"] = (e, Vector((0.0, 0.0, -3.0)))
    box((1.0, 0.45, 0.4), (0, -0.25, -4.0), METAL, parent=CH)
    # carcasa grande de antes
    S["vieja"] = box((7.2, 3.0, 11.0), LEJOS, CASE, unique=True); alpha(S["vieja"], 0.3)
    # partículas
    S["prim"] = [sph(0.11, LEJOS, HOT, seg=10, unique=True) for _ in range(18)]
    S["sec"] = [sph(0.11, LEJOS, LOW, seg=10, unique=True) for _ in range(16)]
    S["dato"] = [sph(0.07, LEJOS, (1, 1, 1), seg=8) for _ in range(6)]
    S["flux"] = [sph(0.13, LEJOS, FLUX, seg=10) for _ in range(12)]
    S["chispa"] = [sph(0.09, LEJOS, YEL, seg=8) for _ in range(8)]
    dyn = [cam, CH, S["fill"], S["cable"], S["vieja"], S["prim"], S["sec"], S["dato"], S["flux"], S["chispa"]]
    join_static(dyn)
    return sc, S

def drop(e_pos, t, t0, k=0):
    e, p = e_pos; u = seg(t, t0 + 0.12 * k, t0 + 0.12 * k + 0.5)
    if u <= 0: e.location = LEJOS; return
    e.location = p + Vector((0, -2.8, 2.2)) * (1 - u) + Vector((0, 0, 0.12 * math.sin(math.pi * u)))

def rect_pos(t, w):
    """posición acumulada con velocidad |sen| (corriente rectificada)"""
    x = w * t; n = math.floor(x / math.pi); return (2 * n + 1 - math.cos(x - n * math.pi)) / w

def pose(t, S):
    CH = S["CH"]
    t_cmo, t_230, t_bat, t_dio, t_cond = T("cómo lo harías"), T("en el enchufe"), T("tu batería"), T("unos diodos"), T("un condensador")
    t_300, t_tr, t_cinc, t_enor, t_int = T("pero ahora"), T("necesitas"), T("pero con"), T("tendría"), T("así que añades")
    t_rap, t_peq, t_antes, t_ahora, t_cur = T("cuanto más"), T("más pequeño"), T("por eso los"), T("y los de ahora"), T("y aquí viene")
    t_salta, t_asi, t_falta, t_chip, t_pide = T("la energía"), T("así los"), T("pero aún"), T("un chip"), T("el móvil le")
    t_llena, t_baja, t_cero, t_sig = T("cuando la batería"), T("la corriente baja"), T("casi cero", fin=True), T("sígueme")
    # el cargador entra en el enchufe
    ins = seg(t, 0.0, 0.55)
    CH.location = (0, -1.3 * (1 - ins), 0)
    # carcasa: opaca, se levanta y se va; vuelve al final
    lev = seg(t, t_cmo - 0.1, t_cmo + 0.8); fin = seg(t, t_sig - 0.2, t_sig + 0.7)
    if lev < 1 or fin > 0:
        S["case"].location = (0, -0.6 - 4 * lev * (1 - fin), 6 * lev * (1 - fin)); alpha(S["case"], max(1 - lev, fin))
    else: S["case"].location = LEJOS
    for k, c in enumerate(S["chispa"]):
        u = (t - 0.5) / 0.45
        if 0 < u < 1:
            a = k * math.tau / 8; c.location = (0.9 * (1 if k % 2 else -1) + 0.6 * u * math.cos(a), 0.4, 1.2 + 0.6 * u * math.sin(a)); c.scale = (1 - u,) * 3
        else: c.location = LEJOS
    # cable a la batería
    bar_set(S["cable"], Vector((0, -0.3, -4.2)) + CH.location, (0, -0.3, YB + 1.95))
    nivel = keyed(t, [(0, 0.15), (t_cmo, 0.3), (t_pide, 0.45), (t_llena, 0.8), (t_cero, 0.97), (DUR + 2, 0.98)])
    S["fill"].location = (0, -0.65, YB - 1.7 + 3.4 * nivel / 2); S["fill"].scale = (2.5, 0.05, 3.4 * nivel)
    set_color(S["fill"], BATG if nivel < 0.95 else (0.5, 1.0, 0.6))
    # piezas
    for k, d in enumerate(S["diodos"]): drop(d, t, t_dio, k)
    drop(S["cap"], t, t_cond); drop(S["sw"], t, T("un interruptor")); drop(S["chip"], t, t_chip)
    # transformador: aparece, crece (50 cambios/s), encoge (cientos de miles)
    tr = S["trafo"]; u = seg(t, t_tr + 0.4, t_tr + 1.0)
    if u > 0:
        sz = keyed(t, [(0, 1.0), (t_enor - 0.3, 1.0), (t_enor + 0.6, 1.75), (t_rap, 1.75), (T("el transformador") + 0.6, 0.62), (DUR + 2, 0.62)])
        tr.location = TC + Vector((0, -2.8, 2.2)) * (1 - u) + Vector((0, -0.6 * (sz - 1) if sz > 1 else 0, -1.7 * (sz - 1) if sz > 1 else 0)); tr.scale = (sz,) * 3
    else: tr.location = LEJOS
    sw_on = t > T("que corta") - 0.2
    set_color(S["led"], (1.0, 0.95, 0.4) if (sw_on and int(t * 30) % 2 == 0) else (0.3, 0.3, 0.3))
    # carcasa de antes / de ahora
    v = S["vieja"]
    if t_antes < t < t_cur:
        enc = seg(t, t_ahora - 0.1, t_ahora + 0.9)
        v.location = (0, -0.9, -0.5); v.scale = (7.2 * mix(1.0, 0.68, enc), 3.0 * mix(1.0, 0.75, enc), 11.0 * mix(1.0, 0.8, enc))
        alpha(v, 0.35 * win01(t, t_antes, t_cur, 0.3, 0.3))
    else: v.location = LEJOS
    # corriente del lado de 230 V
    on = t_230 - 0.1 < t < t_sig
    Lp = PRIM[1][-1]; n = len(S["prim"])
    for k, d in enumerate(S["prim"]):
        if not on: d.location = LEJOS; continue
        base = Lp * k / n
        if t < t_dio + 0.8:
            s = base + 0.8 * math.sin(math.tau * 1.3 * t)
        elif t < t_cond + 0.5:
            s = base + 0.9 * rect_pos(t, math.tau * 1.3 / 2)
        elif sw_on and t > t_salta:
            s = base + 1.6 * t
        else:
            s = base + 1.2 * t
        s = s % Lp
        if sw_on and int(t * 30) % 2 == 1 and t < t_rap: s = (base + 1.2 * t) % Lp
        d.location = Vector(at(PRIM, s)) + CH.location
        hot = mix(0, 1, seg(t, t_300 - 0.2, t_300 + 0.5)) if t < t_tr else 1.0
        set_color(d, tuple(mix(a, b, hot) for a, b in zip((1.0, 0.65, 0.25), (1.0, 0.25, 0.15))))
    # corriente del lado de la batería
    Ls = SEC[1][-1]; n = len(S["sec"])
    V = keyed(t, [(0, 5), (T("nueve") - 0.1, 5), (T("nueve") + 0.3, 9), (T("veinte") - 0.1, 9), (T("veinte") + 0.3, 20), (t_llena, 20), (t_llena + 0.6, 9), (DUR + 2, 9)])
    for k, d in enumerate(S["sec"]):
        cab = t < 2.6 or (t_bat - 0.1 < t < t_dio)       # solo el cable (antes de inventar)
        full = t > t_salta + 0.4
        if not (cab or full): d.location = LEJOS; continue
        vel = 1.4 * (1 - seg(t, t_baja, t_cero)) if t > t_llena else 1.4
        if full:
            s = (Ls * k / n + vel * t + (0 if t < t_baja else 0)) % Ls
        else:
            s = CABLE_S + ((Ls - CABLE_S) * k / n + 0.9 * t) % (Ls - CABLE_S)
        p = Vector(at(SEC, s))
        if s < CABLE_S: p += CH.location
        oncab = s >= CABLE_S - 0.01
        if oncab: p += Vector((0, -0.17, 0))
        if t > t_cero - 0.2 and full and (k % 4): p = Vector(LEJOS)
        d.location = p; r = (1.0 + 0.6 * (V - 5) / 15 if full else 1.0) * (1.6 if oncab and V < 8 else (1.15 if oncab else 1.0)); d.scale = (r,) * 3
        set_color(d, LOW if V < 8 else ((0.4, 0.95, 0.8) if V < 15 else (0.9, 1.0, 0.5)))
    # el chip habla con la batería (puntos blancos subiendo)
    for k, d in enumerate(S["dato"]):
        if t_chip + 0.5 < t < t_llena:
            s = Ls - ((Ls - SEC[1][3]) * ((t * 0.9 + k / 6) % 1.0)); d.location = Vector(at(SEC, s)) + Vector((0.32, -0.1, 0))
        else: d.location = LEJOS
    # flujo magnético por el núcleo
    for k, d in enumerate(S["flux"]):
        if t_salta - 0.2 < t < t_falta:
            sz = S["trafo"].scale.x; q = Vector(at(FLUXP, ((t * 1.2 + k / 12) % 1.0) * FLUXP[1][-1]))
            loc = S["trafo"].location + Vector((q.x * sz, -0.35 * sz, (q.z - TC.z) * sz))
            d.location = loc; d.scale = (sz * 0.9,) * 3
        else: d.location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.06))

def V_(at, off, lens=40):
    at = Vector(at) + Vector((0, 0, 0.075 * Vector(off).length * 40 / lens)); return (tuple(at + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    add(0.0, V_((0, 0.5, 0.6), (-8.0, -3.5, 0.6), 35))
    add(1.4, V_((0, -0.3, -2.4), (-6, -17, 2.5), 40))
    add(2.6, V_((0, -0.3, -2.0), (-5, -17, 2.5), 40))
    add(T("en el enchufe"), V_((0, 0, 1.4), (-3, -12, 2.5), 40))
    add(T("tu batería"), V_((0, -0.3, -7.0), (-3, -12, 1.5), 40))
    add(T("unos diodos") + 0.3, V_((0, 0, 2.2), (-2.5, -9, 3.0), 40))
    add(T("un condensador"), V_((-0.3, -0.5, 1.6), (-4, -8.5, 2.0), 40))
    add(T("pero ahora"), V_((0, -0.4, 1.6), (-2, -10, 2.2), 40))
    add(T("necesitas") + 0.6, V_((0, -0.6, -0.4), (-3, -11.5, 2.0), 40))
    add(T("pero con"), V_((0, -0.6, -0.6), (-3.5, -12, 2.2), 40))
    add(T("tendría") + 0.6, V_((0, -0.8, -1.8), (-4.5, -18, 3.0), 40))
    add(T("así que añades") + 0.8, V_((0.4, -0.4, 1.0), (3, -10, 2.0), 40))
    add(T("cuanto más"), V_((0.2, -0.5, 0.0), (2, -12, 2.0), 40))
    add(T("más pequeño") + 1.0, V_((0, -0.6, -0.9), (-2.5, -11, 2.0), 40))
    add(T("por eso los") + 0.6, V_((0, -0.6, -1.2), (-5, -19, 3.0), 40))
    add(T("y aquí viene") - 0.2, V_((0, -0.6, -1.2), (-4.2, -19.5, 2.6), 40))
    add(T("y aquí viene"), V_((0, -0.9, -1.0), (-3, -9, 1.5), 40))
    add(T("las dos bobinas") + 0.8, V_((0, -0.9, -0.9), (-2.8, -6.5, 1.0), 40))
    add(T("así los"), V_((0, -0.9, -1.4), (-3.5, -9, 1.5), 40))
    add(T("pero aún"), V_((0, -0.3, -3.0), (-3, -9, 2.0), 40))
    add(T("el móvil le"), V_((0, -0.3, -4.6), (-3, -12, 2.0), 40))
    add(T("cuando la batería"), V_((0, -0.3, -6.4), (-3, -11, 1.5), 40))
    add(T("sígueme"), V_((0, -0.3, -2.6), (-5, -18, 3.0), 40))
    add(DUR + 2, V_((0, -0.3, -2.4), (-6, -20, 3.5), 40))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); tr = S["trafo"]; sz = tr.scale.x; L = tr.location
    return {"diodo": Pj((0, -0.4, 2.85)), "cap": Pj((-1.0, -1.6, 1.4)), "sw": Pj((0.55, -0.5, 1.9)), "bat": Pj((0, -0.6, YB + 1.9)),
            "trafo": Pj(L + Vector((0, -0.3 * sz, 1.7 * sz))), "prim": Pj(L + Vector((-0.7 * sz, -0.3 * sz, 0.6 * sz))),
            "secu": Pj(L + Vector((0.7 * sz, -0.3 * sz, -0.9 * sz))), "hueco": Pj(L + Vector((0.75 * sz, -0.3 * sz, -0.15 * sz))),
            "chip": Pj((0, -0.3, -2.4)), "vieja": Pj((-3.6, -0.9, 1.5)), "nueva": Pj((-2.4, -0.9, 0.5)), "usb": Pj((0, -0.6, -4.3)), "nucleo": Pj(L + Vector((1.25 * sz, -0.3 * sz, 1.2 * sz)))}

if __name__ == "__main__":
    run("cargador", build, pose, anchors)
