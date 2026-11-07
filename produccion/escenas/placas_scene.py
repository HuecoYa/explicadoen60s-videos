# «Así funcionan las placas solares en un apagón»: el sol dispara rayos contra las placas y la corriente baja por el cable;
# se va la luz en el barrio y todo se para. Dentro, en corte: el inversor con su tapa fuera (condensadores, transistores,
# bobina y relé), la continua que avanza y la alterna que va y viene. Se va la red: el relé se abre. El técnico en el poste
# y la corriente que no debe llegarle. Vuelve la luz, espera y reconecta. Al final, batería, interruptor y la casa como isla.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("placas")
BG = (0.07, 0.08, 0.11); GROUND = (0.2, 0.24, 0.2); WALL = (0.86, 0.8, 0.7); WALLIN = (0.95, 0.92, 0.86); ROOF = (0.62, 0.3, 0.22)
PANEL = (0.1, 0.2, 0.48); PANEL_ON = (0.2, 0.42, 0.85); FRAME = (0.78, 0.8, 0.84); YEL = (1.0, 0.85, 0.2); SUN = (1.0, 0.78, 0.15)
DCC = (0.95, 0.3, 0.25); ACC = (0.25, 0.25, 0.28); INV = (0.94, 0.95, 0.96); INVIN = (0.2, 0.22, 0.27); DARK = (0.1, 0.1, 0.12)
COPPER = (0.9, 0.5, 0.25); CAPC = (0.2, 0.4, 0.9); GREEN = (0.3, 0.9, 0.45); RED = (0.95, 0.25, 0.22); POLE = (0.45, 0.35, 0.25)
SKIN = (0.93, 0.72, 0.6); ORANGE = (1.0, 0.5, 0.1); WATER = (0.15, 0.45, 0.85); OFF = (0.35, 0.36, 0.4); WIN_ON = (1.0, 0.85, 0.45)
LEJOS = (0, 0, -300)
INVC = Vector((-0.8, 1.24, 1.5))       # centro del inversor
SUNP = Vector((3.2, -6.0, 8.0))

def poly(pts):
    pts = [Vector(p) for p in pts]; L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    return pts, L
def at(path, s):
    pts, L = path; s = max(0.0, min(L[-1], s))
    for i in range(len(pts) - 1):
        if L[i] <= s <= L[i + 1]: return pts[i].lerp(pts[i + 1], (s - L[i]) / max(L[i + 1] - L[i], 1e-6))
    return pts[-1]

DC = poly([(-0.9, -1.25, 2.95), (-0.9, -1.15, 2.45), (-0.9, 1.25, 2.45), (-0.9, 1.25, 1.86)])
AC_IN = poly([(-0.54, 1.25, 1.4), (1.85, 1.25, 1.4), (1.85, 1.25, 2.2), (2.3, 0.8, 2.2)])
LINE = poly([(2.3, 0.8, 2.2), (3.6, 0.0, 4.0)])
STREET = poly([(3.6, 0.0, 4.0), (10.0, 0.0, 4.0)])
SW_X = 1.3                               # interruptor de la casa

def prism(pts2d, y0, y1, color, unique=False):
    """prisma: polígono en XZ extruido entre y0 e y1"""
    me = bpy.data.meshes.new("pr"); bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts2d]; b = [bm.verts.new((x, y1, z)) for x, z in pts2d]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    n = len(pts2d)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((a[i], b[i], b[j], a[j]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("pr", me); bpy.context.collection.objects.link(o)
    return setup(o, color, unique=unique)

def wire(path, color, r):
    pts = path[0]
    for a, b in zip(pts, pts[1:]):
        o = bar_obj(color, r); bar_set(o, a, b)

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    # suelo, agua (isla final) y barrio al fondo
    S["ground"] = box((60, 60, 1), (0, 0, -0.5), GROUND, unique=True)
    S["water"] = cyl(30, 0.2, (0, 0, -0.6), WATER, v=64, unique=True)
    S["island"] = cyl(3.0, 0.6, (0, 0, -0.3), (0.3, 0.42, 0.25), v=64, unique=True)
    box((8, 0.8, 0.02), (0.5, -2.6, 0.01), (0.3, 0.3, 0.32))   # acera
    S["wins"] = []
    for k, (x, y, w, h) in enumerate(((-6.5, 6, 3, 4), (-2.5, 8, 2.6, 5.5), (6.5, 6.5, 3.2, 3.5), (10, 9, 3, 6))):
        box((w, 2, h), (x, y, h / 2), (0.26, 0.28, 0.34))
        for i in range(2):
            for j in range(int(h // 1.3)):
                S["wins"].append(box((0.45, 0.05, 0.5), (x - w / 4 + i * w / 2, y - 1.03, 0.9 + j * 1.25), WIN_ON, unique=True))
    # casa en corte: sin pared delantera
    box((4.15, 0.15, 2.5), (0, 1.425, 1.25), WALLIN)               # pared del fondo
    for sx in (-1, 1):
        box((0.15, 3.0, 2.5), (sx * 2.0, 0, 1.25), WALL)
        g = prism([(-1.5, 2.5), (1.5, 2.5), (0, 3.5)], -0.075, 0.075, WALL)    # hastial (YZ)
        g.rotation_euler = (0, 0, math.pi / 2); g.location = (sx * 2.0, 0, 0)
    box((4.0, 3.0, 0.08), (0, 0, 0.04), (0.55, 0.45, 0.35))         # suelo de la casa
    for sx in (-1, 1): box((0.155, 0.01, 2.5), (sx * 2.0, -1.5, 1.25), (1, 1, 1))   # canto del corte
    ang = math.atan2(1.2, 1.8); L = math.hypot(1.8, 1.2) + 0.25
    for sy in (-1, 1):
        r = box((4.5, L, 0.12), (0, sy * 0.9, 3.1 + 0.06), ROOF); r.rotation_euler = (-sy * ang, 0, 0)
    # placas en el faldón delantero
    S["cells"] = []
    for i in range(3):
        for j in range(2):
            e = empty((-1.25 + 1.25 * i, -1.3 + 0.75 * j, 0)); e.location.z = 2.5 + (1.8 + e.location.y) * 1.2 / 1.8 + 0.17
            e.rotation_euler = (ang, 0, 0)
            box((1.15, 0.72, 0.05), (0, 0, 0), FRAME, parent=e)
            c = box((1.08, 0.66, 0.04), (0, 0, 0.012), PANEL, parent=e, unique=True); S["cells"].append(c)
            for q in (-1, 1): box((0.012, 0.66, 0.045), (q * 0.27, 0, 0.012), FRAME, parent=e)
            box((1.08, 0.012, 0.045), (0, 0, 0.012), FRAME, parent=e)
    # sol y rayos
    S["sun"] = sph(0.7, SUNP, SUN, unique=True)
    S["rays"] = [bar_obj(YEL, 0.03) for _ in range(14)]
    # cables
    wire(DC, DCC, 0.022)
    wire(poly([(-0.54, 1.25, 1.4), (SW_X - 0.12, 1.25, 1.4)]), ACC, 0.022); wire(poly([(SW_X + 0.12, 1.25, 1.4)] + [tuple(v) for v in AC_IN[0][1:]]), ACC, 0.022)
    wire(LINE, ACC, 0.018); wire(STREET, ACC, 0.018)
    # inversor (cuerpo abierto) y su tapa
    c = INVC
    box((0.5, 0.03, 0.72), (c.x, 1.335, c.z), INVIN)
    for sx in (-1, 1): box((0.03, 0.2, 0.72), (c.x + sx * 0.25, 1.24, c.z), INV)
    for sz in (-1, 1): box((0.53, 0.2, 0.03), (c.x, 1.24, c.z + sz * 0.36), INV)
    box((0.5, 0.02, 0.1), (c.x, 1.15, c.z + 0.3), INV)
    S["disp"] = box((0.2, 0.012, 0.06), (c.x, 1.135, c.z + 0.3), GREEN, unique=True)
    S["tapa"] = box((0.5, 0.025, 0.55), (c.x, 1.13, c.z - 0.06), INV, unique=True)
    for k in range(2): cyl(0.045, 0.16, (c.x - 0.16 + 0.1 * k, 1.25, c.z + 0.12), CAPC, v=20)
    box((0.12, 0.08, 0.18), (c.x - 0.02 + 0.07, 1.29, c.z + 0.05), (0.6, 0.62, 0.66))
    for k in range(4): box((0.035, 0.02, 0.05), (c.x - 0.03 + 0.04 * k, 1.24, c.z - 0.02 + 0.07 * (k % 2)), DARK)
    torus(0.06, 0.025, (c.x + 0.16, 1.25, c.z + 0.12), COPPER, rot=(math.pi / 2, 0, 0))
    box((0.13, 0.08, 0.1), (c.x + 0.13, 1.27, c.z - 0.2), (0.85, 0.85, 0.88))
    box((0.02, 0.02, 0.02), (c.x + 0.19, 1.22, c.z - 0.16), (0.8, 0.6, 0.3))
    S["rele"] = bar_obj(GREEN, 0.012, unique=True)
    # lámpara
    bar = bar_obj((0.3, 0.3, 0.3), 0.01); bar_set(bar, (0.6, 0.2, 3.3), (0.6, 0.2, 2.35))
    cyl(0.14, 0.08, (0.6, 0.2, 2.37), (0.3, 0.3, 0.32))
    S["bulb"] = sph(0.1, (0.6, 0.2, 2.27), OFF, unique=True)
    S["glow"] = sph(0.22, (0.6, 0.2, 2.27), (1.0, 0.95, 0.7), unique=True)
    # enchufe en la pared y su cable
    box((0.12, 0.02, 0.12), (0.4, 1.34, 0.45), (0.97, 0.97, 0.97))
    o = bar_obj(ACC, 0.015); bar_set(o, (0.4, 1.3, 1.4), (0.4, 1.3, 0.51))
    # interruptor de la casa (cuchilla)
    box((0.22, 0.03, 0.32), (SW_X, 1.33, 1.4), (0.85, 0.86, 0.9))
    S["sw"] = bar_obj(RED, 0.028, unique=True)
    # batería
    S["bat"] = empty(LEJOS)
    box((0.5, 0.25, 0.6), (0, 0, 0.3), (0.25, 0.27, 0.32), parent=S["bat"])
    S["batbars"] = [box((0.36, 0.02, 0.09), (0, -0.13, 0.12 + 0.12 * k), GREEN, parent=S["bat"], unique=True) for k in range(4)]
    S["batw"] = bar_obj(ACC, 0.015)
    # poste, farola y técnico
    cyl(0.1, 4.6, (3.6, 0.0, 2.3), POLE, v=16)
    box((0.9, 0.1, 0.08), (3.6, 0.0, 4.0), POLE)
    for sx in (-0.35, 0.35): cyl(0.03, 0.12, (3.6 + sx, 0, 4.1), (0.85, 0.85, 0.9), v=12)
    o = bar_obj(DARK, 0.03); bar_set(o, (3.6, 0, 3.4), (3.6, -0.6, 3.5))
    S["farola"] = sph(0.11, (3.6, -0.62, 3.42), WIN_ON, scale=(1.4, 1.4, 0.6), unique=True)
    for sx in (-0.18, 0.18):
        o = bar_obj((0.75, 0.75, 0.78), 0.02); bar_set(o, (3.25 + sx, -0.75, 0), (3.45 + sx, -0.15, 3.6))
    for k in range(10):
        a = Vector((3.07 + 0.02 * k, -0.75 + 0.06 * k, 0.36 * k + 0.2)); o = bar_obj((0.75, 0.75, 0.78), 0.015); bar_set(o, a, a + Vector((0.36, 0, 0)))
    S["tech"] = empty(LEJOS)
    S["techbody"] = [cyl(0.15, 0.55, (0, 0, 0.27), ORANGE, parent=S["tech"], unique=True),
                     sph(0.12, (0, 0, 0.68), SKIN, parent=S["tech"], unique=True)]
    sph(0.135, (0, 0, 0.73), YEL, parent=S["tech"], scale=(1, 1, 0.7))
    for sx in (-1, 1): cyl(0.055, 0.5, (sx * 0.08, 0, -0.25), (0.2, 0.25, 0.45), parent=S["tech"])
    S["arm"] = bar_obj(ORANGE, 0.045, unique=True)
    S["sparks"] = [sph(0.035, LEJOS, YEL, seg=8) for _ in range(8)]
    # partículas
    S["pdc"] = [sph(0.035, LEJOS, YEL, seg=10) for _ in range(14)]
    S["pac"] = [sph(0.035, LEJOS, YEL, seg=10, unique=True) for _ in range(30)]
    S["psun"] = [sph(0.06, LEJOS, YEL, seg=10) for _ in range(14)]
    S["pbat"] = [sph(0.03, LEJOS, GREEN, seg=10) for _ in range(5)]
    dyn = [cam, S["ground"], S["water"], S["island"], S["wins"], S["cells"], S["sun"], S["rays"], S["disp"], S["tapa"], S["rele"], S["bulb"],
           S["glow"], S["sw"], S["bat"], S["batw"], S["farola"], S["tech"], S["arm"], S["sparks"], S["pdc"], S["pac"], S["psun"], S["pbat"]]
    join_static(dyn)
    for o in [S["glow"]]:
        m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], 0.35)
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    return sc, S

# ---------------- estado ----------------
def red_on(t):
    """hay luz en la calle"""
    if t < 1.0: return True
    if t < T("y aquí viene") + 1.3: return T("mira dentro") - 0.2 < t
    if t < T("cuando vuelve"): return False
    if t < T("y si quieres"): return True
    return False

def rele_cerrado(t):
    if t < T("se desconecta"): return True
    if t < T("reconectarse"): return False
    if t < T("y si quieres") + 0.6: return True
    return False

def casa_luz(t):
    if t < 2.4: return True
    if t < T("mira dentro"): return False
    if t < T("y aquí viene") + 1.3: return True
    if t < T("reconectarse"): return False
    if t < T("y si quieres") + 0.6: return True
    return t > T("separe") + 0.3

def isla(t): return seg(t, T("así tu casa") - 0.2, T("isla", fin=True))

def pose(t, S):
    t_dc, t_alt, t_inv = T("da corriente continua"), T("tus enchufes"), T("el inversor")
    t_tec, t_mand, t_anti = T("por los técnicos"), T("si tu tejado"), T("a esto se")
    t_bat, t_sw = T("necesitas baterías"), T("con un interruptor")
    rn = red_on(t); rc = rele_cerrado(t); lz = casa_luz(t)
    # barrio
    for w in S["wins"]: set_color(w, WIN_ON if rn else (0.16, 0.17, 0.2))
    set_color(S["farola"], WIN_ON if rn else OFF)
    # sol, rayos y placas (siempre producen)
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    S["sun"].scale = (1 + 0.05 * pulse,) * 3
    for k, r in enumerate(S["rays"]):
        a = k / len(S["rays"]) * math.tau + t * 0.3
        d = Vector((math.cos(a), 0.3 * math.sin(a), math.sin(a)))
        L = 0.9 + 0.35 * (0.5 + 0.5 * math.sin(t * 5 + k))
        bar_set(r, SUNP + d * 0.8, SUNP + d * (0.8 + L))
    for k, p in enumerate(S["psun"]):
        u = (k / len(S["psun"]) + t * 0.7) % 1.0
        tgt = Vector((-1.25 + 1.25 * (k % 3), -1.3 + 0.75 * (k % 2), 3.0))
        p.location = SUNP.lerp(tgt, u)
    for c in S["cells"]: set_color(c, PANEL_ON if pulse > 0.2 else PANEL)
    # corriente continua: avanza mientras el inversor la acepta (o mientras la exporta en el «y si…»)
    peligro = win01(t, t_mand + 0.2, t_anti, 0.2, 0.2) > 0
    dc_on = rc or peligro or t > t_bat + 0.4
    for k, p in enumerate(S["pdc"]):
        if dc_on or t < 2.4:
            p.location = at(DC, (k / len(S["pdc"]) + t * 0.35) % 1.0 * DC[1][-1])
        else:
            # se agolpan al final del cable, quietas
            p.location = at(DC, DC[1][-1] - 0.06 * k) if t > 2.4 else LEJOS
    # alterna: va y viene por la casa, el poste y la calle
    full = AC_IN[1][-1] + LINE[1][-1] + STREET[1][-1]
    for k, p in enumerate(S["pac"]):
        s = k / len(S["pac"]) * full + 0.25 * math.sin(t * 9)
        if s < AC_IN[1][-1]: pt, zona = at(AC_IN, s), 0
        elif s < AC_IN[1][-1] + LINE[1][-1]: pt, zona = at(LINE, s - AC_IN[1][-1]), 1
        else: pt, zona = at(STREET, s - AC_IN[1][-1] - LINE[1][-1]), 2
        isla_mode = t > t_sw + 0.5
        vis = (rn and (zona > 0 or rc)) or (zona == 0 and (rc or (lz and isla_mode)))
        if peligro and zona <= 1:
            # el «y si…»: la corriente del tejado sale hacia el técnico
            s2 = (k / len(S["pac"]) + (t - t_mand) * 0.4) % 1.0 * (AC_IN[1][-1] + LINE[1][-1] * 0.8)
            pt = at(AC_IN, s2) if s2 < AC_IN[1][-1] else at(LINE, s2 - AC_IN[1][-1]); vis = True
            set_color(p, RED)
        else: set_color(p, YEL)
        if isla_mode and zona == 0 and pt.x > SW_X: vis = vis and rn
        p.location = pt if vis else LEJOS
    # tapa del inversor
    u = seg(t, T("mira dentro"), T("mira dentro") + 0.8)
    S["tapa"].location = (INVC.x, mix(1.13, 0.2, u), INVC.z - 0.06 + mix(0, 1.8, u))
    S["tapa"].hide_render = u > 0.97
    # pantalla del inversor
    alarma = (T("si la frecuencia") < t < T("y aquí viene")) or (T("se desconecta") < t < T("reconectarse"))
    set_color(S["disp"], RED if (alarma and math.sin(t * 12) > 0) else (YEL if alarma else GREEN))
    # relé
    a = mix(0.7, 0.0, seg(t, T("reconectarse") - 0.2, T("reconectarse") + 0.1)) if not rc and t < T("y si quieres") else (0.0 if rc else 0.7)
    if t < T("reconectarse"): a = 0.7 * seg(t, T("se desconecta"), T("se desconecta") + 0.15) if not rc else 0.0
    if t > T("y si quieres") + 0.6: a = 0.7 * seg(t, T("y si quieres") + 0.6, T("y si quieres") + 0.75)
    if t > T("con un interruptor"): a = 0.7 * (1 - seg(t, T("con un interruptor"), T("con un interruptor") + 0.3))
    p0 = Vector((INVC.x + 0.07, 1.2, INVC.z - 0.24))
    bar_set(S["rele"], p0, p0 + Vector((0.13 * math.cos(a), 0, 0.13 * math.sin(a))))
    set_color(S["rele"], GREEN if a < 0.2 else RED)
    # lámpara
    set_color(S["bulb"], WIN_ON if lz else OFF)
    S["glow"].hide_render = not lz
    # batería
    ub = seg(t, t_bat, t_bat + 0.5)
    S["bat"].location = (-1.55, 1.15, 0.08) if ub > 0.01 else LEJOS; S["bat"].scale = (ub,) * 3 if ub > 0.01 else (1, 1, 1)
    bar_set(S["batw"], Vector((-1.55, 1.22, 0.7)) if ub > 0.5 else Vector(LEJOS), Vector((-1.05, 1.22, 1.25)) if ub > 0.5 else Vector(LEJOS) + Vector((0, 0, 0.1)))
    nivel = 4 - int(3.0 * seg(t, t_sw + 0.5, DUR + 3))
    for k, b in enumerate(S["batbars"]): b.hide_render = k >= nivel
    for k, p in enumerate(S["pbat"]):
        if t > t_sw + 0.4 and ub > 0.9:
            p.location = Vector((-1.55, 1.22, 0.7)).lerp(Vector((-1.05, 1.22, 1.25)), (k / 5 + t * 0.8) % 1.0)
        else: p.location = LEJOS
    # interruptor de la casa
    sa = 1.1 * seg(t, t_sw + 0.2, t_sw + 0.5)
    q0 = Vector((SW_X - 0.12, 1.29, 1.4))
    bar_set(S["sw"], q0, q0 + Vector((0.24 * math.cos(sa), -0.04, 0.24 * math.sin(sa))))
    set_color(S["sw"], RED if sa > 0.3 else (0.85, 0.86, 0.9))
    # técnico en la escalera
    ut = seg(t, t_tec - 0.3, t_tec + 0.6) * (1 - seg(t, T("cuando vuelve") - 0.3, T("cuando vuelve")))
    S["tech"].location = Vector((3.25, -0.42, 2.95)) + Vector((0, -1.2, -2.5)) * (1 - ut) if ut > 0.01 else LEJOS
    hand = at(LINE, LINE[1][-1] * 0.8)
    sh = S["tech"].location + Vector((0.08, 0.05, 0.5))
    reach = seg(t, T("alguien tiene") - 0.3, T("reparar") + 0.2)
    bar_set(S["arm"], sh, sh.lerp(hand, 0.95 * reach) + Vector((0, 0, 0.001)) if reach > 0.01 else sh + Vector((0.05, 0, -0.3)))
    zap = peligro and t > T("tendría tensión") - 0.2
    for b in S["techbody"]: set_color(b, (RED if math.sin(t * 25) > 0 else YEL) if zap else (ORANGE if b is S["techbody"][0] else SKIN))
    for k, sp in enumerate(S["sparks"]):
        if zap:
            a = t * 31 + k * 0.8; sp.location = hand + Vector((0.12 * math.cos(a), 0.05, 0.12 * math.sin(a * 1.4)))
        else: sp.location = LEJOS
    # isla
    ui = isla(t)
    S["water"].location.z = mix(-0.6, -0.08, ui); S["ground"].location.z = -0.5 - 1.5 * ui
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def cam_lin(t, ks, drift=0.01):
    """interpolación suave tramo a tramo (sin pasarse de largo como Catmull-Rom)"""
    if t <= ks[0][0]: a = b = ks[0]; u = 0
    elif t >= ks[-1][0]: a = b = ks[-1]; u = 0
    else:
        for i in range(len(ks) - 1):
            if ks[i][0] <= t <= ks[i + 1][0]: break
        a, b = ks[i], ks[i + 1]; u = ss((t - a[0]) / max(b[0] - a[0], 1e-4))
    pos = Vector(a[1]).lerp(Vector(b[1]), u); tgt = Vector(a[2]).lerp(Vector(b[2]), u); lens = mix(a[3], b[3], u)
    pos += Vector((math.sin(t * 0.9), 0.7 * math.sin(t * 0.7), 0.8 * math.sin(t * 1.1))) * drift
    return pos, tgt, lens

def V(at_, off, lens=35): at_ = Vector(at_); return (tuple(at_ + Vector(off)), tuple(at_), lens)
def CAM():
    k = []
    def add(t, v, hold=0.0):
        k.append((t,) + v)
        if hold: k.append((t + hold,) + v)
    panel = (0.0, -0.95, 3.15)
    ancho = V((1.0, 0.3, 2.0), (0.6, -8.6, 1.4), 30)
    inv = V((INVC.x + 0.05, 1.2, INVC.z), (0.15, -1.75, 0.15), 35)
    cables = V((-0.35, 1.2, 1.6), (0.2, -2.7, 0.3), 32)
    add(0.0, V(panel, (0.9, -2.2, 2.0), 36))
    add(1.0, V(panel, (1.1, -2.9, 2.3), 34))
    add(3.0, ancho, 2.6)
    add(T("mira dentro") + 0.6, inv)
    add(T("da corriente") - 0.3, cables, 2.0)
    add(T("tus enchufes") + 0.4, V((-0.1, 1.2, 1.6), (0.3, -2.9, 0.3), 32), 4.0)
    add(T("así que en medio"), inv, 3.0)
    add(T("pero para hacerlo"), cables)
    add(T("vigila"), V((INVC.x + 0.1, 1.2, INVC.z + 0.05), (0.2, -2.0, 0.2), 34), 7.0)
    add(T("si se va"), ancho)
    add(T("se desconecta") - 0.2, inv, 2.0)
    add(T("aunque tus placas"), V((-0.3, 0.2, 2.4), (0.4, -5.6, 0.7), 30), 2.0)
    add(T("por los técnicos") + 0.2, V((3.1, -0.2, 3.3), (-0.6, -4.6, 0.1), 34), 2.6)
    add(T("si tu tejado"), V((2.4, 0.2, 2.7), (-0.4, -6.2, 0.3), 30), 4.0)
    add(T("a esto se") + 0.4, V((2.9, 0.0, 3.4), (-0.6, -4.6, 0.1), 34))
    add(T("cuando vuelve") , ancho, 0.8)
    add(T("espera"), inv, 3.0)
    add(T("y si quieres"), ancho)
    add(T("necesitas") + 0.3, V((-0.85, 1.0, 1.0), (0.35, -3.2, 0.5), 30), 1.5)
    add(T("con un interruptor") + 0.2, V((0.95, 1.0, 1.2), (0.0, -2.4, 0.1), 30), 1.6)
    add(T("así tu casa") + 0.2, V((1.0, 0.0, 1.0), (1.0, -10.0, 4.6), 30))
    add(DUR + 2, V((1.0, 0.0, 1.0), (1.6, -11.0, 5.0), 30))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    return {"inv": P((INVC.x, 1.15, INVC.z + 0.38)), "rele": P((INVC.x + 0.13, 1.2, INVC.z - 0.22)), "disp": P((INVC.x, 1.13, INVC.z + 0.3)),
            "dc": P((-0.9, 1.25, 2.2)), "ac": P((0.6, 1.25, 1.4)), "panel": P((0.0, -0.95, 3.4)), "casa": P((0.6, 0.2, 2.27)),
            "linea": P(tuple(at(LINE, LINE[1][-1] * 0.8))), "tech": P((3.25, -0.42, 3.7)), "poste": P((3.6, 0, 4.2)),
            "bat": P((-1.55, 1.1, 0.75)), "sw": P((SW_X, 1.3, 1.55))}

if __name__ == "__main__":
    run("placas", build, pose, anchors)
