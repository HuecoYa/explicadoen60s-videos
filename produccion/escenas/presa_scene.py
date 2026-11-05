# «¿Y si construyes una presa?»: corte del valle a lo largo del río. El río corre; se desvía por un túnel, se quita el barro
# hasta la roca, el muro sube por capas, flechas de presión que crecen con la profundidad, el muro pasa a triángulo, calor y
# grietas al fraguar y tubos de agua fría, se llena el embalse, filtración y subpresión bajo la presa, cortina de inyecciones y
# drenes, aliviadero con compuertas, tubería forzada hasta la turbina y el generador, y la luz que llega a una casa.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("presa")
SKY = (0.62, 0.8, 0.95); WATER = (0.22, 0.52, 0.9); FOAM = (0.85, 0.95, 1.0); MUD = (0.5, 0.38, 0.26); MUD2 = (0.42, 0.31, 0.21)
ROCK = (0.5, 0.5, 0.55); ROCK2 = (0.43, 0.43, 0.48); CONC = (0.8, 0.8, 0.8); CONC2 = (0.72, 0.72, 0.74); HOTC = (0.98, 0.55, 0.3)
COLD = (0.3, 0.7, 1.0); GRASS = (0.42, 0.66, 0.35); GROUT = (0.62, 0.62, 0.6); STEEL = (0.55, 0.57, 0.62); YEL = (1.0, 0.85, 0.2)
LEJOS = (0, 0, -80)
ZR = -1.5                       # techo de la roca
YD = 4.0                        # ancho de presa visible (de y=0 a y=YD)
HEEL, TOE, CW, HC = -3.0, 5.5, 1.0, 10.0   # pie aguas arriba, pie aguas abajo, ancho de coronación, altura
NL = 12

def prism(pts, y0, y1, color, unique=True):
    """polígono en XZ extruido en Y"""
    me = bpy.data.meshes.new("pr"); bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts]; b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((a[j], a[i], b[i], b[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("pr", me); bpy.context.collection.objects.link(o)
    return setup(o, color, unique=unique)

def along(pts, s):
    L = [(Vector(b) - Vector(a)).length for a, b in zip(pts, pts[1:])]; tot = sum(L); d = max(0.0, min(1.0, s)) * tot
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l: return Vector(a).lerp(Vector(b), d / max(l, 1e-6))
        d -= l
    return Vector(pts[-1])

def x_cara(z):
    """x de la cara aguas abajo a la altura z"""
    u = (z - ZR) / (HC - ZR); return mix(TOE, HEEL + CW, u)

PENSTOCK = [(HEEL - 0.3, -0.05, 4.2), (HEEL + 0.6, -0.05, 4.2), (4.8, -0.05, -0.6), (6.3, -0.05, -0.6)]
SALIDA = [(7.0, -0.05, -0.8), (9.5, -0.05, -0.3), (14, -0.05, -0.3)]
FILTRA = [(-6.0, -0.05, ZR), (-4.0, -0.05, -3.2), (0.0, -0.05, -3.6), (4.0, -0.05, -2.8), (6.2, -0.05, ZR)]
ALIVIA = [(HEEL + 0.1, -0.1, 10.25), (HEEL + CW, -0.1, 10.2)] + [(x_cara(z) + 0.1, -0.1, z + 0.2) for z in (8, 5, 2, ZR + 0.3)] + [(9, -0.1, -0.2)]

def build():
    sc, cam = scene_setup(world=SKY, shadow=0.3)
    S = {"cam": cam}
    # valle: roca y barro en corte (frente en y=0), laderas al fondo
    box((80, 30, 20), (0, 15, ZR - 10), ROCK)
    for k in range(40):
        rr = random.Random(k); x, z = rr.uniform(-30, 30), rr.uniform(-9, -2)
        box((rr.uniform(0.6, 1.4), 0.04, 0.05), (x, -0.02, z), ROCK2, rot=(0, rr.uniform(-0.6, 0.6), 0))
    S["barro_obra"] = box((14, 30, 1.5), (0.5, 15, ZR + 0.75), MUD, unique=True)
    box((40, 30, 1.5), (-27.5, 15, ZR + 0.75), MUD); box((40, 30, 1.5), (27.5, 15, ZR + 0.75), MUD)
    S["piedras"] = []
    for k in range(30):
        rr = random.Random(100 + k); x = rr.uniform(-14, 14)
        o = sph(rr.uniform(0.12, 0.3), (x, -0.03, rr.uniform(ZR + 0.2, -0.2)), (0.62, 0.6, 0.6), scale=(1.3, 0.4, 1), unique=True)
        S["piedras"].append(o)
    for sx in (-1, 1):
        prism([(-40, 0), (40, 0), (40, 18), (-40, 18)], 9, 30, (0.48, 0.58, 0.4), unique=False)
    prism([(-40, 0), (40, 0), (40, 6), (-40, 9)], 6, 9, (0.5, 0.62, 0.42), unique=False)
    # túnel de desvío al pie de la ladera
    S["tunel"] = cyl(0.7, 22, (0, 6.2, 0.4), (0.2, 0.2, 0.22), rot=(0, math.pi / 2, 0), unique=True)
    S["boca"] = [cyl(0.85, 0.3, (sx * 11, 6.0, 0.4), (0.35, 0.35, 0.38), rot=(0, math.pi / 2, 0), unique=True) for sx in (-1, 1)]
    S["tapon"] = cyl(0.72, 0.4, (-11.2, 6.0, 0.4), CONC2, rot=(0, math.pi / 2, 0), unique=True)
    # agua: río (tramos), embalse y aguas abajo
    S["rio"] = box((60, 5.5, 1), (0, 2.75, 0), WATER, unique=True)
    S["embalse"] = box((40, YD + 1.5, 1), (HEEL - 20, (YD + 1.5) / 2, 0), WATER, unique=True)
    S["abajo"] = box((30, 5.5, 0.5), (TOE + 15, 2.75, -0.2), WATER, unique=True)
    S["espuma"] = [sph(0.12, LEJOS, FOAM, seg=8, scale=(1.8, 1, 0.4)) for _ in range(40)]
    # muro recto (primera idea) y presa triangular, por capas
    S["recto"] = []; S["tri"] = []
    dz = (HC - ZR) / NL
    for i in range(NL):
        z0, z1 = ZR + i * dz, ZR + (i + 1) * dz
        S["recto"].append(prism([(HEEL, z0), (HEEL + 1.2, z0), (HEEL + 1.2, z1), (HEEL, z1)], 0, YD, CONC if i % 2 else CONC2))
        S["tri"].append(prism([(HEEL, z0), (x_cara(z0), z0), (x_cara(z1), z1), (HEEL, z1)], 0, YD, CONC if i % 2 else CONC2))
    S["grietas"] = []
    for k in range(6):
        rr = random.Random(50 + k); z = rr.uniform(0.5, 7); x = rr.uniform(HEEL + 0.6, x_cara(z) - 0.6)
        S["grietas"].append(box((0.06, 0.03, 0.9), (x, -0.02, z), (0.12, 0.12, 0.14), rot=(0, rr.uniform(-0.5, 0.5), 0), unique=True))
    S["frio"] = []
    for i in range(NL - 1):
        z = ZR + (i + 0.5) * dz; x0, x1 = HEEL + 0.3, x_cara(z) - 0.3
        if x1 - x0 < 0.3: continue
        o = bar_obj(COLD, 0.07, unique=True); bar_set(o, (x0, -0.04, z), (x1, -0.04, z)); S["frio"].append(o)
    # cortina de inyecciones, drenes y galería
    S["cortina"] = box((0.6, 0.04, 5.0), (HEEL + 0.5, -0.03, ZR - 2.5), (0.88, 0.8, 0.6), unique=True)
    S["perfo"] = bar_obj((0.3, 0.3, 0.32), 0.05, unique=True)
    S["drenes"] = [box((0.1, 0.04, 2.6), (HEEL + 1.4 + 0.5 * k, -0.035, ZR - 1.2), (0.12, 0.12, 0.14), unique=True) for k in range(3)]
    S["galeria"] = box((0.5, 0.05, 0.45), (HEEL + 1.9, -0.03, ZR + 0.45), (0.15, 0.15, 0.17), unique=True)
    # compuertas del aliviadero
    S["compuerta"] = box((0.15, YD, 0.9), (HEEL + 0.5, YD / 2, HC + 0.45), STEEL, unique=True)
    S["pilas"] = [box((0.1, YD, 1.6), (x, YD / 2, HC + 0.8), CONC2, unique=True) for x in (HEEL + 0.05, HEEL + 0.95)]
    S["pilas"].append(box((CW + 0.2, YD, 0.15), (HEEL + 0.5, YD / 2, HC + 1.65), CONC2, unique=True))
    # tubería forzada, central, turbina, generador, torre y casa
    S["tuberia"] = []
    for a, b in zip(PENSTOCK, PENSTOCK[1:]):
        o = bar_obj((0.35, 0.37, 0.42), 0.28, unique=True); bar_set(o, a, b); S["tuberia"].append(o)
    S["central"] = box((2.6, YD, 2.6), (7.2, YD / 2, -0.2), (0.85, 0.82, 0.75), unique=True)
    S["sala"] = box((2.2, 0.06, 2.2), (7.2, -0.02, -0.2), (0.25, 0.27, 0.3), unique=True)
    S["turbina"] = empty((6.6, -0.12, -0.6))
    cyl(0.18, 0.1, (0, 0, 0), STEEL, parent=S["turbina"], rot=(math.pi / 2, 0, 0))
    for k in range(6): box((0.62, 0.06, 0.14), (0.32 * math.cos(k * math.tau / 6), 0, 0.32 * math.sin(k * math.tau / 6)), YEL,
                           parent=S["turbina"], rot=(0, -k * math.tau / 6, 0))
    S["eje"] = bar_obj(STEEL, 0.06, unique=True); bar_set(S["eje"], (6.6, -0.12, -0.6), (6.6, -0.12, 0.3))
    S["gen"] = cyl(0.42, 0.55, (6.6, -0.12, 0.55), (0.3, 0.5, 0.85), unique=True)
    S["gen_luz"] = [box((0.06, 0.02, 0.4), (6.6 + 0.43 * math.cos(a), -0.12 - 0.43 * math.sin(a) * 0, 0.55), YEL, unique=True) for a in (0, math.pi)]
    S["torre"] = empty((10.5, 1.0, 0))
    for sx in (-1, 1):
        o = bar_obj((0.5, 0.5, 0.55), 0.06); o.parent = S["torre"]; bar_set(o, (sx * 0.6, 0, 0), (0, 0, 5))
    o = bar_obj((0.5, 0.5, 0.55), 0.06); o.parent = S["torre"]; bar_set(o, (-0.9, 0, 4.2), (0.9, 0, 4.2))
    S["cable"] = [bar_obj((0.2, 0.2, 0.22), 0.04, unique=True) for _ in range(2)]
    bar_set(S["cable"][0], (8.5, 1.0, 1.2), (10.5, 1.0, 4.2)); bar_set(S["cable"][1], (10.5, 1.0, 4.2), (14.5, 1.0, 2.2))
    S["casa"] = empty((15.5, 1.5, 0))
    box((2.0, 1.6, 1.4), (0, 0, 0.7), (0.95, 0.9, 0.8), parent=S["casa"]); prism([(-1.2, 1.4), (1.2, 1.4), (0, 2.3)], -0.8, 0.8, (0.75, 0.35, 0.3), unique=False).parent = S["casa"]
    S["ventana"] = box((0.5, 0.05, 0.45), (-0.4, -0.81, 0.8), (0.3, 0.32, 0.38), parent=S["casa"], unique=True)
    # partículas y flechas
    S["p_filtra"] = [sph(0.1, LEJOS, (0.35, 0.65, 1.0), seg=8) for _ in range(16)]
    S["p_tubo"] = [sph(0.13, LEJOS, FOAM, seg=8) for _ in range(18)]
    S["p_alivia"] = [sph(0.14, LEJOS, FOAM, seg=8) for _ in range(26)]
    S["p_luz"] = [sph(0.09, LEJOS, YEL, seg=8) for _ in range(10)]
    S["lluvia"] = [bar_obj((0.85, 0.92, 1.0), 0.035) for _ in range(50)]
    S["flechas"] = []
    for k in range(6):
        bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0, depth=1, location=LEJOS); f = bpy.context.object; setup(f, (0.95, 0.3, 0.25))
        S["flechas"].append(f)
    S["sub"] = []
    for k in range(5):
        bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0, depth=0.9, location=LEJOS); f = bpy.context.object; setup(f, (0.3, 0.55, 1.0))
        S["sub"].append(f)
    dyn = [cam, S["barro_obra"], S["piedras"], S["tunel"], S["boca"], S["tapon"], S["rio"], S["embalse"], S["abajo"], S["espuma"], S["recto"],
           S["tri"], S["pilas"], S["grietas"], S["frio"], S["cortina"], S["perfo"], S["drenes"], S["galeria"], S["compuerta"], S["tuberia"], S["central"],
           S["sala"], S["turbina"], S["eje"], S["gen"], S["gen_luz"], S["torre"], S["cable"], S["casa"], S["p_filtra"], S["p_tubo"],
           S["p_alivia"], S["p_luz"], S["lluvia"], S["flechas"], S["sub"]]
    join_static(dyn)
    return sc, S

def nivel(t):
    return keyed(t, [(0, 0.0), (T("ahora cierras"), 0.0), (T("se llena", fin=True) + 0.5, 8.6), (T("pero si llueve"), 8.6),
                     (T("pasar por encima"), 10.4), (T("así que pones"), 10.4), (T("que sobra", fin=True), 9.3), (DUR + 2, 9.3)])

def pose(t, S):
    t_desv, t_seco, t_barro, t_exc, t_apoy, t_sube = T("desvías"), T("para trabajar"), T("pero el fondo"), T("así que excavas"), T("ahí apoyas"), T("subes hormigón")
    t_emp, t_cada, t_cien, t_tri, t_calor = T("pero el agua empuja"), T("cada diez"), T("a cien"), T("así que haces"), T("pero el hormigón")
    t_agr, t_frio, t_cierra, t_cuela, t_iny = T("se agrieta"), T("así que lo enfrías"), T("ahora cierras"), T("se cuela"), T("así que inyectas")
    t_dren, t_llueve, t_comp, t_prem, t_tub, t_gen, t_luz = T("y abres pozos"), T("pero si llueve"), T("compuertas"), T("y por último"), T("parte del agua"), T("mueve los"), T("y la luz")
    # río: corre hasta el desvío; luego el tramo de obra queda seco
    seco = seg(t, t_desv + 0.4, t_seco + 0.4)
    S["rio"].scale = (60, 5.5, max(0.01, 0.8 * (1 - seco))); S["rio"].location = (0, 2.75, 0.4 * (1 - seco))
    S["rio"].hide_render = seco > 0.98
    for k, f in enumerate(S["espuma"]):
        rr = random.Random(k); x = -14 + ((t * 3.2 + rr.uniform(0, 28)) % 28); z = 0.82 if t < t_desv + 0.5 else 0.82 * (1 - seco)
        if seco < 0.95: f.location = (x, rr.uniform(-0.15, 0.0) if k % 2 else rr.uniform(0.5, 4), z)
        elif t < t_cierra + 1.0:
            # el agua entra por el túnel
            u = (t * 0.25 + rr.uniform(0, 1)) % 1.0; f.location = (-11 + 22 * u, 6.2, 0.4 + 0.3 * math.sin(k)) if k % 2 == 0 else (x - 14 if x < -12 else -50, 3, 0.1)
        else: f.location = LEJOS
    S["tunel"].hide_render = t < t_desv - 0.3 or t > t_cierra + 1.5
    for b in S["boca"]: b.hide_render = t < t_desv - 0.3
    S["tapon"].hide_render = t < t_cierra
    # barro y piedras sueltas: se excava el tramo de obra hasta la roca
    ex = seg(t, t_exc + 0.2, T("roca dura", fin=True) + 0.4)
    S["barro_obra"].scale = (14, 30, max(0.01, 1.5 * (1 - ex))); S["barro_obra"].location = (0.5, 15, ZR + 0.75 * (1 - ex))
    S["barro_obra"].hide_render = ex > 0.98
    for k, p in enumerate(S["piedras"]):
        bump = 0.12 * math.sin(t * 8 + k) * win01(t, t_barro, t_exc)
        x0 = random.Random(100 + k).uniform(-14, 14)
        p.hide_render = ex > 0.5 and -6.5 < x0 < 7.5
        p.location.z = random.Random(100 + k).uniform(ZR + 0.2, -0.2) + bump if not p.hide_render else p.location.z
    # muro: recto por capas, luego triangular
    dz = (HC - ZR) / NL
    nrec = NL * seg(t, t_apoy, T("capa a capa", fin=True) + 0.5)
    ntri = NL * seg(t, t_tri + 0.3, T("gordísimo", fin=True))
    for i, (r, tr) in enumerate(zip(S["recto"], S["tri"])):
        r.hide_render = not (i < nrec and t < t_tri + 0.3 + 0.12 * i)
        tr.hide_render = not (i < ntri)
        calor = win01(t, t_calor + 0.2, t_frio + 1.2 + 0.1 * i, 0.6, 0.6)
        base = CONC if i % 2 else CONC2
        set_color(tr, tuple(mix(a, b, calor * (0.7 + 0.3 * math.sin(t * 4 + i))) for a, b in zip(base, HOTC)))
    for g in S["grietas"]: g.hide_render = not (t_agr - 0.2 < t < t_frio + 1.0)
    fr = seg(t, t_frio + 0.4, T("agua fría", fin=True))
    for k, o in enumerate(S["frio"]): o.hide_render = not (fr > k / max(1, len(S["frio"])) and t < t_cierra + 1.0)
    # agua: embalse y aguas abajo
    lv = nivel(t)
    emb_on = t > t_cierra - 0.1 or t < t_desv + 0.5
    if t < t_desv + 0.5: lv_e = 0.8 * (1 - seco)
    else: lv_e = lv
    S["embalse"].hide_render = lv_e < 0.05 or not emb_on
    S["embalse"].scale = (40, YD + 1.5, max(0.01, lv_e - ZR + 0.0)); S["embalse"].location = (HEEL - 20, (YD + 1.5) / 2, (lv_e + ZR) / 2)
    if t < t_desv + 0.5: S["embalse"].hide_render = True
    S["abajo"].hide_render = t < t_cierra
    # presión: flechas contra el muro que crecen con la profundidad
    pres = win01(t, t_emp, t_tri + 1.0) + win01(t, t_cierra + 1.5, t_cuela)
    agua_p = 9.0 if t < t_tri + 1.5 else lv
    for k, f in enumerate(S["flechas"]):
        z = agua_p - 0.8 - k * 1.6
        if pres > 0.05 and z > ZR + 0.2:
            depth = agua_p - z; L = 0.4 + 0.22 * depth
            f.location = (HEEL - 0.15 - L / 2 + 0.06 * math.sin(t * 6 + k), -0.4, z); f.rotation_euler = (0, math.pi / 2, 0)
            f.scale = (pres * (0.6 + 0.08 * depth), pres * (0.6 + 0.08 * depth), pres * L)
        else: f.location = LEJOS
    # filtración bajo la presa y subpresión; cortina y drenes la reducen
    fil = win01(t, t_cuela - 0.2, t_llueve)
    corte = seg(t, t_iny + 0.5, T("una cortina", fin=True))
    for k, p in enumerate(S["p_filtra"]):
        if fil > 0.05:
            s = (k / 16 + t * 0.15) % 1.0
            if corte > 0.5 and s > 0.32: s = 0.32 - 0.03 * (k % 3)
            p.location = along(FILTRA, s); p.scale = (fil,) * 3
        else: p.location = LEJOS
    sub = win01(t, T("y empuja la presa") - 0.3, t_llueve) * (1 - 0.65 * seg(t, t_dren + 0.5, t_dren + 1.5))
    for k, f in enumerate(S["sub"]):
        if sub > 0.05:
            x = HEEL + 1.0 + 1.4 * k; f.location = (x, -0.3, ZR - 0.6 + 0.12 * math.sin(t * 7 + k)); f.scale = (sub,) * 3
        else: f.location = LEJOS
    S["cortina"].hide_render = corte < 0.02
    S["cortina"].scale.z = max(0.01, corte); S["cortina"].location.z = ZR - 2.5 * corte
    perf = t_iny < t < T("una cortina", fin=True) + 0.3
    if perf: bar_set(S["perfo"], (HEEL + 0.5, -0.06, ZR + 0.4), (HEEL + 0.5, -0.06, ZR - 5.0 * corte - 0.1))
    else: bar_set(S["perfo"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    dr = seg(t, t_dren, t_dren + 1.0)
    for d in S["drenes"]: d.hide_render = dr < 0.5
    S["galeria"].hide_render = dr < 0.5
    # lluvia, desbordamiento y compuertas
    for k, r in enumerate(S["lluvia"]):
        if t_llueve - 0.2 < t < t_comp + 0.5:
            rr = random.Random(k); x = rr.uniform(-14, 6); y = rr.uniform(-2, 3); z = 15 - ((t * 10 + rr.uniform(0, 6)) % 6)
            bar_set(r, (x, y, z), (x, y, z + 0.6))
        else: bar_set(r, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    for o in S["pilas"] + [S["compuerta"]]: o.hide_render = t < T("gordísimo", fin=True)
    ab = seg(t, t_comp - 0.3, t_comp + 0.6)
    S["compuerta"].location.z = HC + 0.45 + 1.1 * ab
    sale = ab * (1 - seg(t, t_prem - 0.4, t_prem + 0.4))
    for k, p in enumerate(S["p_alivia"]):
        if sale > 0.05: p.location = along(ALIVIA, (k / 26 + t * 0.35) % 1.0); p.scale = (sale,) * 3
        else: p.location = LEJOS
    # tubería, turbina, generador y luz
    tub = seg(t, t_tub, t_tub + 1.0)
    for o in S["tuberia"]: o.hide_render = t < t_tub - 0.3
    for o in (S["central"], S["sala"], S["eje"], S["gen"], S["torre"]): o.hide_render = t < t_tub - 0.3
    S["turbina"].location = (6.6, -0.12, -0.6) if t > t_tub - 0.3 else LEJOS
    for k, p in enumerate(S["p_tubo"]):
        if tub > 0.05:
            path = PENSTOCK + SALIDA; p.location = along(path, (k / 18 + t * 0.4) % 1.0); p.scale = (tub,) * 3
        else: p.location = LEJOS
    giro = max(0.0, t - T("hasta las turbinas")) * 7.0 * seg(t, T("hasta las turbinas"), T("hasta las turbinas") + 1.5)
    S["turbina"].rotation_euler = (0, giro, 0)
    gen_on = t > t_gen
    for o in S["gen_luz"]: o.hide_render = not gen_on
    set_color(S["gen"], (0.95, 0.85, 0.3) if gen_on and math.sin(t * 10) > 0 else (0.3, 0.5, 0.85))
    for c in S["cable"]: set_color(c, YEL if t > t_luz - 0.3 else (0.2, 0.2, 0.22))
    for k, p in enumerate(S["p_luz"]):
        if t > t_luz - 0.3:
            path = [(7.5, 1.0, 0.8), (8.5, 1.0, 1.2), (10.5, 1.0, 4.2), (14.5, 1.0, 2.2)]
            p.location = along(path, (k / 10 + t * 0.5) % 1.0)
        else: p.location = LEJOS
    set_color(S["ventana"], (1.0, 0.9, 0.45) if t > T("encendida") else (0.3, 0.32, 0.38))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.04))

def V(at, off, lens=30): at = Vector(at); return (tuple(at + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v, hold=0.0):
        k.append((t,) + v)
        if hold: k.append((t + hold,) + v)
    add(0.0, V((-1.0, 1.5, 0.8), (-1.2, -2.6, 0.7), 30))
    add(2.4, V((-1.0, 1.5, 1.0), (-2.0, -6.0, 2.0), 28))
    add(T("desvías") + 0.5, V((0.0, 3.0, 0.8), (-3.0, -12.0, 5.0), 24), 1.5)
    add(T("pero el fondo") + 0.3, V((0.0, 0.0, -0.8), (-1.5, -6.5, 1.5), 28), 1.2)
    add(T("ahí apoyas"), V((-2.0, 0.0, 1.5), (-2.5, -9.0, 2.0), 28))
    add(T("pero el agua empuja"), V((-2.5, 0.0, 4.0), (-3.5, -13.0, 2.0), 28))
    add(T("a cien") + 0.5, V((-3.0, 0.0, 3.0), (-3.0, -12.5, 1.8), 28), 2.0)
    add(T("así que haces") + 0.5, V((1.0, 0.0, 4.2), (-3.0, -16.0, 2.5), 28), 2.0)
    add(T("pero el hormigón") + 0.5, V((1.0, 0.0, 3.8), (-2.0, -14.0, 2.0), 28))
    add(T("así que lo enfrías") + 1.0, V((0.5, 0.0, 3.5), (-1.5, -13.5, 1.5), 28))
    add(T("ahora cierras") + 0.5, V((-3.0, 0.0, 4.0), (-4.0, -17.0, 3.5), 26), 1.0)
    add(T("se cuela") + 0.5, V((0.5, 0.0, -1.8), (-2.0, -12.0, 2.0), 28), 1.5)
    add(T("así que inyectas") + 0.5, V((-1.5, 0.0, -2.2), (-1.5, -9.0, 1.5), 28), 2.0)
    add(T("y abres pozos") + 1.0, V((-0.5, 0.0, -1.5), (-2.0, -10.0, 1.5), 28))
    add(T("pero si llueve") + 0.5, V((-2.0, 0.0, 6.0), (-3.5, -16.0, 3.0), 26))
    add(T("compuertas") + 0.5, V((0.5, 0.0, 5.0), (-3.0, -17.0, 3.0), 26), 1.5)
    add(T("parte del agua") + 0.5, V((4.0, 0.0, 1.5), (-3.0, -13.0, 2.0), 27))
    add(T("mueve los") , V((6.6, 0.0, 0.0), (-1.5, -6.5, 1.0), 28), 1.5)
    add(T("y la luz") + 0.8, V((10.0, 0.0, 1.8), (-2.5, -12.0, 1.5), 27))
    add(T("sígueme"), V((5.0, 0.0, 3.5), (-4.0, -20.0, 3.5), 26))
    add(DUR + 2, V((5.0, 0.0, 3.8), (-4.5, -22.0, 4.0), 26))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"tunel": Pj((-11, 6.0, 1.3)), "barro": Pj((0, 0, ZR + 0.75)), "roca": Pj((0, 0, ZR - 1.2)), "muro": Pj((HEEL + 0.6, 0, 6)),
            "fondo": Pj((HEEL - 0.5, 0, ZR + 0.6)), "presa": Pj((0.5, 0, 4.0)), "frio": Pj((0.5, 0, 2.0)), "cortina": Pj((HEEL + 0.5, 0, ZR - 3.5)),
            "dren": Pj((HEEL + 1.9, 0, ZR - 2.0)), "compuerta": Pj((HEEL + 0.5, 0, HC + 1.8)), "turbina": Pj((6.6, 0, -0.6)),
            "gen": Pj((6.6, 0, 1.0)), "casa": Pj((15.5, 1.5, 2.5)), "sup": Pj((HEEL - 1.5, 0, 9.0)), "base": Pj((HEEL - 1.5, 0, ZR + 0.5))}

if __name__ == "__main__":
    run("presa", build, pose, anchors)
