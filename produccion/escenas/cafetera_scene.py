# «Así funciona la cafetera italiana»: cafetera de ocho caras cortada por delante, sobre el fuego.
# Se separan sus tres piezas; el vapor del depósito empuja el agua por el tubo del embudo, atraviesa el café
# y sale por la chimenea a la jarra. Al final, la válvula de seguridad suelta vapor.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from cafetera_ov import presion
from mathutils import Vector

T, DUR = cargar("cafetera")
ALU = (0.78, 0.8, 0.84); INN = (0.92, 0.93, 0.95); BLACK = (0.13, 0.13, 0.15); WATER = (0.35, 0.65, 1.0); HOTW = (0.55, 0.8, 1.0)
COFFEE = (0.42, 0.24, 0.12); GROUND = (0.3, 0.2, 0.13); WET = (0.2, 0.12, 0.07); STEAM = (0.97, 0.97, 1.0)
ROT8 = math.pi / 8
RB, HB = 1.6, 2.2           # depósito
RJ, ZJ, HJ = 1.6, 2.7, 2.7  # jarra

def vaso(r, h, loc, color, bottom=True, top=False, v=8, unique=True):
    me = bpy.data.meshes.new("vaso"); bm = bmesh.new()
    a = [bm.verts.new((r * math.cos(ROT8 + 2 * math.pi * k / v), r * math.sin(ROT8 + 2 * math.pi * k / v), 0)) for k in range(v)]
    b = [bm.verts.new((r * math.cos(ROT8 + 2 * math.pi * k / v), r * math.sin(ROT8 + 2 * math.pi * k / v), h)) for k in range(v)]
    for k in range(v): j = (k + 1) % v; bm.faces.new((a[k], a[j], b[j], b[k]))
    if bottom: bm.faces.new(list(reversed(a)))
    if top: bm.faces.new(b)
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("vaso", me); bpy.context.collection.objects.link(o); o.location = loc
    return setup(o, color, unique=unique)

def build():
    sc, cam = scene_setup(world=(0.12, 0.12, 0.14), shadow=0.3)
    S = {"cam": cam}
    box((80, 80, 0.1), (0, 0, -1.25), (0.2, 0.2, 0.23))
    # fogón
    cyl(1.3, 0.25, (0, 0, -1.05), (0.1, 0.1, 0.11)); torus(1.0, 0.12, (0, 0, -0.85), (0.25, 0.25, 0.28))
    for k in range(4):
        a = k * math.pi / 4; box((4.2, 0.18, 0.18), (0, 0, -0.12), (0.08, 0.08, 0.09), rot=(0, 0, a))
    S["llamas"] = [sph(0.16, (0.95 * math.cos(2 * math.pi * k / 14), 0.95 * math.sin(2 * math.pi * k / 14), -0.62), (1, 0.55, 0.15), scale=(1, 1, 2.2), unique=True) for k in range(14)]
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 3)); cutter = bpy.context.object; cutter.scale = (14, 10, 20); cutter.hide_render = True
    S["cutter"] = cutter
    def cortar(o, th=None, inner=INN):
        if th:
            o.data.materials.append(mat(inner, unique=True))
            m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1; m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
        return o
    dyn = [cam, cutter, S["llamas"]]
    # ---- depósito ----
    S["dep"] = dep = empty((0, 0, 0))
    o = cortar(vaso(RB, HB, (0, 0, 0), ALU), 0.12); o.parent = dep; dyn.append(o)
    for k in range(3): o = cortar(torus(RB - 0.02, 0.05, (0, 0, HB - 0.12 - 0.13 * k), (0.62, 0.64, 0.68), unique=True)); o.parent = dep; dyn.append(o)
    S["valv"] = empty((RB + 0.05, 0, 1.9), parent=dep)
    cyl(0.22, 0.3, (0.12, 0, 0), (0.85, 0.75, 0.4), parent=S["valv"], rot=(0, math.pi / 2, 0), v=6)
    S["valvcap"] = cyl(0.13, 0.16, (0.32, 0, 0), (0.75, 0.66, 0.35), parent=S["valv"], rot=(0, math.pi / 2, 0), v=6)
    S["agua"] = cortar(vaso(RB - 0.13, 1.0, (0, 0, 0.12), WATER, top=True)); S["agua"].parent = dep; dyn.append(S["agua"])
    # ---- embudo ----
    S["emb"] = emb = empty((0, 0, 0))
    o = cortar(vaso(1.32, 0.62, (0, 0, 2.0), (0.7, 0.72, 0.76)), 0.07); o.parent = emb; dyn.append(o)
    o = cortar(cyl(0.2, 1.85, (0, 0, 1.08), (0.7, 0.72, 0.76), v=16, unique=True), 0.05); o.parent = emb; dyn.append(o)
    S["cafe"] = cortar(vaso(1.24, 0.5, (0, 0, 2.06), GROUND, top=True)); S["cafe"].parent = emb; dyn.append(S["cafe"])
    S["tubo"] = cortar(cyl(0.15, 1.0, (0, 0, 0), WATER, v=16, unique=True)); S["tubo"].parent = emb; dyn.append(S["tubo"])
    # ---- jarra ----
    S["jar"] = jar = empty((0, 0, 0))
    o = cortar(vaso(RJ, HJ, (0, 0, ZJ), ALU, top=True), 0.12); o.parent = jar; dyn.append(o)
    for k in range(3): o = cortar(torus(RJ - 0.02, 0.05, (0, 0, ZJ + 0.15 + 0.13 * k), (0.62, 0.64, 0.68), unique=True)); o.parent = jar; dyn.append(o)
    S["filtro"] = cortar(cyl(1.25, 0.06, (0, 0, ZJ + 0.04), (0.6, 0.62, 0.66), v=32, unique=True)); S["filtro"].parent = jar; dyn.append(S["filtro"])
    S["goma"] = cortar(torus(1.32, 0.07, (0, 0, ZJ - 0.03), BLACK, unique=True)); S["goma"].parent = jar; dyn.append(S["goma"])
    o = cortar(cyl(0.22, 1.9, (0, 0, ZJ + 1.05), (0.72, 0.74, 0.78), v=16, unique=True), 0.05); o.parent = jar; dyn.append(o)
    S["chim"] = cortar(cyl(0.16, 1.0, (0, 0, 0), COFFEE, v=16, unique=True)); S["chim"].parent = jar; dyn.append(S["chim"])
    S["cafj"] = cortar(vaso(RJ - 0.13, 1.0, (0, 0, ZJ + 0.12), COFFEE, top=True)); S["cafj"].parent = jar; dyn.append(S["cafj"])
    sph(0.28, (0, 0.6, ZJ + HJ + 0.15), BLACK, parent=jar, scale=(1, 1, 0.6))
    asa = box((0.35, 0.4, 2.0), (-RJ - 0.75, 0.3, ZJ + 1.4), BLACK, parent=jar)
    box((0.9, 0.35, 0.3), (-RJ - 0.35, 0.3, ZJ + 2.3), BLACK, parent=jar); box((0.9, 0.35, 0.3), (-RJ - 0.35, 0.3, ZJ + 0.6), BLACK, parent=jar)
    box((0.6, 0.6, 0.25), (RJ + 0.15, 0.4, ZJ + HJ - 0.15), ALU, parent=jar, rot=(0, -0.3, 0))
    # partículas
    S["vapor"] = [sph(0.11, (0, 0, -30), STEAM, seg=10) for _ in range(18)]
    S["gotas"] = [sph(0.065, (0, 0, -30), COFFEE, seg=10) for _ in range(14)]
    S["chorro"] = [sph(0.13, (0, 0, -30), STEAM, seg=10, unique=True) for _ in range(14)]
    dyn += [dep, emb, jar, S["vapor"], S["gotas"], S["chorro"]]
    join_static(dyn)
    return sc, S

def cmix(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))

def estado(t):
    """niveles: depósito (0..1.55), tubo (0/1), chimenea (0/1), jarra (0..1.4), café mojado (0..1)"""
    t_sube, t_fin, t_gor, t_cae = T("así que el agua sube"), T("por fin"), T("ese gorgoteo"), T("y cae en")
    if t < T("tiene tres") + 0.4:   # el principio: ya está subiendo el café
        return 0.7, 1.0, 1.0, 0.25 + 0.06 * t, 1.0
    dep = 1.55 - 1.2 * seg(t, t_sube, t_gor)
    tubo = 1.0 if t_sube < t < t_gor + 0.6 else 0.0
    tubo = seg(t, t_sube, t_sube + 1.0) * (1 - seg(t, t_gor, t_gor + 0.6))
    chim = seg(t, t_fin, t_fin + 1.2) * (1 - seg(t, t_gor + 0.8, t_gor + 1.6))
    jarra = 1.1 * seg(t, T("el café sale") + 0.6, t_gor + 1.2)
    moj = seg(t, T("atraviesa"), T("atraviesa") + 1.2)
    return dep, tubo, chim, jarra, moj

def fuego(t):
    t_tres = T("tiene tres")
    if t < t_tres + 0.3: return 1 - seg(t, t_tres, t_tres + 0.3)
    on = seg(t, T("pones el fuego"), T("pones el fuego") + 0.4) * (1 - seg(t, T("apagar el fuego"), T("apagar el fuego") + 0.4))
    return max(on, win01(t, T("si el café está"), T("ahora un dato"), 0.4, 0.4))

def pose(t, S):
    t_tres, t_fuego = T("tiene tres"), T("pones el fuego")
    ex = seg(t, t_tres, t_tres + 1.0) * (1 - seg(t, t_fuego - 0.2, t_fuego + 0.6))
    S["emb"].location.z = 1.7 * ex; S["jar"].location.z = 3.6 * ex
    dep, tubo, chim, jarra, moj = estado(t)
    S["agua"].scale.z = max(dep, 0.001)
    set_color(S["agua"], cmix(WATER, HOTW, seg(t, T("el agua se calienta"), T("pero el depósito"))))
    S["tubo"].location.z = 0.15 + 1.9 * tubo / 2; S["tubo"].scale.z = max(1.9 * tubo, 0.001)
    set_color(S["tubo"], WATER)
    set_color(S["cafe"], cmix(GROUND, WET, moj))
    S["chim"].location.z = ZJ + 0.1 + 1.9 * chim / 2; S["chim"].scale.z = max(1.9 * chim, 0.001)
    S["cafj"].scale.z = max(jarra, 0.001)
    atasco = win01(t, T("y el filtro se"), T("ahora un dato"), 0.3, 0.6)
    set_color(S["filtro"], cmix((0.6, 0.62, 0.66), (0.9, 0.25, 0.2), atasco))
    f = fuego(t)
    for k, l in enumerate(S["llamas"]):
        fl = 0.8 + 0.35 * math.sin(t * 17 + k * 2.3) + 0.2 * math.sin(t * 29 + k)
        l.scale = (max(f, 0.001), max(f, 0.001), max(2.2 * f * fl, 0.001))
        set_color(l, cmix((1, 0.5, 0.12), (1.0, 0.85, 0.3), 0.5 + 0.5 * math.sin(t * 11 + k)))
    # vapor dentro del depósito: más rápido con más presión
    p = presion(t); vis = p > 0.05 or (t < t_tres)
    top = 0.12 + dep + 0.05
    for k, v in enumerate(S["vapor"]):
        if not vis or t < 0 or ex > 0.05: v.location = (0, 0, -30); continue
        r = random.Random(k); ang = r.uniform(0.5, math.pi - 0.5); rr = r.uniform(0.2, 1.3)
        h = (r.uniform(0, 1) + t * (0.25 + 0.3 * p)) % 1.0
        z = mix(top, HB - 0.15, h) if top < HB - 0.2 else -30
        v.location = (rr * math.cos(ang + 0.3 * math.sin(t * 3 + k)), rr * math.sin(ang) * 0.6 + 0.2, z)
        v.scale = (0.8 + 0.4 * p,) * 3
    # café que sale por la chimenea
    for k, g in enumerate(S["gotas"]):
        if chim < 0.3: g.location = (0, 0, -30); continue
        u = (t * 1.4 + k / len(S["gotas"])) % 1.0; ang = math.pi * (0.15 + 0.7 * random.Random(k).random()) + 0.3
        rr = 0.75 * u; z = ZJ + 2.05 + 0.3 * math.sin(math.pi * min(u * 1.6, 1.0)) - (2.1 - jarra) * max(0, u - 0.6) / 0.4
        g.location = (rr * math.cos(ang), rr * math.sin(ang) * 0.5 + 0.3, max(z, ZJ + 0.15 + jarra))
    # chorro: gorgoteo por la chimenea y vapor por la válvula
    gor = win01(t, T("ese gorgoteo"), T("es la señal") + 0.6, 0.2, 0.4)
    val = win01(t, T("se abre") - 0.1, T("antes de que") + 1.0, 0.1, 0.5)
    S["valvcap"].location.x = 0.32 + 0.35 * val
    for k, c in enumerate(S["chorro"]):
        u = (t * 1.8 + k / len(S["chorro"])) % 1.0; r = random.Random(k)
        if gor > 0.05:
            c.location = (r.uniform(-0.3, 0.3) * u * 2, 0.3, ZJ + 2.1 + 1.6 * u); c.scale = ((0.5 + 1.5 * u) * gor,) * 3
        elif val > 0.05:
            c.location = (RB + 0.6 + 2.6 * u, r.uniform(-0.3, 0.3) * u, 1.9 + 0.6 * u * u + r.uniform(-0.2, 0.2) * u); c.scale = ((0.5 + 2.0 * u) * val,) * 3
        else: c.location = (0, 0, -30)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def orb(tg, d, el, az, lens=35, up=0.09):
    """órbita alrededor de tg; mira un poco por encima (up × d) para que la cafetera quede por debajo de los subtítulos"""
    tg = Vector(tg); el, az = math.radians(el), math.radians(az); d *= 1.1
    pos = tg + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return (tuple(pos), tuple(tg + Vector((0, 0, up * d))), lens)

def CAM():
    return [(0.0,) + orb((0, 0, ZJ + 1.6), 5.5, 14, -18), (2.0,) + orb((0, 0, ZJ + 1.0), 8.5, 12, -12),
            (T("cómo lo hace"),) + orb((0, 0, 2.7), 13.5, 10, -10), (T("tiene tres") + 0.8,) + orb((0, 0, 3.8), 19, 10, -14),
            (T("abajo"),) + orb((0, 0, 1.6), 14, 12, -16), (T("en medio"),) + orb((0, 0, 3.6), 14, 10, -10),
            (T("arriba", 2) ,) + orb((0, 0, 6.6), 14, 6, -6), (T("pones el fuego"),) + orb((0, 0, 2.6), 15, 10, -12),
            (T("el agua se calienta"),) + orb((0, 0, 1.4), 9.5, 12, -16), (T("pero el depósito"),) + orb((0.5, 0, 2.0), 8.5, 10, -24),
            (T("y la presión"),) + orb((0, 0, 1.6), 10.5, 12, -12), (T("ese vapor aprieta"),) + orb((0, 0, 1.3), 9.5, 14, -8),
            (T("y la única"),) + orb((0, 0, 1.6), 10, 10, -14), (T("así que el agua sube"),) + orb((0, 0, 2.3), 10.5, 8, -10),
            (T("un filtro"),) + orb((0, 0, 2.7), 7.5, 10, -16), (T("por fin"),) + orb((0, 0, 4.0), 9.5, 10, -10),
            (T("y cae en"),) + orb((0, 0, 3.6), 10, 8, -6), (T("ese gorgoteo"),) + orb((0, 0, 4.2), 10, 8, -12),
            (T("es la señal"),) + orb((0, 0, 1.0), 12, 10, -14), (T("y esa tuerca"),) + orb((RB, 0, 2.2), 9.0, 12, 26),
            (T("si el café está"),) + orb((0.8, 0, 2.6), 12.5, 10, 12), (T("así que la válvula"),) + orb((RB + 0.6, 0, 2.4), 12.0, 10, 18),
            (T("ahora un dato"),) + orb((0, 0, 2.8), 12.0, 10, -6), (DUR + 2,) + orb((0, 0, 2.8), 13.5, 12, -14)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); ez, ej = S["emb"].location.z, S["jar"].location.z
    dep = estado(t)[0]
    return {"dep": Pj((0, 0, 0.9)), "emb": Pj((0, 0, 2.3 + ez)), "jar": Pj((0, 0, ZJ + 1.6 + ej)), "rosca": Pj((RB, 0, HB - 0.2)),
            "vapor": Pj((0.6, 0, (0.27 + dep + HB) / 2)), "sup": Pj((0, 0, 0.12 + dep)), "supL": Pj((-0.9, 0, 0.12 + dep)),
            "supR": Pj((0.9, 0, 0.12 + dep)), "tubo": Pj((0, 0, 0.8 + ez)), "fondo": Pj((0, 0, 0.15 + ez)), "cafe": Pj((0, 0, 2.35 + ez)),
            "filtro": Pj((0.9, 0, ZJ + 0.06 + ej)), "goma": Pj((-1.3, 0, ZJ - 0.03 + ej)), "chim": Pj((0, 0, ZJ + 2.1 + ej)),
            "valv": Pj((RB + 0.4, 0, 1.9)), "fuego": Pj((0, 0, -0.6))}

if __name__ == "__main__":
    run("cafetera", build, pose, anchors)
