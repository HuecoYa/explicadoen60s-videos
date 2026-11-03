# «¿Y si construyes un rascacielos?»: corte bajo tierra y del edificio: plantas que se hunden, pilotes hasta la roca,
# núcleo con ascensor, viento y balanceo, péndulo amortiguador, depósitos de agua por tramos y piel de cristal.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("rascacielos")
CONC = (0.78, 0.78, 0.8); CORE = (0.55, 0.56, 0.6); SOIL = (0.62, 0.45, 0.3); SOIL2 = (0.5, 0.36, 0.25); ROCK = (0.5, 0.5, 0.55)
GRASS = (0.42, 0.7, 0.35); GLASS = (0.42, 0.72, 0.97); WATER = (0.3, 0.6, 1.0); GOLD = (0.95, 0.75, 0.25)
NF, FH, W = 60, 0.4, 4.0        # plantas, altura de planta, ancho
HMAX = NF * FH

def bool_diff(o, c):
    b = o.modifiers.new(c.name, "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = c

def build():
    sc, cam = scene_setup(world=(0.62, 0.8, 0.96))
    S = {"cam": cam}
    # terreno en corte: hierba, dos capas de tierra y roca
    box((80, 40, 0.3), (0, 20, -0.15), GRASS)
    box((80, 6, 5), (0, 3, -2.5 - 0.3), SOIL); box((80, 6, 4), (0, 3, -7.3), SOIL2); box((80, 6, 8), (0, 3, -13.3), ROCK)
    rng = random.Random(2)
    for k in range(40): sph(rng.uniform(0.15, 0.45), (rng.uniform(-30, 30), -0.02, rng.uniform(-16, -10)), (0.42, 0.42, 0.47), scale=(1.4, 0.3, 1))
    for k in range(18):  # ciudad de fondo
        h = rng.uniform(4, 14); box((rng.uniform(2, 4), 2, h), (rng.uniform(-36, 36), rng.uniform(14, 24), h / 2), (0.7, 0.76, 0.86))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 10)); cut = bpy.context.object; cut.scale = (30, 10, 60); cut.hide_render = True; cut.name = "corte"
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 100)); techo = bpy.context.object; techo.scale = (30, 30, 100); techo.hide_render = True; techo.name = "techo"
    S["cut"], S["techo"] = cut, techo
    torre = empty((0, 0, 0)); S["torre"] = torre
    # plantas: un objeto por planta (forjado + pilares); se muestran según la altura construida
    S["plantas"] = []
    for i in range(NF):
        z = i * FH; piezas = [box((W, W, 0.09), (0, 0, z + FH - 0.045), CONC)]
        for x in (-W / 2 + 0.12, W / 2 - 0.12):
            for y in (-W / 2 + 0.12, 0, W / 2 - 0.12):
                piezas.append(box((0.16, 0.16, FH), (x, y, z + FH / 2), (0.7, 0.7, 0.72)))
        bpy.ops.object.select_all(action='DESELECT')
        for p in piezas: p.select_set(True)
        bpy.context.view_layer.objects.active = piezas[0]; bpy.ops.object.join()
        o = bpy.context.object; o.parent = torre; o["z"] = z; S["plantas"].append(o)
    S["rojo"] = box((W + 0.02, W + 0.02, 6 * FH), (0, 0, 3 * FH), (0.95, 0.3, 0.25), parent=torre, unique=True); bool_diff(S["rojo"], cut)
    S["nucleo"] = box((1.3, 1.3, HMAX), (0, 0.8, HMAX / 2), CORE, parent=torre, unique=True)
    S["asc"] = box((0.5, 0.5, 0.35), (0, 0.35, 1), (1, 0.82, 0.2), parent=torre, unique=True)
    S["tubo"] = cyl(0.13, HMAX - 1, (1.0, 0.6, (HMAX - 1) / 2), (0.4, 0.55, 0.9), parent=torre, unique=True)
    S["tanques"] = []
    for f in (14, 29, 44, 57):
        z = f * FH; sh = cyl(0.75, 1.1, (1.2, 0.3, z + 0.55), (0.85, 0.88, 0.92), parent=torre, unique=True)
        w = cyl(0.68, 1.0, (1.2, 0.3, z + 0.55), WATER, parent=torre, unique=True); w["z"] = z; S["tanques"].append(w)
        bo = box((0.5, 0.4, 0.4), (0.3, 0.3, z + 0.2), (0.95, 0.5, 0.15), parent=torre, unique=True)
        S.setdefault("conj_agua", []).extend([sh, bo])
    # péndulo
    S["pend"] = empty((0, 0.4, HMAX - 0.6), parent=torre)
    for x in (-0.25, 0.25): box((0.04, 0.04, 2.0), (x, 0, -1.0), (0.3, 0.3, 0.32), parent=S["pend"])
    S["bola"] = sph(0.95, (0, 0, -2.2), GOLD, parent=S["pend"], seg=32, unique=True)
    # piel de cristal
    S["cristal"] = empty((0, 0, 0), parent=torre)
    for x, y, sx, sy in ((-W / 2 - 0.03, 0, 0.04, W), (W / 2 + 0.03, 0, 0.04, W), (0, W / 2 + 0.03, W, 0.04)):
        g = box((sx, sy, HMAX), (x, y, HMAX / 2), GLASS, parent=S["cristal"]); bool_diff(g, cut)
        for k in range(1, NF // 3): box((sx + 0.02 if sx < 1 else sx, sy + 0.02 if sy < 1 else sy, 0.05), (x, y, k * 3 * FH), (0.35, 0.45, 0.55), parent=S["cristal"])
    # pilotes
    S["pilotes"] = [cyl(0.22, 10.5, (x, -0.06, 0), (0.6, 0.6, 0.64), unique=True) for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    S["viento"] = [box((1.6, 0.05, 0.05), (0, 0, -40), (1, 1, 1)) for _ in range(16)]
    S["arena"] = [sph(0.12, (0, 0, -40), SOIL) for _ in range(14)]
    join_static([cam, cut, techo, torre, S["pilotes"], S["viento"], S["arena"]])
    return sc, S

def pose(t, S):
    t_api, t_hunde, t_exc, t_sub = T("apilando"), T("hunde"), T("así que excavas"), T("subes plantas")
    t_abajo, t_nuc, t_viento, t_bal = T("las de abajo"), T("núcleo"), T("el viento"), T("se balancea")
    t_bola, t_frena, t_tai, t_agua = T("cuelgas"), T("frena"), T("taipéi"), T("aún queda el agua")
    t_dep, t_piel = T("pones depósitos"), T("piel de cristal")
    # altura construida
    h = keyed(t, [(0, 0.0), (t_api - 0.2, 0.0), (t_api + 1.5, 10 * FH), (t_exc + 0.2, 10 * FH), (t_exc + 0.9, 0.0),
                  (t_sub - 0.3, 0.0), (t_sub + 2.4, HMAX), (DUR + 5, HMAX)])
    for o in S["plantas"]: o.hide_render = o["z"] + FH * 0.5 > h
    S["nucleo"].hide_render = t < t_nuc - 0.2
    S["nucleo"].scale.z = max(0.001, h / HMAX); S["nucleo"].location.z = h / 2
    # hundimiento antes de los pilotes
    hund = seg(t, t_hunde, t_hunde + 1.6) * (1 - seg(t, t_exc, t_exc + 0.6))
    # balanceo por viento, frenado por el péndulo
    amp = 0.035 * seg(t, t_bal, t_bal + 1.0) * (1 - 0.8 * seg(t, t_frena - 0.3, t_frena + 1.2)) * (1 - seg(t, t_agua, t_agua + 1.0))
    ang = amp * math.sin(t * 2.6)
    S["torre"].location = (0, 0, -1.4 * hund); S["torre"].rotation_euler = (0, ang, 0)
    S["pend"].rotation_euler = (0, -ang * 9 * seg(t, t_bola + 0.6, t_bola + 1.4), 0)
    for c in S["pend"].children: c.hide_render = t < t_bola
    S["bola"].scale = (seg(t, t_bola + 0.2, t_bola + 0.9),) * 3
    # plantas de abajo en rojo (cargan con todo)
    S["rojo"].hide_render = not (t_abajo - 0.1 < t < t_nuc)
    # ascensor sube y baja en el núcleo
    S["asc"].location.z = 0.5 + (HMAX - 2) * (0.5 - 0.5 * math.cos((t - t_nuc) * 0.9)) if t > t_nuc + 0.4 else -40
    # agua: depósitos que se llenan por tramos
    for k, w in enumerate(S["tanques"]):
        f = seg(t, t_dep + 0.5 + k * 0.9, t_dep + 1.2 + k * 0.9)
        w.scale.z = max(0.001, f); w.location.z = w["z"] + 0.05 + 0.5 * f
        w.hide_render = t < t_agua
    S["tubo"].hide_render = t < t_agua
    for o in S["conj_agua"]: o.hide_render = t < t_agua
    # cristal
    S["cristal"].scale = (1, 1, max(0.001, seg(t, t_piel, t_piel + 1.6)))
    for c in S["cristal"].children: c.hide_render = t < t_piel
    # pilotes que bajan hasta la roca
    for k, p in enumerate(S["pilotes"]):
        u = seg(t, t_exc + 0.6 + k * 0.12, t_exc + 1.8 + k * 0.12)
        p.location.z = -u * 10.5 / 2; p.scale.z = max(0.001, u); p.hide_render = t < t_exc + 0.5
    # viento
    for k, v in enumerate(S["viento"]):
        r = random.Random(k)
        if t_viento - 0.2 < t < t_frena + 2:
            u = (t * 0.5 + k / 16) % 1.0; v.location = (-14 + 28 * u, r.uniform(-3, 3), r.uniform(12, HMAX + 2))
        else: v.location = (0, 0, -40)
    for k, a in enumerate(S["arena"]):
        r = random.Random(k + 9)
        a.location = (r.uniform(-2.6, 2.6), -0.15, -0.2 - 1.4 * hund + r.uniform(0, 0.6)) if hund > 0.05 else (0, 0, -40)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.05))

def V(z, d, x=0.0, h=1.0, lens=30): return ((x, -d, z + h), (x * 0.3, 0, z), lens)
def CAM():
    return [(0.0,) + V(1.0, 20), (T("apilando"),) + V(1.5, 18), (T("hunde"),) + V(-0.5, 16, 0, 1.5), (T("así que excavas"),) + V(-5, 24, 0, 1.0),
            (T("ahora el peso"),) + V(-4, 26), (T("subes plantas"),) + V(6, 34), (T("subes plantas") + 2.6,) + V(10, 44),
            (T("las de abajo"),) + V(2, 22), (T("núcleo"),) + V(8, 30), (T("el viento"),) + V(14, 40), (T("cuelgas"),) + V(21, 14, 0, 0.5),
            (T("frena"),) + V(20, 18), (T("taipéi"),) + V(19, 22), (T("aún queda el agua"),) + V(12, 34), (T("pones depósitos"),) + V(12, 26, 0.6),
            (T("piel de cristal"),) + V(10, 46), (T("sígueme"),) + V(8, 50, 3), (DUR + 2,) + V(8, 52, 3)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"pilotes": Pj((0, -0.5, -8)), "roca": Pj((5, -0.5, -12)), "nucleo": Pj((0, 0.8, 12)), "bola": Pj((0, 0.4, HMAX - 2.8)),
            "abajo": Pj((0, -0.5, 1.2)), "tanque": Pj((1.45, 0.6, 29 * FH)), "torre": Pj((0, 0, HMAX * 0.6)), "cima": Pj((0, 0, HMAX))}

if __name__ == "__main__":
    run("rascacielos", build, pose, anchors)
