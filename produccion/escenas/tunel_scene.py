# «¿Y si construyes un túnel bajo un río?»: corte del río y del terreno; derrumbe al cavar → escudo → tuneladora con rueda de corte,
# cámara de tierra a presión, anillos de dovelas, gatos hidráulicos, juntas de goma, mortero, bomba; la broma y Brunel.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("tunel")
WATER = (0.3, 0.58, 0.9); MUD = (0.42, 0.32, 0.24); MUD2 = (0.36, 0.27, 0.2); GRASS = (0.42, 0.68, 0.35); BANK = (0.6, 0.45, 0.3)
CONC = (0.72, 0.72, 0.74); CONC2 = (0.62, 0.62, 0.65); TBM = (0.98, 0.75, 0.15); STEEL = (0.6, 0.62, 0.66); VOID = (0.16, 0.14, 0.13)
ZT, RO, RI = -6.0, 1.3, 1.08     # eje del túnel, radio exterior e interior
X_INI, X_FIN = -11.0, 14.0
RING = 0.62

def media_corona(r_out, r_in, largo, color, a0=-math.pi / 2, a1=math.pi / 2, n=24, parent=None, loc=(0, 0, 0), unique=False):
    """media corona del lado de atrás (y>=0) extruida a lo largo de X; la cámara mira desde y<0 y ve el corte"""
    me = bpy.data.meshes.new("corona"); bm = bmesh.new(); vs = []
    for x in (0, largo):
        fila = []
        for k in range(n + 1):
            a = mix(a0, a1, k / n); c, s_ = math.cos(a), math.sin(a)
            fila.append((bm.verts.new((x, r_out * c, r_out * s_)), bm.verts.new((x, r_in * c, r_in * s_))))
        vs.append(fila)
    for k in range(n):
        o0, i0 = vs[0][k]; o1, i1 = vs[0][k + 1]; O0, I0 = vs[1][k]; O1, I1 = vs[1][k + 1]
        bm.faces.new((o0, o1, O1, O0)); bm.faces.new((i0, I0, I1, i1)); bm.faces.new((o0, i0, i1, o1)); bm.faces.new((O0, O1, I1, I0))
    for k in (0, n):
        o, i = vs[0][k]; O, I = vs[1][k]; bm.faces.new((o, O, I, i))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("corona", me); bpy.context.collection.objects.link(ob); ob.location = loc
    return setup(ob, color, parent, unique=unique)

def build():
    sc, cam = scene_setup(world=(0.65, 0.82, 0.96))
    S = {"cam": cam}
    # río y terreno en corte (todo en y>=0; la cámara mira desde y<0)
    box((70, 30, 1.5), (0, 15, -0.75), WATER)
    box((70, 30, 2.5), (0, 15, -2.75), MUD)
    S["suelo"] = box((70, 30, 11), (0, 15, -9.5), MUD2)
    corte = cyl(RO + 0.2, X_FIN - X_INI, ((X_INI + X_FIN) / 2, 0, ZT), MUD2, rot=(0, math.pi / 2, 0), v=48)
    corte.hide_render = True; corte.hide_viewport = True
    m = S["suelo"].modifiers.new("hueco", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = corte; m.solver = "EXACT"
    S["corte"] = corte
    box((20, 30, 2.6), (-20, 15, 0.0), BANK); box((20, 30, 0.2), (-20, 15, 1.4), GRASS)
    box((20, 30, 2.6), (24, 15, 0.0), BANK); box((20, 30, 0.2), (24, 15, 1.4), GRASS)
    rng = random.Random(3)
    for k in range(60):
        x, z = rng.uniform(-30, 30), rng.uniform(-14, -2)
        if abs(z - ZT) < RO + 0.6 or (X_INI - 2.5 < x < X_INI + 0.2): continue
        sph(rng.uniform(0.1, 0.3), (x, 0.0, z), (0.5, 0.4, 0.3), scale=(1.4, 0.2, 1))
    # barco en la superficie
    S["barco"] = empty((0, 4, 0))
    box((4, 1.6, 0.6), (0, 0, 0.1), (0.9, 0.35, 0.25), parent=S["barco"]); box((1.6, 1.2, 0.8), (-0.6, 0, 0.8), (0.95, 0.95, 0.95), parent=S["barco"])
    # pozo de entrada en la orilla izquierda
    box((2.2, 0.05, 7.4), (X_INI - 1.2, -0.02, -2.3), VOID)
    # hueco excavado (crece con el avance) y derrumbe inicial
    S["tapa"] = box((1, 0.06, 2 * RO + 0.5), (0, -0.03, ZT), MUD2, unique=True)
    S["cav"] = box((1, 0.05, 1.8), (X_INI + 0.5, -0.08, ZT), VOID, unique=True)
    S["trozos"] = [box((0.35, 0.3, 0.3), (0, 0, -40), MUD) for _ in range(10)]
    S["agua"] = [sph(0.12, (0, 0, -40), WATER) for _ in range(18)]
    # tuneladora (media sección): cuerpo, rueda de corte con cuchillas, cámara de tierra, gatos
    tbm = empty((0, 0, ZT)); S["tbm"] = tbm
    media_corona(RO + 0.08, RO - 0.05, 3.2, TBM, parent=tbm, loc=(-3.2, 0, 0))
    S["rueda"] = media_corona(RO + 0.08, 0.0, 0.18, (0.55, 0.57, 0.6), parent=tbm, loc=(0.0, 0, 0), unique=True)
    S["cuchillas"] = [box((0.2, 0.12, 0.12), (0, 0, 0), (0.85, 0.87, 0.9), parent=tbm) for _ in range(12)]
    S["camara"] = media_corona(RO - 0.06, 0.0, 0.7, MUD, parent=tbm, loc=(-0.75, 0, 0), unique=True)
    media_corona(0.35, 0.0, 2.2, STEEL, parent=tbm, loc=(-3.0, 0, 0))   # eje y motor
    S["gatos"] = [bar_obj(TBM, 0.06, unique=True) for _ in range(3)]
    S["flechas"] = []
    for k in range(5):
        bpy.ops.mesh.primitive_cone_add(radius1=0.18, radius2=0, depth=0.45, location=(0, 0, -40)); f = bpy.context.object; setup(f, (0.4, 0.75, 1.0))
        f.rotation_euler = (0, -math.pi / 2, 0); S["flechas"].append(f)
    # anillos de dovelas (3 piezas por media sección), juntas y mortero
    S["anillos"] = []
    n = int((X_FIN - X_INI) / RING)
    for i in range(n):
        x = X_INI + i * RING; piezas = []
        for j in range(3):
            a0 = -math.pi / 2 + j * math.pi / 3 + 0.02; a1 = -math.pi / 2 + (j + 1) * math.pi / 3 - 0.02
            piezas.append(media_corona(RO, RI, RING - 0.04, CONC if (i + j) % 2 else CONC2, a0=a0, a1=a1, n=8, loc=(x, 0, ZT), unique=True))
        S["anillos"].append(piezas)
    S["juntas"] = [media_corona(RO, RI, 0.04, (0.1, 0.1, 0.1), loc=(X_INI + i * RING + RING - 0.04, 0, ZT), unique=True) for i in range(n)]
    S["mortero"] = [media_corona(RO + 0.18, RO, RING, (0.55, 0.55, 0.5), loc=(X_INI + i * RING, 0, ZT), unique=True) for i in range(n)]
    # bomba en el punto más bajo
    S["bomba"] = box((0.6, 0.5, 0.5), (2.0, 0.3, ZT - RI + 0.25), (0.25, 0.45, 0.85), unique=True)
    # tabla con la broma (bicho que perfora la madera)
    S["tabla"] = empty((-4, -1.5, 2.6))
    box((4.0, 0.5, 1.0), (0, 0, 0), (0.7, 0.5, 0.3), parent=S["tabla"])
    for k in range(6): box((4.0, 0.52, 0.04), (0, 0, -0.4 + k * 0.16), (0.62, 0.43, 0.25), parent=S["tabla"])
    S["galeria"] = box((1, 0.05, 0.22), (0, -0.27, 0), VOID, parent=S["tabla"], unique=True)
    S["broma"] = [sph(0.11, (0, 0, 0), (0.95, 0.9, 0.8), parent=S["tabla"]) for _ in range(7)]
    join_static([cam, S["suelo"], S["corte"], S["barco"], S["tapa"], S["cav"], S["trozos"], S["agua"], tbm, S["gatos"], S["flechas"], S["anillos"], S["juntas"],
                 S["mortero"], S["bomba"], S["tabla"], S["galeria"]])
    return sc, S

def pose(t, S):
    t_cav, t_derr, t_esc, t_tun = T("empiezas cavando"), T("se derrumba"), T("usas un escudo"), T("tuneladora")
    t_rio, t_cam, t_av = T("el río empuja"), T("cámara llena"), T("y avanza")
    t_sin, t_anil, t_dov, t_gatos = T("sin paredes"), T("anillos de hormigón"), T("dovelas"), T("gatos hidráulicos")
    t_goma, t_mort, t_bomb, t_broma, t_brunel = T("juntas de goma"), T("mortero"), T("bombas"), T("de la broma"), T("marc brunel")
    S["barco"].location.x = -8 + 0.6 * t
    # 1) cavar a mano: hueco pequeño junto al pozo, derrumbe y agua
    cav = seg(t, t_cav, t_cav + 1.5) * (1 - seg(t, t_esc - 0.2, t_esc + 0.3))
    S["cav"].scale.x = max(0.001, 3.5 * cav); S["cav"].location.x = X_INI + 1.75 * cav
    rng = random.Random(1)
    for k, o in enumerate(S["trozos"]):
        u = seg(t, t_derr + k * 0.05, t_derr + 0.8 + k * 0.05)
        x = X_INI + rng.uniform(0.3, 3.2)
        o.location = (x, -0.1, mix(ZT + 0.9, ZT - 0.7, u)) if t_derr < t < t_esc else (0, 0, -40)
    for k, o in enumerate(S["agua"]):
        u = ((t - t_derr) * 1.4 + k / 18) % 1.0
        o.location = (X_INI + 0.3 + 3 * (k / 18), -0.1, ZT + 1.0 - 1.8 * u) if t_derr + 0.4 < t < t_esc else (0, 0, -40)
    # 2) avance de la tuneladora (a saltos de un anillo con los gatos)
    vis = t > t_esc - 0.2
    pasos = keyed(t, [(0, 0.0), (t_esc, 0.0), (t_rio, 6.0), (t_sin, 10.0), (t_gatos, 16.0), (t_gatos + 2.5, 18.0), (t_goma, 22.0), (DUR, 34.0)])
    xf = X_INI + 3.2 + pasos * RING                       # cara de corte
    S["tbm"].location = (xf if vis else -60, 0, ZT)
    xt = xf + 0.4 if vis else X_INI
    S["tapa"].scale.x = max(0.001, X_FIN - xt); S["tapa"].location.x = (X_FIN + xt) / 2
    for k, c in enumerate(S["cuchillas"]):
        a = t * 2.2 + k * math.tau / 12; y, z = RO * 0.85 * math.cos(a), RO * 0.85 * math.sin(a)
        c.location = (0.2, y, z) if y >= 0.05 and t > t_tun - 0.3 else (0, 0, -40)
    S["rueda"].hide_render = t < t_tun - 0.3
    # río empuja / cámara a presión
    for k, f in enumerate(S["flechas"]):
        if t_rio - 0.2 < t < t_av + 0.6:
            d = 0.35 * math.sin(t * 6 + k)
            f.location = (xf + 1.4 + d, -0.2, ZT - 1.0 + 0.5 * k)
        else: f.location = (0, 0, -40)
    pres = win01(t, t_cam - 0.2, t_av + 0.8)
    set_color(S["camara"], tuple(mix(a, b, pres * (0.5 + 0.5 * math.sin(t * 8))) for a, b in zip(MUD, (0.75, 0.45, 0.25))))
    # anillos: aparecen detrás de la cola de la máquina (desde «anillos»; antes se ve el hueco sin paredes)
    cola = xf - 3.2
    for i, (piezas, junta, mort) in enumerate(zip(S["anillos"], S["juntas"], S["mortero"])):
        x = X_INI + i * RING
        hecho = t > t_anil - 0.3 and x + RING < cola + 0.05
        reciente = hecho and x + RING > cola - RING
        for j, p in enumerate(piezas):
            p.hide_render = not hecho
            if reciente and t < t_goma: p.hide_render = not (t * 3 % 3 > j)   # pieza a pieza, como un puzle
        junta.hide_render = not hecho
        set_color(junta, (0.1, 0.1, 0.1) if win01(t, t_goma, t_mort, 0.2, 0.2) < 0.5 else (0.95, 0.85, 0.2))
        mort.hide_render = not (hecho and t > t_mort - 0.2 and x < cola - 2 * RING)
    # gatos hidráulicos entre la cola y el último anillo
    gl = 0.35 + 0.3 * (0.5 + 0.5 * math.sin((t - t_gatos) * 4)) if t_gatos - 0.3 < t < t_goma else 0.35
    for k, g in enumerate(S["gatos"]):
        z = ZT + (k - 1) * 0.65
        if t > t_anil - 0.3: bar_set(g, (cola, 0.55, z), (cola + gl, 0.55, z))
        else: g.location = (0, 0, -40)
    S["bomba"].hide_render = t < t_bomb - 0.2
    # la broma perforando la tabla
    S["tabla"].location.z = 2.6 if t_broma - 0.5 < t < t_brunel + 0.3 else -40
    u = seg(t, t_broma - 0.3, t_broma + 2.6); head = -1.8 + 3.2 * u
    S["galeria"].scale.x = max(0.001, head + 1.9); S["galeria"].location.x = (head - 1.9) / 2
    for k, b in enumerate(S["broma"]):
        b.location = (head - k * 0.15, -0.3, 0.04 * math.sin(t * 9 + k))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.04))

def V(at, d, h=0.8, lens=30, dx=0.0): at = Vector(at); return ((at.x + dx, at.y - d, at.z + h), tuple(at), lens)
def CAM():
    tbm_x = lambda p: X_INI + 3.2 + p * RING
    return [(0.0,) + V((-1, 0, -3.0), 21, 1.5), (T("empiezas cavando") - 0.3,) + V((-6, 0, -4.0), 14, 1.0),
            (T("se derrumba"),) + V((X_INI + 2, 0, ZT + 0.5), 7.5, 0.5), (T("usas un escudo"),) + V((X_INI + 3, 0, ZT), 9.0, 0.6),
            (T("tuneladora"),) + V((tbm_x(2), 0, ZT), 6.5, 0.4, 34, 1.5), (T("el río empuja"),) + V((tbm_x(6), 0, ZT + 2.0), 11, 0.8),
            (T("cámara llena"),) + V((tbm_x(7), 0, ZT), 6.0, 0.4, 34), (T("sin paredes"),) + V((tbm_x(10) - 4, 0, ZT), 9.0, 0.6),
            (T("dovelas"),) + V((tbm_x(12) - 4, 0, ZT), 6.0, 0.5, 34), (T("gatos hidráulicos"),) + V((tbm_x(16) - 3.2, 0, ZT), 5.0, 0.4, 36),
            (T("juntas de goma"),) + V((tbm_x(22) - 6, 0, ZT), 6.5, 0.4, 34), (T("mortero"),) + V((tbm_x(24) - 8, 0, ZT), 7.5, 0.5),
            (T("bombas"),) + V((2.0, 0, ZT - 0.5), 6.5, 0.4), (T("de la broma"),) + V((-4, -1.5, 2.6), 6.5, 0.4, 34), (T("marc brunel") - 0.5,) + V((-3.6, -1.5, 2.5), 6.0, 0.4, 34),
            (T("marc brunel") + 0.8,) + V((2, 0, -4.2), 18, 2.0), (DUR + 2,) + V((3, 0, -4.2), 20, 2.2)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); xf = S["tbm"].location.x
    return {"tbm": Pj((xf - 1.6, 0, ZT + RO + 0.3)), "rueda": Pj((xf, 0, ZT + RO)), "camara": Pj((xf - 0.4, 0, ZT + 0.3)),
            "anillo": Pj((xf - 4.0, 0, ZT + RO)), "gatos": Pj((xf - 3.4, 0, ZT + 0.4)), "bomba": Pj((2.0, 0.3, ZT - RI + 0.6)),
            "rio": Pj((xf + 2, 0, -0.7)), "broma": Pj((-4, -1.5, 3.2))}

if __name__ == "__main__":
    run("tunel", build, pose, anchors)
