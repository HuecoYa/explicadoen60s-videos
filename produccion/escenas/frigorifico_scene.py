# «Así funciona la nevera»: nevera cortada de lado; circuito del refrigerante (evaporador dentro, compresor abajo,
# condensador negro detrás, tubo capilar) con el líquido cambiando de color; el calor sale de la comida y va a la cocina.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("frigorifico")
WHITE = (0.95, 0.96, 0.97); INNER = (0.86, 0.9, 0.95); COLD = (0.25, 0.6, 1.0); HOT = (1.0, 0.3, 0.15); WARM = (1.0, 0.65, 0.2)
FLOOR = (0.8, 0.72, 0.62); WALL = (0.72, 0.84, 0.8); BLACK = (0.15, 0.15, 0.17)
X0 = 0.25   # plano donde van los tubos (justo detrás del corte)

def zigzag(y, z0, z1, n, x=X0, w=0.0):
    pts = []
    for k in range(n + 1):
        z = mix(z0, z1, k / n); pts += [Vector((x, y, z)), Vector((x + 0.0, y, z))]
    return pts

# recorrido cerrado del refrigerante: evaporador (dentro, pared del fondo) → compresor → condensador (fuera, detrás) → capilar
EVAP = [Vector((X0, 0.75, 5.2 - 0.25 * k)) + Vector((0, 0, 0)) for k in range(7)]
CIRC = ([Vector((X0, 0.72, 5.25))] +
        [Vector((X0 + (0.9 if k % 2 else -0.9) * 0 , 0.72, 5.1 - 0.22 * k)) for k in range(1)] +
        [Vector((X0, 0.72, 3.6)), Vector((X0, 0.72, 3.3)), Vector((X0, 1.15, 3.3)), Vector((X0, 1.15, 0.9)), Vector((X0, 1.45, 0.75)),
         Vector((X0, 1.45, 0.75))])

def ruta():
    """lista de puntos y fase de cada tramo: 0 evaporador, 1 hacia compresor, 2 compresor, 3 condensador, 4 capilar"""
    P, F = [], []
    def add(p, f): P.append(Vector(p)); F.append(f)
    # evaporador en serpentín
    for k in range(6):
        z = 5.2 - 0.32 * k
        add((X0, 0.72, z), 0); add((X0, 0.72, z - 0.16), 0)
    add((X0, 0.72, 3.2), 1); add((X0, 1.05, 3.2), 1); add((X0, 1.05, 0.9), 1)
    add((X0, 1.25, 0.7), 2); add((X0, 1.55, 0.7), 2)
    # condensador detrás (serpentín que sube)
    for k in range(9):
        z = 1.1 + 0.48 * k
        add((X0, 1.4, z), 3); add((X0, 1.4, z + 0.24), 3)
    add((X0, 1.4, 5.6), 4); add((X0, 0.95, 5.6), 4); add((X0, 0.95, 5.35), 4); add((X0, 0.72, 5.35), 4)
    return P, F

def build():
    sc, cam = scene_setup(world=(0.93, 0.9, 0.85))
    S = {"cam": cam}
    box((60, 60, 0.1), (0, 0, -0.05), FLOOR); box((0.2, 60, 30), (8, 0, 15), WALL)
    for k in range(-20, 21): box((0.03, 60, 0.005), (k * 1.0, 0, 0.003), (0.72, 0.64, 0.55))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-5.0, 0, 3)); cutter = bpy.context.object; cutter.scale = (10, 14, 14); cutter.hide_render = True
    S["cutter"] = cutter
    def cortar(o, inner=None, th=0.08):
        m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
        if inner: o.data.materials.append(mat(inner, unique=True)); m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
    cuerpo = box((2.4, 2.0, 5.6), (0, 0, 3.0), WHITE, unique=True); cortar(cuerpo, INNER, 0.18); S["cuerpo"] = cuerpo
    S["piv"] = empty((-1.2, -1.0, 3.0))
    puerta = box((2.4, 0.18, 5.6), (1.2, -0.09, 0), WHITE, parent=S["piv"], unique=True)
    b = puerta.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
    box((0.08, 0.12, 1.2), (2.2, -0.24, 0.8), (0.7, 0.72, 0.76), parent=S["piv"])
    for z in (1.6, 3.0, 4.3): box((2.1, 1.7, 0.05), (0, -0.05, z), (0.8, 0.9, 1.0))
    rng = random.Random(1); S["comida"] = []
    for z in (1.6, 3.0, 4.3):
        for k in range(4):
            c = random.choice([(0.95, 0.3, 0.3), (0.3, 0.75, 0.35), (0.98, 0.8, 0.3), (0.95, 0.55, 0.2)])
            o = box((0.4, 0.4, rng.uniform(0.3, 0.7)), (rng.uniform(0.2, 0.9), -0.6 + k * 0.38, z + 0.3), c, unique=True); S["comida"].append(o)
    # tubos: un tramo de tubo entre cada par de puntos
    P, F = ruta(); S["P"], S["F"] = P, F
    S["tubos"] = []
    for i in range(len(P) - 1):
        r = 0.035 if F[i] == 4 else 0.07
        o = bar_obj((0.6, 0.62, 0.66) if F[i] != 3 else BLACK, r, unique=True); bar_set(o, P[i], P[i + 1]); S["tubos"].append(o)
    o = bar_obj((0.6, 0.62, 0.66), 0.07, unique=True); bar_set(o, P[-1], P[0]); S["tubos"].append(o)
    S["comp"] = empty((X0, 1.4, 0.55))
    cyl(0.42, 0.75, (0, 0, 0), (0.18, 0.18, 0.2), parent=S["comp"]); cyl(0.3, 0.1, (0, 0, 0.42), (0.3, 0.3, 0.34), parent=S["comp"])
    S["termo"] = cyl(0.12, 0.25, (-0.2, 0.0, 5.3), (0.95, 0.85, 0.25), rot=(0, math.pi / 2, 0), unique=True)
    S["gotas"] = [sph(0.11, (0, 0, -9), COLD, unique=True) for _ in range(46)]
    S["calor"] = [sph(0.09, (0, 0, -9), WARM, unique=True) for _ in range(14)]
    S["ondas"] = [torus(0.35, 0.03, (0, 0, -9), (1, 0.55, 0.25), rot=(0, math.pi / 2, 0)) for _ in range(5)]
    join_static([cam, cutter, cuerpo, S["piv"], S["comida"], S["tubos"], S["comp"], S["termo"], S["gotas"], S["calor"], S["ondas"]])
    return sc, S

def punto(P, s):
    """posición a la distancia s a lo largo del circuito cerrado"""
    L = [(P[i] - P[(i + 1) % len(P)]).length for i in range(len(P))]; tot = sum(L); s %= tot
    for i, l in enumerate(L):
        if s <= l: return P[i].lerp(P[(i + 1) % len(P)], s / max(l, 1e-6)), i
        s -= l
    return P[0], 0

def pose(t, S):
    t_mira, t_ref, t_evap, t_gas = T("mira dentro"), T("refrigerante"), T("se evapora"), T("ahora es un gas")
    t_comp, t_apr, t_rej, t_trasera = T("compresor"), T("lo aprieta"), T("rejilla negra"), T("por eso la parte")
    t_cap, t_cae, t_vuelve, t_term = T("tubo finísimo"), T("la presión cae"), T("vuelve a entrar"), T("termostato")
    t_puerta, t_fin = T("si dejas la puerta"), T("todo el calor")
    S["cutter"].location.x = -5.0 - 25 * (1 - seg(t, t_mira - 0.2, t_mira + 0.8))
    P, F = S["P"], S["F"]
    # el refrigerante circula (se para con el termostato)
    on = 1 - win01(t, T("apaga el compresor"), t_puerta - 0.3, 0.3, 0.3)
    S.setdefault("s", 0.0); dt = 1 / 30
    S["s"] = S.get("s_base", 0) + 0  # evita acumulación entre frames saltados
    sbase = 2.2 * (t - win01_integral(t, T("apaga el compresor"), t_puerta - 0.3))
    for k, g in enumerate(S["gotas"]):
        p, i = punto(P, sbase + k * 0.55)
        g.location = p if t > t_ref - 0.3 else (0, 0, -9)
        f = F[i]
        col = {0: COLD, 1: (0.55, 0.75, 1.0), 2: HOT, 3: mix_c(HOT, WARM, 0.5), 4: (0.35, 0.65, 1.0)}[f]
        set_color(g, col); g.scale = ((0.75 if f in (0, 1) and t > t_gas else 1),) * 3
    # tubos que brillan por fases cuando se nombran
    hl = {0: win01(t, t_evap - 0.3, t_gas + 0.5), 2: win01(t, t_comp - 0.2, t_rej), 3: win01(t, t_rej - 0.2, t_cap), 4: win01(t, t_cap - 0.2, t_vuelve + 0.5)}
    for i, o in enumerate(S["tubos"]):
        f = F[min(i, len(F) - 1)]; base = BLACK if f == 3 else (0.6, 0.62, 0.66)
        tgt = {0: COLD, 2: HOT, 3: (1.0, 0.45, 0.2), 4: (0.3, 0.7, 1.0)}.get(f, base)
        set_color(o, mix_c(base, tgt, hl.get(f, 0)))
    # compresor vibra mientras funciona
    vib = 0.025 * math.sin(t * 60) * on * (t > t_comp - 0.5)
    S["comp"].location = (X0 + vib, 1.4, 0.55)
    # calor: de la comida al evaporador, y del condensador a la cocina
    for k, c in enumerate(S["calor"]):
        r = random.Random(k)
        if t_evap - 0.2 < t < t_gas + 1.0 or (t_puerta + 0.5 < t):
            src = S["comida"][k % len(S["comida"])].location; u = (t * 0.6 + k / 14) % 1.0
            c.location = Vector(src).lerp(Vector((X0, 0.65, 4.3 + 0.6 * math.sin(k))), u); c.scale = ((1 - u) * 1.2 + 0.2,) * 3
        else: c.location = (0, 0, -9)
    for k, w in enumerate(S["ondas"]):
        if (t_rej - 0.2 < t < t_cap) or (t_puerta + 0.5 < t):
            u = (t * 0.5 + k / 5) % 1.0
            w.location = (X0, 1.6 + 1.8 * u, 1.5 + 0.8 * k); w.scale = (1 + u, 1 + u, 1 + u)
        else: w.location = (0, 0, -9)
    # termostato
    set_color(S["termo"], (0.3, 0.9, 0.4) if win01(t, t_term - 0.1, t_puerta - 0.3) > 0.5 else (0.95, 0.85, 0.25))
    # puerta que se abre al final
    S["piv"].rotation_euler = (0, 0, -1.9 * seg(t, t_puerta + 0.3, t_puerta + 1.4))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def win01_integral(t, a, b):
    """tiempo total que el compresor ha estado parado hasta t (para que el flujo se detenga)"""
    if t <= a: return 0.0
    return min(t, b) - a

def mix_c(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))

def V(at, d, h=0.6, lens=32, dy=0.0): at = Vector(at); return ((at.x - d, at.y + dy, at.z + h), tuple(at), lens)
def CAM():
    return [(0.0, (-7.5, -8.5, 4.2), (0, 0, 2.9), 32), (T("mira dentro") - 0.3, (-8.5, -5.0, 4.0), (0, 0, 2.9), 32),
            (T("mira dentro") + 0.9,) + V((0, 0.2, 3.0), 11.5, 0.4), (T("refrigerante"),) + V((0, 0.6, 4.4), 6.5, 0.4),
            (T("se evapora"),) + V((0, 0.4, 4.2), 7.0), (T("ahora es un gas"),) + V((0, 0.7, 2.5), 9.0),
            (T("compresor"),) + V((0, 1.3, 0.9), 5.5, 0.5, 36), (T("rejilla negra"),) + V((0, 1.4, 3.0), 9.0, 0.6, 32, 1.0),
            (T("tubo finísimo"),) + V((0, 1.0, 5.3), 5.0, 0.4, 36), (T("vuelve a entrar"),) + V((0, 0.4, 3.6), 10.0),
            (T("termostato"),) + V((0, 0, 5.0), 6.0, 0.3, 36), (T("si dejas la puerta"), (-7.5, -9.5, 4.5), (0, 0, 2.9), 30),
            (T("todo el calor"), (-9, -11, 5.0), (0.5, 0.5, 2.9), 30), (DUR + 2, (-9.5, -11.5, 5.0), (0.5, 0.5, 2.9), 30)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"evap": Pj((X0, 0.72, 4.4)), "comp": Pj((X0, 1.4, 0.9)), "cond": Pj((X0, 1.4, 3.0)), "cap": Pj((X0, 0.95, 5.55)),
            "termo": Pj((-0.2, 0, 5.4)), "puerta": Pj((-0.5, -1.4, 3.0)), "nevera": Pj((0, 0, 3.0))}

if __name__ == "__main__":
    run("frigorifico", build, pose, anchors)
