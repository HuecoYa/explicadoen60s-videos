# «Así funciona la batería del móvil»: el indicador baja; se levanta la pantalla y la cámara entra en la batería.
# Dentro, en corte: lámina de cobre + grafito (capas), separador con poros, óxido con litio + lámina de aluminio,
# líquido entre medias y el cable exterior con cargador/pantalla. El litio cruza al cargar y vuelve al usarlo;
# algunos átomos se quedan atrapados (grises), ciclos rápidos, y el calor acelera el desgaste.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Matrix

T, DUR = cargar("bateria")
BODY = (0.18, 0.19, 0.22); DISP = (0.06, 0.07, 0.1); POUCH = (0.72, 0.76, 0.82); CU = (0.9, 0.5, 0.25); ALU = (0.75, 0.78, 0.82)
GRAF = (0.22, 0.23, 0.26); OXI = (0.78, 0.36, 0.3); SEP = (0.95, 0.95, 0.92); ELEC = (0.55, 0.8, 1.0); LI = (0.78, 0.5, 1.0)
DEAD = (0.45, 0.45, 0.48); EL = (0.25, 0.75, 1.0); GREEN = (0.3, 0.85, 0.4); HOTC = (1.0, 0.55, 0.25)
O = Vector((0, -1.5, 0.76)); SC = 0.035          # el modelo «macro» vive dentro de la batería, a escala
def M(v): v = Vector(v); return O + SC * v

ROWS = [1.15 + 0.7 * k for k in range(6)]
XG = [-3.9, -3.1, -2.3]; XO = [3.8, 2.9, 2.0]
IONS = [(XO[c], XG[c], ROWS[r]) for r in range(6) for c in range(3)]   # (x en óxido, x en grafito, z)
STUCK1 = [2, 9, 13]; STUCK2 = [5]                                   # se quedan atrapados (y uno más con calor)
WIRE = [Vector((4.75, 0, 5.8)), Vector((4.75, 0, 7.6)), Vector((-4.6, 0, 7.6)), Vector((-4.6, 0, 5.8))]

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def build():
    sc, cam = scene_setup(world=(0.08, 0.09, 0.12), shadow=0.3)
    S = {"cam": cam}
    box((80, 80, 0.1), (0, 0, -0.05), (0.16, 0.17, 0.21))
    rounded_slab(7.3, 15.4, 1.0, 0.75, (0, 0, 0), BODY)
    S["pouch"] = box((5.6, 9.0, 0.36), (0, -1.5, 0.94), POUCH, unique=True)
    box((5.0, 2.6, 0.2), (0, 5.2, 0.85), (0.1, 0.35, 0.2)); box((1.4, 1.0, 0.16), (0.8, 5.0, 1.0), (0.1, 0.1, 0.12))
    box((1.2, 0.5, 0.1), (-1.6, 3.2, 0.95), (0.85, 0.7, 0.35))
    # pantalla (tapa) con icono de batería
    S["tapa"] = empty((0, 0, 0))
    rounded_slab(7.1, 15.2, 0.95, 0.22, (0, 0, 1.15), DISP, parent=S["tapa"])
    box((3.4, 1.6, 0.04), (-0.2, 0.5, 1.39), (0.85, 0.87, 0.9), parent=S["tapa"])
    box((3.2, 1.4, 0.05), (-0.2, 0.5, 1.4), DISP, parent=S["tapa"])
    box((0.25, 0.6, 0.05), (1.6, 0.5, 1.4), (0.85, 0.87, 0.9), parent=S["tapa"])
    S["nivel"] = box((1.0, 1.2, 0.06), (-1.75, 0.5, 1.42), GREEN, parent=S["tapa"], unique=True)
    for k in range(3): box((5.8, 0.5, 0.03), (0, -3.8 - 1.0 * k, 1.39), (0.2, 0.22, 0.3), parent=S["tapa"])
    # ---- modelo macro ----
    S["macro"] = mac = empty(O); mac.scale = (SC, SC, SC)
    box((10.4, 3.4, 0.3), (0, 0, -0.1), (0.12, 0.13, 0.16), parent=mac)
    box((80, 0.2, 60), (0, 6.0, 10), (0.09, 0.1, 0.13), parent=mac)      # fondo oscuro dentro de la batería
    box((80, 40, 0.2), (0, 0, -0.4), (0.11, 0.12, 0.15), parent=mac)
    box((0.15, 3.0, 5.6), (-4.6, 0, 3.0), CU, parent=mac)
    S["graf"] = [box((2.6, 2.0, 0.14), (-3.1, 0.35, 0.8 + 0.7 * k), GRAF, parent=mac) for k in range(7)]
    zs = [0.3] + [z for r in ROWS for z in (r - 0.18, r + 0.18)] + [5.6]
    for a, b in zip(zs[0::2], zs[1::2]): box((0.22, 3.0, b - a), (0, 0, (a + b) / 2), SEP, parent=mac)
    for x in (1.55, 2.45, 3.35, 4.25):
        for k in range(7): box((0.46, 1.6, 0.46), (x, 0.35, 0.8 + 0.7 * k), OXI, parent=mac)
    box((0.15, 3.0, 5.6), (4.75, 0, 3.0), ALU, parent=mac)
    S["elec"] = box((9.2, 2.8, 5.4), (0.05, 0, 3.0), ELEC, parent=mac, unique=True); alpha(S["elec"], 0.16)
    for a, b in zip(WIRE, WIRE[1:]):
        o = bar_obj((0.15, 0.15, 0.18), 0.12, parent=mac); bar_set(o, a, b)
    S["cargador"] = box((1.8, 1.0, 1.0), (0, 0, 7.6), (0.95, 0.95, 0.95), parent=mac, unique=True)
    S["pant"] = box((1.9, 0.3, 1.3), (0, 0, 7.75), (0.3, 0.32, 0.4), parent=mac, unique=True)
    S["ions"] = [sph(0.31, (x, -0.85, z), LI, parent=mac, seg=16, unique=True) for x, _, z in IONS]
    S["els"] = [sph(0.24, (0, 0, -50), EL, parent=mac, seg=10) for _ in range(10)]
    S["sol"] = sph(0.9, (0, 0, -50), (1.0, 0.8, 0.2), parent=mac, unique=True)
    join_static([cam, S["pouch"], S["tapa"], S["macro"]])
    return sc, S

def cmix(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))

def wire_pt(s):
    L = [(b - a).length for a, b in zip(WIRE, WIRE[1:])]; s = (s % 1.0) * sum(L)
    for (a, b), l in zip(zip(WIRE, WIRE[1:]), L):
        if s <= l: return a.lerp(b, s / l)
        s -= l
    return WIRE[-1]

def ion_u(k, t):
    """0 = en el óxido, 1 = metido en el grafito"""
    t_ch, t_rush, t_uso = T("el litio suelta"), T("y el porcentaje"), T("el litio vuelve")
    t_atr, t_mil, t_ojo, t_hoy, t_man = T("algunos átomos"), T("muchos móviles"), T("pero ojo"), T("si gastas"), T("y la otra")
    lento = [0, 4, 8, 13, 16]
    if k in lento: a = t_ch + 1.4 * lento.index(k)
    else: a = t_rush - 1.0 + 0.16 * (k - sum(1 for j in lento if j < k))
    u = seg(t, a, a + 1.6 if k in lento else a + 0.7)
    u *= 1 - seg(t, t_uso + 0.25 * k, t_uso + 0.9 + 0.25 * k)
    # desgaste: vuelven a cargar y al soltar algunos se quedan
    u = max(u, seg(t, T("pero cada") + 0.05 * k, T("pero cada") + 0.8 + 0.05 * k) * (1 - seg(t, t_atr + 0.05 * k, t_atr + 0.9 + 0.05 * k)))
    # ciclos rápidos
    if t_mil - 0.2 < t < t_ojo:
        f = 0.5 - 0.5 * math.cos(2 * math.pi * (t - t_mil) / 1.1 - 0.2 * k)
        u = max(u, f * win01(t, t_mil - 0.2, t_ojo, 0.5, 0.5))
    # un ciclo: lleno → la mitad hoy, la otra mitad mañana
    full = seg(t, T("un ciclo no") - 0.3, T("un ciclo no") + 0.6)
    if t > T("un ciclo no") - 0.3:
        mitad = k % 2 == 0
        vac = seg(t, t_hoy + 0.3, t_hoy + 1.3) if mitad else seg(t, t_man + 0.2, t_man + 1.2)
        u = max(u, full * (1 - vac))
    if k in STUCK1 and t > t_atr: u = 1.0
    if k in STUCK2 and t > t_mil + 3.0: u = 1.0
    return u

def dead(k, t):
    if k in STUCK1: return seg(t, T("algunos átomos") + 1.0 + 0.3 * STUCK1.index(k), T("algunos átomos") + 1.4 + 0.3 * STUCK1.index(k))
    if k in STUCK2: return seg(t, T("muchos móviles") + 3.0, T("muchos móviles") + 3.5)
    return 0.0

def pose(t, S):
    t_abre = T("abre la batería")
    S["tapa"].location = Vector((0, 0, 0)).lerp(Vector((9.5, 2.0, 3.0)), seg(t, t_abre, t_abre + 1.0))
    S["tapa"].rotation_euler = (0, -0.5 * seg(t, t_abre, t_abre + 1.0), 0)
    lvl = mix(0.64, 0.5, seg(t, 0, 4.5))
    w = 3.1 * lvl; S["nivel"].scale.x = w; S["nivel"].location.x = -1.75 + w / 2
    set_color(S["nivel"], cmix(GREEN, (1.0, 0.75, 0.2), seg(t, 1.0, 4.0)))
    # la funda de la batería desaparece cuando la cámara entra
    S["pouch"].location.z = 0.94 if t < T("son dos") - 0.4 else -30
    # iones
    hot = seg(t, T("el calor"), T("el calor") + 0.8)
    for k, (o, (xo, xg, z)) in enumerate(zip(S["ions"], IONS)):
        u = ion_u(k, t); jit = Vector((0, 0, 0))
        if hot > 0:
            r = random.Random(k * 7 + int(t * 12)); jit = Vector((r.uniform(-1, 1), 0, r.uniform(-1, 1))) * 0.12 * hot
        o.location = Vector((mix(xo, xg, u), -0.85, z)) + jit
        d = dead(k, t)
        set_color(o, cmix(LI, DEAD, d)); o.scale = (1 - 0.15 * d,) * 3
    c = cmix(ELEC, HOTC, hot); S["elec"].active_material.diffuse_color = (*lin(c), 0.16 + 0.1 * hot)
    # electrones por el cable: cargando van del aluminio al cobre (por el cargador); usándolo, al revés
    carga = win01(t, T("el litio suelta"), T("cuando usas"), 0.3, 0.3)
    uso = win01(t, T("el litio vuelve"), T("pero cada"), 0.3, 0.3)
    for k, e in enumerate(S["els"]):
        if carga > 0.01: e.location = wire_pt(k / 10 + t * 0.35); e.scale = (carga,) * 3
        elif uso > 0.01: e.location = wire_pt(k / 10 - t * 0.35); e.scale = (uso,) * 3
        else: e.location = (0, 0, -50)
    S["cargador"].location.z = 7.6 if t < T("cuando usas") + 0.3 or t > T("un ciclo no") else -50
    S["pant"].location.z = 7.75 if T("cuando usas") + 0.3 <= t <= T("un ciclo no") else -50
    set_color(S["pant"], cmix((0.3, 0.32, 0.4), (1.0, 0.95, 0.55), uso))
    set_color(S["cargador"], cmix((0.95, 0.95, 0.95), (0.4, 1.0, 0.5), carga * (0.5 + 0.5 * math.sin(t * 8))))
    S["sol"].location = (0, 0, 10.0) if t > T("no lo dejes") - 0.2 else (0, 0, -50)
    S["sol"].scale = (seg(t, T("no lo dejes") - 0.2, T("no lo dejes") + 0.3) + 0.001,) * 3
    pos, tgt, lens = cam_state(t, CAM(), drift=0.0)
    apply_cam(S["cam"], pos, tgt, lens)

def orbw(tg, d, el, az, lens=35):
    tg = Vector(tg); el, az = math.radians(el), math.radians(az)
    return (tuple(tg + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))), tuple(tg), lens)
def orbm(tg, d, el, az, lens=35, up=2.2):
    """como orbw pero en coordenadas del modelo macro; mira un poco más arriba para que el modelo quede bajo los subtítulos"""
    p, g, l = orbw(tg, d * 1.12, el, az, lens); g = Vector(g) + Vector((0, 0, up)); return (tuple(M(p)), tuple(M(g)), l)

def CAM():
    ab, dos = T("abre la batería"), T("son dos")
    return [(0.0,) + orbw((-0.4, 0.3, 1.4), 7.0, 62, -18), (2.5,) + orbw((-0.4, 0.3, 1.4), 8.5, 60, -10),
            (ab,) + orbw((0, -0.5, 1.2), 12.0, 58, -8), (ab + 1.0,) + orbw((0, -1.5, 1.0), 9.0, 60, -6),
            (dos - 0.35,) + orbw((0, -1.5, 0.9), 2.2, 40, -10, 32), (dos + 0.4,) + orbm((0, 0, 3.4), 20, 12, -14, 32),
            (T("separadas por"),) + orbm((0, 0, 3.2), 17, 10, -10, 32), (T("a un lado"),) + orbm((-2.6, 0, 3.0), 12, 12, -18, 32),
            (T("al otro"),) + orbm((2.6, 0, 3.0), 12, 12, 14, 32), (T("y entre medias"),) + orbm((0, 0, 3.2), 15, 12, -6, 32),
            (T("cuando enchufas"),) + orbm((0, 0, 4.3), 20, 14, -10, 32), (T("se mete entre"),) + orbm((-2.8, 0, 3.0), 11, 14, -16, 32),
            (T("mientras"),) + orbm((0, 0, 4.4), 20, 14, -8, 32), (T("y el porcentaje"),) + orbm((0, 0, 3.6), 18, 12, 6, 32),
            (T("el litio vuelve"),) + orbm((0, 0, 4.2), 20, 14, 10, 32), (T("pero cada"),) + orbm((-1.0, 0, 3.2), 16, 12, -10, 32),
            (T("algunos átomos") + 0.8,) + orbm((-2.8, 0, 3.0), 11, 14, -14, 32), (T("muchos móviles"),) + orbm((0, 0, 3.6), 18, 16, -6, 32),
            (T("pero ojo"),) + orbm((0, 0, 3.6), 19, 14, 8, 32), (T("y un truco"),) + orbm((0, 0, 4.2), 19, 14, -4, 32),
            (DUR + 2,) + orbm((0, 0, 4.6), 22, 16, -10, 32)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, M(v))
    a = {"icono": proj(sc, cam, Vector((-0.2, 0.5, 1.45)) + S["tapa"].location), "pouch": proj(sc, cam, (0, -1.5, 1.2)),
         "graf": Pj((-3.1, 0, 5.2)), "oxi": Pj((2.9, 0, 5.2)), "sep": Pj((0, 0, 5.7)), "elec": Pj((-1.0, 0, 0.6)),
         "cu": Pj((-4.6, 0, 6.0)), "al": Pj((4.75, 0, 6.0)), "dev": Pj((0, 0, 8.4)), "wire": Pj(tuple(wire_pt(0.5 - 0.2))),
         "ion0": Pj(tuple(S["ions"][0].location)), "ion4": Pj(tuple(S["ions"][4].location))}
    for k in STUCK1 + STUCK2: a["st%d" % k] = Pj(tuple(S["ions"][k].location))
    return a

if __name__ == "__main__":
    run("bateria", build, pose, anchors)
