# «¿Y si construyes una piscina?»: jardín en corte. La excavadora cava el agujero, las paredes se desmoronan, malla de acero y
# hormigón proyectado, se llena (contador de litros), el agua se pone verde, circuito sumidero/skimmer → bomba → filtro de
# arena → boquillas, cloro contra las bacterias, y el dato: el agua del subsuelo sube, la piscina vacía flota y la válvula
# del fondo la deja entrar.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("piscina")
GRASS = (0.42, 0.68, 0.33); SOIL = (0.55, 0.4, 0.27); SOIL2 = (0.47, 0.34, 0.23); CONC = (0.8, 0.8, 0.82); CONCIN = (0.68, 0.68, 0.7)
TILE = (0.55, 0.8, 0.92); WATER = (0.25, 0.6, 0.95); GREENW = (0.35, 0.62, 0.28); STEEL = (0.45, 0.47, 0.5); YEL = (0.98, 0.75, 0.15)
PIPE = (0.92, 0.92, 0.94); DIRTY = (0.55, 0.45, 0.25); CLEAN = (0.75, 0.95, 1.0); BACT = (0.3, 0.85, 0.3); GW = (0.35, 0.65, 1.0)
LEJOS = (0, 0, -60)
X0, X1, D, YB, TH = -4.0, 4.0, 1.5, 2.0, 0.25            # interior de la piscina, profundidad, pared del fondo, espesor
NSEG = 12

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def unir(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); return objs[0]

def along(pts, s):
    L = [(Vector(b) - Vector(a)).length for a, b in zip(pts, pts[1:])]; tot = sum(L); d = max(0.0, min(1.0, s)) * tot
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l: return Vector(a).lerp(Vector(b), d / max(l, 1e-6))
        d -= l
    return Vector(pts[-1])

def tubos(pts, color, r):
    for a, b in zip(pts, pts[1:]):
        o = bar_obj(color, r); bar_set(o, a, b)
    for p in pts[1:-1]: sph(r, p, color)

YP = 0.02          # tuberías en el plano de corte (medio asomadas)
FX, FZ = 6.9, 0.0  # filtro
PX = 5.7           # bomba
SUMI = [(0.0, -0.02, -D), (0.0, YP, -D - 0.45), (5.7, YP, -D - 0.45), (5.7, YP, 0.25)]
SKIM = [(X1 - 0.05, -0.02, -0.15), (X1 + 0.6, YP, -0.15), (5.4, YP, -0.15), (5.7, YP, 0.25)]
BOMBA_FILTRO = [(5.7, YP, 0.25), (6.5, YP, 0.25), (6.5, YP, 1.25), (FX, YP, 1.25)]
RETORNO = [(FX, YP, 0.08), (FX, YP, -0.7), (FX, YP, -D - 0.7), (X0 - 0.55, YP, -D - 0.7), (X0 - 0.55, YP, -0.45), (X0 + 0.05, -0.02, -0.45)]
VALV = (-2.0, 0.0)

def build():
    sc, cam = scene_setup(world=(0.6, 0.78, 0.95), shadow=0.3)
    S = {"cam": cam}
    # terreno en corte con el hueco que crece
    hueco = box((1, 1, 1), (0, 0, 0), None); hueco.hide_render = hueco.hide_viewport = True; S["hueco"] = hueco
    S["suelo"] = box((40, 20, 30), (0, 10, -15), SOIL, unique=True)
    m = S["suelo"].modifiers.new("h", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = hueco; m.solver = "EXACT"
    S["cesped"] = box((30, 20, 0.08), (0, 10, 0.04), GRASS, unique=True)
    m = S["cesped"].modifiers.new("h", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = hueco; m.solver = "EXACT"
    box((40, 0.02, 26), (0, -0.01, -17), SOIL2)
    rng = random.Random(4)
    for k in range(40):
        x, z = rng.uniform(-14, 14), rng.uniform(-5.6, -0.4)
        if X0 - 0.8 < x < X1 + 3.3 and z > -D - 1.0: continue
        sph(rng.uniform(0.06, 0.16), (x, -0.02, z), (0.42, 0.32, 0.22), scale=(1.4, 0.3, 1))
    # valla y árbol de fondo, casa
    for k in range(16): box((0.08, 0.08, 1.0), (-12 + 1.6 * k, 9.5, 0.5), (0.85, 0.75, 0.6))
    box((26, 0.05, 0.1), (0, 9.5, 0.85), (0.85, 0.75, 0.6))
    box((6, 4, 3), (-9, 13, 1.5), (0.95, 0.9, 0.82)); box((6.4, 4.4, 0.3), (-9, 13, 3.1), (0.75, 0.35, 0.3))
    cyl(0.15, 2, (9, 7, 1), (0.5, 0.35, 0.2)); sph(1.2, (9, 7, 2.6), (0.3, 0.6, 0.3))
    # trozos que se desmoronan y tierra que vuela
    S["trozos"] = [box((0.35, 0.3, 0.3), LEJOS, SOIL2) for _ in range(14)]
    S["tierra"] = [sph(0.14, LEJOS, SOIL2, seg=8) for _ in range(10)]
    # excavadora
    S["exc"] = empty((-7.0, 1.0, 0)); e = S["exc"]
    box((2.4, 1.4, 0.5), (0, 0, 0.3), (0.2, 0.2, 0.22), parent=e)
    box((2.0, 1.3, 1.0), (-0.1, 0, 1.0), YEL, parent=e); box((0.8, 1.0, 0.8), (0.55, 0, 1.85), YEL, parent=e)
    box((0.7, 1.02, 0.55), (0.6, 0, 1.9), (0.5, 0.75, 0.95), parent=e)
    S["brazo1"] = bar_obj(YEL, 0.17); S["brazo2"] = bar_obj(YEL, 0.13)
    S["cazo"] = empty(LEJOS)
    box((0.6, 0.8, 0.12), (0, 0, -0.25), (0.35, 0.35, 0.38), parent=S["cazo"]); box((0.12, 0.8, 0.5), (-0.27, 0, 0), (0.35, 0.35, 0.38), parent=S["cazo"])
    for k in range(4): box((0.12, 0.08, 0.15), (0.32, -0.3 + 0.2 * k, -0.27), (0.6, 0.6, 0.62), parent=S["cazo"])
    S["cazo_tierra"] = sph(0.28, (0.0, 0, -0.08), SOIL2, parent=S["cazo"], scale=(1, 1.3, 0.6), unique=True)
    # malla de acero
    barras = []
    for k in range(17):
        x = X0 + 0.5 * k
        o = bar_obj(STEEL, 0.025); bar_set(o, (x, 0, -D - 0.12), (x, YB + 0.12, -D - 0.12)); barras.append(o)
        o = bar_obj(STEEL, 0.025); bar_set(o, (x, YB + 0.12, -D - 0.12), (x, YB + 0.12, 0)); barras.append(o)
    for k in range(5):
        y = 0.5 * k
        o = bar_obj(STEEL, 0.025); bar_set(o, (X0 - 0.12, y, -D - 0.12), (X1 + 0.12, y, -D - 0.12)); barras.append(o)
    for k in range(4):
        z = -D + 0.4 * k
        o = bar_obj(STEEL, 0.025); bar_set(o, (X0 - 0.12, YB + 0.12, z), (X1 + 0.12, YB + 0.12, z)); barras.append(o)
        for sx in (X0 - 0.12, X1 + 0.12):
            o = bar_obj(STEEL, 0.025); bar_set(o, (sx, 0, z), (sx, YB + 0.12, z)); barras.append(o)
    S["malla"] = unir(barras)
    # vaso de hormigón por tramos (suelo + pared del fondo) y paredes de los extremos
    S["vaso"] = empty((0, 0, 0)); S["tramos"] = []
    dx = (X1 - X0 + 2 * TH) / NSEG
    for i in range(NSEG):
        x = X0 - TH + dx * (i + 0.5)
        a = box((dx + 0.002, YB + TH, TH), (x, (YB + TH) / 2, -D - TH / 2), CONC, parent=S["vaso"], unique=True)
        b = box((dx + 0.002, TH, D + TH), (x, YB + TH / 2, -(D + TH) / 2), CONC, parent=S["vaso"], unique=True)
        c = box((dx + 0.002, YB, 0.02), (x, YB / 2, -D + 0.01), TILE, parent=S["vaso"], unique=True)
        d = box((dx + 0.002, 0.02, D), (x, YB - 0.01, -D / 2), TILE, parent=S["vaso"], unique=True)
        S["tramos"].append((a, b, c, d))
    S["extremos"] = [box((TH, YB + TH, D + TH), (sx * (X1 + TH / 2), (YB + TH) / 2, -(D + TH) / 2), CONC, parent=S["vaso"], unique=True)
                     for sx in (-1, 1)]
    S["cara"] = [box((0.02, YB, D), (sx * (X1 - 0.01), YB / 2, -D / 2), TILE, parent=S["vaso"], unique=True) for sx in (-1, 1)]
    S["borde"] = box((X1 - X0 + 2 * TH + 0.3, TH + 0.3, 0.08), (0, YB + TH / 2, 0.04), (0.9, 0.88, 0.82), parent=S["vaso"], unique=True)
    # accesorios: sumidero, skimmer, boquillas, válvula
    S["sumidero"] = cyl(0.18, 0.06, (0, 0.0, -D + 0.03), (0.3, 0.3, 0.32), parent=S["vaso"], unique=True)
    S["skimmer"] = box((0.1, 0.4, 0.2), (X1 - 0.03, 0.0, -0.15), (0.3, 0.3, 0.32), parent=S["vaso"], unique=True)
    S["boquilla"] = cyl(0.07, 0.12, (X0 + 0.05, 0.0, -0.45), (0.95, 0.95, 0.95), parent=S["vaso"], rot=(0, math.pi / 2, 0), unique=True)
    S["valvula"] = cyl(0.16, 0.06, (VALV[0], VALV[1], -D + 0.03), (0.95, 0.5, 0.2), parent=S["vaso"], unique=True)
    S["valv_tapa"] = cyl(0.13, 0.04, (VALV[0], VALV[1], -D + 0.07), (0.85, 0.85, 0.88), parent=S["vaso"], unique=True)
    # agua
    S["agua"] = box((X1 - X0, YB, 1), (0, YB / 2, -D), WATER, parent=S["vaso"], unique=True); 
    S["bacterias"] = [sph(0.07, LEJOS, BACT, seg=8) for _ in range(18)]
    # proyección de hormigón
    S["lanza"] = empty(LEJOS)
    cyl(0.06, 0.8, (0, 0, 0.4), (0.25, 0.25, 0.28), parent=S["lanza"]); S["manguera"] = bar_obj((0.15, 0.15, 0.17), 0.06)
    S["chorro"] = [sph(0.06, LEJOS, CONCIN, seg=8) for _ in range(14)]
    # depuradora: bomba, filtro de arena (en corte), clorador
    S["equipo"] = []
    cyl(0.22, 0.6, (PX, 0.5, 0.25), (0.25, 0.45, 0.75), rot=(0, math.pi / 2, 0)); cyl(0.17, 0.5, (PX - 0.5, 0.5, 0.25), (0.6, 0.62, 0.66), rot=(0, math.pi / 2, 0))
    box((1.2, 0.6, 0.06), (PX - 0.2, 0.5, 0.03), (0.5, 0.5, 0.52))
    cut_f = box((2, 1, 3), (FX, -0.5 + 0.0, 0.8), None); cut_f.hide_render = cut_f.hide_viewport = True; S["cut_f"] = cut_f
    tank = cyl(0.42, 1.3, (FX, 0.0, 0.7), (0.3, 0.35, 0.4), unique=True)
    mm = tank.modifiers.new("s", "SOLIDIFY"); mm.thickness = 0.04
    mb = tank.modifiers.new("c", "BOOLEAN"); mb.operation = "DIFFERENCE"; mb.object = cut_f; mb.solver = "EXACT"; S["tank"] = tank
    sand = cyl(0.38, 0.75, (FX, 0.0, 0.45), (0.9, 0.8, 0.55), unique=True)
    mb = sand.modifiers.new("c", "BOOLEAN"); mb.operation = "DIFFERENCE"; mb.object = cut_f; mb.solver = "EXACT"; S["arena"] = sand
    sph(0.42, (FX, 0.25, 1.35), (0.3, 0.35, 0.4), scale=(1, 0.4, 0.4))
    S["suciedad"] = [sph(0.035, LEJOS, DIRTY, seg=8) for _ in range(22)]
    S["clorador"] = cyl(0.13, 0.35, (FX - 0.05, 0.25, -0.5 + 0.0), (0.95, 0.95, 0.95), unique=True)
    S["clorador"].location = (FX + 0.0, 0.25, -1.0)
    tubos(SUMI, PIPE, 0.06); tubos(SKIM, PIPE, 0.06); tubos(BOMBA_FILTRO, PIPE, 0.06); tubos(RETORNO, PIPE, 0.06)
    S["p_sucia"] = [sph(0.07, LEJOS, DIRTY, seg=8) for _ in range(24)]
    S["p_limpia"] = [sph(0.07, LEJOS, CLEAN, seg=8) for _ in range(14)]
    S["cl"] = [sph(0.05, LEJOS, (0.95, 0.95, 0.4), seg=8) for _ in range(8)]
    S["jet"] = [sph(0.06, LEJOS, CLEAN, seg=8) for _ in range(10)]
    # agua del subsuelo (franja azul translúcida en el corte) y lluvia
    S["freatico"] = []
    for x0, x1, top in ((-15, X0 - TH, 1), (X1 + TH, 15, 1), (X0 - TH, X1 + TH, 0)):
        o = box((x1 - x0, 0.02, 1), ((x0 + x1) / 2, -0.03, -3), GW, unique=True); alpha(o, 0.4); S["freatico"].append((o, top))
    S["lluvia"] = [bar_obj((0.85, 0.92, 1.0), 0.03) for _ in range(60)]
    S["flechas"] = []
    for k in range(5):
        bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0, depth=0.8, location=LEJOS); f = bpy.context.object; setup(f, (0.2, 0.45, 1.0))
        S["flechas"].append(f)
    S["peso"] = []
    for k in range(3):
        bpy.ops.mesh.primitive_cone_add(radius1=0.26, radius2=0, depth=0.55, location=LEJOS, rotation=(math.pi, 0, 0)); f = bpy.context.object
        setup(f, (0.95, 0.85, 0.3)); S["peso"].append(f)
    S["grietas"] = [box((0.05, 0.03, 0.5), LEJOS, (0.15, 0.12, 0.1), rot=(0, 0.4 * (k - 1), 0)) for k in range(3)]
    S["entra"] = [sph(0.06, LEJOS, GW, seg=8) for _ in range(10)]
    dyn = [cam, hueco, S["suelo"], S["cesped"], S["trozos"], S["tierra"], S["exc"], S["brazo1"], S["brazo2"], S["cazo"], S["malla"], S["vaso"],
           S["bacterias"], S["lanza"], S["manguera"], S["chorro"], cut_f, tank, sand, S["suciedad"], S["clorador"], S["p_sucia"], S["p_limpia"],
           S["cl"], S["jet"], [o for o, _ in S["freatico"]], S["lluvia"], S["flechas"], S["peso"], S["grietas"], S["entra"]]
    join_static(dyn)
    return sc, S

def nivel_freatico(t):
    return keyed(t, [(0, -4.5), (T("si llueve"), -4.5), (T("el fondo hacia", fin=True), -0.9), (T("así que en el"), -0.9),
                     (T("por eso nunca"), -1.2), (DUR + 2, -1.2)])

def nivel_agua(t):
    """altura del agua respecto al fondo (0..D-0.15)"""
    full = D - 0.15
    return keyed(t, [(0, 0), (T("la llenas"), 0), (T("son cuarenta"), full), (T("y ahora"), full), (T("sabías que") + 1.4, 0.05),
                     (T("con la piscina llena"), 0.05), (T("con la piscina llena") + 0.6, full), (T("pero si la vacías"), full),
                     (T("pero si la vacías") + 0.8, 0.05), (T("se abre"), 0.05), (T("por eso nunca"), 0.45), (DUR + 2, 0.5)])

def excav(t):
    """(frente de excavación en x, profundidad)"""
    t0, t1 = 0.0, T("y metro y medio", fin=True)
    u = seg(t, t0, t1)
    return mix(X0 - TH + 0.6, X1 + TH, min(1, u * 1.25)), mix(0.5, D + TH, u)

def pose(t, S):
    t_pero, t_malla, t_proy, t_caja, t_llen = T("pero la tierra"), T("pones una malla"), T("proyectas"), T("ahora tienes"), T("la llenas")
    t_verde, t_circ, t_sale, t_bomba, t_vuelve = T("pero el agua quieta"), T("así que la haces"), T("sale por"), T("una bomba"), T("y vuelve limpia")
    t_cada, t_bact, t_cloro, t_dato, t_llueve = T("cada día"), T("pero la arena"), T("añades cloro"), T("y ahora"), T("si llueve")
    t_llena, t_vac, t_valv, t_abre, t_fin = T("con la piscina llena"), T("pero si la vacías"), T("así que en el"), T("se abre"), T("por eso nunca")
    # excavación
    xe, de = excav(t)
    S["hueco"].scale = (xe - (X0 - TH), YB + TH + 1.0, de + 0.3); S["hueco"].location = (((X0 - TH) + xe) / 2, (YB + TH - 1.0) / 2, -de / 2 + 0.15)
    # excavadora: cazo que cava y descarga
    ex = keyed(t, [(0, -6.6), (t_pero, -6.6), (t_pero + 1.5, -11.0), (DUR + 2, -11.0)])
    S["exc"].location = (ex, 1.0, 0)
    ph = (t * 0.75 + 0.4) % 1.0
    dig = Vector((min(xe - 0.4, X1 - 0.2), 1.0, -de + 0.35)); up = Vector((ex + 2.8, 1.0, 2.0)); dump = Vector((ex + 1.6, 1.0, 1.6))
    if ph < 0.45: tgt = up.lerp(dig, ss(ph / 0.45))
    elif ph < 0.6: tgt = dig + Vector((-0.6 * ss((ph - 0.45) / 0.15), 0, 0.3 * ss((ph - 0.45) / 0.15)))
    else: tgt = (dig + Vector((-0.6, 0, 0.3))).lerp(up, ss((ph - 0.6) / 0.4))
    if t > t_pero: tgt = Vector((ex + 2.5, 1.0, 1.8))
    base = Vector((ex + 0.6, 1.0, 1.4)); L1, L2 = 3.8, 3.2
    dv = tgt - base; dl = min(dv.length, L1 + L2 - 0.05)
    a = math.acos(max(-1, min(1, (L1 ** 2 + dl ** 2 - L2 ** 2) / (2 * L1 * dl))))
    ang = math.atan2(dv.z, dv.x) + a
    elbow = base + Vector((L1 * math.cos(ang), 0, L1 * math.sin(ang)))
    tip = base + dv.normalized() * dl
    bar_set(S["brazo1"], base, elbow); bar_set(S["brazo2"], elbow, tip)
    S["cazo"].location = tip; S["cazo"].rotation_euler = (0, -0.6 + (1.2 if 0.45 < ph < 0.9 else 0.0), 0)
    S["cazo_tierra"].hide_render = not (0.5 < ph < 0.92) or t > t_pero
    for k, o in enumerate(S["tierra"]):
        u = (ph - 0.9) / 0.1
        if 0.9 < ph and t < t_pero:
            o.location = tip + Vector((-0.5 * u - 0.1 * k, 0, -1.6 * u * u + 0.05 * k))
        else: o.location = LEJOS
    # derrumbe de las paredes
    for k, o in enumerate(S["trozos"]):
        u = seg(t, t_pero + 0.5 + 0.08 * k, t_pero + 1.4 + 0.08 * k)
        side = X0 - TH if k % 2 == 0 else X1 + TH
        sx = 1 if k % 2 == 0 else -1
        z0 = -0.3 - 0.1 * (k % 4)
        if t_pero < t < t_malla + 0.6:
            o.location = (side + sx * (0.1 + 0.9 * u + 0.05 * k), 0.3 + 0.12 * k, mix(z0, -D - TH + 0.15, u * u)); o.rotation_euler = (u * 2, u * 1.3, 0)
        else: o.location = LEJOS
    # malla y hormigón proyectado
    S["malla"].hide_render = t < t_malla - 0.1 or t > t_caja + 0.4
    pr = seg(t, t_proy - 0.2, T("a presión", fin=True) + 0.4)
    vis_vaso = t > t_proy - 0.3
    for i, piezas in enumerate(S["tramos"]):
        on = vis_vaso and (i + 0.5) / NSEG < pr
        for p in piezas[:2]: p.hide_render = not on
        for p in piezas[2:]: p.hide_render = not (on and t > t_caja)
    for o in S["extremos"]: o.hide_render = not vis_vaso or (o.location.x < 0 and pr < 0.05) or (o.location.x > 0 and pr < 0.98)
    for o in S["cara"] + [S["borde"]]: o.hide_render = t < t_caja
    for o in (S["sumidero"], S["skimmer"], S["boquilla"]): o.hide_render = t < t_circ - 0.2
    S["valvula"].hide_render = S["valv_tapa"].hide_render = t < t_valv + 0.6
    xn = mix(X0 - TH, X1 + TH, pr)
    if t_proy - 0.3 < t < T("a presión", fin=True) + 0.5:
        nz = Vector((xn, 0.9, -0.4 + 0.3 * math.sin(t * 5)))
        S["lanza"].location = nz; S["lanza"].rotation_euler = (0.5, 0.5, 0)
        bar_set(S["manguera"], nz + Vector((0, 0, 0.8)), Vector((xn - 1, 0.6, 1.2)))
        for k, c in enumerate(S["chorro"]):
            u = ((t * 2.5 + k / 14) % 1.0)
            c.location = nz + Vector((0.1 * math.sin(k * 3.1), 1.2 * u, -0.6 * u - 0.3 * u * math.cos(k)))
    else:
        S["lanza"].location = LEJOS; bar_set(S["manguera"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
        for c in S["chorro"]: c.location = LEJOS
    # vaso que flota y se rompe; vuelve a su sitio al abrir la válvula
    lev = seg(t, t_vac + 1.2, T("levantarse", fin=True) + 0.6) * (1 - seg(t, t_valv - 0.2, t_valv + 0.8))
    S["vaso"].location = (0, 0, 1.0 * lev); S["vaso"].rotation_euler = (0, 0.04 * lev, 0)
    for k, g in enumerate(S["grietas"]):
        g.location = (-1.5 + 1.4 * k, -0.02, -D - TH / 2 + 1.0 * lev) if T("y romperse") - 0.1 < t < t_abre + 0.6 else LEJOS
    # agua
    h = nivel_agua(t)
    S["agua"].hide_render = h < 0.02 or t < t_llen - 0.1
    S["agua"].scale = (X1 - X0 - 0.04, YB - 0.04, max(0.01, h)); S["agua"].location = (0, YB / 2, -D + 0.02 + h / 2)
    verde = seg(t, T("en pocos días"), T("se vuelve verde", fin=True)) * (1 - seg(t, t_vuelve, t_cada + 2.5))
    col = tuple(mix(a, b, verde) for a, b in zip(WATER, GREENW))
    m = S["agua"].active_material; m.diffuse_color = (*lin(col), 1.0)
    # bacterias: aparecen con el agua verde y en la nota de la arena; el cloro las elimina
    rng = random.Random(9)
    for k, b in enumerate(S["bacterias"]):
        x, y, z = rng.uniform(X0 + 0.3, X1 - 0.3), -0.03, rng.uniform(-D + 0.15, -0.3)
        on = (T("en pocos días") < t < t_circ + 1.0) or (t_bact - 0.1 < t < t_cloro + 0.4 + 0.08 * k)
        b.location = (x, y, z + 0.05 * math.sin(t * 3 + k)) if on else LEJOS
    # circulación: sucia hacia la bomba y el filtro; limpia de vuelta
    circ = win01(t, t_sale - 0.2, t_bact + 0.5) + win01(t, t_cloro - 0.2, t_dato + 0.3)
    caminos = [SUMI + BOMBA_FILTRO[1:], SKIM + BOMBA_FILTRO[1:]]
    for k, p in enumerate(S["p_sucia"]):
        if circ > 0.05:
            path = caminos[k % 2]; s = ((k // 2) / 12 + (t - t_sale) * 0.12) % 1.0
            if t < t_bomba and s > 0.5: s *= 0.5
            p.location = along(path, s); p.scale = (circ,) * 3
        else: p.location = LEJOS
    lim = circ * seg(t, t_vuelve - 0.4, t_vuelve + 0.2)
    for k, p in enumerate(S["p_limpia"]):
        if lim > 0.05: p.location = along(RETORNO, (k / 14 + (t - t_vuelve) * 0.12) % 1.0); p.scale = (lim,) * 3
        else: p.location = LEJOS
    for k, p in enumerate(S["jet"]):
        if lim > 0.05:
            u = (t * 1.2 + k / 10) % 1.0; p.location = (X0 + 0.15 + 2.8 * u, -0.03, -0.45 + 0.05 * math.sin(k * 2.0))
            p.scale = ((1 - u) * lim,) * 3
        else: p.location = LEJOS
    rng = random.Random(5)
    trap = seg(t, T("que atrapa"), T("que atrapa") + 2.5)
    for k, d in enumerate(S["suciedad"]):
        ang = rng.uniform(0, math.pi); r = rng.uniform(0.0, 0.34)
        d.location = (FX + r * math.cos(ang), 0.02 + r * math.sin(ang) * 0.3, 0.82 - 0.03 * (k % 3)) if trap > (k + 1) / 23 else LEJOS
    S["clorador"].location = (FX, 0.25, -0.7) if t > t_cloro - 0.2 else LEJOS
    for k, c in enumerate(S["cl"]):
        if t_cloro < t < t_dato:
            c.location = along(RETORNO, (0.18 + k / 8 * 0.82 + (t - t_cloro) * 0.12) % 1.0)
        else: c.location = LEJOS
    # agua del subsuelo, lluvia y empujes
    gz = nivel_freatico(t)
    for o, top in S["freatico"]:
        z_top = gz if top else min(gz, -D - TH + 1.0 * lev)
        z_bot = -6.0
        o.hide_render = z_top < -5.9 or t < t_llueve - 0.2
        o.scale.z = max(0.01, z_top - z_bot); o.location.z = (z_top + z_bot) / 2
    for k, r in enumerate(S["lluvia"]):
        if t_llueve - 0.2 < t < t_llena:
            rr = random.Random(k); x = rr.uniform(-7, 7); y = rr.uniform(-1.5, 2); z = 5 - ((t * 9 + rr.uniform(0, 5)) % 5)
            bar_set(r, (x, y, max(z, 0.05 if y > 0 else -9)), (x, y, max(z, 0.05 if y > 0 else -9) + 0.45))
        else: bar_set(r, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    empuje = seg(t, T("empuja el fondo") - 0.3, T("el fondo hacia", fin=True)) * (1 - seg(t, t_abre + 0.3, t_abre + 1.5))
    for k, f in enumerate(S["flechas"]):
        if empuje > 0.05 and t < t_fin:
            f.location = (-3.0 + 1.5 * k, -0.25, -D - TH - 0.7 + 1.0 * lev + 0.12 * math.sin(t * 6 + k)); f.scale = (empuje,) * 3
        else: f.location = LEJOS
    pes = win01(t, t_llena + 0.3, t_vac + 0.3)
    for k, f in enumerate(S["peso"]):
        if pes > 0.05: f.location = (-2.5 + 2.5 * k, -0.25, -0.5 - 0.1 * math.sin(t * 5 + k)); f.scale = (pes,) * 3
        else: f.location = LEJOS
    vo = seg(t, t_abre - 0.1, t_abre + 0.3)
    S["valv_tapa"].location = (VALV[0], VALV[1], -D + 0.07 + 0.18 * vo * (1 - seg(t, t_fin + 1.0, t_fin + 1.5)))
    for k, p in enumerate(S["entra"]):
        if t_abre < t < t_fin + 1.2:
            u = (t * 0.9 + k / 10) % 1.0
            p.location = (VALV[0] + 0.15 * math.sin(k * 2.3), -0.05, -D - TH - 0.7 + 1.3 * u)
        else: p.location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def V(at, off, lens=28): at = Vector(at) + Vector((0, 0, 0.7)); return (tuple(at + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v, hold=0.0):
        k.append((t,) + v)
        if hold: k.append((t + hold,) + v)
    add(0.0, V((-3.2, 1.0, -0.4), (-1.0, -3.2, 0.9), 32))
    add(2.2, V((-2.5, 1.0, -0.6), (-1.8, -4.5, 1.4), 30))
    add(T("y metro y medio"), V((0.0, 1.0, -0.9), (-3.0, -6.5, 2.4), 26))
    add(T("pero la tierra") + 0.4, V((-2.8, 0.8, -1.0), (-1.2, -4.2, 1.1), 28), 1.0)
    add(T("proyectas"), V((-1.0, 0.8, -1.0), (-1.8, -4.8, 1.4), 28))
    add(T("ahora tienes") + 0.5, V((0.0, 1.0, -0.9), (-3.0, -6.5, 2.4), 26))
    add(T("la llenas") + 0.5, V((0.0, 1.0, -0.9), (-2.8, -6.0, 2.0), 26), 3.0)
    add(T("se vuelve verde"), V((-0.5, 1.0, -0.8), (-2.2, -5.0, 1.6), 27))
    add(T("sale por") + 0.5, V((3.0, 0.8, -1.0), (-2.0, -6.0, 1.4), 26))
    add(T("una bomba") + 0.3, V((6.0, 0.5, -0.2), (-1.5, -5.0, 1.2), 27), 1.5)
    add(T("y vuelve limpia"), V((0.5, 0.8, -1.0), (-1.8, -7.0, 1.8), 24))
    add(T("cada día") + 1.0, V((1.0, 0.8, -0.9), (-1.2, -7.5, 2.0), 24))
    add(T("pero la arena"), V((-0.5, 0.8, -0.8), (-2.0, -5.0, 1.3), 27))
    add(T("añades cloro") + 0.3, V((5.5, 0.4, -0.5), (-1.2, -5.0, 1.0), 27))
    add(T("el dato curioso"), V((-0.5, 0.8, -1.8), (-2.0, -7.5, 1.8), 25))
    add(T("si llueve") + 0.5, V((-0.5, 0.8, -2.1), (-2.0, -8.0, 2.0), 25), 2.5)
    add(T("con la piscina llena"), V((-0.5, 0.8, -1.9), (-1.8, -7.0, 1.5), 25))
    add(T("pero si la vacías") + 1.5, V((-0.5, 0.8, -1.5), (-1.6, -7.0, 1.4), 25), 1.5)
    add(T("así que en el") + 0.6, V((VALV[0], 0.6, -D - 0.3), (-1.0, -4.5, 2.0), 28), 1.3)
    add(T("se abre") + 0.4, V((VALV[0], 0.6, -D - 0.4), (-0.8, -4.0, 1.6), 28))
    add(T("por eso nunca") + 0.5, V((0.0, 0.8, -1.4), (-2.5, -7.5, 2.0), 25))
    add(DUR + 2, V((0.0, 0.8, -1.2), (-3.0, -8.5, 2.4), 25))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); lz = S["vaso"].location.z
    return {"largo": Pj((0, 0, 0.3)), "fondo": Pj((X0 - 0.4, 0, -D / 2)), "malla": Pj((0, YB, -0.5)), "agua": Pj((0, 0.5, -0.4)),
            "sumidero": Pj((0, 0.0, -D + lz)), "skimmer": Pj((X1, 0.0, -0.1 + lz)), "bomba": Pj((PX, 0.5, 0.5)), "filtro": Pj((FX, 0, 1.45)),
            "boquilla": Pj((X0, 0.0, -0.4 + lz)), "cloro": Pj((FX, 0.25, -0.45)), "freatico": Pj((-7, 0, nivel_freatico(t) - 0.3)),
            "valvula": Pj((VALV[0], VALV[1], -D + lz)), "vaso": Pj((0, 0, -D - TH + lz))}

if __name__ == "__main__":
    run("piscina", build, pose, anchors)
